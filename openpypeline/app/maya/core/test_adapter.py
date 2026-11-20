"""Unit tests for the Autodesk Maya host adapter and file operations.

:File: test_adapter.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch

from tests.test_host_adapters import (
    REQUIRED_FILE_PROTOCOL,
    REQUIRED_LOADER_PROTOCOL,
)


class TestMayaFileHandlerProtocol(unittest.TestCase):
    """Verify that the Maya file handler implements the required file protocol."""

    def test_maya_file_handler_protocol(self) -> None:
        """Verify all required protocol methods exist and are callable in Maya."""
        mock_maya = ModuleType("maya")
        mock_cmds = ModuleType("maya.cmds")
        with patch.dict("sys.modules", {"maya": mock_maya, "maya.cmds": mock_cmds}):
            from openpypeline.app.maya.file import file as maya_file

            for method_name in REQUIRED_FILE_PROTOCOL:
                self.assertTrue(
                    hasattr(maya_file, method_name),
                    f"Maya file handler is missing required method: '{method_name}'",
                )
                self.assertTrue(callable(getattr(maya_file, method_name)))


class TestMayaLoaderProtocol(unittest.TestCase):
    """Verify that the Maya loader implements the required loader protocol."""

    def test_maya_loader_protocol(self) -> None:
        """Mock PySide6 and maya.cmds to verify Maya loader entry points."""
        mock_pyside = ModuleType("PySide6")
        mock_widgets = MagicMock()
        mock_core = MagicMock()
        mock_pyside.QtWidgets = mock_widgets
        mock_pyside.QtCore = mock_core
        mock_maya = ModuleType("maya")
        mock_cmds = ModuleType("maya.cmds")

        with patch.dict(
            "sys.modules",
            {
                "PySide6": mock_pyside,
                "PySide6.QtWidgets": mock_widgets,
                "PySide6.QtCore": mock_core,
                "maya": mock_maya,
                "maya.cmds": mock_cmds,
            },
        ):
            from openpypeline.app.maya import loader as maya_loader

            for func_name in REQUIRED_LOADER_PROTOCOL:
                self.assertTrue(
                    hasattr(maya_loader, func_name),
                    f"Maya loader is missing required function: '{func_name}'",
                )
                self.assertTrue(callable(getattr(maya_loader, func_name)))


class TestMayaFileOperations(unittest.TestCase):
    """Test Maya file operations with a mocked ``maya.cmds`` SDK.

    .. note::

       These tests validate that the Maya file adapter methods delegate
       properly to ``maya.cmds`` without performing disk I/O.
    """

    def setUp(self) -> None:
        """Patch ``sys.modules`` with mock ``maya`` and ``maya.cmds`` modules."""
        self.mock_maya = ModuleType("maya")
        self.mock_cmds = MagicMock()
        self.mock_maya.cmds = self.mock_cmds
        self.maya_patcher = patch.dict(
            "sys.modules",
            {"maya": self.mock_maya, "maya.cmds": self.mock_cmds},
        )
        self.maya_patcher.start()

        from openpypeline.app.maya.file import file as maya_file

        self.maya_file = maya_file
        self._orig_cmds = getattr(maya_file, "cmds", None)
        maya_file.cmds = self.mock_cmds

    def tearDown(self) -> None:
        """Restore the original ``cmds`` reference and stop module patching."""
        self.maya_file.cmds = self._orig_cmds
        self.maya_patcher.stop()

    def test_maya_save_success(self) -> None:
        """Verify ``save()`` delegates to ``cmds.file(save=True)`` and returns ``True``."""
        result = self.maya_file.save()
        self.assertTrue(result)
        self.mock_cmds.file.assert_called_once_with(save=True)

    def test_maya_new_file(self) -> None:
        """Verify ``new_file()`` delegates to ``cmds.file(force=True, newFile=True)``."""
        result = self.maya_file.new_file()
        self.assertTrue(result)
        self.mock_cmds.file.assert_called_once_with(force=True, newFile=True)

    def test_maya_is_modified(self) -> None:
        """Verify ``is_modified()`` reflects ``cmds.file(query=True, modified=True)``."""
        self.mock_cmds.file.return_value = True
        self.assertTrue(self.maya_file.is_modified())
        self.mock_cmds.file.assert_called_once_with(query=True, modified=True)

    def test_maya_file_type_and_workspace(self) -> None:
        """Verify extension mapping and workspace root resolution from ``cmds.workspace``."""
        self.assertEqual(self.maya_file.get_file_type(".ma"), "mayaAscii")
        self.assertEqual(self.maya_file.get_file_type(".mb"), "mayaBinary")
        self.assertEqual(self.maya_file.get_file_type(".ABC"), "Alembic")
        self.mock_cmds.workspace.return_value = "/projects/my_shot"
        self.assertEqual(self.maya_file.get_workspace_root(), "/projects/my_shot")


if __name__ == "__main__":
    unittest.main()
