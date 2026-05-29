"""
File: opsLoader.py
Description: Main initialization and setup script for openPypeline Studio in Maya.
             It provides a modern Python-based entry point to manage script
             and project path configurations using the DCC-agnostic prefs module, sources 
             necessary MEL and Python modules, and launches the main UI.
             
Original Framework: OpenPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import sys
import importlib
import logging
from PySide6 import QtWidgets, QtCore

# Add the root openPypeline directory to sys.path to access core utilities
_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")).replace("\\", "/")
if _root_path not in sys.path:
    sys.path.insert(0, _root_path)
from openpypeline.core.util import prefs

# --- Logger Setup ---
logger = logging.getLogger("openPypeline")
logger.setLevel(logging.INFO) # Change to logging.DEBUG to see verbose file sourcing
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(name)s] %(levelname)s: %(message)s'))
    logger.addHandler(handler)

# Store the active dialog to prevent garbage collection
_setup_dialog = None

# --- Constants for preference keys ---
PROJECT_PATH_PREF = "ops_projectFilePath"

def _migrate_legacy_prefs():
    """Migrates legacy Maya optionVars to the DCC-agnostic prefs system."""
    try:
        import maya.cmds as cmds
        migrations = [
            ("openPipeline_projectFilePath", PROJECT_PATH_PREF),
            (PROJECT_PATH_PREF, PROJECT_PATH_PREF)
        ]
        for old_var, new_pref in migrations:
            if cmds.optionVar(exists=old_var) and not prefs.has_pref(new_pref):
                prefs.set_pref(new_pref, cmds.optionVar(query=old_var))
                cmds.optionVar(remove=old_var)
    except ImportError:
        # Not running in Maya, no legacy optionVars to migrate
        pass

def source_python_module(path):
    """
    Adds a path to sys.path and imports/reloads all Python modules within it.

    Args:
        path (str): The directory path to look in.

    Returns:
        None
    """
    if not os.path.isdir(path):
        logger.warning(f"Cannot source Python modules from non-existent path: {path}")
        return

    # Add path to sys.path if it's not already there
    if path not in sys.path:
        sys.path.append(path)
        logger.info(f"Appending {path} to sys.path")

    logger.info(f"----- Sourcing Python from {path} ------")
    for file_name in os.listdir(path):
        if file_name.endswith(".py") and not file_name.startswith("__"):
            module_name = os.path.splitext(file_name)[0]
            logger.info(f"//// Python Source: {module_name}")
            try:
                # Import the module if it's the first time
                module = importlib.import_module(module_name)
                # Reload it to pick up any changes
                importlib.reload(module)
            except Exception as e:
                logger.warning(f"Failed to load python module {module_name}: {e}")


def is_valid_script_path():
    """
    Checks if the automatically calculated _root_path is valid.

    Returns:
        bool: True if the path is a valid script path, False otherwise.
    """
    if not _root_path or not os.path.isdir(_root_path):
        return False

    py_loader_file = os.path.join(_root_path, "openpypeline", "app", "maya", "core", "opsLoader.py").replace("\\", "/")
    sub_folder = os.path.join(_root_path, "openpypeline").replace("\\", "/")

    if not os.path.isfile(py_loader_file):
        return False
    if not os.path.isdir(sub_folder):
        return False

    return True


def is_valid_project_file_path(folder):
    """
    Checks if the given folder is a valid project path (i.e., it exists).

    Args:
        folder (str): The path to be checked.

    Returns:
        bool: True if the path is valid, False otherwise.
    """
    return isinstance(folder, str) and os.path.isdir(folder)


class OpsSetupDialog(QtWidgets.QDialog):
    """PySide6 dialog for initializing openPypeline Studio paths."""
    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("openPypeline Studio Setup")
        self.setMinimumSize(405, 200)
        self.project_path_initial = project_path
        self._build_ui()
        
        # Post-init setup
        default_proj_path = os.path.join(_root_path, "openpypeline/").replace("\\", "/")
        if self.project_path_initial and self.project_path_initial != default_proj_path:
            self.toggle_project_path_field(force_custom=True, path=self.project_path_initial)

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Project File Setup
        proj_label = QtWidgets.QLabel("Project File Setup:")
        proj_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(proj_label)
        
        proj_desc = QtWidgets.QLabel('By default, the Project File will be located in the "openpypeline" folder.\nYou may set a different location for the Project File here.')
        proj_desc.setWordWrap(True)
        layout.addWidget(proj_desc)
        
        proj_layout = QtWidgets.QHBoxLayout()
        self.proj_field = QtWidgets.QLineEdit("[Default]")
        self.proj_field.setReadOnly(True)
        self.proj_toggle_btn = QtWidgets.QPushButton("Edit")
        self.proj_toggle_btn.clicked.connect(self.toggle_project_path_field)
        self.proj_browse_btn = QtWidgets.QPushButton("Browse...")
        self.proj_browse_btn.setEnabled(False)
        self.proj_browse_btn.clicked.connect(self.browse_proj_path)
        
        proj_layout.addWidget(self.proj_field)
        proj_layout.addWidget(self.proj_toggle_btn)
        proj_layout.addWidget(self.proj_browse_btn)
        layout.addLayout(proj_layout)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        accept_btn = QtWidgets.QPushButton("Accept")
        accept_btn.clicked.connect(self.setup_exec)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(accept_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_proj_path(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if dir_path:
            self.proj_field.setText(os.path.join(dir_path, "").replace("\\", "/"))

    def toggle_project_path_field(self, *args, force_custom=False, path=""):
        if not self.proj_field.isReadOnly() and not force_custom:
            self.proj_field.setReadOnly(True)
            self.proj_field.setText("[Default]")
            self.proj_toggle_btn.setText("Edit")
            self.proj_browse_btn.setEnabled(False)
        else:
            project_path = path if force_custom else prefs.get_pref(PROJECT_PATH_PREF, "")
            self.proj_field.setReadOnly(False)
            self.proj_field.setText(project_path)
            self.proj_toggle_btn.setText("Default")
            self.proj_browse_btn.setEnabled(True)

    def setup_exec(self):
        if not self.proj_field.isReadOnly():
            proj_file_path = self.proj_field.text()
        else:
            proj_file_path = os.path.join(_root_path, "openpypeline/").replace("\\", "/")

        proj_file_path = os.path.join(proj_file_path, "").replace("\\", "/")

        error = ""
        if not is_valid_script_path():
            error += f'Core framework path not valid. Missing essential files in "{_root_path}".\n'
        elif not is_valid_project_file_path(proj_file_path):
            error += f'Project File path not valid. Make sure path "{proj_file_path}" exists.\n'

        if not error:
            prefs.set_pref(PROJECT_PATH_PREF, proj_file_path)
            self.accept()
            openPypeline()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "openPypeline Studio - Project Setup Error",
                "Could not complete openPypeline Studio setup:\n" + error
            )


def openPypelineSetup():
    """
    Creates and shows the openPypeline Studio Setup UI.

    Returns:
        None
    """
    global _setup_dialog
    # --- Backward Compatibility Migration ---
    _migrate_legacy_prefs()

    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")

    _setup_dialog = OpsSetupDialog(project_path)
    _setup_dialog.show()


def openPypeline():
    """
    Main entry point for openPypeline Studio.

    Retrieves stored path configurations, validates them,
    sources all required modules, and launches the main UI.

    Returns:
        None
    """
    # --- Backward Compatibility Migration ---
    _migrate_legacy_prefs()

    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")

    error = ""

    if not is_valid_script_path():
        error += "Core script path is not valid. Essential files missing.\n"
    if not is_valid_project_file_path(project_path):
        error += "Project File path has not yet been set or could not be found.\n"

    if not error:
        logger.info("Paths are valid. Sourcing modules...")
        base_path = os.path.join(_root_path, "openpypeline", "").replace("\\", "/")
        addons_path = os.path.join(base_path, "addons", "").replace("\\", "/")
        custom_path = os.path.join(base_path, "custom", "").replace("\\", "/")

        source_python_module(addons_path)
        source_python_module(custom_path)
        
        # Add backend logic and the modernized UI paths to sys.path
        ui_path = os.path.join(base_path, "app", "maya", "ui").replace("\\", "/")
        backend_path = os.path.join(base_path, "app", "maya", "core", "openPypelineStudio").replace("\\", "/")
        
        for path in [_root_path, ui_path, backend_path]:
            if path not in sys.path:
                sys.path.insert(0, path)

        try:
            import UIObjects
            import opsMainUI
            UIObjects.UIObjects().opsMainUI = opsMainUI.opsMainUI()
            UIObjects.UIObjects().opsMainUI.showWindow()
        except Exception as e:
            logger.error(f"Failed to launch openPypelineUI: {e}")

    else:
        logger.warning("Paths are invalid or not set. Launching setup...")
        openPypelineSetup()