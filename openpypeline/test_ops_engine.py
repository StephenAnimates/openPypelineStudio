"""Tests for host-adapter loading in the pipeline engine."""

import sys
from types import ModuleType
from unittest.mock import MagicMock

from openpypeline import ops_engine


def test_ops_engine_imports_host_adapter_from_package(monkeypatch):
    """Load the host-specific file adapter from the package namespace."""
    imported = []
    adapter = ModuleType("maya_file_adapter")
    maya = ModuleType("maya")
    maya_cmds = ModuleType("maya.cmds")
    monkeypatch.setitem(sys.modules, "maya", maya)
    monkeypatch.setitem(sys.modules, "maya.cmds", maya_cmds)

    def fake_import(module_path):
        """Record the adapter import and return its mocked module."""
        imported.append(module_path)
        return adapter

    monkeypatch.setattr(ops_engine.importlib, "import_module", fake_import)
    monkeypatch.setattr(ops_engine.importlib, "reload", lambda module: module)

    engine = ops_engine.OpsEngine()

    assert engine.host_app == "maya"
    assert imported == ["openpypeline.app.maya.file.file"]
    assert engine.file_handler is adapter


def test_workspace_root_uses_maya_workspace(monkeypatch, tmp_path):
    """Use Maya's workspace root when running inside Maya."""
    maya_cmds = ModuleType("maya.cmds")
    maya_cmds.workspace = lambda **_kwargs: str(tmp_path)
    monkeypatch.setattr(
        ops_engine.importlib,
        "import_module",
        lambda module_path: maya_cmds,
    )

    assert ops_engine._get_workspace_root("maya") == str(tmp_path)


def test_workspace_root_uses_current_directory_for_standalone(monkeypatch):
    """Use the process working directory outside a DCC host."""
    monkeypatch.setattr(ops_engine.os, "getcwd", lambda: "/workspace")

    assert ops_engine._get_workspace_root("standalone") == "/workspace"


def test_ui_diagnostics_do_not_open_scene(monkeypatch):
    """Keep diagnostic inventory logging from opening a scene file."""
    from openpypeline.core.file import inventory, master
    from openpypeline.core.notes import notes
    from openpypeline.core.util import prefs
    from openpypeline.core.version import Version

    monkeypatch.setattr(ops_engine.importlib, "reload", lambda module: module)
    monkeypatch.setattr(
        prefs,
        "get_pref",
        lambda key, default=None: {
            "ops_currProjectPath": "/project",
            "ops_currOpenTab": 2,
            "ops_currOpenLevel1": "characters",
            "ops_currOpenLevel2": "hero",
            "ops_currOpenLevel3": "model",
        }.get(key, default),
    )

    class InventoryStub:
        """Supply predictable inventory results to the diagnostic test."""
        def __init__(self, _elements):
            """Accept path elements without requiring a filesystem inventory."""
            pass

        def list(self):
            """Return the single item used by the diagnostic test."""
            return ["hero"]

        def getPath(self):
            """Return the fixture item's expected directory."""
            return "/project/lib/characters/hero/components/model"

    class VersionStub:
        """Provide deterministic WIP versions to the diagnostic test."""
        def all(self, _path):
            """Return the item's available version numbers."""
            return [1, 2]

    monkeypatch.setattr(inventory, "Inventory", InventoryStub)
    monkeypatch.setattr(Version, "Version", VersionStub)
    monkeypatch.setattr(master, "Master", lambda: MagicMock(query=lambda _path: 0))
    monkeypatch.setattr(notes, "Notes", lambda: MagicMock(query=lambda *_args: 0))
    file_handler = MagicMock()

    engine = ops_engine.OpsEngine()
    engine.file_handler = file_handler

    engine.ui()

    file_handler.open.assert_not_called()


def test_open_latest_workshop_opens_latest_version(monkeypatch):
    """Open the path resolved for the item's highest WIP version."""
    from openpypeline.core.file import wip
    from openpypeline.core.version import Version

    monkeypatch.setattr(
        Version,
        "Version",
        lambda: MagicMock(latest=lambda _path: 3),
    )
    monkeypatch.setattr(
        wip,
        "WIP",
        lambda: MagicMock(open=lambda *_args: "/project/hero/wip/hero_wip_0003.ma"),
    )
    handler = MagicMock()
    handler.open.return_value = True
    engine = ops_engine.OpsEngine()
    engine.file_handler = handler

    assert engine.open_latest_workshop("/project/hero", "hero") is True
    handler.open.assert_called_once_with("/project/hero/wip/hero_wip_0003.ma")
