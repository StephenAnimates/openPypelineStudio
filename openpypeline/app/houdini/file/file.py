"""
File: file.py
Description: Houdini-specific file handling operations for openPypeline Studio.
             This module is dynamically loaded by opsEngine when Houdini is detected.
"""

import hou
import os
import logging

logger = logging.getLogger("openPypeline.houdini.file")

def open(filepath):
    """
    Opens a Houdini scene file (.hip, .hiplc, .hipnc) given the filepath.
    """
    if not os.path.exists(filepath):
        hou.ui.displayMessage(f"Error: File does not exist:\n{filepath}", severity=hou.severityType.Error)
        return False
        
    try:
        hou.hipFile.load(filepath)
        logger.info(f"Successfully opened {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to open {filepath}. Error: {e}")
        return False

def save():
    """Saves the current Houdini scene."""
    hou.hipFile.save()

def import_file(filepath):
    """Merges a Houdini scene into the current scene."""
    if os.path.exists(filepath):
        hou.hipFile.merge(filepath)

def new_file():
    """Creates a new empty scene."""
    hou.hipFile.clear()
    logger.info("Created new scene.")
    return True

def save_as(filepath, file_type=None):
    """Saves the scene to a new path."""
    try:
        hou.hipFile.save(filepath)
        logger.info(f"Successfully saved as {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save as {filepath}. Error: {e}")
        return False

def export_file(filepath, file_type=None, selected=False):
    """Exports the current scene or selection."""
    # TODO: Implement Houdini specific export logic (e.g., save selected nodes)
    logger.warning("export_file is not yet implemented for Houdini.")
    return False