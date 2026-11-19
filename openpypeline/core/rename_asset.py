"""Utility to rename an asset directory and all matching nested files/folders.

Safely traverses the asset directory tree bottom-up (``topdown=False``) so
child paths are renamed before their parent directories, preventing broken
filesystem paths during traversal.

:File: rename_asset.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core import rename_asset

    rename_asset.renameAsset("/path/to/project/lib/old_asset_name", "new_asset_name")
"""

import logging
import os

#: Module logger for asset directory and file rename operations.
logger = logging.getLogger("openPypeline.renameAsset")


def renameAsset(folderPath: str, newName: str, oldName: str = "") -> None:
    """Rename an asset directory and all matching files and subdirectories.

    Walks ``folderPath`` bottom-up, replacing occurrences of ``oldName`` with
    ``newName`` in filenames, subdirectory names, and finally the top-level
    asset directory itself. Logs an error and aborts if ``newName`` already
    exists alongside ``folderPath``.

    :param folderPath: Absolute path to the top-level asset directory to rename.
    :param newName: Replacement asset name applied to matching files and folders.
    :param oldName: Original asset name to replace. When omitted or empty, inferred from the base directory name of ``folderPath``.
    """
    # Clean up the folder path to accurately get the base name (remove trailing slashes)
    folderPath = folderPath.rstrip("/\\")

    # If an explicit old name isn't provided, assume it's the name of the target folder
    if not oldName:
        oldName = os.path.basename(folderPath)

    # Determine the parent directory to construct the final destination path
    parentDir = os.path.dirname(folderPath)
    newDirPath = os.path.join(parentDir, newName)

    # Safety check: ensure we don't accidentally overwrite an existing asset
    if os.path.isdir(newDirPath):
        logger.error(f"An asset named '{newName}' already exists.")
        return

    # Walk bottom-up (topdown=False) so renaming child directories doesn't break the paths we still need to traverse for the parent directories.
    for root, dirs, files in os.walk(folderPath, topdown=False):
        # First, rename all matching files within the current directory level
        for filename in files:
            if oldName in filename:
                logger.info(f"Renaming file: {filename}")
                newFileName = filename.replace(oldName, newName)
                os.rename(os.path.join(root, filename), os.path.join(root, newFileName))

        # Next, rename all matching subdirectories within the current directory level
        for dirname in dirs:
            if oldName in dirname:
                logger.info(f"Renaming directory: {dirname}")
                newDirName = dirname.replace(oldName, newName)
                os.rename(os.path.join(root, dirname), os.path.join(root, newDirName))

    # Finally, rename the top-level directory itself to complete the asset rename
    logger.info(f"Renaming top-level directory: {oldName} -> {newName}")
    os.rename(folderPath, newDirPath)
