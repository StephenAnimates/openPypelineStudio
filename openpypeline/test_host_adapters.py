"""Unit tests for DCC host adapters and standard loader/file interfaces.

This module validates protocol compliance across Maya, Houdini, and Nuke adapters using test doubles.

TODO: relocate the functions in the integrations for each host to their own test modules, and add more comprehensive tests for file operations and loader functionality. The test host adpaters need to be refactored to use pytest fixtures and parametrization for better maintainability and coverage.

:File: test_host_adapters.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import sys
import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch

REQUIRED_FILE_PROTOCOL = [
    "open",
    "save",
    "save_as",
    "import_file",
    "reference_file",
    "new_file",
    "export_file",
    "is_modified",
    "get_file_type",
    "get_workspace_root",
]

REQUIRED_LOADER_PROTOCOL = [
    "openPypeline",
    "openPypelineSetup",
]

class TestHostFileHandlerProtocol(unittest.TestCase):
    """Verify that every DCC adapter implements the standardized file handler protocol.
    
    :raises AssertionError: If any required method is missing or not callable in a host adapter.
    :returns: None

    .. warning::
        This test suite checks for the presence of required methods in each host's file adapter module. It does not execute the methods, only verifies their existence and callability.
    """

    def test_maya_file_handler_protocol(self):
        # Mock maya.cmds for headless testing
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

    def test_houdini_file_handler_protocol(self):
        """Verify that the Houdini file handler implements the required file operations protocol.
        TODO: Move this function to the apps integration. Expand this test to include more comprehensive checks for Houdini file operations, including error handling and edge cases.

        :raises AssertionError: If any required method is missing or not callable in the Houdini file adapter.
        :returns: None

        .. warning::
            This test checks for the presence of required methods in the Houdini file adapter module. It does not execute the methods, only verifies their existence and callability.
        """
        from openpypeline.app.houdini.file import file as hou_file
        for method_name in REQUIRED_FILE_PROTOCOL:
            self.assertTrue(
                hasattr(hou_file, method_name),
                f"Houdini file handler is missing required method: '{method_name}'",
            )
            self.assertTrue(callable(getattr(hou_file, method_name)))

    def test_nuke_file_handler_protocol(self):
        """Verify that the Nuke file handler implements the required file operations protocol.
        TODO: Move this function to the apps integration. Expand this test to include more comprehensive checks for Nuke file operations, including error handling and edge cases.

        :raises AssertionError: If any required method is missing or not callable in the Nuke file adapter.
        :returns: None

        .. warning::
            This test checks for the presence of required methods in the Nuke file adapter module. It does not execute the methods, only verifies their existence and callability.
        """
        from openpypeline.app.nuke.file import file as nuke_file
        for method_name in REQUIRED_FILE_PROTOCOL:
            self.assertTrue(
                hasattr(nuke_file, method_name),
                f"Nuke file handler is missing required method: '{method_name}'",
            )
            self.assertTrue(callable(getattr(nuke_file, method_name)))


class TestHostLoaderProtocol(unittest.TestCase):
    """Verify that every DCC adapter implements the standardized loader protocol.
    TODO: can this be used to call the different app integrations from there respective folders?

    :raises AssertionError: If any required method is missing or not callable in a host loader.
    :returns: None

    .. warning::
        This test suite checks for the presence of required methods in each host's loader module. It does not execute the methods, only verifies their existence and callability.
    """

    def test_maya_loader_protocol(self):
        """
        Mock PySide6 and maya.cmds for headless testing
        """
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

    def test_houdini_loader_protocol(self):
        """
        test for Houdini loader
        """
        from openpypeline.app.houdini import loader as hou_loader
        for func_name in REQUIRED_LOADER_PROTOCOL:
            self.assertTrue(
                hasattr(hou_loader, func_name),
                f"Houdini loader is missing required function: '{func_name}'",
            )
            self.assertTrue(callable(getattr(hou_loader, func_name)))
            self.assertTrue(hasattr(hou_loader, "install_shelf"))

    def test_nuke_loader_protocol(self):
        """
        test for Nuke loader
        """
        from openpypeline.app.nuke import loader as nuke_loader
        for func_name in REQUIRED_LOADER_PROTOCOL:
            self.assertTrue(
                hasattr(nuke_loader, func_name),
                f"Nuke loader is missing required function: '{func_name}'",
            )
            self.assertTrue(callable(getattr(nuke_loader, func_name)))
            self.assertTrue(hasattr(nuke_loader, "install_menu"))


class TestHoudiniFileOperations(unittest.TestCase):
    """Test Houdini file operations with a mocked hou SDK.
    TODO: Move the class to the Houdini integration directory. Expand tests to verify that the OpsEngine correctly interacts with the Houdini file adapter, including opening, saving, and creating new files.
    
    .. warning::
        These tests validate that the Houdini file adapter methods exist and can be called without raising exceptions. They do not perform actual file operations.
    """

    def setUp(self):
        """
        setUp
        """
        self.mock_hou = MagicMock()
        self.hou_patcher = patch.dict("sys.modules", {"hou": self.mock_hou})
        self.hou_patcher.start()

    def tearDown(self):
        """
        Teardown
        """
        self.hou_patcher.stop()

    def test_houdini_save_success(self):
        """
        Test Save
        """
        from openpypeline.app.houdini.file import file as hou_file
        hou_file.hou = self.mock_hou
        result = hou_file.save()
        self.assertTrue(result)
        self.mock_hou.hipFile.save.assert_called_once()

    def test_houdini_new_file(self):
        """
        Test Houdini New File
        """
        from openpypeline.app.houdini.file import file as hou_file
        hou_file.hou = self.mock_hou
        result = hou_file.new_file()
        self.assertTrue(result)
        self.mock_hou.hipFile.clear.assert_called_once()

    def test_houdini_is_modified(self):
        from openpypeline.app.houdini.file import file as hou_file
        hou_file.hou = self.mock_hou
        self.mock_hou.hipFile.hasUnsavedChanges.return_value = True
        self.assertTrue(hou_file.is_modified())

    def test_houdini_file_type_and_workspace(self):
        from openpypeline.app.houdini.file import file as hou_file
        hou_file.hou = self.mock_hou
        self.assertEqual(hou_file.get_file_type(".hip"), "Houdini Scene")
        self.assertEqual(hou_file.get_file_type(".HIP"), "Houdini Scene")
        self.mock_hou.hipFile.path.return_value = "/projects/my_shot/shot.hip"
        with patch("os.path.exists", return_value=True):
            self.assertEqual(hou_file.get_workspace_root(), "/projects/my_shot")


class TestNukeFileOperations(unittest.TestCase):
    """Test Nuke file operations with a mocked nuke SDK.
    
    .. warning::
        These tests validate that the Nuke file adapter methods exist and can be called without raising exceptions. They do not perform actual file operations.
    """

    def setUp(self):
        self.mock_nuke = MagicMock()
        self.nuke_patcher = patch.dict("sys.modules", {"nuke": self.mock_nuke})
        self.nuke_patcher.start()

    def tearDown(self):
        self.nuke_patcher.stop()

    def test_nuke_save_success(self):
        from openpypeline.app.nuke.file import file as nuke_file
        nuke_file.nuke = self.mock_nuke
        result = nuke_file.save()
        self.assertTrue(result)
        self.mock_nuke.scriptSave.assert_called_once()

    def test_nuke_new_file(self):
        from openpypeline.app.nuke.file import file as nuke_file
        nuke_file.nuke = self.mock_nuke
        result = nuke_file.new_file()
        self.assertTrue(result)
        self.mock_nuke.scriptClear.assert_called_once()

    def test_nuke_is_modified(self):
        from openpypeline.app.nuke.file import file as nuke_file
        nuke_file.nuke = self.mock_nuke
        self.mock_nuke.root.return_value.modified.return_value = False
        self.assertFalse(nuke_file.is_modified())

    def test_nuke_file_type_and_workspace(self):
        from openpypeline.app.nuke.file import file as nuke_file
        nuke_file.nuke = self.mock_nuke
        self.assertEqual(nuke_file.get_file_type(".nk"), "Nuke Script")
        self.mock_nuke.root.return_value.name.return_value = "/projects/comp/comp_v01.nk"
        with patch("os.path.exists", return_value=True):
            self.assertEqual(nuke_file.get_workspace_root(), "/projects/comp")


if __name__ == "__main__":
    unittest.main()
