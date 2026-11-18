"""Abstract Base Class for Production Tracking APIs.

Defines the :class:`ProductionTracker` interface that concrete tracker
integrations (such as :class:`~openpypeline.core.shotgrid_tracker.ShotGridTracker`,
Ftrack, or Kitsu) must implement to ensure DCC-agnostic compatibility across
openPypeline Studio.

:File: tracker.py
:License: Common Public License 1.0 (CPL-1.0)
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Union

#: Module logger for abstract production tracker operations.
logger = logging.getLogger("openPypeline.tracking")


class ProductionTracker(ABC):
    """Abstract base class for production tracking systems.

    Any tracking integration must inherit from this class and implement its
    abstract methods to ensure DCC-agnostic compatibility within openPypeline.

    :ivar url: Base server endpoint URL for the tracking service.
    :vartype url: str
    :ivar auth_user: Login username or API script name used for authentication.
    :vartype auth_user: str
    :ivar auth_key: API key, token, or password used for authentication.
    :vartype auth_key: str
    :ivar connected: ``True`` once :meth:`connect` has verified an active
        session, otherwise ``False``.
    :vartype connected: bool
    """

    def __init__(self, url: str, auth_user: str, auth_key: str) -> None:
        """Store the tracker endpoint and credentials and mark it disconnected.

        :param url: Base server URL for the production tracking instance.
        :param auth_user: Login username or script name for authentication.
        :param auth_key: API key or password for authentication.
        """
        self.url: str = url
        self.auth_user: str = auth_user
        self.auth_key: str = auth_key
        self.connected: bool = False

    @abstractmethod
    def connect(self) -> bool:
        """Authenticate and establish a connection with the tracking API.

        :returns: ``True`` if authentication and connection succeeded,
            otherwise ``False``.
        """
        pass

    @abstractmethod
    def get_projects(self) -> list[dict[str, Any]]:
        """Retrieve a list of active projects from the tracker.

        :returns: List of active project metadata dictionaries.
        """
        pass

    @abstractmethod
    def get_user_tasks(self, username: str) -> list[dict[str, Any]]:
        """Retrieve a list of tasks assigned to the given username.

        :param username: User login or identifier in the tracking system.
        :returns: List of task metadata dictionaries assigned to ``username``.
        """
        pass

    @abstractmethod
    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update the status of a specific task.

        :param task_id: Numeric identifier of the target task.
        :param status: Target status code or label (for example,
            ``"In Progress"`` or ``"Pending Review"``).
        :returns: ``True`` if the task status update succeeded, otherwise
            ``False``.
        """
        pass

    @abstractmethod
    def publish_version(
        self,
        task_id: int,
        filepath: str,
        version: Union[int, str],
        comment: str,
    ) -> bool:
        """Log a new published master or workshop version to the tracking system.

        :param task_id: Numeric identifier of the parent task.
        :param filepath: Filesystem path to the published media or scene file.
        :param version: Version number or formatted version identifier.
        :param comment: Publish description or artist note attached to the
            version record.
        :returns: ``True`` if the version record was created successfully,
            otherwise ``False``.
        """
        pass
