"""Backward-compatible re-export of :mod:`openpypeline.core.rename_asset`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.rename_asset` while delegating asset renaming utilities to :mod:`openpypeline.core.rename_asset`.

:File: rename_asset.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from openpypeline.core.rename_asset import *  # noqa: F401, F403

__all__: list[str] = []
