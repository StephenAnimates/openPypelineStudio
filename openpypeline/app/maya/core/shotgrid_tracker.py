"""Backward-compatible re-export of :mod:`openpypeline.core.shotgrid_tracker`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.shotgrid_tracker` while delegating ShotGrid production tracker integration to :mod:`openpypeline.core.shotgrid_tracker`.

:File: shotgrid_tracker.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from openpypeline.core.shotgrid_tracker import *  # noqa: F401, F403

__all__: list[str] = []
