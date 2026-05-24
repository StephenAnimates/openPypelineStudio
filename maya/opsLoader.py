"""
File: opsLoader.py
Description: Main initialization and setup script for openPypeline Studio in Maya.
             It provides a modern Python-based entry point to manage script
             and project path configurations using Maya optionVars, sources 
             necessary MEL and Python modules, and launches the main UI.
             
Original Framework: OpenPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
Source: 
"""

import maya.cmds as cmds
import os
import sys
import importlib
from functools import partial
import logging

# --- Logger Setup ---
logger = logging.getLogger("openPypeline")
logger.setLevel(logging.INFO) # Change to logging.DEBUG to see verbose file sourcing
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(name)s] %(levelname)s: %(message)s'))
    logger.addHandler(handler)

# --- Constants for UI element names ---
SETUP_WINDOW = "ops_setupWindow"
MAIN_PATH_TEXT_FIELD = "ops_mainPathTextField"
PROJ_PATH_TEXT_FIELD = "ops_mainProjPathTextField"
PROJ_PATH_TOGGLE_BUTTON = "ops_projPathToggleButton"
PROJ_PATH_BROWSE_BUTTON = "ops_projPathBrowseButton"

# --- Constants for optionVar keys ---
SCRIPT_PATH_OPTION_VAR = "ops_scriptPath"
PROJECT_PATH_OPTION_VAR = "ops_projectFilePath"

def source_python_module(path):
    """
    Adds a path to sys.path and imports/reloads all Python modules within it.

    Args:
        path (str): The directory path to look in.

    Returns:
        None
    """
    if not os.path.isdir(path):
        cmds.warning(f"Cannot source Python modules from non-existent path: {path}")
        return

    # Add path to sys.path if it's not already there
    if path not in sys.path:
        sys.path.append(path)
        print(f"Appending {path} to sys.path")

    print(f"----- Sourcing Python from {path} ------")
    for file_name in os.listdir(path):
        if file_name.endswith(".py") and not file_name.startswith("__"):
            module_name = os.path.splitext(file_name)[0]
            print(f"//// Python Source: {module_name}")
            try:
                # Import the module if it's the first time
                module = importlib.import_module(module_name)
                # Reload it to pick up any changes
                importlib.reload(module)
            except Exception as e:
                cmds.warning(f"Failed to load python module {module_name}: {e}")


def is_valid_script_path(folder):
    """
    Checks if the given folder is a valid script path.

    A valid path contains 'opsLoader.py' and an 'openpypeline' subfolder.

    Args:
        folder (str): The path to be checked.

    Returns:
        bool: True if the path is a valid script path, False otherwise.
    """
    if not folder or not os.path.isdir(folder):
        return False

    py_loader_file = os.path.join(folder, "opsLoader.py")
    root_folder = os.path.dirname(folder.rstrip("/\\"))
    sub_folder = os.path.join(root_folder, "openpypeline")

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
    return os.path.isdir(folder)


def set_text_field_path(field_name, path, *args):
    """
    Callback to set the text of a given text field.

    Note:
        Called directly by the browse file dialog.

    Args:
        field_name (str): The UI name of the text field.
        path (str): The path to set the field to.
        *args: Catches any extra arguments passed by Maya UI commands.

    Returns:
        None
    """
    cmds.textField(field_name, edit=True, text=path)


def browse_for_path(callback_func, *args):
    """
    Opens a directory browser and calls a callback function with the result.

    Args:
        callback_func (callable): The function to call with the selected path.
        *args: Catches any extra arguments passed by Maya UI commands.

    Returns:
        None
    """
    result = cmds.fileDialog2(fileMode=3, caption="Select Folder")
    if result and result[0]:
        # Ensure path has a trailing slash
        path = os.path.join(result[0], "").replace("\\", "/")
        callback_func(path)


def toggle_project_path_field(*args):
    """
    Toggles the project file path text field between 'Default' and custom input.

    Args:
        *args: Catches any extra arguments passed by Maya UI commands.

    Returns:
        None
    """
    is_editable = cmds.textField(PROJ_PATH_TEXT_FIELD, query=True, editable=True)
    if is_editable:
        cmds.textField(PROJ_PATH_TEXT_FIELD, edit=True, editable=False, text="[Default]")
        cmds.button(PROJ_PATH_TOGGLE_BUTTON, edit=True, label="Edit")
        cmds.button(PROJ_PATH_BROWSE_BUTTON, edit=True, enable=False)
    else:
        # Get the last known project path to populate the field
        project_path = cmds.optionVar(query=PROJECT_PATH_OPTION_VAR)
        cmds.textField(PROJ_PATH_TEXT_FIELD, edit=True, editable=True, text=project_path)
        cmds.button(PROJ_PATH_TOGGLE_BUTTON, edit=True, label="Default")
        cmds.button(PROJ_PATH_BROWSE_BUTTON, edit=True, enable=True)


