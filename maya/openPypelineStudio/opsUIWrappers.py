"""
File: opsUIWrappers.py
Description: UI action wrappers for openPypeline Studio.
             Connects the UI button commands to the core opsActions logic.
             Replaces the legacy wrapper dialogs from openPipelineUI.mel.
"""

import maya.cmds as cmds
import maya.mel as mel
import os
import opsInfo
import opsActions

def refresh_ui(*args):
    """Calls the UI update functions to reflect the latest file state."""
    try:
        mel.eval("openPipelineUpdateCurrentlyOpen();")
        mel.eval("openPipelineUpdateAssetTypeList();")
        mel.eval("openPipelineUpdateSequenceList();")
    except Exception as e:
        cmds.warning(f"UI Refresh warning: {e}")

def open_currently_selected(tab, level, item_type, version_offset=0, *args):
    levels = opsInfo.get_currently_selected_item(tab, level)
    if opsActions.open_item(item_type, tab, levels[0], levels[1], levels[2], version_offset):
        refresh_ui()

def import_selected(tab, level, item_type, *args):
    levels = opsInfo.get_currently_selected_item(tab, level)
    opsActions.import_item(item_type, tab, levels[0], levels[1], levels[2], "")

def reference_selected(tab, level, item_type, *args):
    levels = opsInfo.get_currently_selected_item(tab, level)
    opsActions.reference_item(item_type, tab, levels[0], levels[1], levels[2], "")

def remove_process(tab, depth, *args):
    levels = opsInfo.get_currently_selected_item(tab, depth)
    if opsActions.remove_item(tab, levels[0], levels[1], levels[2]):
        refresh_ui()

def explore_selected(tab, *args):
    levels = opsInfo.get_currently_selected_item(tab, 3)
    opsActions.open_location(tab, levels[0], levels[1], levels[2])

def explore_current(*args):
    tab = cmds.optionVar(query="op_currOpenTab")
    level1 = cmds.optionVar(query="op_currOpenLevel1")
    level2 = cmds.optionVar(query="op_currOpenLevel2")
    level3 = cmds.optionVar(query="op_currOpenLevel3")
    opsActions.open_location(tab, level1, level2, level3)

def view_playblast_selected(tab, *args):
    levels = opsInfo.get_currently_selected_item(tab, 3)
    opsActions.view_playblast(tab, levels[0], levels[1], levels[2])

def view_playblast_current(*args):
    tab = cmds.optionVar(query="op_currOpenTab")
    level1 = cmds.optionVar(query="op_currOpenLevel1")
    level2 = cmds.optionVar(query="op_currOpenLevel2")
    level3 = cmds.optionVar(query="op_currOpenLevel3")
    opsActions.view_playblast(tab, level1, level2, level3)

def record_current_playblast(*args):
    tab = cmds.optionVar(query="op_currOpenTab")
    level1 = cmds.optionVar(query="op_currOpenLevel1")
    level2 = cmds.optionVar(query="op_currOpenLevel2")
    level3 = cmds.optionVar(query="op_currOpenLevel3")
    opsActions.record_playblast(tab, level1, level2, level3)
    refresh_ui()

def take_snapshot(*args):
    tab = cmds.optionVar(query="op_currOpenTab")
    level1 = cmds.optionVar(query="op_currOpenLevel1")
    level2 = cmds.optionVar(query="op_currOpenLevel2")
    level3 = cmds.optionVar(query="op_currOpenLevel3")
    img = opsActions.create_thumbnail(tab, level1, level2, level3)
    if os.path.isfile(img):
        cmds.image("op_currOpenPreview_img", edit=True, image=img)

def save_note(*args):
    tab = cmds.optionVar(query="op_currOpenTab")
    level1 = cmds.optionVar(query="op_currOpenLevel1")
    level2 = cmds.optionVar(query="op_currOpenLevel2")
    level3 = cmds.optionVar(query="op_currOpenLevel3")
    text = cmds.scrollField("op_currOpen_scrollField", query=True, text=True)
    opsActions.set_custom_notes(tab, level1, level2, level3, text)
    cmds.button("op_currOpenSaveNote_btn", edit=True, enable=False)

def clear_note(*args):
    cmds.scrollField("op_currOpen_scrollField", edit=True, text="")
    save_note()

def close_current(*args):
    if opsActions.close_file():
        refresh_ui()

def launch_help(*args):
    cmds.showHelp("http://openpipeline.sourceforge.net/", absolute=True)

# --- UI Dialog Wrappers ---

def prompt_new_asset_type(*args):
    res = cmds.promptDialog(title="New Asset Type", message="Asset Type Name\n(no spaces or special characters):", button=["Create", "Cancel"], defaultButton="Create", cancelButton="Cancel", dismissString="Cancel")
    if res == "Create":
        name = cmds.promptDialog(query=True, text=True).strip()
        if opsActions.create_new_item(2, name, "", "", 0): refresh_ui()

