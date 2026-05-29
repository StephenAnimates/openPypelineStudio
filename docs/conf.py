"""
File: conf.py
Description: Sphinx documentation builder configuration file for openPypeline Studio.
             
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import sys

# Add the project root to the sys.path so Sphinx can import openPypeline modules
sys.path.insert(0, os.path.abspath('../'))
# Also add the maya directory so Sphinx can find Maya-specific modules (like opsLoader)
sys.path.insert(0, os.path.abspath('../maya'))
# Add the core openpypeline directory so absolute imports (like 'from core.file...') resolve correctly
sys.path.insert(0, os.path.abspath('../openpypeline'))

# -- Project information -----------------------------------------------------
project = 'openPypeline Studio'
copyright = '2026, openPypeline Contributors'
author = 'openPypeline Contributors'
release = '2.0.0-alpha'

# -- General configuration ---------------------------------------------------
# Enable autodoc (pulls docstrings), napoleon (supports Google/NumPy docstring formats), 
# and viewcode (adds links to the source code in the generated HTML)
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Mock imports for DCC-specific libraries so Sphinx doesn't crash on GitHub Actions
autodoc_mock_imports = ['maya', 'nuke', 'hou', 'bpy', 'unreal']

# Keep the order of functions and classes exactly as they appear in your source code
autodoc_member_order = 'bysource'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# We will use the standard 'Read the Docs' theme, which is popular and clean
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Theme Options -----------------------------------------------------------
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
}