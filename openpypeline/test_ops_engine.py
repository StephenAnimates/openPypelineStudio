"""Tests for host-adapter loading in the pipeline engine.

TODO: These tests should be expanded to verify that the OpsEngine correctly imports and assigns the appropriate host adapter based on the detected host application, and that the file handler is functional within the OpsEngine instance.

:File: test_ops_engine.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import sys
from types import ModuleType
from unittest.mock import MagicMock

from openpypeline import ops_engine


def test_ops_engine_imports_host_adapter_from_package(monkeypatch: MagicMock):
    """Test that the OpsEngine correctly imports the host-specific file adapter from the package namespace.
    TODO: This test should be expanded to verify that the correct host adapter is imported based on the detected host application, and that the file handler is assigned properly within the OpsEngine instance.
    
    Loads the host-specific file adapter from the package namespace.

    :param monkeypatch: A pytest fixture for safely modifying the import system.
    :type monkeypatch: pytest.MonkeyPatch
    :returns: None
    :raises AssertionError: If the host adapter is not imported or assigned correctly.
    """
    imported = []
    adapter = ModuleType("maya_file_adapter")
    maya = ModuleType("maya")
    maya_cmds = ModuleType("maya.cmds")
    monkeypatch.setitem(sys.modules, "maya", maya)
    monkeypatch.setitem(sys.modules, "maya.cmds", maya_cmds)

    def fake_import(module_path: str):
        """Record the adapter import and return its mocked module.

        :param module_path: The dotted path of the module being imported.
        :returns: The mocked module corresponding to the import path.
        :note: 
            This function is used to intercept import calls and track which modules are being imported during the test.
        """
        imported.append(module_path)
        return adapter

    monkeypatch.setattr(ops_engine.importlib, "import_module", fake_import)
    monkeypatch.setattr(ops_engine.importlib, "reload", lambda module: module)

    engine = ops_engine.OpsEngine()

    assert engine.host_app == "maya"
    assert imported == ["openpypeline.app.maya.file.file"]
    assert engine.file_handler is adapter


def test_workspace_root_uses_maya_workspace(monkeypatch: MagicMock, tmp_path: str):
    """Use Maya's workspace root when running inside Maya.
    TODO: This test should be expanded to verify that the OpsEngine correctly retrieves the workspace root from Maya's workspace settings, ensuring that it does not fall back to the current working directory when running inside Maya.
    
    :param monkeypatch: A pytest fixture for safely modifying the import system.
    :type monkeypatch: pytest.MonkeyPatch
    :param tmp_path: A temporary directory path for testing.
    :type tmp_path: str
    :returns: None
    :raises AssertionError: If the workspace root is not correctly resolved to Maya's workspace.
    :note: 
        This test ensures that when the OpsEngine is running inside Maya, it correctly retrieves the workspace root from Maya's workspace settings rather than falling back to the current working directory.
    """
    maya_cmds = ModuleType("maya.cmds")
    maya_cmds.workspace = lambda **_kwargs: str(tmp_path)
    monkeypatch.setattr(
        ops_engine.importlib,
        "import_module",
        lambda module_path: maya_cmds,
    )

    assert ops_engine._get_workspace_root("maya") == str(tmp_path)


def test_workspace_root_uses_current_directory_for_standalone(monkeypatch: MagicMock):
    """Use the process working directory outside a DCC host.
    TODO: This test should be expanded to verify that the OpsEngine correctly falls back to the current working directory when running in a standalone context, ensuring that it does not attempt to access any host-specific workspace settings.
    
    :param monkeypatch: A pytest fixture for safely modifying the import system.
    :type monkeypatch: pytest.MonkeyPatch
    :returns: None
    :raises AssertionError: If the workspace root is not correctly resolved to the current working directory.
    :note: 
        This test ensures that when the OpsEngine is running in a standalone context (not within a DCC host), it correctly falls back to using the current working directory as the workspace root.
    """
    monkeypatch.setattr(ops_engine.os, "getcwd", lambda: "/workspace")

    assert ops_engine._get_workspace_root("standalone") == "/workspace"


def test_ui_diagnostics_do_not_open_scene(monkeypatch: MagicMock):
    """Keep diagnostic inventory logging from opening a scene file.
    TODO: This test should be expanded to verify that the UI diagnostics can run without triggering any file opening operations, ensuring that the OpsEngine's UI can be safely invoked in headless or automated testing environments.
    
    :param monkeypatch: A pytest fixture for safely modifying the import system.
    :type monkeypatch: pytest.MonkeyPatch
    :returns: None
    :raises AssertionError: If the file handler's open method is called during the UI diagnostics.
    :note: 
        This test ensures that the OpsEngine's UI diagnostics can run without triggering any file opening operations, which is important for headless testing and automated environments.
    """
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
        """Supply predictable inventory results to the diagnostic test.
        TODO: This stub should be expanded to simulate a more complete inventory structure for comprehensive testing of the OpsEngine's UI diagnostics.
        
        :returns: None
        :note: 
            This stub simulates the behavior of the Inventory class without requiring an actual filesystem or project structure. It provides a controlled environment for testing the OpsEngine's UI diagnostics.
        """
        def __init__(self, _elements):
            """Accept path elements without requiring a filesystem inventory.
            TODO: This constructor should be updated to accept a list of path elements that represent the inventory structure for more comprehensive testing.
            
            :param _elements: A list of path elements representing the inventory structure.
            :note: 
                This constructor does not perform any filesystem operations. It simply stores the provided elements for later use in the list and getPath methods.
            """
            pass

        def list(self):
            """Lists the single item used by the diagnostic test.
            TODO: This method should be updated to return a list based on the test's temporary directory structure rather than a hardcoded list.
            
            :returns: A list containing the single item name 'hero'.
            :note: 
                This method simulates the inventory listing for a specific project structure. It returns a hardcoded list containing the single item name 'hero' to facilitate testing of the OpsEngine's UI diagnostics without relying on an actual inventory.
             """
            return ["hero"]

        def getPath(self):
            """Get the fixture item's expected directory.
            TODO: This method should be updated to return a path based on the test's temporary directory structure rather than a hardcoded path.

            :returns: The absolute path to the fixture item's directory as a string.
            :note: 
                This method simulates the retrieval of the item's path in the inventory. It returns a hardcoded path corresponding to the expected directory structure for the 'hero' item, allowing the OpsEngine's UI diagnostics to function without accessing a real filesystem.
            """
            return "/project/lib/characters/hero/components/model"

    class VersionStub:
        """Provide deterministic WIP versions to the diagnostic test.
        TODO: This stub should be expanded to simulate a more complete versioning system for comprehensive testing of the OpsEngine's UI diagnostics.
        
        :returns: None
        :note: 
            This stub simulates the behavior of the Version class without requiring an actual versioning system. It provides a controlled environment for testing the OpsEngine's UI diagnostics.
        """
        def all(self, _path):
            """Return the item's available version numbers.
            TODO: This method should be expanded to simulate a more complete versioning system for comprehensive testing of the OpsEngine's UI diagnostics.

            :returns: A list of available version numbers.
            :note: 
                This stub simulates the behavior of the Version class without requiring an actual versioning system. It provides a controlled environment for testing the OpsEngine's UI diagnostics.
            """
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


def test_open_latest_workshop_opens_latest_version(monkeypatch: MagicMock):
    """Open the path resolved for the item's highest WIP version.
    TODO: This test should be expanded to verify that the OpsEngine correctly resolves the latest WIP version for a given item and invokes the file handler's open method with the correct path, ensuring that the latest version is opened in the host application.

    :returns: None
    :raises AssertionError: If the file handler's open method is not called with the expected path.

    .. note::
        This test does not verify the actual file opening, only that the correct path is resolved and passed to the file handler's open method.

    """
    from openpypeline.core.file import wip
    from openpypeline.core.version import Version

    monkeypatch.setattr(
        Version,
        "Version",
        lambda: MagicMock(latest=lambda _path: 3),
    )
    #TODO: This stub should be expanded to simulate a more complete versioning system for comprehensive testing of the OpsEngine's open_latest_workshop method.
    monkeypatch.setattr(
        wip,
        "WIP",
        lambda: MagicMock(open=lambda *_args: "/project/hero/wip/hero_wip_0003.ma"),
    )
    handler = MagicMock()
    handler.open.return_value = True
    engine = ops_engine.OpsEngine()
    engine.file_handler = handler

    # TODO: This test should be expanded to verify that the OpsEngine correctly resolves the latest WIP version for a given item and invokes the file handler's open method with the correct path, ensuring that the latest version is opened in the host application.
    assert engine.open_latest_workshop("/project/hero", "hero") is True
    handler.open.assert_called_once_with("/project/hero/wip/hero_wip_0003.ma")