def prompt_new_sequence(*args):
    res = cmds.promptDialog(title="New Sequence", message="Sequence Name\n(no spaces or special characters):", button=["Create", "Cancel"], defaultButton="Create", cancelButton="Cancel", dismissString="Cancel")
    if res == "Create":
        name = cmds.promptDialog(query=True, text=True).strip()
        if opsActions.create_new_item(3, name, "", "", 0): refresh_ui()

def _item_creation_dialog(title, field_label, create_callback):
    if cmds.window("op_secondaryUI", exists=True): cmds.deleteUI("op_secondaryUI")
    cmds.window("op_secondaryUI", title=title, widthHeight=(250, 180))
    cmds.columnLayout(width=220, rowSpacing=5, columnOffset=("both", 10))
    cmds.text(label=field_label)
    cmds.textField("op_newItemNameField", editable=True, width=220)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(110, 110))
    create_btn = cmds.button(label="Create", width=110)
    cmds.button(label="Cancel", width=110, command=lambda x: cmds.deleteUI("op_secondaryUI"))
    cmds.setParent("..")
    cmds.radioCollection()
    cmds.radioButton(label="Start with empty item", select=True, onCommand=lambda x: cmds.button(create_btn, edit=True, command=lambda y: create_callback(1)))
    cmds.radioButton(label="Export current selection", onCommand=lambda x: cmds.button(create_btn, edit=True, command=lambda y: create_callback(2)))
    cmds.radioButton(label="Export current scene", onCommand=lambda x: cmds.button(create_btn, edit=True, command=lambda y: create_callback(3)))
    cmds.button(create_btn, edit=True, command=lambda y: create_callback(1))
    cmds.showWindow("op_secondaryUI")

def prompt_new_asset(*args):
    def _create(mode):
        name = cmds.textField("op_newItemNameField", query=True, text=True).strip()
        selected = opsInfo.get_currently_selected_item(2, 1)
        if not selected[0]: cmds.confirmDialog(title="Error", message="No Asset Type selected.", button=["OK"])
        elif opsActions.create_new_item(2, selected[0], name, "", mode):
            refresh_ui()
            cmds.deleteUI("op_secondaryUI")
    _item_creation_dialog("Create New Asset", "Asset Name (no spaces or special chars):", _create)

def prompt_new_asset_component(*args):
    def _create(mode):
        name = cmds.textField("op_newItemNameField", query=True, text=True).strip()
        selected = opsInfo.get_currently_selected_item(2, 2)
        if not selected[1]: cmds.confirmDialog(title="Error", message="No Asset selected.", button=["OK"])
        elif opsActions.create_new_item(2, selected[0], selected[1], name, mode):
            refresh_ui()
            cmds.deleteUI("op_secondaryUI")
    _item_creation_dialog("Create New Component", "Component Name (no spaces or special chars):", _create)

def prompt_rename_asset(*args):
    if cmds.window("op_secondaryUI", exists=True): cmds.deleteUI("op_secondaryUI")
    cmds.window("op_secondaryUI", title="Rename Asset", widthHeight=(280, 180))
    cmds.columnLayout(width=220, rowSpacing=5, columnOffset=("both", 10))
    cmds.text(label="New Asset Name (no spaces or special chars):")
    cmds.textField("op_newNameField", editable=True, width=220)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(110, 110))
    cmds.button(label="Rename", width=110, command=lambda x: _rename_asset_callback())
    cmds.button(label="Cancel", width=110, command=lambda x: cmds.deleteUI("op_secondaryUI"))
    cmds.showWindow("op_secondaryUI")

def _rename_asset_callback():
    import renameAsset
    new_name = cmds.textField("op_newNameField", query=True, text=True).strip()
    selected = opsInfo.get_currently_selected_item(2, 2)
    asset_path = opsInfo.get_file_name(2, selected[0], selected[1], selected[2], "folder")
    renameAsset.renameAsset(asset_path, new_name)
    refresh_ui()
    cmds.deleteUI("op_secondaryUI")
    
def prompt_save_workshop(*args):
    w_name = cmds.optionVar(query="op_workshopName").capitalize()
    if cmds.window("op_secondaryUI", exists=True): cmds.deleteUI("op_secondaryUI")
    cmds.window("op_secondaryUI", title=f"Save {w_name}", widthHeight=(300, 90))
    cmds.columnLayout(rowSpacing=5, columnOffset=("both", 10))
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(60, 230), columnAlign2=("center", "center"))
    cmds.text(label="comment: ", width=60)
    cmds.textField("op_saveWorkshopCommentField", width=190)
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(125, 125), columnAlign2=("center", "center"))
    cmds.button(label=f"SAVE {w_name}", width=125, backgroundColor=(0.8, 0.6, 0.5), command=lambda x: opsActions.save_workshop(cmds.textField("op_saveWorkshopCommentField", query=True, text=True)) and cmds.deleteUI("op_secondaryUI") and refresh_ui())
    cmds.button(label="cancel", width=125, backgroundColor=(0.8, 0.4, 0.4), command=lambda x: cmds.deleteUI("op_secondaryUI"))
    cmds.showWindow("op_secondaryUI")

