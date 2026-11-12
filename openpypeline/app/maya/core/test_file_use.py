"""Focused tests for Maya file-use callback lifecycle behavior."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest

from openpypeline.core.file_use import FileUseRegistry


@pytest.fixture
def maya_file_use_module(monkeypatch):
    """Load Maya file-use callbacks against mocked Maya and Qt modules."""
    maya = ModuleType("maya")
    maya.__path__ = []
    maya.cmds = MagicMock()

    scene_message = SimpleNamespace(
        kAfterOpen=1,
        kAfterNew=2,
        kAfterSave=3,
        kBeforeOpenCheck=4,
        kBeforeSaveCheck=5,
        kMayaExiting=6,
        addCallback=MagicMock(side_effect=range(6)),
        addCheckFileCallback=MagicMock(side_effect=range(6, 12)),
        addCheckCallback=MagicMock(side_effect=range(12, 18)),
    )
    maya_api = ModuleType("maya.api")
    maya_api.OpenMaya = SimpleNamespace(
        MSceneMessage=scene_message,
        MMessage=SimpleNamespace(removeCallback=MagicMock()),
    )
    pyside = ModuleType("PySide6")
    timer = MagicMock()
    pyside.QtCore = SimpleNamespace(QTimer=MagicMock(return_value=timer))
    pyside.QtWidgets = MagicMock()
    monkeypatch.setitem(sys.modules, "maya", maya)
    monkeypatch.setitem(sys.modules, "maya.api", maya_api)
    monkeypatch.setitem(sys.modules, "PySide6", pyside)

    source = Path(__file__).with_name("file_use.py")
    spec = importlib.util.spec_from_file_location(
        "_openpypeline_test_maya_file_use",
        source,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module, timer


def test_install_callbacks_registers_scene_already_open(maya_file_use_module):
    """Register lifecycle callbacks and process a scene already open in Maya."""
    module, timer = maya_file_use_module
    module._after_open = MagicMock()

    module.install_callbacks()

    module._after_open.assert_called_once_with()
    timer.start.assert_called_once_with()
    assert len(module._callbacks) == 6


def test_save_as_outside_project_releases_old_notice(
    maya_file_use_module,
    monkeypatch,
    tmp_path,
):
    """Release the old project notice after saving to an external path."""
    module = maya_file_use_module[0]
    project = tmp_path / "project"
    project.mkdir()
    original_scene = project / "asset.ma"
    original_scene.touch()
    outside_scene = tmp_path / "external.ma"
    outside_scene.touch()
    registry = FileUseRegistry(str(project), "Artist A")
    registry.acquire(str(original_scene))
    module._registry = registry
    module._project_root = str(project.resolve())
    monkeypatch.setattr(module, "_get_registry", lambda: registry)
    monkeypatch.setattr(
        module,
        "_current_scene_path",
        lambda: str(outside_scene),
    )

    module._after_save()

    assert not registry.has_notice


def test_save_as_inside_project_moves_notice_to_saved_path(
    maya_file_use_module,
    monkeypatch,
    tmp_path,
):
    """Move the active notice from the old scene to an in-project Save As path."""
    module = maya_file_use_module[0]
    project = tmp_path / "project"
    project.mkdir()
    original_scene = project / "asset.ma"
    original_scene.touch()
    saved_scene = project / "asset_v002.ma"
    saved_scene.touch()
    registry = FileUseRegistry(str(project), "Artist A")
    observer = FileUseRegistry(str(project), "Artist B")
    registry.acquire(str(original_scene))
    module._registry = registry
    module._project_root = str(project.resolve())
    monkeypatch.setattr(module, "_get_registry", lambda: registry)
    monkeypatch.setattr(
        module,
        "_current_scene_path",
        lambda: str(saved_scene),
    )

    module._after_save()

    assert registry.list_notices(str(original_scene)) == []
    notices = observer.list_notices(str(saved_scene))
    assert [notice.user for notice in notices] == ["Artist A"]


def test_save_as_warns_after_saving_to_path_with_existing_notice(
    maya_file_use_module,
    monkeypatch,
    tmp_path,
):
    """Warn when Save As completes at a path already noticed by another session."""
    module = maya_file_use_module[0]
    project = tmp_path / "project"
    project.mkdir()
    saved_scene = project / "asset_v002.ma"
    saved_scene.touch()
    owner = FileUseRegistry(
        str(project),
        "Artist A",
        session_id="existing-session",
    )
    owner.acquire(str(saved_scene))
    current_session = FileUseRegistry(
        str(project),
        "Artist B",
        session_id="current-session",
    )
    observer = FileUseRegistry(
        str(project),
        "Observer",
        session_id="observer-session",
    )
    module._registry = current_session
    module._project_root = str(project.resolve())
    monkeypatch.setattr(module, "_get_registry", lambda: current_session)
    monkeypatch.setattr(module, "_current_scene_path", lambda: str(saved_scene))
    module.get_file_state = lambda _path: (1, 1)

    module._after_save()

    module.QtWidgets.QMessageBox.warning.assert_called_once()
    assert "The scene was saved" in module.QtWidgets.QMessageBox.warning.call_args.args[2]
    assert {
        notice.user for notice in observer.list_notices(str(saved_scene))
    } == {"Artist A", "Artist B"}
