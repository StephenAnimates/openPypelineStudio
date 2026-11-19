"""Main initialization and setup script for openPypeline Studio in Maya.

Migrates legacy Maya ``optionVar`` entries, validates paths via
:mod:`openpypeline.core.ops_loader`, sources Maya ``addons/`` and ``custom/``
modules, registers :mod:`openpypeline.app.maya.core.file_use` scene callbacks,
and launches :class:`~openpypeline.app.maya.ui.ops_main_controller.OpsMainController`.

:File: ops_loader.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import logging
import os
import sys
from typing import Optional

from PySide6 import QtWidgets

# Ensure repository root is registered before importing openpypeline packages
_root_path: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
).replace("\\", "/")
if _root_path not in sys.path:
    sys.path.insert(0, _root_path)

from openpypeline.core import ops_loader as core_loader  # noqa: E402
from openpypeline.core.ops_loader import (  # noqa: E402
    PROJECT_PATH_PREF,
    is_valid_project_file_path,
    is_valid_script_path,
    source_python_module,
)
from openpypeline.core.util import prefs  # noqa: E402
from openpypeline.ui.ops_setup_dialog import OpsSetupDialog  # noqa: E402

#: Module logger for openPypeline Studio Maya startup and setup events.
logger = logging.getLogger("openPypeline")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)

#: Active setup dialog reference retained to prevent premature garbage collection.
_setup_dialog: Optional[QtWidgets.QDialog] = None


def _migrate_legacy_prefs() -> None:
    """Migrate legacy Maya ``optionVar`` entries to the DCC-agnostic prefs system.

    Copies ``openPipeline_projectFilePath`` and ``ops_projectFilePath`` from
    ``maya.cmds.optionVar`` into :mod:`~openpypeline.core.util.prefs` under
    :data:`PROJECT_PATH_PREF` and removes the legacy ``optionVar`` keys. Safely
    no-ops when executed outside Autodesk Maya.
    """
    try:
        import maya.cmds as cmds

        migrations = [
            ("openPipeline_projectFilePath", PROJECT_PATH_PREF),
            (PROJECT_PATH_PREF, PROJECT_PATH_PREF),
        ]
        for old_var, new_pref in migrations:
            if cmds.optionVar(exists=old_var) and not prefs.has_pref(new_pref):
                prefs.set_pref(new_pref, cmds.optionVar(query=old_var))
                cmds.optionVar(remove=old_var)
    except ImportError:
        pass


def openPypelineSetup() -> None:
    """Create and display the openPypeline Studio setup dialog in Maya.

    Migrates legacy Maya ``optionVar`` preferences via :func:`_migrate_legacy_prefs`, reads :data:`PROJECT_PATH_PREF`, and displays a non-modal :class:`~openpypeline.ui.ops_setup_dialog.OpsSetupDialog` configured to call :func:`openPypeline` upon acceptance.
    """
    global _setup_dialog
    _migrate_legacy_prefs()

    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
    _setup_dialog = OpsSetupDialog(project_path, on_success=openPypeline)
    _setup_dialog.show()


def openPypeline() -> None:
    """Main entry point for launching openPypeline Studio in Maya.

    Migrates legacy Maya preferences via :func:`_migrate_legacy_prefs`,
    validates script and project paths, sources optional Maya ``addons/`` and
    ``custom/`` modules, installs synchronized file-use scene callbacks via
    :func:`~openpypeline.app.maya.core.file_use.install_callbacks`, and launches
    :class:`~openpypeline.app.maya.ui.ops_main_controller.OpsMainController`.
    Falls back to :func:`openPypelineSetup` if required paths are missing or
    invalid.
    """
    _migrate_legacy_prefs()

    project_path = prefs.get_pref(PROJECT_PATH_PREF, "")

    error = ""
    if not is_valid_script_path():
        error += "Core script path is not valid. Essential files missing.\n"
    if not is_valid_project_file_path(project_path):
        error += "Project File path has not yet been set or could not be found.\n"

    if not error:
        logger.info("Paths are valid. Sourcing modules...")
        maya_core_path = os.path.dirname(__file__)
        addons_path = os.path.join(maya_core_path, "addons", "").replace("\\", "/")
        custom_path = os.path.join(maya_core_path, "custom", "").replace("\\", "/")

        source_python_module(addons_path)
        source_python_module(custom_path)

        if _root_path not in sys.path:
            sys.path.insert(0, _root_path)

        try:
            from openpypeline.app.maya.core import file_use

            file_use.install_callbacks()
        except Exception as e:
            logger.error("Failed to install synchronized file-use notices: %s", e)

        try:
            from openpypeline.app.maya.ui import (
                ops_main_controller as opsMainController,
            )
            from openpypeline.ui import ui_objects as UIObjects

            controller = opsMainController.OpsMainController()
            UIObjects.UIObjects().opsMainController = controller
            UIObjects.UIObjects().opsMainUI = controller.view
            controller.showWindow()
        except Exception as e:
            logger.error("Failed to launch openPypelineUI: %s", e)
    else:
        logger.warning("Paths are invalid or not set. Launching setup...")
        openPypelineSetup()


__all__ = [
    "PROJECT_PATH_PREF",
    "_root_path",
    "core_loader",
    "is_valid_project_file_path",
    "is_valid_script_path",
    "openPypeline",
    "openPypelineSetup",
    "source_python_module",
]
