"""Tests for local project creation and shared-project onboarding."""

import json

import pytest

from openpypeline.core import ops_actions, ops_project
from openpypeline.core.models import ProjectConfig


@pytest.fixture
def local_registry(tmp_path, monkeypatch):
    """Provide an isolated registry path and local preference store."""
    registry_path = tmp_path / "artist" / "openpypeline_projects.json"
    preference_values = {}
    monkeypatch.setattr(ops_project, "get_proj_file", lambda: str(registry_path))
    monkeypatch.setattr(
        ops_actions.prefs,
        "get_pref",
        lambda key, default=None: preference_values.get(key, default),
    )
    monkeypatch.setattr(
        ops_actions.prefs,
        "set_pref",
        lambda key, value: preference_values.__setitem__(key, value),
    )
    return registry_path, preference_values


def _project_config(name, path, **changes):
    """Build project settings with the production defaults."""
    return ProjectConfig(name=name, path=str(path), **changes)


def test_create_writes_shared_manifest_and_machine_local_registration(
    local_registry,
    tmp_path,
):
    """Creation stores shared settings in the project and the local root in the registry."""
    registry_path, preferences = local_registry
    root = tmp_path / "shared" / "DemoProject"

    assert ops_actions.create_or_edit_project(
        0,
        "",
        _project_config("DemoProject", root),
    ) == 1

    manifest_path = root / ".openpypeline" / "project.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    registered_projects = json.loads(registry_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == ops_project.PROJECT_MANIFEST_SCHEMA_VERSION
    assert manifest["project"]["name"] == "DemoProject"
    assert "path" not in manifest["project"]
    assert registered_projects[0]["path"] == str(root)
    assert registered_projects[0]["project_id"] == manifest["project_id"]
    assert (root / "scenes").is_dir()
    assert preferences["ops_currProjectName"] == "DemoProject"
    assert preferences["ops_currProjectPath"] == str(root)


def test_edit_preserves_manifest_identity_and_updates_shared_settings(
    local_registry,
    tmp_path,
):
    """Editing a registered project keeps its stable ID and refreshes the manifest."""
    registry_path, _ = local_registry
    root = tmp_path / "shared" / "DemoProject"
    original = _project_config("DemoProject", root)
    ops_actions.create_or_edit_project(0, "", original)
    original_id = json.loads(
        (root / ".openpypeline" / "project.json").read_text(encoding="utf-8")
    )["project_id"]

    edited = _project_config("DemoProject", root, description="Shared team project")
    assert ops_actions.create_or_edit_project(1, "DemoProject", edited) == 1

    manifest = json.loads(
        (root / ".openpypeline" / "project.json").read_text(encoding="utf-8")
    )
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert manifest["project_id"] == original_id
    assert manifest["project"]["description"] == "Shared team project"
    assert registry[0]["project_id"] == original_id


def test_join_registers_artist_local_root_without_recreating_shared_folders(
    local_registry,
    tmp_path,
):
    """Joining a synced copy only registers its local path and preserves shared files."""
    registry_path, preferences = local_registry
    source_root = tmp_path / "source" / "DemoProject"
    ops_actions.create_or_edit_project(
        0,
        "",
        _project_config("DemoProject", source_root),
    )

    synced_root = tmp_path / "artist-two" / "DemoProject"
    manifest_directory = synced_root / ".openpypeline"
    manifest_directory.mkdir(parents=True)
    (manifest_directory / "project.json").write_bytes(
        (source_root / ".openpypeline" / "project.json").read_bytes()
    )
    registry_path.unlink()

    assert ops_actions.join_existing_project(str(synced_root)) == 1
    assert ops_actions.join_existing_project(str(synced_root)) == 1

    registered_projects = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registered_projects) == 1
    assert registered_projects[0]["path"] == str(synced_root)
    assert not (synced_root / "scenes").exists()
    assert preferences["ops_currProjectName"] == "DemoProject"
    assert preferences["ops_currProjectPath"] == str(synced_root)


def test_join_rejects_missing_manifest_and_create_rejects_escaping_folder(
    local_registry,
    tmp_path,
):
    """Invalid onboarding inputs do not create or register projects."""
    _, _ = local_registry
    root = tmp_path / "without-manifest"
    root.mkdir()
    with pytest.raises(ops_actions.ProjectActionError, match="manifest"):
        ops_actions.join_existing_project(str(root))

    config = _project_config(
        "UnsafeProject",
        tmp_path / "unsafe",
        scenesfolder="../outside",
    )
    with pytest.raises(ops_actions.ProjectActionError, match="escape"):
        ops_actions.create_or_edit_project(0, "", config)
    assert not (tmp_path / "outside").exists()


def test_join_rejects_manifest_with_unsupported_schema(local_registry, tmp_path):
    """A manifest version the application cannot interpret is not registered."""
    _, _ = local_registry
    root = tmp_path / "unsupported"
    manifest_directory = root / ".openpypeline"
    manifest_directory.mkdir(parents=True)
    (manifest_directory / "project.json").write_text(
        json.dumps(
            {
                "schema_version": 99,
                "project_id": "project-id",
                "project": {"name": "Unsupported"},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ops_actions.ProjectActionError, match="Unsupported"):
        ops_actions.join_existing_project(str(root))


def test_create_does_not_replace_a_corrupt_local_registry(local_registry, tmp_path):
    """A malformed registry is reported without replacing its existing bytes."""
    registry_path, _ = local_registry
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text("{not valid json", encoding="utf-8")
    root = tmp_path / "new-project"

    with pytest.raises(ops_actions.ProjectActionError, match="local project registry"):
        ops_actions.create_or_edit_project(
            0,
            "",
            _project_config("NewProject", root),
        )

    assert registry_path.read_text(encoding="utf-8") == "{not valid json"
    assert not root.exists()
