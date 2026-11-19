"""Best-effort file-use notices for projects in user-managed sync folders.

Provides :class:`FileUseRegistry`, :class:`FileUseNotice`, and :func:`get_file_state` to coordinate advisory file-use markers and detect external overwrites inside cloud-synchronized project directories.

:File: file_use.py
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.file.file_use import FileUseRegistry

    registry = FileUseRegistry("/projects/demo", user="Stephen")
    active = registry.list_notices("/projects/demo/scenes/shot01.ma")
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import socket
import uuid

#: Module logger for advisory file-use notice operations.
logger = logging.getLogger("openPypeline.file_use")


class FileUseRegistryError(RuntimeError):
    """Raised when file-use metadata cannot be safely read or written."""


@dataclass(frozen=True)
class FileUseNotice:
    """Describe another session's advisory use of a project file."""

    #: Display name of the user holding the advisory notice.
    user: str
    #: Hostname of the workstation running the other session.
    machine: str
    #: POSIX project-relative path to the tracked file.
    file_path: str
    #: UTC timestamp when the other session began using the file.
    started_at: datetime
    #: UTC timestamp of the other session's most recent heartbeat update.
    heartbeat_at: datetime
    #: ``True`` when ``heartbeat_at`` falls outside the active freshness window.
    stale: bool


def get_file_state(file_path: str) -> tuple[int, int] | None:
    """Return size and modification time for overwrite detection.

    :param file_path: Filesystem path to inspect.
    :returns: A ``(size_bytes, mtime_ns)`` tuple, or ``None`` if the file does not exist.
    :raises FileUseRegistryError: If ``os.stat`` fails due to permissions or an
        I/O error.
    """
    try:
        stat = os.stat(file_path)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise FileUseRegistryError(
            f"Could not inspect file {file_path}: {exc}"
        ) from exc
    return stat.st_size, stat.st_mtime_ns


