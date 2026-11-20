"""Manage project configuration and project-list persistence.

Defines the :class:`Project` interface and base methods for locating, validating, and managing openPypeline project registries.

:File: project.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.project import Project

    proj = Project()
    proj.openPipeline_projectFilePath = "/projects/studio"
    proj.openPipeline_projList = "openpypeline_projects.xml"
    full_path = proj.path()
"""

import importlib
import os

from ..util import XML

importlib.reload(XML)


class Project:
    """Core project configuration and lifecycle management interface.

    Provides base attributes and extension hooks for creating, listing,
    validating, and selecting studio projects.

    :ivar openPipeline_projectFilePath: Directory path containing the project configuration file.
    :vartype openPipeline_projectFilePath: str
    :ivar openPipeline_projList: Filename of the project registry list.
    :vartype openPipeline_projList: str
    """

    def __init__(self) -> None:
        """Initialize the project configuration path and project-list name."""
        self.openPipeline_projectFilePath: str = ""
        self.openPipeline_projList: str = ""

    def create(self) -> None:
        """Provide the extension point for creating a new project.

        .. note::
           Intended to be overridden by host-specific or subclassed project managers.
        """
        pass

    def remove(self) -> None:
        """Provide the extension point for removing an existing project.

        .. note::
           Intended to be overridden by host-specific or subclassed project managers.
        """
        pass

    def list(self) -> None:
        """Provide the extension point for listing configured projects.

        .. note::
           Intended to be overridden by host-specific or subclassed project managers.
        """
        pass

    def set(self) -> None:
        """Provide the extension point for selecting the active project.

        .. note::
           May require host-application-specific implementation when setting active workspace paths.
        """
        # app specific?
        pass

    def validateProject(self) -> None:
        """Provide the extension point for validating project settings."""
        pass

    def validateProjectFile(self) -> None:
        """Provide the extension point for validating the project registry file."""
        pass

    def path(self) -> str:
        """Return the full path of the project configuration file.

        Joins :attr:`openPipeline_projectFilePath` and :attr:`openPipeline_projList` into a single file system path.

        :returns: The full path to the project file.
        """
        projectFilePath = os.path.join(
            self.openPipeline_projectFilePath, self.openPipeline_projList
        )
        return projectFilePath
