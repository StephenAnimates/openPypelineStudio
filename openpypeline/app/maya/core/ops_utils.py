"""Backward-compatible re-export of :mod:`openpypeline.core.ops_utils`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.ops_utils` while delegating filesystem and path helpers to :mod:`openpypeline.core.ops_utils`.

:File: ops_utils.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from openpypeline.core.ops_utils import *  # noqa: F401, F403

__all__: list[str] = []
