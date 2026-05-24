"""
File: opsInit.py
Description: Initializes all of the optionVars and configurations for openPypeline Studio.
             Refactored from openPipelineInit.mel (now opsInit.py) to use modern Python libraries.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import getpass

# Define module-level constants instead of global variables
OPENPIPELINE_NAME = "openPypeline Studio"
OPENPIPELINE_VERSION = "2.0.0-alpha"
OPENPIPELINE_PROJ_LIST = "openPypeline_projects.xml"
OPENPIPELINE_ICON_FILENAME = "openPypelineIcon.png"
OPENPIPELINE_DEFAULT_PREVIEW_FILENAME = "defaultPreview.png"
OPENPIPELINE_NO_PREVIEW_FILENAME = "noPreview.png"


def opsInitialize():
    """
    Initializes all of the optionVars for openPypeline Studio.
    """
    
    if not cmds.optionVar(exists="ops_currProjectName"):
        cmds.optionVar(stringValue=("ops_currProjectName", ""))
        
    if not cmds.optionVar(exists="ops_currentUser"):
        cmds.optionVar(stringValue=("ops_currentUser", "default"))
        
    # Define the optionVars to initialize with their types ('sv' for string, 'iv' for int) and default values
    option_vars = {
        "ops_currOpenType": ("sv", ""),
        "ops_currOpenCategory": ("sv", ""),
        "ops_currOpenVersion": ("iv", 0),
        "ops_currOpenLevel1": ("sv", ""),
        "ops_currOpenLevel2": ("sv", ""),
        "ops_currOpenLevel3": ("sv", ""),
        "ops_currOpenTab": ("iv", 0),
        "ops_currProjectPath": ("sv", ""),
        "ops_libPath": ("sv", ""),
        "ops_shotPath": ("sv", ""),
        "ops_scriptsPath": ("sv", ""),
        "ops_rendersPath": ("sv", ""),
        "ops_particlesPath": ("sv", ""),
        "ops_texturesPath": ("sv", ""),
        "ops_archivePath": ("sv", ""),
        "ops_deletePath": ("sv", ""),
        "ops_workshopFormat": ("sv", ""),
        "ops_masterFormat": ("sv", ""),
        "ops_workshopName": ("sv", ""),
        "ops_masterName": ("sv", ""),
    }
    
    # If there is no current project, we should force reset all optionVars below
    force_reset = (cmds.optionVar(query="ops_currProjectName") == "")
    
    for var_name, (var_type, default_val) in option_vars.items():
        if force_reset or not cmds.optionVar(exists=var_name):
            if var_type == "sv":
                cmds.optionVar(stringValue=(var_name, default_val))
            elif var_type == "iv":
                cmds.optionVar(intValue=(var_name, default_val))


def opsReset():
    """
    Resets all of the optionVars for openPypeline Studio.
    This reverts openPypeline Studio to a state in which no project is activated 
    and no item is open for editing.
    """
    cmds.optionVar(stringValue=("ops_currProjectName", ""))
    opsInitialize()