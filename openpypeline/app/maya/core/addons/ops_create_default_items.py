"""
File: ops_create_default_items.py
Description: openPypeline "Create Default Items" add-on refactored to Python.
             Populates the current project with a default set of assets and shots.
"""

import maya.cmds as cmds

try:
    from openpypeline.core.models import ItemContext, Tab
except ImportError:
    pass

ADDON_NAME = "Create Default Items"

def run():
    """
    Prompts the user and then populates the current project with default items.
    """
    result = cmds.confirmDialog(
        title="Create Default Items",
        message="This procedure will populate the current project with some default items.\nTo see how this script works and to change it to fit your own specifications, see the file 'ops_create_default_items.py'",
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
        (Tab.ASSET, "characters", "man", "model", 1),
        (Tab.ASSET, "characters", "man", "rig", 1),
        (Tab.ASSET, "characters", "woman", "model", 1),
        (Tab.ASSET, "characters", "woman", "rig", 1),
        (Tab.ASSET, "characters", "dog", "model", 1),
        (Tab.ASSET, "characters", "dog", "rig", 1),
        (Tab.ASSET, "props", "chair", "model", 1),
        (Tab.ASSET, "props", "chair", "rig", 1),
        (Tab.ASSET, "props", "fork", "model", 1),
        (Tab.ASSET, "props", "knife", "model", 1),
        (Tab.ASSET, "props", "spoon", "model", 1),
        (Tab.ASSET, "props", "cup", "model", 1),
        (Tab.ASSET, "scenery", "kitchen", "model", 1),
        (Tab.ASSET, "scenery", "livingRoom", "model", 1),
        (Tab.ASSET, "scenery", "street", "model", 1),
        (Tab.ASSET, "miscellaneous", "waterTests", "test1", 1),
        (Tab.ASSET, "miscellaneous", "waterTests", "test2", 1),
        # Shots
        (Tab.SHOT, "01", "01", "animation", 1),
        (Tab.SHOT, "01", "01", "lighting", 1),
        (Tab.SHOT, "01", "01", "effects", 1),
        (Tab.SHOT, "01", "02", "animation", 1),
        (Tab.SHOT, "01", "02", "lighting", 1),
        (Tab.SHOT, "02", "01", "animation", 1),
        (Tab.SHOT, "02", "01", "lighting", 1),
        (Tab.SHOT, "02", "02", "animation", 1),
        (Tab.SHOT, "02", "02", "lighting", 1),
        (Tab.SHOT, "02", "02", "effects", 1),
        (Tab.SHOT, "02", "03", "animation", 1),
        (Tab.SHOT, "02", "03", "lighting", 1),
        (Tab.SHOT, "02", "04", "animation", 1),
        (Tab.SHOT, "02", "04", "lighting", 1),
    ]

    for item in default_items:
        tab, level1, level2, level3, force = item
        try:
            from .. import ops_actions as opsActions
            context = ItemContext(tab, level1, level2, level3)
            opsActions.create_new_item(context, force)
        except Exception as e:
            cmds.warning(f"Create Default Items Add-on error: {e}")

    if cmds.window("openPypelineUI", query=True, exists=True) or cmds.window("openPipelineUI", query=True, exists=True):
        try:
            from .. import ops_ui_wrappers as opsUIWrappers
            opsUIWrappers.update_sequence_list()
            opsUIWrappers.update_asset_type_list()
        except Exception as e:
            cmds.warning(f"Create Default Items UI update error: {e}")