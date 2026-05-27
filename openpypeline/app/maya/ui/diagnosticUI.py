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

import UIObjects

import openpypeline.core.util.XML as XML
importlib.reload(XML)

import opsSaveMasterGUI
importlib.reload(opsSaveMasterGUI)

import openpypeline.app.maya.ui.opsProjectManagerGUI as opsProjectManagerGUI
importlib.reload(opsProjectManagerGUI)

import opsProjDialogGUI
importlib.reload(opsProjDialogGUI)

import opsMainUI
importlib.reload(opsMainUI)

import opsProject
importlib.reload(opsProject)

import opsActions
importlib.reload(opsActions)

import opsLoader
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
        
        self.UIObjects.opsSaveMasterGUI = opsSaveMasterGUI.opsSaveMasterGUI()
        self.UIObjects.opsProjectManagerGUI = opsProjectManagerGUI.opsProjectManagerGUI()
        self.UIObjects.opsProjDialogGUI = opsProjDialogGUI.opsProjDialogGUI()
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
        main_layout = QtWidgets.QVBoxLayout(self.centralWidget())
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- UI Launchers Group ---
        launcher_group = QtWidgets.QGroupBox("UI Launchers")
        launcher_layout = QtWidgets.QVBoxLayout(launcher_group)
        
        # Data-driven button creation (Pythonic DRY principle)
        buttons_data = [
            ("Open Pipeline Main GUI", "opsMainUI"),
            ("Project Manager GUI", "opsProjectManagerGUI"),
            ("Save Master GUI", "opsSaveMasterGUI"),
            ("Project Dialogue GUI", "opsProjDialogGUI")
        ]
        
        for label, target in buttons_data:
            btn = QtWidgets.QPushButton(label)
            btn.setMinimumHeight(30)
            # Using lambda checked=False, t=target to capture the loop variable locally
            btn.clicked.connect(lambda checked=False, t=target: self.buttonRelease(t))
            launcher_layout.addWidget(btn)
            
        main_layout.addWidget(launcher_group)

        # --- Diagnostic Output Group ---
        output_group = QtWidgets.QGroupBox("Diagnostic Output")
        output_layout = QtWidgets.QVBoxLayout(output_group)
        
        self.diagnosticUI_UIObjects_scrollField = QtWidgets.QTextEdit()
        self.diagnosticUI_UIObjects_scrollField.setReadOnly(True)
        output_layout.addWidget(self.diagnosticUI_UIObjects_scrollField)
        
        # stretch=1 forces the text edit to fill remaining vertical space when resized
        main_layout.addWidget(output_group, stretch=1) 
    
    def reload(self):
        '''
        "reload" resets the diagnosticUI and closes associated windows.
        '''
                
        # Try to close PySide widgets tracked via attributes on UIObjects directly
        for attr in ['opsSaveMasterGUI', 'opsProjectManagerGUI', 'opsProjDialogGUI', 'opsMainUI']:
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                if hasattr(ui_obj, 'close'):
                    ui_obj.close()

        self.UIObjects = UIObjects.UIObjects()
        self.UIObjects.opsSaveMasterGUI = opsSaveMasterGUI.opsSaveMasterGUI()
        self.UIObjects.opsProjectManagerGUI = opsProjectManagerGUI.opsProjectManagerGUI()
        self.UIObjects.opsProjDialogGUI = opsProjDialogGUI.opsProjDialogGUI()
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
        for attr in ['opsSaveMasterGUI', 'opsProjectManagerGUI', 'opsProjDialogGUI', 'opsMainUI']:
            if hasattr(self.UIObjects, attr):
                ui_obj = getattr(self.UIObjects, attr)
                if hasattr(ui_obj, 'isVisible') and ui_obj.isVisible():
                    name = ui_obj.objectName() or type(ui_obj).__name__
                    if name not in textFieldString:
                        textFieldString += f"{name}\n"

        self.diagnosticUI_UIObjects_scrollField.setPlainText(textFieldString)
        
    def savePrefs(self):
        '''
        "savePrefs" stores xml data using the 'XML.py' module
        '''
        fileName = 'test1.xml'
        prefs = ['hello', 'goodbye', 'idunno']
        if self.filePath:
            prefs_dir = os.path.join(self.filePath, 'openpypeline', 'app', 'maya', 'ui', 'prefs')
            os.makedirs(prefs_dir, exist_ok=True)
            filePath = os.path.join(prefs_dir, fileName)
            xmlFile = XML.xmlfile(filePath)
            xmlFile.save(prefs)
        
    def loadPrefs(self):
        '''
        "loadPrefs" loads xml data using the 'XML.py' module
        '''
        fileName = 'test1.xml'
        if self.filePath:
            filePath = os.path.join(self.filePath, 'openpypeline', 'app', 'maya', 'ui', 'prefs', fileName)
            if os.path.exists(filePath):
                xmlFile = XML.xmlfile(filePath)
                prefs = xmlFile.load()
                print(f"prefs = {prefs}")