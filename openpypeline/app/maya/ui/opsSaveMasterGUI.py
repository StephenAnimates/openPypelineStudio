"""
Module: opsSaveMasterGUI.py

Description:
    Launches the UI for Mastering
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

# --- UI Stylesheet ---
OPS_SAVE_MASTER_STYLESHEET = """
    QPushButton[styleClass="masterBtn"] {
        background-color: #e6b366; 
        color: black; 
        font-weight: bold;
    }
"""

class opsSaveMasterGUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.mName = "Master"
        
        self.setWindowTitle("Master File Switchboard")
        self.setObjectName("opsSaveMasterGUI")
        self.setMinimumSize(350, 260)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self._build_ui()

    def _build_ui(self):
        """Constructs the UI using PySide widgets and layouts."""
        self.setStyleSheet(OPS_SAVE_MASTER_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # --- Options Section ---
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout(options_group)
        
        self.masterImportReferencesBox_checkBox = QtWidgets.QCheckBox("Import References")
        self.masterImportReferencesBox_checkBox.setChecked(True)
        self.masterDeleteLayersBox_checkBox = QtWidgets.QCheckBox("Delete Display Layers")
        self.masterDeleteLayersBox_checkBox.setChecked(True)
        
        options_layout.addWidget(self.masterImportReferencesBox_checkBox)
        options_layout.addWidget(self.masterDeleteLayersBox_checkBox)
        
        after_layout = QtWidgets.QHBoxLayout()
        after_layout.addWidget(QtWidgets.QLabel("After Master Open:"))
        
        self.after_radio_group = QtWidgets.QButtonGroup(self)
        self.radio_workshop = QtWidgets.QRadioButton("WIP")
        self.radio_workshop.setChecked(True)  # Default selection (1)
        self.radio_master = QtWidgets.QRadioButton("Master")
        self.radio_new = QtWidgets.QRadioButton("New")
        
        self.after_radio_group.addButton(self.radio_workshop, 1)
        self.after_radio_group.addButton(self.radio_master, 2)
        self.after_radio_group.addButton(self.radio_new, 3)
        
        after_layout.addWidget(self.radio_workshop)
        after_layout.addWidget(self.radio_master)
        after_layout.addWidget(self.radio_new)
        after_layout.addStretch()
        
        options_layout.addLayout(after_layout)
        main_layout.addWidget(options_group)

        # --- Tracker Section ---
        self.tracker_group = QtWidgets.QGroupBox("Production Tracking")
        tracker_layout = QtWidgets.QFormLayout(self.tracker_group)
        self.task_combo = QtWidgets.QComboBox()
        tracker_layout.addRow("Select Task:", self.task_combo)
        main_layout.addWidget(self.tracker_group)

        # --- Command & Comment Section ---
        cmd_layout = QtWidgets.QFormLayout()
        self.ops_masterCommandField_txtField = QtWidgets.QLineEdit()
        cmd_layout.addRow(f"Custom {self.mName} Command:", self.ops_masterCommandField_txtField)
        
        self.ops_masterCommentField_scrollField = QtWidgets.QTextEdit()
        self.ops_masterCommentField_scrollField.setMaximumHeight(60)
        cmd_layout.addRow("Comment:", self.ops_masterCommentField_scrollField)
        
        main_layout.addLayout(cmd_layout)

        # --- Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.ops_masterCallback_btn = QtWidgets.QPushButton(self.mName)
        self.ops_masterCallback_btn.setProperty("styleClass", "masterBtn")
        self.ops_masterCallback_btn.setMinimumHeight(35)
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(35)
        
        btn_layout.addWidget(self.ops_masterCallback_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)