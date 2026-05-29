"""
File: opsArchiveAll.py
Description: openPypeline "Archive All" add-on refactored to Python.
             Archives, retrieves, or deletes all items in the library.
"""

import maya.cmds as cmds

try:
    from .. import ops_info as opsInfo
except ImportError:
    pass


def ops_archiveAll():
    if cmds.window("ops_secondaryUI", exists=True):
        cmds.deleteUI("ops_secondaryUI")

    cmds.window("ops_secondaryUI", title="oP - Archive All", width=300, height=300)
    cmds.columnLayout()
    
    cmds.separator(height=5, width=220, style="none")
    cmds.button(width=220, label="Archive All", command=lambda *args: ops_archiveAllProc(), bgc=[0.6, 0.7, 0.9])
    
    cmds.separator(height=5, width=220, style="none")
    cmds.button(width=220, label="Retrieve All Archives", command=lambda *args: ops_retrieveArchiveAllProc(), bgc=[1, 1, 1])
    
    cmds.separator(height=5, width=220, style="none")
    cmds.button(width=220, label="Delete All Archives", enable=True, command=lambda *args: ops_deleteArchiveAllProc(), bgc=[1, 0.7, 0.6])
    
    cmds.separator(height=30, width=220, style="out")
    cmds.button(width=220, label="Close", command=lambda *args: cmds.deleteUI("ops_secondaryUI"))
    
    cmds.window("ops_secondaryUI", edit=True, width=230, height=200)
    cmds.showWindow("ops_secondaryUI")


def _update_ui():
    """Helper function to update the UI after an operation."""
    if cmds.window("openPypelineUI", exists=True) or cmds.window("openPipelineUI", exists=True):
        try:
            from .. import ops_ui_wrappers as opsUIWrappers
            opsUIWrappers.update_currently_open()
        except (ImportError, AttributeError):
            pass


def _process_all_archives(action):
    """
    Helper to iterate through all items and apply an archive action.
    action parameter should be one of: 'archive', 'retrieve', 'delete'
    """
    tabs = [2, 3]  # Asset library and shot library tabs
    
    for tab in tabs:
        items1 = opsInfo.get_children(tab, "", "", "")
        for level1 in items1:
            items2 = opsInfo.get_children(tab, level1, "", "")
            for level2 in items2:
                
                levels_to_process = [(level1, level2, "")]
                
                items3 = opsInfo.get_children(tab, level1, level2, "")
                for level3 in items3:
                    levels_to_process.append((level1, level2, level3))
                    
                for l1, l2, l3 in levels_to_process:
                    try:
                        from .. import ops_actions as opsActions
                        if action == 'archive': opsActions.archive_item(tab, l1, l2, l3, 1, 1)
                        elif action == 'retrieve': opsActions.retrieve_archive(tab, l1, l2, l3, 1, 1)
                        elif action == 'delete': opsActions.remove_archive(tab, l1, l2, l3)
                    except Exception as e:
                        cmds.warning(f"Archive Add-on error: {e}")
    
    _update_ui()


def ops_archiveAllProc():
    _process_all_archives('archive')


def ops_retrieveArchiveAllProc():
    _process_all_archives('retrieve')


def ops_deleteArchiveAllProc():
    _process_all_archives('delete')