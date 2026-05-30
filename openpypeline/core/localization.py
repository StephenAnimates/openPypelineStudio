"""
File: localization.py
Description: Core Localization Manager for openPypeline Studio.
             Handles loading JSON language files and retrieving UI strings.
"""

import os
import json
import logging
from openpypeline.core.util import prefs

logger = logging.getLogger("openPypeline.localization")

class LocalizationManager:
    def __init__(self):
        self.strings = {}
        self.current_lang = "en"

    def load_language(self, lang_code=None):
        """Loads the specified language JSON file into memory."""
        if not lang_code:
            lang_code = prefs.get_pref("ops_language", "en")
        
        self.current_lang = lang_code
        
        base_dir = os.path.dirname(__file__)
        lang_dir = os.path.abspath(os.path.join(base_dir, "..", "resources", "lang")).replace("\\", "/")
        lang_file = os.path.join(lang_dir, f"{lang_code}.json").replace("\\", "/")
        
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
            logger.info(f"Loaded language: {lang_code}")
        else:
            logger.warning(f"Language file not found: {lang_file}")
            self.strings = {}

    def get_string(self, key, default=None):
        return self.strings.get(key, default or f"[{key}]")

localization = LocalizationManager()