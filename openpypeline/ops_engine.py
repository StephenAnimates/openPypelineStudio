"""The central, DCC-agnostic pipeline engine for openPypeline Studio.

This module orchestrates the core data flow, detects the host application dynamically, and delegates file operations to the appropriate application handlers.

:File: ops_engine.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)

Usage Example (Testing)::

    import sys
    sys.path.append("/path/to/openPypeline/openpypeline")

    import ops_engine
    import importlib
    importlib.reload(ops_engine)

    ops_engine.OpsEngine().ui()

"""

import importlib
import logging
import os
import sys
from types import ModuleType
from typing import Optional

#: Module logger for core pipeline engine operations.
logger = logging.getLogger("openPypeline.engine")


# TODO: Refactor workspace resolution to use an extensible host adapter registry so new DCC hosts can provide workspace paths without modifying this function.
def _get_workspace_root(host_app: str) -> str:
    """Get the workspace root directory for the active host application.

    Attempts to retrieve the workspace root from the host-specific file adapter (``openpypeline.app.<host_app>.file.file``) when available, falling back to Maya's active workspace or ``os.getcwd()`` in standalone mode.

    :param host_app: Identifier for the active host application (for example,
        ``"maya"``, ``"nuke"``, ``"houdini"``, or ``"standalone"``).
    :returns: The absolute path to the workspace root directory.
    """
    if host_app and host_app != "standalone":
        try:
            adapter = importlib.import_module(f"openpypeline.app.{host_app}.file.file")
            if callable(getattr(adapter, "get_workspace_root", None)):
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
    """Main pipeline engine driving openPypeline Studio.

    Acts as the central bridge between the UI, user preferences, core data models, and the active host DCC application.

    :ivar host_app: Identifier of the active host application (for example,
        ``"maya"``, ``"nuke"``, ``"houdini"``, or ``"standalone"``).
    :vartype host_app: str
    :ivar file_handler: Loaded host-specific file adapter module, or ``None`` when running in standalone mode or if loading fails.
    :vartype file_handler: Optional[ModuleType]

    .. note::
       Designed to be DCC-agnostic and operates in ``"standalone"`` mode whenever no supported host application is detected.
    """

    def __init__(self, host_app: Optional[str] = None) -> None:
        """Detect the host application and load its file-operation adapter.

        :param host_app: Optional identifier for the host application
            (``"maya"``, ``"nuke"``, ``"houdini"``, ``"blender"``, or
            ``"unreal"``). Auto-detected via :meth:`_detect_host_app` when
            omitted.
        """
        # Detect the environment to adapt pipeline behaviors accordingly upon initialization
        self.host_app: str = host_app or self._detect_host_app()
        logger.info(f"Initialized OpsEngine. Detected host: {self.host_app}")

        # Load DCC-Specific File Handler
        self.file_handler = None
        if self.host_app != "standalone":
            module_path = f"openpypeline.app.{self.host_app}.file.file"
            try:
                self.file_handler = importlib.import_module(module_path)
                importlib.reload(self.file_handler)
            except ImportError:
                logger.warning(
                    f"Could not load file handler for host '{self.host_app}' at {module_path}."
                )
    
    # TODO: Refactor host detection to use an extensible registry so new DCC hosts can be registered without modifying this method.
    def _detect_host_app(self) -> str:
        """Detect which host application is currently running the engine.

        Inspects ``sys.modules`` for known DCC-specific libraries to deduce the active host environment, defaulting to ``"standalone"`` when no supported host module is loaded.

        :returns: Identifier for the detected host application (``"maya"``,
            ``"nuke"``, ``"houdini"``, ``"blender"``, ``"unreal"``, or
            ``"standalone"``).
        """
        # Check loaded system modules for standard DCC libraries to deduce the active host
        if "maya" in sys.modules or "maya.cmds" in sys.modules:
            return "maya"
        elif "nuke" in sys.modules:
            return "nuke"
        elif "hou" in sys.modules:
            return "houdini"
        elif "bpy" in sys.modules:
            return "blender"
        elif "unreal" in sys.modules:
            return "unreal"
        return "standalone"


    def open_latest_workshop(self, item_path: str, item_name: str) -> bool:
        """Open an item's latest WIP version in the active host application.

        Resolves the highest available WIP version number for ``item_name`` inside
        ``item_path`` and delegates opening the file to :attr:`file_handler`.

        :param item_path: The absolute path to the item's directory.
        :param item_name: The name of the item to open.
        :returns: ``True`` if the latest WIP was successfully opened, ``False`` otherwise.

        .. note::
            This method relies on the host-specific :attr:`file_handler` to perform the actual file opening operation. If no file handler is available, it logs a warning and returns ``False``.
        """
        from openpypeline.core.file import wip
        from openpypeline.core.version import Version

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
        return bool(self.file_handler.open(latest_workshop))

    def get_workspace_root(self) -> str:
        """Get the active workspace root directory from the host application.

        Queries :attr:`file_handler` when available, otherwise falls back to resolving the workspace root for :attr:`host_app` (or the current working directory in standalone mode).

        :returns: The absolute path to the active workspace root directory.

        .. note::
            Delegates to the host-specific :attr:`file_handler` when present; otherwise uses the standalone fallback resolver for :attr:`host_app`.
        """
        if callable(getattr(self.file_handler, "get_workspace_root", None)):
            return self.file_handler.get_workspace_root()
        return _get_workspace_root(self.host_app)

    def ui(self) -> None:
        """Evaluate and log inventory, version, master, and note status for the active selection.

        Reads the active project path and selection state from user preferences (falling back to :meth:`get_workspace_root` and default test values when unset), queries available inventory items, and logs version, master, and XML note status without opening or modifying scene files.

        .. note::
           Intended for diagnostic verification from a host application's UI or script editor context. Reloads core pipeline modules on each call to reflect live code changes during development.
        """
        # --- 1. Load Core Modules ---
        # Reload modules to ensure the latest code is executing (useful for development)
        from openpypeline.core.file import inventory, master
        from openpypeline.core.notes import notes
        from openpypeline.core.util import prefs
        from openpypeline.core.version import Version

        importlib.reload(inventory)
        importlib.reload(Version)
        importlib.reload(master)
        importlib.reload(notes)

        # --- 2. Retrieve Preferences ---
        importlib.reload(prefs)

        # Determine the project root, falling back to the host workspace if none is set
        project = prefs.get_pref("ops_currProjectPath", "")
        if not project:
            logger.warning(
                "'ops_currProjectPath' preference is not set. Using host workspace root as fallback."
            )
            project = self.get_workspace_root()

        # Fetch the active UI selection states (Tab, Level 1/2/3) from preferences.
        # Fallbacks are provided to allow testing outside of the actual UI.
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
        inv_handler = inventory.Inventory(elements)
        inv = inv_handler.list()
        path = inv_handler.getPath()
        logger.debug(f"Inventory list: {inv}")

        for item in inv:
            # Build the full absolute path for each discovered item
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
