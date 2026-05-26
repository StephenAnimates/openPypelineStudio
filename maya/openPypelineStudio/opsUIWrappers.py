"""
File: opsUIWrappers.py
Description: UI action wrappers for openPypeline Studio.
             Connects the UI button commands to the core opsActions logic.
             Replaces the legacy wrapper dialogs from openPipelineUI.mel.

TODO: - Refactor the individual UI action functions to be more modular and reusable across different UI contexts.
Ask: What's the best way to convert the `project_ui_selection` list to a `QListWidget` when we move to PySide?
"""

import maya.cmds as cmds
import os
import opsInfo
import opsActions


def refresh_ui(*args):
    """Calls the UI update functions to reflect the latest file state."""
    try:
        update_currently_open()
        update_asset_type_list()
        update_sequence_list()
    except Exception as e:
        cmds.warning(f"UI Refresh warning: {e}")


def remove_secondary_windows(*args):
    if cmds.window("ops_secondaryUI", exists=True):
        cmds.deleteUI("ops_secondaryUI")


def close_ui(*args):
    if cmds.workspaceControl("openPypelineUI", exists=True):
        cmds.deleteUI("openPypelineUI")
    elif cmds.window("openPypelineUI", exists=True):
        cmds.deleteUI("openPypelineUI")
    remove_secondary_windows()
    try:
        import opsProject
        opsProject.close_proj_ui()
    except Exception: pass


# --- Primary UI Updaters ---

def update_currently_open(*args):
    curr_type = cmds.optionVar(query="ops_currOpenType") if cmds.optionVar(exists="ops_currOpenType") else ""
    curr_cat = cmds.optionVar(query="ops_currOpenCategory") if cmds.optionVar(exists="ops_currOpenCategory") else ""
    curr_version = cmds.optionVar(query="ops_currOpenVersion") if cmds.optionVar(exists="ops_currOpenVersion") else 0
    level1 = cmds.optionVar(query="ops_currOpenLevel1") if cmds.optionVar(exists="ops_currOpenLevel1") else ""
    level2 = cmds.optionVar(query="ops_currOpenLevel2") if cmds.optionVar(exists="ops_currOpenLevel2") else ""
    level3 = cmds.optionVar(query="ops_currOpenLevel3") if cmds.optionVar(exists="ops_currOpenLevel3") else ""
    tab = cmds.optionVar(query="ops_currOpenTab") if cmds.optionVar(exists="ops_currOpenTab") else 0

    curr_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    ui_dir = os.path.dirname(__file__)
    default_preview = os.path.join(ui_dir, 'defaultPreview.png').replace("\\", "/")
    no_preview = os.path.join(ui_dir, 'noPreview.png').replace("\\", "/")

    if not level1:
        clear_current_history()
        if cmds.scrollField("ops_currOpen_scrollField", exists=True): cmds.scrollField("ops_currOpen_scrollField", edit=True, text="")
        if cmds.image("ops_currOpenPreview_img", exists=True): cmds.image("ops_currOpenPreview_img", edit=True, image=default_preview)
        
        for btn in ["ops_currOpenSaveWorkshop_btn", "ops_currOpenRecordPlayblast_btn", "ops_currOpenViewPlayblast_btn", 
                    "ops_currOpenMaster_btn", "ops_currOpenRevive_btn", "ops_currOpenClose_btn", "ops_currOpenClearNote_btn",
                    "ops_currOpenSaveNote_btn", "ops_currOpenSnapshot_btn", "ops_currOpenExplore_btn"]:
            if cmds.button(btn, exists=True): cmds.button(btn, edit=True, enable=False)
                
        if cmds.textField("ops_currOpenLocation_txtField", exists=True): cmds.textField("ops_currOpenLocation_txtField", edit=True, text="")
        if cmds.text("ops_currOpenHeading_txt", exists=True): cmds.text("ops_currOpenHeading_txt", edit=True, label="none")
        if cmds.text("ops_currOpenHeadingVersion_txt", exists=True): cmds.text("ops_currOpenHeadingVersion_txt", edit=True, label="      ", backgroundColor=(0.8, 0.8, 0.8))
    elif os.path.isdir(curr_path):
        w_name = cmds.optionVar(query="ops_wip") if cmds.optionVar(exists="ops_wip") else "workshop"
        m_name = cmds.optionVar(query="ops_masterName") if cmds.optionVar(exists="ops_masterName") else "master"
        
        num_versions = opsInfo.get_num_workshops(tab, level1, level2, level3)
        latest_version = opsInfo.get_latest_workshop_version(tab, level1, level2, level3)
        revive_enabled = True if num_versions > 1 else False
        
        version_string = f"{w_name} version {curr_version}" if curr_type == "workshop" else m_name
        display_string = f"{level1}: {level2}  ({curr_cat.capitalize()})" if curr_cat in ["asset", "shot"] else f"{level1}: {level2}: {level3}  (Component)" if curr_cat in ["component", "shotComponent"] else ""
            
        prev_img = opsInfo.get_thumbnail(tab, level1, level2, level3)
        if cmds.image("ops_currOpenPreview_img", exists=True): cmds.image("ops_currOpenPreview_img", edit=True, image=prev_img if os.path.isfile(prev_img) else no_preview)
            
        note_text = opsInfo.get_custom_notes(tab, level1, level2, level3)
        if cmds.scrollField("ops_currOpen_scrollField", exists=True): cmds.scrollField("ops_currOpen_scrollField", edit=True, editable=True, text=note_text)
            
        load_current_history()
        
        if cmds.button("ops_currOpenRevive_btn", exists=True): cmds.button("ops_currOpenRevive_btn", edit=True, enable=revive_enabled)
        if cmds.button("ops_currOpenRecordPlayblast_btn", exists=True): cmds.button("ops_currOpenRecordPlayblast_btn", edit=True, enable=True)
        if cmds.button("ops_currOpenViewPlayblast_btn", exists=True): cmds.button("ops_currOpenViewPlayblast_btn", edit=True, enable=opsInfo.has_playblast(tab, level1, level2, level3))
        
        for btn in ["ops_currOpenClose_btn", "ops_currOpenSaveWorkshop_btn", "ops_currOpenMaster_btn", "ops_currOpenClearNote_btn", "ops_currOpenSnapshot_btn", "ops_currOpenExplore_btn"]:
            if cmds.button(btn, exists=True): cmds.button(btn, edit=True, enable=True)
            
        if cmds.button("ops_currOpenSaveNote_btn", exists=True): cmds.button("ops_currOpenSaveNote_btn", edit=True, enable=False)
        if cmds.textField("ops_currOpenLocation_txtField", exists=True): cmds.textField("ops_currOpenLocation_txtField", edit=True, text=curr_path)
            
        if cmds.text("ops_currOpenHeadingVersion_txt", exists=True):
            bgc = (0.8, 0.6, 0.5) if latest_version == curr_version else (0.5, 0.7, 0.7)
            if curr_type == "master": bgc = (0.9, 0.7, 0.4)
            cmds.text("ops_currOpenHeadingVersion_txt", edit=True, backgroundColor=bgc, visible=True, label=version_string)
            
        if cmds.text("ops_currOpenHeading_txt", exists=True): cmds.text("ops_currOpenHeading_txt", edit=True, label=display_string)
            
        if curr_type == "master":
            for btn in ["ops_currOpenSaveWorkshop_btn", "ops_currOpenMaster_btn"]:
                if cmds.button(btn, exists=True): cmds.button(btn, edit=True, enable=False)
    else:
        opsActions.close_file()
        remove_secondary_windows()


