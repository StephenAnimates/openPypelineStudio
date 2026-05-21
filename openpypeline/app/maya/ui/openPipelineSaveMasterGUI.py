"""
Module: openPypelineSaveMasterGUI.py

Description:
    Launches the UI for Mastering
"""

import maya.cmds as cmds
import window as window
import UIObjects as UIObjects

class openPypelineSaveMasterGUI(window.window):

    def __init__(self):
        
        self.UIObjects = UIObjects.UIObjects()
        
        self.width=300
        self.height=200
        self.name = "Master File Switchboard"
        self.dockable=0
    
    def content(self):
        """
        Builds and returns the main form layout for the Save Master UI.
        """
        self.mName = "Master"
        self.form1 = cmds.formLayout('openPypelineSaveMasterGUI_form', numberOfDivisions=100)
        
        self._build_options_section()
        self._build_command_section()
        self._build_comment_section()
        self._build_action_buttons()
        self._attach_form_elements()
        
        return [self.form1]

    def _build_options_section(self):
        self.masterImportReferencesBox_checkBox = cmds.checkBox('masterImportReferencesBox_checkBox', label="Import References", v=1, parent=self.form1)
        self.masterDeleteLayersBox_checkBox = cmds.checkBox('masterDeleteLayersBox_checkBox', label="Delete Display Layers", v=1, parent=self.form1)
        
        self.op_afterMasterField_radioBtnGrp = cmds.radioButtonGrp(
            'op_afterMasterField_radioBtnGrp',
            numberOfRadioButtons=3,
            label="After Master Open:",
            labelArray3=("Workshop", "Master", "New"),
            columnWidth4=(100, 70, 60, 60),
            columnAlign4=("left", "left", "left", "left"),
            sl=1,
            parent=self.form1
        )

    def _build_command_section(self):
        self.op_masterCommandField_txt = cmds.text('op_masterCommandField_txt', label="Custom " + str(self.mName) + " Command:", parent=self.form1)
        self.op_masterCommandField_txtField = cmds.textField('op_masterCommandField_txtField', parent=self.form1)

    def _build_comment_section(self):
        self.op_masterCommentField_txt = cmds.text('op_masterCommentField_txt', label="comment: ", w=60, h=20, parent=self.form1)
        self.op_masterCommentField_scrollField = cmds.scrollField('op_masterCommentField_scrollField', h=40, ww=1, parent=self.form1)

    def _build_action_buttons(self):
        self.openPipelineMasterCallback_btn = cmds.button(
            'openPipelineMasterCallback_btn',
            label = self.mName,
            backgroundColor = (0.9, 0.7, 0.4),
            parent=self.form1
        )
        
        self.cancel_btn = cmds.button(
            'cancel_btn',
            label = "cancel",
            backgroundColor = ( 0.8, 0.4, 0.4),
            parent=self.form1
        )

    def _attach_form_elements(self):
        cmds.formLayout(
            self.form1,
            edit=True,
            attachPosition=[
                (self.op_masterCommandField_txtField, 'right', -280, 0),
                (self.op_masterCommentField_scrollField, 'right', -280, 0),
                (self.openPipelineMasterCallback_btn, 'right', -140, 0),
                (self.cancel_btn, 'right', -280, 0),
            ],
            attachForm=[
                (self.masterImportReferencesBox_checkBox, 'top', 2),
                (self.masterImportReferencesBox_checkBox, 'left', 2),
                (self.masterDeleteLayersBox_checkBox, 'top', 2),
                (self.op_afterMasterField_radioBtnGrp, 'left', 2),
                (self.op_masterCommandField_txt, 'left', 2),
                (self.op_masterCommentField_scrollField, 'left', 2),
                (self.openPipelineMasterCallback_btn, 'left', 2),
                (self.op_masterCommandField_txtField, 'left', 2),
                
            ],
            attachControl=[
                (self.masterDeleteLayersBox_checkBox, 'left', 2, self.masterImportReferencesBox_checkBox),
                (self.op_afterMasterField_radioBtnGrp, 'top', 2, self.masterImportReferencesBox_checkBox),
                (self.op_masterCommandField_txt, 'top', 2, self.op_afterMasterField_radioBtnGrp),
                (self.op_masterCommandField_txtField, 'top', 2, self.op_masterCommandField_txt),
                (self.op_masterCommentField_txt, 'top', 2, self.op_masterCommandField_txtField),
                (self.op_masterCommentField_scrollField, 'left', 2, self.op_masterCommentField_txt),
                (self.op_masterCommentField_scrollField, 'top', 2, self.op_masterCommandField_txtField),
                (self.openPipelineMasterCallback_btn, 'top', 2, self.op_masterCommentField_scrollField),
                (self.cancel_btn, 'top', 2, self.op_masterCommentField_scrollField),
                (self.cancel_btn, 'left', 2, self.openPipelineMasterCallback_btn),
            ]
        )