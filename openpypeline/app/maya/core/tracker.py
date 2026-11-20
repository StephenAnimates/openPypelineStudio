"""Backward-compatible re-export of :mod:`openpypeline.core.tracker`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.tracker` while delegating all production tracker classes and helpers to the shared :mod:`openpypeline.core.tracker` module.

:File: tracker.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from openpypeline.core.tracker import *  # noqa: F401, F403

__all__: list[str] = []
