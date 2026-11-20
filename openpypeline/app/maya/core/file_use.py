"""Maya scene callbacks for synchronized-folder file-use notices.

Registers :class:`maya.api.OpenMaya.MSceneMessage` lifecycle hooks and a periodic :class:`PySide6.QtCore.QTimer` heartbeat to acquire, refresh, and release advisory file-use notices via :class:`~openpypeline.core.file_use.FileUseRegistry`.

:File: file_use.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import getpass
import logging
import os
from pathlib import Path
import socket
from typing import Any, Optional
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

#: Module logger for Maya advisory file-use lifecycle events.
logger = logging.getLogger("openPypeline.maya.file_use")

# --- Module-Level Callback and Registry State ---
#: Active :class:`~openpypeline.core.file_use.FileUseRegistry` bound to the current project.
_registry: Optional[FileUseRegistry] = None
#: Resolved root directory path of the active project monitored by :data:`_registry`.
_project_root: Optional[str] = None
#: Registered Maya ``MSceneMessage`` callback IDs tracked for cleanup on exit/uninstall.
_callbacks: list[Any] = []
#: Periodic ``QTimer`` keeping the active session's advisory notice heartbeat alive.
_heartbeat_timer: Optional[QtCore.QTimer] = None
#: Canonical path of the currently opened project scene tracked by this session.
_opened_path: Optional[str] = None
#: Filesystem ``(mtime, size)`` state recorded when :data:`_opened_path` was loaded or saved.
_opened_file_state: Optional[tuple[Any, ...]] = None
#: Target path captured during ``kBeforeOpenCheck`` for post-open validation.
_pending_open_path: Optional[str] = None
#: Pre-open filesystem state captured during ``kBeforeOpenCheck`` to detect external sync updates.
_pending_open_state: Optional[tuple[Any, ...]] = None

# Deterministic per-process session identifier scoped to host and PID so notices survive module reloads
_session_id: str = uuid.uuid5(
    uuid.NAMESPACE_URL,
    f"openpypeline-maya:{socket.gethostname()}:{os.getpid()}",
).hex
def _configured_user() -> str:
    """Return the configured user name, falling back to the operating-system user.

    Reads ``ops_currentUser`` from :mod:`~openpypeline.core.util.prefs` and falls back to :func:`getpass.getuser` when unset or left at ``"default"``.

    :returns: Non-empty artist display name for advisory lock notices.
    """
    user = str(prefs.get_pref("ops_currentUser", "")).strip()
    # Treat the placeholder "default" user pref as unset so OS login is preferred
    if not user or user.casefold() == "default":
        user = getpass.getuser().strip()
    return user or "Unknown user"


def _get_registry() -> Optional[FileUseRegistry]:
    """Return a registry for the active project, releasing it if paths change.

    Reuses the cached :class:`~openpypeline.core.file_use.FileUseRegistry` when ``ops_currProjectPath`` resolves to the same canonical root, or releases any prior notice and instantiates a fresh registry when switching projects.

    :returns: Active :class:`~openpypeline.core.file_use.FileUseRegistry` for the current project, or ``None`` if no valid project directory is set.
    """
    global _registry, _project_root

    project_root = str(prefs.get_pref("ops_currProjectPath", "")).strip()
    if not project_root or not os.path.isdir(project_root):
        _release_current()
        return None

    resolved_root = str(Path(project_root).expanduser().resolve())
    # Rebuild the registry whenever the artist switches to a different project root
    if _registry is None or resolved_root != _project_root:
        _release_current()
        _registry = FileUseRegistry(
            resolved_root,
            _configured_user(),
            session_id=_session_id,
        )
        _project_root = resolved_root
    return _registry


def _current_scene_path() -> str:
    """Return Maya's current scene path, or an empty string for an untitled scene."""
    return cmds.file(query=True, sceneName=True) or ""


