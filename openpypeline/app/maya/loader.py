"""
File: loader.py
Description: Main initialization and setup entry point for openPypeline Studio in Autodesk Maya.
Exposes standard loader functions matching the DCC adapter pattern.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from .core.ops_loader import (
    openPypeline,
    openPypelineSetup,
    is_valid_project_file_path,
    is_valid_script_path,
    OpsSetupDialog,
)

__all__ = [
    "openPypeline",
    "openPypelineSetup",
    "is_valid_project_file_path",
    "is_valid_script_path",
    "OpsSetupDialog",
]
