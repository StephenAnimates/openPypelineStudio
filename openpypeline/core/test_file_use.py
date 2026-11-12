import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from openpypeline.core.file_use import (
    FileUseRegistry,
    FileUseRegistryError,
    get_file_state,
)


def test_file_state_detects_modification_and_missing_file(tmp_path):
    """Detect changed file metadata and return no state after deletion."""
    scene = tmp_path / "asset.ma"
    scene.write_bytes(b"scene")
    original_state = get_file_state(str(scene))

    scene.write_bytes(b"other")
    modified_time = scene.stat().st_mtime_ns + 1_000_000_000
    os.utime(scene, ns=(modified_time, modified_time))

    assert get_file_state(str(scene)) != original_state
    scene.unlink()
    assert get_file_state(str(scene)) is None


def test_file_use_notice_is_visible_to_another_session(tmp_path):
    """Expose one artist's project-relative notice to another session."""
    project = tmp_path / "project"
    project.mkdir()
    scene = project / "scenes" / "asset.ma"
    scene.parent.mkdir()
    scene.touch()

    artist_a = FileUseRegistry(
        str(project),
        "Artist A",
        machine="workstation-a",
    )
    artist_b = FileUseRegistry(
        str(project),
        "Artist B",
        machine="workstation-b",
    )

    assert artist_a.acquire(str(scene)) == []
    notices = artist_b.list_notices(str(scene))

    assert len(notices) == 1
    assert notices[0].user == "Artist A"
    assert notices[0].machine == "workstation-a"
    assert notices[0].file_path == "scenes/asset.ma"
    assert notices[0].stale is False


def test_release_removes_only_the_current_session_notice(tmp_path):
    """Remove only the releasing registry's notice for a shared file."""
    project = tmp_path / "project"
    project.mkdir()
    scene = project / "asset.ma"
    scene.touch()

    artist_a = FileUseRegistry(str(project), "Artist A")
    artist_b = FileUseRegistry(str(project), "Artist B")
    artist_a.acquire(str(scene))
    artist_b.acquire(str(scene))

    artist_a.release()

    remaining = artist_a.list_notices(str(scene))
    assert [notice.user for notice in remaining] == ["Artist B"]


def test_heartbeat_keeps_notice_visible_and_release_clears_state(tmp_path):
    """Refresh a notice for observers and clear local state on release."""
    project = tmp_path / "project"
    project.mkdir()
    scene = project / "asset.ma"
    scene.touch()
    owner = FileUseRegistry(str(project), "Artist A")
    observer = FileUseRegistry(str(project), "Artist B")

    owner.acquire(str(scene))
    owner.heartbeat()

    assert owner.has_notice
    assert len(observer.list_notices(str(scene))) == 1
    owner.release()
    assert not owner.has_notice


def test_heartbeat_recreates_a_notice_removed_by_sync(tmp_path):
    """Recreate this session's notice when synchronization removes it."""
    project = tmp_path / "project"
    project.mkdir()
    scene = project / "asset.ma"
    scene.touch()
    owner = FileUseRegistry(str(project), "Artist A")
    observer = FileUseRegistry(str(project), "Artist B")

    owner.acquire(str(scene))
    assert owner._lock_path is not None
    owner._lock_path.unlink()

    owner.heartbeat()

    assert owner._lock_path.exists()
    assert len(observer.list_notices(str(scene))) == 1


def test_case_distinct_files_have_independent_notices_when_supported(tmp_path):
    """Keep notices distinct for case-different files on case-sensitive disks."""
    project = tmp_path / "project"
    project.mkdir()
    lower_case_scene = project / "asset.ma"
    upper_case_scene = project / "Asset.ma"
    lower_case_scene.touch()
    upper_case_scene.touch()

    owner = FileUseRegistry(str(project), "Artist A")
    observer = FileUseRegistry(str(project), "Artist B")
    owner.acquire(str(lower_case_scene))

    notices = observer.list_notices(str(upper_case_scene))
    if lower_case_scene.samefile(upper_case_scene):
        assert [notice.user for notice in notices] == ["Artist A"]
    else:
        assert notices == []


def test_old_notice_is_reported_as_stale_not_silently_removed(tmp_path):
    """Report expired notices as stale without deleting their metadata."""
    project = tmp_path / "project"
    project.mkdir()
    scene = project / "asset.ma"
    scene.touch()

    owner = FileUseRegistry(str(project), "Artist A", session_id="old-session")
    observer = FileUseRegistry(
        str(project),
        "Artist B",
        session_id="new-session",
    )
    owner.acquire(str(scene))
    metadata_path = owner._lock_path
    assert metadata_path is not None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    old_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    metadata["heartbeat_at"] = old_time
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    notices = observer.list_notices(str(scene))

    assert len(notices) == 1
    assert notices[0].stale is True
    assert metadata_path.exists()


def test_file_outside_project_is_rejected(tmp_path):
    """Reject attempts to acquire a notice for a file outside the project."""
    project = tmp_path / "project"
    project.mkdir()
    outside_file = tmp_path / "outside.ma"
    outside_file.touch()
    registry = FileUseRegistry(str(project), "Artist A")

    with pytest.raises(
        FileUseRegistryError,
        match="outside the shared project folder",
    ):
        registry.acquire(str(outside_file))


def test_corrupt_notice_fails_closed(tmp_path):
    """Raise a registry error rather than ignoring malformed notice data."""
    project = tmp_path / "project"
    project.mkdir()
    scene = project / "asset.ma"
    scene.touch()
    owner = FileUseRegistry(str(project), "Artist A", session_id="owner")
    observer = FileUseRegistry(str(project), "Artist B", session_id="observer")
    owner.acquire(str(scene))
    assert owner._lock_path is not None
    owner._lock_path.write_text("{", encoding="utf-8")

    with pytest.raises(
        FileUseRegistryError,
        match="Could not read file-use notice",
    ):
        observer.list_notices(str(scene))
