"""Scene and Asset Inventory functions for openPypeline Studio in Maya.

Handles querying active Maya scene references, tracking loaded assets and shot components, and providing PySide6 dialogs for reference inspection and replacement. Refactored from ``openPipelineSceneInv.mel`` to Python 3 and PySide6.

:File: ops_scene_inv.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import logging
import os
import re
from typing import Any, Optional

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
import maya.cmds as cmds
from PySide6 import QtCore, QtWidgets

from openpypeline.core.util import prefs

#: Module logger for Maya scene and reference inventory operations.
logger = logging.getLogger("openPypeline.sceneInv")

def existed_asset(input_mode: str) -> list[str]:
    """List library assets or their expected master paths and validation state.

    Scans the project library folder (``ops_libPath`` or ``<project>/lib/``) for matching asset directories and checks whether ``<asset>_asset.mb`` exists on disk.

    :param input_mode: Output selector—one of ``"fullPath"``, ``"list"``, ``"validList"``, ``"invalidList"``, or ``"validation"``.
    :returns: Filtered list of asset names, expected master file paths, or ``"true"``/``"false"`` validation strings matching ``input_mode``, or an empty list for unrecognized modes.
    """
    current_project = prefs.get_pref("ops_currProjectPath", "")
    the_path = prefs.get_pref("ops_libPath", "")
    if not the_path and current_project:
        the_path = os.path.join(current_project, "lib/").replace("\\", "/")

    # Resolve configured master extension from project prefs (defaulting to Maya ASCII)
    master_ext = prefs.get_pref("ops_masterFormat", "ma").lstrip(".") or "ma"
    extension = f"_asset.{master_ext}"

    validation: list[str] = []
    chomp: list[str] = []
    full_path: list[str] = []

    if os.path.isdir(the_path):
        the_files = [f for f in os.listdir(the_path) if not f.startswith(".")]
        for item in the_files:
            match = re.match(r"^[a-zA-Z_0-9]+", item)
            if match:
                chomp_val = match.group(0)
                chomp.append(chomp_val)
                expected_master_file = os.path.join(
                    the_path, chomp_val, chomp_val + extension
                ).replace("\\", "/")
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


def existed_seq(input_mode: str) -> list[str]:
    """List scene components or expected master paths with existence status.

    Traverses ``<project>/scenes/<seq>/<shot>/<component>/`` directories and
    checks whether ``<seq>_<shot>_<component>.mb`` exists on disk.

    :param input_mode: Output selector—one of ``"fullPath"``, ``"list"``, ``"validList"``, ``"invalidList"``, or ``"validation"``.
    :returns: Filtered list of component identifiers, expected master file paths, or ``"true"``/``"false"`` validation strings matching ``input_mode``, or an empty list for unrecognized modes.
    """
    current_project = prefs.get_pref("ops_currProjectPath", "")
    seq_path = (
        os.path.join(current_project, "scenes/").replace("\\", "/")
        if current_project
        else ""
    )

    # Resolve configured master extension from project prefs (defaulting to Maya ASCII)
    master_ext = prefs.get_pref("ops_masterFormat", "ma").lstrip(".") or "ma"
    extension = f".{master_ext}"

    validation: list[str] = []
    chomp: list[str] = []
    full_path: list[str] = []

    if os.path.isdir(seq_path):
        seq_files = [f for f in os.listdir(seq_path) if not f.startswith(".")]
        for seq in seq_files:
            shot_path = os.path.join(seq_path, seq, "").replace("\\", "/")
            if os.path.isdir(shot_path):
                shot_files = [f for f in os.listdir(shot_path) if not f.startswith(".")]
                for shot in shot_files:
                    type_folder_path = os.path.join(shot_path, shot, "").replace(
                        "\\", "/"
                    )
                    if os.path.isdir(type_folder_path):
                        type_folders = [
                            f
                            for f in os.listdir(type_folder_path)
                            if not f.startswith(".")
                        ]
                        for t_folder in type_folders:
                            type_file_path = os.path.join(
                                type_folder_path, t_folder, ""
                            ).replace("\\", "/")
                            if os.path.isdir(type_file_path):
                                chomp_val = f"{seq}_{shot}_{t_folder}"
                                chomp.append(chomp_val)
                                expected_master = os.path.join(
                                    type_file_path, chomp_val + extension
                                ).replace("\\", "/")
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


def existed_ref_asset(input_mode: str) -> list[str]:
    """Return loaded-state, reference paths, or short names for asset references.

    Matches active Maya scene references against expected library asset master paths from :func:`existed_asset`.

    :param input_mode: Output selector—one of ``"loadingCheck"``, ``"fileName"``, or ``"shortName"``.
    :returns: List of ``"true"``/``"false"`` load states, unresolved reference strings (including copy-number suffixes), or asset base names.
    """
    all_ref_asset: list[str] = []
    ref_asset_loaded: list[str] = []
    asset_short_name: list[str] = []

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


def existed_ref_seq(input_mode: str) -> list[str]:
    """Return loaded-state, reference paths, or short names for shot references.

    Matches active Maya scene references against expected sequence component master paths from :func:`existed_seq`.

    :param input_mode: Output selector—one of ``"loadingCheck"``, ``"fileName"``, or ``"shortName"``.
    :returns: List of ``"true"``/``"false"`` load states, unresolved reference strings (including copy-number suffixes), or component base names.
    """
    all_ref_seq: list[str] = []
    ref_seq_loaded: list[str] = []
    seq_short_name: list[str] = []

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


def create_reference(input_mode: str, input_path: str) -> None:
    """Reference a sequence or asset into Maya and refresh the inventory window.

    :param input_mode: Reference target mode—``"seq"`` to reference ``input_path`` directly, or ``"asset"`` to resolve ``<lib>/<input_path>/<input_path>_asset.mb`` with a matching namespace.
    :param input_path: Direct scene file path (for ``"seq"``) or library asset directory name (for ``"asset"``).
    """
    if input_mode == "seq":
        cmds.file(input_path, reference=True)
    elif input_mode == "asset":
        lib_path = prefs.get_pref("ops_libPath", "")
        if not lib_path:
            current_project = prefs.get_pref("ops_currProjectPath", "")
            lib_path = (
                os.path.join(current_project, "lib/").replace("\\", "/")
                if current_project
                else ""
            )

        # Resolve configured master extension and Maya file type (defaulting to Maya ASCII)
        master_ext = prefs.get_pref("ops_masterFormat", "ma").lstrip(".") or "ma"
        file_type = "mayaBinary" if master_ext == "mb" else "mayaAscii"
        path = os.path.join(lib_path, input_path, f"{input_path}_asset.{master_ext}").replace(
            "\\", "/"
        )
        cmds.file(
            path,
            reference=True,
            type=file_type,
            groupLocator=True,
            namespace=input_path,
            options="v=0",
        )

    if _scene_inv_dialog is not None:
        _scene_inv_dialog.refresh_all()

class SceneInventoryUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """PySide6 implementation of the Scene Inventory and Reference manager.

    Displays active Maya asset and shot references inside a checkable ``QTreeWidget``, allowing artists to toggle reference load/unload states and refresh the scene reference list.

    :ivar ref_tree: Tree widget listing active scene references and load checkboxes.
    :vartype ref_tree: QtWidgets.QTreeWidget
    :ivar refresh_btn: Button triggering :meth:`refresh_all` to reload reference states from Maya.
    :vartype refresh_btn: QtWidgets.QPushButton
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the scene inventory window and construct its controls.

        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(parent)
        self.setWindowTitle("Scene Inventory")
        self.setObjectName("opsSceneInventoryUI")
        self.setMinimumSize(400, 400)
        self.setWindowFlags(QtCore.Qt.Window)
        self._build_ui()

    def showWindow(self) -> None:
        """Refresh reference data before displaying the scene inventory."""
        self.refresh_all()
        self.show()

    def _build_ui(self) -> None:
        """Build the reference tree and its refresh control."""
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

    def refresh_all(self) -> None:
        """Reload all listed scene references."""
        self._populate_refs()

    def _populate_refs(self) -> None:
        """Fill the tree with asset and sequence references and load states."""
        self.ref_tree.blockSignals(True)
        self.ref_tree.clear()

        for ref_type in [existed_ref_seq, existed_ref_asset]:
            shorts = ref_type("shortName")
            loads = ref_type("loadingCheck")
            paths = ref_type("fileName")

            for i in range(len(shorts)):
                item = QtWidgets.QTreeWidgetItem(self.ref_tree, ["", shorts[i]])
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(
                    0,
                    QtCore.Qt.Checked if loads[i] == "true" else QtCore.Qt.Unchecked,
                )
                item.setData(0, QtCore.Qt.UserRole, paths[i])
                item.setToolTip(1, paths[i])

        self.ref_tree.blockSignals(False)

    def _on_ref_item_changed(
        self, item: QtWidgets.QTreeWidgetItem, column: int
    ) -> None:
        """Load or unload a Maya reference when its checkbox changes.

        :param item: Modified tree widget row containing the reference path in ``QtCore.Qt.UserRole``.
        :param column: Column index that changed (handled only when ``0``).
        """
        if column == 0:
            path = item.data(0, QtCore.Qt.UserRole)
            load = item.checkState(0) == QtCore.Qt.Checked
            try:
                ref_node = cmds.file(path, query=True, referenceNode=True)
                if load:
                    cmds.file(loadReference=ref_node)
                else:
                    cmds.file(unloadReference=ref_node)
            except Exception as e:
                logger.warning(f"Failed to toggle reference: {e}")


#: Singleton instance of :class:`SceneInventoryUI` retained while open.
_scene_inv_dialog: Optional[SceneInventoryUI] = None


def show_window() -> None:
    """Create (if needed) and display the PySide6 Scene Inventory UI.

    Instantiates the singleton :class:`SceneInventoryUI` dialog if it does not already exist and calls :meth:`SceneInventoryUI.showWindow`.
    """
    global _scene_inv_dialog
    if _scene_inv_dialog is None:
        _scene_inv_dialog = SceneInventoryUI()
    _scene_inv_dialog.showWindow()