def update_working_tab(*args):
    if cmds.tabLayout("ops_mainTabs_tabLayout", exists=True):
        tab = cmds.tabLayout("ops_mainTabs_tabLayout", query=True, selectTabIndex=True)
        cmds.optionVar(intValue=("ops_currTab", tab))
        if tab == 3: update_currently_open()
        elif tab == 1: update_asset_type_list()
        elif tab == 2: update_sequence_list()


# --- Asset Inventory Updaters ---

def update_asset_type_list(*args):
    selected = opsInfo.get_currently_selected_item(2, 1)
    if cmds.textScrollList("ops_assetType_txtScrollList", exists=True):
        cmds.textScrollList("ops_assetType_txtScrollList", edit=True, removeAll=True)
        if cmds.optionVar(exists="ops_assetTypes"): cmds.optionVar(clearArray="ops_assetTypes")
        types = sorted(opsInfo.get_children(2, "", "", ""))
        for t in types:
            cmds.optionVar(stringValueAppend=("ops_assetTypes", t))
            cmds.textScrollList("ops_assetType_txtScrollList", edit=True, append=t)
            if selected[0] == t: cmds.textScrollList("ops_assetType_txtScrollList", edit=True, selectItem=t)
    update_asset_list(1)


def update_asset_list(preserve_selection=1, *args):
    if isinstance(preserve_selection, (list, tuple, str)): preserve_selection = int(preserve_selection[0]) if isinstance(preserve_selection, (list, tuple)) else int(preserve_selection)
    selected = opsInfo.get_currently_selected_item(2, 2)
    if cmds.textScrollList("ops_asset_scrollList", exists=True):
        cmds.textScrollList("ops_asset_scrollList", edit=True, removeAll=True)
        if cmds.optionVar(exists="ops_assets"): cmds.optionVar(clearArray="ops_assets")
        active = False
        if selected[0]:
            assets = sorted(opsInfo.get_children(2, selected[0], "", ""))
            for asset in assets:
                active = True
                cmds.optionVar(stringValueAppend=("ops_assets", asset))
                post = " +" if opsInfo.has_master(2, selected[0], asset, "") else " -" if opsInfo.has_workshop(2, selected[0], asset, "") else ""
                pre = "* " if opsInfo.get_file_name(2, selected[0], asset, "", "folder") == opsInfo.get_currently_open_path() else ""
                post += " *" if pre else ""
                display_str = f"{pre}{asset}{post}"
                cmds.textScrollList("ops_asset_scrollList", edit=True, append=display_str)
                if preserve_selection and selected[1] == asset:
                    try: cmds.textScrollList("ops_asset_scrollList", edit=True, selectItem=display_str)
                    except: pass
        if cmds.button("ops_assetTypeRemove_btn", exists=True): cmds.button("ops_assetTypeRemove_btn", edit=True, enable=bool(selected[0]))
        if cmds.button("ops_assetNew_btn", exists=True): cmds.button("ops_assetNew_btn", edit=True, enable=bool(selected[0]))
        cmds.textScrollList("ops_asset_scrollList", edit=True, enable=active)
    asset_selected(1)


