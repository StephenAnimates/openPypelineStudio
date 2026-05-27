"""
Module: opsSettingsGUI.py

Description:
    Global Preferences and Settings UI for openPypeline Studio.
    Allows users to customize localization and pipeline defaults.
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
import UIObjects
from openpypeline.core.util import prefs

class opsSettingsGUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    A Maya window class for managing global openPypeline Studio settings.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.UIObjects = UIObjects.UIObjects()
        
        self.setWindowTitle("Global Settings")
        self.setObjectName("opsSettingsGUI")
        self.setMinimumSize(400, 450)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self._build_ui()
        self._populate_fields()
        
    def showWindow(self):
        self.show()

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
        self.file_format_combo.addItems(["ma", "mb", "usd", "usda", "abc"])
        
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
        self.save_btn.clicked.connect(self.on_save)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

    def _populate_fields(self):
        date_fmt = prefs.get_pref("ops_dateFormat", "%m/%d/%Y")
        if date_fmt == "%d/%m/%Y": self.date_format_combo.setCurrentIndex(1)
        elif date_fmt == "%Y-%m-%d": self.date_format_combo.setCurrentIndex(2)
        else: self.date_format_combo.setCurrentIndex(0)
        
        time_fmt = prefs.get_pref("ops_timeFormat", "%I:%M:%S %p")
        if time_fmt == "%I:%M:%S %p": self.time_format_combo.setCurrentIndex(0)
        else: self.time_format_combo.setCurrentIndex(1)
        
        w_name = prefs.get_pref("ops_wip", "wip")
        m_name = prefs.get_pref("ops_masterName", "master")
        self.wip_name_field.setText(w_name)
        self.master_name_field.setText(m_name)
        
        f_fmt = prefs.get_pref("ops_wipFormat", "ma")
        if f_fmt == "abc": self.file_format_combo.setCurrentIndex(4)
        elif f_fmt == "usda": self.file_format_combo.setCurrentIndex(3)
        elif f_fmt == "usd": self.file_format_combo.setCurrentIndex(2)
        elif f_fmt == "mb": self.file_format_combo.setCurrentIndex(1)
        else: self.file_format_combo.setCurrentIndex(0)

        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "shotgrid": self.tracker_type_combo.setCurrentIndex(1)
        else: self.tracker_type_combo.setCurrentIndex(0)
        
        self.tracker_url_field.setText(prefs.get_pref("ops_tracker_url", ""))
        self.tracker_user_field.setText(prefs.get_pref("ops_tracker_user", ""))
        self.tracker_key_field.setText(prefs.get_pref("ops_tracker_key", ""))

    def on_save(self, *args):
        date_idx = self.date_format_combo.currentIndex()
        if date_idx == 1: prefs.set_pref("ops_dateFormat", "%d/%m/%Y")
        elif date_idx == 2: prefs.set_pref("ops_dateFormat", "%Y-%m-%d")
        else: prefs.set_pref("ops_dateFormat", "%m/%d/%Y")
        
        time_idx = self.time_format_combo.currentIndex()
        if time_idx == 0: prefs.set_pref("ops_timeFormat", "%I:%M:%S %p")
        else: prefs.set_pref("ops_timeFormat", "%H:%M:%S")
        
        w_name = self.wip_name_field.text().strip()
        m_name = self.master_name_field.text().strip()
        
        if w_name: prefs.set_pref("ops_wip", w_name)
        if m_name: prefs.set_pref("ops_masterName", m_name)
        
        fmt_idx = self.file_format_combo.currentIndex()
        fmt_map = {0: "ma", 1: "mb", 2: "usd", 3: "usda", 4: "abc"}
        fmt = fmt_map.get(fmt_idx, "ma")
        prefs.set_pref("ops_wipFormat", fmt)
        prefs.set_pref("ops_masterFormat", fmt)
        
        t_type = "shotgrid" if self.tracker_type_combo.currentIndex() == 1 else "none"
        prefs.set_pref("ops_tracker_type", t_type)
        prefs.set_pref("ops_tracker_url", self.tracker_url_field.text().strip())
        prefs.set_pref("ops_tracker_user", self.tracker_user_field.text().strip())
        prefs.set_pref("ops_tracker_key", self.tracker_key_field.text().strip())
        
        self.close()
        import opsUIWrappers
        opsUIWrappers.refresh_ui()