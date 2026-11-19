"""Developer diagnostic tool for launching, reloading, and inspecting PySide6 GUIs.

Provides a Maya dockable/standalone developer window that reloads core and UI
modules on import and exposes quick-launch buttons for testing openPypeline
Studio windows and dialogs without restarting Maya.

:File: diagnostic_ui.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import importlib
import os
from typing import Any, Optional

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide6 import QtCore, QtWidgets

from openpypeline.ui import ui_objects as UIObjects

# Reload UI controllers and core modules on import so developer edits take effect immediately in Maya
from . import ops_save_master_controller as opsSaveMasterController

importlib.reload(opsSaveMasterController)

from . import ops_project_manager_controller as opsProjectManagerController

importlib.reload(opsProjectManagerController)

from . import ops_proj_dialog_controller as opsProjDialogController

importlib.reload(opsProjDialogController)

from . import ops_main_ui as opsMainUI

importlib.reload(opsMainUI)

from . import ops_main_controller as opsMainController

importlib.reload(opsMainController)

from openpypeline.core import ops_project as opsProject

importlib.reload(opsProject)

from openpypeline.core import ops_actions as opsActions

importlib.reload(opsActions)

from openpypeline.ui import ops_ui_wrappers as opsUIWrappers

importlib.reload(opsUIWrappers)

from openpypeline.core import ops_info as opsInfo

importlib.reload(opsInfo)

from openpypeline.app.maya.core import ops_loader as opsLoader

importlib.reload(opsLoader)
class diagnosticUI(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    """Provide developer controls for launching and inspecting application windows.

    Instantiates the core PySide6 UI controllers, registers them on the
    :class:`~openpypeline.ui.ui_objects.UIObjects` singleton, and provides a
    developer dashboard for launching windows, inspecting active widgets, and
    viewing serialized preferences.

    :ivar UIObjects: Shared :class:`~openpypeline.ui.ui_objects.WindowManager`
        singleton holding active controller and view references.
    :vartype UIObjects: openpypeline.ui.ui_objects.WindowManager
    :ivar filePath: Optional initial file path passed when constructing the
        diagnostic window.
    :vartype filePath: Optional[str]
    :ivar diagnosticUI_UIObjects_scrollField: Read-only text area displaying
        visible window objects and diagnostic preference dumps.
    :vartype diagnosticUI_UIObjects_scrollField: QtWidgets.QTextEdit
    """

    def __init__(
        self,
        filePath: Optional[str] = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        """Initialize managed controllers and build the diagnostic window.

        :param filePath: Optional scene or diagnostic path context.
        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(parent=parent)
        self.UIObjects = UIObjects.UIObjects()
        self.filePath = filePath

        self.setWindowTitle("Diagnostic UI Manager")
        self.setObjectName("DiagnosticUIManager")
        self.resize(500, 300)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        from openpypeline.core.localization import localization

        localization.load_language()

        self.UIObjects.opsMainController = opsMainController.OpsMainController()
        self.UIObjects.opsMainUI = self.UIObjects.opsMainController.view
        self.UIObjects.opsSaveMasterController = (
            opsSaveMasterController.OpsSaveMasterController()
        )
        self.UIObjects.opsProjectManagerController = (
            opsProjectManagerController.OpsProjectManagerController()
        )
        self.UIObjects.opsProjDialogController = (
            opsProjDialogController.OpsProjDialogController()
        )

        self._build_ui()

    def showWindow(self) -> None:
        """Show the diagnostic manager and refresh its visible-window report."""
        self.show()
        self.updateTextField()

    def _build_ui(self) -> None:
        """Construct the menu bar, diagnostic output pane, and launcher buttons."""
        # Menu Bar
        menubar = self.menuBar()
        options_menu = menubar.addMenu("Options")

        refresh_action = options_menu.addAction("Refresh Objects Field")
        refresh_action.triggered.connect(self.updateTextField)

        reload_action = options_menu.addAction("Reload")
        reload_action.triggered.connect(self.reload)

        save_prefs_action = options_menu.addAction("Save Prefs")
        save_prefs_action.triggered.connect(self.savePrefs)

        load_prefs_action = options_menu.addAction("Load Prefs")
        load_prefs_action.triggered.connect(self.loadPrefs)

        # Central Layout
        main_layout = QtWidgets.QHBoxLayout(self.centralWidget())
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Diagnostic Output Group ---
        output_group = QtWidgets.QGroupBox("Diagnostic Output")
        output_layout = QtWidgets.QVBoxLayout(output_group)

        self.diagnosticUI_UIObjects_scrollField = QtWidgets.QTextEdit()
        self.diagnosticUI_UIObjects_scrollField.setReadOnly(True)
        output_layout.addWidget(self.diagnosticUI_UIObjects_scrollField)

        # stretch=2 forces the text edit to fill most of the horizontal space
        main_layout.addWidget(output_group, stretch=2)

        # --- UI Launchers Group ---
        launcher_group = QtWidgets.QGroupBox("UI Launchers")
        launcher_layout = QtWidgets.QVBoxLayout(launcher_group)

        # Data-driven button creation (Pythonic DRY principle)
        buttons_data = [
            ("Main GUI", "opsMainController"),
            ("Project Manager GUI", "opsProjectManagerController"),
            ("Save Master GUI", "opsSaveMasterController"),
            ("Project Dialogue GUI", "opsProjDialogController"),
        ]

        for label, target in buttons_data:
            btn = QtWidgets.QPushButton(label)
            btn.setMinimumHeight(30)
            # Using lambda checked=False, t=target to capture the loop variable locally
            btn.clicked.connect(
                lambda checked=False, t=target: self.buttonRelease(t)
            )
            launcher_layout.addWidget(btn)

        # Push the buttons up to the top of the column
        launcher_layout.addStretch()

        # stretch=1 restricts the width of the button column relative to the text box
        main_layout.addWidget(launcher_group, stretch=1)

    def reload(self) -> None:
        """Close managed windows, reinitialize controllers, and refresh the display."""
        # Try to close PySide widgets tracked via attributes on UIObjects directly
        for attr in [
            "opsSaveMasterController",
            "opsProjectManagerController",
            "opsProjDialogController",
            "opsMainUI",
        ]:
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                if hasattr(ui_obj, "close"):
                    ui_obj.close()
                    ui_obj.deleteLater()

        self.UIObjects = UIObjects.UIObjects()

        from openpypeline.core.localization import localization

        localization.load_language()

        self.UIObjects.opsMainController = opsMainController.OpsMainController()
        self.UIObjects.opsMainUI = self.UIObjects.opsMainController.view
        self.UIObjects.opsSaveMasterController = (
            opsSaveMasterController.OpsSaveMasterController()
        )
        self.UIObjects.opsProjectManagerController = (
            opsProjectManagerController.OpsProjectManagerController()
        )
        self.UIObjects.opsProjDialogController = (
            opsProjDialogController.OpsProjDialogController()
        )

        self.showWindow()
        self.updateTextField()

    def buttonRelease(self, window: str) -> None:
        """Show the named managed window and refresh the diagnostic report.

        :param window: Attribute name of the target controller on
            :attr:`UIObjects` (for example, ``"opsMainController"``).
        """
        getattr(self.UIObjects, window).showWindow()
        self.updateTextField()

    def updateTextField(self) -> None:
        """Update the diagnostic output pane with currently visible GUI objects."""
        textFieldString = "---window objects---\n\n"

        # Fallback to display the PySide attribute objects if they aren't explicitly registered
        for attr in [
            "opsSaveMasterController",
            "opsProjectManagerController",
            "opsProjDialogController",
            "opsMainUI",
        ]:
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                if hasattr(ui_obj, "isVisible") and ui_obj.isVisible():
                    name = ui_obj.objectName() or type(ui_obj).__name__
                    if name not in textFieldString:
                        textFieldString += f"{name}\n"

        self.diagnosticUI_UIObjects_scrollField.setPlainText(textFieldString)

    def savePrefs(self) -> None:
        """Report that preferences are persisted automatically by ``prefs``."""
        self.diagnosticUI_UIObjects_scrollField.append(
            "\nPreferences are auto-saved to ~/.openpypeline/user_prefs.json"
        )

    def loadPrefs(self) -> None:
        """Load serialized preferences from ``prefs`` and append them to the log."""
        import json

        from openpypeline.core.util import prefs

        data = prefs._load_prefs()
        formatted_prefs = json.dumps(data, indent=4)
        self.diagnosticUI_UIObjects_scrollField.append(
            f"\n--- Current Preferences ---\n{formatted_prefs}"
        )
