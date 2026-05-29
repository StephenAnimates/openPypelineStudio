"""
Module: opsProjDialogController.py

Description:
    The Controller class for the openPypeline Studio Project Dialog.
    Handles logic, data population, and validation for creating or editing projects.
"""

import os
import re
from PySide6 import QtWidgets, QtCore

import UIObjects
import opsProject
import opsInfo
import opsUtils
import opsActions
import opsUIWrappers
from openpypeline.app.maya.ui.opsProjDialogGUI import opsProjDialogGUI

class OpsProjDialogController(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.UIObjects = UIObjects.UIObjects()
        
        self.view = opsProjDialogGUI()
        self.mode = 0
        self.old_name = ""
        
        self._warning_timer = QtCore.QTimer(self)
        self._warning_timer.setSingleShot(True)
        self._warning_timer.timeout.connect(self._clear_warning)

        self._connect_signals()

    def showWindow(self):
        """Configures the dialog state based on mode and shows it."""
        if self.mode == 1:
            self.view.setWindowTitle(f"Edit Project: {self.old_name}")
        else:
            self.view.setWindowTitle("Create New Project")
            
        self._populate_fields()
        self.view.show()

    def _connect_signals(self):
        self.view.path_browse_btn.clicked.connect(lambda: self._browse_directory(self.view.proj_path_field, append_proj_name=True))
        
        if hasattr(self.view, 'maya_proj_btn'):
            self.view.maya_proj_btn.clicked.connect(self._populate_from_maya)

        self.view.custom_users_chk.stateChanged.connect(self._toggle_custom_users)
        self.view.custom_users_btn.clicked.connect(self._select_custom_users)

        self.view.archive_btn.clicked.connect(lambda: self._browse_directory(self.view.archive_field))
        self.view.deleted_btn.clicked.connect(lambda: self._browse_directory(self.view.deleted_field))

        self.view.accept_btn.clicked.connect(self.on_accept)
        self.view.cancel_btn.clicked.connect(self.view.close)

        # Real-time Validation Connections
        self.view.proj_name_field.textEdited.connect(lambda t: self._validate_name_field(t, self.view.proj_name_field))
        self.view.master_name_field.textEdited.connect(lambda t: self._validate_name_field(t, self.view.master_name_field))
        self.view.wip_name_field.textEdited.connect(lambda t: self._validate_name_field(t, self.view.wip_name_field))

        self.view.asset_lib_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.asset_lib_field))
        self.view.scripts_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.scripts_field))
        self.view.shot_lib_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.shot_lib_field))
        self.view.textures_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.textures_field))
        self.view.renders_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.renders_field))
        self.view.particles_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.particles_field))
        self.view.archive_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.archive_field))
        self.view.deleted_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.view.deleted_field))

    def _show_warning(self, message):
        self.view.validation_warning_label.setText(message)
        self._warning_timer.start(3500)

    def _clear_warning(self):
        self.view.validation_warning_label.setText("")

    def _validate_name_field(self, text, line_edit):
        self._apply_validation(text, line_edit, r'[^a-zA-Z0-9_]')

    def _validate_folder_field(self, text, line_edit):
        if '\\' in text:
            text = text.replace('\\', '/')
            self._show_warning("Backslashes converted to forward slashes.")
        self._apply_validation(text, line_edit, r'[^a-zA-Z0-9_/]')
        
    def _apply_validation(self, text, line_edit, regex_pattern):
        original_text = text
        warning_msg = ""
        
        if ' ' in text:
            text = text.replace(' ', '_')
            warning_msg = "Spaces are not allowed. Replaced with underscores."
            
        filtered_text = re.sub(regex_pattern, '', text)
        if filtered_text != text:
            text = filtered_text
            warning_msg = "Special characters are not allowed and were removed."
            
        if text != original_text:
            cursor_pos = line_edit.cursorPosition()
            diff = len(original_text) - len(text)
            line_edit.blockSignals(True)
            line_edit.setText(text)
            line_edit.blockSignals(False)
            line_edit.setCursorPosition(max(0, cursor_pos - diff))
            self._show_warning(warning_msg)

    def _browse_directory(self, line_edit, append_proj_name=False):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self.view, "Select Location")
        if dir_path:
            if append_proj_name:
                proj_name = self.view.proj_name_field.text().strip()
                if proj_name:
                    dir_path = os.path.join(dir_path, proj_name)
            line_edit.setText(dir_path.replace("\\", "/"))

    def _populate_from_maya(self):
        try:
            import maya.cmds as cmds
            proj_dir = cmds.workspace(query=True, rootDirectory=True)
            if proj_dir:
                self.view.proj_path_field.setText(proj_dir.replace("\\", "/").rstrip("/"))
                
            scene_dir = cmds.workspace(fileRuleEntry="scene")
            if scene_dir:
                self.view.shot_lib_field.setText(scene_dir)
                self.view.asset_lib_field.setText(f"{scene_dir}/assets")
                
            images_dir = cmds.workspace(fileRuleEntry="images")
            if images_dir:
                self.view.renders_field.setText(f"{images_dir}/renders")
                
            source_images_dir = cmds.workspace(fileRuleEntry="sourceImages")
            if source_images_dir:
                self.view.textures_field.setText(source_images_dir)
                
            scripts_dir = cmds.workspace(fileRuleEntry="scripts")
            if scripts_dir:
                self.view.scripts_field.setText(scripts_dir)
                
            particles_dir = cmds.workspace(fileRuleEntry="particles")
            if particles_dir:
                self.view.particles_field.setText(particles_dir)
        except ImportError:
            pass

    def _toggle_custom_users(self, state):
        is_enabled = bool(state)
        self.view.custom_users_field.setEnabled(is_enabled)
        self.view.custom_users_btn.setEnabled(is_enabled)

    def _select_custom_users(self):
        users = opsProject.get_users()
        dialog = QtWidgets.QDialog(self.view)
        dialog.setWindowTitle("Set Project Users")
        dialog.setMinimumSize(300, 240)
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel("Select users to add to project:"))
        list_widget = QtWidgets.QListWidget()
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        list_widget.addItems(users)
        layout.addWidget(list_widget)

        current_users = self.view.custom_users_field.text().split(",")
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() in current_users:
                item.setSelected(True)

        btn_layout = QtWidgets.QHBoxLayout()
        set_btn = QtWidgets.QPushButton("Set Users")
        edit_btn = QtWidgets.QPushButton("Edit Global Users")
        cancel_btn = QtWidgets.QPushButton("Cancel")

        def on_set():
            selected = [item.text() for item in list_widget.selectedItems()]
            self.view.custom_users_field.setText(",".join(selected))
            dialog.accept()

        set_btn.clicked.connect(on_set)
        edit_btn.clicked.connect(opsProject.proj_edit_users)
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(set_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _populate_fields(self):
        date_str = opsInfo.get_date()
        self.view.creation_date_field.setText(date_str)
        self.view.deadline_field.setText(date_str)
        
        if self.mode == 1 and self.old_name:
            proj_xml = opsProject.get_single_project_xml(self.old_name)
            if proj_xml:
                self.view.proj_name_field.setText(opsUtils.get_xml_data(proj_xml, "name"))
                self.view.proj_path_field.setText(opsUtils.get_xml_data(proj_xml, "path"))
                self.view.desc_field.setText(opsUtils.get_xml_data(proj_xml, "description"))
                self.view.creation_date_field.setText(opsUtils.get_xml_data(proj_xml, "date"))
                self.view.deadline_field.setText(opsUtils.get_xml_data(proj_xml, "deadline"))
                
                self.view.asset_lib_field.setText(opsUtils.get_xml_data(proj_xml, "libraryfolder"))
                self.view.shot_lib_field.setText(opsUtils.get_xml_data(proj_xml, "scenesfolder"))
                self.view.archive_field.setText(opsUtils.get_xml_data(proj_xml, "archivefolder"))
                self.view.deleted_field.setText(opsUtils.get_xml_data(proj_xml, "deletedfolder"))
                self.view.renders_field.setText(opsUtils.get_xml_data(proj_xml, "rendersfolder"))
                self.view.particles_field.setText(opsUtils.get_xml_data(proj_xml, "particlesfolder"))
                self.view.textures_field.setText(opsUtils.get_xml_data(proj_xml, "texturesfolder"))
                self.view.scripts_field.setText(opsUtils.get_xml_data(proj_xml, "scriptsfolder"))
                
                self.view.master_name_field.setText(opsUtils.get_xml_data(proj_xml, "mastername"))
                self.view.master_format_combo.setCurrentText(opsUtils.get_xml_data(proj_xml, "masterformat"))
                self.view.wip_name_field.setText(opsUtils.get_xml_data(proj_xml, "wipname"))
                self.view.wip_format_combo.setCurrentText(opsUtils.get_xml_data(proj_xml, "wipformat"))
                
                status = int(opsUtils.get_xml_data(proj_xml, "status") or 1)
                self.view.status_combo.setCurrentIndex(1 - status)
                
                user_mode = int(opsUtils.get_xml_data(proj_xml, "userMode") or 0)
                self.view.custom_users_chk.setChecked(bool(user_mode))
                
                curr_users = opsUtils.get_xml_data(proj_xml, "users")
                if curr_users:
                    global_users = opsProject.get_users()
                    valid_users = [u for u in curr_users.split(",") if u in global_users]
                    self.view.custom_users_field.setText(",".join(valid_users))
                else:
                    self.view.custom_users_field.setText("")
                    
                self.view.asset_lib_field.setReadOnly(True)
                self.view.shot_lib_field.setReadOnly(True)
                self.view.master_name_field.setReadOnly(True)
                self.view.wip_name_field.setReadOnly(True)
                self.view.master_format_combo.setEnabled(False)
                self.view.wip_format_combo.setEnabled(False)
        else:
            self.view.custom_users_chk.setChecked(False)
            self.view.proj_name_field.clear()
            self.view.proj_path_field.clear()
            self.view.desc_field.clear()
            self.view.custom_users_field.clear()
            
            self.view.asset_lib_field.setReadOnly(False)
            self.view.shot_lib_field.setReadOnly(False)
            self.view.master_name_field.setReadOnly(False)
            self.view.wip_name_field.setReadOnly(False)
            self.view.master_format_combo.setEnabled(True)
            self.view.wip_format_combo.setEnabled(True)

    def on_accept(self, *args):
        new_name = self.view.proj_name_field.text().strip()
        new_path = self.view.proj_path_field.text().strip()
        new_description = self.view.desc_field.text().strip()
        new_status = "1" if self.view.status_combo.currentIndex() == 0 else "0"
        new_date = self.view.creation_date_field.text().strip()
        new_deadline = self.view.deadline_field.text().strip()
        new_master_name = self.view.master_name_field.text().strip()
        new_master_format = self.view.master_format_combo.currentText().strip()
        new_wip_name = self.view.wip_name_field.text().strip()
        new_wip_format = self.view.wip_format_combo.currentText().strip()
        new_lib_loc = self.view.asset_lib_field.text().strip()
        new_shot_loc = self.view.shot_lib_field.text().strip()
        new_renders_loc = self.view.renders_field.text().strip()
        new_scripts_loc = self.view.scripts_field.text().strip()
        new_textures_loc = self.view.textures_field.text().strip()
        new_particles_loc = self.view.particles_field.text().strip()
        new_archive_loc = self.view.archive_field.text().strip()
        new_deleted_loc = self.view.deleted_field.text().strip()
        new_users = self.view.custom_users_field.text().strip()
        user_mode = "1" if self.view.custom_users_chk.isChecked() else "0"
        
        result = opsActions.create_or_edit_project(
            self.mode, self.old_name, new_name, new_path, new_description, new_status, new_date, new_deadline,
            new_master_name, new_master_format, new_wip_name, new_wip_format, new_lib_loc,
            new_shot_loc, new_renders_loc, new_scripts_loc, new_textures_loc, new_particles_loc,
            new_archive_loc, new_deleted_loc, new_users, user_mode
        )
        
        if result:
            self.view.close()
            opsUIWrappers.refresh_ui()
            if hasattr(self.UIObjects, 'opsProjectManagerGUI'):
                try: 
                    self.UIObjects.opsProjectManagerGUI.on_refresh_list()
                except: pass