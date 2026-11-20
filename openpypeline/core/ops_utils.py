"""General filesystem and path utility functions for openPypeline Studio.

Provides cross-platform directory validation and path-component extraction helpers, replacing the legacy ``openPipelineUtility.mel`` script.

:File: ops_utils.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import os

__all__ = ["get_folder_from_path", "is_valid_folder"]


def is_valid_folder(path: str) -> bool:
    """Return whether ``path`` is an existing, non-hidden directory.

    Ignores hidden or metadata folders whose directory name begins with a
    leading period (such as ``.svn``, ``.git``, or ``.openpypeline``).

    :param path: Filesystem path to validate.
    :returns: ``True`` if ``path`` exists as a directory and its base name does
        not start with ``"."``, ``False`` otherwise.
    """
    if not os.path.isdir(path):
        return False
    # Strip trailing slashes so basename inspects the directory name rather than returning ""
    return not os.path.basename(path.rstrip("/\\")).startswith(".")


def get_folder_from_path(path: str, offset_from_last: int) -> str:
    """Return the path segment at a given offset from the trailing segment.

    Normalizes path separators to forward slashes and indexes backward from the
    final non-empty segment (where ``offset_from_last=0`` returns the last
    segment, ``1`` returns its parent directory, and so on).

    :param path: Filesystem path string to inspect.
    :param offset_from_last: Zero-based reverse offset from the final path
        component.
    :returns: Matching folder or filename component, or ``""`` if
        ``offset_from_last`` is out of range.
    """
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    idx = len(parts) - 1 - offset_from_last
    if 0 <= idx < len(parts):
        return parts[idx]
    return ""
