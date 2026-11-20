"""Pytest fixtures for openPypeline Studio.

Automatically discovered by ``pytest`` when running tests under ``tests/``. Provides the opt-in :func:`mock_dcc_modules` fixture so contributor tests can simulate DCC host environments without polluting ``sys.modules`` globally across the suite or requiring proprietary DCC installations.

Usage Example
-------------

Request ``mock_dcc_modules`` as a parameter in any ``pytest`` test function to temporarily inject mocked ``maya``, ``maya.cmds``, ``nuke``, ``hou``, ``bpy``, and ``unreal`` modules into ``sys.modules``:

.. code-block:: python

   def test_maya_specific_workflow(mock_dcc_modules) -> None:
       mock_dcc_modules["maya.cmds"].ls.return_value = ["pCube1"]
       # Code under test can now safely import maya.cmds

Run from the repository root with ``pytest``:

.. code-block:: bash

   pytest -v

:File: conftest.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""


from collections.abc import Iterator
import sys
from unittest.mock import MagicMock, patch

try:
    import pytest

    @pytest.fixture
    def mock_dcc_modules() -> Iterator[dict[str, MagicMock]]:
        """Temporarily inject stub DCC SDK modules into ``sys.modules`` for a test."""
        mocks = {
            "maya": MagicMock(),
            "maya.cmds": MagicMock(),
            "nuke": MagicMock(),
            "hou": MagicMock(),
            "bpy": MagicMock(),
            "unreal": MagicMock(),
        }
        with patch.dict(sys.modules, mocks):
            yield mocks

except ImportError:
    pass
