"""
File: file.py
Description: Houdini-specific file handling operations for openPypeline Studio.
This module is dynamically loaded by OpsEngine when Houdini is detected.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import logging

try:
    import hou
except ImportError:
    hou = None

logger = logging.getLogger("openPypeline.houdini.file")

FILE_TYPES = {
    ".hip": "Houdini Scene",
    ".hiplc": "Houdini Limited Commercial",
    ".hipnc": "Houdini Non-Commercial",
}


def get_file_type(extension):
    """Return Houdini's file type identifier for the given extension."""
    return FILE_TYPES.get(extension.lower()) if extension else None


def get_workspace_root():
    """Return Houdini's current workspace directory or scene directory."""
    if hou and hasattr(hou, "hipFile"):
        try:
            hip_path = hou.hipFile.path()
            if hip_path and os.path.exists(hip_path):
                return os.path.dirname(hip_path)
        except Exception:
            pass
    return os.getcwd()



def open(filepath):
    """
    Opens a Houdini scene file (.hip, .hiplc, .hipnc) given the filepath.

    Args:
        filepath (str): Full path to the Houdini scene file.

    Returns:
        bool: True if the file opened successfully, False otherwise.
    """
    if not os.path.exists(filepath):
        if hou and hasattr(hou, "ui"):
            hou.ui.displayMessage(
                f"Error: File does not exist:\n{filepath}",
                severity=hou.severityType.Error,
            )
        else:
            logger.error(f"File does not exist: {filepath}")
        return False

    try:
        hou.hipFile.load(filepath)
        logger.info(f"Successfully opened {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to open {filepath}. Error: {e}")
        return False


def save():
    """
    Saves the current Houdini scene.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        hou.hipFile.save()
        logger.info("Successfully saved scene.")
        return True
    except Exception as e:
        logger.error(f"Failed to save scene. Error: {e}")
        return False


def save_as(filepath, file_type=None):
    """
    Saves the scene to a new path.

    Args:
        filepath (str): Target file path.
        file_type (str, optional): Unused in Houdini (format determined by extension).

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        hou.hipFile.save(filepath)
        logger.info(f"Successfully saved as {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save as {filepath}. Error: {e}")
        return False


def import_file(filepath):
    """
    Merges a Houdini scene into the current scene.

    Args:
        filepath (str): Path to the scene file to merge.

    Returns:
        bool: True if merged successfully, False otherwise.
    """
    if not os.path.exists(filepath):
        logger.error(f"File does not exist for import: {filepath}")
        return False

    try:
        hou.hipFile.merge(filepath)
        logger.info(f"Successfully imported/merged {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to import/merge {filepath}. Error: {e}")
        return False


def reference_file(filepath):
    """
    References a file into the current Houdini scene.

    Args:
        filepath (str): Path to the file to reference.

    Returns:
        bool: False (referencing protocol placeholder for Houdini).
    """
    logger.warning("reference_file is not yet implemented for Houdini.")
    return False


def new_file():
    """
    Creates a new empty scene.

    Returns:
        bool: True if created successfully, False otherwise.
    """
    try:
        hou.hipFile.clear()
        logger.info("Created new scene.")
        return True
    except Exception as e:
        logger.error(f"Failed to create new scene. Error: {e}")
        return False


def export_file(filepath, file_type=None, selected=False):
    """
    Exports the current scene or selection.

    Args:
        filepath (str): Destination path.
        file_type (str, optional): Export format.
        selected (bool): Whether to export only selected nodes.

    Returns:
        bool: False (export is not yet implemented for Houdini).
    """
    logger.warning("export_file is not yet implemented for Houdini.")
    return False


def is_modified():
    """
    Checks if the current scene has unsaved changes.

    Returns:
        bool: True if unsaved changes exist, False otherwise.
    """
    try:
        return hou.hipFile.hasUnsavedChanges()
    except Exception:
        return False
