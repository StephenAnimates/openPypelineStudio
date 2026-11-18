"""Resolve and manage work-in-progress file versions.

Defines the :class:`WIP` handler for locating and resolving versioned work-in-progress scene files using user-configured naming conventions.

:File: wip.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.file import wip

    wip_handler = wip.WIP()
    scene_path = wip_handler.open("/projects/demo/lib/characters/woman/model", "woman", 3)
"""

import importlib
import logging
import os
from typing import Optional

from . import file as base_file
from ..util import prefs

#: Module logger for work-in-progress file resolution operations.
logger = logging.getLogger("openPypeline.wip")

importlib.reload(base_file)
importlib.reload(prefs)


class WIP(base_file.File):
    """Resolve and manage an item's work-in-progress versions.

    Inherits filesystem query helpers from :class:`~openpypeline.core.file.file.File` and constructs versioned WIP file paths from user preferences (``ops_wip`` and ``ops_wipFormat``).
    """

    def __init__(self) -> None:
        """Initialize the WIP handler through the shared file base."""
        super().__init__()

    def open(self, path: str, item: str, version: int) -> Optional[str]:
        """Resolve and return the file path for a specific work-in-progress version.

        Constructs the expected path
        ``<path>/<ops_wip>/<item>_<ops_wip>_<version:04d>.<ops_wipFormat>``
        and verifies that it exists on disk using :meth:`query`.

        :param path: Base directory path of the pipeline asset or component.
        :param item: Base name of the pipeline item.
        :param version: Integer version number to resolve (zero-padded to four
            digits).
        :returns: The normalized forward-slash path to the WIP file if found,
            otherwise ``None``.
        """
        # Fetch nomenclature and format dynamically from preferences
        w_name = prefs.get_pref("ops_wip", "wip")
        w_ext = prefs.get_pref("ops_wipFormat", "ma")

        # Build Work-in-Progress filename safely
        name = f"{item}_{w_name}_{version:04d}.{w_ext}"
        wipPath = os.path.join(path, w_name, name).replace("\\", "/")

        if self.query(wipPath):
            logger.debug(f"Found Work-in-Progress: {wipPath}")
            return wipPath
        else:
            logger.error(f"Could not find Work-in-Progress at {wipPath}")
            return None

    def save(self) -> None:
        """Provide the extension point for saving a work-in-progress version.

        .. note::
           Intended to be overridden by host-specific or subclassed WIP handlers.
        """
        pass
