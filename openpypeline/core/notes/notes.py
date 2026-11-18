"""Create and query XML notes associated with pipeline items.

Defines the :class:`Notes` base interface for checking, creating, reading,
and writing revision history and custom note files attached to studio assets
and shots.

:File: notes.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.notes import Notes

    notes_handler = Notes()
    exists = notes_handler.query("/projects/demo/assets/hero", "hero")
"""

import os


class Notes:
    """Query and manage XML notes attached to pipeline items.

    Provides base query functionality and extension hooks for creating, reading, and writing item note files stored inside an item's ``notes`` subdirectory.
    """

    def __init__(self) -> None:
        """Initialize the notes handler."""
        pass

    def create(self) -> None:
        """Provide the extension point for creating an item's notes file.

        .. note::
           Intended to be overridden by host-specific or subclassed note
           handlers.
        """
        pass

    def query(self, path: str, element: str) -> int:
        """Check whether an asset-note XML file exists for a pipeline item.

        Constructs the expected path ``<path>/notes/<element>_AssetNote.xml`` and verifies its presence on disk.

        :param path: Directory path of the parent asset or pipeline item.
        :param element: Base name of the pipeline element (used as the prefix for ``_AssetNote.xml``).
        :returns: ``1`` if the note XML file exists on disk, otherwise ``0``.
        """
        note = os.path.join(path, "notes", (element + "_AssetNote.xml"))
        if os.path.exists(note):
            return 1
        else:
            return 0

    def read(self) -> None:
        """Provide the extension point for reading an item's notes.

        .. note::
           Intended to be overridden by host-specific or subclassed note
           handlers.
        """
        pass

    def write(self) -> None:
        """Provide the extension point for writing an item's notes.

        .. note::
           Intended to be overridden by host-specific or subclassed note
           handlers.
        """
        pass
