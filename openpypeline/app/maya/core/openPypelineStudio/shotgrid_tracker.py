"""
File: shotgrid_tracker.py
Description: ShotGrid (Flow Production Tracking) implementation of the ProductionTracker API.
             Provides concrete methods to interface with Autodesk ShotGrid using shotgun_api3.
"""

import logging
from openpypeline.app.maya.core.openPypelineStudio.tracker import ProductionTracker

logger = logging.getLogger("openPypeline.tracking.shotgrid")

try:
    import shotgun_api3
except ImportError:
    shotgun_api3 = None
    logger.warning("shotgun_api3 module not found. ShotGrid tracking will not be available.")

class ShotGridTracker(ProductionTracker):
    """
    Implementation of the ProductionTracker for Autodesk ShotGrid.
    """
    
    def __init__(self, url, auth_user, auth_key):
        super().__init__(url, auth_user, auth_key)
        self.sg = None

    def connect(self):
        if not shotgun_api3:
            logger.error("Cannot connect to ShotGrid: shotgun_api3 is not installed.")
            return False
        
        try:
            # auth_user acts as the script_name, auth_key acts as the script api_key
            self.sg = shotgun_api3.Shotgun(self.url, script_name=self.auth_user, api_key=self.auth_key)
            
            # Test connection by attempting to fetch a single project
            self.sg.find_one("Project", [])
            self.connected = True
            logger.info(f"Successfully connected to ShotGrid at {self.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ShotGrid: {e}")
            self.connected = False
            return False

    def get_projects(self):
        if not self.connected:
            return []
        try:
            # Retrieve all active projects
            projects = self.sg.find("Project", [['sg_status', 'is', 'Active']], ['name', 'id'])
            return projects
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []

    def get_user_tasks(self, username):
        if not self.connected:
            return []
        try:
            user = self.sg.find_one("HumanUser", [['login', 'is', username]], ['id', 'name'])
            if not user:
                logger.warning(f"User '{username}' not found in ShotGrid.")
                return []
            
            tasks = self.sg.find("Task", [['task_assignees', 'is', user]], ['content', 'entity', 'sg_status_list', 'project'])
            return tasks
        except Exception as e:
            logger.error(f"Error fetching tasks for {username}: {e}")
            return []

    def update_task_status(self, task_id, status):
        if not self.connected:
            return False
        try:
            self.sg.update("Task", task_id, {'sg_status_list': status})
            logger.info(f"Task {task_id} status updated to {status}.")
            return True
        except Exception as e:
            logger.error(f"Error updating task {task_id} to status {status}: {e}")
            return False

    def publish_version(self, task_id, filepath, version, comment):
        if not self.connected:
            return False
        try:
            task = self.sg.find_one("Task", [['id', 'is', task_id]], ['entity', 'project'])
            if not task:
                logger.error(f"Task {task_id} not found. Cannot publish version.")
                return False

            data = {
                'project': task['project'],
                'entity': task['entity'],
                'sg_task': task,
                'code': f"v{str(version).zfill(3)}",
                'description': comment,
                'sg_path_to_frames': filepath
            }
            
            new_version = self.sg.create("Version", data)
            logger.info(f"Successfully published Version {new_version['id']} for task {task_id}.")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing version: {e}")
            return False