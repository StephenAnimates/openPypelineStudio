"""DCC-agnostic host adapter and loader protocol contract tests.

Defines the standardized file-handler and loader interfaces required across all host integrations and dynamically verifies that every app package under :mod:`openpypeline.app` implements them.

:File: test_host_adapters.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import importlib
import pkgutil
from types import ModuleType
import unittest
from unittest.mock import MagicMock, patch

from openpypeline import app as app_pkg

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


def _headless_dcc_modules() -> dict[str, object]:
    """Build lightweight stub modules for headless DCC and Qt imports."""
    mock_pyside = ModuleType("PySide6")
    mock_widgets = MagicMock()
    mock_core = MagicMock()
    mock_pyside.QtWidgets = mock_widgets
    mock_pyside.QtCore = mock_core

    mock_maya = ModuleType("maya")
    mock_cmds = MagicMock()
    mock_maya.cmds = mock_cmds

    return {
        "PySide6": mock_pyside,
        "PySide6.QtWidgets": mock_widgets,
        "PySide6.QtCore": mock_core,
        "maya": mock_maya,
        "maya.cmds": mock_cmds,
    }


class TestAllHostProtocols(unittest.TestCase):
    """Automatically discover all app integrations and verify protocol compliance."""

    def test_discovered_apps_implement_file_protocol(self) -> None:
        """Verify every package under ``openpypeline.app`` implements ``REQUIRED_FILE_PROTOCOL``."""
        with patch.dict("sys.modules", _headless_dcc_modules()):
            for _, app_name, is_pkg in pkgutil.iter_modules(app_pkg.__path__):
                if not is_pkg:
                    continue
                file_mod = importlib.import_module(
                    f"openpypeline.app.{app_name}.file.file"
                )
                for method_name in REQUIRED_FILE_PROTOCOL:
                    with self.subTest(app=app_name, method=method_name):
                        self.assertTrue(
                            hasattr(file_mod, method_name),
                            f"'{app_name}' file handler is missing required method: '{method_name}'",
                        )
                        self.assertTrue(
                            callable(getattr(file_mod, method_name)),
                            f"'{app_name}' file handler member '{method_name}' is not callable",
                        )

    def test_discovered_apps_implement_loader_protocol(self) -> None:
        """Verify every package under ``openpypeline.app`` implements ``REQUIRED_LOADER_PROTOCOL``."""
        with patch.dict("sys.modules", _headless_dcc_modules()):
            for _, app_name, is_pkg in pkgutil.iter_modules(app_pkg.__path__):
                if not is_pkg:
                    continue
                loader_mod = importlib.import_module(
                    f"openpypeline.app.{app_name}.loader"
                )
                for func_name in REQUIRED_LOADER_PROTOCOL:
                    with self.subTest(app=app_name, func=func_name):
                        self.assertTrue(
                            hasattr(loader_mod, func_name),
                            f"'{app_name}' loader is missing required function: '{func_name}'",
                        )
                        self.assertTrue(
                            callable(getattr(loader_mod, func_name)),
                            f"'{app_name}' loader member '{func_name}' is not callable",
                        )


if __name__ == "__main__":
    unittest.main()
