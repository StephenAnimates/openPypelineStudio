"""
File: conftest.py
Description: Pytest configuration file for openPypeline Studio.
             This file is automatically discovered by pytest before running any tests.
             It mocks DCC-specific modules (like maya.cmds) so that the core Python
             logic can be tested in CI environments (like GitHub Actions) without
             requiring a headless Maya, Nuke, or Houdini installation.
"""

import sys
from unittest.mock import MagicMock

# Create mock objects for DCC-specific modules
mock_maya = MagicMock()
mock_maya_cmds = MagicMock()

# Inject the mocks into sys.modules so imports don't fail in GitHub Actions
sys.modules['maya'] = mock_maya
sys.modules['maya.cmds'] = mock_maya_cmds

# Mock other DCCs supported by opsEngine.py
sys.modules['nuke'] = MagicMock()
sys.modules['hou'] = MagicMock()
sys.modules['bpy'] = MagicMock()
sys.modules['unreal'] = MagicMock()