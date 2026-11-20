"""Base filesystem interface used by pipeline file handlers.

Defines the :class:`File` base class inherited by specialized file managers
such as :class:`~openpypeline.core.file.master.Master` and
:class:`~openpypeline.core.file.wip.WIP`.

:File: file.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    from openpypeline.core.file import file

    handler = file.File()
    exists = handler.query("/projects/demo/lib/characters/woman/model")
"""

import os


class File:
    """Base interface for querying and bundling pipeline files.

    Provides common filesystem existence checks and defines extension hooks for packaging or archiving managed pipeline assets.
    """

    def __init__(self) -> None:
        """Initialize the base file handler."""
        pass

    def query(self, path: str) -> int:
        """Check whether a file or directory path exists on disk.

        :param path: File system path to verify.
        :returns: ``1`` if ``path`` exists on disk, otherwise ``0``.
        """
        if os.path.exists(path):
            return 1
        else:
            return 0

    def bundle(self) -> None:
        """Provide the extension point for bundling a managed file.

        .. note::
           Intended to be overridden by host-specific or subclassed file handlers to package dependencies for transfer or archiving.
        """
        pass