def asset_selected(preserve_selection=1, *args):
    if isinstance(preserve_selection, (list, tuple, str)): preserve_selection = int(preserve_selection[0]) if isinstance(preserve_selection, (list, tuple)) else int(preserve_selection)
    selected = opsInfo.get_currently_selected_item(2, 3)
    if cmds.textScrollList("ops_componentScrollList", exists=True):
        cmds.textScrollList("ops_componentScrollList", edit=True, removeAll=True)
        if cmds.optionVar(exists="ops_components"): cmds.optionVar(clearArray="ops_components")
        is_selected = bool(selected[1])
        for item in ["ops_assetActions_EditAsset_menuItem", "ops_assetActions_OpenMaster_menuItem", "ops_assetActions_import_menuItem", 
                     "ops_assetActions_reference_menuItem", "ops_assetPopUpMenu_editAsset_menuItem", "ops_assetPopUpMenu_openMaster_menuItem",
                     "ops_assetPopUpMenu_import_menuItem", "ops_assetPopUpMenu_reference_menuItem", "ops_assetActions_archive_menuItem", "ops_assetPopUpMenu_archive_menuItem"]:
            if cmds.menuItem(item, exists=True): cmds.menuItem(item, edit=True, enable=is_selected)
        for btn in ["ops_assetRename_btn", "ops_assetRemove_btn", "ops_assetViewPlayblastAssetButton", "ops_componentNewButton"]:
            if cmds.button(btn, exists=True): cmds.button(btn, edit=True, enable=is_selected)
        active = False
        if is_selected:
            components = sorted(opsInfo.get_children(2, selected[0], selected[1], ""))
            for comp in components:
                active = True
                cmds.optionVar(stringValueAppend=("ops_components", comp))
                post = " +" if opsInfo.has_master(2, selected[0], selected[1], comp) else " -" if opsInfo.has_workshop(2, selected[0], selected[1], comp) else ""
                pre = "* " if opsInfo.get_file_name(2, selected[0], selected[1], comp, "folder") == opsInfo.get_currently_open_path() else ""
                post += " *" if pre else ""
                display_str = f"{pre}{comp}{post}"
                cmds.textScrollList("ops_componentScrollList", edit=True, append=display_str)
                if preserve_selection and selected[2] == comp:
                    try: cmds.textScrollList("ops_componentScrollList", edit=True, selectItem=display_str)
                    except: pass
        cmds.textScrollList("ops_componentScrollList", edit=True, enable=active)
    component_selected()
    

def component_selected(*args):
    selected = opsInfo.get_currently_selected_item(2, 3)
    is_selected = bool(selected[2])
    for item in ["ops_compMenuEdit", "ops_compMenuView", "ops_compMenuImport", "ops_compMenuReference", "ops_assetCompMenuArchive",
                 "ops_compMenuEdit2", "ops_compMenuView2", "ops_compMenuImport2", "ops_compMenuReference2", "ops_assetCompMenuArchive2"]:
        if cmds.menuItem(item, exists=True): cmds.menuItem(item, edit=True, enable=is_selected)
    if cmds.button("ops_componentRemoveButton", exists=True): cmds.button("ops_componentRemoveButton", edit=True, enable=is_selected)
    asset_information()
    load_asset_history()


# --- Shot Inventory Updaters ---

def update_sequence_list(*args):
    selected = opsInfo.get_currently_selected_item(3, 1)
    if cmds.textScrollList("ops_sequenceScrollList", exists=True):
        cmds.textScrollList("ops_sequenceScrollList", edit=True, removeAll=True)
        if cmds.optionVar(exists="ops_sequences"): cmds.optionVar(clearArray="ops_sequences")
        seqs = sorted(opsInfo.get_children(3, "", "", ""))
        for seq in seqs:
            cmds.optionVar(stringValueAppend=("ops_sequences", seq))
            cmds.textScrollList("ops_sequenceScrollList", edit=True, append=seq)
            if selected[0] == seq: cmds.textScrollList("ops_sequenceScrollList", edit=True, selectItem=seq)
    update_shot_list(1)


