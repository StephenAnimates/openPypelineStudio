"""
File: begin.py
Description:
    This script provides a developer-focused entry point for launching and testing
    the openPypeline Studio Maya GUI components. It prompts the user to select
    the root script directory, adds it to the system path, and then launches
    a diagnostic UI to manage and view the various GUI windows.

    This is primarily intended for development and debugging, not as the main
    entry point for artists. The main entry point is `opsLoader.py`.

Usage:
    To use this developer tool, execute the following in a Maya Python tab:

    from openpypeline.app.maya.ui import begin
    import importlib
    importlib.reload(begin)

    dev_launcher = begin.begin()

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import sys
import importlib
import os

# TODO: Remember to run the end-to-end manual test for OpenUSD (.usd, .usda) 
#       and Alembic (.abc) project creation and export using this diagnostic launcher!

class begin():

    def __init__(self):
        '''
        Initializes the developer launcher.

        This constructor orchestrates the process of getting the source directory,
        updating the system path, and launching the diagnostic UI.
        '''
        self.srcDir = ""
        # First, prompt the user to select the root script directory.
        self.sourceFilesPath()
        # If a valid directory was selected, proceed with initialization.
        if self.srcDir:
            self.appendDir()
            self.diagnostic()

    def sourceFilesPath(self):
        """
        Opens a Maya file dialog to let the user select the source directory.

        The selected path is stored in the instance variable `self.srcDir`.
        """
        # Use the modern fileDialog2 for directory selection.
        result = cmds.fileDialog2(fileMode=3, caption="Select the folder that contains the 'openpypeline' directory")
        # Store the path if the user selected a folder.
        if result and result[0]:
            self.srcDir = result[0]

    def diagnostic(self):
        """
        Imports and launches the main diagnostic UI window.

        This UI acts as a control panel for showing/hiding the various
        component GUIs of the openPypeline Studio application.
        """
        # Import the diagnostic UI module.
        import openpypeline.app.maya.ui.diagnosticUI as diagnosticUI
        # Reload the module to ensure the latest code is used during development.
        importlib.reload(diagnosticUI)
        # Instantiate and show the diagnostic window, passing the source directory.
        self.diagnosticUI = diagnosticUI.diagnosticUI(self.srcDir)
        self.diagnosticUI.showWindow()

    def appendDir(self):
        """
        Appends the selected source directory to Python's system path.

        This allows Python to find and import the openPypeline modules.
        """
        # Check if the directory is not already in the path to avoid duplicates.
        if self.srcDir not in sys.path:
            # Insert at the beginning of the list to ensure it's checked first.
            sys.path.insert(0, self.srcDir)
            
        # Add backend logic and the modernized UI paths to sys.path so flat imports work
        maya_path = os.path.join(self.srcDir, "maya").replace("\\", "/")
        ui_path = os.path.join(self.srcDir, "openpypeline", "app", "maya", "ui").replace("\\", "/")
        backend_path = os.path.join(self.srcDir, "maya", "openPypelineStudio").replace("\\", "/")
        
        for path in [maya_path, ui_path, backend_path]:
            if path not in sys.path:
                sys.path.insert(0, path)