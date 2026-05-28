"""
Module: opsProjDialogGUI.py

Description:
    Opens the Project Dialog Window. This is used either for creating a new project 
    or editing an existing project using PySide6.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import re
from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import UIObjects as UIObjects
import opsProject
import opsInfo
import opsUtils
import opsActions
import opsUIWrappers

# --- UI Stylesheet ---
OPS_PROJ_DIALOG_STYLESHEET = """
    QPushButton[styleClass="acceptBtn"] {
        background-color: #6699cc; 
        color: black; 
        font-weight: bold;
    }
"""

class opsProjDialogGUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    A PySide6 Maya window class for creating or editing an openPypeline Studio project.
    """

    def __init__(self, parent=None):
        """
        Initialize the Project Dialog window. Sets up window dimensions and defaults.
        """
        super().__init__(parent=parent)
        self.UIObjects = UIObjects.UIObjects()
        
        self.setWindowTitle("Create New Project")
        self.setObjectName("openPypelineProjDialog")
        self.setMinimumSize(450, 650)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.mode = 0
        self.old_name = ""
        
        self._warning_timer = QtCore.QTimer(self)
        self._warning_timer.setSingleShot(True)
        self._warning_timer.timeout.connect(self._clear_warning)

        self._build_ui()

    def showWindow(self):
        """Configures the dialog state based on mode and shows it."""
        if self.mode == 1:
            self.setWindowTitle(f"Edit Project: {self.old_name}")
        else:
            self.setWindowTitle("Create New Project")
            
        self._populate_fields()
        self.show()
    
    def _build_ui(self):
        """Constructs the UI using PySide widgets and layouts."""
        self.setStyleSheet(OPS_PROJ_DIALOG_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)

        # --- Project Settings Group ---
        settings_group = QtWidgets.QGroupBox("Project Settings")
        settings_layout = QtWidgets.QFormLayout(settings_group)

        self.proj_name_field = QtWidgets.QLineEdit()
        self.proj_name_field.setMaxLength(22)

        path_layout = QtWidgets.QHBoxLayout()
        self.proj_path_field = QtWidgets.QLineEdit()
        self.path_browse_btn = QtWidgets.QPushButton("Browse...")
        self.path_browse_btn.clicked.connect(lambda: self._browse_directory(self.proj_path_field, append_proj_name=True))
        
        self.maya_proj_btn = QtWidgets.QPushButton("Use Maya Project")
        self.maya_proj_btn.clicked.connect(self._populate_from_maya)
        
        path_layout.addWidget(self.proj_path_field)
        path_layout.addWidget(self.path_browse_btn)
        
        try:
            import maya.cmds
            path_layout.addWidget(self.maya_proj_btn)
        except ImportError:
            pass

        self.desc_field = QtWidgets.QLineEdit()
        self.desc_field.setMaxLength(250)

        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["active", "inactive"])

        settings_layout.addRow("Project Name:", self.proj_name_field)
        settings_layout.addRow("Project Path:", path_layout)
        settings_layout.addRow("Description:", self.desc_field)
        settings_layout.addRow("Status:", self.status_combo)

        main_layout.addWidget(settings_group)

        # --- Users & Dates Group ---
        users_dates_group = QtWidgets.QGroupBox("Users & Dates")
        users_dates_layout = QtWidgets.QFormLayout(users_dates_group)

        self.custom_users_chk = QtWidgets.QCheckBox("Enable Custom Users")
        self.custom_users_chk.stateChanged.connect(self._toggle_custom_users)

        users_layout = QtWidgets.QHBoxLayout()
        self.custom_users_field = QtWidgets.QLineEdit()
        self.custom_users_field.setReadOnly(True)
        self.custom_users_field.setEnabled(False)
        self.custom_users_btn = QtWidgets.QPushButton("...")
        self.custom_users_btn.setEnabled(False)
        self.custom_users_btn.clicked.connect(self._select_custom_users)
        users_layout.addWidget(self.custom_users_field)
        users_layout.addWidget(self.custom_users_btn)

        self.creation_date_field = QtWidgets.QLineEdit("dd/mm/year")
        self.deadline_field = QtWidgets.QLineEdit("dd/mm/year")

        users_dates_layout.addRow("", self.custom_users_chk)
        users_dates_layout.addRow("Users:", users_layout)
        users_dates_layout.addRow("Creation Date:", self.creation_date_field)
        users_dates_layout.addRow("Deadline:", self.deadline_field)

        main_layout.addWidget(users_dates_group)

        # --- Files Group ---
        files_group = QtWidgets.QGroupBox("Files (Master / WIP)")
        files_layout = QtWidgets.QGridLayout(files_group)

        files_layout.addWidget(QtWidgets.QLabel("Master Name:"), 0, 0)
        self.master_name_field = QtWidgets.QLineEdit("master")
        files_layout.addWidget(self.master_name_field, 0, 1)

        files_layout.addWidget(QtWidgets.QLabel("Format:"), 0, 2)
        self.master_format_combo = QtWidgets.QComboBox()
        self.master_format_combo.addItems(["ma", "mb", "usd", "usda", "abc"])
        files_layout.addWidget(self.master_format_combo, 0, 3)

        files_layout.addWidget(QtWidgets.QLabel("WIP Name:"), 1, 0)
        self.wip_name_field = QtWidgets.QLineEdit("wip")
        files_layout.addWidget(self.wip_name_field, 1, 1)

        files_layout.addWidget(QtWidgets.QLabel("Format:"), 1, 2)
        self.wip_format_combo = QtWidgets.QComboBox()
        self.wip_format_combo.addItems(["ma", "mb", "usd", "usda", "abc"])
        files_layout.addWidget(self.wip_format_combo, 1, 3)

        main_layout.addWidget(files_group)

        # --- Sub-Folders Group ---
        subfolders_group = QtWidgets.QGroupBox("Sub-Folder Names")
        subfolders_layout = QtWidgets.QGridLayout(subfolders_group)

        self.asset_lib_field = QtWidgets.QLineEdit("scenes/assets")
        self.scripts_field = QtWidgets.QLineEdit("scripts")
        self.shot_lib_field = QtWidgets.QLineEdit("scenes")
        self.textures_field = QtWidgets.QLineEdit("sourceimages")
        self.renders_field = QtWidgets.QLineEdit("images/renders")
        self.particles_field = QtWidgets.QLineEdit("particles")

        subfolders_layout.addWidget(QtWidgets.QLabel("Asset Library:"), 0, 0)
        subfolders_layout.addWidget(self.asset_lib_field, 0, 1)
        subfolders_layout.addWidget(QtWidgets.QLabel("Scripts:"), 0, 2)
        subfolders_layout.addWidget(self.scripts_field, 0, 3)

        subfolders_layout.addWidget(QtWidgets.QLabel("Shot Library:"), 1, 0)
        subfolders_layout.addWidget(self.shot_lib_field, 1, 1)
        subfolders_layout.addWidget(QtWidgets.QLabel("Textures:"), 1, 2)
        subfolders_layout.addWidget(self.textures_field, 1, 3)

        subfolders_layout.addWidget(QtWidgets.QLabel("Renders:"), 2, 0)
        subfolders_layout.addWidget(self.renders_field, 2, 1)
        subfolders_layout.addWidget(QtWidgets.QLabel("Particles:"), 2, 2)
        subfolders_layout.addWidget(self.particles_field, 2, 3)

        main_layout.addWidget(subfolders_group)

        # --- Archive / Deleted Group ---
        archive_group = QtWidgets.QGroupBox("Archived and Deleted Locations")
        archive_layout = QtWidgets.QFormLayout(archive_group)

        arch_layout = QtWidgets.QHBoxLayout()
        self.archive_field = QtWidgets.QLineEdit("archive")
        self.archive_btn = QtWidgets.QPushButton("Browse...")
        self.archive_btn.clicked.connect(lambda: self._browse_directory(self.archive_field))
        arch_layout.addWidget(self.archive_field)
        arch_layout.addWidget(self.archive_btn)

        del_layout = QtWidgets.QHBoxLayout()
        self.deleted_field = QtWidgets.QLineEdit("deleted")
        self.deleted_btn = QtWidgets.QPushButton("Browse...")
        self.deleted_btn.clicked.connect(lambda: self._browse_directory(self.deleted_field))
        del_layout.addWidget(self.deleted_field)
        del_layout.addWidget(self.deleted_btn)

        archive_layout.addRow("Archive:", arch_layout)
        archive_layout.addRow("Deleted Items:", del_layout)

        main_layout.addWidget(archive_group)

        # --- Validation Warning Label ---
        self.validation_warning_label = QtWidgets.QLabel("")
        self.validation_warning_label.setStyleSheet("color: #cc4d4d; font-weight: bold;")
        self.validation_warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.validation_warning_label.setFixedHeight(20)
        main_layout.addWidget(self.validation_warning_label)

        # --- Bottom Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.accept_btn = QtWidgets.QPushButton("Accept")
        self.accept_btn.setProperty("styleClass", "acceptBtn")
        self.accept_btn.setMinimumHeight(35)
        self.accept_btn.clicked.connect(self.on_accept)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.accept_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        # --- Real-time Validation Connections ---
        self.proj_name_field.textEdited.connect(lambda t: self._validate_name_field(t, self.proj_name_field))
        self.master_name_field.textEdited.connect(lambda t: self._validate_name_field(t, self.master_name_field))
        self.wip_name_field.textEdited.connect(lambda t: self._validate_name_field(t, self.wip_name_field))

        self.asset_lib_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.asset_lib_field))
        self.scripts_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.scripts_field))
        self.shot_lib_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.shot_lib_field))
        self.textures_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.textures_field))
        self.renders_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.renders_field))
        self.particles_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.particles_field))
        self.archive_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.archive_field))
        self.deleted_field.textEdited.connect(lambda t: self._validate_folder_field(t, self.deleted_field))

    def _show_warning(self, message):
        self.validation_warning_label.setText(message)
        self._warning_timer.start(3500)  # Clear after 3.5 seconds

    def _clear_warning(self):
        self.validation_warning_label.setText("")

    def _validate_name_field(self, text, line_edit):
        """Validates strict naming fields, allowing only alphanumeric characters and underscores."""
        self._apply_validation(text, line_edit, r'[^a-zA-Z0-9_]')

    def _validate_folder_field(self, text, line_edit):
        """Validates folder names, converting backslashes to forward slashes."""
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
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Location")
        if dir_path:
            if append_proj_name:
                proj_name = self.proj_name_field.text().strip()
                if proj_name:
                    dir_path = os.path.join(dir_path, proj_name)
            line_edit.setText(dir_path.replace("\\", "/"))

    def _populate_from_maya(self):
        """Populates the dialog fields using the currently active Maya project workspaces."""
        try:
            import maya.cmds as cmds
            proj_dir = cmds.workspace(query=True, rootDirectory=True)
            if proj_dir:
                self.proj_path_field.setText(proj_dir.replace("\\", "/").rstrip("/"))
                
            scene_dir = cmds.workspace(fileRuleEntry="scene")
            if scene_dir:
                self.shot_lib_field.setText(scene_dir)
                self.asset_lib_field.setText(f"{scene_dir}/assets")
                
            images_dir = cmds.workspace(fileRuleEntry="images")
            if images_dir:
                self.renders_field.setText(f"{images_dir}/renders")
                
            source_images_dir = cmds.workspace(fileRuleEntry="sourceImages")
            if source_images_dir:
                self.textures_field.setText(source_images_dir)
                
            scripts_dir = cmds.workspace(fileRuleEntry="scripts")
            if scripts_dir:
                self.scripts_field.setText(scripts_dir)
                
            particles_dir = cmds.workspace(fileRuleEntry="particles")
            if particles_dir:
                self.particles_field.setText(particles_dir)
        except ImportError:
            pass

    def _toggle_custom_users(self, state):
        is_enabled = bool(state)
        self.custom_users_field.setEnabled(is_enabled)
        self.custom_users_btn.setEnabled(is_enabled)

    def _select_custom_users(self):
        """Native PySide implementation of the custom project users selection dialog."""
        users = opsProject.get_users()
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Set Project Users")
        dialog.setMinimumSize(300, 240)
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel("Select users to add to project:"))
        list_widget = QtWidgets.QListWidget()
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        list_widget.addItems(users)
        layout.addWidget(list_widget)

        # Select currently assigned users
        current_users = self.custom_users_field.text().split(",")
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
            self.custom_users_field.setText(",".join(selected))
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
        """Auto-populates the UI fields for new or existing projects."""
        
        date_str = opsInfo.get_date()
        self.creation_date_field.setText(date_str)
        self.deadline_field.setText(date_str)
        
        if self.mode == 1 and self.old_name:
            proj_xml = opsProject.get_single_project_xml(self.old_name)
            if proj_xml:
                self.proj_name_field.setText(opsUtils.get_xml_data(proj_xml, "name"))
                self.proj_path_field.setText(opsUtils.get_xml_data(proj_xml, "path"))
                self.desc_field.setText(opsUtils.get_xml_data(proj_xml, "description"))
                self.creation_date_field.setText(opsUtils.get_xml_data(proj_xml, "date"))
                self.deadline_field.setText(opsUtils.get_xml_data(proj_xml, "deadline"))
                
                self.asset_lib_field.setText(opsUtils.get_xml_data(proj_xml, "libraryfolder"))
                self.shot_lib_field.setText(opsUtils.get_xml_data(proj_xml, "scenesfolder"))
                self.archive_field.setText(opsUtils.get_xml_data(proj_xml, "archivefolder"))
                self.deleted_field.setText(opsUtils.get_xml_data(proj_xml, "deletedfolder"))
                self.renders_field.setText(opsUtils.get_xml_data(proj_xml, "rendersfolder"))
                self.particles_field.setText(opsUtils.get_xml_data(proj_xml, "particlesfolder"))
                self.textures_field.setText(opsUtils.get_xml_data(proj_xml, "texturesfolder"))
                self.scripts_field.setText(opsUtils.get_xml_data(proj_xml, "scriptsfolder"))
                
                self.master_name_field.setText(opsUtils.get_xml_data(proj_xml, "mastername"))
                self.master_format_combo.setCurrentText(opsUtils.get_xml_data(proj_xml, "masterformat"))
                self.wip_name_field.setText(opsUtils.get_xml_data(proj_xml, "wipname"))
                self.wip_format_combo.setCurrentText(opsUtils.get_xml_data(proj_xml, "wipformat"))
                
                # status: active=1, inactive=0. Option menu indexes: active=1, inactive=2.
                status = int(opsUtils.get_xml_data(proj_xml, "status") or 1)
                self.status_combo.setCurrentIndex(1 - status)
                
                user_mode = int(opsUtils.get_xml_data(proj_xml, "userMode") or 0)
                self.custom_users_chk.setChecked(bool(user_mode))
                
                curr_users = opsUtils.get_xml_data(proj_xml, "users")
                if curr_users:
                    global_users = opsProject.get_users()
                    valid_users = [u for u in curr_users.split(",") if u in global_users]
                    self.custom_users_field.setText(",".join(valid_users))
                else:
                    self.custom_users_field.setText("")
                    
                # Disable structural fields in edit mode to prevent path breakage
                self.asset_lib_field.setReadOnly(True)
                self.shot_lib_field.setReadOnly(True)
                self.master_name_field.setReadOnly(True)
                self.wip_name_field.setReadOnly(True)
                self.master_format_combo.setEnabled(False)
                self.wip_format_combo.setEnabled(False)
        else:
            self.custom_users_chk.setChecked(False)
            self.proj_name_field.clear()
            self.proj_path_field.clear()
            self.desc_field.clear()
            self.custom_users_field.clear()
            
            # Re-enable structural fields for new project mode
            self.asset_lib_field.setReadOnly(False)
            self.shot_lib_field.setReadOnly(False)
            self.master_name_field.setReadOnly(False)
            self.wip_name_field.setReadOnly(False)
            self.master_format_combo.setEnabled(True)
            self.wip_format_combo.setEnabled(True)

    # --- Button Callbacks ---

    def on_accept(self, *args):
        """Gathers data from the UI and passes it to the core opsActions module."""
        new_name = self.proj_name_field.text().strip()
        new_path = self.proj_path_field.text().strip()
        new_description = self.desc_field.text().strip()
        
        # OptionMenu: 1="active", 2="inactive". We want "1" for active, "0" for inactive.
        new_status = "1" if self.status_combo.currentIndex() == 0 else "0"
        
        new_date = self.creation_date_field.text().strip()
        new_deadline = self.deadline_field.text().strip()
        
        new_master_name = self.master_name_field.text().strip()
        new_master_format = self.master_format_combo.currentText().strip()
        
        new_wip_name = self.wip_name_field.text().strip()
        new_wip_format = self.wip_format_combo.currentText().strip()
        
        new_lib_loc = self.asset_lib_field.text().strip()
        new_shot_loc = self.shot_lib_field.text().strip()
        new_renders_loc = self.renders_field.text().strip()
        new_scripts_loc = self.scripts_field.text().strip()
        new_textures_loc = self.textures_field.text().strip()
        new_particles_loc = self.particles_field.text().strip()
        
        new_archive_loc = self.archive_field.text().strip()
        new_deleted_loc = self.deleted_field.text().strip()
        
        new_users = self.custom_users_field.text().strip()
        user_mode = "1" if self.custom_users_chk.isChecked() else "0"
        
        result = opsActions.create_or_edit_project(
            self.mode, self.old_name, new_name, new_path, new_description, new_status, new_date, new_deadline,
            new_master_name, new_master_format, new_wip_name, new_wip_format, new_lib_loc,
            new_shot_loc, new_renders_loc, new_scripts_loc, new_textures_loc, new_particles_loc,
            new_archive_loc, new_deleted_loc, new_users, user_mode
        )
        
        if result:
            self.close()
            opsUIWrappers.refresh_ui()
            if hasattr(self.UIObjects, 'opsProjectManagerGUI'):
                try: 
                    self.UIObjects.opsProjectManagerGUI.on_refresh_list()
                except: pass