"""Shared host-agnostic controller for the openPypeline Studio Save Master dialog.

Handles asynchronous production tracker task lookup via :class:`TaskFetcher`, captures cleanup/post-master options and release comments from :class:`~openpypeline.ui.ops_save_master_gui.OpsSaveMasterGUI`, and executes :func:`~openpypeline.core.ops_actions.save_master` across standalone tools and extensible DCC host integrations.

:File: ops_save_master_controller.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Any, Optional

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets  # type: ignore[no-redef]

from openpypeline.core import ops_actions as opsActions
from openpypeline.core.localization import localization
from openpypeline.core.util import prefs
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers
from openpypeline.ui import ui_objects as UIObjects


# --- Async Worker ---
class TaskFetcher(QtCore.QObject):
    """Asynchronous worker for fetching tasks from a production tracker.

    :ivar tracker_type: Production tracker backend identifier (for example, ``"shotgrid"``).
    :vartype tracker_type: str
    :ivar url: Production tracker server URL.
    :vartype url: str
    :ivar user: Tracker authentication username or script name.
    :vartype user: str
    :ivar key: Tracker authentication API key or personal access token.
    :vartype key: str
    :ivar username: Artist username whose assigned tasks should be queried.
    :vartype username: str
    """

    #: Signal emitted with a list of task dictionaries upon successful query.
    finished = QtCore.Signal(list)
    #: Signal emitted with an error message string if the tracker query fails.
    error = QtCore.Signal(str)

    def __init__(
        self,
        tracker_type: str,
        url: str,
        user: str,
        key: str,
        username: str,
    ) -> None:
        """Store tracker connection settings and the username to query.

        :param tracker_type: Tracker backend identifier.
        :param url: Tracker server URL.
        :param user: Tracker authentication user or script name.
        :param key: Tracker authentication API key or token.
        :param username: Target artist username for task lookup.
        """
        super().__init__()
        self.tracker_type = tracker_type
        self.url = url
        self.user = user
        self.key = key
        self.username = username

    def run(self) -> None:
        """Fetch the user's tracker tasks and emit results or an error."""
        from openpypeline.core import tracker_factory

        try:
            tracker = tracker_factory.get_tracker(
                self.tracker_type, self.url, self.user, self.key
            )
            if not tracker:
                self.error.emit("No tracker")
                return
            tasks = tracker.get_user_tasks(self.username)
            self.finished.emit(tasks)
        except Exception as e:
            self.error.emit(str(e))


class OpsSaveMasterController(QtCore.QObject):
    """Coordinate the Save Master dialog and its task lookup.

    Instantiates the Save Master view via :meth:`_create_view`, asynchronously populates assigned tasks via :class:`TaskFetcher`, and delegates master publishing to :func:`~openpypeline.core.ops_actions.save_master`.

    :ivar UIObjects: Shared :class:`~openpypeline.ui.ui_objects.WindowManager` singleton reference.
    :vartype UIObjects: openpypeline.ui.ui_objects.WindowManager
    :ivar view: Save Master switchboard widget managed by this controller.
    :vartype view: Any
    :ivar thread: Background ``QThread`` executing :attr:`worker`, if active.
    :vartype thread: Optional[QtCore.QThread]
    :ivar worker: Active :class:`TaskFetcher` worker instance, if started.
    :vartype worker: Optional[TaskFetcher]
    """

    def __init__(self) -> None:
        """Create the view, connect its controls, and begin loading tasks."""
        super().__init__()
        self.UIObjects = UIObjects.UIObjects()
        self.view = self._create_view()
        self.thread: Optional[QtCore.QThread] = None
        self.worker: Optional[TaskFetcher] = None

        self._connect_signals()
        self._populate_tasks()

    def _create_view(self) -> Any:
        """Instantiate and return the Save Master UI view widget.

        Host-specific subclasses should override this method to return their
        DCC-parented view subclass.

        :returns: Save Master view instance.
        """
        from openpypeline.ui.ops_save_master_gui import OpsSaveMasterGUI

        return OpsSaveMasterGUI()

    def showWindow(self) -> None:
        """Show the Save Master dialog."""
        self.view.show()

    def _connect_signals(self) -> None:
        """Bind view publish and cancel buttons to controller actions."""
        if hasattr(self.view, "save_btn"):
            self.view.save_btn.clicked.connect(self.on_save)
        if hasattr(self.view, "cancel_btn"):
            self.view.cancel_btn.clicked.connect(self.view.close)

    def _populate_tasks(self) -> None:
        """Fetch and populate the user's tasks from the active tracker asynchronously."""
        self.view.task_combo.addItem(
            localization.get_string("msg_loadingTasks"), 0
        )
        self.view.task_combo.setEnabled(False)

        tracker_type = prefs.get_pref("ops_tracker_type", "none")
        if tracker_type == "none" or not tracker_type:
            self.view.tracker_group.setEnabled(False)
            return

        username = prefs.get_pref("ops_tracker_user", "")
        if not username:
            self.view.task_combo.setItemText(
                0, localization.get_string("msg_noUserConfigured")
            )
            return

        url = prefs.get_pref("ops_tracker_url", "")
        key = prefs.get_pref("ops_tracker_key", "")

        self.thread = QtCore.QThread(self)
        self.worker = TaskFetcher(tracker_type, url, username, key, username)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_tasks_loaded)
        self.worker.error.connect(self._on_tasks_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_tasks_loaded(self, tasks: list[dict[str, Any]]) -> None:
        """Populate the task selector with fetched tracker tasks.

        :param tasks: List of task dictionaries returned by :class:`TaskFetcher`.
        """
        self.view.task_combo.clear()
        self.view.task_combo.addItem(localization.get_string("lbl_none"), 0)
        self.view.task_combo.setEnabled(True)
        if not tasks:
            self.view.task_combo.setItemText(
                0, localization.get_string("msg_noTasksFound")
            )
            return

        unknown_val = localization.get_string("msg_unknown")
        unknown_task = localization.get_string("msg_unknownTask")
        for task in tasks:
            entity_name = (
                task.get("entity", {}).get("name", unknown_val)
                if task.get("entity")
                else unknown_val
            )
            task_name = task.get("content", unknown_task)
            task_id = task.get("id", 0)
            display_str = f"{entity_name} - {task_name}"
            self.view.task_combo.addItem(display_str, task_id)

    def _on_tasks_error(self, err_msg: str) -> None:
        """Show the appropriate fallback state after a failed task lookup.

        :param err_msg: Error string emitted by :attr:`TaskFetcher.error`.
        """
        self.view.task_combo.clear()
        self.view.task_combo.addItem(localization.get_string("lbl_none"), 0)
        if err_msg == "No tracker":
            self.view.tracker_group.setEnabled(False)
        else:
            self.view.task_combo.setItemText(
                0, localization.get_string("msg_errorLoadingTasks")
            )

    def on_save(self, *args: Any) -> None:
        """Execute master publishing with the configured options and comment.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
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
