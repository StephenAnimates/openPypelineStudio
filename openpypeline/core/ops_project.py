"""Project Management UI and backend logic for openPypeline Studio.

This file handles creating, editing, removing projects, and user management. Refactored from openPipelineProject.mel to Python 3.

:File: ops_project.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import os
import re
import json
import logging
import tempfile
from openpypeline.core.util import prefs

from . import ops_info as opsInfo
from ..app.maya.core import ops_utils as opsUtils
from . import ops_actions as opsActions

logger = logging.getLogger("openPypeline.project")

PROJECT_MANIFEST_DIRECTORY = ".openpypeline"
PROJECT_MANIFEST_FILENAME = "project.json"
PROJECT_MANIFEST_SCHEMA_VERSION = 1
PROJECT_CONFIG_FIELDS = (
    "name",
    "description",
    "date",
    "deadline",
    "status",
    "mastername",
    "masterformat",
    "wipname",
    "wipformat",
    "libraryfolder",
    "scenesfolder",
    "archivefolder",
    "deletedfolder",
    "scriptsfolder",
    "rendersfolder",
    "particlesfolder",
    "texturesfolder",
    "users",
    "userMode",
)
PROJECT_FOLDER_FIELDS = (
    "libraryfolder",
    "scenesfolder",
    "archivefolder",
    "deletedfolder",
    "scriptsfolder",
    "rendersfolder",
    "particlesfolder",
    "texturesfolder",
)


def get_proj_file():
    """Gets the set project registry file path from user preferences.

    :returns: The normalized path to ``openpypeline_projects.json``, or an empty string if unset.
    :note: The path is derived from the user preference "ops_projectFilePath" and does not include the filename itself.
    """
    proj_path = prefs.get_pref("ops_projectFilePath", "")
    if not proj_path or str(proj_path).strip() in ["", "Not Set"]:
        return ""
    return os.path.join(proj_path, "openpypeline_projects.json").replace("\\", "/")

def get_projects_data() -> list[dict]:
    """Gets the list of projects from the local registry file.

    :returns: A list of project dictionaries, or an empty list if loading fails.
    :note: This function may raise exceptions if the project file is malformed.
    """
    try:
        return read_projects_data()
    except (OSError, ValueError) as error:
        logger.error("Could not load the project registry: %s", error)
        return []

def read_projects_data():
    """Reads the local registry strictly so write operations cannot erase bad data.

    :returns: A list of project dictionaries.
    :raises ValueError: If the registry file is malformed or contains invalid data.
    :note: This function may raise exceptions if the project file is malformed.
    """
    proj_file = get_proj_file()
    if not proj_file:
        return []
    if os.path.isfile(proj_file):
        try:
            with open(proj_file, 'r', encoding="utf-8") as f:
                projects = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise ValueError(f"Could not read the local projects file: {proj_file}") from e
        if not isinstance(projects, list) or not all(isinstance(project, dict) for project in projects):
            raise ValueError(f"The local projects file must contain a list of project objects: {proj_file}")
        return projects
    else:
        proj_dir = os.path.dirname(proj_file)
        if proj_dir:
            try:
                os.makedirs(proj_dir, exist_ok=True)
                with open(proj_file, 'w', encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except OSError as e:
                logger.error("Project file could not be created at %s: %s", proj_file, e)
                raise
    return []


def get_project_manifest_path(project_root: str) -> str:
    """Gets the full path to the shared project manifest file.

    :param project_root: The root directory path of the project.
    :returns: The full normalized path to the project manifest file.
    :note: The manifest is stored in a hidden subdirectory to avoid cluttering the project root.
    """
    return os.path.join(
        os.path.abspath(os.path.expanduser(project_root)),
        PROJECT_MANIFEST_DIRECTORY,
        PROJECT_MANIFEST_FILENAME,
    )

def read_project_manifest(project_root: str) -> dict:
    """Reads and validates the versioned shared project manifest.

    :param project_root: The root directory path of the project.
    :returns: A dictionary containing the project manifest data.
    :raises FileNotFoundError: If no project manifest is found at the specified path.
    :raises ValueError: If the project manifest is malformed or contains invalid data.
    :note: This function may raise exceptions if the project manifest is malformed.
    """
    manifest_path = get_project_manifest_path(project_root)
    try:
        with open(manifest_path, "r", encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"No openPypeline project manifest found at {manifest_path}") from None
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read the project manifest at {manifest_path}: {error}") from error

    if not isinstance(manifest, dict):
        raise ValueError("The project manifest must contain a JSON object.")
    if manifest.get("schema_version") != PROJECT_MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported project manifest schema version: {manifest.get('schema_version')!r}"
        )
    project_id = manifest.get("project_id")
    project = manifest.get("project")
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("The project manifest is missing a valid project_id.")
    if not isinstance(project, dict) or not isinstance(project.get("name"), str) or not project["name"].strip():
        raise ValueError("The project manifest is missing a valid project name.")
    if "path" in project:
        raise ValueError("The shared project manifest must not contain a machine-specific project path.")
    return manifest


def write_project_manifest(project_root: str, project_id: str, project_data: dict) -> bool:
    """Atomically write shared project settings without a machine-specific root path.

    :param project_root: The root directory path of the project.
    :param project_id: The ID of the project.
    :param project_data: A dictionary containing the project settings.
    :returns: True if the manifest was written successfully, False otherwise.
    :note: This function creates a temporary file and replaces the manifest to ensure atomicity.
    """
    manifest_path = get_project_manifest_path(project_root)
    shared_project = {
        field: project_data[field]
        for field in PROJECT_CONFIG_FIELDS
        if field in project_data
    }
    manifest = {
        "schema_version": PROJECT_MANIFEST_SCHEMA_VERSION,
        "project_id": project_id,
        "project": shared_project,
    }
    temporary_path = None
    try:
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(manifest_path),
            prefix=".project.",
            suffix=".tmp",
            delete=False,
        ) as manifest_file:
            temporary_path = manifest_file.name
            json.dump(manifest, manifest_file, indent=4)
            manifest_file.write("\n")
        os.replace(temporary_path, manifest_path)
    except (OSError, TypeError) as error:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError as cleanup_error:
                logger.warning("Could not remove temporary manifest %s: %s", temporary_path, cleanup_error)
        logger.error("Failed to write project manifest at %s: %s", manifest_path, error)
        return False
    return True


def get_project(proj_name: str) -> dict:
    """Get the project data for a specific project by name.
    
    :param proj_name: The name of the project to retrieve.
    :returns: A dictionary containing the project data, or an empty dictionary if not found.
    :note: This function may raise exceptions if the project file is malformed.
    """
    proj_data = get_projects_data()
    for p in proj_data:
        if isinstance(p, dict) and p.get("name") == proj_name:
            return p
    return {}


def rewrite_proj_file(proj_list: list) -> bool:
    """Rewrites the project JSON file with the given list of dictionaries.
    
    :param proj_list: A list of dictionaries representing the projects to write.
    :returns: True if the file was written successfully, False otherwise.
    :note: This function creates a temporary file and replaces the project file to ensure atomicity.
    """
    proj_file = get_proj_file()
    if not proj_file:
        logger.error("Project file path is not set. Please use 'Edit Locations...' to set it.")
        return False
    temporary_path = None
    try:
        os.makedirs(os.path.dirname(proj_file), exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(proj_file),
            prefix=".projects.",
            suffix=".tmp",
            delete=False,
        ) as project_file:
            temporary_path = project_file.name
            json.dump(proj_list, project_file, indent=4)
            project_file.write("\n")
        os.replace(temporary_path, proj_file)
    except (OSError, TypeError) as error:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError as cleanup_error:
                logger.warning("Could not remove temporary project file %s: %s", temporary_path, cleanup_error)
        logger.error("Project file %s could not be written: %s", proj_file, error)
        return False
    return True


def close_proj_ui(*args):
    """Close the project management UI dialog.

    :param args: Optional arguments for compatibility with UI callbacks.
    :note: This function requires a running Qt application context.
    """
    pass


def get_project_info_string(proj_name: str) -> str:
    """Get the project information as a formatted string for display.

    :param proj_name: The name of the project for which to retrieve information.
    :returns: A formatted string containing the project details.
    :note: This function may raise exceptions if the project file is malformed.
    """
    proj = get_project(proj_name)
    if not proj: return ""
    
    status_str = ["inactive", "active"][int(proj.get("status") or 1)]
    
    info = (
        f"Project Name: {proj.get('name', '')}\n"
        f"Path: {proj.get('path', '')}\n"
        f"Description: {proj.get('description', '')}\n"
        f"Status: {status_str}\n"
        f"-------------------------------------\n"
        f"Date Created: {proj.get('date', '')}\n"
        f"Deadline: {proj.get('deadline', '')}\n"
        f"-------------------------------------\n"
        f"Master Files:\nname - {proj.get('mastername', '')}\nformat - {proj.get('masterformat', '')}\n"
        f"Workshop Files:\nname - {proj.get('wipname', '')}\nformat - {proj.get('wipformat', '')}\n"
        f"-------------------------------------\n"
        f"Library Sub-folder:    {proj.get('libraryfolder', '')}\n"
        f"Shots Sub-folder:      {proj.get('scenesfolder', '')}\n"
        f"Scripts Sub-folder:    {proj.get('scriptsfolder', '')}\n"
        f"Renders Sub-folder:    {proj.get('rendersfolder', '')}\n"
        f"Textures Sub-folder:   {proj.get('texturesfolder', '')}\n"
        f"Particles Sub-folder:  {proj.get('particlesfolder', '')}\n"
        f"Archive folder:        {proj.get('archivefolder', '')}\n"
        f"Deleted Items folder:  {proj.get('deletedfolder', '')}\n"
        f"Users:  {proj.get('users', '')}\n"
    )
    
    return info


def get_users() -> list:
    """Get the list of global project users from the users.json file.

    :returns: A list of user names, or an empty list if the file is missing or unreadable.
    :note: This function may raise exceptions if the users file is malformed.
    """
    proj_path = prefs.get_pref("ops_projectFilePath", "")
    if not proj_path or str(proj_path).strip() in ["", "Not Set"]:
        return []
    users_file = os.path.join(proj_path, "openpypeline_users.json").replace("\\", "/")
    if os.path.isfile(users_file):
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def edit_users_save_file(users: list):
    """Edit the global project users file with the provided list of users.

    :param users: A list of user names to save.
    :returns: True if the file was saved successfully, False otherwise.
    :note: This function may raise exceptions if the users file is malformed.
    """
    proj_path = prefs.get_pref("ops_projectFilePath", "")
    if not proj_path or str(proj_path).strip() in ["", "Not Set"]:
        logger.warning("Project file path is not set. Cannot save users.")
        return False
    users_file = os.path.join(proj_path, "openpypeline_users.json").replace("\\", "/")
    try:
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save users file: {e}")
        return False
    return True


def proj_edit_users(*args):
    """Edit the global project users through a simple dialog interface.

    :param args: Optional arguments for compatibility with UI callbacks.
    :returns: True if the dialog was accepted, False otherwise.
    :note: This function requires a running Qt application context.
    """
    from PySide6 import QtWidgets

    class EditUsersDialog(QtWidgets.QDialog):
        """Dialog for adding and removing global project users.

        :returns: True if the dialog was accepted, False otherwise.
        :note: This dialog does not validate user names or check for duplicates beyond simple string matching.
        """

        def __init__(self, parent=None):
            """Initialize the dialog with a list of users and buttons for adding/removing users.

            :param parent: The parent widget for the dialog, if any.
            :note: This dialog requires a running Qt application context.
            """
            super().__init__(parent)
            self.setWindowTitle("Add / Remove Users")
            self.setMinimumSize(340, 230)

            layout = QtWidgets.QVBoxLayout(self)
            self.user_list = QtWidgets.QListWidget()
            self.user_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self._refresh_list()
            layout.addWidget(self.user_list)

            button_layout = QtWidgets.QHBoxLayout()
            self.add_btn = QtWidgets.QPushButton("Add user")
            self.remove_btn = QtWidgets.QPushButton("Remove Selected")
            self.close_btn = QtWidgets.QPushButton("Close")
            self.add_btn.clicked.connect(self.on_add)
            self.remove_btn.clicked.connect(self.on_remove)
            self.close_btn.clicked.connect(self.accept)
            button_layout.addWidget(self.add_btn)
            button_layout.addWidget(self.remove_btn)
            button_layout.addWidget(self.close_btn)
            layout.addLayout(button_layout)

        def _refresh_list(self):
            """Refresh the list of users displayed in the dialog.

            :note: This method clears and repopulates the list widget with the current users.
            """
            self.user_list.clear()
            self.user_list.addItems(get_users())

        def on_add(self):
            """Prompt the user to add a new user name to the list.
            :note: This method does not validate the input beyond checking for non-empty strings.
            """
            name, ok = QtWidgets.QInputDialog.getText(self, "Add User", "Enter Name:")
            if ok and name.strip():
                users = get_users()
                if name.strip() not in users:
                    users.append(name.strip())
                    edit_users_save_file(users)
                    self._refresh_list()

        def on_remove(self):
            """Remove the selected users from the list.

            :note: This method does not validate the selection beyond ensuring items are selected.
            """
            selected = [item.text() for item in self.user_list.selectedItems()]
            if selected:
                users = [user for user in get_users() if user not in selected]
                edit_users_save_file(users)
                self._refresh_list()

    dialog = EditUsersDialog()
    return dialog.exec()