class FileUseRegistry:
    """Store advisory file-use notices inside a synchronized project folder.

    Sync clients propagate these JSON metadata files asynchronously, so
    notices are informative only and cannot provide guaranteed mutual
    exclusion.

    :ivar project_root: Resolved root directory of the shared project.
    :vartype project_root: Path
    :ivar user: Sanitized display name for the current session's user.
    :vartype user: str
    :ivar machine: Hostname identifying the local workstation.
    :vartype machine: str
    :ivar stale_after: Maximum allowed age (or future clock skew) before a notice heartbeat is marked stale.
    :vartype stale_after: timedelta
    :ivar session_id: Unique hex identifier for this registry session.
    :vartype session_id: str
    """

    def __init__(
        self,
        project_root: str,
        user: str,
        machine: str | None = None,
        stale_after: timedelta = timedelta(minutes=5),
        session_id: str | None = None,
    ) -> None:
        """Initialize this session's registry and validate the project root.

        :param project_root: Root directory of the synchronized project folder.
        :param user: Name of the current user (falls back to ``"Unknown user"`` if blank).
        :param machine: Optional workstation hostname; defaults to ``socket.gethostname()``.
        :param stale_after: Freshness threshold applied to notice heartbeats.
        :param session_id: Optional explicit session identifier; defaults to a random UUID hex string.
        :raises FileUseRegistryError: If ``project_root`` does not exist or is not a directory.
        """
        self.project_root = Path(project_root).expanduser().resolve()
        self.user = user.strip() or "Unknown user"
        self.machine = machine or socket.gethostname()
        self.stale_after = stale_after
        self.session_id = session_id or uuid.uuid4().hex
        self._lock_path: Path | None = None
        self._locked_file_key: str | None = None
        self._relative_path: str | None = None
        self._started_at: datetime | None = None

        if not self.project_root.is_dir():
            raise FileUseRegistryError(
                f"Project folder does not exist: {self.project_root}"
            )

    @property
    def has_notice(self) -> bool:
        """Report whether this registry currently tracks an active file-use notice.

        :returns: ``True`` if a lock file path and file key are currently active, otherwise ``False``.
        """
        return bool(self._lock_path and self._locked_file_key)

    def _file_key(self, file_path: str) -> tuple[str, str]:
        """Validate a project-relative path and derive its stable notice key.

        Resolves canonical on-disk filename casing on case-insensitive filesystems and computes a SHA-256 hash of the POSIX relative path.

        :param file_path: Target file path inside :attr:`project_root`.
        :returns: A ``(file_id, relative_path)`` tuple containing the SHA-256 hex digest and normalized POSIX project-relative path.
        :raises FileUseRegistryError: If ``file_path`` lies outside :attr:`project_root` or its on-disk casing cannot be resolved.
        """
        target = Path(file_path).expanduser().resolve()
        try:
            relative = target.relative_to(self.project_root)
        except ValueError as exc:
            raise FileUseRegistryError(
                f"File is outside the shared project folder: {target}"
            ) from exc

        relative_path = relative.as_posix()
        if target.exists():
            # resolve() does not consistently return stored filename casing. Canonicalize aliases on case-insensitive filesystems, while retaining exact spellings for distinct case-sensitive files.
            parts = []
            parent = self.project_root
            try:
                for part in relative.parts:
                    with os.scandir(parent) as entries:
                        names = [entry.name for entry in entries]
                    if part not in names:
                        matches = [
                            name for name in names
                            if name.casefold() == part.casefold()
                        ]
                        if len(matches) == 1:
                            part = matches[0]
                        else:
                            raise FileUseRegistryError(
                                f"Could not resolve project path casing for "
                                f"{target}"
                            )
                    parts.append(part)
                    parent = parent / part
            except OSError as exc:
                raise FileUseRegistryError(
                    "Could not resolve project path casing for "
                    f"{target}: {exc}"
                ) from exc
            relative_path = Path(*parts).as_posix()

        file_id = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()
        return file_id, relative_path

    def _notices_directory(self, file_id: str) -> Path:
        """Return the directory containing notices for the given file key.

        :param file_id: SHA-256 hex digest identifying the tracked file.
        :returns: Path under ``<project_root>/.openpypeline/file_use/<file_id>``.
        """
        return self.project_root / ".openpypeline" / "file_use" / file_id

    @staticmethod
    def _parse_timestamp(
        value: str,
        metadata_path: Path,
    ) -> datetime:
        """Parse a timezone-aware notice timestamp and normalize it to UTC.

        :param value: ISO-8601 timestamp string read from notice metadata.
        :param metadata_path: Path to the JSON notice file (used in error context).
        :returns: Timezone-aware ``datetime`` converted to UTC.
        :raises FileUseRegistryError: If ``value`` is not valid ISO-8601 format or lacks timezone information.
        """
        try:
            timestamp = datetime.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise FileUseRegistryError(
                f"Invalid timestamp in file-use notice: {metadata_path}"
            ) from exc
        if timestamp.tzinfo is None:
            raise FileUseRegistryError(
                f"Missing timezone in file-use notice: {metadata_path}"
            )
        return timestamp.astimezone(timezone.utc)
    def list_notices(self, file_path: str) -> list[FileUseNotice]:
        """Return all external notices for a file, including stale ones.

        Reads all ``.json`` notice files for ``file_path``, skips notices belonging to the current :attr:`session_id`, and flags entries whose heartbeat exceeds :attr:`stale_after` (including future clock skew).

        :param file_path: Target file path inside :attr:`project_root`.
        :returns: List of :class:`FileUseNotice` records from other sessions.
        :raises FileUseRegistryError: If ``file_path`` is invalid or any notice JSON file is unreadable, malformed, or uses an unsupported schema.
        """
        file_id, relative_path = self._file_key(file_path)
        directory = self._notices_directory(file_id)
        try:
            metadata_paths = sorted(
                path for path in directory.iterdir() if path.suffix == ".json"
            )
        except FileNotFoundError:
            return []
        except OSError as exc:
            raise FileUseRegistryError(
                f"Could not list file-use notices in {directory}: {exc}"
            ) from exc

        now = datetime.now(timezone.utc)
        notices = []

        for metadata_path in metadata_paths:
            try:
                with metadata_path.open("r", encoding="utf-8") as handle:
                    metadata = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                raise FileUseRegistryError(
                    f"Could not read file-use notice {metadata_path}: {exc}"
                ) from exc

            if not isinstance(metadata, dict):
                raise FileUseRegistryError(
                    f"Invalid file-use notice format: {metadata_path}"
                )
            if metadata.get("schema_version") != 1:
                raise FileUseRegistryError(
                    f"Unsupported file-use notice version: {metadata_path}"
                )
            if metadata.get("session_id") == self.session_id:
                continue
            metadata_file_path = metadata.get("file_path")
            if not isinstance(metadata_file_path, str):
                raise FileUseRegistryError(
                    f"Invalid file path in file-use notice: {metadata_path}"
                )
            if metadata_file_path != relative_path:
                continue

            started_at = self._parse_timestamp(
                metadata.get("started_at"),
                metadata_path,
            )
            heartbeat_at = self._parse_timestamp(
                metadata.get("heartbeat_at"),
                metadata_path,
            )
            age = now - heartbeat_at
            # Treat future heartbeats as stale too; clock skew must not make an implausibly recent notice appear to be a live session.
            stale = (
                age > self.stale_after
                or age < -self.stale_after
            )
            notices.append(
                FileUseNotice(
                    user=str(metadata.get("user", "Unknown user")),
                    machine=str(metadata.get("machine", "Unknown machine")),
                    file_path=relative_path,
                    started_at=started_at,
                    heartbeat_at=heartbeat_at,
                    stale=stale,
                )
            )
        return notices
    def _write_notice(
        self,
        file_id: str,
        relative_path: str,
        started_at: datetime,
    ) -> None:
        """Atomically write this session's notice and update local state.

        Writes JSON metadata to a temporary ``.tmp`` file before replacing ``<session_id>.json`` via ``os.replace`` so sync clients do not observe partially written files.

        :param file_id: SHA-256 hex digest identifying the tracked file.
        :param relative_path: Normalized POSIX path relative to :attr:`project_root`.
        :param started_at: UTC timestamp recording when this session first acquired the file notice.
        :raises FileUseRegistryError: If creating the directory or writing the notice file fails.
        """
        directory = self._notices_directory(file_id)
        lock_path = directory / f"{self.session_id}.json"
        temporary_path = directory / f"{self.session_id}.tmp"
        now = datetime.now(timezone.utc)
        metadata = {
            "schema_version": 1,
            "session_id": self.session_id,
            "user": self.user,
            "machine": self.machine,
            "file_path": relative_path,
            "started_at": started_at.isoformat(),
            "heartbeat_at": now.isoformat(),
        }

        try:
            directory.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as handle:
                json.dump(metadata, handle, indent=2)
            os.replace(temporary_path, lock_path)
        except OSError as exc:
            raise FileUseRegistryError(
                f"Could not write file-use notice for {relative_path}: {exc}"
            ) from exc
        self._lock_path = lock_path
        self._locked_file_key = file_id
        self._relative_path = relative_path
        self._started_at = started_at
    def acquire(self, file_path: str) -> list[FileUseNotice]:
        """Write this session's notice and return notices already observed.

        Releases any previously held notice on a different file via :meth:`release`, preserves the original ``started_at`` timestamp if re-acquiring the same file, and records a fresh heartbeat.

        :param file_path: Target file path inside :attr:`project_root`.
        :returns: List of existing :class:`FileUseNotice` records from other sessions found prior to writing this session's notice.
        :raises FileUseRegistryError: If ``file_path`` is invalid or writing the notice fails.
        """
        file_id, relative_path = self._file_key(file_path)
        existing_notices = self.list_notices(file_path)
        if self._locked_file_key and self._locked_file_key != file_id:
            self.release()

        started_at = datetime.now(timezone.utc)
        if (
            self._lock_path
            and self._locked_file_key == file_id
            and self._lock_path.exists()
        ):
            try:
                with self._lock_path.open("r", encoding="utf-8") as handle:
                    metadata = json.load(handle)
                started_at = self._parse_timestamp(
                    metadata.get("started_at"),
                    self._lock_path,
                )
            except (OSError, json.JSONDecodeError):
                logger.warning(
                    "Replacing unreadable file-use notice for this session."
                )
        self._write_notice(file_id, relative_path, started_at)
        return existing_notices
    def heartbeat(self) -> None:
        """Refresh this session's notice while its file remains open.

        Re-creates the notice file if removed externally, or updates ``heartbeat_at`` while preserving the original ``started_at`` timestamp.

        :raises FileUseRegistryError: If no notice is currently active for this session, or if the existing notice file cannot be read or rewritten.
        """
        if (
            not self._lock_path
            or not self._locked_file_key
            or not self._relative_path
            or not self._started_at
        ):
            raise FileUseRegistryError(
                "This session has no synchronized file-use notice."
            )
        if not self._lock_path.exists():
            self._write_notice(
                self._locked_file_key,
                self._relative_path,
                self._started_at,
            )
            return
        try:
            with self._lock_path.open("r", encoding="utf-8") as handle:
                metadata = json.load(handle)
            if (
                not isinstance(metadata, dict)
                or not isinstance(metadata.get("file_path"), str)
            ):
                raise FileUseRegistryError(
                    f"Invalid file-use notice: {self._lock_path}"
                )
            started_at = self._parse_timestamp(
                metadata.get("started_at"),
                self._lock_path,
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise FileUseRegistryError(
                f"Could not refresh file-use notice {self._lock_path}: {exc}"
            ) from exc
        self._write_notice(
            self._locked_file_key,
            str(metadata["file_path"]),
            started_at,
        )
    def release(self) -> None:
        """Remove this session's notice on file close or host exit.

        Deletes the active ``<session_id>.json`` file if present and clears internal tracking state.

        :raises FileUseRegistryError: If unlinking the notice file fails due to an OS or permission error.
        """
        if not self._lock_path:
            return
        try:
            self._lock_path.unlink(missing_ok=True)
        except OSError as exc:
            raise FileUseRegistryError(
                f"Could not remove file-use notice {self._lock_path}: {exc}"
            ) from exc
        self._lock_path = None
        self._locked_file_key = None
        self._relative_path = None
        self._started_at = None
