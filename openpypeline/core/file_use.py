"""Best-effort file-use notices for projects in user-managed sync folders."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import socket
import uuid

logger = logging.getLogger("openPypeline.file_use")


class FileUseRegistryError(RuntimeError):
    """Raised when file-use metadata cannot be safely read or written."""


@dataclass(frozen=True)
class FileUseNotice:
    """Describe another session's advisory use of a project file."""

    user: str
    machine: str
    file_path: str
    started_at: datetime
    heartbeat_at: datetime
    stale: bool


def get_file_state(file_path: str) -> tuple[int, int] | None:
    """Return size and modification time for overwrite detection."""
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
    """Stores advisory file-use notices inside a synchronized project folder.

    Sync clients propagate these files asynchronously, so notices are
    informative only and cannot provide guaranteed mutual exclusion.
    """

    def __init__(
        self,
        project_root: str,
        user: str,
        machine: str | None = None,
        stale_after: timedelta = timedelta(minutes=5),
        session_id: str | None = None,
    ):
        """Initialize this session's registry and validate the project root."""
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
        """Report whether this registry currently tracks a file-use notice."""
        return bool(self._lock_path and self._locked_file_key)

    def _file_key(self, file_path: str) -> tuple[str, str]:
        """Validate a project-relative path and derive its stable notice key."""
        target = Path(file_path).expanduser().resolve()
        try:
            relative = target.relative_to(self.project_root)
        except ValueError as exc:
            raise FileUseRegistryError(
                f"File is outside the shared project folder: {target}"
            ) from exc

        relative_path = relative.as_posix()
        if target.exists():
            # resolve() does not consistently return stored filename casing.
            # Canonicalize aliases on case-insensitive filesystems, while
            # retaining exact spellings for distinct case-sensitive files.
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
        """Return the directory containing notices for the given file key."""
        return self.project_root / ".openpypeline" / "file_use" / file_id

    @staticmethod
    def _parse_timestamp(
        value: str,
        metadata_path: Path,
    ) -> datetime:
        """Parse a timezone-aware notice timestamp and normalize it to UTC."""
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
        """Return all notices for a file, including stale ones."""
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
            # Treat future heartbeats as stale too; clock skew must not make
            # an implausibly recent notice appear to be a live session.
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
        """Atomically write this session's notice and update local state."""
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
        """Write this session's notice and return notices already observed."""
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
        """Refresh this session's notice while its file remains open."""
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
        """Remove this session's notice on file close or host exit."""
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
