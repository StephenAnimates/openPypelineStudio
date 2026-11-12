"""Maya scene callbacks for synchronized-folder file-use notices."""

import getpass
import logging
import os
from pathlib import Path
import socket
import uuid

from maya import cmds
from maya.api import OpenMaya as om
from PySide6 import QtCore, QtWidgets

from openpypeline.core.file_use import (
    FileUseRegistry,
    FileUseRegistryError,
    get_file_state,
)
from openpypeline.core.util import prefs

logger = logging.getLogger("openPypeline.maya.file_use")

_registry = None
_project_root = None
_callbacks = []
_heartbeat_timer = None
_opened_path = None
_opened_file_state = None
_pending_open_path = None
_pending_open_state = None
_session_id = uuid.uuid5(
    uuid.NAMESPACE_URL,
    f"openpypeline-maya:{socket.gethostname()}:{os.getpid()}",
).hex


def _configured_user():
    """Return the configured user name, falling back to the operating-system user."""
    user = str(prefs.get_pref("ops_currentUser", "")).strip()
    if not user or user.casefold() == "default":
        user = getpass.getuser().strip()
    return user or "Unknown user"


def _get_registry():
    """Return a registry for the active project, releasing it if paths change."""
    global _registry, _project_root

    project_root = str(prefs.get_pref("ops_currProjectPath", "")).strip()
    if not project_root or not os.path.isdir(project_root):
        _release_current()
        return None

    resolved_root = str(Path(project_root).expanduser().resolve())
    if _registry is None or resolved_root != _project_root:
        _release_current()
        _registry = FileUseRegistry(
            resolved_root,
            _configured_user(),
            session_id=_session_id,
        )
        _project_root = resolved_root
    return _registry


def _current_scene_path():
    """Return Maya's current scene path, or an empty string for an untitled scene."""
    return cmds.file(query=True, sceneName=True) or ""


def _resolved_path(filepath):
    """Expand and resolve a scene path to its canonical absolute form."""
    return str(Path(filepath).expanduser().resolve())


def _is_in_project(registry, filepath):
    """Return whether a resolved scene path is inside the registry's project."""
    try:
        target = Path(filepath).expanduser().resolve()
        target.relative_to(registry.project_root)
        return True
    except ValueError:
        return False


def _notice_text(notices):
    """Format file-use notices for warnings shown to Maya users."""
    lines = []
    for notice in notices:
        state = "possibly stale" if notice.stale else "reported open"
        lines.append(f"{notice.user} on {notice.machine} ({state})")
    return "\n".join(lines)


def _before_open_check(file_object, *_args):
    """Capture the target path and disk state before Maya opens a scene."""
    global _pending_open_path, _pending_open_state
    del _args
    filepath = file_object.resolvedFullName() or file_object.fullName()
    if not filepath:
        _pending_open_path = None
        _pending_open_state = None
        return True

    _pending_open_path = _resolved_path(filepath)
    try:
        _pending_open_state = get_file_state(filepath)
    except FileUseRegistryError as exc:
        _pending_open_state = None
        logger.warning("Could not record scene state before open: %s", exc)
    return True


def _warn_open_notices(notices):
    """Warn that another session may already have the requested scene open."""
    if notices:
        QtWidgets.QMessageBox.warning(
            None,
            "File May Be Open Elsewhere",
            "This file has synchronized file-use notices from:\n\n"
            f"{_notice_text(notices)}\n\n"
            "The other artist's status may be out of date because sync can be "
            "delayed. "
            "Opening is allowed, but coordinate before editing.",
        )


def _warn_saved_to_in_use_file(notices):
    """Warn after saving to a path with notices from other sessions."""
    if notices:
        QtWidgets.QMessageBox.warning(
            None,
            "Saved File May Be In Use",
            "The scene was saved, but synchronized file-use notices already "
            "existed for this path:\n\n"
            f"{_notice_text(notices)}\n\n"
            "The save has already completed. Coordinate with the other artist "
            "and verify the synchronized file before continuing.",
        )


def _release_current():
    """Release the active file-use notice and clear registry state."""
    global _registry, _project_root
    if _registry:
        try:
            _registry.release()
        except FileUseRegistryError:
            logger.exception("Could not release the current file-use notice.")
    _registry = None
    _project_root = None


def _after_open(*_args):
    """Acquire a notice for an opened in-project scene and warn about peers."""
    global _opened_path, _opened_file_state
    global _pending_open_path, _pending_open_state
    del _args
    registry = _get_registry()
    filepath = _current_scene_path()
    if not registry or not filepath:
        return
    _opened_path = _resolved_path(filepath)
    if _pending_open_path == _opened_path:
        _opened_file_state = _pending_open_state
    else:
        try:
            _opened_file_state = get_file_state(filepath)
        except FileUseRegistryError as exc:
            _opened_file_state = None
            logger.warning("Could not record scene state after open: %s", exc)
    _pending_open_path = None
    _pending_open_state = None

    if not _is_in_project(registry, filepath):
        _release_current()
        return

    try:
        notices = registry.acquire(filepath)
    except FileUseRegistryError as exc:
        logger.error("Could not register file use: %s", exc)
        QtWidgets.QMessageBox.warning(
            None,
            "File-Use Notice Unavailable",
            f"Could not publish a file-use notice for this scene:\n{exc}\n\n"
            "Other users may not be warned that the file is open.",
        )
        return
    _warn_open_notices(notices)


