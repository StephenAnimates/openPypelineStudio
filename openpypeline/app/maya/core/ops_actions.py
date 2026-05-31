"""
File: opsActions.py
Description: Core actions and functional operations for openPypeline Studio.
             Handles creation, file operations, referencing, importing, and history.
             Refactored from openPipelineActions.mel to use modern Python libraries.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import re
import json
import logging
from functools import wraps
from openpypeline.core.models import ItemContext, ProjectConfig, Level
import dataclasses
from openpypeline.core.localization import localization
from openpypeline.core.util import prefs
from PySide6 import QtWidgets

logger = logging.getLogger("openPypeline.actions")

from . import ops_info as opsInfo
from . import ops_loader as opsLoader
from . import ops_utils as opsUtils
from . import ops_project as opsProject


def _ensure_context(func):
    """Decorator to support both ItemContext objects and legacy (tab, level1, level2, level3) arguments."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args and isinstance(args[0], ItemContext):
            return func(*args, **kwargs)
        
        args_list = list(args)
        if len(args_list) >= 4 and isinstance(args_list[0], int):
            context = ItemContext(tab=args_list[0], level1=args_list[1], level2=args_list[2], level3=args_list[3])
            return func(context, *args_list[4:], **kwargs)
        elif len(args_list) >= 5 and isinstance(args_list[1], int):
            context = ItemContext(tab=args_list[1], level1=args_list[2], level2=args_list[3], level3=args_list[4])
            return func(context, args_list[0], *args_list[5:], **kwargs)
        return func(*args, **kwargs)
    return wrapper


def activate_project(proj_name):
    """Selects a project to work in and updates all associated optionVars and workspaces."""
    project = opsProject.get_project(proj_name)
    if not project:
        logger.warning(localization.get_string("err_projSelectFail").format(proj_name, "Unknown"))
        return 0
        
    proj_path = project.get("path", "")
    
    if proj_path and not proj_path.endswith('/'):
        proj_path += '/'
        
    if os.path.isdir(proj_path):
        proj_lib = project.get("libraryfolder", "")
        proj_shots = project.get("scenesfolder", "")
        proj_scripts = project.get("scriptsfolder", "")
        proj_renders = project.get("rendersfolder", "")
        proj_particles = project.get("particlesfolder", "")
        proj_textures = project.get("texturesfolder", "")
        proj_archive = project.get("archivefolder", "")
        proj_deleted = project.get("deletedfolder", "")
        proj_m_format = project.get("masterformat", "")
        proj_w_format = project.get("wipformat", project.get("workshopformat", ""))
        proj_m_name = project.get("mastername", "")
        proj_w_name = project.get("wipname", project.get("workshopname", ""))
        proj_users = project.get("users", "")

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
            
        import openpypeline.ops_engine as ops_engine
        engine = ops_engine.OpsEngine()
        if engine.file_handler and hasattr(engine.file_handler, 'set_workspace'):
            rules = {
                'mel': proj_scripts,
                'scene': proj_shots,
                'textures': proj_textures,
                'particles': proj_particles,
                'renderScenes': proj_renders
            }
            engine.file_handler.set_workspace(proj_path, rules)
        return 1
    else:
        logger.warning(localization.get_string("err_projSelectFail").format(proj_name, proj_path))
        return 0