def update_shot_list(preserve_selection=1, *args):
    if isinstance(preserve_selection, (list, tuple, str)): preserve_selection = int(preserve_selection[0]) if isinstance(preserve_selection, (list, tuple)) else int(preserve_selection)
    selected = opsInfo.get_currently_selected_item(3, 2)
    if cmds.textScrollList("ops_shotScrollList", exists=True):
        cmds.textScrollList("ops_shotScrollList", edit=True, removeAll=True)
        if cmds.optionVar(exists="ops_shots"): cmds.optionVar(clearArray="ops_shots")
        active = False
        if selected[0]:
            shots = sorted(opsInfo.get_children(3, selected[0], "", ""))
            for shot in shots:
                active = True
                cmds.optionVar(stringValueAppend=("ops_shots", shot))
                post = " +" if opsInfo.has_master(3, selected[0], shot, "") else " -" if opsInfo.has_workshop(3, selected[0], shot, "") else ""
                pre = "* " if opsInfo.get_file_name(3, selected[0], shot, "", "folder") == opsInfo.get_currently_open_path() else ""
                post += " *" if pre else ""
                display_str = f"{pre}{shot}{post}"
                cmds.textScrollList("ops_shotScrollList", edit=True, append=display_str)
                if preserve_selection and selected[1] == shot:
                    try: cmds.textScrollList("ops_shotScrollList", edit=True, selectItem=display_str)
                    except: pass
        if cmds.button("ops_sequenceRemoveButton", exists=True): cmds.button("ops_sequenceRemoveButton", edit=True, enable=bool(selected[0]))
        if cmds.button("ops_shotNewButton", exists=True): cmds.button("ops_shotNewButton", edit=True, enable=bool(selected[0]))
        cmds.textScrollList("ops_shotScrollList", edit=True, enable=active)
    shot_selected(1)


def shot_selected(preserve_selection=1, *args):
    if isinstance(preserve_selection, (list, tuple, str)): preserve_selection = int(preserve_selection[0]) if isinstance(preserve_selection, (list, tuple)) else int(preserve_selection)
    selected = opsInfo.get_currently_selected_item(3, 3)
    if cmds.textScrollList("ops_shotComponentScrollList", exists=True):
        cmds.textScrollList("ops_shotComponentScrollList", edit=True, removeAll=True)
        if cmds.optionVar(exists="ops_shotComponents"): cmds.optionVar(clearArray="ops_shotComponents")
        is_selected = bool(selected[1])
        for item in ["ops_shotMenuEdit", "ops_shotMenuView", "ops_shotMenuImport", "ops_shotMenuReference", "ops_shotMenuArchive",
                     "ops_shotMenuEdit2", "ops_shotMenuView2", "ops_shotMenuImport2", "ops_shotMenuReference2", "ops_shotMenuArchive2"]:
            if cmds.menuItem(item, exists=True): cmds.menuItem(item, edit=True, enable=is_selected)
        for btn in ["ops_shotRemoveButton", "ops_shotComponentNewButton", "ops_shotViewPlayblastButton"]:
            if cmds.button(btn, exists=True): cmds.button(btn, edit=True, enable=is_selected)
        active = False
        if is_selected:
            components = sorted(opsInfo.get_children(3, selected[0], selected[1], ""))
            for comp in components:
                active = True
                cmds.optionVar(stringValueAppend=("ops_shotComponents", comp))
                post = " +" if opsInfo.has_master(3, selected[0], selected[1], comp) else " -" if opsInfo.has_workshop(3, selected[0], selected[1], comp) else ""
                pre = "* " if opsInfo.get_file_name(3, selected[0], selected[1], comp, "folder") == opsInfo.get_currently_open_path() else ""
                post += " *" if pre else ""
                display_str = f"{pre}{comp}{post}"
                cmds.textScrollList("ops_shotComponentScrollList", edit=True, append=display_str)
                if preserve_selection and selected[2] == comp:
                    try: cmds.textScrollList("ops_shotComponentScrollList", edit=True, selectItem=display_str)
                    except: pass
        cmds.textScrollList("ops_shotComponentScrollList", edit=True, enable=active)
    shot_component_selected()
    

def shot_component_selected(*args):
    selected = opsInfo.get_currently_selected_item(3, 3)
    is_selected = bool(selected[2])
    for item in ["ops_shotcompMenuEdit", "ops_shotcompMenuView", "ops_shotcompMenuImport", "ops_shotcompMenuReference", "ops_shotcompMenuArchive",
                 "ops_shotcompMenuEdit2", "ops_shotcompMenuView2", "ops_shotcompMenuImport2", "ops_shotcompMenuReference2", "ops_shotcompMenuArchive2"]:
        if cmds.menuItem(item, exists=True): cmds.menuItem(item, edit=True, enable=is_selected)
    if cmds.button("ops_shotComponentRemoveButton", exists=True): cmds.button("ops_shotComponentRemoveButton", edit=True, enable=is_selected)
    shot_information()
    load_shot_history()


