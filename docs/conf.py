"""
Sphinx configuration for openPypeline Studio documentation.

To build the HTML documentation locally, open Terminal on macOS, a terminal emulator on Linux, or PowerShell or Command Prompt on Windows. From the repository root (the folder containing ``docs/`` and ``openpypeline/``), run:
    sphinx-apidoc -f -o docs/ openpypeline/
    sphinx-build -b html -W --keep-going docs/ docs/_build/html

The first command regenerates the tracked API reference pages in ``docs/``. Run it locally when you want those generated changes included in a commit. GitHub Actions on this repo also regenerates the pages and builds the documentation for pull requests and pushes, but changes made in its checkout are not committed back to the repo. Running the HTML build locally is optional if you are relying on CI for validation.
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
html_js_files = ["image-lightbox.js"]
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
}
