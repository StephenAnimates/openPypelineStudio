"""Maya UI bridge to the shared :mod:`openpypeline.core.localization` subsystem.

Provides the Maya UI package with access to :class:`~openpypeline.core.localization.LocalizationManager`, its active ``localization`` instance, and Maya-scoped string lookup helpers. Add Maya-specific localization helpers here if the Maya UI requires behavior that does not belong in the shared core.

:File: localization.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Optional

from openpypeline.core.localization import LocalizationManager, localization


def get_maya_string(key: str, default: Optional[str] = None) -> str:
    """Return a localized string for Maya UI, using the supplied fallback if missing.

    Delegates lookup to :func:`openpypeline.core.localization.localization.get_string`.

    :param key: Localization lookup key identifying the UI string.
    :param default: Optional fallback string returned when ``key`` is not found in the active language table.
    :returns: Localized string corresponding to ``key``, or ``default`` (or ``key``) if unavailable.
    """
    return localization.get_string(key, default)


__all__ = ["LocalizationManager", "get_maya_string", "localization"]