def create_or_edit_project(mode, old_name, config: ProjectConfig):
    """Creates a new project or edits the properties of an existing project using a ProjectConfig dataclass."""
    mode_names = ["created", "edited"]
    active_project_name = prefs.get_pref("ops_currProjectName", "")
    proj_data = opsProject.get_projects_data() or []
    error = ""
    
    # Input validations
    if len(config.name) > 22: error += localization.get_string("err_projNameLen")
    if len(config.mastername) > 18: error += localization.get_string("err_masterNameLen")
    if len(config.wipname) > 18: error += localization.get_string("err_wipNameLen")
    if len(config.libraryfolder) > 22: error += localization.get_string("err_libLocLen")
    if len(config.scenesfolder) > 22: error += localization.get_string("err_shotLocLen")
    if len(config.scriptsfolder) > 22: error += localization.get_string("err_scriptLocLen")
    if len(config.rendersfolder) > 22: error += localization.get_string("err_renderLocLen")
    if len(config.particlesfolder) > 22: error += localization.get_string("err_particleLocLen")
    if len(config.texturesfolder) > 22: error += localization.get_string("err_textureLocLen")
    if len(config.date) > 18: error += localization.get_string("err_dateLen")
    if len(config.deadline) > 18: error += localization.get_string("err_deadlineLen")
    if len(config.description) > 250: error += localization.get_string("err_descLen")

    test_path = config.path.rstrip(config.name).rstrip("/").rstrip("\\")
    if not os.path.exists(test_path):
        error += localization.get_string("err_projPathInvalid")
        
    valid_pattern = re.compile(r"^[a-zA-Z0-9_]*$")
    if not valid_pattern.match(config.name): error += localization.get_string("err_projNameInvalid")
    if not valid_pattern.match(config.mastername): error += localization.get_string("err_masterNameInvalid")
    if not valid_pattern.match(config.wipname): error += localization.get_string("err_wipNameInvalid")

    valid_folder_pattern = re.compile(r"^[a-zA-Z0-9_/]*$")
    if not valid_folder_pattern.match(config.libraryfolder): error += localization.get_string("err_libLocInvalid")
    if not valid_folder_pattern.match(config.scenesfolder): error += localization.get_string("err_shotLocInvalid")
    if not valid_folder_pattern.match(config.texturesfolder): error += localization.get_string("err_textureLocInvalid")
    if not valid_folder_pattern.match(config.scriptsfolder): error += localization.get_string("err_scriptLocInvalid")
    if not valid_folder_pattern.match(config.rendersfolder): error += localization.get_string("err_renderLocInvalid")
    if not valid_folder_pattern.match(config.particlesfolder): error += localization.get_string("err_particleLocInvalid")
    
    new_path = os.path.join(config.path, "").replace("\\", "/")
    test_folders = [config.particlesfolder, config.rendersfolder, config.scriptsfolder, config.texturesfolder, config.scenesfolder, config.libraryfolder, config.archivefolder, config.deletedfolder]
    if len(test_folders) != len(set(test_folders)):
        error += localization.get_string("err_subfolderUnique")
        
    os.makedirs(new_path, exist_ok=True)
    if os.path.exists(new_path):
        try: os.makedirs(config.archivefolder if os.path.isabs(config.archivefolder) else os.path.join(new_path, config.archivefolder), exist_ok=True)
        except Exception: error += localization.get_string("err_archivePathInvalid")
        
        try: os.makedirs(config.deletedfolder if os.path.isabs(config.deletedfolder) else os.path.join(new_path, config.deletedfolder), exist_ok=True)
        except Exception: error += localization.get_string("err_deletedPathInvalid")
        
        for loc in [config.libraryfolder, config.scenesfolder, config.texturesfolder, config.rendersfolder, config.scriptsfolder, config.particlesfolder]:
            try: os.makedirs(os.path.join(new_path, loc), exist_ok=True)
            except Exception: error += localization.get_string("err_locPathInvalid").format(loc)
    else:
        error += localization.get_string("err_projPathCreate")

    found = False
    for project in proj_data:
        curr_proj_name = project.get("name")
        if config.name == curr_proj_name and curr_proj_name != old_name:
            found = True
            break
            
    if found:
        error += localization.get_string("err_projExists")

    if not error:
        new_project = dataclasses.asdict(config)
                   
        index = -1
        if not mode:
            proj_data.append(new_project)
        else:
            for i, project in enumerate(proj_data):
                if project.get("name") == old_name:
                    index = i
                    break
            if index == -1:
                logger.error(localization.get_string("err_projNotFoundEdit").format(old_name))
                return 0
            proj_data[index] = new_project
            
        opsProject.rewrite_proj_file(proj_data)
        
        if active_project_name == old_name:
            prefs.set_pref("ops_currProjectName", config.name)
            activate_project(config.name)
            
        logger.info(localization.get_string("msg_projMode").format(mode_names[mode]))
        return 1
    else:
        logger.error(localization.get_string("err_projModeFail").format(mode_names[mode], error))
        return 0


