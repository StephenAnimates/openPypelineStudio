"""
Module: opsSettingsGUI.py

Description:
    Global Preferences and Settings UI for openPypeline Studio.
    Allows users to customize localization and pipeline defaults.
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

class opsSettingsGUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    A Maya window class for managing global openPypeline Studio settings.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.setWindowTitle("Global Settings")
        self.setObjectName("opsSettingsGUI")
        self.setMinimumSize(400, 450)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self._build_ui()
        
    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Localization Section ---
        loc_group = QtWidgets.QGroupBox("Localization & Display")
        loc_layout = QtWidgets.QFormLayout(loc_group)
        
        self.date_format_combo = QtWidgets.QComboBox()
        self.date_format_combo.addItems(["MM/DD/YYYY (US)", "DD/MM/YYYY (EU/UK)", "YYYY-MM-DD (ISO)"])
        
        self.time_format_combo = QtWidgets.QComboBox()
        self.time_format_combo.addItems(["12-Hour (AM/PM)", "24-Hour"])
        
        loc_layout.addRow("Date Format:", self.date_format_combo)
        loc_layout.addRow("Time Format:", self.time_format_combo)
        main_layout.addWidget(loc_group)

        # --- Pipeline Defaults Section ---
        pipe_group = QtWidgets.QGroupBox("Pipeline Defaults")
        pipe_layout = QtWidgets.QFormLayout(pipe_group)
        
        self.wip_name_field = QtWidgets.QLineEdit()
        self.master_name_field = QtWidgets.QLineEdit()
        
        self.file_format_combo = QtWidgets.QComboBox()
        self.file_format_combo.addItems(["ma", "mb", "usd", "usda", "abc", "fbx"])
        
        pipe_layout.addRow("Default WIP Name:", self.wip_name_field)
        pipe_layout.addRow("Default Master Name:", self.master_name_field)
        pipe_layout.addRow("Default File Format:", self.file_format_combo)
        main_layout.addWidget(pipe_group)

        # --- Tracker Settings Section ---
        tracker_group = QtWidgets.QGroupBox("Production Tracking")
        tracker_layout = QtWidgets.QFormLayout(tracker_group)
        
        self.tracker_type_combo = QtWidgets.QComboBox()
        self.tracker_type_combo.addItems(["none", "shotgrid"])
        
        self.tracker_url_field = QtWidgets.QLineEdit()
        self.tracker_user_field = QtWidgets.QLineEdit()
        self.tracker_key_field = QtWidgets.QLineEdit()
        self.tracker_key_field.setEchoMode(QtWidgets.QLineEdit.Password)
        
        tracker_layout.addRow("Tracker Type:", self.tracker_type_combo)
        tracker_layout.addRow("Tracker URL:", self.tracker_url_field)
        tracker_layout.addRow("Auth User:", self.tracker_user_field)
        tracker_layout.addRow("Auth Key:", self.tracker_key_field)
        main_layout.addWidget(tracker_group)

        # --- Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)