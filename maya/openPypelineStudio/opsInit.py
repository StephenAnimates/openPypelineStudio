"""
File: opsInit.py
Description: Initializes all of the preferences and configurations for openPypeline Studio.
             Refactored from openPipelineInit.mel (now opsInit.py) to use modern Python libraries.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import getpass
from openpypeline.core.util import prefs

# Define module-level constants instead of global variables
OPENPIPELINE_NAME = "openPypeline Studio"
OPENPIPELINE_VERSION = "2.0.0-alpha"
OPENPIPELINE_PROJ_LIST = "openPypeline_projects.xml"
OPENPIPELINE_ICON_FILENAME = "openPypelineIcon.png"
OPENPIPELINE_DEFAULT_PREVIEW_FILENAME = "defaultPreview.png"
OPENPIPELINE_NO_PREVIEW_FILENAME = "noPreview.png"

# --- Pipeline System Options ---
DEFAULT_WIP_DIR_NAME = "wip"     # Originally "workshop"
DEFAULT_MASTER_DIR_NAME = "master"

def opsInitialize():
    """
    Initializes all of the preferences for openPypeline Studio.
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
    option_vars = {
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
    force_reset = (prefs.get_pref("ops_currProjectName") == "")
    
    for var_name, default_val in option_vars.items():
        if force_reset or not prefs.has_pref(var_name):
            prefs.set_pref(var_name, default_val)


def opsReset():
    """
    Resets all of the preferences for openPypeline Studio.
    This reverts openPypeline Studio to a state in which no project is activated 
    and no item is open for editing.
    """
    prefs.set_pref("ops_currProjectName", "")
    opsInitialize()