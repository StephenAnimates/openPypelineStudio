"""
File: loader.py
Description: Main initialization and setup script for openPypeline Studio in SideFX Houdini.
Provides the entry points to configure project paths, source modules, and launch the UI.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import sys
import logging

# Ensure root openpypeline package is in sys.path
_root_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
).replace("\\", "/")
if _root_path not in sys.path:
    sys.path.insert(0, _root_path)

from openpypeline.core.util import prefs

logger = logging.getLogger("openPypeline.houdini.loader")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(handler)

PROJECT_PATH_PREF = "ops_projectFilePath"


def is_valid_project_file_path(folder):
    """
    Checks if the given folder is a valid directory.

    Args:
        folder (str): Directory path to validate.

    Returns:
        bool: True if folder exists and is a directory.
    """
    return isinstance(folder, str) and os.path.isdir(folder)


def install_shelf(shelf_name="openPypeline"):
    """
    Creates or registers an openPypeline shelf tool on Houdini's shelf.

    Args:
        shelf_name (str): Name of the shelf tab.

    Returns:
        bool: True if created or updated, False if hou is unavailable.
    """
    try:
        import hou
    except ImportError:
        logger.warning("Houdini 'hou' module is not available.")
        return False

    try:
        shelves = hou.shelves.shelves()
        shelf = shelves.get(shelf_name)
        if not shelf:
            shelf = hou.shelves.newShelf(name=shelf_name, label="openPypeline")

        tool_name = "openpypeline_launch"
        tools = hou.shelves.tools()
        tool = tools.get(tool_name)
        tool_script = (
            "from openpypeline.app.houdini import loader\n"
            "loader.openPypeline()\n"
        )
        if not tool:
            tool = hou.shelves.newTool(
                name=tool_name,
                label="openPypeline",
                script=tool_script,
            )
        else:
            tool.setScript(tool_script)

        # Ensure tool is on the shelf
        shelf_tools = list(shelf.tools())
        if tool not in shelf_tools:
            shelf_tools.append(tool)
            shelf.setTools(shelf_tools)

        logger.info(f"Installed openPypeline shelf tool to '{shelf_name}'.")
        return True
    except Exception as e:
        logger.error(f"Failed to install Houdini shelf tool: {e}")
        return False


def openPypelineSetup():
    """
    Launches the openPypeline Studio Setup dialog in Houdini.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    logger.info(f"Configuring openPypeline Studio paths (current: '{project_path}')...")

    # In Houdini with PySide2/PySide6, launch the setup dialog
    try:
        from PySide6 import QtWidgets
    except ImportError:
        try:
            from PySide2 import QtWidgets
        except ImportError:
            QtWidgets = None

    if QtWidgets:
        from openpypeline.app.maya.core.ops_loader import OpsSetupDialog
        import hou
        parent = hou.qt.mainWindow() if hasattr(hou, "qt") else None
        dialog = OpsSetupDialog(project_path, parent=parent)
        dialog.exec_()
    else:
        logger.warning("Qt/PySide is not available in this Houdini session.")


def openPypeline():
    """
    Main entry point for openPypeline Studio in Houdini.
    Validates paths, initializes the engine, and launches the UI or diagnostic console.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    if not is_valid_project_file_path(project_path):
        logger.warning("Project path is not configured. Launching setup...")
        openPypelineSetup()
        return

    logger.info("Initializing openPypeline Studio in Houdini...")
    from openpypeline.ops_engine import OpsEngine
    engine = OpsEngine()
    logger.info(f"Engine initialized with host: {engine.host_app}")
    engine.ui()
