"""Unit tests for the SideFX Houdini host adapter and file operations.

:File: test_adapter.py
:Host: SideFX Houdini
:Status: In Progress
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import unittest
from unittest.mock import MagicMock, patch

from tests.test_host_adapters import (
    REQUIRED_FILE_PROTOCOL,
    REQUIRED_LOADER_PROTOCOL,
)


class TestHoudiniFileHandlerProtocol(unittest.TestCase):
    """Verify that the Houdini file handler implements the required file protocol."""

    def test_houdini_file_handler_protocol(self) -> None:
        """Verify all required protocol methods exist and are callable in Houdini."""
        from openpypeline.app.houdini.file import file as hou_file

        for method_name in REQUIRED_FILE_PROTOCOL:
            self.assertTrue(
                hasattr(hou_file, method_name),
                f"Houdini file handler is missing required method: '{method_name}'",
            )
            self.assertTrue(callable(getattr(hou_file, method_name)))


class TestHoudiniLoaderProtocol(unittest.TestCase):
    """Verify that the Houdini loader implements the required loader protocol."""

    def test_houdini_loader_protocol(self) -> None:
        """Verify Houdini loader functions and shelf installer exist."""
        from openpypeline.app.houdini import loader as hou_loader

        for func_name in REQUIRED_LOADER_PROTOCOL:
            self.assertTrue(
                hasattr(hou_loader, func_name),
                f"Houdini loader is missing required function: '{func_name}'",
            )
            self.assertTrue(callable(getattr(hou_loader, func_name)))
        self.assertTrue(callable(getattr(hou_loader, "install_shelf", None)))


class TestHoudiniFileOperations(unittest.TestCase):
    """Test Houdini file operations with a mocked ``hou`` SDK.

    .. note::

       These tests validate that the Houdini file adapter methods delegate
       properly to ``hou.hipFile`` without performing disk I/O.
    """

    def setUp(self) -> None:
        """Patch ``sys.modules`` with a mock ``hou`` module."""
        self.mock_hou = MagicMock()
        self.hou_patcher = patch.dict("sys.modules", {"hou": self.mock_hou})
        self.hou_patcher.start()

        from openpypeline.app.houdini.file import file as hou_file

        self.hou_file = hou_file
        self._orig_hou = getattr(hou_file, "hou", None)
        hou_file.hou = self.mock_hou

    def tearDown(self) -> None:
        """Restore the original ``hou`` reference and stop module patching."""
        self.hou_file.hou = self._orig_hou
        self.hou_patcher.stop()

    def test_houdini_save_success(self) -> None:
        """Verify ``save()`` delegates to ``hou.hipFile.save()`` and returns ``True``."""
        result = self.hou_file.save()
        self.assertTrue(result)
        self.mock_hou.hipFile.save.assert_called_once()

    def test_houdini_new_file(self) -> None:
        """Verify ``new_file()`` clears the current Houdini scene."""
        result = self.hou_file.new_file()
        self.assertTrue(result)
        self.mock_hou.hipFile.clear.assert_called_once()

    def test_houdini_is_modified(self) -> None:
        """Verify ``is_modified()`` reflects ``hou.hipFile.hasUnsavedChanges()``."""
        self.mock_hou.hipFile.hasUnsavedChanges.return_value = True
        self.assertTrue(self.hou_file.is_modified())

    def test_houdini_file_type_and_workspace(self) -> None:
        """Verify extension mapping and workspace root resolution from ``hou.hipFile.path()``."""
        self.assertEqual(self.hou_file.get_file_type(".hip"), "Houdini Scene")
        self.assertEqual(self.hou_file.get_file_type(".HIP"), "Houdini Scene")
        self.mock_hou.hipFile.path.return_value = "/projects/my_shot/shot.hip"
        with patch("os.path.exists", return_value=True):
            self.assertEqual(self.hou_file.get_workspace_root(), "/projects/my_shot")


if __name__ == "__main__":
    unittest.main()