# --- Information and History Blocks ---

def asset_information(*args):
    selected = opsInfo.get_currently_selected_item(2, 3)
    ui_dir = os.path.dirname(__file__)
    preview_file = os.path.join(ui_dir, 'defaultPreview.png').replace("\\", "/")
    output_text = ""
    
    if selected[1]:
        thumb = opsInfo.get_thumbnail(2, selected[0], selected[1], selected[2])
        if os.path.isfile(thumb): preview_file = thumb
        else: preview_file = os.path.join(ui_dir, 'noPreview.png').replace("\\", "/")
        output_text = opsInfo.get_custom_notes(2, selected[0], selected[1], selected[2])
        if cmds.button("ops_assetViewPlayblastAssetButton", exists=True):
            cmds.button("ops_assetViewPlayblastAssetButton", edit=True, enable=opsInfo.has_playblast(2, selected[0], selected[1], selected[2]))
    else:
        if cmds.button("ops_assetViewPlayblastAssetButton", exists=True): cmds.button("ops_assetViewPlayblastAssetButton", edit=True, enable=False)
        
    folder = opsInfo.get_file_name(2, selected[0], selected[1], selected[2], "folder")
    if cmds.textField("ops_assetLocationField", exists=True): cmds.textField("ops_assetLocationField", edit=True, text=folder)
    if cmds.scrollField("ops_assetNoteField", exists=True): cmds.scrollField("ops_assetNoteField", edit=True, text=output_text)
    if cmds.image("ops_assetPreviewImage", exists=True): cmds.image("ops_assetPreviewImage", edit=True, image=preview_file)


def shot_information(*args):
    selected = opsInfo.get_currently_selected_item(3, 3)
    ui_dir = os.path.dirname(__file__)
    preview_file = os.path.join(ui_dir, 'defaultPreview.png').replace("\\", "/")
    output_text = ""
    
    if selected[1]:
        thumb = opsInfo.get_thumbnail(3, selected[0], selected[1], selected[2])
        if os.path.isfile(thumb): preview_file = thumb
        else: preview_file = os.path.join(ui_dir, 'noPreview.png').replace("\\", "/")
        output_text = opsInfo.get_custom_notes(3, selected[0], selected[1], selected[2])
        if cmds.button("ops_shotViewPlayblastButton", exists=True):
            cmds.button("ops_shotViewPlayblastButton", edit=True, enable=opsInfo.has_playblast(3, selected[0], selected[1], selected[2]))
    else:
        if cmds.button("ops_shotViewPlayblastButton", exists=True): cmds.button("ops_shotViewPlayblastButton", edit=True, enable=False)
        
    folder = opsInfo.get_file_name(3, selected[0], selected[1], selected[2], "folder")
    if cmds.textField("ops_shotLocationField", exists=True): cmds.textField("ops_shotLocationField", edit=True, text=folder)
    if cmds.scrollField("ops_shotInfoField", exists=True): cmds.scrollField("ops_shotInfoField", edit=True, text=output_text)
    if cmds.image("ops_shotPreviewImage", exists=True): cmds.image("ops_shotPreviewImage", edit=True, image=preview_file)


def load_asset_history(*args):
    selected = opsInfo.get_currently_selected_item(2, 3)
    history_text = opsInfo.get_event_notes(2, selected[0], selected[1], selected[2])
    if cmds.scrollField("ops_commentField", exists=True): cmds.scrollField("ops_commentField", edit=True, text=history_text)
    

def load_shot_history(*args):
    selected = opsInfo.get_currently_selected_item(3, 3)
    history_text = opsInfo.get_event_notes(3, selected[0], selected[1], selected[2])
    if cmds.scrollField("ops_shotCommentField", exists=True): cmds.scrollField("ops_shotCommentField", edit=True, text=history_text)
    

def load_current_history(*args):
    tab = cmds.optionVar(query="ops_currOpenTab") if cmds.optionVar(exists="ops_currOpenTab") else 0
    level1 = cmds.optionVar(query="ops_currOpenLevel1") if cmds.optionVar(exists="ops_currOpenLevel1") else ""
    level2 = cmds.optionVar(query="ops_currOpenLevel2") if cmds.optionVar(exists="ops_currOpenLevel2") else ""
    level3 = cmds.optionVar(query="ops_currOpenLevel3") if cmds.optionVar(exists="ops_currOpenLevel3") else ""
    history_text = opsInfo.get_event_notes(tab, level1, level2, level3)
    if cmds.scrollField("ops_currOpenAssetNote_scrollField", exists=True): cmds.scrollField("ops_currOpenAssetNote_scrollField", edit=True, text=history_text)
    

