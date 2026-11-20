"""Main initialization and setup entry point for openPypeline Studio in Autodesk Maya.

Exposes the standard host loader symbols (:func:`openPypeline`, :func:`openPypelineSetup`, path validators, and :class:`~openpypeline.ui.ops_setup_dialog.OpsSetupDialog`) matching the cross-DCC adapter pattern used across host integrations.

:File: loader.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from .core.ops_loader import (
    OpsSetupDialog,
    is_valid_project_file_path,
    is_valid_script_path,
    openPypeline,
    openPypelineSetup,
)

__all__ = [
    "OpsSetupDialog",
    "is_valid_project_file_path",
    "is_valid_script_path",
    "openPypeline",
    "openPypelineSetup",
]
