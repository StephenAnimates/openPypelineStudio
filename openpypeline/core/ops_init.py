"""Preference and configuration initialization for openPypeline Studio.

Initializes and resets default pipeline preferences and migrates legacy
``openPipeline`` option variables to their modern ``openPypeline`` equivalents.
Refactored from ``openPipelineInit.mel`` to use modern Python libraries.

:File: ops_init.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    from openpypeline.core import ops_init

    ops_init.opsInitialize()

"""

from typing import Any

from openpypeline.core.util import prefs

#: Display name of the studio pipeline suite.
OPENPIPELINE_NAME: str = "openPypeline Studio"
#: Current semantic version string of openPypeline Studio.
OPENPIPELINE_VERSION: str = "2.0.0-beta"
#: Default filename for the local JSON project registry.
OPENPIPELINE_PROJ_LIST: str = "openpypeline_projects.json"
#: Filename of the primary studio application icon.
OPENPIPELINE_ICON_FILENAME: str = "ops_icon.png"
#: Fallback preview thumbnail filename used when an item lacks a custom preview.
OPENPIPELINE_DEFAULT_PREVIEW_FILENAME: str = "ops_default_preview.png"
#: Placeholder preview thumbnail filename displayed when previews are unavailable.
OPENPIPELINE_NO_PREVIEW_FILENAME: str = "ops_no_preview.png"

# --- Pipeline System Options ---
#: Default folder and filename token for work-in-progress files (originally ``"workshop"``).
DEFAULT_WIP_DIR_NAME: str = "wip"
#: Default filename token for published master files.
DEFAULT_MASTER_DIR_NAME: str = "master"


def opsInitialize() -> None:
    """Initialize all default preferences for openPypeline Studio.

    Migrates legacy preference keys (``ops_workshopName`` and
    ``ops_workshopFormat``) to ``ops_wip`` and ``ops_wipFormat``, ensures
    ``ops_currProjectName`` and ``ops_currentUser`` are populated, and
    initializes all active session and project path preferences to their
    default values (forcing a reset when no project is currently active).
    """
    # --- Backward Compatibility Migration ---
    # Migrate legacy 'ops_workshopName' to the new 'ops_wip' variable
    if prefs.has_pref("ops_workshopName"):
        legacy_wip = prefs.get_pref("ops_workshopName")
        prefs.set_pref("ops_wip", legacy_wip)
        prefs.remove_pref("ops_workshopName")

    if prefs.has_pref("ops_workshopFormat"):
        legacy_format = prefs.get_pref("ops_workshopFormat")
        prefs.set_pref("ops_wipFormat", legacy_format)
        prefs.remove_pref("ops_workshopFormat")

    if not prefs.has_pref("ops_currProjectName"):
        prefs.set_pref("ops_currProjectName", "")

    if not prefs.has_pref("ops_currentUser"):
        prefs.set_pref("ops_currentUser", "default")

    # Define the preferences to initialize with their default values
    option_vars: dict[str, Any] = {
        "ops_currOpenType": "",
        "ops_currOpenCategory": "",
        "ops_currOpenVersion": 0,
        "ops_currOpenLevel1": "",
        "ops_currOpenLevel2": "",
        "ops_currOpenLevel3": "",
        "ops_currOpenTab": 0,
        "ops_currProjectPath": "",
        "ops_libPath": "",
        "ops_shotPath": "",
        "ops_scriptsPath": "",
        "ops_rendersPath": "",
        "ops_particlesPath": "",
        "ops_texturesPath": "",
        "ops_archivePath": "",
        "ops_deletePath": "",
        "ops_wipFormat": "",
        "ops_masterFormat": "",
        "ops_wip": DEFAULT_WIP_DIR_NAME,
        "ops_masterName": DEFAULT_MASTER_DIR_NAME,
    }

    # If there is no current project, we should force reset all preferences below
    force_reset = prefs.get_pref("ops_currProjectName") == ""

    for var_name, default_val in option_vars.items():
        if force_reset or not prefs.has_pref(var_name):
            prefs.set_pref(var_name, default_val)


def opsReset() -> None:
    """Reset all preferences for openPypeline Studio.

    Clears ``ops_currProjectName`` and invokes :func:`opsInitialize` to revert
    openPypeline Studio to a clean state where no project is active and no item
    is open for editing.
    """
    prefs.set_pref("ops_currProjectName", "")
    opsInitialize()