def clear_current_history(*args):
    if cmds.scrollField("ops_currOpenAssetNote_scrollField", exists=True): cmds.scrollField("ops_currOpenAssetNote_scrollField", edit=True, text="")


def open_currently_selected(tab, level, item_type, version_offset=0, *args):
    levels = opsInfo.get_currently_selected_item(tab, level)
    if opsActions.open_item(item_type, tab, levels[0], levels[1], levels[2], version_offset):
        if cmds.tabLayout("ops_mainTabs_tabLayout", exists=True):
            cmds.tabLayout("ops_mainTabs_tabLayout", edit=True, selectTabIndex=3)
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
    tab = cmds.optionVar(query="ops_currOpenTab")
    level1 = cmds.optionVar(query="ops_currOpenLevel1")
    level2 = cmds.optionVar(query="ops_currOpenLevel2")
    level3 = cmds.optionVar(query="ops_currOpenLevel3")
    opsActions.open_location(tab, level1, level2, level3)


def view_playblast_selected(tab, *args):
    levels = opsInfo.get_currently_selected_item(tab, 3)
    opsActions.view_playblast(tab, levels[0], levels[1], levels[2])


def view_playblast_current(*args):
    tab = cmds.optionVar(query="ops_currOpenTab")
    level1 = cmds.optionVar(query="ops_currOpenLevel1")
    level2 = cmds.optionVar(query="ops_currOpenLevel2")
    level3 = cmds.optionVar(query="ops_currOpenLevel3")
    opsActions.view_playblast(tab, level1, level2, level3)


def record_current_playblast(*args):
    tab = cmds.optionVar(query="ops_currOpenTab")
    level1 = cmds.optionVar(query="ops_currOpenLevel1")
    level2 = cmds.optionVar(query="ops_currOpenLevel2")
    level3 = cmds.optionVar(query="ops_currOpenLevel3")
    opsActions.record_playblast(tab, level1, level2, level3)
    refresh_ui()


def take_snapshot(*args):
    tab = cmds.optionVar(query="ops_currOpenTab")
    level1 = cmds.optionVar(query="ops_currOpenLevel1")
    level2 = cmds.optionVar(query="ops_currOpenLevel2")
    level3 = cmds.optionVar(query="ops_currOpenLevel3")
    img = opsActions.create_thumbnail(tab, level1, level2, level3)
    if os.path.isfile(img):
        cmds.image("ops_currOpenPreview_img", edit=True, image=img)


def save_note(*args):
    tab = cmds.optionVar(query="ops_currOpenTab")
    level1 = cmds.optionVar(query="ops_currOpenLevel1")
    level2 = cmds.optionVar(query="ops_currOpenLevel2")
    level3 = cmds.optionVar(query="ops_currOpenLevel3")
    text = cmds.scrollField("ops_currOpen_scrollField", query=True, text=True)
    opsActions.set_custom_notes(tab, level1, level2, level3, text)
    cmds.button("ops_currOpenSaveNote_btn", edit=True, enable=False)


def clear_note(*args):
    cmds.scrollField("ops_currOpen_scrollField", edit=True, text="")
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
    if cmds.window("ops_secondaryUI", exists=True): cmds.deleteUI("ops_secondaryUI")
    cmds.window("ops_secondaryUI", title=title, widthHeight=(250, 180))
    cmds.columnLayout(width=220, rowSpacing=5, columnOffset=("both", 10))
    cmds.text(label=field_label)
    cmds.textField("ops_newItemNameField", editable=True, width=220)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(110, 110))
    create_btn = cmds.button(label="Create", width=110)
    cmds.button(label="Cancel", width=110, command=lambda x: cmds.deleteUI("ops_secondaryUI"))
    cmds.setParent("..")
    cmds.radioCollection()
    cmds.radioButton(label="Start with empty item", select=True, onCommand=lambda x: cmds.button(create_btn, edit=True, command=lambda y: create_callback(1)))
    cmds.radioButton(label="Export current selection", onCommand=lambda x: cmds.button(create_btn, edit=True, command=lambda y: create_callback(2)))
    cmds.radioButton(label="Export current scene", onCommand=lambda x: cmds.button(create_btn, edit=True, command=lambda y: create_callback(3)))
    cmds.button(create_btn, edit=True, command=lambda y: create_callback(1))
    cmds.showWindow("ops_secondaryUI")


def prompt_new_asset(*args):
    def _create(mode):
        name = cmds.textField("ops_newItemNameField", query=True, text=True).strip()
        selected = opsInfo.get_currently_selected_item(2, 1)
        if not selected[0]: cmds.confirmDialog(title="Error", message="No Asset Type selected.", button=["OK"])
        elif opsActions.create_new_item(2, selected[0], name, "", mode):
            refresh_ui()
            cmds.deleteUI("ops_secondaryUI")
    _item_creation_dialog("Create New Asset", "Asset Name (no spaces or special chars):", _create)


