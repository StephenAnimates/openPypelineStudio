"""
File: ops_engine.py
Description: The central, DCC-agnostic pipeline engine for openPypeline Studio.
             This module orchestrates the core data flow, detects the host application
             dynamically, and delegates file operations to the appropriate application handlers.

Usage Example (Testing):
'''
import sys
sys.path.append("/path/to/openPypeline/openpypeline")

import ops_engine
import importlib
importlib.reload(ops_engine)

ops_engine.OpsEngine().ui()
'''

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import importlib
import sys
import logging

logger = logging.getLogger("openPypeline.engine")


def _get_workspace_root(host_app):
    """Return a workspace root for the active host or standalone process."""
    if host_app == "maya":
        cmds = importlib.import_module("maya.cmds")
        return cmds.workspace(query=True, rootDirectory=True)
    return os.getcwd()


class OpsEngine:
    """
    The main engine class that drives openPypeline Studio.
    It acts as the bridge between the UI/preferences, the core data models, and the host DCC.
    """
    def __init__(self):
        # Detect the environment to adapt pipeline behaviors accordingly upon initialization
        self.host_app = self._detect_host_app()
        logger.info(f"Initialized OpsEngine. Detected host: {self.host_app}")
        
        # Load DCC-Specific File Handler
        self.file_handler = None
        if self.host_app != 'standalone':
            try:
                module_path = (
                    f"openpypeline.app.{self.host_app}.file.file"
                )
                self.file_handler = importlib.import_module(module_path)
                importlib.reload(self.file_handler)
            except ImportError:
                logger.warning(f"Could not load file handler for host '{self.host_app}' at {module_path}.")
        
    def _detect_host_app(self):
        """Detects which host application is currently running the engine."""
        # Check loaded system modules for standard DCC libraries to deduce the active host
        if 'maya' in sys.modules or 'maya.cmds' in sys.modules:
            return 'maya'
        elif 'nuke' in sys.modules:
            return 'nuke'
        elif 'hou' in sys.modules:
            return 'houdini'
        elif 'bpy' in sys.modules:
            return 'blender'
        elif 'unreal' in sys.modules:
            return 'unreal'
        return 'standalone'

    def open_latest_workshop(self, item_path, item_name):
        """Open an item's latest WIP version in the active host application."""
        from openpypeline.core.version import Version
        from openpypeline.core.file import wip

        latest_version = Version.Version().latest(item_path)
        if latest_version is None:
            logger.warning("No WIP versions found for %s", item_path)
            return False

        latest_workshop = wip.WIP().open(
            item_path,
            item_name,
            latest_version,
        )
        if not latest_workshop:
            logger.warning("Could not resolve latest WIP file for %s", item_path)
            return False
        if not self.file_handler or not hasattr(self.file_handler, "open"):
            logger.warning(
                "Would open %s (no DCC file handler available)",
                latest_workshop,
            )
            return False
        return self.file_handler.open(latest_workshop)

    def ui(self):
        """
        Log inventory, version, master, and note status for the current selection.
        This diagnostic does not open or modify scene files.
        """
        # --- 1. Load Core Modules ---
        # Reload modules to ensure the latest code is executing (useful for development)
        from openpypeline.core.file import inventory
        importlib.reload(inventory)

        from openpypeline.core.version import Version
        importlib.reload(Version)

        from openpypeline.core.file import master
        importlib.reload(master)
        
        from openpypeline.core.notes import notes
        importlib.reload(notes)
        
        # --- 2. Retrieve Preferences ---
        from openpypeline.core.util import prefs
        importlib.reload(prefs)
        
        # Determine the project root, falling back to the host workspace if none is set
        project = prefs.get_pref("ops_currProjectPath", "")
        if not project:
            logger.warning("'ops_currProjectPath' preference is not set. Using host workspace root as fallback.")
            project = _get_workspace_root(self.host_app)
            
        # Fetch the active UI selection states (Tab, Level 1/2/3) from preferences
        # Fallbacks are provided to allow testing outside of the actual UI
        tab = prefs.get_pref("ops_currOpenTab", 2)
        level1 = prefs.get_pref("ops_currOpenLevel1", "")
        level2 = prefs.get_pref("ops_currOpenLevel2", "")
        level3 = prefs.get_pref("ops_currOpenLevel3", "")
            
        module = "lib" if tab == 2 else "scenes"
        item_type = level1 if level1 else "characters"
        asset = level2 if level2 else "woman"
        component = level3 if level3 else "model"
        
        # Construct an ordered list of path elements, ignoring empty values
        elements = [e for e in [project, module, item_type, asset, component] if e]
        
        # --- 3. Query Inventory and Evaluate Items ---
        # Ask the inventory module what items actually exist at the evaluated path
        inv = inventory.Inventory(elements).list()
        logger.debug(f"Inventory list: {inv}")
        
        for item in inv:
            # Build the full absolute path for each discovered item
            path = inventory.Inventory(elements).getPath()
            fullpath = os.path.join(path, item)
            logger.debug(f"Checking path: {fullpath}")
            
            # Check what workshop versions are available
            versions = Version.Version().all(fullpath)
            logger.debug(f"Versions found: {versions}")
            
            # Check if this item has been finalized as a Master
            hasMaster = master.Master().query(fullpath)
            if hasMaster == 1:
                logger.debug(f"{item}: mastered")
            else:
                logger.debug(f"{item}: not mastered")
            
            # Check if artists have left XML notes for this item
            hasNotes = notes.Notes().query(fullpath, item)
            if hasNotes == 1:
                logger.debug(f"{item}: has notes")
            else:
                logger.debug(f"{item}: no notes")
                
            latest_version = max(versions) if versions else None
            logger.debug("%s: latest WIP version is %s", item, latest_version)