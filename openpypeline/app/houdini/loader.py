"""Main initialization and setup script for openPypeline Studio in SideFX Houdini.

Configures ``sys.path`` for the repository root and provides entry points to
validate project paths, register a Houdini shelf tool, launch the setup
dialog, and start :class:`~openpypeline.ops_engine.OpsEngine`.

:File: loader.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import logging
import os
import sys

# Ensure root openpypeline package is in sys.path
_root_path: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
).replace("\\", "/")
if _root_path not in sys.path:
    sys.path.insert(0, _root_path)


#: Module logger for Houdini startup and shelf registration.
logger = logging.getLogger("openPypeline.houdini.loader")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)

from openpypeline.core.ops_loader import (  # noqa: E402
    PROJECT_PATH_PREF,
    is_valid_project_file_path,
)
from openpypeline.core.util import prefs  # noqa: E402


def install_shelf(shelf_name: str = "openPypeline") -> bool:
    """Create or update the openPypeline launch tool on a Houdini shelf.

    Creates the target shelf tab if absent, creates or updates the
    ``openpypeline_launch`` shelf tool script, and attaches the tool to the
    shelf.

    :param shelf_name: Internal name of the Houdini shelf tab.
    :returns: ``True`` if the shelf tool was created or updated, ``False`` if
        ``hou`` is unavailable or shelf registration fails.
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

        logger.info("Installed openPypeline shelf tool to '%s'.", shelf_name)
        return True
    except Exception as e:
        logger.error("Failed to install Houdini shelf tool: %s", e)
        return False


def openPypelineSetup() -> None:
    """Launch the openPypeline Studio path setup dialog in Houdini.

    Supports both Houdini builds bundled with ``PySide6`` (Houdini 20.5+) and
    older builds bundled with ``PySide2``, parenting
    :class:`~openpypeline.ui.ops_setup_dialog.OpsSetupDialog` to
    ``hou.qt.mainWindow()`` when available and invoking :func:`openPypeline`
    upon confirmation.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    logger.info(
        "Configuring openPypeline Studio paths (current: '%s')...",
        project_path,
    )

    # Support both PySide6 (Houdini 20.5+) and PySide2 (older Houdini releases)
    try:
        from PySide6 import QtWidgets
    except ImportError:
        try:
            from PySide2 import QtWidgets
        except ImportError:
            QtWidgets = None

    if QtWidgets:
        from openpypeline.ui.ops_setup_dialog import OpsSetupDialog

        try:
            import hou

            parent = hou.qt.mainWindow() if hasattr(hou, "qt") else None
        except ImportError:
            parent = None

        dialog = OpsSetupDialog(
            project_path, parent=parent, on_success=openPypeline
        )
        exec_fn = getattr(dialog, "exec", None) or dialog.exec_
        exec_fn()
    else:
        logger.warning("Qt/PySide is not available in this Houdini session.")


def openPypeline() -> None:
    """Main entry point for launching openPypeline Studio in Houdini.

    Validates :data:`PROJECT_PATH_PREF` (opening :func:`openPypelineSetup` if
    unconfigured), initializes :class:`~openpypeline.ops_engine.OpsEngine`,
    and launches the host UI.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    if not is_valid_project_file_path(project_path):
        logger.warning("Project path is not configured. Launching setup...")
        openPypelineSetup()
        return

    logger.info("Initializing openPypeline Studio in Houdini...")
    from openpypeline.ops_engine import OpsEngine

    engine = OpsEngine()
    logger.info("Engine initialized with host: %s", engine.host_app)
    engine.ui()