def _before_save_check(*_args):
    """Check for competing use or disk changes and gate Maya's save callback."""
    global _opened_path
    del _args
    registry = _get_registry()
    filepath = _current_scene_path()
    if not registry or not filepath or not _is_in_project(registry, filepath):
        return True

    try:
        notices = registry.list_notices(filepath)
        current_file_state = get_file_state(filepath)
    except FileUseRegistryError as exc:
        QtWidgets.QMessageBox.warning(
            None,
            "Cannot Verify File Use",
            f"Could not check synchronized file-use notices:\n{exc}\n\n"
            "Saving was canceled to avoid overwriting another "
            "artist's changes.",
        )
        return False

    path = _resolved_path(filepath)
    changed_on_disk = (
        path == _opened_path and current_file_state != _opened_file_state
    )
    existing_unopened_target = (
        path != _opened_path and current_file_state is not None
    )
    if notices or changed_on_disk or existing_unopened_target:
        reasons = []
        if notices:
            reasons.append(
                "This file has synchronized file-use notices from:\n\n"
                f"{_notice_text(notices)}"
            )
        if changed_on_disk:
            reasons.append(
                "The file changed on disk after this session opened it."
            )
        if existing_unopened_target:
            reasons.append(
                "The save target exists and was not opened in this session."
            )
        result = QtWidgets.QMessageBox.warning(
            None,
            "File May Have Changed",
            "\n\n".join(reasons)
            + "\n\nSync may be delayed, so file-use notices and file "
            "timestamps "
            "cannot guarantee exclusive access. Save anyway?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if result != QtWidgets.QMessageBox.Yes:
            return False

    try:
        registry.acquire(filepath)
    except FileUseRegistryError as exc:
        QtWidgets.QMessageBox.warning(
            None,
            "File-Use Notice Unavailable",
            f"Could not update this session's file-use notice:\n{exc}\n\n"
            "Saving was canceled.",
        )
        return False
    _opened_path = path
    return True


def _after_new(*_args):
    """Release scene-use state and clear paths after creating a new scene."""
    global _opened_path, _opened_file_state
    global _pending_open_path, _pending_open_state
    del _args
    _release_current()
    _opened_path = None
    _opened_file_state = None
    _pending_open_path = None
    _pending_open_state = None


def _after_save(*_args):
    """Update scene state and move or create a notice after a completed save."""
    global _opened_path, _opened_file_state
    del _args
    registry = _get_registry()
    filepath = _current_scene_path()
    _opened_path = _resolved_path(filepath) if filepath else None
    try:
        _opened_file_state = get_file_state(filepath) if filepath else None
    except FileUseRegistryError as exc:
        _opened_file_state = None
        logger.warning("Could not refresh scene state after save: %s", exc)
    if not registry or not filepath or not _is_in_project(registry, filepath):
        _release_current()
        return
    try:
        # Maya may update sceneName only after a Save As completes.
        notices = registry.acquire(filepath)
    except FileUseRegistryError as exc:
        logger.error(
            "Could not update the saved scene's file-use notice: %s",
            exc,
        )
        QtWidgets.QMessageBox.warning(
            None,
            "File-Use Notice Unavailable",
            "The scene was saved, but this session could not publish its "
            f"file-use notice:\n{exc}\n\nOther users may not be warned that "
            "the file is open.",
        )
        return
    _warn_saved_to_in_use_file(notices)


def _heartbeat():
    """Refresh the current session's notice while Maya remains open."""
    if not _registry or not _registry.has_notice:
        return
    try:
        _registry.heartbeat()
    except FileUseRegistryError as exc:
        logger.warning("Could not refresh file-use notice: %s", exc)


def install_callbacks():
    """Install Maya scene lifecycle callbacks once per Maya process."""
    global _callbacks, _heartbeat_timer
    if _callbacks:
        return

    registrations = [
        lambda: om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterOpen,
            _after_open,
        ),
        lambda: om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterNew,
            _after_new,
        ),
        lambda: om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterSave,
            _after_save,
        ),
        lambda: om.MSceneMessage.addCheckFileCallback(
            om.MSceneMessage.kBeforeOpenCheck,
            _before_open_check,
        ),
        lambda: om.MSceneMessage.addCheckCallback(
            om.MSceneMessage.kBeforeSaveCheck,
            _before_save_check,
        ),
        lambda: om.MSceneMessage.addCallback(
            om.MSceneMessage.kMayaExiting,
            _after_new,
        ),
    ]
    try:
        for register in registrations:
            _callbacks.append(register())
        _heartbeat_timer = QtCore.QTimer()
        _heartbeat_timer.setInterval(30_000)
        _heartbeat_timer.timeout.connect(_heartbeat)
        _heartbeat_timer.start()
    except Exception:
        if _heartbeat_timer:
            _heartbeat_timer.stop()
            _heartbeat_timer = None
        for callback_id in _callbacks:
            om.MMessage.removeCallback(callback_id)
        _callbacks = []
        raise

    try:
        # openPypeline can be launched after Maya has already loaded a scene.
        _after_open()
    except Exception:
        logger.exception("Could not register the already-open Maya scene.")


def uninstall_callbacks():
    """Remove callbacks and release this process's current notice."""
    global _callbacks, _heartbeat_timer, _registry, _project_root
    if _heartbeat_timer:
        _heartbeat_timer.stop()
        _heartbeat_timer = None
    for callback_id in _callbacks:
        om.MMessage.removeCallback(callback_id)
    _callbacks = []
    _release_current()
    _registry = None
    _project_root = None
