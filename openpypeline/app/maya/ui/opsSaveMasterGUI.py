"""
Module: opsSaveMasterGUI.py

Description:
    Launches the UI for Mastering
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import UIObjects
import tracker_factory
from openpypeline.core.util import prefs

# --- Async Worker ---
class TaskFetcher(QtCore.QObject):
    """Asynchronous worker for fetching tasks from a ProductionTracker."""
    finished = QtCore.Signal(list)
    error = QtCore.Signal(str)

    def __init__(self, tracker_type, url, user, key, username):
        super().__init__()
        self.tracker_type = tracker_type
        self.url = url
        self.user = user
        self.key = key
        self.username = username

    def run(self):
        import tracker_factory
        try:
            tracker = tracker_factory.get_tracker(self.tracker_type, self.url, self.user, self.key)
            if not tracker:
                self.error.emit("No tracker")
                return
            tasks = tracker.get_user_tasks(self.username)
            self.finished.emit(tasks)
        except Exception as e:
            self.error.emit(str(e))

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
        
        self.UIObjects = UIObjects.UIObjects()
        
        self.mName = "Master"
        
        self.setWindowTitle("Master File Switchboard")
        self.setObjectName("opsSaveMasterGUI")
        self.setMinimumSize(350, 260)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self._build_ui()

    def showWindow(self):
        """Shows the dialog window."""
        self.show()

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
        self._populate_tasks()

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
        self.ops_masterCallback_btn.clicked.connect(self.on_master_callback)
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.ops_masterCallback_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

    def _populate_tasks(self):
        """Fetches and populates the user's tasks from the active tracker asynchronously."""
        self.task_combo.addItem("Loading tasks...", 0)
        self.task_combo.setEnabled(False)
        
        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "none" or not tracker_type:
            self.tracker_group.setEnabled(False)
            return
            
        username = prefs.get_pref("ops_tracker_user", "")
        if not username:
            self.task_combo.setItemText(0, "No User Configured")
            return
            
        url = prefs.get_pref("ops_tracker_url", "")
        key = prefs.get_pref("ops_tracker_key", "")
        
        # Setup background thread to fetch tasks
        self.thread = QtCore.QThread(self)
        self.worker = TaskFetcher(tracker_type, url, username, key, username)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_tasks_loaded)
        self.worker.error.connect(self._on_tasks_error)
        
        # Cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def _on_tasks_loaded(self, tasks):
        self.task_combo.clear()
        self.task_combo.addItem("None", 0)
        self.task_combo.setEnabled(True)
        if not tasks:
            self.task_combo.setItemText(0, "No Tasks Found")
            return
            
        for task in tasks:
            entity_name = task.get("entity", {}).get("name", "Unknown") if task.get("entity") else "Unknown"
            task_name = task.get("content", "Unknown Task")
            task_id = task.get("id", 0)
            display_str = f"{entity_name} - {task_name}"
            self.task_combo.addItem(display_str, task_id)

    def _on_tasks_error(self, err_msg):
        self.task_combo.clear()
        self.task_combo.addItem("None", 0)
        if err_msg == "No tracker":
            self.tracker_group.setEnabled(False)
        else:
            self.task_combo.setItemText(0, "Error loading tasks")

    # --- Button Callbacks ---

    def on_master_callback(self, *args):
        import opsActions
        import opsUIWrappers
        
        flatten = self.masterImportReferencesBox_checkBox.isChecked()
        del_layers = self.masterDeleteLayersBox_checkBox.isChecked()
        after = self.after_radio_group.checkedId()
        command = self.ops_masterCommandField_txtField.text()
        comment = self.ops_masterCommentField_scrollField.toPlainText()
        task_id = self.task_combo.currentData() or 0
        
        opsActions.save_master(comment, flatten, del_layers, after, command, task_id)
        self.close()
        opsUIWrappers.refresh_ui()