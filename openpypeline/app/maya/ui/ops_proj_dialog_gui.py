"""
Module: ops_proj_dialog_gui.py

Description:
    Opens the Project Dialog Window. This is used either for creating a new project 
    or editing an existing project using PySide6.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from openpypeline.core.localization import localization

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
        
        self.setWindowTitle(localization.get_string("win_createProject"))
        self.setObjectName("openPypelineProjDialog")
        self.setMinimumSize(450, 650)
        self.setWindowFlags(QtCore.Qt.Window)

        self._build_ui()

    def _build_ui(self):
        """Constructs the UI using PySide widgets and layouts."""
        self.setStyleSheet(OPS_PROJ_DIALOG_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)

        # --- Project Settings Group ---
        settings_group = QtWidgets.QGroupBox(localization.get_string("grp_projectSettings"))
        settings_layout = QtWidgets.QFormLayout(settings_group)

        self.proj_name_field = QtWidgets.QLineEdit()
        self.proj_name_field.setMaxLength(22)
        self.proj_name_field.setToolTip(localization.get_string("anno_projName"))

        path_layout = QtWidgets.QHBoxLayout()
        self.proj_path_field = QtWidgets.QLineEdit()
        self.proj_path_field.setReadOnly(True)
        self.proj_path_field.setToolTip(localization.get_string("anno_projPath"))
        self.path_override_btn = QtWidgets.QPushButton(localization.get_string("btn_overrideProjectPath"))
        
        path_layout.addWidget(self.proj_path_field)
        path_layout.addWidget(self.path_override_btn)

        self.desc_field = QtWidgets.QLineEdit()
        self.desc_field.setMaxLength(250)
        self.desc_field.setToolTip(localization.get_string("anno_projDesc"))

        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["active", "inactive"])
        self.status_combo.setToolTip(localization.get_string("anno_projStatus"))

        settings_layout.addRow(localization.get_string("lbl_projectName"), self.proj_name_field)
        settings_layout.addRow(localization.get_string("lbl_projectPath"), path_layout)
        settings_layout.addRow(localization.get_string("lbl_description"), self.desc_field)
        settings_layout.addRow(localization.get_string("lbl_status"), self.status_combo)

        main_layout.addWidget(settings_group)

        # --- Users & Dates Group ---
        users_dates_group = QtWidgets.QGroupBox(localization.get_string("grp_usersDates"))
        users_dates_layout = QtWidgets.QFormLayout(users_dates_group)

        self.custom_users_chk = QtWidgets.QCheckBox(localization.get_string("chk_enableCustomUsers"))
        self.custom_users_chk.setToolTip(localization.get_string("anno_customUsers"))

        users_layout = QtWidgets.QHBoxLayout()
        self.custom_users_field = QtWidgets.QLineEdit()
        self.custom_users_field.setReadOnly(True)
        self.custom_users_field.setEnabled(False)
        self.custom_users_btn = QtWidgets.QPushButton("...")
        self.custom_users_btn.setEnabled(False)
        users_layout.addWidget(self.custom_users_field)
        users_layout.addWidget(self.custom_users_btn)

        self.creation_date_field = QtWidgets.QLineEdit("dd/mm/year")
        self.deadline_field = QtWidgets.QLineEdit("dd/mm/year")

        users_dates_layout.addRow("", self.custom_users_chk)
        users_dates_layout.addRow(localization.get_string("lbl_users"), users_layout)
        users_dates_layout.addRow(localization.get_string("lbl_creationDate"), self.creation_date_field)
        users_dates_layout.addRow(localization.get_string("lbl_deadline"), self.deadline_field)

        main_layout.addWidget(users_dates_group)

        # --- Files Group ---
        files_group = QtWidgets.QGroupBox(localization.get_string("grp_filesMasterWip"))
        files_layout = QtWidgets.QGridLayout(files_group)
        files_group.setToolTip(localization.get_string("anno_masterName"))

        files_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_masterName")), 0, 0)
        self.master_name_field = QtWidgets.QLineEdit("master")
        self.master_name_field.setToolTip(localization.get_string("anno_masterName"))
        files_layout.addWidget(self.master_name_field, 0, 1)

        files_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_format")), 0, 2)
        self.master_format_combo = QtWidgets.QComboBox()
        self.master_format_combo.addItems(["ma", "mb", "usd", "usda", "abc", "fbx"])
        files_layout.addWidget(self.master_format_combo, 0, 3)

        files_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_wipName")), 1, 0)
        self.wip_name_field = QtWidgets.QLineEdit("wip")
        self.wip_name_field.setToolTip(localization.get_string("anno_wipName"))
        files_layout.addWidget(self.wip_name_field, 1, 1)

        files_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_format")), 1, 2)
        self.wip_format_combo = QtWidgets.QComboBox()
        self.wip_format_combo.addItems(["ma", "mb", "usd", "usda", "abc", "fbx"])
        files_layout.addWidget(self.wip_format_combo, 1, 3)

        main_layout.addWidget(files_group)

        # --- Sub-Folders Group ---
        subfolders_group = QtWidgets.QGroupBox(localization.get_string("grp_subfolders"))
        subfolders_layout = QtWidgets.QGridLayout(subfolders_group)
        subfolders_group.setToolTip(localization.get_string("anno_subfolders"))

        self.asset_lib_field = QtWidgets.QLineEdit("scenes/assets")
        self.scripts_field = QtWidgets.QLineEdit("scripts")
        self.shot_lib_field = QtWidgets.QLineEdit("scenes")
        self.textures_field = QtWidgets.QLineEdit("sourceimages")
        self.renders_field = QtWidgets.QLineEdit("images/renders")
        self.particles_field = QtWidgets.QLineEdit("particles")

        subfolders_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_assetLibrary")), 0, 0)
        subfolders_layout.addWidget(self.asset_lib_field, 0, 1)
        subfolders_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_scripts")), 0, 2)
        subfolders_layout.addWidget(self.scripts_field, 0, 3)

        subfolders_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_shotLibrary")), 1, 0)
        subfolders_layout.addWidget(self.shot_lib_field, 1, 1)
        subfolders_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_textures")), 1, 2)
        subfolders_layout.addWidget(self.textures_field, 1, 3)

        subfolders_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_renders")), 2, 0)
        subfolders_layout.addWidget(self.renders_field, 2, 1)
        subfolders_layout.addWidget(QtWidgets.QLabel(localization.get_string("lbl_particles")), 2, 2)
        subfolders_layout.addWidget(self.particles_field, 2, 3)

        main_layout.addWidget(subfolders_group)

        # --- Archive / Deleted Group ---
        archive_group = QtWidgets.QGroupBox(localization.get_string("grp_archiveDeleted"))
        archive_layout = QtWidgets.QFormLayout(archive_group)

        arch_layout = QtWidgets.QHBoxLayout()
        self.archive_field = QtWidgets.QLineEdit("archive")
        self.archive_btn = QtWidgets.QPushButton(localization.get_string("btn_browse"))
        arch_layout.addWidget(self.archive_field)
        arch_layout.addWidget(self.archive_btn)

        del_layout = QtWidgets.QHBoxLayout()
        self.deleted_field = QtWidgets.QLineEdit("deleted")
        self.deleted_btn = QtWidgets.QPushButton(localization.get_string("btn_browse"))
        del_layout.addWidget(self.deleted_field)
        del_layout.addWidget(self.deleted_btn)

        archive_layout.addRow(localization.get_string("lbl_archive"), arch_layout)
        archive_layout.addRow(localization.get_string("lbl_deletedItems"), del_layout)

        main_layout.addWidget(archive_group)

        # --- Validation Warning Label ---
        self.validation_warning_label = QtWidgets.QLabel("")
        self.validation_warning_label.setStyleSheet("color: #cc4d4d; font-weight: bold;")
        self.validation_warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.validation_warning_label.setFixedHeight(20)
        main_layout.addWidget(self.validation_warning_label)

        # --- Bottom Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.accept_btn = QtWidgets.QPushButton(localization.get_string("btn_accept"))
        self.accept_btn.setProperty("styleClass", "acceptBtn")
        self.accept_btn.setMinimumHeight(35)

        self.cancel_btn = QtWidgets.QPushButton(localization.get_string("btn_cancel"))
        self.cancel_btn.setMinimumHeight(35)

        btn_layout.addWidget(self.accept_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)