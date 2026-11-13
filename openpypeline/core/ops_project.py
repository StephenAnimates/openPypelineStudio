"""
File: ops_project.py

Description: Project Management UI and backend logic for openPypeline Studio. Handles creating, editing, removing projects, and user management. Refactored from openPipelineProject.mel to Python 3.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
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
    """Returns the full path of the Project configuration file."""
    proj_path = prefs.get_pref("ops_projectFilePath", "")
    if not proj_path or str(proj_path).strip() in ["", "Not Set"]:
        return ""
    return os.path.join(proj_path, "openpypeline_projects.json").replace("\\", "/")


def get_projects_data():
    """Returns the full data of all existing projects as a list of dictionaries."""
    try:
        return read_projects_data()
    except (OSError, ValueError) as error:
        logger.error("Could not load the project registry: %s", error)
        return []


def read_projects_data():
    """Read the local registry strictly so write operations cannot erase bad data."""
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


def get_project_manifest_path(project_root):
    """Return the shared manifest path for a project root."""
    return os.path.join(
        os.path.abspath(os.path.expanduser(project_root)),
        PROJECT_MANIFEST_DIRECTORY,
        PROJECT_MANIFEST_FILENAME,
    )


def read_project_manifest(project_root):
    """Read and validate the versioned shared project manifest."""
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


def write_project_manifest(project_root, project_id, project_data):
    """Atomically write shared project settings without a machine-specific root path."""
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


def get_project(proj_name):
    """Returns the data for a single project as a dictionary."""
    proj_data = get_projects_data()
    for p in proj_data:
        if isinstance(p, dict) and p.get("name") == proj_name:
            return p
    return {}


def rewrite_proj_file(proj_list):
    """Rewrites the project JSON file with the given list of dictionaries."""
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
    """Retain the legacy project-UI close hook; it currently performs no action."""
    pass


def get_project_info_string(proj_name):
    """Returns a formatted string containing project details for the UI."""
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


def get_users():
    """Reads the users JSON file."""
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


def edit_users_save_file(users):
    """Updates user.json file with users, overwrites existing."""
    proj_path = prefs.get_pref("ops_projectFilePath", "")
    if not proj_path or str(proj_path).strip() in ["", "Not Set"]:
        logger.warning("Project file path is not set. Cannot save users.")
        return
    users_file = os.path.join(proj_path, "openpypeline_users.json").replace("\\", "/")
    try:
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save users file: {e}")


def proj_edit_users(*args):
    """Launches the PySide6 UI to edit global project users."""
    from PySide6 import QtWidgets

    class EditUsersDialog(QtWidgets.QDialog):
        """Dialog for adding and removing global project users."""

        def __init__(self, parent=None):
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
            self.user_list.clear()
            self.user_list.addItems(get_users())

        def on_add(self):
            name, ok = QtWidgets.QInputDialog.getText(self, "Add User", "Enter Name:")
            if ok and name.strip():
                users = get_users()
                if name.strip() not in users:
                    users.append(name.strip())
                    edit_users_save_file(users)
                    self._refresh_list()

        def on_remove(self):
            selected = [item.text() for item in self.user_list.selectedItems()]
            if selected:
                users = [user for user in get_users() if user not in selected]
                edit_users_save_file(users)
                self._refresh_list()

    dialog = EditUsersDialog()
    dialog.exec()