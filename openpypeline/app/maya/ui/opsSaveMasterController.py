"""
Module: opsSaveMasterController.py

Description:
    The Controller class for the openPypeline Studio Save Master Dialog.
    Handles logic, comment capturing, and validation for saving master files.
"""

from PySide6 import QtCore
import UIObjects
import opsUIWrappers
import opsActions
from openpypeline.core.util import prefs
from openpypeline.app.maya.ui.opsSaveMasterGUI import opsSaveMasterGUI

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

class OpsSaveMasterController(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.UIObjects = UIObjects.UIObjects()
        self.view = opsSaveMasterGUI()
        
        self._connect_signals()
        self._populate_tasks()

    def showWindow(self):
        """Shows the Save Master dialog."""
        self.view.show()

    def _connect_signals(self):
        """Binds view buttons to controller actions."""
        # Map these attributes to the exact widget names inside your opsSaveMasterGUI
        if hasattr(self.view, 'save_btn'):
            self.view.save_btn.clicked.connect(self.on_save)
        if hasattr(self.view, 'cancel_btn'):
            self.view.cancel_btn.clicked.connect(self.view.close)

    def _populate_tasks(self):
        """Fetches and populates the user's tasks from the active tracker asynchronously."""
        self.view.task_combo.addItem("Loading tasks...", 0)
        self.view.task_combo.setEnabled(False)
        
        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "none" or not tracker_type:
            self.view.tracker_group.setEnabled(False)
            return
            
        username = prefs.get_pref("ops_tracker_user", "")
        if not username:
            self.view.task_combo.setItemText(0, "No User Configured")
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
        self.view.task_combo.clear()
        self.view.task_combo.addItem("None", 0)
        self.view.task_combo.setEnabled(True)
        if not tasks:
            self.view.task_combo.setItemText(0, "No Tasks Found")
            return
            
        for task in tasks:
            entity_name = task.get("entity", {}).get("name", "Unknown") if task.get("entity") else "Unknown"
            task_name = task.get("content", "Unknown Task")
            task_id = task.get("id", 0)
            display_str = f"{entity_name} - {task_name}"
            self.view.task_combo.addItem(display_str, task_id)

    def _on_tasks_error(self, err_msg):
        self.view.task_combo.clear()
        self.view.task_combo.addItem("None", 0)
        if err_msg == "No tracker":
            self.view.tracker_group.setEnabled(False)
        else:
            self.view.task_combo.setItemText(0, "Error loading tasks")

    def on_save(self, *args):
        """Handles the master save execution."""
        flatten = self.view.masterImportReferencesBox_checkBox.isChecked()
        del_layers = self.view.masterDeleteLayersBox_checkBox.isChecked()
        after = self.view.after_radio_group.checkedId()
        command = self.view.ops_masterCommandField_txtField.text()
        comment = self.view.ops_masterCommentField_scrollField.toPlainText()
        task_id = self.view.task_combo.currentData() or 0
        
        opsActions.save_master(comment, flatten, del_layers, after, command, task_id)
        
        self.view.close()
        opsUIWrappers.refresh_ui()