def _resolved_path(filepath: str) -> str:
    """Expand and resolve a scene path to its canonical absolute form.

    :param filepath: Raw filesystem path string.
    :returns: Canonical resolved path string.
    """
    return str(Path(filepath).expanduser().resolve())


def _is_in_project(registry: FileUseRegistry, filepath: str) -> bool:
    """Return whether a resolved scene path is inside the registry's project.

    :param registry: Active :class:`~openpypeline.core.file_use.FileUseRegistry` whose ``project_root`` defines the project boundary.
    :param filepath: Candidate scene path to check.
    :returns: ``True`` if ``filepath`` resides beneath ``registry.project_root``, ``False`` otherwise.
    """
    try:
        target = Path(filepath).expanduser().resolve()
        # Raises ValueError when target escapes registry.project_root
        target.relative_to(registry.project_root)
        return True
    except ValueError:
        return False


def _notice_text(notices: list[Any]) -> str:
    """Format file-use notices for warnings shown to Maya users.

    :param notices: Sequence of advisory notice objects returned by :class:`~openpypeline.core.file_use.FileUseRegistry`.
    :returns: Newline-delimited human-readable summary of active notices.
    """
    lines = []
    for notice in notices:
        state = "possibly stale" if notice.stale else "reported open"
        lines.append(f"{notice.user} on {notice.machine} ({state})")
    return "\n".join(lines)


def _before_open_check(file_object: Any, *_args: Any) -> bool:
    """Capture the target path and disk state before Maya opens a scene.

    Invoked by ``MSceneMessage.kBeforeOpenCheck`` so post-open hooks can detect whether a cloud-sync client modified the file while Maya was loading it.

    :param file_object: ``MFileObject`` provided by Maya's pre-open check hook.
    :param _args: Additional Maya callback arguments (ignored).
    :returns: Always ``True`` to permit Maya to proceed with opening the file.
    """
    global _pending_open_path, _pending_open_state
    del _args
    filepath = file_object.resolvedFullName() or file_object.fullName()
    if not filepath:
        _pending_open_path = None
        _pending_open_state = None
        return True

    _pending_open_path = _resolved_path(filepath)
    try:
        # Snapshot mtime/size prior to load to detect mid-open sync updates
        _pending_open_state = get_file_state(filepath)
    except FileUseRegistryError as exc:
        _pending_open_state = None
        logger.warning("Could not record scene state before open: %s", exc)
    return True


def _warn_open_notices(notices: list[Any]) -> None:
    """Warn that another session may already have the requested scene open.

    :param notices: Sequence of conflicting advisory notices detected on open.
    """
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
def _warn_saved_to_in_use_file(notices: list[Any]) -> None:
    """Warn after saving to a path with notices from other sessions.

    :param notices: Sequence of active peer notices detected at the saved path.
    """
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


def _release_current() -> None:
    """Release the active file-use notice and clear registry state."""
    global _registry, _project_root
    if _registry:
        try:
            _registry.release()
        except FileUseRegistryError:
            logger.exception("Could not release the current file-use notice.")
    _registry = None
    _project_root = None


def _after_open(*_args: Any) -> None:
    """Acquire a notice for an opened in-project scene and warn about peers.

    Invoked by ``MSceneMessage.kAfterOpen`` to record the opened file's disk state, release any prior notice if the scene lies outside the active project, publish a new notice via :meth:`~openpypeline.core.file_use.FileUseRegistry.acquire`, and alert the artist if peer notices exist.

    :param _args: Maya callback arguments (ignored).
    """
    global _opened_path, _opened_file_state
    global _pending_open_path, _pending_open_state
    del _args
    registry = _get_registry()
    filepath = _current_scene_path()
    if not registry or not filepath:
        return
    _opened_path = _resolved_path(filepath)
    # Reuse the pre-open disk snapshot if kBeforeOpenCheck captured this exact path
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

    # Release any active project notice when opening an external scene
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


