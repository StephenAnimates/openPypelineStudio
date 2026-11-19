"""DCC-agnostic preference manager for openPypeline Studio.

Replaces Maya's ``optionVars`` by storing configurations in a centralized JSON file in the user's home directory so preferences persist across host applications.

:File: prefs.py
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline import prefs

    prefs.set_pref("ops_projectFilePath", "/projects/studio")
    path = prefs.get_pref("ops_projectFilePath", "")
"""

import json
import logging
import os
from typing import Any

#: Module logger for preference read/write operations.
logger = logging.getLogger("openPypeline.prefs")

#: Path to the centralized JSON preferences file in the user's home directory.
PREFS_FILE: str = os.path.expanduser("~/.openpypeline/user_prefs.json")


def _load_prefs() -> dict[str, Any]:
    """Reads the JSON preferences file from disk.

    :returns: A dictionary of stored preference keys and values, or an empty dictionary if the file does not exist or fails to parse.
    """
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
    return {}


def _save_prefs(data: dict[str, Any]) -> None:
    """Writes the JSON preferences dictionary to disk.

    :param data: Dictionary of preference key-value pairs to serialize.
    """
    os.makedirs(os.path.dirname(PREFS_FILE), exist_ok=True)
    try:
        with open(PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save preferences: {e}")


def get_pref(key: str, default: Any = None) -> Any:
    """Retrieves a preference value by key.

    :param key: The name of the preference to look up.
    :param default: Fallback value returned if ``key`` is not found.
    :returns: The stored preference value, or ``default`` if missing.
    """
    data = _load_prefs()
    return data.get(key, default)


def set_pref(key: str, value: Any) -> None:
    """Sets a preference key to a specific value and saves it to disk.

    :param key: The name of the preference to store.
    :param value: Any JSON-serializable value to associate with ``key``.
    """
    data = _load_prefs()
    data[key] = value
    _save_prefs(data)


def has_pref(key: str) -> bool:
    """Checks whether a preference key exists in the stored preferences.

    :param key: The name of the preference to check.
    :returns: ``True`` if ``key`` exists, otherwise ``False``.
    """
    return key in _load_prefs()


def remove_pref(key: str) -> None:
    """Removes a preference key from disk if it exists.

    :param key: The name of the preference to delete.
    """
    data = _load_prefs()
    if key in data:
        del data[key]
        _save_prefs(data)
