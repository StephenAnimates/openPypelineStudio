"""
File: file.py
Description: Nuke-specific file handling operations for openPypeline Studio.
             This module is dynamically loaded by opsEngine when Nuke is detected.
"""

import nuke
import os
import logging

logger = logging.getLogger("openPypeline.nuke.file")

def open(filepath):
    """
    Opens a Nuke script (.nk) given the filepath.
    """
    if not os.path.exists(filepath):
        nuke.message(f"Error: File does not exist:\n{filepath}")
        return False
        
    try:
        nuke.scriptOpen(filepath)
        logger.info(f"Successfully opened {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to open {filepath}. Error: {e}")
        return False

def save():
    """Saves the current Nuke script."""
    nuke.scriptSave()

def new_file():
    """Creates a new empty script."""
    nuke.scriptClear()
    logger.info("Created new script.")
    return True

def save_as(filepath, file_type=None):
    """Saves the script to a new path."""
    try:
        nuke.scriptSaveAs(filepath)
        logger.info(f"Successfully saved as {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save as {filepath}. Error: {e}")
        return False

def export_file(filepath, file_type=None, selected=False):
    """Exports the current script or selection."""
    # TODO: Implement Nuke specific export logic (e.g., node export)
    logger.warning("export_file is not yet implemented for Nuke.")
    return False