def prompt_archive(tab, level, *args):
    levels = opsInfo.get_currently_selected_item(tab, level)
    if not levels[0]: return
    
    w_name = cmds.optionVar(query="op_workshopName").capitalize()
    m_name = cmds.optionVar(query="op_masterName").capitalize()
    
    item_name_str = f"{levels[0]}"
    if levels[1]: item_name_str += f": {levels[1]}"
    if levels[2]: item_name_str += f": {levels[2]}"
    
    if cmds.window("op_secondaryUI", exists=True): cmds.deleteUI("op_secondaryUI")
    cmds.window("op_secondaryUI", title=f"Archive - {item_name_str}", widthHeight=(400, 360))
    
    cmds.columnLayout(rowSpacing=5, columnOffset=("both", 10))
    cmds.text(align="left", font="smallPlainLabelFont", label=f"ARCHIVE: Archiving the selected item will clean up its working directory\nby moving old {w_name} files and old {m_name} versions to the Archive\nfolder. The most recent files won't be affected.")
    cmds.separator(height=5, width=370, style="none")
    
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190))
    chk_w = cmds.checkBox(label=f"Archive {w_name} Files", value=True)
    chk_m = cmds.checkBox(label=f"Archive {m_name} Versions", value=True)
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=4, columnWidth4=(110, 80, 110, 80))
    cmds.text(label="keep most recent")
    int_w = cmds.intField(value=1, min=1, step=1, width=40)
    cmds.text(label="keep most recent")
    int_m = cmds.intField(value=1, min=1, step=1, width=40)
    cmds.setParent("..")
    
    cmds.separator(height=5, width=370, style="none")
    cmds.button(width=370, label="Archive", backgroundColor=(0.6, 0.7, 0.9), command=lambda x: opsActions.archive_item(tab, levels[0], levels[1], levels[2], cmds.intField(int_w, query=True, value=True) if cmds.checkBox(chk_w, query=True, value=True) else 0, cmds.intField(int_m, query=True, value=True) if cmds.checkBox(chk_m, query=True, value=True) else 0) and cmds.deleteUI("op_secondaryUI") and refresh_ui())
    
    cmds.separator(height=10, width=370, style="out")
    cmds.text(align="left", font="smallPlainLabelFont", label="RETRIEVE: Retrieving archived files for the current item will return them\nto their original working directories.")
    cmds.separator(height=5, width=370, style="none")
    
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190))
    r_chk_w = cmds.checkBox(label=f"Retrieve {w_name} Files", value=False)
    r_chk_m = cmds.checkBox(label=f"Retrieve {m_name} Versions", value=False)
    cmds.setParent("..")
    
    cmds.separator(height=5, width=370, style="none")
    cmds.button(width=370, label="Retrieve", backgroundColor=(1, 1, 1), command=lambda x: opsActions.retrieve_archive(tab, levels[0], levels[1], levels[2], cmds.checkBox(r_chk_w, query=True, value=True), cmds.checkBox(r_chk_m, query=True, value=True)) and cmds.deleteUI("op_secondaryUI") and refresh_ui())
    
    cmds.separator(height=10, width=370, style="out")
    cmds.text(align="left", font="smallPlainLabelFont", label="DELETE: This will move all archived files for this item to the 'deleted' folder.")
    cmds.separator(height=5, width=370, style="none")
    cmds.button(width=370, label="Delete Archive", backgroundColor=(1, 0.7, 0.6), command=lambda x: opsActions.remove_archive(tab, levels[0], levels[1], levels[2]) and cmds.deleteUI("op_secondaryUI"))
    cmds.separator(height=10, width=370, style="out")
    cmds.button(width=370, label="Close", command=lambda x: cmds.deleteUI("op_secondaryUI"))
    
    cmds.showWindow("op_secondaryUI")

def about_dialog(*args):
    if cmds.window("infoWindow", exists=True): cmds.deleteUI("infoWindow")
    cmds.window("infoWindow", title="About openPypeline Studio", widthHeight=(300, 250))
    cmds.columnLayout(adjustableColumn=True)
    text = ("openPypeline Studio\n\nAn open source, free, and customizable pipeline for production (in Autodesk Maya).\n\n"
            "Originally created by Kickstand.\nModernized to Python 3 by the open-source community.\n\n"
            "More information may be found at:\nhttp://openpipeline.sourceforge.net/")
    cmds.scrollField(wordWrap=True, width=300, height=200, text=text, editable=False)
    cmds.button(label="Close", command=lambda x: cmds.deleteUI("infoWindow"))
    cmds.showWindow("infoWindow")