def prompt_new_asset_component(*args):
    def _create(mode):
        name = cmds.textField("ops_newItemNameField", query=True, text=True).strip()
        selected = opsInfo.get_currently_selected_item(2, 2)
        if not selected[1]: cmds.confirmDialog(title="Error", message="No Asset selected.", button=["OK"])
        elif opsActions.create_new_item(2, selected[0], selected[1], name, mode):
            refresh_ui()
            cmds.deleteUI("ops_secondaryUI")
    _item_creation_dialog("Create New Component", "Component Name (no spaces or special chars):", _create)


def prompt_new_shot(*args):
    def _create(mode):
        name = cmds.textField("ops_newItemNameField", query=True, text=True).strip()
        selected = opsInfo.get_currently_selected_item(3, 1)
        if not selected[0]: cmds.confirmDialog(title="Error", message="No Sequence selected.", button=["OK"])
        elif opsActions.create_new_item(3, selected[0], name, "", mode):
            refresh_ui()
            cmds.deleteUI("ops_secondaryUI")
    _item_creation_dialog("Create New Shot", "Shot Name (no spaces or special chars):", _create)


def prompt_new_shot_component(*args):
    def _create(mode):
        name = cmds.textField("ops_newItemNameField", query=True, text=True).strip()
        selected = opsInfo.get_currently_selected_item(3, 2)
        if not selected[1]: cmds.confirmDialog(title="Error", message="No Shot selected.", button=["OK"])
        elif opsActions.create_new_item(3, selected[0], selected[1], name, mode):
            refresh_ui()
            cmds.deleteUI("ops_secondaryUI")
    _item_creation_dialog("Create New Shot Component", "Component Name (no spaces or special chars):", _create)


def prompt_rename_asset(*args):
    if cmds.window("ops_secondaryUI", exists=True): cmds.deleteUI("ops_secondaryUI")
    cmds.window("ops_secondaryUI", title="Rename Asset", widthHeight=(280, 180))
    cmds.columnLayout(width=220, rowSpacing=5, columnOffset=("both", 10))
    cmds.text(label="New Asset Name (no spaces or special chars):")
    cmds.textField("ops_newNameField", editable=True, width=220)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(110, 110))
    cmds.button(label="Rename", width=110, command=lambda x: _rename_asset_callback())
    cmds.button(label="Cancel", width=110, command=lambda x: cmds.deleteUI("ops_secondaryUI"))
    cmds.showWindow("ops_secondaryUI")


def _rename_asset_callback():
    import renameAsset
    new_name = cmds.textField("ops_newNameField", query=True, text=True).strip()
    selected = opsInfo.get_currently_selected_item(2, 2)
    asset_path = opsInfo.get_file_name(2, selected[0], selected[1], selected[2], "folder")
    renameAsset.renameAsset(asset_path, new_name)
    refresh_ui()
    cmds.deleteUI("ops_secondaryUI")


def prompt_save_workshop(*args):
    w_name = cmds.optionVar(query="ops_wip").capitalize()
    if cmds.window("ops_secondaryUI", exists=True): cmds.deleteUI("ops_secondaryUI")
    cmds.window("ops_secondaryUI", title=f"Save {w_name}", widthHeight=(300, 90))
    cmds.columnLayout(rowSpacing=5, columnOffset=("both", 10))
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(60, 230), columnAlign2=("center", "center"))
    cmds.text(label="comment: ", width=60)
    cmds.textField("ops_saveWorkshopCommentField", width=190)
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(125, 125), columnAlign2=("center", "center"))
    cmds.button(label=f"SAVE {w_name}", width=125, backgroundColor=(0.8, 0.6, 0.5), command=lambda x: opsActions.save_workshop(cmds.textField("ops_saveWorkshopCommentField", query=True, text=True)) and cmds.deleteUI("ops_secondaryUI") and refresh_ui())
    cmds.button(label="cancel", width=125, backgroundColor=(0.8, 0.4, 0.4), command=lambda x: cmds.deleteUI("ops_secondaryUI"))
    cmds.showWindow("ops_secondaryUI")


