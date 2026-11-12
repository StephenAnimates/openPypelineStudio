"""
Module: ops_proj_dialog_controller.py

Description:
    The Controller class for the openPypeline Studio Project Dialog.
    Handles logic, data population, and validation for creating or editing projects.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import re
from PySide6 import QtWidgets, QtCore

from . import ui_objects as UIObjects
from openpypeline.core import ops_project as opsProject
from openpypeline.core import ops_info as opsInfo
from openpypeline.app.maya.core import ops_utils as opsUtils
from openpypeline.core import ops_actions as opsActions
from openpypeline.app.maya.core import ops_ui_wrappers as opsUIWrappers
from openpypeline.core.models import ProjectConfig
from .ops_proj_dialog_gui import opsProjDialogGUI
from openpypeline.core.localization import localization

class OpsProjDialogController(QtCore.QObject):
    """Controls project-dialog behavior, validation, and project creation or editing."""

    def __init__(self):
        """Initialize the dialog view, state, timer, and signal connections."""
        super().__init__()
        # Keep access to other UI controllers for refreshing the project manager after saving
        self.UIObjects = UIObjects.UIObjects()
        
        # Create the dialog and initialize it in create mode with no prior project selected
        self.view = opsProjDialogGUI()
        self.mode = 0
        self.old_name = ""
        
        # Clear validation warnings once after their display delay; parent the timer to this controller.
        self._warning_timer = QtCore.QTimer(self)
        self._warning_timer.setSingleShot(True)
        self._warning_timer.timeout.connect(self._clear_warning)

        # Route user actions and field edits to their controller handlers.
        self._connect_signals()

    def showWindow(self):
        """Configures the dialog state based on mode and shows it."""
        # Set the title from the active create/edit mode before loading the form.
        if self.mode == 1:
            win_title = localization.get_string("win_editProject", "Edit Project: {0}")
            self.view.setWindowTitle(win_title.format(self.old_name))
        else:
            self.view.setWindowTitle(localization.get_string("win_createProject", "Create New Project"))
            
        # Load the appropriate defaults or existing project, then display the dialog.
        self._populate_fields()
        self.view.show()

    def _connect_signals(self):
        """Connect dialog controls to their handlers and live field validation."""
        # Connect browse and dialog buttons to their respective actions.
        self.view.path_browse_btn.clicked.connect(lambda: self._browse_directory(self.view.proj_path_field, append_proj_name=True))
        
        self.view.custom_users_chk.stateChanged.connect(self._toggle_custom_users)
        self.view.custom_users_btn.clicked.connect(self._select_custom_users)

        self.view.archive_btn.clicked.connect(lambda: self._browse_directory(self.view.archive_field))
        self.view.deleted_btn.clicked.connect(lambda: self._browse_directory(self.view.deleted_field))

        self.view.accept_btn.clicked.connect(self.on_accept)
        self.view.cancel_btn.clicked.connect(self.view.close)

        # Validate names and folder paths as the user edits them.
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
        """Displays a validation warning temporarily."""
        # Restarting the one-shot timer keeps each warning visible for the full delay.
        self.view.validation_warning_label.setText(message)
        self._warning_timer.start(3500)

    def _clear_warning(self):
        """Clears the validation warning label."""
        self.view.validation_warning_label.setText("")

    def _validate_name_field(self, text, line_edit):
        """Restricts a project or folder name to letters, digits, and underscores."""
        self._apply_validation(text, line_edit, r'[^a-zA-Z0-9_]')

    def _validate_folder_field(self, text, line_edit):
        """Normalizes and validates a folder path as it is entered."""
        if '\\' in text:
            text = text.replace('\\', '/')
            self._show_warning(localization.get_string("msg_warnBackslashes"))
        self._apply_validation(text, line_edit, r'[^a-zA-Z0-9_/]')
        
    def _apply_validation(self, text, line_edit, regex_pattern):
        """Normalizes invalid characters and spaces in a line-edit value."""
        original_text = text
        warning_msg = ""
        
        # Replace spaces first, then strip characters not allowed by this field's pattern.
        if ' ' in text:
            text = text.replace(' ', '_')
            warning_msg = localization.get_string("msg_warnSpaces")
            
        filtered_text = re.sub(regex_pattern, '', text)
        if filtered_text != text:
            text = filtered_text
            warning_msg = localization.get_string("msg_warnSpecialChars")
        
        if text != original_text:
            cursor_pos = line_edit.cursorPosition()
            diff = len(original_text) - len(text)
            # Prevent the programmatic correction from triggering textEdited again.
            line_edit.blockSignals(True)
            line_edit.setText(text)
            line_edit.blockSignals(False)
            # Keep the caret near its original position after removing characters.
            line_edit.setCursorPosition(max(0, cursor_pos - diff))
            self._show_warning(warning_msg)

    def _browse_directory(self, line_edit, append_proj_name=False):
        """Browse for a directory and optionally append the entered project name."""
        # Leave the current field unchanged if the user cancels the directory picker.
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self.view, localization.get_string("win_selectLocation"))
        if dir_path:
            # The project-root picker selects a parent folder, so append the project folder.
            if append_proj_name:
                proj_name = self.view.proj_name_field.text().strip()
                if proj_name:
                    dir_path = os.path.join(dir_path, proj_name)
            line_edit.setText(dir_path.replace("\\", "/"))

    def _populate_from_maya(self):
        """Populate project and folder fields from the current Maya workspace."""
        try:
            import maya.cmds as cmds
            # Seed the dialog from Maya's active workspace; artists can adjust these values.
            proj_dir = cmds.workspace(query=True, rootDirectory=True)
            if proj_dir:
                clean_dir = proj_dir.replace("\\", "/").rstrip("/")
                self.view.proj_path_field.setText(clean_dir)
                
                # Extract the folder name to use as the Project Name
                proj_name = os.path.basename(clean_dir)
                if proj_name:
                    self.view.proj_name_field.setText(proj_name)

            # Map Maya workspace rules to the corresponding project dialog locations.
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
            # The dialog can be imported outside Maya, where workspace defaults are unavailable.
            pass

    def _toggle_custom_users(self, state):
        """Enable or disable the custom project-users controls."""
        # Keep the text field and picker button in sync with the checkbox.
        is_enabled = bool(state)
        self.view.custom_users_field.setEnabled(is_enabled)
        self.view.custom_users_btn.setEnabled(is_enabled)

    def _select_custom_users(self):
        """Show a dialog for selecting users assigned to the project."""
        # Build the picker from configured global users and preselect current assignments.
        users = opsProject.get_users()
        dialog = QtWidgets.QDialog(self.view)
        dialog.setWindowTitle(localization.get_string("win_setProjectUsers"))
        dialog.setMinimumSize(300, 240)
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_selectUsersToAdd")))
        list_widget = QtWidgets.QListWidget()
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        list_widget.addItems(users)
        layout.addWidget(list_widget)

        current_users = self.view.custom_users_field.text().split(",")
        # Restore the current selection so opening the picker does not clear existing choices.
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() in current_users:
                item.setSelected(True)

        btn_layout = QtWidgets.QHBoxLayout()
        # Provide actions to apply the selection, edit global users, or cancel.
        set_btn = QtWidgets.QPushButton(localization.get_string("btn_setUsers"))
        edit_btn = QtWidgets.QPushButton(localization.get_string("btn_editGlobalUsers"))
        cancel_btn = QtWidgets.QPushButton(localization.get_string("btn_cancel"))

        def on_set():
            """Apply the selected users and close the selection dialog."""
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
        """Populate the dialog with defaults or the selected project's settings."""
        # New projects start with today's date for both date fields.
        date_str = opsInfo.get_date()
        self.view.creation_date_field.setText(date_str)
        self.view.deadline_field.setText(date_str)
        
        if self.mode == 1 and self.old_name:
            # Load the selected project's saved values when editing.
            proj = opsProject.get_project(self.old_name)
            if proj:
                self.view.proj_name_field.setText(proj.get("name", ""))
                self.view.proj_path_field.setText(proj.get("path", ""))
                self.view.desc_field.setText(proj.get("description", ""))
                self.view.creation_date_field.setText(proj.get("date", ""))
                self.view.deadline_field.setText(proj.get("deadline", ""))
                
                self.view.asset_lib_field.setText(proj.get("libraryfolder", ""))
                self.view.shot_lib_field.setText(proj.get("scenesfolder", ""))
                self.view.archive_field.setText(proj.get("archivefolder", ""))
                self.view.deleted_field.setText(proj.get("deletedfolder", ""))
                self.view.renders_field.setText(proj.get("rendersfolder", ""))
                self.view.particles_field.setText(proj.get("particlesfolder", ""))
                self.view.textures_field.setText(proj.get("texturesfolder", ""))
                self.view.scripts_field.setText(proj.get("scriptsfolder", ""))
                
                self.view.master_name_field.setText(proj.get("mastername", ""))
                self.view.master_format_combo.setCurrentText(proj.get("masterformat", ""))
                self.view.wip_name_field.setText(proj.get("wipname", ""))
                self.view.wip_format_combo.setCurrentText(proj.get("wipformat", ""))
                
                status = int(proj.get("status") or 1)
                # The combo presents active/inactive in the opposite order of stored status.
                self.view.status_combo.setCurrentIndex(1 - status)
                
                user_mode = int(proj.get("userMode") or 0)
                self.view.custom_users_chk.setChecked(bool(user_mode))
                
                curr_users = proj.get("users", "")
                if curr_users:
                    global_users = opsProject.get_users()
                    # Ignore assignments for users no longer present in the global user list.
                    valid_users = [u for u in curr_users.split(",") if u in global_users]
                    self.view.custom_users_field.setText(",".join(valid_users))
                else:
                    self.view.custom_users_field.setText("")
                    
                # Preserve structural settings for an existing project.
                self.view.asset_lib_field.setReadOnly(True)
                self.view.shot_lib_field.setReadOnly(True)
                self.view.master_name_field.setReadOnly(True)
                self.view.wip_name_field.setReadOnly(True)
                self.view.master_format_combo.setEnabled(False)
                self.view.wip_format_combo.setEnabled(False)
        else:
            # Reset project-specific fields before applying current Maya workspace defaults.
            self.view.custom_users_chk.setChecked(False)
            self.view.proj_name_field.clear()
            self.view.proj_path_field.clear()
            self.view.desc_field.clear()
            self.view.custom_users_field.clear()
            
            # Auto-populate from current Maya project
            self._populate_from_maya()
            
            self.view.asset_lib_field.setReadOnly(False)
            self.view.shot_lib_field.setReadOnly(False)
            self.view.master_name_field.setReadOnly(False)
            self.view.wip_name_field.setReadOnly(False)
            self.view.master_format_combo.setEnabled(True)
            self.view.wip_format_combo.setEnabled(True)

    def on_accept(self, *args):
        """Create or update the project using the values entered in the dialog."""
        # Read and trim all user-entered values before building the persistence model.
        new_name = self.view.proj_name_field.text().strip()
        new_path = self.view.proj_path_field.text().strip()
        new_description = self.view.desc_field.text().strip()
        # Convert the active-first combo index back to the project's stored status value.
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
        
        # Package the form values in the shared project model expected by core actions.
        config = ProjectConfig(
            name=new_name,
            path=new_path,
            description=new_description,
            status=new_status,
            date=new_date,
            deadline=new_deadline,
            mastername=new_master_name,
            masterformat=new_master_format,
            wipname=new_wip_name,
            wipformat=new_wip_format,
            libraryfolder=new_lib_loc,
            scenesfolder=new_shot_loc,
            rendersfolder=new_renders_loc,
            scriptsfolder=new_scripts_loc,
            texturesfolder=new_textures_loc,
            particlesfolder=new_particles_loc,
            archivefolder=new_archive_loc,
            deletedfolder=new_deleted_loc,
            users=new_users,
            userMode=user_mode
        )
        
        # Save through the shared action layer; refresh the UI only after success.
        result = opsActions.create_or_edit_project(self.mode, self.old_name, config)
        
        if result:
            self.view.close()
            opsUIWrappers.refresh_ui()
            # The project manager controller is present only when that UI is currently open.
            if hasattr(self.UIObjects, 'opsProjectManagerController'):
                try: 
                    self.UIObjects.opsProjectManagerController.on_refresh_list()
                except: pass