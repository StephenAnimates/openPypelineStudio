"""Houdini-specific file handling operations for openPypeline Studio.

Implements the DCC file adapter interface dynamically loaded by ``OpsEngine`` when SideFX Houdini (``hou``) is detected, covering scene loading, saving, merging, workspace resolution, and unsaved-change queries.

:File: file.py
:Host: SideFX Houdini
:Status: In Progress
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import logging
import os
from typing import Optional

try:
    import hou
except ImportError:
    hou = None

#: Module logger for Houdini file I/O operations.
logger = logging.getLogger("openPypeline.houdini.file")

#: Mapping of supported Houdini scene file extensions to human-readable labels.
FILE_TYPES: dict[str, str] = {
    ".hip": "Houdini Scene",
    ".hiplc": "Houdini Limited Commercial",
    ".hipnc": "Houdini Non-Commercial",
}


def get_file_type(extension: Optional[str]) -> Optional[str]:
    """Return Houdini's file type description for the given extension.

    :param extension: File extension including leading dot (for example, ``".hip"`` or ``".hiplc"``).
    :returns: Human-readable Houdini scene type label, or ``None`` if unrecognized.
    """
    return FILE_TYPES.get(extension.lower()) if extension else None


def get_workspace_root() -> str:
    """Return Houdini's current scene directory or process working directory.

    Inspects ``hou.hipFile.path()`` when running inside Houdini and falls back to :func:`os.getcwd` for unsaved scenes or headless sessions.

    :returns: Directory path representing the active Houdini workspace root.
    """
    if hou and hasattr(hou, "hipFile"):
        try:
            hip_path = hou.hipFile.path()
            if hip_path and os.path.exists(hip_path):
                return os.path.dirname(hip_path)
        except Exception:
            pass
    return os.getcwd()


def open(filepath: str) -> bool:
    """Open a Houdini scene file (``.hip``, ``.hiplc``, or ``.hipnc``).

    Displays an error dialog via ``hou.ui.displayMessage`` when running with Houdini's GUI available if ``filepath`` does not exist on disk.

    :param filepath: Full filesystem path to the Houdini scene file.
    :returns: ``True`` if the file loaded successfully, ``False`` otherwise.
    """
    if not os.path.exists(filepath):
        if hou and hasattr(hou, "ui"):
            hou.ui.displayMessage(
                f"Error: File does not exist:\n{filepath}",
                severity=hou.severityType.Error,
            )
        else:
            logger.error("File does not exist: %s", filepath)
        return False

    try:
        hou.hipFile.load(filepath)
        logger.info("Successfully opened %s", filepath)
        return True
    except Exception as e:
        logger.error("Failed to open %s. Error: %s", filepath, e)
        return False


def save() -> bool:
    """Save the current Houdini scene in place.

    :returns: ``True`` if saved successfully, ``False`` otherwise.
    """
    try:
        hou.hipFile.save()
        logger.info("Successfully saved scene.")
        return True
    except Exception as e:
        logger.error("Failed to save scene. Error: %s", e)
        return False


def save_as(filepath: str, file_type: Optional[str] = None) -> bool:
    """Save the current Houdini scene to a new path.

    :param filepath: Target filesystem path (the file extension determines the Houdini license format).
    :param file_type: Unused in Houdini; accepted for DCC adapter signature compatibility.
    :returns: ``True`` if saved successfully, ``False`` otherwise.
    """
    del file_type
    try:
        hou.hipFile.save(filepath)
        logger.info("Successfully saved as %s", filepath)
        return True
    except Exception as e:
        logger.error("Failed to save as %s. Error: %s", filepath, e)
        return False


def import_file(filepath: str) -> bool:
    """Merge an external Houdini scene into the current scene.

    :param filepath: Path to the Houdini scene file to merge.
    :returns: ``True`` if merged successfully, ``False`` otherwise.
    """
    if not os.path.exists(filepath):
        logger.error("File does not exist for import: %s", filepath)
        return False

    try:
        hou.hipFile.merge(filepath)
        logger.info("Successfully imported/merged %s", filepath)
        return True
    except Exception as e:
        logger.error("Failed to import/merge %s. Error: %s", filepath, e)
        return False


def reference_file(filepath: str) -> bool:
    """Reference an external file into the current Houdini scene.

    Currently a placeholder stub matching the cross-DCC file adapter contract.

    :param filepath: Path to the file to reference.
    :returns: Always ``False`` until Houdini referencing is implemented.
    """
    del filepath
    logger.warning("reference_file is not yet implemented for Houdini.")
    return False


def new_file() -> bool:
    """Clear the current Houdini session to start an empty scene.

    :returns: ``True`` if cleared successfully, ``False`` otherwise.
    """
    try:
        hou.hipFile.clear()
        logger.info("Created new scene.")
        return True
    except Exception as e:
        logger.error("Failed to create new scene. Error: %s", e)
        return False


def export_file(
    filepath: str,
    file_type: Optional[str] = None,
    selected: bool = False,
) -> bool:
    """Export the current Houdini scene or selected nodes.

    Currently a placeholder stub matching the cross-DCC file adapter contract.

    :param filepath: Destination export file path.
    :param file_type: Optional target export format identifier.
    :param selected: Whether to export only currently selected nodes.
    :returns: Always ``False`` until Houdini export is implemented.
    """
    del filepath, file_type, selected
    logger.warning("export_file is not yet implemented for Houdini.")
    return False


def is_modified() -> bool:
    """Return whether the current Houdini scene has unsaved changes.

    :returns: ``True`` if unsaved changes exist, ``False`` otherwise (or when ``hou`` is unavailable).
    """
    try:
        return bool(hou.hipFile.hasUnsavedChanges())
    except Exception:
        return False