def prompt_revive(*args):
    tab = cmds.optionVar(query="ops_currOpenTab") if cmds.optionVar(exists="ops_currOpenTab") else 0
    level1 = cmds.optionVar(query="ops_currOpenLevel1") if cmds.optionVar(exists="ops_currOpenLevel1") else ""
    level2 = cmds.optionVar(query="ops_currOpenLevel2") if cmds.optionVar(exists="ops_currOpenLevel2") else ""
    level3 = cmds.optionVar(query="ops_currOpenLevel3") if cmds.optionVar(exists="ops_currOpenLevel3") else ""
    
    if not level1:
        return
        
    w_name = cmds.optionVar(query="ops_wip").capitalize() if cmds.optionVar(exists="ops_wip") else "Workshop"
    
    workshops = opsInfo.get_workshops(tab, level1, level2, level3)
    if not workshops or len(workshops) < 2:
        cmds.warning(f"Not enough {w_name} files to revive.")
        return
        
    if cmds.window("ops_secondaryUI", exists=True): cmds.deleteUI("ops_secondaryUI")
    cmds.window("ops_secondaryUI", title=f"Revive {w_name}", widthHeight=(280, 200))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnOffset=("both", 10))
    cmds.text(label=f"Select a previous {w_name} version to revive:", align="left")
    
    cmds.textScrollList("ops_revive_scrollList", height=100)
    
    # Skip index 0 (the latest version) since you can't revive what is already current
    for i in range(1, len(workshops)):
        version = opsInfo.get_version_from_file(workshops[i])
        cmds.textScrollList("ops_revive_scrollList", edit=True, append=f"Version {version:04d}")
        
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 130))
    cmds.button(label="Revive", width=130, backgroundColor=(0.5, 0.7, 0.7), command=lambda x: _revive_callback(tab, level1, level2, level3))
    cmds.button(label="Cancel", width=130, command=lambda x: cmds.deleteUI("ops_secondaryUI"))
    
    cmds.showWindow("ops_secondaryUI")


def _revive_callback(tab, level1, level2, level3):
    selected_idx = cmds.textScrollList("ops_revive_scrollList", query=True, selectIndexedItem=True)
    if not selected_idx:
        return
        
    # Because we skipped index 0 in the UI list, a UI index of 1 perfectly matches an offset of 1
    offset = selected_idx[0]
    
    import opsActions
    # Safely prompt to save current changes, then open the older file
    if opsActions.open_item("workshop", tab, level1, level2, level3, offset):
        # Save the old file back into the pipeline as the newest version
        opsActions.save_workshop("Revived from an older version.")
        
    cmds.deleteUI("ops_secondaryUI")
    refresh_ui()


def prompt_archive(tab, level, *args):
    levels = opsInfo.get_currently_selected_item(tab, level)
    if not levels[0]: return
    
    w_name = cmds.optionVar(query="ops_wip").capitalize()
    m_name = cmds.optionVar(query="ops_masterName").capitalize()
    
    item_name_str = f"{levels[0]}"
    if levels[1]: item_name_str += f": {levels[1]}"
    if levels[2]: item_name_str += f": {levels[2]}"
    
    if cmds.window("ops_secondaryUI", exists=True): cmds.deleteUI("ops_secondaryUI")
    cmds.window("ops_secondaryUI", title=f"Archive - {item_name_str}", widthHeight=(400, 360))
    
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
    cmds.button(width=370, label="Archive", backgroundColor=(0.6, 0.7, 0.9), command=lambda x: opsActions.archive_item(tab, levels[0], levels[1], levels[2], cmds.intField(int_w, query=True, value=True) if cmds.checkBox(chk_w, query=True, value=True) else 0, cmds.intField(int_m, query=True, value=True) if cmds.checkBox(chk_m, query=True, value=True) else 0) and cmds.deleteUI("ops_secondaryUI") and refresh_ui())
    
    cmds.separator(height=10, width=370, style="out")
    cmds.text(align="left", font="smallPlainLabelFont", label="RETRIEVE: Retrieving archived files for the current item will return them\nto their original working directories.")
    cmds.separator(height=5, width=370, style="none")
    
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190))
    r_chk_w = cmds.checkBox(label=f"Retrieve {w_name} Files", value=False)
    r_chk_m = cmds.checkBox(label=f"Retrieve {m_name} Versions", value=False)
    cmds.setParent("..")
    
    cmds.separator(height=5, width=370, style="none")
    cmds.button(width=370, label="Retrieve", backgroundColor=(1, 1, 1), command=lambda x: opsActions.retrieve_archive(tab, levels[0], levels[1], levels[2], cmds.checkBox(r_chk_w, query=True, value=True), cmds.checkBox(r_chk_m, query=True, value=True)) and cmds.deleteUI("ops_secondaryUI") and refresh_ui())
    
    cmds.separator(height=10, width=370, style="out")
    cmds.text(align="left", font="smallPlainLabelFont", label="DELETE: This will move all archived files for this item to the 'deleted' folder.")
    cmds.separator(height=5, width=370, style="none")
    cmds.button(width=370, label="Delete Archive", backgroundColor=(1, 0.7, 0.6), command=lambda x: opsActions.remove_archive(tab, levels[0], levels[1], levels[2]) and cmds.deleteUI("ops_secondaryUI"))
    cmds.separator(height=10, width=370, style="out")
    cmds.button(width=370, label="Close", command=lambda x: cmds.deleteUI("ops_secondaryUI"))
    
    cmds.showWindow("ops_secondaryUI")


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