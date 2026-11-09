"""
Sphinx configuration for openPypeline Studio documentation.

License: Common Public License 1.0 (CPL-1.0)
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

project = "openPypeline Studio"
copyright = "2026, openPypeline Contributors"
author = "openPypeline Contributors"
release = "2.0.0-beta"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

# DCC SDKs and Qt are provided by host applications, not the docs build environment.
autodoc_mock_imports = [
    "maya",
    "nuke",
    "hou",
    "bpy",
    "unreal",
    "PySide6",
]
autodoc_member_order = "bysource"

root_doc = "index"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv", "env"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "sphinx_rtd_theme"
html_title = f"{project} {release}"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
}
