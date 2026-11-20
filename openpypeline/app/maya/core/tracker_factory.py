"""Backward-compatible re-export of :mod:`openpypeline.core.tracker_factory`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.tracker_factory` while delegating tracker factory resolution to :mod:`openpypeline.core.tracker_factory`.

:File: tracker_factory.py
:Host: Autodesk Maya
:Status: Stub
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from openpypeline.core.tracker_factory import *  # noqa: F401, F403

__all__: list[str] = []
