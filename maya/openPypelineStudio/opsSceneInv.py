"""
File: opsSceneInv.py
Description: Scene and Asset Inventory functions for openPypeline Studio.
             Handles tracking existing assets, sequences, and reference loading.
             Refactored from openPipelineSceneInv.mel to Python 3 and PySide6.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import os
import re
from openpypeline.core.util import prefs
import logging
from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

logger = logging.getLogger("openPypeline.sceneInv")


def existed_asset(input_mode):
    current_project = prefs.get_pref("ops_currProjectPath", "")
    the_path = prefs.get_pref("ops_libPath", "")
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
    current_project = prefs.get_pref("ops_currProjectPath", "")
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


def create_reference(input_mode, input_path):
    if input_mode == "seq":
        cmds.file(input_path, reference=True)
    elif input_mode == "asset":
        lib_path = prefs.get_pref("ops_libPath", "")
        if not lib_path:
            current_project = prefs.get_pref("ops_currProjectPath", "")
            lib_path = os.path.join(current_project, "lib/").replace("\\", "/") if current_project else ""
            
        path = os.path.join(lib_path, input_path, f"{input_path}_asset.mb").replace("\\", "/")
        cmds.file(path, reference=True, type="mayaBinary", groupLocator=True, namespace=input_path, options="v=0")
        
    if _scene_inv_dialog is not None:
        _scene_inv_dialog.refresh_all()


class SceneInventoryUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """PySide6 implementation of the Scene Inventory and Reference manager."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scene Inventory")
        self.setObjectName("opsSceneInventoryUI")
        self.setMinimumSize(400, 400)
        self.setWindowFlags(QtCore.Qt.Window)
        self._build_ui()

    def showWindow(self):
        self.refresh_all()
        self.show()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Reference Inventory
        ref_group = QtWidgets.QGroupBox("Reference Inventory")
        ref_layout = QtWidgets.QVBoxLayout(ref_group)
        self.ref_tree = QtWidgets.QTreeWidget()
        self.ref_tree.setHeaderLabels(["Load", "Reference Namespace"])
        self.ref_tree.setColumnWidth(0, 50)
        self.ref_tree.itemChanged.connect(self._on_ref_item_changed)
        ref_layout.addWidget(self.ref_tree)
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton("Refresh Inventory")
        self.refresh_btn.setMinimumHeight(30)
        self.refresh_btn.clicked.connect(self.refresh_all)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        ref_layout.addLayout(btn_layout)
        
        layout.addWidget(ref_group)
        
    def refresh_all(self):
        self._populate_refs()

    def _populate_refs(self):
        self.ref_tree.blockSignals(True)
        self.ref_tree.clear()
        
        for ref_type in [existed_ref_seq, existed_ref_asset]:
            shorts = ref_type("shortName")
            loads = ref_type("loadingCheck")
            paths = ref_type("fileName")
            
            for i in range(len(shorts)):
                item = QtWidgets.QTreeWidgetItem(self.ref_tree, ["", shorts[i]])
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(0, QtCore.Qt.Checked if loads[i] == "true" else QtCore.Qt.Unchecked)
                item.setData(0, QtCore.Qt.UserRole, paths[i])
                item.setToolTip(1, paths[i])
                
        self.ref_tree.blockSignals(False)

    def _on_ref_item_changed(self, item, column):
        if column == 0:
            path = item.data(0, QtCore.Qt.UserRole)
            load = (item.checkState(0) == QtCore.Qt.Checked)
            try:
                ref_node = cmds.file(path, query=True, referenceNode=True)
                if load: cmds.file(loadReference=ref_node)
                else: cmds.file(unloadReference=ref_node)
            except Exception as e:
                logger.warning(f"Failed to toggle reference: {e}")


_scene_inv_dialog = None

def show_window():
    """Launches the PySide6 Scene Inventory UI."""
    global _scene_inv_dialog
    if _scene_inv_dialog is None:
        _scene_inv_dialog = SceneInventoryUI()
    _scene_inv_dialog.showWindow()