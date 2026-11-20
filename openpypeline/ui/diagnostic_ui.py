"""Shared host-agnostic developer diagnostic tool for openPypeline Studio.

Provides a PySide main window that reloads core and UI modules on demand and
exposes quick-launch buttons for testing openPypeline Studio windows and
dialogs across standalone tools and extensible DCC host integrations.

:File: diagnostic_ui.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import importlib
import json
from typing import Optional

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets  # type: ignore[no-redef]

from openpypeline.core import ops_actions as opsActions
from openpypeline.core import ops_info as opsInfo
from openpypeline.core import ops_project as opsProject
from openpypeline.core.localization import localization
from openpypeline.core.util import prefs
from openpypeline.ui import ops_main_controller as opsMainController
from openpypeline.ui import ops_main_ui as opsMainUI
from openpypeline.ui import ops_proj_dialog_controller as opsProjDialogController
from openpypeline.ui import (
    ops_project_manager_controller as opsProjectManagerController,
)
from openpypeline.ui import ops_save_master_controller as opsSaveMasterController
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers
from openpypeline.ui import ui_objects as UIObjects


class DiagnosticUI(QtWidgets.QMainWindow):
    """Provide developer controls for launching and inspecting application windows.

    Instantiates the core PySide UI controllers, registers them on the
    :class:`~openpypeline.ui.ui_objects.WindowManager` singleton, and provides
    a developer dashboard for launching windows, inspecting active widgets, and
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
        :param parent: Optional parent widget for host window parenting.
        """
        super().__init__(parent=parent)
        self.UIObjects = UIObjects.UIObjects()
        self.filePath = filePath

        self.setWindowTitle("Diagnostic UI Manager")
        self.setObjectName("DiagnosticUIManager")
        self.resize(500, 300)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self._reload_modules()
        localization.load_language()
        self._instantiate_controllers()

        self._build_ui()

    def _reload_modules(self) -> None:
        """Hot-reload core and shared UI modules for rapid developer iteration."""
        for module in (
            opsSaveMasterController,
            opsProjectManagerController,
            opsProjDialogController,
            opsMainUI,
            opsMainController,
            opsProject,
            opsActions,
            opsUIWrappers,
            opsInfo,
        ):
            importlib.reload(module)

    def _instantiate_controllers(self) -> None:
        """Instantiate default UI controllers and bind them to :attr:`UIObjects`."""
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

    def showWindow(self) -> None:
        """Show the diagnostic manager and refresh its visible-window report."""
        self.show()
        self.updateTextField()

    def _build_ui(self) -> None:
        """Construct the menu bar, diagnostic output pane, and launcher buttons."""
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

        main_layout = QtWidgets.QHBoxLayout(self.centralWidget())
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Diagnostic Output Group ---
        output_group = QtWidgets.QGroupBox("Diagnostic Output")
        output_layout = QtWidgets.QVBoxLayout(output_group)

        self.diagnosticUI_UIObjects_scrollField = QtWidgets.QTextEdit()
        self.diagnosticUI_UIObjects_scrollField.setReadOnly(True)
        output_layout.addWidget(self.diagnosticUI_UIObjects_scrollField)

        main_layout.addWidget(output_group, stretch=2)

        # --- UI Launchers Group ---
        launcher_group = QtWidgets.QGroupBox("UI Launchers")
        launcher_layout = QtWidgets.QVBoxLayout(launcher_group)

        buttons_data = [
            ("Main GUI", "opsMainController"),
            ("Project Manager GUI", "opsProjectManagerController"),
            ("Save Master GUI", "opsSaveMasterController"),
            ("Project Dialogue GUI", "opsProjDialogController"),
        ]

        for label, target in buttons_data:
            btn = QtWidgets.QPushButton(label)
            btn.setMinimumHeight(30)
            btn.clicked.connect(
                lambda checked=False, t=target: self.buttonRelease(t)
            )
            launcher_layout.addWidget(btn)

        launcher_layout.addStretch()
        main_layout.addWidget(launcher_group, stretch=1)

    def reload(self) -> None:
        """Close managed windows, reinitialize controllers, and refresh the display."""
        for attr in (
            "opsSaveMasterController",
            "opsProjectManagerController",
            "opsProjDialogController",
            "opsMainUI",
        ):
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                target = getattr(ui_obj, "view", ui_obj)
                if hasattr(target, "close"):
                    target.close()
                    target.deleteLater()

        self.UIObjects = UIObjects.UIObjects()
        self._reload_modules()
        localization.load_language()
        self._instantiate_controllers()

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

        for attr in (
            "opsSaveMasterController",
            "opsProjectManagerController",
            "opsProjDialogController",
            "opsMainUI",
        ):
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                widget = getattr(ui_obj, "view", ui_obj)
                if hasattr(widget, "isVisible") and widget.isVisible():
                    name = widget.objectName() or type(widget).__name__
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
        data = prefs._load_prefs()
        formatted_prefs = json.dumps(data, indent=4)
        self.diagnosticUI_UIObjects_scrollField.append(
            f"\n--- Current Preferences ---\n{formatted_prefs}"
        )
