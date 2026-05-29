"""
Module: opsSettingsController.py

Description:
    The Controller class for the openPypeline Studio Global Settings Dialog.
    Handles logic for populating and saving global preferences.
"""

from PySide6 import QtCore
import UIObjects
import opsUIWrappers
from openpypeline.core.util import prefs
from openpypeline.app.maya.ui.opsSettingsGUI import opsSettingsGUI

class OpsSettingsController(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.UIObjects = UIObjects.UIObjects()
        self.view = opsSettingsGUI()
        
        self._connect_signals()
        self._populate_fields()

    def showWindow(self):
        self.view.show()

    def _connect_signals(self):
        self.view.save_btn.clicked.connect(self.on_save)
        self.view.cancel_btn.clicked.connect(self.view.close)

    def _populate_fields(self):
        date_fmt = prefs.get_pref("ops_dateFormat", "%m/%d/%Y")
        if date_fmt == "%d/%m/%Y": self.view.date_format_combo.setCurrentIndex(1)
        elif date_fmt == "%Y-%m-%d": self.view.date_format_combo.setCurrentIndex(2)
        else: self.view.date_format_combo.setCurrentIndex(0)
        
        time_fmt = prefs.get_pref("ops_timeFormat", "%I:%M:%S %p")
        if time_fmt == "%I:%M:%S %p": self.view.time_format_combo.setCurrentIndex(0)
        else: self.view.time_format_combo.setCurrentIndex(1)
        
        w_name = prefs.get_pref("ops_wip", "wip")
        m_name = prefs.get_pref("ops_masterName", "master")
        self.view.wip_name_field.setText(w_name)
        self.view.master_name_field.setText(m_name)
        
        f_fmt = prefs.get_pref("ops_wipFormat", "ma")
        if f_fmt == "fbx": self.view.file_format_combo.setCurrentIndex(5)
        elif f_fmt == "abc": self.view.file_format_combo.setCurrentIndex(4)
        elif f_fmt == "usda": self.view.file_format_combo.setCurrentIndex(3)
        elif f_fmt == "usd": self.view.file_format_combo.setCurrentIndex(2)
        elif f_fmt == "mb": self.view.file_format_combo.setCurrentIndex(1)
        else: self.view.file_format_combo.setCurrentIndex(0)

        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "shotgrid": self.view.tracker_type_combo.setCurrentIndex(1)
        else: self.view.tracker_type_combo.setCurrentIndex(0)
        
        self.view.tracker_url_field.setText(prefs.get_pref("ops_tracker_url", ""))
        self.view.tracker_user_field.setText(prefs.get_pref("ops_tracker_user", ""))
        self.view.tracker_key_field.setText(prefs.get_pref("ops_tracker_key", ""))

    def on_save(self, *args):
        date_idx = self.view.date_format_combo.currentIndex()
        if date_idx == 1: prefs.set_pref("ops_dateFormat", "%d/%m/%Y")
        elif date_idx == 2: prefs.set_pref("ops_dateFormat", "%Y-%m-%d")
        else: prefs.set_pref("ops_dateFormat", "%m/%d/%Y")
        
        time_idx = self.view.time_format_combo.currentIndex()
        if time_idx == 0: prefs.set_pref("ops_timeFormat", "%I:%M:%S %p")
        else: prefs.set_pref("ops_timeFormat", "%H:%M:%S")
        
        w_name = self.view.wip_name_field.text().strip()
        m_name = self.view.master_name_field.text().strip()
        
        if w_name: prefs.set_pref("ops_wip", w_name)
        if m_name: prefs.set_pref("ops_masterName", m_name)
        
        fmt_idx = self.view.file_format_combo.currentIndex()
        fmt_map = {0: "ma", 1: "mb", 2: "usd", 3: "usda", 4: "abc", 5: "fbx"}
        fmt = fmt_map.get(fmt_idx, "ma")
        prefs.set_pref("ops_wipFormat", fmt)
        prefs.set_pref("ops_masterFormat", fmt)
        
        t_type = "shotgrid" if self.view.tracker_type_combo.currentIndex() == 1 else "none"
        prefs.set_pref("ops_tracker_type", t_type)
        prefs.set_pref("ops_tracker_url", self.view.tracker_url_field.text().strip())
        prefs.set_pref("ops_tracker_user", self.view.tracker_user_field.text().strip())
        prefs.set_pref("ops_tracker_key", self.view.tracker_key_field.text().strip())
        
        self.view.close()
        opsUIWrappers.refresh_ui()