def remove_project(proj_name):
    """Removes a project from the openPypeline list (files remain intact)."""
    curr_project_name = prefs.get_pref("ops_currProjectName", "")
    projects_data = opsProject.get_projects_data() or []
    new_projects_data = []
    removed = False
    
    for project in projects_data:
        if project.get("name") != proj_name:
            new_projects_data.append(project)
        else:
            removed = True
            
    if removed:
        if curr_project_name == proj_name:
            prefs.set_pref("ops_currProjectName", "")
            prefs.set_pref("ops_currProjectPath", "")
        opsProject.rewrite_proj_file(new_projects_data)
    else:
        logger.warning(localization.get_string("err_projNotFoundRemove").format(proj_name))
        
    return int(removed)


@_ensure_context
def create_new_item(context, mode):
    """Creates a new item within the currently active project."""
    if not prefs.get_pref("ops_currProjectName", ""):
        logger.warning(localization.get_string("err_noActiveProj"))
        return ""
        
    error = ""
    item_path = opsInfo.get_file_name(context, "folder")
    item_name = os.path.basename(item_path.rstrip('/'))
    parent_path = opsInfo.get_file_name(context, "parentFolder")
    version_folder = opsInfo.get_file_name(context, "versionFolder")
    component_folder = opsInfo.get_file_name(context, "componentFolder")
    note_folder = opsInfo.get_file_name(context, "noteFolder")
    wip_folder = opsInfo.get_file_name(context, "workshopFolder")
    destination_file = opsInfo.get_file_name(context, "nextWorkshop")
    category = opsInfo.get_category(context)
    w_name = prefs.get_pref("ops_wip", "wip")

    if context.depth and item_path:
        if not re.match(r"^[a-zA-Z0-9_]*$", item_name):
            error += localization.get_string("err_invalidItemName").format(category)
        elif os.path.isdir(item_path):
            error += localization.get_string("err_itemExists").format(category, item_name)
        elif not os.path.isdir(parent_path):
            if context.depth == Level.ASSET_OR_SHOT: create_new_item(ItemContext(context.tab, context.level1), 1)
            elif context.depth == Level.COMPONENT: create_new_item(ItemContext(context.tab, context.level1, context.level2), 1)
            else: error += localization.get_string("err_parentNotFound").format(parent_path, category)
        
        if error:
            logger.warning(error.strip())
            return ""
            
        os.makedirs(item_path, exist_ok=True)
        if context.depth == Level.ASSET_OR_SHOT: os.makedirs(component_folder, exist_ok=True)
        if context.depth >= Level.ASSET_OR_SHOT:
            os.makedirs(wip_folder, exist_ok=True)
            os.makedirs(version_folder, exist_ok=True)
            os.makedirs(note_folder, exist_ok=True)

            prefs.set_pref("ops_creationPath", f"{item_path}/")
            prefs.set_pref("ops_creationType", category)
            
            add_event_note(context, "created", 0, "")
            
            ext = prefs.get_pref("ops_wipFormat", "ma")
            file_type_map = {"ma": "mayaAscii", "mb": "mayaBinary", "usd": "USD Export", "usda": "USD Export", "abc": "Alembic"}
            file_type = file_type_map.get(ext, "mayaBinary")

            import openpypeline.ops_engine as ops_engine
            engine = ops_engine.OpsEngine()

            if mode == 2:
                if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
                    engine.file_handler.export_file(destination_file, file_type, selected=True)
                add_event_note(context, w_name, 1, localization.get_string("msg_exportSelFirst").format(w_name))
            elif mode == 3:
                if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
                    engine.file_handler.export_file(destination_file, file_type, selected=False)
                add_event_note(context, w_name, 1, localization.get_string("msg_exportAllFirst").format(w_name))
            
            set_custom_notes(context, " ")
        return item_path
    else:
        logger.warning(localization.get_string("err_paramIncorrect"))
        return ""


