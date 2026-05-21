"""
Module: diagnosticUI.py

Description:
    This script is an example of how a single class can manage and store the data for all Maya openPypeline Studio GUIs.
    With its loadPrefs() and savePrefs() procedures, it also demonstrates its potential ability to save out both session independent & application independent information.
"""

import maya.cmds as cmds
import os

import window as window

import UIObjects as UIObjects

import openpypeline.core.util.XML as XML
reload(XML)

import opsSaveMasterGUI
reload(opsSaveMasterGUI)

import opsProjectManagerGUI
reload(opsProjectManagerGUI)

import opsProjDialogGUI
reload(opsProjDialogGUI)

import opsMainUI
reload(opsMainUI)

class diagnosticUI(window.window):

    def __init__(self, filePath = None):
        
        
        self.UIObjects = UIObjects.UIObjects()
        
        self.filePath = filePath
        
        self.width=500
        self.height=300
        self.name = "Diagnostic UI Manager"
        self.dockable=0
        self.UIObjects.opsSaveMasterGUI = opsSaveMasterGUI.opsSaveMasterGUI()
        self.UIObjects.opsProjectManagerGUI = opsProjectManagerGUI.opsProjectManagerGUI()
        self.UIObjects.opsProjDialogGUI = opsProjDialogGUI.opsProjDialogGUI()
        self.UIObjects.opsMainUI = opsMainUI.opsMainUI()
    
    def content(self):
        """
        Builds and returns the main form layout for the Diagnostic UI.
        """
        self.form1 = cmds.formLayout('openPipelineProjectManagerGUI_form', numberOfDivisions=100)
        
        self._build_menu_bar()
        self._build_main_controls()
        self._build_buttons()
        self._attach_form_elements()
        
        return [self.form1]

    def _build_menu_bar(self):
        self.menuBarLayout0 = cmds.menuBarLayout(parent=self.form1)
        self.menu01 = cmds.menu(label='options', parent=self.menuBarLayout0)
        cmds.menuItem(label="Refresh Objects Field", subMenu=0, parent=self.menu01, command=lambda *args:self.updateTextField())
        cmds.menuItem(label="Reload", subMenu=0, parent=self.menu01, command=lambda *args:self.reload())
        cmds.menuItem(label="Save Prefs", subMenu=0, parent=self.menu01, command=lambda *args:self.savePrefs())
        cmds.menuItem(label="Load Prefs", subMenu=0, parent=self.menu01, command=lambda *args:self.loadPrefs())

    def _build_main_controls(self):
        self.diagnosticUI_UIObjects_scrollField = cmds.scrollField('diagnosticUI_UIObjects_scrollField', parent=self.form1, ww=1, editable=0)

    def _build_buttons(self):
        self.diagnosticUImainUI_btn = cmds.button(l="Open Pipeline Main GUI", parent=self.form1, bgc=(.85, .85, .85), c=lambda *args:self.buttonRelease('opsMainUI'))
        self.diagnosticUIProjManager_btn = cmds.button(l="Project Manager GUI", parent=self.form1, bgc=(.8, .8, .8), c=lambda *args:self.buttonRelease('opsProjectManagerGUI'))
        self.diagnosticUISaveMaster_btn = cmds.button(l="Save Master GUI", parent=self.form1, bgc=(.75, .75, .75), c=lambda *args:self.buttonRelease('opsSaveMasterGUI'))
        self.diagnosticUIProjDialog_btn = cmds.button(l="Project Dialogue GUI", parent=self.form1, bgc=(.7, .7, .7), c=lambda *args:self.buttonRelease('opsProjDialogGUI'))

    def _attach_form_elements(self):
        cmds.formLayout(
            self.form1,
            edit=True,
            attachPosition=[
                (self.menuBarLayout0, 'top', 0, 0),
                (self.menuBarLayout0, 'left', 0, 0),
                (self.menuBarLayout0, 'right', 0, 100),
                (self.diagnosticUImainUI_btn, 'left', 5, 0),
                (self.diagnosticUImainUI_btn, 'right', 5, 100),
                (self.diagnosticUI_UIObjects_scrollField, 'left', 5, 0),
                (self.diagnosticUI_UIObjects_scrollField, 'right', 5, 100),
                (self.diagnosticUIProjManager_btn, 'left', 5, 0),
                (self.diagnosticUIProjManager_btn, 'right', 5, 100),
                (self.diagnosticUISaveMaster_btn, 'left', 5, 0),
                (self.diagnosticUISaveMaster_btn, 'right', 5, 100),
                (self.diagnosticUIProjDialog_btn, 'left', 5, 0),
                (self.diagnosticUIProjDialog_btn, 'right', 5, 100),
                (self.diagnosticUIProjDialog_btn, 'bottom', 2, 100),
            ],
            attachControl=[
                
                (self.diagnosticUI_UIObjects_scrollField, 'top', 2, self.menuBarLayout0),
                (self.diagnosticUI_UIObjects_scrollField, 'bottom', 2, self.diagnosticUImainUI_btn),
                (self.diagnosticUImainUI_btn, 'bottom', 2, self.diagnosticUIProjManager_btn),
                (self.diagnosticUIProjManager_btn, 'bottom', 2, self.diagnosticUISaveMaster_btn),
                (self.diagnosticUISaveMaster_btn, 'bottom', 2, self.diagnosticUIProjDialog_btn),
            ]
        )
    
    def reload(self):
        '''
        "reload" resets the diagnosticUI
        '''
        for obj in self.UIObjects.window:
            if cmds.window(obj, q=True, ex=True):
                cmds.deleteUI(obj)
        for obj in self.UIObjects.dockControl:
            if cmds.workspaceControl(obj, q=1, exists=1):
                cmds.deleteUI(obj)
        self.UIObjects = UIObjects.UIObjects()
        self.showWindow()
        self.updateTextField()
    
    
    def buttonRelease(self, window):
        getattr(self.UIObjects, window).showWindow()
    
    
    def updateTextField(self):
        '''
        "updateTextField" updates the 'self.diagnosticUI_UIObjects_scrollField' text field to reflect the most current GUI state.
        '''
        textFieldString = '---window objects---\n\n'
        for obj in self.UIObjects.window:
            if cmds.window(obj, q=True, ex=True):
                textFieldString += f"{obj}\n"
        textFieldString += '\n---dockable objects---\n\n'
        for obj in self.UIObjects.dockControl:
            if cmds.workspaceControl(obj, q=1, exists=1):
                textFieldString += f"{obj}\n"
        cmds.scrollField(self.diagnosticUI_UIObjects_scrollField, edit=1, text=textFieldString)
        
    def savePrefs(self):
        
        '''
        "savePrefs" stores xml data using the 'XML.py' module
        '''
        fileName = 'test1.xml'
        prefs = [('hello'),('goodbye'),('idunno')]
        filePath = os.path.join(self.filePath, 'openpypeline', 'app', 'maya', 'ui', 'prefs', fileName)
        xmlFile = XML.xmlfile(filePath)
        xmlFile.save(prefs)
        
    def loadPrefs(self):
        
        '''
        "loadPrefs" loades xml data using the 'XML.py' module
        '''
        
        fileName = 'test1.xml'
        filePath = os.path.join(self.filePath, 'openpypeline', 'app', 'maya', 'ui', 'prefs', fileName)
        xmlFile = XML.xmlfile(filePath)
        prefs = xmlFile.load()
        print(f"prefs = {prefs}")