"""
Module: opsSettingsGUI.py

Description:
    Global Preferences and Settings UI for openPypeline Studio.
    Allows users to customize localization and pipeline defaults.
"""

import maya.cmds as cmds
import window as window
import UIObjects as UIObjects

class opsSettingsGUI(window.window):
    """
    A Maya window class for managing global openPypeline Studio settings.
    """

    def __init__(self):
        self.UIObjects = UIObjects.UIObjects()
        
        self.width = 400
        self.height = 250
        self.name = "Global Settings"
        self.dockable = 0
        
        self.lfMargin = 10
        self.rtMargin = 10
        
    def content(self):
        """Builds and returns the main form layout for the Settings UI."""
        self.form1 = cmds.formLayout('opsSettingsGUI_form', numberOfDivisions=100)
        
        self._build_localization_section()
        self._build_pipeline_defaults_section()
        self._build_action_buttons()
        
        self._attach_form_elements()
        self._populate_fields()
        
        return [self.form1]

    def _build_localization_section(self):
        self.loc_frame = cmds.frameLayout('loc_frame', label="Localization & Display", collapsable=False, parent=self.form1)
        self.loc_column = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnOffset=("both", 10), parent=self.loc_frame)
        
        self.date_format_grp = cmds.optionMenuGrp('ops_dateFormat_opt', label="Date Format: ", parent=self.loc_column)
        cmds.menuItem(label="MM/DD/YYYY (US)", parent=self.date_format_grp)
        cmds.menuItem(label="DD/MM/YYYY (EU/UK)", parent=self.date_format_grp)
        cmds.menuItem(label="YYYY-MM-DD (ISO)", parent=self.date_format_grp)
        
        self.time_format_grp = cmds.optionMenuGrp('ops_timeFormat_opt', label="Time Format: ", parent=self.loc_column)
        cmds.menuItem(label="12-Hour (AM/PM)", parent=self.time_format_grp)
        cmds.menuItem(label="24-Hour", parent=self.time_format_grp)

    def _build_pipeline_defaults_section(self):
        self.pipe_frame = cmds.frameLayout('pipe_frame', label="Pipeline Defaults", collapsable=False, parent=self.form1)
        self.pipe_column = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnOffset=("both", 10), parent=self.pipe_frame)
        
        self.wip_name_grp = cmds.textFieldGrp('ops_defaultWip_txt', label="Default WIP Name: ", parent=self.pipe_column)
        self.master_name_grp = cmds.textFieldGrp('ops_defaultMaster_txt', label="Default Master Name: ", parent=self.pipe_column)
        
        self.file_format_grp = cmds.optionMenuGrp('ops_defaultFormat_opt', label="Default File Format: ", parent=self.pipe_column)
        cmds.menuItem(label="ma", parent=self.file_format_grp)
        cmds.menuItem(label="mb", parent=self.file_format_grp)
        cmds.menuItem(label="usd", parent=self.file_format_grp)
        cmds.menuItem(label="usda", parent=self.file_format_grp)
        cmds.menuItem(label="abc", parent=self.file_format_grp)

    def _build_action_buttons(self):
        self.btn_row = cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190), columnAttach=[(1, 'both', 5), (2, 'both', 5)], parent=self.form1)
        self.save_btn = cmds.button(label="Save", command=self.on_save, parent=self.btn_row)
        self.cancel_btn = cmds.button(label="Cancel", command=self.on_cancel, parent=self.btn_row)

    def _attach_form_elements(self):
        cmds.formLayout(
            self.form1,
            edit=True,
            attachForm=[
                (self.loc_frame, 'top', 10),
                (self.loc_frame, 'left', self.lfMargin),
                (self.loc_frame, 'right', self.rtMargin),
                
                (self.pipe_frame, 'left', self.lfMargin),
                (self.pipe_frame, 'right', self.rtMargin),
                
                (self.btn_row, 'left', self.lfMargin),
                (self.btn_row, 'right', self.rtMargin),
                (self.btn_row, 'bottom', 10)
            ],
            attachControl=[
                (self.pipe_frame, 'top', 10, self.loc_frame)
            ]
        )

    def _populate_fields(self):
        date_fmt = cmds.optionVar(query="ops_dateFormat") if cmds.optionVar(exists="ops_dateFormat") else "%m/%d/%Y"
        if date_fmt == "%d/%m/%Y": cmds.optionMenuGrp(self.date_format_grp, edit=True, select=2)
        elif date_fmt == "%Y-%m-%d": cmds.optionMenuGrp(self.date_format_grp, edit=True, select=3)
        else: cmds.optionMenuGrp(self.date_format_grp, edit=True, select=1)
        
        time_fmt = cmds.optionVar(query="ops_timeFormat") if cmds.optionVar(exists="ops_timeFormat") else "%I:%M:%S %p"
        if time_fmt == "%I:%M:%S %p": cmds.optionMenuGrp(self.time_format_grp, edit=True, select=1)
        else: cmds.optionMenuGrp(self.time_format_grp, edit=True, select=2)
        
        w_name = cmds.optionVar(query="ops_wip") if cmds.optionVar(exists="ops_wip") else "wip"
        m_name = cmds.optionVar(query="ops_masterName") if cmds.optionVar(exists="ops_masterName") else "master"
        cmds.textFieldGrp(self.wip_name_grp, edit=True, text=w_name)
        cmds.textFieldGrp(self.master_name_grp, edit=True, text=m_name)
        
        f_fmt = cmds.optionVar(query="ops_workshopFormat") if cmds.optionVar(exists="ops_workshopFormat") else "ma"
        if f_fmt == "abc": cmds.optionMenuGrp(self.file_format_grp, edit=True, select=5)
        elif f_fmt == "usda": cmds.optionMenuGrp(self.file_format_grp, edit=True, select=4)
        elif f_fmt == "usd": cmds.optionMenuGrp(self.file_format_grp, edit=True, select=3)
        elif f_fmt == "mb": cmds.optionMenuGrp(self.file_format_grp, edit=True, select=2)
        else: cmds.optionMenuGrp(self.file_format_grp, edit=True, select=1)

    def on_save(self, *args):
        date_idx = cmds.optionMenuGrp(self.date_format_grp, query=True, select=True)
        if date_idx == 2: cmds.optionVar(stringValue=("ops_dateFormat", "%d/%m/%Y"))
        elif date_idx == 3: cmds.optionVar(stringValue=("ops_dateFormat", "%Y-%m-%d"))
        else: cmds.optionVar(stringValue=("ops_dateFormat", "%m/%d/%Y"))
        
        time_idx = cmds.optionMenuGrp(self.time_format_grp, query=True, select=True)
        if time_idx == 1: cmds.optionVar(stringValue=("ops_timeFormat", "%I:%M:%S %p"))
        else: cmds.optionVar(stringValue=("ops_timeFormat", "%H:%M:%S"))
        
        w_name = cmds.textFieldGrp(self.wip_name_grp, query=True, text=True).strip()
        m_name = cmds.textFieldGrp(self.master_name_grp, query=True, text=True).strip()
        
        if w_name: cmds.optionVar(stringValue=("ops_wip", w_name))
        if m_name: cmds.optionVar(stringValue=("ops_masterName", m_name))
        
        fmt_idx = cmds.optionMenuGrp(self.file_format_grp, query=True, select=True)
        fmt_map = {1: "ma", 2: "mb", 3: "usd", 4: "usda", 5: "abc"}
        fmt = fmt_map.get(fmt_idx, "ma")
        cmds.optionVar(stringValue=("ops_workshopFormat", fmt))
        cmds.optionVar(stringValue=("ops_masterFormat", fmt))
        
        self.deleteWindow()
        import opsUIWrappers
        opsUIWrappers.refresh_ui()

    def on_cancel(self, *args):
        self.deleteWindow()