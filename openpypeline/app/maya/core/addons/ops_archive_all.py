"""Maya add-on for bulk archiving, retrieving, or deleting library items.

Iterates across all asset and shot hierarchy levels in the active project to archive older WIP/master files, restore archived files, or move archived items to deleted storage via :mod:`openpypeline.core.ops_actions`.

:File: ops_archive_all.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from typing import Literal

try:
    import maya.cmds as cmds
except ImportError:
    cmds = None

from openpypeline.core import ops_actions as opsActions
from openpypeline.core import ops_info as opsInfo
from openpypeline.core.models import ItemContext, Tab
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers

#: Display name used by the main UI Tools menu when registering this add-on.
ADDON_NAME: str = "Archive All"


def run() -> None:
    """Create and display the Maya window for bulk archive operations."""
    if cmds is None:
        return

    if cmds.window("ops_secondaryUI", exists=True):
        cmds.deleteUI("ops_secondaryUI")

    cmds.window("ops_secondaryUI", title="oP - Archive All", width=300, height=300)
    cmds.columnLayout()

    cmds.separator(height=5, width=220, style="none")
    cmds.button(
        width=220,
        label="Archive All",
        command=lambda *args: ops_archiveAllProc(),
        bgc=[0.6, 0.7, 0.9],
    )

    cmds.separator(height=5, width=220, style="none")
    cmds.button(
        width=220,
        label="Retrieve All Archives",
        command=lambda *args: ops_retrieveArchiveAllProc(),
        bgc=[1, 1, 1],
    )

    cmds.separator(height=5, width=220, style="none")
    cmds.button(
        width=220,
        label="Delete All Archives",
        enable=True,
        command=lambda *args: ops_deleteArchiveAllProc(),
        bgc=[1, 0.7, 0.6],
    )

    cmds.separator(height=30, width=220, style="out")
    cmds.button(
        width=220,
        label="Close",
        command=lambda *args: cmds.deleteUI("ops_secondaryUI"),
    )

    cmds.window("ops_secondaryUI", edit=True, width=230, height=200)
    cmds.showWindow("ops_secondaryUI")


def _update_ui() -> None:
    """Refresh the openPypeline UI after a bulk archive operation."""
    if cmds is None:
        return

    if cmds.window("openPypelineUI", exists=True) or cmds.window(
        "openPipelineUI", exists=True
    ):
        try:
            opsUIWrappers.update_currently_open()
        except Exception:
            pass


def _process_all_archives(
    action: Literal["archive", "retrieve", "delete"],
) -> None:
    """Iterate through all asset and shot items and apply ``action``.

    :param action: Bulk archive operation to perform—one of ``"archive"``, ``"retrieve"``, or ``"delete"``.
    """
    tabs = [Tab.ASSET, Tab.SHOT]

    for tab in tabs:
        items1 = opsInfo.get_children(ItemContext(tab))
        for level1 in items1:
            items2 = opsInfo.get_children(ItemContext(tab, level1))
            for level2 in items2:
                levels_to_process: list[tuple[str, str, str]] = [
                    (level1, level2, "")
                ]

                items3 = opsInfo.get_children(ItemContext(tab, level1, level2))
                for level3 in items3:
                    levels_to_process.append((level1, level2, level3))

                for l1, l2, l3 in levels_to_process:
                    try:
                        context = ItemContext(tab, l1, l2, l3)
                        if action == "archive":
                            opsActions.archive_item(context, 1, 1)
                        elif action == "retrieve":
                            opsActions.retrieve_archive(context, 1, 1)
                        elif action == "delete":
                            opsActions.remove_archive(context)
                    except Exception as e:
                        if cmds is not None:
                            cmds.warning(f"Archive Add-on error: {e}")

    _update_ui()


def ops_archiveAllProc() -> None:
    """Archive older WIP and master files across the asset and shot libraries."""
    _process_all_archives("archive")


def ops_retrieveArchiveAllProc() -> None:
    """Retrieve archived files across the asset and shot libraries."""
    _process_all_archives("retrieve")


def ops_deleteArchiveAllProc() -> None:
    """Move archived files across the asset and shot libraries to deleted items."""
    _process_all_archives("delete")
