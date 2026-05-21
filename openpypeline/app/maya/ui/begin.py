import maya.cmds as cmds
import sys
import importlib

class begin():
    
    def __init__(self):
        
        '''
        Name: begin.py
        Input: none
        Returns: none
        Description: This script is an example of a potential entry point for the openPypeline Studio Maya GUI
        Use: Initialization of this script will open a dialogue window. Using that window, select the folder that contains the 'openpypeline' directory.
        
        Examples:
        
        openPypeline = begin()
        
        openPypeline.diagnosticUI.showWindow()
        
        '''
        self.srcDir = ""
        self.sourceFilesPath()
        if self.srcDir:
            self.appendDir()
            self.diagnostic()

    def sourceFilesPath(self):
        # Use modern cmds.fileDialog2 instead of deprecated cmds.fileBrowserDialog
        result = cmds.fileDialog2(fileMode=3, caption="Select the folder that contains the 'openpypeline' directory")
        if result and result[0]:
            self.srcDir = result[0]

    def diagnostic(self):
        import openpypeline.app.maya.ui.diagnosticUI as diagnosticUI
        importlib.reload(diagnosticUI)
        self.diagnosticUI = diagnosticUI.diagnosticUI(self.srcDir)
        self.diagnosticUI.showWindow()

    def appendDir(self):
        if self.srcDir not in sys.path:
            sys.path.insert(0, self.srcDir)