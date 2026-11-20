"""Backward-compatible re-export of :mod:`openpypeline.core.ops_init`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.ops_init` while delegating pipeline initialization and environment setup to :mod:`openpypeline.core.ops_init`.

:File: ops_init.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from openpypeline.core.ops_init import *  # noqa: F401, F403

__all__: list[str] = []
