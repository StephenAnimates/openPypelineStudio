"""Core Localization Manager for openPypeline Studio.

Handles loading JSON language files from the package's ``resources/lang`` directory and retrieving localized UI strings via :class:`LocalizationManager`.

:File: localization.py
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.localization import localization

    localization.load_language("en")
    label = localization.get_string("menu.file.open", default="Open")
"""

import json
import logging
import os
from typing import Optional

from openpypeline.core.util import prefs

#: Module logger for localization loading and lookup events.
logger = logging.getLogger("openPypeline.localization")


class LocalizationManager:
    """Load localized UI strings and provide keyed lookups.

    Reads JSON translation dictionaries from ``../resources/lang/<lang_code>.json`` and resolves UI string keys with optional caller fallbacks.

    :ivar strings: Active mapping of translation keys to localized strings.
    :vartype strings: dict[str, str]
    :ivar current_lang: ISO language code currently loaded (defaults to ``"en"``).
    :vartype current_lang: str
    """

    def __init__(self) -> None:
        """Initialize an empty English-language string table."""
        self.strings: dict[str, str] = {}
        self.current_lang: str = "en"

    def load_language(self, lang_code: Optional[str] = None) -> None:
        """Load the specified language JSON file into :attr:`strings`.

        When ``lang_code`` is omitted, reads the ``ops_language`` user preference (defaulting to ``"en"``). Resets :attr:`strings` to an empty dictionary if the target JSON file does not exist on disk.

        :param lang_code: Optional language code matching a JSON filename in
            ``resources/lang`` (for example, ``"en"`` or ``"es"``).
        """
        if not lang_code:
            lang_code = prefs.get_pref("ops_language", "en")

        self.current_lang = lang_code

        base_dir = os.path.dirname(__file__)
        lang_dir = os.path.abspath(
            os.path.join(base_dir, "..", "resources", "lang")
        ).replace("\\", "/")
        lang_file = os.path.join(lang_dir, f"{lang_code}.json").replace("\\", "/")

        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
            logger.info(f"Loaded language: {lang_code}")
        else:
            logger.warning(f"Language file not found: {lang_file}")
            self.strings = {}

    def get_string(self, key: str, default: Optional[str] = None) -> str:
        """Return a translated string, caller fallback, or visible key marker.

        :param key: Translation lookup key inside :attr:`strings`.
        :param default: Optional fallback string returned when ``key`` is not found. If omitted, returns ``"[<key>]"``.
        :returns: The localized string, ``default``, or ``"[<key>]"``.
        """
        return self.strings.get(key, default or f"[{key}]")


#: Shared module-level :class:`LocalizationManager` instance.
localization: LocalizationManager = LocalizationManager()
