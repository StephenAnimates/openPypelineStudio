"""
File: opsSceneInv.py
Description: Scene and Asset Inventory functions for openPypeline Studio.
             Handles tracking existing assets, sequences, and reference loading.
             Refactored from openPipelineSceneInv.mel to Python 3.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import os
import re


def existed_asset(input_mode):
    current_project = cmds.textFieldGrp("projPath", query=True, text=True) if cmds.textFieldGrp("projPath", exists=True) else cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
    the_path = cmds.optionVar(query="ops_libPath") if cmds.optionVar(exists="ops_libPath") else ""
    if not the_path and current_project:
        the_path = os.path.join(current_project, "lib/").replace("\\", "/")
        
    extension = "_asset.mb"
    validation = []
    chomp = []
    full_path = []
    
    if os.path.isdir(the_path):
        the_files = [f for f in os.listdir(the_path) if not f.startswith('.')]
        for item in the_files:
            match = re.match(r"^[a-zA-Z_0-9]+", item)
            if match:
                chomp_val = match.group(0)
                chomp.append(chomp_val)
                expected_master_file = os.path.join(the_path, chomp_val, chomp_val + extension).replace("\\", "/")
                full_path.append(expected_master_file)
                if os.path.isfile(expected_master_file):
                    validation.append("true")
                else:
                    validation.append("false")

    if input_mode == "fullPath":
        return full_path
    elif input_mode == "list":
        return chomp
    elif input_mode == "validList":
        return [c for c, v in zip(chomp, validation) if v == "true"]
    elif input_mode == "invalidList":
        return [c for c, v in zip(chomp, validation) if v == "false"]
    elif input_mode == "validation":
        return validation
    return []


def existed_seq(input_mode):
    current_project = cmds.textFieldGrp("projPath", query=True, text=True) if cmds.textFieldGrp("projPath", exists=True) else cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
    seq_path = os.path.join(current_project, "scenes/").replace("\\", "/") if current_project else ""
    
    extension = ".mb"
    validation = []
    chomp = []
    full_path = []
    
    if os.path.isdir(seq_path):
        seq_files = [f for f in os.listdir(seq_path) if not f.startswith('.')]
        for seq in seq_files:
            shot_path = os.path.join(seq_path, seq, "").replace("\\", "/")
            if os.path.isdir(shot_path):
                shot_files = [f for f in os.listdir(shot_path) if not f.startswith('.')]
                for shot in shot_files:
                    type_folder_path = os.path.join(shot_path, shot, "").replace("\\", "/")
                    if os.path.isdir(type_folder_path):
                        type_folders = [f for f in os.listdir(type_folder_path) if not f.startswith('.')]
                        for t_folder in type_folders:
                            type_file_path = os.path.join(type_folder_path, t_folder, "").replace("\\", "/")
                            if os.path.isdir(type_file_path):
                                chomp_val = f"{seq}_{shot}_{t_folder}"
                                chomp.append(chomp_val)
                                expected_master = os.path.join(type_file_path, chomp_val + extension).replace("\\", "/")
                                full_path.append(expected_master)
                                if os.path.isfile(expected_master):
                                    validation.append("true")
                                else:
                                    validation.append("false")

    if input_mode == "fullPath":
        return full_path
    elif input_mode == "list":
        return chomp
    elif input_mode == "validList":
        return [c for c, v in zip(chomp, validation) if v == "true"]
    elif input_mode == "invalidList":
        return [c for c, v in zip(chomp, validation) if v == "false"]
    elif input_mode == "validation":
        return validation
    return []


def existed_ref_asset(input_mode):
    all_ref_asset = []
    ref_asset_loaded = []
    asset_short_name = []
    
    all_ref = cmds.file(query=True, reference=True) or []
    all_asset_path = existed_asset("fullPath")
    
    for asset_path in all_asset_path:
        for ref in all_ref:
            temp_ref_match = re.match(r"[^{]*", ref)
            if temp_ref_match:
                temp_ref = temp_ref_match.group(0)
                if temp_ref.replace("\\", "/") == asset_path.replace("\\", "/"):
                    all_ref_asset.append(ref)
                    temp_asset_name = temp_ref.split("/")[-1].split(".")[0]
                    asset_short_name.append(temp_asset_name)
                    
                    if not cmds.file(ref, query=True, deferReference=True):
                        ref_asset_loaded.append("true")
                    else:
                        ref_asset_loaded.append("false")
                        
    if input_mode == "loadingCheck":
        return ref_asset_loaded
    elif input_mode == "fileName":
        return all_ref_asset
    elif input_mode == "shortName":
        return asset_short_name
    return []


def existed_ref_seq(input_mode):
    all_ref_seq = []
    ref_seq_loaded = []
    seq_short_name = []
    
    all_ref = cmds.file(query=True, reference=True) or []
    all_seq_path = existed_seq("fullPath")
    
    for seq_path in all_seq_path:
        for ref in all_ref:
            temp_ref_match = re.match(r"[^{]*", ref)
            if temp_ref_match:
                temp_ref = temp_ref_match.group(0)
                if temp_ref.replace("\\", "/") == seq_path.replace("\\", "/"):
                    all_ref_seq.append(ref)
                    temp_seq_name = temp_ref.split("/")[-1].split(".")[0]
                    seq_short_name.append(temp_seq_name)
                    
                    if not cmds.file(ref, query=True, deferReference=True):
                        ref_seq_loaded.append("true")
                    else:
                        ref_seq_loaded.append("false")
                        
    if input_mode == "loadingCheck":
        return ref_seq_loaded
    elif input_mode == "fileName":
        return all_ref_seq
    elif input_mode == "shortName":
        return seq_short_name
    return []


def seq_file_tree_ui():
    current_project = cmds.textFieldGrp("projPath", query=True, text=True) if cmds.textFieldGrp("projPath", exists=True) else cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
    scene_path = os.path.join(current_project, "scenes/").replace("\\", "/") if current_project else ""
    
    if not current_project or not os.path.isdir(scene_path):
        the_seqs = []
    else:
        the_seqs = [f for f in os.listdir(scene_path) if os.path.isdir(os.path.join(scene_path, f)) and not f.startswith('.')]
        
    if not the_seqs:
        cmds.text(enable=False, align="left", width=175, height=20, label="no Seq exists!")
    else:
        for seq in the_seqs:
            cmds.columnLayout(f"col_{seq}")
            cmds.rowLayout(numberOfColumns=2, columnWidth2=(20, 175))
            cmds.columnLayout()
            
            seq_path = os.path.join(scene_path, seq, "").replace("\\", "/")
            the_shots = [f for f in os.listdir(seq_path) if os.path.isdir(os.path.join(seq_path, f)) and not f.startswith('.')] if os.path.isdir(seq_path) else []
            
            expand = "+" if the_shots else "x"
            enable_btn = False if expand == "x" else True
            
            cmds.iconTextButton(f"iTB_{seq}", enable=enable_btn, width=20, height=20, style="textOnly", label=expand, command=lambda x, sq=seq: shot_file_tree_ui(sq))
            cmds.setParent("..")
            
            cmds.columnLayout()
            cmds.text(enable=enable_btn, align="left", width=175, height=20, label=seq)
            cmds.setParent("..")
            cmds.setParent("..")
            cmds.setParent("..")


def shot_file_tree_ui(input_seq):
    seq_itb = f"iTB_{input_seq}"
    if not cmds.iconTextButton(seq_itb, exists=True): return
        
    expand = cmds.iconTextButton(seq_itb, query=True, label=True)
    
    if expand == "+":
        current_project = cmds.textFieldGrp("projPath", query=True, text=True) if cmds.textFieldGrp("projPath", exists=True) else cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
        seq_path = os.path.join(current_project, "scenes", input_seq, "").replace("\\", "/") if current_project else ""
        
        the_shots = [f for f in os.listdir(seq_path) if os.path.isdir(os.path.join(seq_path, f)) and not f.startswith('.')] if os.path.isdir(seq_path) else []
        
        cmds.setParent(f"col_{input_seq}")
        for shot in the_shots:
            cmds.columnLayout(f"col_{input_seq}_{shot}")
            cmds.rowLayout(numberOfColumns=2, columnWidth2=(20, 175), columnAttach2=("left", "left"), columnOffset2=(10, 10))
            cmds.columnLayout()
            
            shot_path = os.path.join(seq_path, shot, "").replace("\\", "/")
            the_types = [f for f in os.listdir(shot_path) if os.path.isdir(os.path.join(shot_path, f)) and not f.startswith('.')] if os.path.isdir(shot_path) else []
            
            expand_child = "+" if the_types else "x"
            enable_btn = False if expand_child == "x" else True
            
            cmds.iconTextButton(f"iTB_{input_seq}_{shot}", enable=enable_btn, width=20, height=20, style="textOnly", label=expand_child, command=lambda x, sq=input_seq, sh=shot: type_file_tree_ui(sq, sh))
            cmds.setParent("..")
            
            cmds.columnLayout()
            cmds.text(align="left", width=175, height=20, label=shot)
            cmds.setParent("..")
            cmds.setParent("..")
            cmds.setParent("..")
            
        cmds.iconTextButton(seq_itb, edit=True, label="-")
        
    elif expand == "-":
        child_col = cmds.columnLayout(f"col_{input_seq}", query=True, childArray=True) or []
        for i in range(1, len(child_col)): cmds.deleteUI(child_col[i])
        cmds.iconTextButton(seq_itb, edit=True, label="+")


def type_file_tree_ui(input_seq, input_shot):
    shot_itb = f"iTB_{input_seq}_{input_shot}"
    if not cmds.iconTextButton(shot_itb, exists=True): return
        
    expand = cmds.iconTextButton(shot_itb, query=True, label=True)
    
    if expand == "+":
        current_project = cmds.textFieldGrp("projPath", query=True, text=True) if cmds.textFieldGrp("projPath", exists=True) else cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
        shot_path = os.path.join(current_project, "scenes", input_seq, input_shot, "").replace("\\", "/") if current_project else ""
        
        the_types = [f for f in os.listdir(shot_path) if os.path.isdir(os.path.join(shot_path, f)) and not f.startswith('.')] if os.path.isdir(shot_path) else []
        
        cmds.setParent(f"col_{input_seq}_{input_shot}")
        for t in the_types:
            cmds.columnLayout(f"col_{input_seq}_{input_shot}_{t}")
            cmds.rowLayout(numberOfColumns=2, columnWidth2=(5, 185), columnAttach2=("left", "left"))
            cmds.columnLayout()
            cmds.text(width=5, height=20, label="")
            cmds.setParent("..")
            
            expected_master = os.path.join(shot_path, t, f"{input_seq}_{input_shot}_{t}.mb").replace("\\", "/")
            master_exists = os.path.isfile(expected_master)
            
            cmds.columnLayout()
            cmds.iconTextButton(f"iTB_{input_seq}_{input_shot}_{t}", enable=master_exists, width=175, height=20, style="textOnly", label=t, align="left", command=lambda x, p=expected_master: create_reference("seq", p))
            cmds.setParent("..")
            cmds.setParent("..")
            cmds.setParent("..")
            
        cmds.iconTextButton(shot_itb, edit=True, label="-")
        
    elif expand == "-":
        child_col = cmds.columnLayout(f"col_{input_seq}_{input_shot}", query=True, childArray=True) or []
        for i in range(1, len(child_col)): cmds.deleteUI(child_col[i])
        cmds.iconTextButton(shot_itb, edit=True, label="+")


def adjust_scroll_layout(input_name, height):
    if cmds.scrollLayout(input_name, exists=True):
        cmds.scrollLayout(input_name, edit=True, height=height)


def ref_loading_box_wrapper(input_name, input_num, *args):
    check_box_name = f"{input_name}_{input_num}_loadBox"
    icon_text_name = f"{input_name}_{input_num}_SelButton"
    
    if cmds.checkBox(check_box_name, exists=True) and cmds.iconTextRadioButton(icon_text_name, exists=True):
        load = cmds.checkBox(check_box_name, query=True, value=True)
        path = cmds.iconTextRadioButton(icon_text_name, query=True, annotation=True)
        ref_node = cmds.file(path, query=True, referenceNode=True)
        
        if load:
            cmds.file(loadReference=ref_node)
        else:
            cmds.file(unloadReference=ref_node)


def create_reference(input_mode, input_path):
    if input_mode == "seq":
        cmds.file(input_path, reference=True)
    elif input_mode == "asset":
        lib_path = cmds.optionVar(query="ops_libPath") if cmds.optionVar(exists="ops_libPath") else ""
        if not lib_path:
            current_project = cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
            lib_path = os.path.join(current_project, "lib/").replace("\\", "/") if current_project else ""
            
        path = os.path.join(lib_path, input_path, f"{input_path}_asset.mb").replace("\\", "/")
        cmds.file(path, reference=True, type="mayaBinary", groupLocator=True, namespace=input_path, options="v=0")
        
    ref_inv_ui()


def ref_inv_ui():
    if cmds.scrollLayout("allRefScroll", query=True, exists=True):
        cmds.deleteUI("allRefScroll")
        
    cmds.scrollLayout("allRefScroll", parent="col_RefInv", backgroundColor=(1, 1, 1), width=240, horizontalScrollBarThickness=0, verticalScrollBarThickness=0)
    cmds.columnLayout(columnWidth=240, height=200)
    cmds.rowLayout(numberOfColumns=3, height=20, columnWidth3=(20, 20, 160))
    cmds.columnLayout("refC1")
    cmds.setParent("..")
    cmds.columnLayout("refC2")
    cmds.iconTextRadioCollection("allRefInventory")
    cmds.setParent("..")
    cmds.setParent("..")
    
    existed_ref_seq_short = existed_ref_seq("shortName")
    seq_loading_check = existed_ref_seq("loadingCheck")
    existed_ref_seq_path = existed_ref_seq("fileName")
    
    for i in range(len(existed_ref_seq_short)):
        load = True if seq_loading_check[i] == "true" else False
        
        cmds.checkBox(f"{existed_ref_seq_short[i]}_{i}_loadBox", label="", value=load, width=20, height=20, parent="refC1", command=lambda x, n=existed_ref_seq_short[i], num=i: ref_loading_box_wrapper(n, num))
        
        cmds.iconTextRadioButton(f"{existed_ref_seq_short[i]}_{i}_SelButton", width=200, height=20, style="textOnly", label=existed_ref_seq_short[i], font="plainLabelFont", backgroundColor=(1, 1, 1), annotation=existed_ref_seq_path[i], parent="refC2", collection="allRefInventory")
        cmds.iconTextRadioButton(f"{existed_ref_seq_short[i]}_{i}_SelButton", edit=True, enable=True)
        
    existed_ref_asset_short = existed_ref_asset("shortName")
    asset_loading_check = existed_ref_asset("loadingCheck")
    existed_ref_asset_path = existed_ref_asset("fileName")
    
    for i in range(len(existed_ref_asset_short)):
        load = True if asset_loading_check[i] == "true" else False
        
        cmds.checkBox(f"{existed_ref_asset_short[i]}_{i}_loadBox", label="", value=load, width=20, height=20, parent="refC1", command=lambda x, n=existed_ref_asset_short[i], num=i: ref_loading_box_wrapper(n, num))
        
        cmds.iconTextRadioButton(f"{existed_ref_asset_short[i]}_{i}_SelButton", width=200, height=20, style="textOnly", label=existed_ref_asset_short[i], font="plainLabelFont", backgroundColor=(1, 1, 1), annotation=existed_ref_asset_path[i], parent="refC2", collection="allRefInventory")
        cmds.iconTextRadioButton(f"{existed_ref_asset_short[i]}_{i}_SelButton", edit=True, enable=True)
        
    cmds.scrollLayout("allRefScroll", edit=True, resizeCommand="import opsSceneInv; opsSceneInv.adjust_scroll_layout('allRefScroll', 200)", height=200)
    cmds.setParent("..")
    cmds.setParent("..")