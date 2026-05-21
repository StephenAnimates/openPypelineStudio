"""
File: opsInit.py
Description: Initializes all of the optionVars and configurations for openPypeline Studio.
             Refactored from openPipelineInit.mel (now opsInit.py) to use modern Python libraries.
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
    
    if not cmds.optionVar(exists="op_currProjectName"):
        cmds.optionVar(stringValue=("op_currProjectName", ""))
        
    if not cmds.optionVar(exists="op_currentUser"):
        cmds.optionVar(stringValue=("op_currentUser", "default"))
        
    # Define the optionVars to initialize with their types ('sv' for string, 'iv' for int) and default values
    option_vars = {
        "op_currOpenType": ("sv", ""),
        "op_currOpenCategory": ("sv", ""),
        "op_currOpenVersion": ("iv", 0),
        "op_currOpenLevel1": ("sv", ""),
        "op_currOpenLevel2": ("sv", ""),
        "op_currOpenLevel3": ("sv", ""),
        "op_currOpenTab": ("iv", 0),
        "op_currProjectPath": ("sv", ""),
        "op_libPath": ("sv", ""),
        "op_shotPath": ("sv", ""),
        "op_scriptsPath": ("sv", ""),
        "op_rendersPath": ("sv", ""),
        "op_particlesPath": ("sv", ""),
        "op_texturesPath": ("sv", ""),
        "op_archivePath": ("sv", ""),
        "op_deletePath": ("sv", ""),
        "op_workshopFormat": ("sv", ""),
        "op_masterFormat": ("sv", ""),
        "op_workshopName": ("sv", ""),
        "op_masterName": ("sv", ""),
    }
    
    # If there is no current project, we should force reset all optionVars below
    force_reset = (cmds.optionVar(query="op_currProjectName") == "")
    
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
    cmds.optionVar(stringValue=("op_currProjectName", ""))
    opsInitialize()