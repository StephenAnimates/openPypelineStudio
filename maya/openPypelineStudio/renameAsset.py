"""
File: renameAsset.py
Description: Utility to rename an asset and all associated files/folders within openPypeline Studio.
             It safely traverses the directory structure bottom-up to ensure paths aren't broken
             during the rename process.

Usage:
    import renameAsset
    renameAsset.renameAsset("/path/to/project/lib/old_asset_name", "new_asset_name")

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import logging

logger = logging.getLogger("openPypeline.renameAsset")

def renameAsset(folderPath, newName, oldName=''):
    """
    Renames an asset directory and all of its contents (files and subdirectories)
    that match the old asset name.
    
    Args:
        folderPath (str): The absolute path to the top-level directory of the asset to rename.
        newName (str): The new name to apply to the asset and its contents.
        oldName (str, optional): The original name of the asset. If omitted, it is inferred
                                 from the base name of the folderPath.
    """
    # Clean up the folder path to accurately get the base name (remove trailing slashes)
    folderPath = folderPath.rstrip('/\\')
    
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
        
    # Walk bottom-up (topdown=False) so renaming child directories doesn't break the paths
    # we still need to traverse for the parent directories.
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
			