def setup_exec(*args):
    """
    Validates and saves the paths from the setup UI, then re-initializes the pipeline.

    This method checks the user's input for validity, saves the configuration
    to Maya optionVars for persistence, and then initializes the pipeline's paths.

    Args:
        *args: Catches any extra arguments passed by Maya UI commands.

    Returns:
        None
    """
    script_path = cmds.textField(MAIN_PATH_TEXT_FIELD, query=True, text=True)
    # Ensure path has a trailing slash
    script_path = os.path.join(script_path, "").replace("\\", "/")

    if cmds.textField(PROJ_PATH_TEXT_FIELD, query=True, editable=True):
        proj_file_path = cmds.textField(PROJ_PATH_TEXT_FIELD, query=True, text=True)
    else:
        root_folder = os.path.dirname(script_path.rstrip("/\\"))
        proj_file_path = os.path.join(root_folder, "openpypeline/").replace("\\", "/")

    # Ensure project path also has a trailing slash
    proj_file_path = os.path.join(proj_file_path, "").replace("\\", "/")

    error = ""
    if not is_valid_script_path(script_path):
        error += f'Script path not valid. Make sure path "{script_path}" exists and contains the "openpypeline" folder and loader script.\n'
    elif not is_valid_project_file_path(proj_file_path):
        error += f'Project File path not valid. Make sure path "{proj_file_path}" exists.\n'

    if not error:
        # Save paths to optionVars for persistence
        cmds.optionVar(stringValue=(SCRIPT_PATH_OPTION_VAR, script_path))
        cmds.optionVar(stringValue=(PROJECT_PATH_OPTION_VAR, proj_file_path))

        if cmds.window(SETUP_WINDOW, exists=True):
            cmds.deleteUI(SETUP_WINDOW)

        # Re-run the main entry point to initialize with the new settings
        openPypeline()
    else:
        cmds.confirmDialog(
            title="openPypeline Studio - Project Setup Error",
            message="Could not complete openPypeline Studio setup:\n" + error,
            button=["Ok"],
            defaultButton="Ok"
        )


def openPypelineSetup():
    """
    Creates and shows the openPypeline Studio Setup UI.

    Returns:
        None
    """
    if cmds.window(SETUP_WINDOW, exists=True):
        cmds.deleteUI(SETUP_WINDOW)

    script_path = cmds.optionVar(query=SCRIPT_PATH_OPTION_VAR)
    project_path = cmds.optionVar(query=PROJECT_PATH_OPTION_VAR)

    cmds.window(SETUP_WINDOW, title="openPypeline Studio Setup", widthHeight=(405, 350), sizeable=False)

    with cmds.columnLayout(adjustableColumn=True, rowSpacing=5, co=("both", 10)):
        cmds.text(label="Script Path Setup:", font="boldLabelFont", align="left")
        cmds.text(label='Please specify the folder in which the "openpypeline" folder and loader scripts are located.', align="left")

        cmds.textField(MAIN_PATH_TEXT_FIELD, text=script_path, height=20)
        with cmds.rowLayout(numberOfColumns=2, columnWidth2=(325, 60)):
            cmds.text(label="")
            browse_cmd = partial(browse_for_path, partial(set_text_field_path, MAIN_PATH_TEXT_FIELD))
            cmds.button(label="Browse...", width=60, command=browse_cmd)

        cmds.separator(style="none", height=10)

        cmds.text(label="Project File Setup:", font="boldLabelFont", align="left")
        cmds.text(label='By default, the Project File will be located in the "openpypeline" folder.\nYou may set a different location for the Project File here.', align="left")

        cmds.textField(PROJ_PATH_TEXT_FIELD, editable=False, text="[Default]", height=20)
        with cmds.rowLayout(numberOfColumns=3, columnWidth3=(265, 60, 60)):
            cmds.text(label="")
            cmds.button(PROJ_PATH_TOGGLE_BUTTON, label="Edit", width=60, command=toggle_project_path_field)
            browse_cmd = partial(browse_for_path, partial(set_text_field_path, PROJ_PATH_TEXT_FIELD))
            cmds.button(PROJ_PATH_BROWSE_BUTTON, label="Browse...", width=60, enable=False, command=browse_cmd)

        cmds.separator(style="none", height=10)

        with cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190), columnAttach=[(1, 'both', 5), (2, 'both', 5)]):
            cmds.button(label="Accept", width=190, command=setup_exec)
            cmds.button(label="Cancel", width=190, command=lambda *args: cmds.deleteUI(SETUP_WINDOW))

    root_folder = os.path.dirname(script_path.rstrip("/\\"))
    if project_path and project_path != os.path.join(root_folder, "openpypeline/").replace("\\", "/"):
        toggle_project_path_field()
        cmds.textField(PROJ_PATH_TEXT_FIELD, edit=True, text=project_path)

    cmds.showWindow(SETUP_WINDOW)


def openPypeline():
    """
    Main entry point for openPypeline Studio.

    Retrieves stored path configurations, validates them,
    sources all required modules, and launches the main UI.

    Returns:
        None
    """
    script_path = cmds.optionVar(query=SCRIPT_PATH_OPTION_VAR) if cmds.optionVar(exists=SCRIPT_PATH_OPTION_VAR) else ""
    project_path = cmds.optionVar(query=PROJECT_PATH_OPTION_VAR) if cmds.optionVar(exists=PROJECT_PATH_OPTION_VAR) else ""

    scripts_folder_name = "openpypeline"
    error = ""

    if not is_valid_script_path(script_path):
        error += "Script path has not yet been set or is not valid.\n"
    if not is_valid_project_file_path(project_path):
        error += "Project File path has not yet been set or could not be found.\n"

    if not error:
        logger.info("Paths are valid. Sourcing modules...")
        root_path = os.path.dirname(script_path.rstrip("/\\"))
        base_path = os.path.join(root_path, scripts_folder_name, "").replace("\\", "/")
        addons_path = os.path.join(base_path, "addons", "").replace("\\", "/")
        custom_path = os.path.join(base_path, "custom", "").replace("\\", "/")

        source_python_module(addons_path)
        source_python_module(custom_path)
        
        # Add backend logic and the modernized UI paths to sys.path
        ui_path = os.path.join(base_path, "app", "maya", "ui").replace("\\", "/")
        backend_path = os.path.join(script_path, "openPypelineStudio").replace("\\", "/")
        for path in [root_path, ui_path, backend_path]:
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