"""
Module: localization.py

Description: Provides the Maya UI package with access to the shared localization manager and its active localization instance.

    Add Maya-specific helpers here later if the Maya UI needs behavior that shouldn’t belong in the shared core.
"""

from openpypeline.core.localization import LocalizationManager, localization


def get_maya_string(key, default=None):
    """Return a localized string for Maya UI, using the supplied fallback if missing."""
    return localization.get_string(key, default)


__all__ = ["LocalizationManager", "get_maya_string", "localization"]