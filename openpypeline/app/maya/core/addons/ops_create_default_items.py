"""Maya add-on for populating the active project with default assets and shots.

Prompts the artist via a Maya confirmation dialog and creates a sample set of
asset types, assets, components, sequences, and shots via
:func:`~openpypeline.core.ops_actions.create_new_item`.

:File: ops_create_default_items.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

try:
    import maya.cmds as cmds
except ImportError:
    cmds = None

from openpypeline.core import ops_actions as opsActions
from openpypeline.core.models import ItemContext, Tab
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers

#: Display name used by the main UI Tools menu when registering this add-on.
ADDON_NAME: str = "Create Default Items"

#: Sample asset and shot entries ``(tab, level1, level2, level3, force)``.
_DEFAULT_ITEMS: tuple[tuple[Tab, str, str, str, int], ...] = (
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
)


def run() -> None:
    """Prompt the user and populate the active project with default items."""
    if cmds is None:
        return

    result = cmds.confirmDialog(
        title="Create Default Items",
        message=(
            "This procedure will populate the current project with some default items.\n"
            "To see how this script works and to change it to fit your own specifications, "
            "see the file 'ops_create_default_items.py'"
        ),
        button=["Continue", "Cancel"],
        defaultButton="Continue",
        cancelButton="Cancel",
        dismissString="Cancel",
    )

    if result != "Continue":
        return

    for tab, level1, level2, level3, force in _DEFAULT_ITEMS:
        try:
            context = ItemContext(tab, level1, level2, level3)
            opsActions.create_new_item(context, force)
        except Exception as e:
            cmds.warning(f"Create Default Items Add-on error: {e}")

    if cmds.window("openPypelineUI", query=True, exists=True) or cmds.window(
        "openPipelineUI", query=True, exists=True
    ):
        try:
            opsUIWrappers.update_sequence_list()
            opsUIWrappers.update_asset_type_list()
        except Exception as e:
            cmds.warning(f"Create Default Items UI update error: {e}")