@_ensure_context
def open_item(context, item_type, version_offset):
    """Opens an item for editing."""
    folder = opsInfo.get_file_name(context, "folder")
    
    if context.depth >= Level.ASSET_OR_SHOT and os.path.isdir(folder) and item_type in ["workshop", "master"]:
        version = 0
        curr_level1 = prefs.get_pref("ops_currOpenLevel1", "")
        
        import openpypeline.ops_engine as ops_engine
        engine = ops_engine.OpsEngine()
        is_mod = engine.file_handler.is_modified() if engine.file_handler and hasattr(engine.file_handler, 'is_modified') else False

        if is_mod and curr_level1:
            w_name = prefs.get_pref("ops_wip", "wip")
            reply = QtWidgets.QMessageBox.question(
                None, localization.get_string("win_opsStudio"),
                localization.get_string("msg_saveBeforeEdit").format(w_name),
                QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel,
                QtWidgets.QMessageBox.StandardButton.Save
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Save:
                    save_wip(localization.get_string("msg_savedBeforeOpen"))
            elif reply == QtWidgets.QMessageBox.StandardButton.Cancel:
                return 0
                
        file_to_open = opsInfo.get_file_name(context, item_type, version_offset)
        latest_wip = opsInfo.get_file_name(context, item_type)
        category = opsInfo.get_category(context)
        
        if os.path.isfile(file_to_open):
            version = opsInfo.get_version_from_file(file_to_open)
            if engine.file_handler and hasattr(engine.file_handler, 'open'):
                engine.file_handler.open(file_to_open)
            else:
                logger.warning(localization.get_string("err_noDccOpen"))
        elif item_type == "workshop" and not os.path.isfile(latest_wip):
            msgBox = QtWidgets.QMessageBox(None)
            msgBox.setWindowTitle(localization.get_string("win_editAsset"))
            msgBox.setText(localization.get_string("msg_firstTimeEdit"))
            new_btn = msgBox.addButton(localization.get_string("btn_newScene"), QtWidgets.QMessageBox.ButtonRole.AcceptRole)
            curr_btn = msgBox.addButton(localization.get_string("btn_currentScene"), QtWidgets.QMessageBox.ButtonRole.RejectRole)
            cancel_btn = msgBox.addButton(localization.get_string("btn_cancel"), QtWidgets.QMessageBox.ButtonRole.RejectRole)
            msgBox.setDefaultButton(curr_btn)
            msgBox.exec()

            if msgBox.clickedButton() == new_btn:
                if engine.file_handler and hasattr(engine.file_handler, 'new_file'):
                    engine.file_handler.new_file()
            elif msgBox.clickedButton() == cancel_btn:
                return 0
        else:
            logger.warning(localization.get_string("err_fileNotFound"))
            return 0
            
        prefs.set_pref("ops_currOpenType", item_type)
        prefs.set_pref("ops_currOpenVersion", version)
        prefs.set_pref("ops_currOpenCategory", category)
        prefs.set_pref("ops_currOpenLevel1", context.level1)
        prefs.set_pref("ops_currOpenLevel2", context.level2)
        prefs.set_pref("ops_currOpenLevel3", context.level3)
        prefs.set_pref("ops_currOpenTab", context.tab)
    else:
        logger.warning(localization.get_string("err_invalidCmdItem"))
        return 0
    return 1


@_ensure_context
def import_item(context, item_type, flags=""):
    """Imports an item into the current scene."""
    file_path = opsInfo.get_file_name(context, item_type)
    if os.path.isfile(file_path):
        import openpypeline.ops_engine as ops_engine
        engine = ops_engine.OpsEngine()
        if engine.file_handler and hasattr(engine.file_handler, 'import_file'):
            return int(engine.file_handler.import_file(file_path))
        else:
            logger.warning(localization.get_string("err_noDccImport"))
            return 0
    else:
        logger.warning(localization.get_string("err_importFail").format(file_path))
        return 0


@_ensure_context
def reference_item(context, item_type, flags=""):
    """References an item into the current scene."""
    file_path = opsInfo.get_file_name(context, item_type)
    if os.path.isfile(file_path):
        import openpypeline.ops_engine as ops_engine
        engine = ops_engine.OpsEngine()
        if engine.file_handler and hasattr(engine.file_handler, 'reference_file'):
            return int(engine.file_handler.reference_file(file_path))
        else:
            logger.warning(localization.get_string("err_noDccRef"))
            return 0
    else:
        logger.warning(localization.get_string("err_refFail").format(file_path))
        return 0




def save_wip(note=""):
    """Saves a WIP for the currently open item."""
    ext = prefs.get_pref("ops_wipFormat", "ma")
    w_name = prefs.get_pref("ops_wip", "wip")
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    tab = prefs.get_pref("ops_currOpenTab", 0)
    context = ItemContext(tab, level1, level2, level3)
    
    destination_file = opsInfo.get_file_name(context, "nextWorkshop")
    
    file_type_map = {"ma": "mayaAscii", "mb": "mayaBinary", "usd": "USD Export", "usda": "USD Export", "abc": "Alembic"}
    file_type = file_type_map.get(ext, "mayaBinary")
    if ext not in file_type_map:
        logger.warning(localization.get_string("err_invalidFormat").format(ext))
        
    import openpypeline.ops_engine as ops_engine
    engine = ops_engine.OpsEngine()
    
    if file_type in ["USD Export", "Alembic"]:
        if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
            engine.file_handler.export_file(destination_file, file_type, selected=False)
        else:
            logger.warning(localization.get_string("err_noDccExport"))
    else:
        if engine.file_handler and hasattr(engine.file_handler, 'save_as'):
            engine.file_handler.save_as(destination_file, file_type)
        else:
            logger.warning(localization.get_string("err_noDccSave"))
    latest_version = opsInfo.get_version_from_file(destination_file)
    prefs.set_pref("ops_currOpenVersion", latest_version)
    add_event_note(context, w_name, latest_version, note)
    return 1


def save_master(comment, flatten, delete_disp_layers, after, custom_command="", task_id=0):
    """Saves a master for the currently open item."""
    ext = prefs.get_pref("ops_masterFormat", "ma")
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    tab = prefs.get_pref("ops_currOpenTab", 0)
    context = ItemContext(tab, level1, level2, level3)
    master_name = prefs.get_pref("ops_masterName", "master")
    
    master_file = opsInfo.get_file_name(context, "master")
    destination_file = opsInfo.get_file_name(context, "nextVersion")
    
    save_wip(comment)
    
    if os.path.exists(master_file):
        os.rename(master_file, destination_file)
        
    import openpypeline.ops_engine as ops_engine
    engine = ops_engine.OpsEngine()
    
    if flatten and engine.file_handler and hasattr(engine.file_handler, 'flatten_references'):
        w_name = prefs.get_pref("ops_wip", "wip")
        engine.file_handler.flatten_references(master_name, w_name)
        
    if delete_disp_layers and engine.file_handler and hasattr(engine.file_handler, 'delete_display_layers'):
        engine.file_handler.delete_display_layers()
                
    if custom_command:
        logger.info(localization.get_string("msg_beginCmd").format(custom_command))
        try: exec(custom_command)
        except Exception as e: logger.warning(localization.get_string("err_cmdFail").format(e))
        logger.info(localization.get_string("msg_endCmd").format(custom_command))
        
    file_type_map = {"ma": "mayaAscii", "mb": "mayaBinary", "usd": "USD Export", "usda": "USD Export", "abc": "Alembic"}
    file_type = file_type_map.get(ext, "mayaBinary")
    
    if file_type in ["USD Export", "Alembic"]:
        if engine.file_handler and hasattr(engine.file_handler, 'export_file'):
            engine.file_handler.export_file(master_file, file_type, selected=False)
    else:
        if engine.file_handler and hasattr(engine.file_handler, 'save_as'):
            engine.file_handler.save_as(master_file, file_type)
    
    if after == 1: open_item(context, "workshop", 0)
    elif after == 2: prefs.set_pref("ops_currOpenType", "master")
    elif after == 3:
        close_file()
        if engine.file_handler and hasattr(engine.file_handler, 'new_file'):
            engine.file_handler.new_file()
        
    add_event_note(context, master_name, 0, comment)
    
    from . import tracker_factory
    tracker = tracker_factory.get_tracker()
    if tracker and task_id:
        tracker.publish_version(task_id, master_file, 0, comment)
        
    return 1


@_ensure_context
def remove_item(context):
    """Moves the files and folders under the selected item to the 'deleted' folder."""
    curr_level1 = prefs.get_pref("ops_currOpenLevel1", "")
    curr_level2 = prefs.get_pref("ops_currOpenLevel2", "")
    curr_level3 = prefs.get_pref("ops_currOpenLevel3", "")
    curr_tab = prefs.get_pref("ops_currOpenTab", 0)
    
    original_path = opsInfo.get_file_name(context, "folder")
    delete_path = prefs.get_pref("ops_deletePath", "")
    name = os.path.basename(original_path.rstrip('/'))
    
    reply = QtWidgets.QMessageBox.question(
        None, localization.get_string("win_removeFiles"),
        localization.get_string("msg_confirmRemoveItem"),
        QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        QtWidgets.QMessageBox.StandardButton.Yes
    )
    if reply == QtWidgets.QMessageBox.StandardButton.Yes:
        os.makedirs(delete_path, exist_ok=True)
        is_current = 0
        if curr_tab == context.tab and curr_level1 == context.level1:
            if context.depth == Level.TYPE_OR_SEQUENCE: is_current = 1
            elif curr_level2 == context.level2:
                if context.depth == Level.ASSET_OR_SHOT: is_current = 1
                elif curr_level3 == context.level3:
                    if context.depth == Level.COMPONENT: is_current = 1
                    
        if is_current:
            confirm_close = QtWidgets.QMessageBox.question(
                None, localization.get_string("win_removeFiles"),
                localization.get_string("msg_confirmRemoveOpen"),
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.Yes
            )
            if confirm_close == QtWidgets.QMessageBox.StandardButton.Yes: close_file()
            else: return 0
                
        new_path = os.path.join(delete_path, f"{name}_deleted_").replace("\\", "/")
        j = 0
        while os.path.exists(f"{new_path}{j}"): j += 1
        new_path = f"{new_path}{j}"
        
        try:
            os.rename(original_path, new_path)
            return remove_archive(context)
        except Exception as e:
            logger.error(localization.get_string("err_removeFail").format(original_path, e))
            return 0
    return 0


@_ensure_context
def remove_archive(context):
    """Moves the archived files and folders under the selected item to the 'deleted' folder."""
    archive_path = opsInfo.get_file_name(context, "folder", archive=1)
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
            logger.error(localization.get_string("err_removeArchiveFail").format(archive_path, e))
            return 0
    return 1


@_ensure_context
def archive_item(context, keep_wips, keep_versions):
    """Archives old versions of an item."""
    w_name = prefs.get_pref("ops_wip", "wip")
    path = opsInfo.get_file_name(context, "folder")
    archive_path = opsInfo.get_file_name(context, "folder", archive=1)
    w_attempts = w_successes = v_attempts = v_successes = 0
    
    if keep_wips:
        wip_files = opsInfo.get_wips(context)
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
        version_files = opsInfo.get_versions(context)
        for i in range(keep_versions, len(version_files)):
            file_path = version_files[i]
            v_attempts += 1
            new_name = file_path.replace(path, archive_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                v_successes += 1
            except: pass
            
    msg = localization.get_string("msg_archiveWipSuccess").format(w_successes, w_attempts, w_name)
    msg += localization.get_string("msg_archiveVerSuccess").format(v_successes, v_attempts)
    logger.info(msg.strip())
    return 1


@_ensure_context
def retrieve_archive(context, do_wips, do_versions):
    """Restores all archived files of an item."""
    w_attempts = w_successes = v_attempts = v_successes = 0
    w_name = prefs.get_pref("ops_wip", "wip")
    original_path = opsInfo.get_file_name(context, "folder")
    archive_path = opsInfo.get_file_name(context, "folder", archive=1)
    
    if do_wips:
        archived_wips = opsInfo.get_wips(context, archive=1)
        for file_path in archived_wips:
            w_attempts += 1
            new_name = file_path.replace(archive_path, original_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                w_successes += 1
            except: pass
            
    if do_versions:
        archived_versions = opsInfo.get_versions(context, archive=1)
        for file_path in archived_versions:
            v_attempts += 1
            new_name = file_path.replace(archive_path, original_path)
            os.makedirs(os.path.dirname(new_name), exist_ok=True)
            try:
                os.rename(file_path, new_name)
                v_successes += 1
            except: pass
            
    msg = localization.get_string("msg_retrieveWipSuccess").format(w_successes, w_attempts, w_name)
    msg += localization.get_string("msg_retrieveVerSuccess").format(v_successes, v_attempts)
    logger.info(msg.strip())
    return 1


def close_file():
    """Closes the currently open file."""
    w_name = prefs.get_pref("ops_wip", "wip")
    curr_level1 = prefs.get_pref("ops_currOpenLevel1", "")

    import openpypeline.ops_engine as ops_engine
    engine = ops_engine.OpsEngine()
    is_mod = engine.file_handler.is_modified() if engine.file_handler and hasattr(engine.file_handler, 'is_modified') else False

    if is_mod and curr_level1:
        reply = QtWidgets.QMessageBox.question(
            None, localization.get_string("win_opsStudio"),
            localization.get_string("msg_saveBeforeClose").format(w_name),
            QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Discard
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Save: save_wip(localization.get_string("msg_savedBeforeClose"))
        elif reply == QtWidgets.QMessageBox.StandardButton.Cancel: return 1
    
    prefs.set_pref("ops_currOpenType", "")
    prefs.set_pref("ops_currOpenVersion", 0)
    prefs.set_pref("ops_currOpenCategory", "")
    prefs.set_pref("ops_currOpenLevel1", "")
    prefs.set_pref("ops_currOpenLevel2", "")
    prefs.set_pref("ops_currOpenLevel3", "")
    prefs.set_pref("ops_currOpenTab", 0)
    if engine.file_handler and hasattr(engine.file_handler, 'new_file'):
        engine.file_handler.new_file()
    return 1


@_ensure_context
def open_location(context):
    """Opens an item's folder in the OS's explorer."""
    path = opsInfo.get_file_name(context, "folder")
    if path and os.path.isdir(path):
        import sys
        if sys.platform == "darwin": os.system(f"open '{path}'")
        elif sys.platform == "win32": os.startfile(path.replace("/", "\\"))
        else: os.system(f"xdg-open '{path}'")
    else: logger.warning(localization.get_string("err_folderNotFound").format(path))


@_ensure_context
def record_playblast(context):
    """Records a playblast for an item."""
    playblast_file = opsInfo.get_file_name(context, "playblastFile")
    import openpypeline.ops_engine as ops_engine
    engine = ops_engine.OpsEngine()
    if engine.file_handler and hasattr(engine.file_handler, 'record_playblast'):
        engine.file_handler.record_playblast(playblast_file)
    return playblast_file


@_ensure_context
def create_thumbnail(context):
    """Takes a snapshot of the current scene and makes it the thumbnail for an item."""
    file_name = opsInfo.get_file_name(context, "previewFile")
    import openpypeline.ops_engine as ops_engine
    engine = ops_engine.OpsEngine()
    if engine.file_handler and hasattr(engine.file_handler, 'create_thumbnail'):
        engine.file_handler.create_thumbnail(file_name)
    return file_name


@_ensure_context
def set_custom_notes(context, notes):
    """Set the custom notes for an item."""
    notes_file = opsInfo.get_file_name(context, "notesFile")
    
    # Clean up any leftover XML-specific breaks or tags if they exist
    new_text = notes.replace("<", " ").replace(">", " ").replace("<br>", "\n")
    
    try:
        os.makedirs(os.path.dirname(notes_file), exist_ok=True)
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump({"description": new_text}, f, indent=4)
    except Exception as e:
        logger.warning(localization.get_string("err_updateNotesFail").format(e))
        
    return 1


@_ensure_context
def view_playblast(context):
    """Opens the playblast of an item."""
    playblast_file = opsInfo.get_file_name(context, "playblastFile")
    if playblast_file and os.path.isfile(playblast_file):
        import sys
        if sys.platform == "darwin": os.system(f"open '{playblast_file}'")
        elif sys.platform == "win32": os.startfile(playblast_file.replace("/", "\\"))
        else: os.system(f"xdg-open '{playblast_file}'")
    else: logger.warning(localization.get_string("err_playblastNotFound").format(playblast_file))


@_ensure_context
def add_event_note(context, event, version, comment):
    """Adds an event note to an item's history."""
    history_file = opsInfo.get_file_name(context, "historyFile")
    user_name = prefs.get_pref("ops_currentUser", "default")
    date_str = opsInfo.get_date()
    time_str = opsInfo.get_time()
    
    note = {
        "author": user_name,
        "date": date_str,
        "time": time_str,
        "event": event,
        "version": str(version) if version else "",
        "comment": comment
    }
    
    notes_list = []
    if os.path.isfile(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                notes_list = json.load(f)
        except Exception:
            pass
            
    notes_list.append(note)
    
    try:
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(notes_list, f, indent=4)
    except Exception as e:
        logger.warning(localization.get_string("err_historyWriteFail").format(e))
        
    return 1