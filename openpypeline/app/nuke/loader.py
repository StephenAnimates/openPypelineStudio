"""
File: loader.py
Description: Main initialization and setup script for openPypeline Studio in Foundry Nuke.
Provides the entry points to configure project paths, source modules, and register menus.

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

logger = logging.getLogger("openPypeline.nuke.loader")
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


def install_menu(menu_name="openPypeline"):
    """
    Creates or registers an openPypeline menu on Nuke's main window menu bar.

    Args:
        menu_name (str): Name of the top-level menu.

    Returns:
        bool: True if menu items registered, False if nuke is unavailable.
    """
    try:
        import nuke
    except ImportError:
        logger.warning("Nuke 'nuke' module is not available.")
        return False

    try:
        main_menu = nuke.menu("Nuke")
        ops_menu = main_menu.findItem(menu_name)
        if not ops_menu:
            ops_menu = main_menu.addMenu(menu_name)

        ops_menu.addCommand(
            "Launch openPypeline",
            "import openpypeline.app.nuke.loader as loader; loader.openPypeline()",
        )
        ops_menu.addCommand(
            "Configure Setup...",
            "import openpypeline.app.nuke.loader as loader; loader.openPypelineSetup()",
        )
        logger.info(f"Registered openPypeline commands in Nuke menu '{menu_name}'.")
        return True
    except Exception as e:
        logger.error(f"Failed to register Nuke menu items: {e}")
        return False


def openPypelineSetup():
    """
    Launches the openPypeline Studio Setup dialog in Nuke.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    logger.info(f"Configuring openPypeline Studio paths (current: '{project_path}')...")

    # In Nuke with PySide2/PySide6, launch the setup dialog
    try:
        from PySide6 import QtWidgets
    except ImportError:
        try:
            from PySide2 import QtWidgets
        except ImportError:
            QtWidgets = None

    if QtWidgets:
        from openpypeline.app.maya.core.ops_loader import OpsSetupDialog
        import nuke
        # Parent to QApplication active window or Nuke's main window
        app = QtWidgets.QApplication.instance()
        parent = app.activeWindow() if app else None
        dialog = OpsSetupDialog(project_path, parent=parent)
        dialog.exec_()
    else:
        logger.warning("Qt/PySide is not available in this Nuke session.")


def openPypeline():
    """
    Main entry point for openPypeline Studio in Nuke.
    Validates paths, initializes the engine, and launches the UI or diagnostic console.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    if not is_valid_project_file_path(project_path):
        logger.warning("Project path is not configured. Launching setup...")
        openPypelineSetup()
        return

    logger.info("Initializing openPypeline Studio in Nuke...")
    from openpypeline.ops_engine import OpsEngine
    engine = OpsEngine()
    logger.info(f"Engine initialized with host: {engine.host_app}")
    engine.ui()
