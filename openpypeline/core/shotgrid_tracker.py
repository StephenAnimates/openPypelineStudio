"""ShotGrid (Flow Production Tracking) implementation of the ProductionTracker API.

Provides concrete methods to authenticate, query projects and tasks, update
task statuses, and publish version records to Autodesk ShotGrid using
``shotgun_api3``.

:File: shotgrid_tracker.py
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    from openpypeline.core.shotgrid_tracker import ShotGridTracker

    sg_tracker = ShotGridTracker("https://autodesk.com", "script_user", "api_key")
    if sg_tracker.connect():
        projects = sg_tracker.get_projects()
"""

import logging
from typing import Any, Optional, Union

from openpypeline.core.tracker import ProductionTracker

#: Module logger for ShotGrid API connection and query events.
logger = logging.getLogger("openPypeline.tracking.shotgrid")

try:
    import shotgun_api3
except ImportError:
    shotgun_api3 = None
    logger.warning(
        "shotgun_api3 module not found. ShotGrid tracking will not be available."
    )


class ShotGridTracker(ProductionTracker):
    """Concrete :class:`~openpypeline.core.tracker.ProductionTracker` for Autodesk ShotGrid.

    Wraps ``shotgun_api3.Shotgun`` to expose studio project queries, artist
    task lookups, task status updates, and version publishing.

    :ivar sg: Active ``shotgun_api3.Shotgun`` client instance, or ``None``
        before :meth:`connect` succeeds.
    :vartype sg: Optional[Any]
    """

    def __init__(self, url: str, auth_user: str, auth_key: str) -> None:
        """Initialize tracker credentials and an empty ShotGrid API client.

        :param url: Base URL of the ShotGrid site (for example,
            ``"https://autodesk.com"``).
        :param auth_user: ShotGrid script name used for API authentication.
        :param auth_key: ShotGrid script API key used for authentication.
        """
        super().__init__(url, auth_user, auth_key)
        self.sg: Optional[Any] = None

    def connect(self) -> bool:
        """Authenticate to ShotGrid and verify connectivity with a project query.

        Instantiates ``shotgun_api3.Shotgun`` using :attr:`url`,
        :attr:`auth_user`, and :attr:`auth_key`, then runs a lightweight
        ``find_one("Project", [])`` test query.

        :returns: ``True`` if authentication and the test query succeeded,
            ``False`` if ``shotgun_api3`` is unavailable or connection fails.
        """
        if not shotgun_api3:
            logger.error("Cannot connect to ShotGrid: shotgun_api3 is not installed.")
            return False

        try:
            # auth_user acts as the script_name, auth_key acts as the script api_key
            self.sg = shotgun_api3.Shotgun(
                self.url, script_name=self.auth_user, api_key=self.auth_key
            )

            # Test connection by attempting to fetch a single project
            self.sg.find_one("Project", [])
            self.connected = True
            logger.info(f"Successfully connected to ShotGrid at {self.url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to ShotGrid: {e}")
            self.connected = False
            return False

    def get_projects(self) -> list[dict[str, Any]]:
        """Return active ShotGrid projects when connected.

        :returns: List of active project dictionaries containing ``"name"`` and
            ``"id"`` keys, or an empty list if disconnected or an error occurs.
        """
        if not self.connected:
            return []
        try:
            # Retrieve all active projects
            projects = self.sg.find(
                "Project", [["sg_status", "is", "Active"]], ["name", "id"]
            )
            return projects
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []

    def get_user_tasks(self, username: str) -> list[dict[str, Any]]:
        """Return tasks assigned to the ShotGrid user with the given login.

        :param username: ShotGrid ``HumanUser.login`` string to query.
        :returns: List of task dictionaries containing ``"content"``,
            ``"entity"``, ``"sg_status_list"``, and ``"project"`` fields, or an
            empty list if disconnected, the user is not found, or an error
            occurs.
        """
        if not self.connected:
            return []
        try:
            user = self.sg.find_one(
                "HumanUser", [["login", "is", username]], ["id", "name"]
            )
            if not user:
                logger.warning(f"User '{username}' not found in ShotGrid.")
                return []

            tasks = self.sg.find(
                "Task",
                [["task_assignees", "is", user]],
                ["content", "entity", "sg_status_list", "project"],
            )
            return tasks
        except Exception as e:
            logger.error(f"Error fetching tasks for {username}: {e}")
            return []

    def update_task_status(self, task_id: int, status: str) -> bool:
        """Set a ShotGrid task's status and report whether the update succeeded.

        :param task_id: Numeric ShotGrid ``Task`` entity ID.
        :param status: Target ShotGrid status short code (for example,
            ``"ip"`` or ``"rev"``).
        :returns: ``True`` if the status update succeeded, ``False`` otherwise.
        """
        if not self.connected:
            return False
        try:
            self.sg.update("Task", task_id, {"sg_status_list": status})
            logger.info(f"Task {task_id} status updated to {status}.")
            return True
        except Exception as e:
            logger.error(f"Error updating task {task_id} to status {status}: {e}")
            return False

    def publish_version(
        self,
        task_id: int,
        filepath: str,
        version: Union[int, str],
        comment: str,
    ) -> bool:
        """Create a ShotGrid Version linked to the task and its project entity.

        Looks up the parent ``Task`` to resolve its associated ``Project`` and
        linked ``entity`` (Asset or Shot), then creates a new ``Version``
        record formatted as ``v###``.

        :param task_id: Numeric ShotGrid ``Task`` entity ID.
        :param filepath: Filesystem path to the published media or scene file
            stored in ``sg_path_to_frames``.
        :param version: Version number or string formatted into a zero-padded
            three-digit version code (for example, ``"v003"``).
        :param comment: Description note attached to the ShotGrid ``Version``.
        :returns: ``True`` if the ``Version`` record was created successfully,
            ``False`` otherwise.
        """
        if not self.connected:
            return False
        try:
            task = self.sg.find_one(
                "Task", [["id", "is", task_id]], ["entity", "project"]
            )
            if not task:
                logger.error(f"Task {task_id} not found. Cannot publish version.")
                return False

            data = {
                "project": task["project"],
                "entity": task["entity"],
                "sg_task": task,
                "code": f"v{str(version).zfill(3)}",
                "description": comment,
                "sg_path_to_frames": filepath,
            }

            new_version = self.sg.create("Version", data)
            logger.info(
                f"Successfully published Version {new_version['id']} for task {task_id}."
            )
            return True

        except Exception as e:
            logger.error(f"Error publishing version: {e}")
            return False
