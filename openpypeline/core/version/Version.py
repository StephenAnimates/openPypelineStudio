"""Core version control management for openPypeline Studio.

Handles parsing, incrementing, and verifying file versions using a copy-based numbering scheme, with extensible subclasses for external revision control
systems such as Subversion, Git, CVS, and Perforce.

:File: Version.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.version import Version

    ver = Version.Version()
    latest = ver.latest("/projects/demo/lib/characters/woman/model")
    next_num = ver.next("woman_wip_0003.mb")
"""

import importlib
import logging
import os
import re
import subprocess
from typing import Any, Optional

from ..util import prefs

#: Module logger for version control parsing and publishing operations.
logger = logging.getLogger("openPypeline.version")

importlib.reload(prefs)


class Version:
    """Base file-copy version manager for openPypeline Studio.

    Implements legacy copy-based file versioning and serves as the base class for external revision control adapters (:class:`svn`, :class:`git`, :class:`cvs`, and :class:`perforce`).

    Default Naming Convention::

        [name]_wip_####.[ext]

    Example Filename::

        testMaster_wip_0003.mb
    """

    def __init__(self) -> None:
        """Initialize the version manager."""
        pass

    def getByIndex(self, index: int) -> Any:
        """Provide the extension point for resolving a version by index.

        :param index: Zero-based index into the item's ordered version list.
        :returns: Version metadata or file path resolved by a subclass.

        .. note::
           Intended to be overridden by custom version control subclasses.
        """
        pass

    def latest(self, path: str) -> Optional[int]:
        """Return the highest WIP version number found under ``path``.

        Queries :meth:`all` for all discovered version integers and returns the maximum value.

        :param path: Directory path of the asset or component containing the WIP subfolder.
        :returns: The highest version number as an integer, or ``None`` if no versions exist.
        """
        # Retrieve a list of all existing version numbers in the directory
        all_versions = self.all(path)
        if all_versions:
            # Return the highest version number if the list is not empty
            return max(all_versions)
        # Return None if no versions were found
        return None

    def verify(self, path: str) -> int:
        """Verify whether a specific versioned file exists on disk.

        :param path: Full file system path to the versioned file to check.
        :returns: ``1`` if ``path`` exists on disk, otherwise ``0``.
        """
        # Check if the exact filepath exists on the filesystem
        if os.path.exists(path):
            return 1
        return 0

    def next(self, filepath: str) -> int:
        """Calculate the next sequential version number from a versioned filename.

        Extracts the trailing ``_<digits>`` suffix before the file extension and
        increments it by ``1``, defaulting to ``1`` if no version suffix is found.

        :param filepath: File path or filename (for example, ``"woman_wip_0003.mb"``).
        :returns: The next integer version number (for example, ``4``), or ``1`` if no existing version number could be parsed.
        """
        # Split the filepath to isolate the base name and the extension
        basename, ext = os.path.splitext(filepath)

        # Use regex to find the version number at the end of the base name
        match = re.search(r"_(\d+)$", basename)
        if match:
            # If a version number is found, parse it as an integer and increment by 1
            version = int(match.group(1))
            next_version = version + 1
            logger.info(
                f"Current version is {version:04d}. Next version is {next_version:04d}."
            )
            return next_version

        # If no version number could be parsed, default to version 1
        logger.warning("Could not determine version from filename.")
        return 1

    def all(self, path: str) -> list[int]:
        """Discover and return all sorted WIP version numbers under ``path``.

        Reads the WIP subfolder name from user preferences (``ops_wip``,
        defaulting to ``"wip"``), scans non-hidden files for trailing
        ``_<digits>.<ext>`` suffixes, and returns the parsed integers sorted in
        ascending order.

        :param path: Directory path of the asset or component containing the WIP
            subfolder.
        :returns: Sorted list of integer version numbers, or an empty list if
            the WIP directory does not exist or contains no matching files.
        """
        # Initialize an empty list to store discovered version numbers
        versions = []

        # Retrieve the work-in-progress folder name from preferences (defaulting to 'wip')
        w_name = prefs.get_pref("ops_wip", "wip")

        # Construct the full path to the versions directory
        versionspath = os.path.join(path, w_name)
        if not os.path.isdir(versionspath):
            # If the directory doesn't exist, return the empty list
            return versions

        # List all files in the directory, filtering out hidden OS files (starting with '.')
        inventory = [f for f in os.listdir(versionspath) if not f.startswith(".")]
        for version_file in inventory:
            # Safely extract version using regex to avoid issues with underscores in item names or arbitrary extensions
            match = re.search(r"_(\d+)\.[a-zA-Z0-9]+$", version_file)
            if match:
                # If a valid version string is found, convert it to an integer and add it to the list
                versions.append(int(match.group(1)))

        # Sort the list of versions in ascending order before returning
        versions.sort()
        return versions


class svn(Version):
    """Publish versioned files through Subversion (SVN)."""

    def publish(self, filepath: str, comment: str = "Publishing new version") -> bool:
        """Add and commit a file to its parent Subversion working copy.

        :param filepath: Full path to the file to stage and commit.
        :param comment: Commit log message passed to ``svn commit``.
        :returns: ``True`` if the SVN commit succeeded, ``False`` otherwise.
        """
        repo_dir = os.path.dirname(filepath)
        try:
            subprocess.run(
                ["svn", "add", filepath],
                cwd=repo_dir,
                check=False,
                capture_output=True,
            )
            subprocess.run(
                ["svn", "commit", "-m", comment, filepath],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )
            logger.info(f"Successfully published {filepath} to SVN.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(
                f"SVN publish failed: {e.stderr.decode('utf-8').strip() if e.stderr else e}"
            )
            return False


class git(Version):
    """Publish versioned files through Git."""

    def publish(self, filepath: str, comment: str = "Publishing new version") -> bool:
        """Stage, commit, and push a file to the remote Git repository.

        :param filepath: Full path to the file to stage, commit, and push.
        :param comment: Commit log message passed to ``git commit``.
        :returns: ``True`` if staging, committing, and pushing succeeded,
            ``False`` otherwise.
        """
        repo_dir = os.path.dirname(filepath)
        try:
            subprocess.run(
                ["git", "add", filepath],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", comment],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "push"],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )
            logger.info(f"Successfully published {filepath} to Git.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Git publish failed: {e.stderr.decode('utf-8').strip() if e.stderr else e}"
            )
            return False


class cvs(Version):
    """Version manager stub reserved for CVS-backed publishing."""

    pass


class perforce(Version):
    """Publish versioned files through Perforce (Helix Core)."""

    def publish(self, filepath: str, comment: str = "Publishing new version") -> bool:
        """Reconcile and submit a file to Perforce.

        :param filepath: Full path to the file to reconcile and submit.
        :param comment: Changelist description passed to ``p4 submit``.
        :returns: ``True`` if the Perforce submission succeeded, ``False``
            otherwise.
        """
        try:
            subprocess.run(
                ["p4", "reconcile", filepath], check=False, capture_output=True
            )
            subprocess.run(
                ["p4", "submit", "-d", comment, filepath],
                check=True,
                capture_output=True,
            )
            logger.info(f"Successfully published {filepath} to Perforce.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Perforce publish failed: {e.stderr.decode('utf-8').strip() if e.stderr else e}"
            )
            return False
