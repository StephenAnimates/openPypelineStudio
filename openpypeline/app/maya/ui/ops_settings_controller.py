"""Controller class for the openPypeline Studio Global Settings dialog.

Mediates between the :class:`~openpypeline.app.maya.ui.ops_settings_gui.opsSettingsGUI`
view and the persistent :mod:`~openpypeline.core.util.prefs` backend,
populating controls on initialization and persisting date/time formats,
pipeline naming defaults, file formats, and tracker credentials on save.

:File: ops_settings_controller.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Any

from PySide6 import QtCore

from openpypeline.core.util import prefs
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers
from openpypeline.ui import ui_objects

from .ops_settings_gui import opsSettingsGUI


class OpsSettingsController(QtCore.QObject):
    """Coordinate preference fields in the global settings dialog.

    Instantiates :class:`~openpypeline.app.maya.ui.ops_settings_gui.opsSettingsGUI`,
    hydrates its widgets from :mod:`~openpypeline.core.util.prefs`, and writes
    updated settings back on confirmation.

    :ivar UIObjects: Shared :class:`~openpypeline.ui.ui_objects.WindowManager`
        singleton reference.
    :vartype UIObjects: openpypeline.ui.ui_objects.WindowManager
    :ivar view: Settings window widget managed by this controller.
    :vartype view: openpypeline.app.maya.ui.ops_settings_gui.opsSettingsGUI
    """

    def __init__(self) -> None:
        """Create the settings view and load its current preference values."""
        super().__init__()
        self.UIObjects = ui_objects.UIObjects()
        self.view = opsSettingsGUI()

        self._connect_signals()
        self._populate_fields()

    def showWindow(self) -> None:
        """Display the settings window."""
        self.view.show()

    def _connect_signals(self) -> None:
        """Connect save and cancel controls to their actions."""
        self.view.save_btn.clicked.connect(self.on_save)
        self.view.cancel_btn.clicked.connect(self.view.close)

    def _populate_fields(self) -> None:
        """Populate each settings control from the stored user preferences."""
        date_fmt = prefs.get_pref("ops_dateFormat", "%m/%d/%Y")
        if date_fmt == "%d/%m/%Y":
            self.view.date_format_combo.setCurrentIndex(1)
        elif date_fmt == "%Y-%m-%d":
            self.view.date_format_combo.setCurrentIndex(2)
        else:
            self.view.date_format_combo.setCurrentIndex(0)

        time_fmt = prefs.get_pref("ops_timeFormat", "%I:%M:%S %p")
        if time_fmt == "%I:%M:%S %p":
            self.view.time_format_combo.setCurrentIndex(0)
        else:
            self.view.time_format_combo.setCurrentIndex(1)

        w_name = prefs.get_pref("ops_wip", "wip")
        m_name = prefs.get_pref("ops_masterName", "master")
        self.view.wip_name_field.setText(w_name)
        self.view.master_name_field.setText(m_name)

        f_fmt = prefs.get_pref("ops_wipFormat", "ma")
        if f_fmt == "fbx":
            self.view.file_format_combo.setCurrentIndex(5)
        elif f_fmt == "abc":
            self.view.file_format_combo.setCurrentIndex(4)
        elif f_fmt == "usda":
            self.view.file_format_combo.setCurrentIndex(3)
        elif f_fmt == "usd":
            self.view.file_format_combo.setCurrentIndex(2)
        elif f_fmt == "mb":
            self.view.file_format_combo.setCurrentIndex(1)
        else:
            self.view.file_format_combo.setCurrentIndex(0)

        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "shotgrid":
            self.view.tracker_type_combo.setCurrentIndex(1)
        else:
            self.view.tracker_type_combo.setCurrentIndex(0)

        self.view.tracker_url_field.setText(prefs.get_pref("ops_tracker_url", ""))
        self.view.tracker_user_field.setText(prefs.get_pref("ops_tracker_user", ""))
        self.view.tracker_key_field.setText(prefs.get_pref("ops_tracker_key", ""))

    def on_save(self, *args: Any) -> None:
        """Persist the selected settings and refresh the main UI.

        Writes updated localization, naming, format, and tracker settings via
        :func:`~openpypeline.core.util.prefs.set_pref`, closes :attr:`view`,
        and calls :func:`~openpypeline.ui.ops_ui_wrappers.refresh_ui`.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        date_idx = self.view.date_format_combo.currentIndex()
        if date_idx == 1:
            prefs.set_pref("ops_dateFormat", "%d/%m/%Y")
        elif date_idx == 2:
            prefs.set_pref("ops_dateFormat", "%Y-%m-%d")
        else:
            prefs.set_pref("ops_dateFormat", "%m/%d/%Y")

        time_idx = self.view.time_format_combo.currentIndex()
        if time_idx == 0:
            prefs.set_pref("ops_timeFormat", "%I:%M:%S %p")
        else:
            prefs.set_pref("ops_timeFormat", "%H:%M:%S")

        w_name = self.view.wip_name_field.text().strip()
        m_name = self.view.master_name_field.text().strip()

        if w_name:
            prefs.set_pref("ops_wip", w_name)
        if m_name:
            prefs.set_pref("ops_masterName", m_name)

        fmt_idx = self.view.file_format_combo.currentIndex()
        fmt_map = {0: "ma", 1: "mb", 2: "usd", 3: "usda", 4: "abc", 5: "fbx"}
        fmt = fmt_map.get(fmt_idx, "ma")
        # Keep WIP and master default formats synchronized when saved from Global Settings
        prefs.set_pref("ops_wipFormat", fmt)
        prefs.set_pref("ops_masterFormat", fmt)

        t_type = (
            "shotgrid" if self.view.tracker_type_combo.currentIndex() == 1 else "none"
        )
        prefs.set_pref("ops_tracker_type", t_type)
        prefs.set_pref("ops_tracker_url", self.view.tracker_url_field.text().strip())
        prefs.set_pref("ops_tracker_user", self.view.tracker_user_field.text().strip())
        prefs.set_pref("ops_tracker_key", self.view.tracker_key_field.text().strip())

        self.view.close()
        opsUIWrappers.refresh_ui()
