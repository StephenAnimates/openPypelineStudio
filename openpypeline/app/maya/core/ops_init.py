"""Backward-compatible re-export of :mod:`openpypeline.core.ops_init`.

Preserves legacy import paths under :mod:`openpypeline.app.maya.core.ops_init` while delegating pipeline initialization and environment setup to :mod:`openpypeline.core.ops_init`.

:File: ops_init.py
:Host: Autodesk Maya
:Status: Stub
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from openpypeline.core.ops_init import *  # noqa: F401, F403

__all__: list[str] = []
