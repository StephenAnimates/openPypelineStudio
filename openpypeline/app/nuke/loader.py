"""Main initialization and setup script for openPypeline Studio in Foundry Nuke.

Configures ``sys.path`` for the repository root and provides entry points to
register a top-level Nuke menu, launch the cross-DCC path setup dialog, and
start :class:`~openpypeline.ops_engine.OpsEngine`.

:File: loader.py
:Host: Foundry Nuke
:Status: In Progress
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
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

from openpypeline.core.ops_loader import (  # noqa: E402
    PROJECT_PATH_PREF,
    is_valid_project_file_path,
)
from openpypeline.core.util import prefs  # noqa: E402

#: Module logger for Nuke startup and menu registration.
logger = logging.getLogger("openPypeline.nuke.loader")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)


def install_menu(menu_name: str = "openPypeline") -> bool:
    """Create or register an openPypeline menu on Nuke's main window menu bar.

    :param menu_name: Top-level menu label added to ``nuke.menu("Nuke")``.
    :returns: ``True`` if menu commands were registered, ``False`` if ``nuke``
        is unavailable or registration fails.
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
        logger.info(
            "Registered openPypeline commands in Nuke menu '%s'.", menu_name
        )
        return True
    except Exception as e:
        logger.error("Failed to register Nuke menu items: %s", e)
        return False


def openPypelineSetup() -> None:
    """Launch the openPypeline Studio path setup dialog in Nuke.

    Supports both Nuke builds bundled with ``PySide6`` (Nuke 15+) and older
    builds bundled with ``PySide2``, parenting
    :class:`~openpypeline.ui.ops_setup_dialog.OpsSetupDialog` to the active Qt
    window when available and invoking :func:`openPypeline` upon confirmation.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    logger.info(
        "Configuring openPypeline Studio paths (current: '%s')...",
        project_path,
    )

    # Support both PySide6 (Nuke 15+) and PySide2 (older Nuke releases)
    try:
        from PySide6 import QtWidgets
    except ImportError:
        try:
            from PySide2 import QtWidgets
        except ImportError:
            QtWidgets = None

    if QtWidgets:
        from openpypeline.ui.ops_setup_dialog import OpsSetupDialog

        app = QtWidgets.QApplication.instance()
        parent = app.activeWindow() if app else None

        dialog = OpsSetupDialog(
            project_path, parent=parent, on_success=openPypeline
        )
        exec_fn = getattr(dialog, "exec", None) or dialog.exec_
        exec_fn()
    else:
        logger.warning("Qt/PySide is not available in this Nuke session.")


def openPypeline() -> None:
    """Main entry point for launching openPypeline Studio in Nuke.

    Validates :data:`~openpypeline.core.ops_loader.PROJECT_PATH_PREF` (opening
    :func:`openPypelineSetup` if unconfigured), initializes
    :class:`~openpypeline.ops_engine.OpsEngine`, and launches the host UI.
    """
    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    if not is_valid_project_file_path(project_path):
        logger.warning("Project path is not configured. Launching setup...")
        openPypelineSetup()
        return

    logger.info("Initializing openPypeline Studio in Nuke...")
    from openpypeline.ops_engine import OpsEngine

    engine = OpsEngine()
    logger.info("Engine initialized with host: %s", engine.host_app)
    engine.ui()
