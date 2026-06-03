"""
File: ops_project.py

Description:
    Project Management UI and backend logic for openPypeline Studio.
    Handles creating, editing, removing projects, and user management.
    Refactored from openPipelineProject.mel to Python 3.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)

"""

import os
import re
import json
import logging
from openpypeline.core.util import prefs
from PySide6 import QtWidgets, QtCore

from . import ops_info as opsInfo
from ..app.maya.core import ops_utils as opsUtils
from . import ops_actions as opsActions

logger = logging.getLogger("openPypeline.project")


def get_proj_file():
    """Returns the full path of the Project configuration file."""
    proj_path = prefs.get_pref("ops_projectFilePath", "")
    if not proj_path or str(proj_path).strip() in ["", "Not Set"]:
        return ""
    return os.path.join(proj_path, "openpypeline_projects.json").replace("\\", "/")


def get_projects_data():
    """Returns the full data of all existing projects as a list of dictionaries."""
    proj_file = get_proj_file()
    if not proj_file:
        return []
    if os.path.isfile(proj_file):
        try:
            with open(proj_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse JSON projects file: {e}")
    else:
        proj_dir = os.path.dirname(proj_file)
        if proj_dir:
            try:
                os.makedirs(proj_dir, exist_ok=True)
                with open(proj_file, 'w', encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except Exception as e:
                logger.error(f"Project File does not exist, could not be opened, or could not be created: {e}")
    return []


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
        return
    try:
        with open(proj_file, 'w', encoding="utf-8") as f:
            json.dump(proj_list, f, indent=4)
    except Exception as e:
        logger.error(f"Project File {proj_file} could not be found, or is not writable: {e}")


def close_proj_ui(*args):
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


class EditUsersDialog(QtWidgets.QDialog):
    """PySide6 Dialog for adding and removing global project users."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Remove Users")
        self.setMinimumSize(340, 230)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.user_list = QtWidgets.QListWidget()
        self.user_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._refresh_list()
        layout.addWidget(self.user_list)
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add user")
        self.remove_btn = QtWidgets.QPushButton("Remove Selected")
        self.close_btn = QtWidgets.QPushButton("Close")
        
        self.add_btn.clicked.connect(self.on_add)
        self.remove_btn.clicked.connect(self.on_remove)
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
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
        if not selected: return
        
        users = get_users()
        users = [u for u in users if u not in selected]
        edit_users_save_file(users)
        self._refresh_list()


def proj_edit_users(*args):
    """Launches the PySide6 UI to edit global project users."""
    dialog = EditUsersDialog()
    dialog.exec()