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
        
        self.setWindowTitle("Create New Project")
        self.setObjectName("openPypelineProjDialog")
        self.setMinimumSize(450, 650)
        self.setWindowFlags(QtCore.Qt.Window)

        self._build_ui()

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
        
        self.maya_proj_btn = QtWidgets.QPushButton("Use Maya Project")
        
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
        self.master_format_combo.addItems(["ma", "mb", "usd", "usda", "abc", "fbx"])
        files_layout.addWidget(self.master_format_combo, 0, 3)

        files_layout.addWidget(QtWidgets.QLabel("WIP Name:"), 1, 0)
        self.wip_name_field = QtWidgets.QLineEdit("wip")
        files_layout.addWidget(self.wip_name_field, 1, 1)

        files_layout.addWidget(QtWidgets.QLabel("Format:"), 1, 2)
        self.wip_format_combo = QtWidgets.QComboBox()
        self.wip_format_combo.addItems(["ma", "mb", "usd", "usda", "abc", "fbx"])
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
        arch_layout.addWidget(self.archive_field)
        arch_layout.addWidget(self.archive_btn)

        del_layout = QtWidgets.QHBoxLayout()
        self.deleted_field = QtWidgets.QLineEdit("deleted")
        self.deleted_btn = QtWidgets.QPushButton("Browse...")
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

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(35)

        btn_layout.addWidget(self.accept_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)