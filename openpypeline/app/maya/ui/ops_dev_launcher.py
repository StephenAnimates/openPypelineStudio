"""Developer entry point for launching and testing openPypeline Studio Maya GUIs.

Prompts the developer to select the root repository directory containing ``openpypeline/``, prepends it to ``sys.path``, and opens :class:`~openpypeline.app.maya.ui.diagnostic_ui.diagnosticUI` to manage and inspect individual PySide6 windows during development.

Intended strictly for development and debugging; artist sessions should use :mod:`openpypeline.app.maya.core.ops_loader`.

:File: ops_dev_launcher.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    import importlib
    from openpypeline.app.maya.ui import ops_dev_launcher

    importlib.reload(ops_dev_launcher)
    dev_launcher = ops_dev_launcher.OpsDevLauncher()
"""

import importlib
import sys
from typing import Any, Optional

from PySide6 import QtWidgets

# TODO: Run the end-to-end manual test for OpenUSD (.usd, .usda) and Alembic (.abc) project creation and export using this diagnostic launcher.


class OpsDevLauncher:
    """Launch the developer diagnostic window after locating the source tree.

    Orchestrates repository directory selection via :meth:`sourceFilesPath`, ``sys.path`` registration via :meth:`appendDir`, and diagnostic window initialization via :meth:`diagnostic`.

    :ivar srcDir: Normalized forward-slash path to the selected repository root directory, or ``""`` if selection was canceled.
    :vartype srcDir: str
    :ivar diagnosticUI: Active :class:`~openpypeline.app.maya.ui.diagnostic_ui.diagnosticUI` window instance when launched.
    :vartype diagnosticUI: Optional[Any]
    """

    def __init__(self) -> None:
        """Prompt for the source directory, update ``sys.path``, and launch the UI."""
        self.srcDir: str = ""
        self.diagnosticUI: Optional[Any] = None
        # First, prompt the user to select the root script directory.
        self.sourceFilesPath()
        # If a valid directory was selected, proceed with initialization.
        if self.srcDir:
            self.appendDir()
            self.diagnostic()

    def sourceFilesPath(self) -> None:
        """Open a PySide6 folder chooser and store the selected path in :attr:`srcDir`."""
        # Use the modern Qt QFileDialog for directory selection.
        _app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select the folder that contains the 'openpypeline' directory",
        )

        if dir_path:
            self.srcDir = dir_path.replace("\\", "/")

    def diagnostic(self) -> None:
        """Reload and display :class:`~openpypeline.app.maya.ui.diagnostic_ui.diagnosticUI`."""
        # Import the diagnostic UI module.
        from . import diagnostic_ui as diagnosticUI

        # Reload the module to ensure the latest code is used during development.
        importlib.reload(diagnosticUI)
        # Instantiate and show the diagnostic window, passing the source directory.
        self.diagnosticUI = diagnosticUI.diagnosticUI(self.srcDir)
        self.diagnosticUI.showWindow()

    def appendDir(self) -> None:
        """Prepend :attr:`srcDir` to ``sys.path`` if it is not already registered."""
        # Check if the directory is not already in the path to avoid duplicates.
        if self.srcDir not in sys.path:
            # Insert at the beginning of the list to ensure it's checked first.
            sys.path.insert(0, self.srcDir)
