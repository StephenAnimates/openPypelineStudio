"""
File: opsCreateDefaultItems.py
Description: openPypeline "Create Default Items" add-on refactored to Python.
             Populates the current project with a default set of assets and shots.
"""

import maya.cmds as cmds

def ops_createDefaultItems():
    """
    Prompts the user and then populates the current project with default items.
    """
    result = cmds.confirmDialog(
        title="Create Default Items",
        message="This procedure will populate the current project with some default items.\nTo see how this script works and to change it to fit your own specifications, see the file 'opsCreateDefaultItems.py'",
        button=["Continue", "Cancel"],
        defaultButton="Continue",
        cancelButton="Cancel",
        dismissString="Cancel"
    )

    if result != "Continue":
        return

    # List of default items to create
    # Format: (tab, level1, level2, level3, force)
    default_items = [
        # Assets
        (2, "characters", "man", "model", 1),
        (2, "characters", "man", "rig", 1),
        (2, "characters", "woman", "model", 1),
        (2, "characters", "woman", "rig", 1),
        (2, "characters", "dog", "model", 1),
        (2, "characters", "dog", "rig", 1),
        (2, "props", "chair", "model", 1),
        (2, "props", "chair", "rig", 1),
        (2, "props", "fork", "model", 1),
        (2, "props", "knife", "model", 1),
        (2, "props", "spoon", "model", 1),
        (2, "props", "cup", "model", 1),
        (2, "scenery", "kitchen", "model", 1),
        (2, "scenery", "livingRoom", "model", 1),
        (2, "scenery", "street", "model", 1),
        (2, "miscellaneous", "waterTests", "test1", 1),
        (2, "miscellaneous", "waterTests", "test2", 1),
        # Shots
        (3, "01", "01", "animation", 1),
        (3, "01", "01", "lighting", 1),
        (3, "01", "01", "effects", 1),
        (3, "01", "02", "animation", 1),
        (3, "01", "02", "lighting", 1),
        (3, "02", "01", "animation", 1),
        (3, "02", "01", "lighting", 1),
        (3, "02", "02", "animation", 1),
        (3, "02", "02", "lighting", 1),
        (3, "02", "02", "effects", 1),
        (3, "02", "03", "animation", 1),
        (3, "02", "03", "lighting", 1),
        (3, "02", "04", "animation", 1),
        (3, "02", "04", "lighting", 1),
    ]

    for item in default_items:
        tab, level1, level2, level3, force = item
        try:
            import openpypeline.app.maya.core.openPypelineStudio.opsActions as opsActions
            opsActions.create_new_item(tab, level1, level2, level3, force)
        except Exception as e:
            cmds.warning(f"Create Default Items Add-on error: {e}")

    if cmds.window("openPypelineUI", query=True, exists=True) or cmds.window("openPipelineUI", query=True, exists=True):
        try:
            import openpypeline.app.maya.core.openPypelineStudio.opsUIWrappers as opsUIWrappers
            opsUIWrappers.update_sequence_list()
            opsUIWrappers.update_asset_type_list()
        except Exception as e:
            cmds.warning(f"Create Default Items UI update error: {e}")