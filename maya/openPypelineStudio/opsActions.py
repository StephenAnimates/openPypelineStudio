"""
File: opsActions.py
Description: Core actions and functional operations for openPypeline Studio.
             Handles creation, file operations, referencing, importing, and history.
             Refactored from openPipelineActions.mel to use modern Python libraries.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import os
import re
import logging
from openpypeline.core.util import prefs

logger = logging.getLogger("openPypeline.actions")

import opsInfo
import opsLoader
import opsUtils
import opsProject


def activate_project(proj_name):
    """Selects a project to work in and updates all associated optionVars and workspaces."""
    proj_xml = opsProject.get_single_project_xml(proj_name)
    proj_path = opsUtils.get_xml_data(proj_xml, "path")
    
    if proj_path and not proj_path.endswith('/'):
        proj_path += '/'
        
    if os.path.isdir(proj_path):
        proj_lib = opsUtils.get_xml_data(proj_xml, "libraryfolder")
        proj_shots = opsUtils.get_xml_data(proj_xml, "scenesfolder")
        proj_scripts = opsUtils.get_xml_data(proj_xml, "scriptsfolder")
        proj_renders = opsUtils.get_xml_data(proj_xml, "rendersfolder")
        proj_particles = opsUtils.get_xml_data(proj_xml, "particlesfolder")
        proj_textures = opsUtils.get_xml_data(proj_xml, "texturesfolder")
        proj_archive = opsUtils.get_xml_data(proj_xml, "archivefolder")
        proj_deleted = opsUtils.get_xml_data(proj_xml, "deletedfolder")
        proj_m_format = opsUtils.get_xml_data(proj_xml, "masterformat")
        proj_w_format = opsUtils.get_xml_data(proj_xml, "wipformat") or opsUtils.get_xml_data(proj_xml, "workshopformat")
        proj_m_name = opsUtils.get_xml_data(proj_xml, "mastername")
        proj_w_name = opsUtils.get_xml_data(proj_xml, "wipname") or opsUtils.get_xml_data(proj_xml, "workshopname")
        proj_users = opsUtils.get_xml_data(proj_xml, "users")

        lib_path = os.path.join(proj_path, proj_lib, "").replace("\\", "/")
        shot_path = os.path.join(proj_path, proj_shots, "").replace("\\", "/")
        scripts_path = os.path.join(proj_path, proj_scripts, "").replace("\\", "/")
        renders_path = os.path.join(proj_path, proj_renders, "").replace("\\", "/")
        particles_path = os.path.join(proj_path, proj_particles, "").replace("\\", "/")
        textures_path = os.path.join(proj_path, proj_textures, "").replace("\\", "/")
        
        archive_path = proj_archive if os.path.isdir(proj_archive) else os.path.join(proj_path, proj_archive)
        archive_path = os.path.join(archive_path, "").replace("\\", "/")
        
        delete_path = proj_deleted if os.path.isdir(proj_deleted) else os.path.join(proj_path, proj_deleted)
        delete_path = os.path.join(delete_path, "").replace("\\", "/")

        prefs.set_pref("ops_currProjectName", proj_name)
        prefs.set_pref("ops_currProjectPath", proj_path)
        prefs.set_pref("ops_libPath", lib_path)
        prefs.set_pref("ops_shotPath", shot_path)
        prefs.set_pref("ops_scriptsPath", scripts_path)
        prefs.set_pref("ops_rendersPath", renders_path)
        prefs.set_pref("ops_particlesPath", particles_path)
        prefs.set_pref("ops_texturesPath", textures_path)
        prefs.set_pref("ops_masterFormat", proj_m_format)
        prefs.set_pref("ops_wipFormat", proj_w_format)
        prefs.set_pref("ops_masterName", proj_m_name)
        prefs.set_pref("ops_wip", proj_w_name)
        prefs.set_pref("ops_deletePath", delete_path)
        prefs.set_pref("ops_archivePath", archive_path)
        prefs.set_pref("ops_users", proj_users)

        if proj_scripts:
            opsLoader.source_mel_module(scripts_path)
            cmds.workspace(fileRule=['mel', proj_scripts])
            
        cmds.workspace(fileRule=['scene', proj_shots])
        
        if proj_textures:
            cmds.workspace(fileRule=['textures', proj_textures])
        if proj_particles:
            cmds.workspace(fileRule=['particles', proj_particles])
        if proj_renders:
            cmds.workspace(fileRule=['renderScenes', proj_renders])

        cmds.workspace(proj_path, openWorkspace=True)
        return 1
    else:
        logger.warning(f"Couldn't select project '{proj_name}'. Path '{proj_path}' couldn't be found.")
        return 0


def create_or_edit_project(mode, old_name, new_name, new_path, new_description, new_status, new_date, new_deadline, new_master_name, new_master_format, new_wip_name, new_wip_format, new_lib_loc, new_shot_loc, new_renders_loc, new_scripts_loc, new_textures_loc, new_particles_loc, new_archive_loc, new_deleted_loc, new_users, user_mode):
    """Creates a new project or edits the properties of an existing project."""
    mode_names = ["created", "edited"]
    active_project_name = prefs.get_pref("ops_currProjectName", "")
    proj_data = opsProject.get_projects_data() or []
    error = ""
    
    # Input validations
    if len(new_name) > 22: error += "Project name cannot exceed 22 characters.\n"
    if len(new_master_name) > 18: error += "Master name cannot exceed 18 characters.\n"
    if len(new_wip_name) > 18: error += "WIP file name cannot exceed 18 characters.\n"
    if len(new_lib_loc) > 22: error += "Library sub-folder name cannot exceed 22 characters.\n"
    if len(new_shot_loc) > 22: error += "Shot sub-folder name cannot exceed 22 characters.\n"
    if len(new_scripts_loc) > 22: error += "Scripts sub-folder name cannot exceed 22 characters.\n"
    if len(new_renders_loc) > 22: error += "Renders sub-folder name cannot exceed 22 characters.\n"
    if len(new_particles_loc) > 22: error += "Particles sub-folder name cannot exceed 22 characters.\n"
    if len(new_textures_loc) > 22: error += "Textures sub-folder name cannot exceed 22 characters.\n"
    if len(new_date) > 18: error += "Date cannot exceed 18 characters.\n"
    if len(new_deadline) > 18: error += "Deadline exceeds 18 characters.\n"
    if len(new_description) > 250: error += "Description exceeds 250 characters.\n"

    test_path = new_path.rstrip(new_name).rstrip("/").rstrip("\\")
    if not os.path.exists(test_path):
        error += "Project path is not valid (a valid base path is required).\n"
        
    valid_pattern = re.compile(r"^[a-zA-Z0-9_]*$")
    if not valid_pattern.match(new_name): error += "Project name is not valid (remove spaces and special characters).\n"
    if not valid_pattern.match(new_master_name): error += "Master name is not valid (remove spaces and special characters).\n"
    if not valid_pattern.match(new_wip_name): error += "WIP file name is not valid (remove spaces and special characters).\n"

    valid_folder_pattern = re.compile(r"^[a-zA-Z0-9_/]*$")
    if not valid_folder_pattern.match(new_lib_loc): error += "Library sub-folder is not valid (remove spaces and special characters, slashes are allowed).\n"
    if not valid_folder_pattern.match(new_shot_loc): error += "Shot sub-folder is not valid (remove spaces and special characters, slashes are allowed).\n"
    if not valid_folder_pattern.match(new_textures_loc): error += "Textures sub-folder is not valid (remove spaces and special characters, slashes are allowed).\n"
    if not valid_folder_pattern.match(new_scripts_loc): error += "Scripts sub-folder is not valid (remove spaces and special characters, slashes are allowed).\n"
    if not valid_folder_pattern.match(new_renders_loc): error += "Renders sub-folder is not valid (remove spaces and special characters, slashes are allowed).\n"
    if not valid_folder_pattern.match(new_particles_loc): error += "Particles sub-folder is not valid (remove spaces and special characters, slashes are allowed).\n"
    
    new_path = os.path.join(new_path, "").replace("\\", "/")
    test_folders = [new_particles_loc, new_renders_loc, new_scripts_loc, new_textures_loc, new_shot_loc, new_lib_loc, new_archive_loc, new_deleted_loc]
    if len(test_folders) != len(set(test_folders)):
        error += "Sub-folders must have unique names.\n"
        
    os.makedirs(new_path, exist_ok=True)
    if os.path.exists(new_path):
        try: os.makedirs(new_archive_loc if os.path.isabs(new_archive_loc) else os.path.join(new_path, new_archive_loc), exist_ok=True)
        except Exception: error += "Archive Path is invalid. It does not exist and could not be created.\n"
        
        try: os.makedirs(new_deleted_loc if os.path.isabs(new_deleted_loc) else os.path.join(new_path, new_deleted_loc), exist_ok=True)
        except Exception: error += "Deleted Items Path is invalid. It does not exist and could not be created.\n"
        
        for loc in [new_lib_loc, new_shot_loc, new_textures_loc, new_renders_loc, new_scripts_loc, new_particles_loc]:
            try: os.makedirs(os.path.join(new_path, loc), exist_ok=True)
            except Exception: error += f"{loc} Sub-folder is invalid. It does not exist and could not be created.\n"
    else:
        error += "Project Path is invalid. It does not exist and could not be created.\n"

    found = False
    for project in proj_data:
        curr_proj_name = opsUtils.get_xml_data(project, "name")
        if new_name == curr_proj_name and curr_proj_name != old_name:
            found = True
            break
            
    if found:
        error += "Project name already exists. Please try a different name."

    if not error:
        new_line = f"<name>{new_name}</name><path>{new_path}</path><description>{new_description}</description>" \
                   f"<date>{new_date}</date><deadline>{new_deadline}</deadline><status>{new_status}</status>" \
                   f"<mastername>{new_master_name}</mastername><masterformat>{new_master_format}</masterformat>" \
                   f"<wipname>{new_wip_name}</wipname><wipformat>{new_wip_format}</wipformat>" \
                   f"<libraryfolder>{new_lib_loc}</libraryfolder><scenesfolder>{new_shot_loc}</scenesfolder>" \
                   f"<archivefolder>{new_archive_loc}</archivefolder><deletedfolder>{new_deleted_loc}</deletedfolder>" \
                   f"<scriptsfolder>{new_scripts_loc}</scriptsfolder><rendersfolder>{new_renders_loc}</rendersfolder>" \
                   f"<particlesfolder>{new_particles_loc}</particlesfolder><texturesfolder>{new_textures_loc}</texturesfolder>" \
                   f"<users>{new_users}</users><userMode>{user_mode}</userMode>"
                   
        index = -1
        if not mode:
            index = len(proj_data)
            proj_data.append(new_line)
        else:
            for i, project in enumerate(proj_data):
                if opsUtils.get_xml_data(project, "name") == old_name:
                    index = i
                    break
            if index == -1:
                logger.error(f"Couldn't edit Project. Can't find Project with name '{old_name}'.")
                return 0
            proj_data[index] = new_line
            
        opsProject.rewrite_proj_file(proj_data)
        
        if active_project_name == old_name:
            prefs.set_pref("ops_currProjectName", new_name)
            activate_project(new_name)
            
        logger.info(f"Project {mode_names[mode]}.")
        return 1
    else:
        logger.error(f"Project could not be {mode_names[mode]} because:\n{error}")
        return 0


def remove_project(proj_name):
    """Removes a project from the openPypeline list (files remain intact)."""
    curr_project_name = prefs.get_pref("ops_currProjectName", "")
    projects_data = opsProject.get_projects_data() or []
    new_projects_data = []
    removed = False
    
    for project in projects_data:
        if opsUtils.get_xml_data(project, "name") != proj_name:
            new_projects_data.append(project)
        else:
            removed = True
            
    if removed:
        if curr_project_name == proj_name:
            prefs.set_pref("ops_currProjectName", "")
            prefs.set_pref("ops_currProjectPath", "")
        opsProject.rewrite_proj_file(new_projects_data)
    else:
        logger.warning(f"Couldn't remove project '{proj_name}'. Project not found.")
        
    return int(removed)


def create_new_item(tab, level1, level2, level3, mode):
    """Creates a new item within the currently active project."""
    error = ""
    item_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    depth = sum(1 for lvl in [level1, level2, level3] if lvl)
    item_name = os.path.basename(item_path.rstrip('/'))
    parent_path = opsInfo.get_file_name(tab, level1, level2, level3, "parentFolder")
    version_folder = opsInfo.get_file_name(tab, level1, level2, level3, "versionFolder")
    component_folder = opsInfo.get_file_name(tab, level1, level2, level3, "componentFolder")
    note_folder = opsInfo.get_file_name(tab, level1, level2, level3, "noteFolder")
    wip_folder = opsInfo.get_file_name(tab, level1, level2, level3, "workshopFolder")
    destination_file = opsInfo.get_file_name(tab, level1, level2, level3, "nextWorkshop")
    category = opsInfo.get_category(tab, level1, level2, level3)
    w_name = prefs.get_pref("ops_wip", "wip")

    if depth and item_path:
        if not re.match(r"^[a-zA-Z0-9_]*$", item_name):
            error += f"Invalid {category} Name (no special characters or spaces allowed).\n"
        elif os.path.isdir(item_path):
            error += f"{category} '{item_name}' already exists!\n"
        elif not os.path.isdir(parent_path):
            if depth == opsInfo.LEVEL_2: create_new_item(tab, level1, "", "", 1)
            elif depth == opsInfo.LEVEL_3: create_new_item(tab, level1, level2, "", 1)
            else: error += f"Item '{parent_path}' doesn't exist. Can't create new {category} under it.\n"
        
        if error:
            logger.warning(error.strip())
            return ""
            
        os.makedirs(item_path, exist_ok=True)
        if depth == opsInfo.LEVEL_2: os.makedirs(component_folder, exist_ok=True)
        if depth >= opsInfo.LEVEL_2:
            os.makedirs(wip_folder, exist_ok=True)
            os.makedirs(version_folder, exist_ok=True)
            os.makedirs(note_folder, exist_ok=True)

            prefs.set_pref("ops_creationPath", f"{item_path}/")
            prefs.set_pref("ops_creationType", category)
            
            add_event_note(tab, level1, level2, level3, "created", 0, "")
            
            ext = prefs.get_pref("ops_wipFormat", "ma")
            file_type_map = {"ma": "mayaAscii", "mb": "mayaBinary", "usd": "USD Export", "usda": "USD Export", "abc": "Alembic"}
            file_type = file_type_map.get(ext, "mayaBinary")

            import opsEngine
            engine = opsEngine.OpsEngine()

            if mode == 2:
                if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
                    engine.file_handler.export_file(destination_file, file_type, selected=True)
                add_event_note(tab, level1, level2, level3, w_name, 1, f"Selection exported as first {w_name} file.")
            elif mode == 3:
                if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
                    engine.file_handler.export_file(destination_file, file_type, selected=False)
                add_event_note(tab, level1, level2, level3, w_name, 1, f"Scene exported as first {w_name} file.")
            
            set_custom_notes(tab, level1, level2, level3, " ")
        return item_path
    else:
        logger.warning("Parameters incorrect, no new item created.")
        return ""


def open_item(item_type, tab, level1, level2, level3, version_offset):
    """Opens an item for editing."""
    folder = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    depth = sum(1 for lvl in [level1, level2, level3] if lvl)
    
    if depth >= opsInfo.LEVEL_2 and os.path.isdir(folder) and item_type in ["workshop", "master"]:
        version = 0
        curr_level1 = prefs.get_pref("ops_currOpenLevel1", "")
        
        if cmds.file(query=True, modified=True) and curr_level1:
            w_name = prefs.get_pref("ops_wip", "wip")
            confirm = cmds.confirmDialog(
                title="openPypeline Studio",
                message=f"Would you like to Save {w_name} before editing Asset?",
                button=["Save", "Don't Save", "Cancel"],
                defaultButton="Save"
            )
            if confirm == "Save":
                    save_wip("saved before opening new item")
            elif confirm == "Cancel":
                return 0
                
        file_to_open = opsInfo.get_file_name(tab, level1, level2, level3, item_type, version_offset)
        latest_wip = opsInfo.get_file_name(tab, level1, level2, level3, item_type)
        category = opsInfo.get_category(tab, level1, level2, level3)
        
        if os.path.isfile(file_to_open):
            version = opsInfo.get_version_from_file(file_to_open)
            import opsEngine
            engine = opsEngine.OpsEngine()
            if engine.file_handler and hasattr(engine.file_handler, 'open'):
                engine.file_handler.open(file_to_open)
            else:
                logger.warning("No DCC file handler available to open files.")
        elif item_type == "workshop" and not os.path.isfile(latest_wip):
            choice = cmds.confirmDialog(
                title="Edit Asset",
                message="You are about to edit an item for the first time. Would you like to start with a new scene, or the currently open scene?",
                button=["New Scene", "Current Scene", "Cancel"],
                cancelButton="Cancel",
                defaultButton="Current Scene"
            )
            if choice == "New Scene":
                import opsEngine
                engine = opsEngine.OpsEngine()
                if engine.file_handler and hasattr(engine.file_handler, 'new_file'):
                    engine.file_handler.new_file()
            elif choice == "Cancel":
                return 0
        else:
            logger.warning("File Not Found")
            return 0
            
        prefs.set_pref("ops_currOpenType", item_type)
        prefs.set_pref("ops_currOpenVersion", version)
        prefs.set_pref("ops_currOpenCategory", category)
        prefs.set_pref("ops_currOpenLevel1", level1)
        prefs.set_pref("ops_currOpenLevel2", level2)
        prefs.set_pref("ops_currOpenLevel3", level3)
        prefs.set_pref("ops_currOpenTab", tab)
    else:
        logger.warning("Invalid command or Item doesn't exist.")
        return 0
    return 1


def import_item(item_type, tab, level1, level2, level3, flags=""):
    """Imports an item into the current scene."""
    file_path = opsInfo.get_file_name(tab, level1, level2, level3, item_type)
    if os.path.isfile(file_path):
        import opsEngine
        engine = opsEngine.OpsEngine()
        if engine.file_handler and hasattr(engine.file_handler, 'import_file'):
            return int(engine.file_handler.import_file(file_path))
        else:
            logger.warning("No DCC file handler available for import.")
            return 0
    else:
        logger.warning(f"Could not find file to import: {file_path}")
        return 0


def reference_item(item_type, tab, level1, level2, level3, flags=""):
    """References an item into the current scene."""
    file_path = opsInfo.get_file_name(tab, level1, level2, level3, item_type)
    if os.path.isfile(file_path):
        import opsEngine
        engine = opsEngine.OpsEngine()
        if engine.file_handler and hasattr(engine.file_handler, 'reference_file'):
            return int(engine.file_handler.reference_file(file_path))
        else:
            logger.warning("No DCC file handler available for reference.")
            return 0
    else:
        logger.warning(f"Could not find file to reference: {file_path}")
        return 0




def save_workshop(note=""):
    """Saves a workshop for the currently open item."""
    ext = prefs.get_pref("ops_wipFormat", "ma")
    w_name = prefs.get_pref("ops_wip", "wip")
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    tab = prefs.get_pref("ops_currOpenTab", 0)
    
    destination_file = opsInfo.get_file_name(tab, level1, level2, level3, "nextWorkshop")
    
    file_type_map = {"ma": "mayaAscii", "mb": "mayaBinary", "usd": "USD Export", "usda": "USD Export", "abc": "Alembic"}
    file_type = file_type_map.get(ext, "mayaBinary")
    if ext not in file_type_map:
        logger.warning(f"Invalid file format ({ext}) specified: saving to Maya Binary")
        
    import opsEngine
    engine = opsEngine.OpsEngine()
    
    if file_type in ["USD Export", "Alembic"]:
        if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
            engine.file_handler.export_file(destination_file, file_type, selected=False)
        else:
            logger.warning("No DCC file handler available for exporting files.")
    else:
        if engine.file_handler and hasattr(engine.file_handler, 'save_as'):
            engine.file_handler.save_as(destination_file, file_type)
        else:
            logger.warning("No DCC file handler available for saving files.")
    latest_version = opsInfo.get_version_from_file(destination_file)
    prefs.set_pref("ops_currOpenVersion", latest_version)
    add_event_note(tab, level1, level2, level3, w_name, latest_version, note)
    return 1


def save_master(comment, flatten, delete_disp_layers, after, custom_command="", task_id=0):
    """Saves a master for the currently open item."""
    ext = prefs.get_pref("ops_masterFormat", "ma")
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    tab = prefs.get_pref("ops_currOpenTab", 0)
    master_name = prefs.get_pref("ops_masterName", "master")
    
    master_file = opsInfo.get_file_name(tab, level1, level2, level3, "master")
    destination_file = opsInfo.get_file_name(tab, level1, level2, level3, "nextVersion")
    
    save_wip(comment)
    
    if os.path.exists(master_file):
        os.rename(master_file, destination_file)
        
    import opsEngine
    engine = opsEngine.OpsEngine()
    
    if flatten and engine.file_handler and hasattr(engine.file_handler, 'flatten_references'):
        w_name = prefs.get_pref("ops_wip", "wip")
        engine.file_handler.flatten_references(master_name, w_name)
        
    if delete_disp_layers and engine.file_handler and hasattr(engine.file_handler, 'delete_display_layers'):
        engine.file_handler.delete_display_layers()
                
    if custom_command:
        logger.info(f"Begin custom command {custom_command}")
        try: exec(custom_command)
        except Exception as e: logger.warning(f"Custom command failed: {e}")
        logger.info(f"End custom command {custom_command}")
        
    file_type_map = {"ma": "mayaAscii", "mb": "mayaBinary", "usd": "USD Export", "usda": "USD Export", "abc": "Alembic"}
    file_type = file_type_map.get(ext, "mayaBinary")
    
    if file_type in ["USD Export", "Alembic"]:
        if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
            engine.file_handler.export_file(master_file, file_type, selected=False)
    else:
        if engine.file_handler and hasattr(engine.file_handler, 'save_as'):
            engine.file_handler.save_as(master_file, file_type)
    
    if after == 1: open_item("workshop", tab, level1, level2, level3, 0)
    elif after == 2: prefs.set_pref("ops_currOpenType", "master")
    elif after == 3:
        close_file()
        if engine.file_handler and hasattr(engine.file_handler, 'new_file'):
            engine.file_handler.new_file()
        
    add_event_note(tab, level1, level2, level3, master_name, 0, comment)
    
    import tracker_factory
    tracker = tracker_factory.get_tracker()
    if tracker and task_id:
        tracker.publish_version(task_id, master_file, 0, comment)
        
    return 1


def remove_item(tab, level1, level2, level3):
    """Moves the files and folders under the selected item to the 'deleted' folder."""
    depth = sum(1 for lvl in [level1, level2, level3] if lvl)
    curr_level1 = prefs.get_pref("ops_currOpenLevel1", "")
    curr_level2 = prefs.get_pref("ops_currOpenLevel2", "")
    curr_level3 = prefs.get_pref("ops_currOpenLevel3", "")
    curr_tab = prefs.get_pref("ops_currOpenTab", 0)
    
    original_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    delete_path = prefs.get_pref("ops_deletePath", "")
    name = os.path.basename(original_path.rstrip('/'))
    
    confirm = cmds.confirmDialog(
        title="Remove Files",
        message="Are you sure you want to remove this Item?\n(all files and folders will be moved to the 'deleted' folder)",
        button=["Yes", "No"], defaultButton="Yes", cancelButton="No"
    )
    if confirm == "Yes":
        os.makedirs(delete_path, exist_ok=True)
        is_current = 0
        if curr_tab == tab and curr_level1 == level1:
            if depth == opsInfo.LEVEL_1: is_current = 1
            elif curr_level2 == level2:
                if depth == opsInfo.LEVEL_2: is_current = 1
                elif curr_level3 == level3:
                    if depth == opsInfo.LEVEL_3: is_current = 1
                    
        if is_current:
            confirm_close = cmds.confirmDialog(
                title="Remove Files", message="You are removing an item that is currently open. Continue?",
                button=["Yes", "No"], defaultButton="Yes", cancelButton="No"
            )
            if confirm_close == "Yes": close_file()
            else: return 0
                
        new_path = os.path.join(delete_path, f"{name}_deleted_").replace("\\", "/")
        j = 0
        while os.path.exists(f"{new_path}{j}"): j += 1
        new_path = f"{new_path}{j}"
        
        try:
            os.rename(original_path, new_path)
            return remove_archive(tab, level1, level2, level3)
        except Exception as e:
            logger.error(f"Remove failed. Folder {original_path} could not be moved to the 'deleted' folder. {e}")
            return 0
    return 0


def remove_archive(tab, level1, level2, level3):
    """Moves the archived files and folders under the selected item to the 'deleted' folder."""
    archive_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder", archive=1)
    delete_path = prefs.get_pref("ops_deletePath", "")
    name = os.path.basename(archive_path.rstrip('/'))
    
    os.makedirs(delete_path, exist_ok=True)
    if os.path.isdir(archive_path):
        new_path = os.path.join(delete_path, f"{name}_archiveDeleted_").replace("\\", "/")
        j = 0
        while os.path.exists(f"{new_path}{j}"): j += 1
        new_path = f"{new_path}{j}"
        try:
            os.rename(archive_path, new_path)
            return 1
        except Exception as e:
            logger.error(f"Remove archive failed. Folder {archive_path} could not be moved to the 'deleted' folder. {e}")
            return 0
    return 1


def archive_item(tab, level1, level2, level3, keep_wips, keep_versions):
    """Archives old versions of an item."""
    w_name = prefs.get_pref("ops_wip", "wip")
    path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    archive_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder", archive=1)
    w_attempts = w_successes = v_attempts = v_successes = 0
    
    if keep_wips:
        wip_files = opsInfo.get_wips(tab, level1, level2, level3)
        for i in range(keep_wips, len(wip_files)):
            file_path = wip_files[i]
            w_attempts += 1
            new_name = file_path.replace(path, archive_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                w_successes += 1
            except: pass
            
    if keep_versions:
        version_files = opsInfo.get_versions(tab, level1, level2, level3)
        for i in range(keep_versions, len(version_files)):
            file_path = version_files[i]
            v_attempts += 1
            new_name = file_path.replace(path, archive_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                v_successes += 1
            except: pass
            
    msg = f"{w_successes} / {w_attempts} {w_name} files successfully moved to the archive.\n"
    msg += f"{v_successes} / {v_attempts} version files successfully moved to the archive.\n"
    logger.info(msg.strip())
    return 1


def retrieve_archive(tab, level1, level2, level3, do_wips, do_versions):
    """Restores all archived files of an item."""
    w_attempts = w_successes = v_attempts = v_successes = 0
    w_name = prefs.get_pref("ops_wip", "wip")
    original_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    archive_path = opsInfo.get_file_name(tab, level1, level2, level3, "folder", archive=1)
    
    if do_wips:
        archived_wips = opsInfo.get_wips(tab, level1, level2, level3, archive=1)
        for file_path in archived_wips:
            w_attempts += 1
            new_name = file_path.replace(archive_path, original_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                w_successes += 1
            except: pass
            
    if do_versions:
        archived_versions = opsInfo.get_versions(tab, level1, level2, level3, archive=1)
        for file_path in archived_versions:
            v_attempts += 1
            new_name = file_path.replace(archive_path, original_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                v_successes += 1
            except: pass
            
    msg = f"{w_successes} / {w_attempts} {w_name} files successfully retrieved from the archive.\n"
    msg += f"{v_successes} / {v_attempts} version files successfully retrieved from the archive.\n"
    logger.info(msg.strip())
    return 1


def close_file():
    """Closes the currently open file."""
    w_name = prefs.get_pref("ops_wip", "wip")
    curr_level1 = prefs.get_pref("ops_currOpenLevel1", "")
    if cmds.file(query=True, modified=True) and curr_level1:
        confirm = cmds.confirmDialog(
            title="openPypeline Studio",
            message=f"Would you like to Save {w_name} before closing?",
            button=["Save", "Don't Save", "Cancel"],
            defaultButton="Don't Save"
        )
        if confirm == "Save": save_wip("saved before closing")
        elif confirm == "Cancel": return 1
    
    prefs.set_pref("ops_currOpenType", "")
    prefs.set_pref("ops_currOpenVersion", 0)
    prefs.set_pref("ops_currOpenCategory", "")
    prefs.set_pref("ops_currOpenLevel1", "")
    prefs.set_pref("ops_currOpenLevel2", "")
    prefs.set_pref("ops_currOpenLevel3", "")
    prefs.set_pref("ops_currOpenTab", 0)
    import opsEngine
    engine = opsEngine.OpsEngine()
    if engine.file_handler and hasattr(engine.file_handler, 'new_file'):
        engine.file_handler.new_file()
    return 1


def open_location(tab, level1, level2, level3):
    """Opens an item's folder in the OS's explorer."""
    path = opsInfo.get_file_name(tab, level1, level2, level3, "folder")
    if path and os.path.isdir(path):
        import sys
        if sys.platform == "darwin": os.system(f"open '{path}'")
        elif sys.platform == "win32": os.startfile(path.replace("/", "\\"))
        else: os.system(f"xdg-open '{path}'")
    else: logger.warning(f"Couldn't find folder '{path}'.")


def record_playblast(tab, level1, level2, level3):
    """Records a playblast for an item."""
    playblast_file = opsInfo.get_file_name(tab, level1, level2, level3, "playblastFile")
    cmds.playblast(filename=playblast_file, forceOverwrite=True, format="movie", viewer=False, showOrnaments=False)
    return playblast_file


def create_thumbnail(tab, level1, level2, level3):
    """Takes a snapshot of the current scene and makes it the thumbnail for an item."""
    file_name = opsInfo.get_file_name(tab, level1, level2, level3, "previewFile")
    curr_frame = cmds.currentTime(query=True)
    format_val = cmds.getAttr("defaultRenderGlobals.imageFormat")
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
    cmds.playblast(frame=curr_frame, format="image", completeFilename=file_name, showOrnaments=False, viewer=False, widthHeight=(164, 105), percent=100)
    cmds.setAttr("defaultRenderGlobals.imageFormat", format_val)
    return file_name


def set_custom_notes(tab, level1, level2, level3, notes):
    """Set the custom notes for an item."""
    notes_file = opsInfo.get_file_name(tab, level1, level2, level3, "notesFile")
    new_text = notes.replace("<", " ").replace(">", " ").replace("\r", "<br>").replace("\n", "<br>")
    
    if not os.path.isfile(notes_file):
        try:
            with open(notes_file, "w") as f:
                f.write("<!--This file is automatically generated by openPipeline. Edit at your own risk!-->\n")
                f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
                f.write("<?xml-stylesheet type=\"text/xsl\" href=\"xsl/plStylesheet.xsl\"?>\n")
                f.write("<openPipeline_objectInfo>\n\t\t<description>\n")
                f.write(f"\t\t\t{new_text}\n\t\t</description>\n</openPipeline_objectInfo>")
        except Exception as e: logger.warning(f"Could not create notes file: {e}")
    else:
        try:
            with open(notes_file, "r") as f: content = f.read()
            content = re.sub(r'<description>.*?</description>', f'<description>\n\t\t\t{new_text}\n\t\t</description>', content, flags=re.DOTALL)
            with open(notes_file, "w") as f: f.write(content)
        except Exception as e: logger.warning(f"Could not update notes file: {e}")
    return 1


def view_playblast(tab, level1, level2, level3):
    """Opens the playblast of an item."""
    playblast_file = opsInfo.get_file_name(tab, level1, level2, level3, "playblastFile")
    if playblast_file and os.path.isfile(playblast_file):
        import sys
        if sys.platform == "darwin": os.system(f"open '{playblast_file}'")
        elif sys.platform == "win32": os.startfile(playblast_file.replace("/", "\\"))
        else: os.system(f"xdg-open '{playblast_file}'")
    else: logger.warning(f"Couldn't find playblast file '{playblast_file}'.")


def add_event_note(tab, level1, level2, level3, event, version, comment):
    """Adds an event note to an item's history."""
    history_file = opsInfo.get_file_name(tab, level1, level2, level3, "historyFile")
    user_name = prefs.get_pref("ops_currentUser", "default")
    date_str = opsInfo.get_date()
    time_str = opsInfo.get_time()
    
    try:
        with open(history_file, "a") as f:
            f.write("\t<note>\n")
            f.write(f"\t\t<author>{user_name}</author>\n")
            f.write(f"\t\t<date>{date_str}</date>\n")
            f.write(f"\t\t<time>{time_str}</time>\n")
            f.write(f"\t\t<event>{event}</event>\n")
            if version: f.write(f"\t\t<version>{version}</version>\n")
            f.write(f"\t\t<comment>{comment}</comment>\n")
            f.write("\t</note>\n")
    except Exception as e: logger.warning(f"Could not write to history file: {e}")
    return 1