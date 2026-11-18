"""The central, DCC-agnostic pipeline engine for openPypeline Studio.

This module orchestrates the core data flow, detects the host application
dynamically, and delegates file operations to the appropriate application handlers.

:File: ops_engine.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example (Testing)::

    import sys
    sys.path.append("/path/to/openPypeline/openpypeline")

    import ops_engine
    import importlib
    importlib.reload(ops_engine)

    ops_engine.OpsEngine().ui()
"""

import os
import importlib
import sys
import logging

logger = logging.getLogger("openPypeline.engine")

def _get_workspace_root(host_app: str) -> str:
    """Gets the workspace root directory for the current host application or standalone process.
    This function attempts to retrieve the workspace root from the host-specific file adapter if available.
    If the host application does not provide a workspace root, it falls back to the current working directory.

    :param host_app: The name of the host application (e.g., 'maya', 'nuke', 'houdini', 'standalone').
    :returns: The absolute path to the workspace root directory as a string.
    """
    if host_app and host_app != "standalone":
        try:
            adapter = importlib.import_module(f"openpypeline.app.{host_app}.file.file")
            if hasattr(adapter, "get_workspace_root") and callable(adapter.get_workspace_root):
                return adapter.get_workspace_root()
        except Exception:
            pass
        if host_app == "maya":
            try:
                cmds = importlib.import_module("maya.cmds")
                return cmds.workspace(query=True, rootDirectory=True)
            except Exception:
                pass
    return os.getcwd()
class OpsEngine:
    """The main engine class that drives openPypeline Studio. It acts as the bridge between the UI/preferences, the core data models, and the host DCC.
    
    :param host_app: Optional. The name of the host application (e.g., 'maya', 'nuke', 'houdini'). If not provided, it will be auto-detected.
    :returns: An instance of the OpsEngine class, ready to manage pipeline operations.

    .. note::
        This class is designed to be DCC-agnostic and can operate in standalone mode if no host application is detected.
    """
    def __init__(self, host_app: str = None):
        """Detect the host application and load its file-operation adapter.

        :param host_app: Optional. The name of the host application (e.g., 'maya', 'nuke', 'houdini'). If not provided, it will be auto-detected.
        :returns: An instance of the OpsEngine class, ready to manage pipeline operations.
        
        .. note::
            This class is designed to be DCC-agnostic and can operate in standalone mode if no host application is detected."""
        # Detect the environment to adapt pipeline behaviors accordingly upon initialization
        self.host_app = host_app or self._detect_host_app()
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
        """Detects which host application is currently running the engine. Checks for known DCC-specific modules in sys.modules to determine the active host environment. New host applications can be added by extending the detection logic here.

        TODO: Change this so that the hosts can be detected without modifying this file. This needs a registry to set any new software host.

        :returns: A string representing the detected host application ('maya', 'nuke', 'houdini', 'blender', 'unreal', or 'standalone').

        .. note::
            This method checks for the presence of known host-specific modules in sys.modules to determine the active host environment.
        """
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

    def open_latest_workshop(self: any, item_path: any, item_name: any):
        """Open an item's latest WIP version in the active host application.

        :param item_path: The absolute path to the item's directory.
        :param item_name: The name of the item to open.
        :returns: True if the latest WIP was successfully opened, False otherwise.
        
        .. warning::
            This method relies on the host-specific file handler to perform the actual file opening operation. If no file handler is available, it will log a warning and return False.
        """
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

    def get_workspace_root(self:any):
        """Gets the active workspace root directory from the host application or standalone process.

        :returns: The absolute path to the active workspace root directory from the file handler as a string. Falling back to cwd.
        
        .. warning::
            This method delegates to the host-specific file handler if available. If no file handler is present, it falls back to the current working directory.
        """

        if self.file_handler and hasattr(self.file_handler, "get_workspace_root") and callable(self.file_handler.get_workspace_root):
            return self.file_handler.get_workspace_root()
        return _get_workspace_root(self.host_app)

    def ui(self:any):
        """The main entry point for the OpsEngine UI. This method initializes and displays the pipeline management interface, allowing users to interact with project items, versions, and file operations.
        
        Log inventory, version, master, and note status for the current selection. This diagnostic does not open or modify scene files.

        :returns: None

        .. note::
            This method is intended to be called from the host application's UI context. It will log relevant information about the current project and selection state for debugging and verification purposes.
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
            project = self.get_workspace_root()
            
        # Fetch the active UI selection states (Tab, Level 1/2/3) from preferences. Fallbacks are provided to allow testing outside of the actual UI.
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