"""
File: tracker.py
Description: Abstract Base Class for Production Tracking APIs.
             Defines the standard interface that all tracker modules
             (e.g., ShotGrid, Ftrack, Kitsu) must implement.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("openPypeline.tracking")


class ProductionTracker(ABC):
    """
    Abstract base class for production tracking systems.
    Any tracking integration must inherit from this class and implement
    these methods to ensure DCC-agnostic compatibility within openPypeline.
    """
    
    def __init__(self, url, auth_user, auth_key):
        self.url = url
        self.auth_user = auth_user
        self.auth_key = auth_key
        self.connected = False

    @abstractmethod
    def connect(self):
        """
        Authenticates and establishes a connection with the tracking API.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_projects(self):
        """
        Retrieves a list of active projects from the tracker.
        """
        pass

    @abstractmethod
    def get_user_tasks(self, username):
        """
        Retrieves a list of tasks assigned to the given username.
        """
        pass

    @abstractmethod
    def update_task_status(self, task_id, status):
        """
        Updates the status of a specific task (e.g., "In Progress", "Pending Review").
        """
        pass

    @abstractmethod
    def publish_version(self, task_id, filepath, version, comment):
        """
        Logs a new published master or workshop version to the tracking system.
        """
        pass