"""
Module: ops_save_master_controller.py

Description: The Controller class for the openPypeline Studio Save Master Dialog. Handles logic, comment capturing, and validation for saving master files.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtCore, QtWidgets
from . import ui_objects as UIObjects
from openpypeline.app.maya.core import ops_ui_wrappers as opsUIWrappers
from openpypeline.core import ops_actions as opsActions
from openpypeline.core.util import prefs
from openpypeline.core.localization import localization
from .ops_save_master_gui import opsSaveMasterGUI

# --- Async Worker ---
class TaskFetcher(QtCore.QObject):
    """Asynchronous worker for fetching tasks from a ProductionTracker."""
    finished = QtCore.Signal(list)
    error = QtCore.Signal(str)

    def __init__(self, tracker_type, url, user, key, username):
        """Store tracker connection settings and the username to query."""
        super().__init__()
        self.tracker_type = tracker_type
        self.url = url
        self.user = user
        self.key = key
        self.username = username

    def run(self):
        """Fetch the user's tracker tasks and emit results or an error."""
        from openpypeline.app.maya.core import tracker_factory
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
    """Coordinate the Save Master dialog and its task lookup."""

    def __init__(self):
        """Create the view, connect its controls, and begin loading tasks."""
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
        self.view.task_combo.addItem(localization.get_string("msg_loadingTasks"), 0)
        self.view.task_combo.setEnabled(False)
        
        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "none" or not tracker_type:
            self.view.tracker_group.setEnabled(False)
            return
            
        username = prefs.get_pref("ops_tracker_user", "")
        if not username:
            self.view.task_combo.setItemText(0, localization.get_string("msg_noUserConfigured"))
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
        # Quit the worker thread on either outcome and defer QObject disposal until Qt has delivered the completion signal.
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def _on_tasks_loaded(self, tasks):
        """Populate the task selector with fetched tracker tasks."""
        self.view.task_combo.clear()
        self.view.task_combo.addItem(localization.get_string("lbl_none"), 0)
        self.view.task_combo.setEnabled(True)
        if not tasks:
            self.view.task_combo.setItemText(0, localization.get_string("msg_noTasksFound"))
            return
            
        for task in tasks:
            unknown_val = localization.get_string("msg_unknown")
            unknown_task = localization.get_string("msg_unknownTask")
            entity_name = task.get("entity", {}).get("name", unknown_val) if task.get("entity") else unknown_val
            task_name = task.get("content", unknown_task)
            task_id = task.get("id", 0)
            display_str = f"{entity_name} - {task_name}"
            self.view.task_combo.addItem(display_str, task_id)

    def _on_tasks_error(self, err_msg):
        """Show the appropriate fallback state after a failed task lookup."""
        self.view.task_combo.clear()
        self.view.task_combo.addItem(localization.get_string("lbl_none"), 0)
        if err_msg == "No tracker":
            self.view.tracker_group.setEnabled(False)
        else:
            self.view.task_combo.setItemText(0, localization.get_string("msg_errorLoadingTasks"))

    def on_save(self, *args):
        """Handles the master save execution."""
        flatten = self.view.masterImportReferencesBox_checkBox.isChecked()
        del_layers = self.view.masterDeleteLayersBox_checkBox.isChecked()
        after = self.view.after_radio_group.checkedId()
        command = self.view.ops_masterCommandField_txtField.text()
        comment = self.view.ops_masterCommentField_scrollField.toPlainText()
        task_id = self.view.task_combo.currentData() or 0
        
        if not opsActions.save_master(
            comment,
            flatten,
            del_layers,
            after,
            command,
            task_id,
        ):
            QtWidgets.QMessageBox.warning(
                self.view,
                localization.get_string("win_masterSwitchboard"),
                "The Master could not be saved. Check the log for details.",
            )
            return
        
        self.view.close()
        opsUIWrappers.refresh_ui()