"""
File: file.py
Description: Nuke-specific file handling operations for openPypeline Studio.
This module is dynamically loaded by OpsEngine when Nuke is detected.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import logging

try:
    import nuke
except ImportError:
    nuke = None

logger = logging.getLogger("openPypeline.nuke.file")

FILE_TYPES = {
    ".nk": "Nuke Script",
}


def get_file_type(extension):
    """Return Nuke's file type identifier for the given extension."""
    return FILE_TYPES.get(extension.lower()) if extension else None


def get_workspace_root():
    """Return Nuke's current script directory or working directory."""
    if nuke and hasattr(nuke, "root"):
        try:
            script_path = nuke.root().name()
            if script_path and os.path.exists(script_path):
                return os.path.dirname(script_path)
        except Exception:
            pass
    return os.getcwd()



def open(filepath):
    """
    Opens a Nuke script (.nk) given the filepath.

    Args:
        filepath (str): Full path to the Nuke script.

    Returns:
        bool: True if the file opened successfully, False otherwise.
    """
    if not os.path.exists(filepath):
        if nuke and hasattr(nuke, "message"):
            nuke.message(f"Error: File does not exist:\n{filepath}")
        else:
            logger.error(f"File does not exist: {filepath}")
        return False

    try:
        nuke.scriptOpen(filepath)
        logger.info(f"Successfully opened {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to open {filepath}. Error: {e}")
        return False


def save():
    """
    Saves the current Nuke script.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        nuke.scriptSave()
        logger.info("Successfully saved script.")
        return True
    except Exception as e:
        logger.error(f"Failed to save script. Error: {e}")
        return False


def save_as(filepath, file_type=None):
    """
    Saves the script to a new path.

    Args:
        filepath (str): Target file path.
        file_type (str, optional): Unused in Nuke (script format is .nk).

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        nuke.scriptSaveAs(filepath)
        logger.info(f"Successfully saved as {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save as {filepath}. Error: {e}")
        return False


def import_file(filepath):
    """
    Imports or pastes nodes from a Nuke script into the current script.

    Args:
        filepath (str): Path to the Nuke script or node file to import.

    Returns:
        bool: True if imported successfully, False otherwise.
    """
    if not os.path.exists(filepath):
        logger.error(f"File does not exist for import: {filepath}")
        return False

    try:
        nuke.nodePaste(filepath)
        logger.info(f"Successfully imported nodes from {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to import {filepath}. Error: {e}")
        return False


def reference_file(filepath):
    """
    References a file into the current Nuke script.

    Args:
        filepath (str): Path to the file to reference.

    Returns:
        bool: False (referencing protocol placeholder for Nuke).
    """
    logger.warning("reference_file is not yet implemented for Nuke.")
    return False


def new_file():
    """
    Creates a new empty script.

    Returns:
        bool: True if cleared successfully, False otherwise.
    """
    try:
        nuke.scriptClear()
        logger.info("Created new script.")
        return True
    except Exception as e:
        logger.error(f"Failed to create new script. Error: {e}")
        return False


def export_file(filepath, file_type=None, selected=False):
    """
    Exports the current script or selected nodes.

    Args:
        filepath (str): Destination path.
        file_type (str, optional): Export format.
        selected (bool): Whether to export only selected nodes.

    Returns:
        bool: False (export is not yet implemented for Nuke).
    """
    logger.warning("export_file is not yet implemented for Nuke.")
    return False


def is_modified():
    """
    Checks if the current Nuke script has unsaved changes.

    Returns:
        bool: True if unsaved changes exist, False otherwise.
    """
    try:
        return nuke.root().modified()
    except Exception:
        return False
