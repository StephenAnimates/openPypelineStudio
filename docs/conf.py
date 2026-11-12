"""
Sphinx configuration for openPypeline Studio documentation.

To build the HTML documentation, open Terminal on macOS, a terminal emulator
on Linux, or PowerShell or Command Prompt on Windows. Change to the repository's
top-level (root) folder (the folder containing ``docs/`` and ``openpypeline/``), then
enter:
    sphinx-apidoc -f -o docs/ openpypeline/
    sphinx-build -b html docs/ docs/_build/html

The first command generates the API reference pages used by the toctree.
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
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
}
