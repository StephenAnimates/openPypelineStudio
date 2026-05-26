"""
File: file.py
Description: Maya-specific file handling operations for openPypeline Studio.
             This module is dynamically loaded by opsEngine when Maya is detected.
"""

import maya.cmds as cmds
import os
import logging

logger = logging.getLogger("openPypeline.maya.file")

def _ensure_plugins_loaded(filepath=None, file_type=None):
    """Helper to ensure required plugins are loaded based on file extension or type."""
    ext = os.path.splitext(filepath)[-1].lower() if filepath else ""
    
    if ext in ['.usd', '.usda', '.usdc'] or file_type == "USD Export":
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            try: cmds.loadPlugin("mayaUsdPlugin")
            except Exception as e: logger.error(f"Failed to load Maya USD Plugin: {e}")
            
    if ext == '.abc' or file_type == "Alembic":
        for plugin in ["AbcImport", "AbcExport"]:
            if not cmds.pluginInfo(plugin, query=True, loaded=True):
                try: cmds.loadPlugin(plugin)
                except Exception as e: logger.error(f"Failed to load {plugin}: {e}")

def open(filepath):
    """
    Opens a Maya scene file (.ma, .mb) or supported container given the filepath.
    """
    if not os.path.exists(filepath):
        cmds.warning(f"openPypeline Studio: File does not exist: {filepath}")
        return False
        
    _ensure_plugins_loaded(filepath=filepath)
    
    try:
        cmds.file(filepath, force=True, open=True)
        logger.info(f"Successfully opened {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to open {filepath}. Error: {e}")
        return False

def save():
    """Saves the current Maya scene."""
    try:
        cmds.file(save=True)
        logger.info("Successfully saved scene.")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to save. Error: {e}")
        return False

def import_file(filepath):
    """Imports a file into the current Maya scene."""
    _ensure_plugins_loaded(filepath=filepath)
    
    try:
        cmds.file(filepath, i=True)
        logger.info(f"Successfully imported {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to import {filepath}. Error: {e}")
        return False

def reference_file(filepath):
    """References a file into the current Maya scene."""
    _ensure_plugins_loaded(filepath=filepath)
    
    try:
        cmds.file(filepath, reference=True)
        logger.info(f"Successfully referenced {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to reference {filepath}. Error: {e}")
        return False

def new_file():
    """Creates a new empty scene."""
    try:
        cmds.file(force=True, newFile=True)
        logger.info("Created new scene.")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to create new scene. Error: {e}")
        return False

def save_as(filepath, file_type=None):
    """Renames and saves the current scene."""
    try:
        cmds.file(rename=filepath)
        kwargs = {"save": True}
        if file_type:
            kwargs["type"] = file_type
        cmds.file(**kwargs)
        logger.info(f"Successfully saved as {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to save as {filepath}. Error: {e}")
        return False

def export_file(filepath, file_type=None, selected=False):
    """Exports the current scene or selection to a file."""
    _ensure_plugins_loaded(filepath=filepath, file_type=file_type)
                
    try:
        kwargs = {"force": True}
        if file_type:
            kwargs["type"] = file_type
            
        if selected:
            kwargs["exportSelected"] = True
        else:
            kwargs["exportAll"] = True
            # Only pass Maya-specific export flags if using a native Maya format
            if file_type in ["mayaAscii", "mayaBinary", None]:
                kwargs["preserveReferences"] = True
                kwargs["constructionHistory"] = True
                kwargs["channels"] = True
                kwargs["constraints"] = True
                kwargs["expressions"] = True
                kwargs["shader"] = True
            
        cmds.file(filepath, **kwargs)
        logger.info(f"Successfully exported to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to export {filepath}. Error: {e}")
        return False

def flatten_references(master_name, workshop_name):
    """Flattens the scene by importing all referenced files."""
    referenced_files = cmds.file(query=True, reference=True) or []
    if not referenced_files:
        logger.warning("openPypeline Studio: no references to import")
        return
        
    for ref in referenced_files:
        if cmds.file(ref, query=True, deferReference=True):
            msg = (f"Referenced file '{ref}' is currently unloaded and cannot be imported.\n"
                   f"Would you like to keep or remove this reference in the {master_name} file (it will remain in the {workshop_name} file)?")
            result = cmds.confirmDialog(title="openPypeline Studio", message=msg, button=["Keep", "Remove"], defaultButton="Keep")
            if result == "Remove": cmds.file(ref, removeReference=True)
        else:
            cmds.file(ref, importReference=True)
            logger.info(f"{ref} imported into current file")

def delete_display_layers():
    """Deletes all display layers except defaultLayer."""
    layers = cmds.ls(type="displayLayer") or []
    for layer in layers:
        if layer != "defaultLayer":
            cmds.delete(layer)