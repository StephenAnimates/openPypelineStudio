"""
File: opsEngine.py
Description: The central, DCC-agnostic pipeline engine for openPypeline Studio.
             This module orchestrates the core data flow, detects the host application
             dynamically, and delegates file operations to the appropriate application handlers.

Usage Example (Testing):
'''
import sys
sys.path.append("/path/to/openPypeline/openpypeline")

import opsEngine
import importlib
importlib.reload(opsEngine)

opsEngine.OpsEngine().ui()
'''

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import importlib
import sys
import logging

logger = logging.getLogger("openPypeline.engine")

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
                module_path = f"app.{self.host_app}.file.file"
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

    def ui(self):
        """
        Executes a diagnostic routine that simulates a core pipeline interaction.
        It loads modules, retrieves preferences, queries the inventory, and evaluates 
        the status (versions, master, notes) of items in the current working directory.
        """
        # --- 1. Load Core Modules ---
        # Reload modules to ensure the latest code is executing (useful for development)
        from core.file import inventory
        importlib.reload(inventory)

        from core.version import Version
        importlib.reload(Version)
        
        from core.file import master
        importlib.reload(master)

        from openpypeline.core.file import wip
        importlib.reload(wip)
        
        from core.notes import notes
        importlib.reload(notes)
        
        # --- 2. Retrieve Preferences ---
        from core.util import prefs
        importlib.reload(prefs)
        
        # Determine the project root, falling back to the host workspace if none is set
        project = prefs.get_pref("ops_currProjectPath", "")
        if not project:
            logger.warning("'ops_currProjectPath' preference is not set. Using host workspace root as fallback.")
            project = prefs.get_workspace_root()
            
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
                
            # --- 4. Attempt File Operation ---
            # Finally, find the latest workshop version and attempt to open it in the host DCC
            getLatestWorkshopNumber = Version.Version().latest(fullpath)
            if getLatestWorkshopNumber is not None:
                latestWorkshop = wip.WIP().open(fullpath, item, getLatestWorkshopNumber)
                if self.file_handler and hasattr(self.file_handler, 'open'):
                    self.file_handler.open(latestWorkshop)
                else:
                    logger.warning(f"Would open {latestWorkshop} (no DCC file handler available)")
                