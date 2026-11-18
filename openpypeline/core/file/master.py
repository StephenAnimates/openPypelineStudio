"""Resolve and manage published master files.

Defines the :class:`Master` interface for resolving, opening, processing, and managing published master assets and shots within openPypeline Studio.

:File: master.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.file import master

    master_handler = master.Master()
    has_master = master_handler.query("/projects/demo/lib/characters/woman/model")
"""

import importlib
import os

from . import file as base_file
from ..util import prefs

importlib.reload(base_file)
importlib.reload(prefs)


class Master(base_file.File):
    """Represent the published master file for a pipeline item.

    Inherits shared file query functionality from :class:`~openpypeline.core.file.file.File` and defines extension hooks for host-specific master resolution, lifecycle callbacks, and publishing workflows.
    """

    def __init__(self) -> None:
        """Initialize the master handler through the shared file base."""
        super().__init__()

    def getMaster(self) -> None:
        """Provide the extension point for resolving an item's master file.

        .. note::
           Intended to be overridden by host-specific or subclassed master handlers.
        """
        pass

    def open(self) -> None:
        """Provide the extension point for opening the master file.

        .. note::
           Intended to be overridden by host-specific or subclassed master handlers.
        """
        pass

    def process(self) -> None:
        """Provide the extension point for processing a master file.

        .. note::
           Intended to be overridden by host-specific or subclassed master handlers.
        """
        pass

    def preMasterCommand(self) -> None:
        """Provide the extension point for commands run before mastering.

        .. note::
           Intended to be overridden by host-specific or subclassed master handlers.
        """
        pass

    def postMasterCommand(self) -> None:
        """Provide the extension point for commands run after mastering.

        .. note::
           Intended to be overridden by host-specific or subclassed master handlers.
        """
        pass

    def close(self) -> None:
        """Provide the extension point for closing the master file.

        .. note::
           Intended to be overridden by host-specific or subclassed master handlers.
        """
        pass
