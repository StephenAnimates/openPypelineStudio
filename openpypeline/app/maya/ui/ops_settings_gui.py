"""
Module: ops_settings_gui.py

Description:
    Global Preferences and Settings UI for openPypeline Studio.
    Allows users to customize localization and pipeline defaults.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from openpypeline.core.localization import localization

class opsSettingsGUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    A Maya window class for managing global openPypeline Studio settings.
    """

    def __init__(self, parent=None):
        """Initialize the settings dialog and build its preference controls."""
        super().__init__(parent=parent)
        
        self.setWindowTitle(localization.get_string("win_globalSettings"))
        self.setObjectName("opsSettingsGUI")
        self.setMinimumSize(400, 450)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self._build_ui()
        
    def _build_ui(self):
        """Lay out controls for localization, pipeline defaults, and tracking."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Localization Section ---
        loc_group = QtWidgets.QGroupBox(localization.get_string("grp_localizationDisplay"))
        loc_layout = QtWidgets.QFormLayout(loc_group)
        
        self.date_format_combo = QtWidgets.QComboBox()
        self.date_format_combo.addItems([localization.get_string("fmt_dateUS"), localization.get_string("fmt_dateEU"), localization.get_string("fmt_dateISO")])
        
        self.time_format_combo = QtWidgets.QComboBox()
        self.time_format_combo.addItems([localization.get_string("fmt_time12"), localization.get_string("fmt_time24")])
        
        loc_layout.addRow(localization.get_string("lbl_dateFormat"), self.date_format_combo)
        loc_layout.addRow(localization.get_string("lbl_timeFormat"), self.time_format_combo)
        main_layout.addWidget(loc_group)

        # --- Pipeline Defaults Section ---
        pipe_group = QtWidgets.QGroupBox(localization.get_string("grp_pipelineDefaults"))
        pipe_layout = QtWidgets.QFormLayout(pipe_group)
        
        self.wip_name_field = QtWidgets.QLineEdit()
        self.master_name_field = QtWidgets.QLineEdit()
        
        self.file_format_combo = QtWidgets.QComboBox()
        self.file_format_combo.addItems(["ma", "mb", "usd", "usda", "abc", "fbx"])
        
        pipe_layout.addRow(localization.get_string("lbl_defaultWipName"), self.wip_name_field)
        pipe_layout.addRow(localization.get_string("lbl_defaultMasterName"), self.master_name_field)
        pipe_layout.addRow(localization.get_string("lbl_defaultFileFormat"), self.file_format_combo)
        main_layout.addWidget(pipe_group)

        # --- Tracker Settings Section ---
        tracker_group = QtWidgets.QGroupBox(localization.get_string("grp_productionTracking"))
        tracker_layout = QtWidgets.QFormLayout(tracker_group)
        
        self.tracker_type_combo = QtWidgets.QComboBox()
        self.tracker_type_combo.addItems([localization.get_string("opt_none"), localization.get_string("opt_shotgrid")])
        
        self.tracker_url_field = QtWidgets.QLineEdit()
        self.tracker_user_field = QtWidgets.QLineEdit()
        self.tracker_key_field = QtWidgets.QLineEdit()
        self.tracker_key_field.setEchoMode(QtWidgets.QLineEdit.Password)
        
        tracker_layout.addRow(localization.get_string("lbl_trackerType"), self.tracker_type_combo)
        tracker_layout.addRow(localization.get_string("lbl_trackerUrl"), self.tracker_url_field)
        tracker_layout.addRow(localization.get_string("lbl_authUser"), self.tracker_user_field)
        tracker_layout.addRow(localization.get_string("lbl_authKey"), self.tracker_key_field)
        main_layout.addWidget(tracker_group)

        # --- Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton(localization.get_string("btn_save"))
        self.cancel_btn = QtWidgets.QPushButton(localization.get_string("btn_cancel"))
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)