def _before_save_check(*_args: Any) -> bool:
    """Check for competing use or disk changes and gate Maya's save callback.

    Invoked by ``MSceneMessage.kBeforeSaveCheck``. Fails closed (canceling the save) if notice verification fails, prompts the user for confirmation when peer notices, external disk edits, or target collisions are detected, and refreshes this session's notice before allowing Maya to write.

    :param _args: Maya callback arguments (ignored).
    :returns: ``True`` to allow Maya to proceed with saving, ``False`` to
        cancel the save operation.
    """
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
        # Fail closed when notice verification fails to prevent silent overwrites
        QtWidgets.QMessageBox.warning(
            None,
            "Cannot Verify File Use",
            f"Could not check synchronized file-use notices:\n{exc}\n\n"
            "Saving was canceled to avoid overwriting another "
            "artist's changes.",
        )
        return False

    path = _resolved_path(filepath)
    # Detect whether a sync client updated the open file on disk since load/last save
    changed_on_disk = (
        path == _opened_path and current_file_state != _opened_file_state
    )
    # Detect Save-As over an existing file that this session never opened
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
def _after_new(*_args: Any) -> None:
    """Release scene-use state and clear paths after creating a new scene.

    Invoked by both ``MSceneMessage.kAfterNew`` and ``MSceneMessage.kMayaExiting`` to release any active notice and reset all tracked open/pending scene path and file-state globals.

    :param _args: Maya callback arguments (ignored).
    """
    global _opened_path, _opened_file_state
    global _pending_open_path, _pending_open_state
    del _args
    _release_current()
    _opened_path = None
    _opened_file_state = None
    _pending_open_path = None
    _pending_open_state = None


def _after_save(*_args: Any) -> None:
    """Update scene state and move or create a notice after a completed save.

    Invoked by ``MSceneMessage.kAfterSave`` to refresh the post-save disk snapshot, release the prior notice if the file was saved outside the active project, acquire a notice at the new in-project path, and warn if peer notices already exist there.

    :param _args: Maya callback arguments (ignored).
    """
    global _opened_path, _opened_file_state
    del _args
    registry = _get_registry()
    filepath = _current_scene_path()
    _opened_path = _resolved_path(filepath) if filepath else None
    try:
        # Refresh baseline disk snapshot to match the file Maya just wrote
        _opened_file_state = get_file_state(filepath) if filepath else None
    except FileUseRegistryError as exc:
        _opened_file_state = None
        logger.warning("Could not refresh scene state after save: %s", exc)
    # Release any active project notice if the user saved to an external location
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


def _heartbeat() -> None:
    """Refresh the current session's notice while Maya remains open."""
    if not _registry or not _registry.has_notice:
        return
    try:
        _registry.heartbeat()
    except FileUseRegistryError as exc:
        logger.warning("Could not refresh file-use notice: %s", exc)


def install_callbacks() -> None:
    """Install Maya scene lifecycle callbacks once per Maya process.

    Registers ``MSceneMessage`` hooks for scene open, new, save, pre-open/save checks, and Maya exit; starts a 30-second :class:`PySide6.QtCore.QTimer` heartbeat via :func:`_heartbeat`; and registers any scene already open in Maya via :func:`_after_open`. Rolls back all registered callbacks if setup fails.
    """
    global _callbacks, _heartbeat_timer
    # Guard against duplicate hook registration if openPypeline is launched twice
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
        # Refresh the session's advisory notice every 30 seconds so peers see it as active
        _heartbeat_timer = QtCore.QTimer()
        _heartbeat_timer.setInterval(30_000)
        _heartbeat_timer.timeout.connect(_heartbeat)
        _heartbeat_timer.start()
    except Exception:
        # Roll back partial callback registrations if any hook or timer setup fails
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


def uninstall_callbacks() -> None:
    """Remove callbacks and release this process's current notice.

    Stops :data:`_heartbeat_timer`, deregisters all ``MSceneMessage`` callback IDs stored in :data:`_callbacks`, and releases any active notice in :data:`_registry`.
    """
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
