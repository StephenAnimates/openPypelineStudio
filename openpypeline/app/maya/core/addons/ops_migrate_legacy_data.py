"""
File: ops_migrate_legacy_data.py
Description: openPypeline Add-on for migrating legacy XML databases to JSON.
             Converts projects, users, and all history/note files.
"""

import os
import re
import json
from PySide6 import QtWidgets

ADDON_NAME = "Migrate Legacy XML Data"

def get_xml_tag(xml_string, tag):
    """Helper to extract the data encapsulated by an XML tag."""
    match = re.search(f"<{tag}>(.*?)</{tag}>", xml_string, re.IGNORECASE | re.DOTALL)
    if match:
        val = match.group(1).strip()
        if tag == "path":
            val = os.path.expandvars(val).replace("\\", "/")
        return val
    return ""

def run():
    """Executes the migration process."""
    # Prompt user for the directory containing the legacy XML files
    msg = "Select the directory containing your legacy 'openPipeline_projects.xml' file."
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(None, msg)
    
    if not dir_path:
        return
        
    dir_path = dir_path.replace("\\", "/")
    legacy_proj_file = os.path.join(dir_path, "openPipeline_projects.xml")
    legacy_users_file = os.path.join(dir_path, "openPipeline_users.xml")
    
    if not os.path.exists(legacy_proj_file):
        QtWidgets.QMessageBox.warning(None, "Migration Failed", f"Could not find openPipeline_projects.xml in:\n{dir_path}")
        return
        
    # 1. Migrate Projects
    migrated_projects = []
    try:
        with open(legacy_proj_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        projects = re.findall(r'<project>(.*?)</project>', content, re.DOTALL)
        for p_xml in projects:
            proj_dict = {
                "name": get_xml_tag(p_xml, "name"),
                "path": get_xml_tag(p_xml, "path"),
                "description": get_xml_tag(p_xml, "description"),
                "date": get_xml_tag(p_xml, "date"),
                "deadline": get_xml_tag(p_xml, "deadline"),
                "status": get_xml_tag(p_xml, "status") or "1",
                "mastername": get_xml_tag(p_xml, "mastername"),
                "masterformat": get_xml_tag(p_xml, "masterformat"),
                "wipname": get_xml_tag(p_xml, "wipname") or get_xml_tag(p_xml, "workshopname"),
                "wipformat": get_xml_tag(p_xml, "wipformat") or get_xml_tag(p_xml, "workshopformat"),
                "libraryfolder": get_xml_tag(p_xml, "libraryfolder"),
                "scenesfolder": get_xml_tag(p_xml, "scenesfolder"),
                "archivefolder": get_xml_tag(p_xml, "archivefolder"),
                "deletedfolder": get_xml_tag(p_xml, "deletedfolder"),
                "scriptsfolder": get_xml_tag(p_xml, "scriptsfolder"),
                "rendersfolder": get_xml_tag(p_xml, "rendersfolder"),
                "particlesfolder": get_xml_tag(p_xml, "particlesfolder"),
                "texturesfolder": get_xml_tag(p_xml, "texturesfolder"),
                "users": get_xml_tag(p_xml, "users"),
                "userMode": get_xml_tag(p_xml, "userMode") or "0"
            }
            migrated_projects.append(proj_dict)
            
        new_proj_file = os.path.join(dir_path, "openpypeline_projects.json")
        with open(new_proj_file, 'w', encoding='utf-8') as f:
            json.dump(migrated_projects, f, indent=4)
            
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Migration Error", f"Failed to migrate projects: {e}")
        return

    # 2. Migrate Users
    if os.path.exists(legacy_users_file):
        try:
            with open(legacy_users_file, 'r', encoding='utf-8') as f:
                users = [line.strip() for line in f if line.strip() and not line.startswith("<?xml") and not line.startswith("<")]
            
            new_users_file = os.path.join(dir_path, "openpypeline_users.json")
            with open(new_users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4)
        except Exception as e:
            print(f"Warning: Failed to migrate users file: {e}")
            
    # 3. Display Success & Note Migration Hint
    msg = (
        f"Migration Complete!\n\n"
        f"Converted {len(migrated_projects)} projects to JSON format.\n"
        f"Your original XML files have been left intact as backups.\n\n"
        f"IMPORTANT:\nIf you want to migrate all of your item history and custom notes, "
        f"please use the 'Migrate Notes' script located in the same Add-ons folder."
    )
    QtWidgets.QMessageBox.information(None, "Migration Successful", msg)
    
    # Refresh the UI if it is currently open
    try:
        from openpypeline.app.maya.ui import ui_objects as UIObjects
        ui_mgr = UIObjects.UIObjects()
        if hasattr(ui_mgr, 'opsProjectManagerController'):
            ui_mgr.opsProjectManagerController.on_refresh_list()
        if hasattr(ui_mgr, 'opsMainController'):
            ui_mgr.opsMainController.view.ops_refreshUIButton.click()
    except Exception:
        pass