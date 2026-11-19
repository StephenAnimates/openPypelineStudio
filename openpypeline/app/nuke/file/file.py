"""Nuke-specific file handling operations for openPypeline Studio.

Implements the DCC file adapter interface dynamically loaded by ``OpsEngine`` when Foundry Nuke (``nuke``) is detected, covering script loading, saving, node-tree importing, workspace resolution, and unsaved-change queries.

:File: file.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import logging
import os
from typing import Optional

try:
    import nuke
except ImportError:
    nuke = None

#: Module logger for Nuke script I/O operations.
logger = logging.getLogger("openPypeline.nuke.file")

#: Mapping of supported Nuke script file extensions to human-readable labels.
FILE_TYPES: dict[str, str] = {
    ".nk": "Nuke Script",
}
def get_file_type(extension: Optional[str]) -> Optional[str]:
    """Return Nuke's file type description for the given extension.

    :param extension: File extension including leading dot (for example, ``".nk"``).
    :returns: Human-readable Nuke script type label, or ``None`` if unrecognized.
    """
    return FILE_TYPES.get(extension.lower()) if extension else None


def get_workspace_root() -> str:
    """Return Nuke's current script directory or process working directory.

    Inspects ``nuke.root().name()`` when running inside Nuke and falls back to :func:`os.getcwd` for unsaved scripts or headless sessions.

    :returns: Directory path representing the active Nuke workspace root.
    """
    if nuke and hasattr(nuke, "root"):
        try:
            script_path = nuke.root().name()
            if script_path and os.path.exists(script_path):
                return os.path.dirname(script_path)
        except Exception:
            pass
    return os.getcwd()


def open(filepath: str) -> bool:
    """Open a Nuke script (``.nk``) given its filesystem path.

    Displays a message dialog via ``nuke.message`` when running with Nuke's GUI available if ``filepath`` does not exist on disk.

    :param filepath: Full filesystem path to the Nuke script.
    :returns: ``True`` if the script opened successfully, ``False`` otherwise.
    """
    if not os.path.exists(filepath):
        if nuke and hasattr(nuke, "message"):
            nuke.message(f"Error: File does not exist:\n{filepath}")
        else:
            logger.error("File does not exist: %s", filepath)
        return False

    try:
        nuke.scriptOpen(filepath)
        logger.info("Successfully opened %s", filepath)
        return True
    except Exception as e:
        logger.error("Failed to open %s. Error: %s", filepath, e)
        return False


def save() -> bool:
    """Save the current Nuke script in place.

    :returns: ``True`` if saved successfully, ``False`` otherwise.
    """
    try:
        nuke.scriptSave()
        logger.info("Successfully saved script.")
        return True
    except Exception as e:
        logger.error("Failed to save script. Error: %s", e)
        return False


def save_as(filepath: str, file_type: Optional[str] = None) -> bool:
    """Save the current Nuke script to a new path.

    :param filepath: Target filesystem path.
    :param file_type: Unused in Nuke; accepted for DCC adapter signature compatibility.
    :returns: ``True`` if saved successfully, ``False`` otherwise.
    """
    del file_type
    try:
        nuke.scriptSaveAs(filepath)
        logger.info("Successfully saved as %s", filepath)
        return True
    except Exception as e:
        logger.error("Failed to save as %s. Error: %s", filepath, e)
        return False


def import_file(filepath: str) -> bool:
    """Paste nodes from an external Nuke script into the current script.

    :param filepath: Path to the Nuke script or node file to import.
    :returns: ``True`` if imported successfully, ``False`` otherwise.
    """
    if not os.path.exists(filepath):
        logger.error("File does not exist for import: %s", filepath)
        return False

    try:
        nuke.nodePaste(filepath)
        logger.info("Successfully imported nodes from %s", filepath)
        return True
    except Exception as e:
        logger.error("Failed to import %s. Error: %s", filepath, e)
        return False


def reference_file(filepath: str) -> bool:
    """Reference an external file into the current Nuke script.

    Currently a placeholder stub matching the cross-DCC file adapter contract.

    :param filepath: Path to the file to reference.
    :returns: Always ``False`` until Nuke referencing is implemented.
    """
    del filepath
    logger.warning("reference_file is not yet implemented for Nuke.")
    return False


def new_file() -> bool:
    """Clear the current Nuke session to start an empty script.

    :returns: ``True`` if cleared successfully, ``False`` otherwise.
    """
    try:
        nuke.scriptClear()
        logger.info("Created new script.")
        return True
    except Exception as e:
        logger.error("Failed to create new script. Error: %s", e)
        return False


def export_file(
    filepath: str,
    file_type: Optional[str] = None,
    selected: bool = False,
) -> bool:
    """Export the current Nuke script or selected nodes.

    Currently a placeholder stub matching the cross-DCC file adapter contract.

    :param filepath: Destination export file path.
    :param file_type: Optional target export format identifier.
    :param selected: Whether to export only currently selected nodes.
    :returns: Always ``False`` until Nuke export is implemented.
    """
    del filepath, file_type, selected
    logger.warning("export_file is not yet implemented for Nuke.")
    return False


def is_modified() -> bool:
    """Return whether the current Nuke script has unsaved changes.

    :returns: ``True`` if unsaved changes exist, ``False`` otherwise (or when ``nuke`` is unavailable).
    """
    try:
        return bool(nuke.root().modified())
    except Exception:
        return False
