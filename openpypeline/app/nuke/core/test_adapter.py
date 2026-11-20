"""Unit tests for the Foundry Nuke host adapter and file operations.

:File: test_adapter.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import unittest
from unittest.mock import MagicMock, patch

from tests.test_host_adapters import (
    REQUIRED_FILE_PROTOCOL,
    REQUIRED_LOADER_PROTOCOL,
)


class TestNukeFileHandlerProtocol(unittest.TestCase):
    """Verify that the Nuke file handler implements the required file protocol."""

    def test_nuke_file_handler_protocol(self) -> None:
        """Verify all required protocol methods exist and are callable in Nuke."""
        from openpypeline.app.nuke.file import file as nuke_file

        for method_name in REQUIRED_FILE_PROTOCOL:
            self.assertTrue(
                hasattr(nuke_file, method_name),
                f"Nuke file handler is missing required method: '{method_name}'",
            )
            self.assertTrue(callable(getattr(nuke_file, method_name)))


class TestNukeLoaderProtocol(unittest.TestCase):
    """Verify that the Nuke loader implements the required loader protocol."""

    def test_nuke_loader_protocol(self) -> None:
        """Verify Nuke loader functions and menu installer exist."""
        from openpypeline.app.nuke import loader as nuke_loader

        for func_name in REQUIRED_LOADER_PROTOCOL:
            self.assertTrue(
                hasattr(nuke_loader, func_name),
                f"Nuke loader is missing required function: '{func_name}'",
            )
            self.assertTrue(callable(getattr(nuke_loader, func_name)))
        self.assertTrue(callable(getattr(nuke_loader, "install_menu", None)))


class TestNukeFileOperations(unittest.TestCase):
    """Test Nuke file operations with a mocked ``nuke`` SDK.

    .. note::

       These tests validate that the Nuke file adapter methods delegate
       properly to ``nuke`` script functions without performing disk I/O.
    """

    def setUp(self) -> None:
        """Patch ``sys.modules`` with a mock ``nuke`` module."""
        self.mock_nuke = MagicMock()
        self.nuke_patcher = patch.dict("sys.modules", {"nuke": self.mock_nuke})
        self.nuke_patcher.start()

        from openpypeline.app.nuke.file import file as nuke_file

        self.nuke_file = nuke_file
        self._orig_nuke = getattr(nuke_file, "nuke", None)
        nuke_file.nuke = self.mock_nuke

    def tearDown(self) -> None:
        """Restore the original ``nuke`` reference and stop module patching."""
        self.nuke_file.nuke = self._orig_nuke
        self.nuke_patcher.stop()

    def test_nuke_save_success(self) -> None:
        """Verify ``save()`` delegates to ``nuke.scriptSave()`` and returns ``True``."""
        result = self.nuke_file.save()
        self.assertTrue(result)
        self.mock_nuke.scriptSave.assert_called_once()

    def test_nuke_new_file(self) -> None:
        """Verify ``new_file()`` clears the current Nuke script."""
        result = self.nuke_file.new_file()
        self.assertTrue(result)
        self.mock_nuke.scriptClear.assert_called_once()

    def test_nuke_is_modified(self) -> None:
        """Verify ``is_modified()`` reflects ``nuke.root().modified()``."""
        self.mock_nuke.root.return_value.modified.return_value = False
        self.assertFalse(self.nuke_file.is_modified())

    def test_nuke_file_type_and_workspace(self) -> None:
        """Verify extension mapping and workspace root resolution from ``nuke.root().name()``."""
        self.assertEqual(self.nuke_file.get_file_type(".nk"), "Nuke Script")
        self.mock_nuke.root.return_value.name.return_value = "/projects/comp/comp_v01.nk"
        with patch("os.path.exists", return_value=True):
            self.assertEqual(self.nuke_file.get_workspace_root(), "/projects/comp")


if __name__ == "__main__":
    unittest.main()
