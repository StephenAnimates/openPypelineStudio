"""Tests for host-adapter loading and routing in the pipeline engine.

Verifies that :class:`~openpypeline.ops_engine.OpsEngine` detects active DCC hosts, imports and assigns the matching host file adapter, resolves workspace roots, executes headless UI diagnostics safely, and delegates scene operations to its active file handler.

:File: test_ops_engine.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import os
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import MagicMock, patch

from openpypeline import ops_engine


class TestOpsEngine(unittest.TestCase):
    """Unit tests covering host detection, workspace resolution, and file routing."""

    def test_ops_engine_imports_maya_adapter_from_package(self) -> None:
        """Import and assign ``openpypeline.app.maya.file.file`` when Maya is active."""
        imported: list[str] = []
        adapter = ModuleType("maya_file_adapter")
        adapter.open = MagicMock(return_value=True)
        adapter.save = MagicMock(return_value=True)

        fake_modules = {
            "maya": ModuleType("maya"),
            "maya.cmds": ModuleType("maya.cmds"),
        }

        def fake_import(module_path: str) -> ModuleType:
            imported.append(module_path)
            return adapter

        with (
            patch.dict(sys.modules, fake_modules),
            patch.object(ops_engine.importlib, "import_module", side_effect=fake_import),
            patch.object(ops_engine.importlib, "reload", side_effect=lambda mod: mod),
        ):
            engine = ops_engine.OpsEngine()

        self.assertEqual(engine.host_app, "maya")
        self.assertEqual(imported, ["openpypeline.app.maya.file.file"])
        self.assertIs(engine.file_handler, adapter)
        self.assertTrue(engine.file_handler.open("/project/hero/wip/hero_wip_0001.ma"))
        adapter.open.assert_called_once_with("/project/hero/wip/hero_wip_0001.ma")

    def test_ops_engine_falls_back_to_standalone_without_dcc_modules(self) -> None:
        """Detect ``standalone`` and leave ``file_handler`` unset when no DCC is present."""
        dcc_names = ("maya", "maya.cmds", "hou", "nuke", "bpy", "unreal")
        clean_modules = {
            k: v for k, v in sys.modules.items() if k not in dcc_names
        }
        with patch.dict(sys.modules, clean_modules, clear=True):
            engine = ops_engine.OpsEngine()

        self.assertEqual(engine.host_app, "standalone")
        self.assertIsNone(engine.file_handler)


    def test_ops_engine_handles_missing_host_adapter_gracefully(self) -> None:
        """Handle ``ImportError`` cleanly when a detected host lacks an adapter module."""
        fake_modules = {
            "maya": ModuleType("maya"),
            "maya.cmds": ModuleType("maya.cmds"),
        }
        with (
            patch.dict(sys.modules, fake_modules),
            patch.object(
                ops_engine.importlib,
                "import_module",
                side_effect=ImportError("No adapter"),
            ),
        ):
            engine = ops_engine.OpsEngine()

        self.assertEqual(engine.host_app, "maya")
        self.assertIsNone(engine.file_handler)

    def test_workspace_root_uses_maya_workspace(self) -> None:
        """Resolve the workspace root from ``maya.cmds.workspace`` inside Maya."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            maya_cmds = ModuleType("maya.cmds")
            maya_cmds.workspace = lambda **_kwargs: tmp_dir

            with patch.object(
                ops_engine.importlib,
                "import_module",
                return_value=maya_cmds,
            ):
                resolved = ops_engine._get_workspace_root("maya")

            self.assertEqual(resolved, tmp_dir)

    def test_workspace_root_uses_current_directory_for_standalone(self) -> None:
        """Fall back to ``os.getcwd()`` when running outside a DCC host."""
        with patch.object(ops_engine.os, "getcwd", return_value="/workspace"):
            self.assertEqual(
                ops_engine._get_workspace_root("standalone"),
                "/workspace",
            )

    def test_ui_diagnostics_do_not_open_scene(self) -> None:
        """Run headless diagnostic inventory logging without invoking ``file_handler.open``."""
        from openpypeline.core.file import inventory, master
        from openpypeline.core.notes import notes
        from openpypeline.core.util import prefs
        from openpypeline.core.version import Version

        pref_values = {
            "ops_currProjectPath": "/project",
            "ops_currOpenTab": 2,
            "ops_currOpenLevel1": "characters",
            "ops_currOpenLevel2": "hero",
            "ops_currOpenLevel3": "model",
        }

        class InventoryStub:
            """Supply deterministic multi-item inventory results for diagnostic runs."""

            def __init__(self, elements: list[object]) -> None:
                self.elements = elements

            def list(self) -> list[str]:
                return ["hero", "sidekick"]

            def getPath(self) -> str:
                item_name = self.elements[-1] if self.elements else "hero"
                return f"/project/lib/characters/{item_name}/components/model"

        class VersionStub:
            """Supply deterministic WIP version numbers."""

            def all(self, _path: str) -> list[int]:
                return [1, 2]

        file_handler = MagicMock()

        with (
            patch.object(ops_engine.importlib, "reload", side_effect=lambda mod: mod),
            patch.object(
                prefs,
                "get_pref",
                side_effect=lambda key, default=None: pref_values.get(key, default),
            ),
            patch.object(inventory, "Inventory", InventoryStub),
            patch.object(Version, "Version", VersionStub),
            patch.object(
                master,
                "Master",
                return_value=MagicMock(query=lambda _path: 1),
            ),
            patch.object(
                notes,
                "Notes",
                return_value=MagicMock(query=lambda *_args: 0),
            ),
        ):
            engine = ops_engine.OpsEngine()
            engine.file_handler = file_handler
            engine.ui()

        file_handler.open.assert_not_called()

    def test_open_latest_workshop_opens_latest_version(self) -> None:
        """Resolve the highest WIP version path and open it via ``file_handler``."""
        from openpypeline.core.file import wip
        from openpypeline.core.version import Version

        wip_path = os.path.join("/project", "hero", "wip", "hero_wip_0003.ma")
        handler = MagicMock()
        handler.open.return_value = True

        with (
            patch.object(
                Version,
                "Version",
                return_value=MagicMock(latest=lambda _path: 3),
            ),
            patch.object(
                wip,
                "WIP",
                return_value=MagicMock(open=lambda *_args: wip_path),
            ),
        ):
            engine = ops_engine.OpsEngine()
            engine.file_handler = handler
            result = engine.open_latest_workshop("/project/hero", "hero")

        self.assertTrue(result)
        handler.open.assert_called_once_with(wip_path)

    def test_open_latest_workshop_returns_false_when_no_versions_exist(self) -> None:
        """Return ``False`` without calling ``file_handler.open`` when latest version is ``0``."""
        from openpypeline.core.version import Version

        handler = MagicMock()
        with patch.object(
            Version,
            "Version",
            return_value=MagicMock(latest=lambda _path: 0),
        ):
            engine = ops_engine.OpsEngine()
            engine.file_handler = handler
            result = engine.open_latest_workshop("/project/hero", "hero")

        self.assertFalse(result)
        handler.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
