"""
File: prefs.py
Description: DCC-agnostic preference manager for openPypeline Studio.
             Replaces Maya's optionVars by storing configurations in a 
             centralized JSON file in the user's home directory.
"""

import os
import json
import logging

logger = logging.getLogger("openPypeline.prefs")

# Store preferences in the user's home directory so they persist across Maya, Nuke, etc.
PREFS_FILE = os.path.expanduser("~/.openpypeline/user_prefs.json")

def _load_prefs():
    """Reads the JSON preferences file from disk."""
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
    return {}

def _save_prefs(data):
    """Writes the JSON preferences dict to disk."""
    os.makedirs(os.path.dirname(PREFS_FILE), exist_ok=True)
    try:
        with open(PREFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save preferences: {e}")

def get_pref(key, default=None):
    """Retrieves a preference by key. Returns default if not found."""
    data = _load_prefs()
    return data.get(key, default)

def set_pref(key, value):
    """Sets a preference key to a specific value and saves it."""
    data = _load_prefs()
    data[key] = value
    _save_prefs(data)

def has_pref(key):
    """Checks if a preference key exists."""
    return key in _load_prefs()

def remove_pref(key):
    """Removes a preference key if it exists."""
    data = _load_prefs()
    if key in data:
        del data[key]
        _save_prefs(data)