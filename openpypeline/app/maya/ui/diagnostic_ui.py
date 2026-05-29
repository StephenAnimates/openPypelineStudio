"""
Module: diagnosticUI.py

Description:
    Developer-focused diagnostic tool for launching, reloading, and tracking the state of 
    various PySide6 GUIs within the openPypeline Studio framework.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import importlib

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

from . import ui_objects as UIObjects

from . import ops_save_master_controller as opsSaveMasterController
importlib.reload(opsSaveMasterController)

from . import ops_project_manager_gui as opsProjectManagerGUI
importlib.reload(opsProjectManagerGUI)

from . import ops_proj_dialog_controller as opsProjDialogController
importlib.reload(opsProjDialogController)

from . import ops_main_ui as opsMainUI
importlib.reload(opsMainUI)

from ..core import ops_project as opsProject
importlib.reload(opsProject)

from ..core import ops_actions as opsActions
importlib.reload(opsActions)

from ..core import ops_ui_wrappers as opsUIWrappers
importlib.reload(opsUIWrappers)

from ..core import ops_info as opsInfo
importlib.reload(opsInfo)

from ..core import ops_loader as opsLoader
importlib.reload(opsLoader)

class diagnosticUI(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):

    def __init__(self, filePath=None, parent=None):
        super().__init__(parent=parent)
        self.UIObjects = UIObjects.UIObjects()
        self.filePath = filePath
        
        self.setWindowTitle("Diagnostic UI Manager")
        self.setObjectName("DiagnosticUIManager")
        self.resize(500, 300)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        self.UIObjects.opsSaveMasterController = opsSaveMasterController.OpsSaveMasterController()
        self.UIObjects.opsProjectManagerGUI = opsProjectManagerGUI.opsProjectManagerGUI()
        self.UIObjects.opsProjDialogController = opsProjDialogController.OpsProjDialogController()
        self.UIObjects.opsMainUI = opsMainUI.opsMainUI()
        
        self._build_ui()

    def showWindow(self):
        self.show()
        self.updateTextField()
    
    def _build_ui(self):
        """Constructs the UI using PySide widgets and layouts."""
        
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
            ("Open Pipeline Main GUI", "opsMainUI"),
            ("Project Manager GUI", "opsProjectManagerGUI"),
            ("Save Master GUI", "opsSaveMasterController"),
            ("Project Dialogue GUI", "opsProjDialogController")
        ]
        
        for label, target in buttons_data:
            btn = QtWidgets.QPushButton(label)
            btn.setMinimumHeight(30)
            # Using lambda checked=False, t=target to capture the loop variable locally
            btn.clicked.connect(lambda checked=False, t=target: self.buttonRelease(t))
            launcher_layout.addWidget(btn)
            
        # Push the buttons up to the top of the column
        launcher_layout.addStretch()
        
        # stretch=1 restricts the width of the button column relative to the text box
        main_layout.addWidget(launcher_group, stretch=1)
    
    def reload(self):
        '''
        "reload" resets the diagnosticUI and closes associated windows.
        '''
                
        # Try to close PySide widgets tracked via attributes on UIObjects directly
        for attr in ['opsSaveMasterController', 'opsProjectManagerGUI', 'opsProjDialogController', 'opsMainUI']:
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                if hasattr(ui_obj, 'close'):
                    ui_obj.close()
                    ui_obj.deleteLater()

        self.UIObjects = UIObjects.UIObjects()
        self.UIObjects.opsSaveMasterController = opsSaveMasterController.OpsSaveMasterController()
        self.UIObjects.opsProjectManagerGUI = opsProjectManagerGUI.opsProjectManagerGUI()
        self.UIObjects.opsProjDialogController = opsProjDialogController.OpsProjDialogController()
        self.UIObjects.opsMainUI = opsMainUI.opsMainUI()
        
        self.showWindow()
        self.updateTextField()
    
    def buttonRelease(self, window):
        getattr(self.UIObjects, window).showWindow()
        self.updateTextField()
    
    def updateTextField(self):
        '''
        Updates the text field to reflect the most current GUI state.
        '''
        textFieldString = '---window objects---\n\n'
                
        # Fallback to display the PySide attribute objects if they aren't explicitly registered
        for attr in ['opsSaveMasterController', 'opsProjectManagerGUI', 'opsProjDialogController', 'opsMainUI']:
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                if hasattr(ui_obj, 'isVisible') and ui_obj.isVisible():
                    name = ui_obj.objectName() or type(ui_obj).__name__
                    if name not in textFieldString:
                        textFieldString += f"{name}\n"

        self.diagnosticUI_UIObjects_scrollField.setPlainText(textFieldString)
        
    def savePrefs(self):
        '''
        "savePrefs" is now managed automatically by the DCC-agnostic prefs module.
        '''
        self.diagnosticUI_UIObjects_scrollField.append("\nPreferences are auto-saved to ~/.openpypeline/user_prefs.json")
        
    def loadPrefs(self):
        '''
        "loadPrefs" loads json data using the 'prefs.py' module and displays it.
        '''
        from openpypeline.core.util import prefs
        import json
        data = prefs._load_prefs()
        formatted_prefs = json.dumps(data, indent=4)
        self.diagnosticUI_UIObjects_scrollField.append(f"\n--- Current Preferences ---\n{formatted_prefs}")