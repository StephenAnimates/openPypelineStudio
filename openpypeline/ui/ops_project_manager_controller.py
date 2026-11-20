"""Shared host-agnostic controller for the openPypeline Studio Project Manager.

Handles signal routing and project lifecycle logic between :class:`~openpypeline.ui.ops_project_manager_gui.OpsProjectManagerGUI` and the core :mod:`~openpypeline.core.ops_project` and :mod:`~openpypeline.core.ops_actions` backends across standalone tools and extensible DCC host integrations.

:File: ops_project_manager_controller.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import importlib
import os
from typing import Any

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets  # type: ignore[no-redef]

from openpypeline.core import ops_actions as opsActions
from openpypeline.core import ops_project as opsProject
from openpypeline.core.localization import localization
from openpypeline.core.util import prefs
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers
from openpypeline.ui import ui_objects as UIObjects
from openpypeline.ui.ops_project_manager_gui import OpsProjectManagerGUI


class OpsProjectManagerController(QtCore.QObject):
    """Coordinate project-manager view events with project operations.

    Instantiates the Project Manager view via :meth:`_create_view`, binds its buttons and list selections to project creation, editing, joining, and removal handlers, and keeps the project registry list synchronized.

    :ivar UIObjects: Shared :class:`~openpypeline.ui.ui_objects.WindowManager` singleton reference.
    :vartype UIObjects: openpypeline.ui.ui_objects.WindowManager
    :ivar view: Project Manager window widget managed by this controller.
    :vartype view: openpypeline.ui.ops_project_manager_gui.OpsProjectManagerGUI
    """


    def __init__(self) -> None:
        """Create the project manager view and initialize its controls and data."""
        super().__init__()
        self.UIObjects = UIObjects.UIObjects()
        self.view: OpsProjectManagerGUI = self._create_view()

        self._connect_signals()
        self._populate_initial_data()

    def _create_view(self) -> OpsProjectManagerGUI:
        """Instantiate and return the Project Manager UI view widget.

        :returns: Project Manager window widget instance.
        """
        return OpsProjectManagerGUI()

    def _resolve_script_location(self) -> str:
        """Resolve and return the root installation directory path.

        :returns: Normalized path to the openPypeline root directory.
        """
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        ).replace("\\", "/")

    def _get_default_join_path(self) -> str:
        """Return the initial directory shown when joining an existing project.

        :returns: Default directory path for the project folder browser.
        """
        return prefs.get_pref("ops_projectFilePath", "")

    def _create_proj_dialog_controller(self) -> Any:
        """Lazily import, hot-reload, and instantiate the Project Dialog controller.

        :returns: :class:`~openpypeline.ui.ops_proj_dialog_controller.OpsProjDialogController` instance.
        """
        from openpypeline.ui import ops_proj_dialog_controller

        importlib.reload(ops_proj_dialog_controller)
        return ops_proj_dialog_controller.OpsProjDialogController()

    def showWindow(self) -> None:
        """Display the project manager window."""
        self.view.showWindow()

    def _connect_signals(self) -> None:
        """Connect project manager buttons and list events to controller methods."""
        self.view.edit_locations_btn.clicked.connect(self.on_edit_locations)
        self.view.edit_users_btn.clicked.connect(self.on_edit_users)
        self.view.project_list_widget.itemSelectionChanged.connect(
            self.on_project_selection
        )
        self.view.project_list_widget.itemDoubleClicked.connect(
            self.on_edit_project
        )
        self.view.new_proj_btn.clicked.connect(self.on_new_project)
        self.view.join_proj_btn.clicked.connect(self.on_join_project)
        self.view.remove_proj_btn.clicked.connect(self.on_remove_project)
        self.view.edit_proj_btn.clicked.connect(self.on_edit_project)
        self.view.refresh_btn.clicked.connect(self.on_refresh_list)
        self.view.close_btn.clicked.connect(self.on_close)

    def _populate_initial_data(self) -> None:
        """Populate location fields and refresh the configured project list."""
        self.view.script_location_field.setText(self._resolve_script_location())
        self.view.project_location_field.setText(
            prefs.get_pref("ops_projectFilePath", "Not Set")
        )
        self.on_refresh_list()

    def on_edit_locations(self, *args: Any) -> None:
        """Open the setup dialog for project and script locations.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        from openpypeline.ui.ops_setup_dialog import OpsSetupDialog

        dialog = OpsSetupDialog(parent=self.view)
        dialog.exec()
        self.view.project_location_field.setText(
            prefs.get_pref("ops_projectFilePath", "Not Set")
        )
        self.on_refresh_list()

    def on_edit_users(self, *args: Any) -> None:
        """Open the global project-user editor.

        Delegates to :func:`~openpypeline.core.ops_project.proj_edit_users`.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        opsProject.proj_edit_users()

    def on_project_selection(self, *args: Any) -> None:
        """Enable project actions and display details for the selected project.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        selected_items = self.view.project_list_widget.selectedItems()
        if not selected_items:
            self.view.edit_proj_btn.setEnabled(False)
            self.view.remove_proj_btn.setEnabled(False)
            return

        self.view.edit_proj_btn.setEnabled(True)
        self.view.remove_proj_btn.setEnabled(True)

        info_string = opsProject.get_project_info_string(
            selected_items[0].text()
        )
        self.view.project_info_field.setPlainText(info_string)

    def on_new_project(self, *args: Any) -> None:
        """Open the project editor in new-project mode (``mode = 0``).

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        self._ensure_dialog_exists()
        self.UIObjects.opsProjDialogController.mode = 0
        self.UIObjects.opsProjDialogController.old_name = ""
        self.UIObjects.opsProjDialogController.showWindow()

    def on_join_project(self, *args: Any) -> None:
        """Register a synchronized project using its shared manifest.

        Prompts the user to choose an existing project directory, reads its shared manifest via :func:`~openpypeline.core.ops_project.read_project_manifest`, registers it locally via :func:`~openpypeline.core.ops_actions.join_existing_project`, selects the joined project in the list, and refreshes the main UI.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        start_path = self._get_default_join_path()

        project_root = QtWidgets.QFileDialog.getExistingDirectory(
            self.view,
            "Join Existing Project",
            start_path,
        )
        if not project_root:
            return
        try:
            project_name = opsProject.read_project_manifest(project_root)[
                "project"
            ]["name"]
            opsActions.join_existing_project(project_root)
        except (opsActions.ProjectActionError, OSError, ValueError) as error:
            QtWidgets.QMessageBox.warning(
                self.view, "Could Not Join Project", str(error)
            )
            return

        self.on_refresh_list()
        matches = self.view.project_list_widget.findItems(
            project_name,
            QtCore.Qt.MatchExactly,
        )
        if matches:
            self.view.project_list_widget.setCurrentItem(matches[0])
        opsUIWrappers.refresh_ui()

    def on_edit_project(self, *args: Any) -> None:
        """Open the project editor for the currently selected project (``mode = 1``).

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        selected_items = self.view.project_list_widget.selectedItems()
        if not selected_items:
            return
        self._ensure_dialog_exists()
        self.UIObjects.opsProjDialogController.mode = 1
        self.UIObjects.opsProjDialogController.old_name = selected_items[
            0
        ].text()
        self.UIObjects.opsProjDialogController.showWindow()

    def _ensure_dialog_exists(self) -> None:
        """Lazily create and cache the project editor controller."""
        if not hasattr(self.UIObjects, "opsProjDialogController"):
            controller = self._create_proj_dialog_controller()
            if controller is not None:
                self.UIObjects.opsProjDialogController = controller

    def on_remove_project(self, *args: Any) -> None:
        """Confirm and remove the selected project, then refresh the list.

        Prompts for confirmation, calls :func:`~openpypeline.core.ops_actions.remove_project`, and updates the project list via :meth:`on_refresh_list`.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        selected_items = self.view.project_list_widget.selectedItems()
        if not selected_items:
            return
        proj_name = selected_items[0].text()

        title = localization.get_string("win_removeProjectConfirm")
        msg = localization.get_string("msg_removeProjectConfirm").format(
            proj_name
        )
        reply = QtWidgets.QMessageBox.question(
            self.view,
            title,
            msg,
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Cancel,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if opsActions.remove_project(proj_name):
                self.on_refresh_list()
            else:
                QtWidgets.QMessageBox.warning(
                    self.view,
                    localization.get_string("win_error"),
                    localization.get_string("msg_projectNotFound"),
                )

    def on_refresh_list(self, *args: Any) -> None:
        """Reload project names, clear selection state, and sync the main selector.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        self.view.project_list_widget.clear()
        proj_list = [
            p.get("name")
            for p in opsProject.get_projects_data()
            if isinstance(p, dict) and p.get("name")
        ]
        if proj_list:
            self.view.project_list_widget.addItems(proj_list)
        self.view.project_info_field.clear()
        self.view.edit_proj_btn.setEnabled(False)
        self.view.remove_proj_btn.setEnabled(False)
        main_controller = getattr(self.UIObjects, "opsMainController", None)
        if main_controller:
            main_controller.refresh_project_selector()

    def on_close(self, *args: Any) -> None:
        """Run the project UI close hook and close the manager window.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        opsProject.close_proj_ui()
        self.view.close()
