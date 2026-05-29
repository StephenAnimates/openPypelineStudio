"""
File: opsInfo.py
Description: Info Retrieval functions for openPypeline Studio.
             Handles fetching the current state of the pipeline, reading 
             paths, versions, UI states, etc.
             Refactored from openPipelineInfo.mel to Python 3. 
                
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import sys
import glob
import datetime
import re
import logging
from openpypeline.core.util import prefs

logger = logging.getLogger("openPypeline.info")

# --- UI Index Constants ---
TAB_ASSET = 2
TAB_SHOT = 3
LEVEL_1 = 1  # Asset Type / Sequence
LEVEL_2 = 2  # Asset / Shot
LEVEL_3 = 3  # Component

def get_project_list():
    """Returns the names of all existing projects."""
    try:
        from . import ops_project as opsProject
        from . import ops_utils as opsUtils
        proj_data = opsProject.get_projects_data() or []
        return [opsUtils.get_xml_data(proj, "name") for proj in proj_data]
    except Exception:
        return []


def get_custom_notes(tab, level1, level2, level3):
    """Get an item's custom notes."""
    notes_file = get_file_name(tab, level1, level2, level3, "notesFile")
    if not os.path.isfile(notes_file):
        try:
            from . import ops_actions as opsActions
            opsActions.set_custom_notes(tab, level1, level2, level3, " ")
        except Exception:
            pass
        return ""
    else:
        try:
            with open(notes_file, 'r') as f:
                content = f.read()
            match = re.search(r'<description>(.*?)</description>', content, re.DOTALL)
            if match:
                text = match.group(1).strip()
                return text.replace("<br>", "\n")
        except Exception:
            pass
    return ""


def get_date():
    """Returns the current date using the user's preferred format."""
    date_fmt = prefs.get_pref("ops_dateFormat", "%m/%d/%Y")
    return datetime.datetime.now().strftime(date_fmt)


def get_time():
    """Returns the current time using the user's preferred format."""
    time_fmt = prefs.get_pref("ops_timeFormat", "%H:%M:%S")
    return datetime.datetime.now().strftime(time_fmt)


def has_wip(tab, level1, level2, level3):
    """Returns whether an item has at least one WIP."""
    return bool(get_file_name(tab, level1, level2, level3, "workshop"))


def has_master(tab, level1, level2, level3):
    """Returns whether an item has at least one master."""
    master = get_file_name(tab, level1, level2, level3, "master")
    return bool(master and os.path.isfile(master))


def has_playblast(tab, level1, level2, level3):
    """Returns whether an item has a playblast."""
    pb_file = get_file_name(tab, level1, level2, level3, "playblastFile")
    return bool(pb_file and os.path.isfile(pb_file))


def get_wips(tab, level1, level2, level3, archive=0):
    """Returns the WIP files for a given item, from newest to oldest."""
    folder = get_file_name(tab, level1, level2, level3, "workshopFolder", 0, archive)
    w_name = prefs.get_pref("ops_wip", "workshop")
    w_ext = prefs.get_pref("ops_wipFormat", "ma")
    
    if os.path.isdir(folder):
        files = sorted(glob.glob(os.path.join(folder, f"*{w_name}_*.{w_ext}").replace("\\", "/")), reverse=True)
        return [f.replace("\\", "/") for f in files]
    return []


def get_versions(tab, level1, level2, level3, archive=0):
    """Returns all of the version files for a given item, from newest to oldest."""
    folder = get_file_name(tab, level1, level2, level3, "versionFolder", 0, archive)
    m_ext = prefs.get_pref("ops_masterFormat", "ma")
    
    if os.path.isdir(folder):
        files = sorted(glob.glob(os.path.join(folder, f"*version_*.{m_ext}").replace("\\", "/")), reverse=True)
        return [f.replace("\\", "/") for f in files]
    return []


def get_num_wips(tab, level1, level2, level3, archive=0):
    """Returns the number of WIPs an item has."""
    return len(get_wips(tab, level1, level2, level3, archive))


def get_num_versions(tab, level1, level2, level3, archive=0):
    """Returns the number of versions an item has."""
    return len(get_versions(tab, level1, level2, level3, archive))


def get_version_from_file(filepath):
    """Extracts the integer version number suffix from a given filename."""
    match = re.search(r'_(\d+)\.[a-zA-Z0-9]+$', filepath)
    if match:
        return int(match.group(1))
    return 0


def get_latest_wip_version(tab, level1, level2, level3):
    """Returns the version of the latest WIP for a given item."""
    latest_wip = get_file_name(tab, level1, level2, level3, "workshop")
    if latest_wip:
        return get_version_from_file(latest_wip)
    return 0


def get_file_name(tab, level1, level2, level3, mode, offset=0, archive=0):
    """
    Returns the full path of a folder or filename pertinent to the given item, 
    dictating openPypeline's file naming conventions.
    """
    depth = sum(1 for lvl in [level1, level2, level3] if lvl)
    file_name = ""
    w_name = prefs.get_pref("ops_wip", "workshop")
    w_ext = prefs.get_pref("ops_wipFormat", "ma")
    m_name = prefs.get_pref("ops_masterName", "master")
    m_ext = prefs.get_pref("ops_masterFormat", "ma")

    if mode == "parentFolder":
        if depth == LEVEL_3: return get_file_name(tab, level1, level2, "", "folder", 0, 0)
        elif depth == LEVEL_2: return get_file_name(tab, level1, "", "", "folder", 0, 0)
        elif depth == LEVEL_1:
            if tab == TAB_ASSET: return prefs.get_pref("ops_libPath", "")
            elif tab == TAB_SHOT: return prefs.get_pref("ops_shotPath", "")
            else: return prefs.get_pref("ops_currProjectPath", "")
        else: return ""

    if tab == TAB_ASSET:
        file_name = prefs.get_pref("ops_libPath", "")
    elif tab == TAB_SHOT:
        file_name = prefs.get_pref("ops_shotPath", "")
    else:
        return ""

    if archive:
        proj_path = prefs.get_pref("ops_currProjectPath", "")
        arch_path = prefs.get_pref("ops_archivePath", "")
        if proj_path and arch_path:
            file_name = file_name.replace(proj_path, arch_path)

    if level1:
        file_name = os.path.join(file_name, level1, "").replace("\\", "/")
        if level2:
            file_name = os.path.join(file_name, level2, "").replace("\\", "/")
            if level3:
                file_name = os.path.join(file_name, "components", level3, "").replace("\\", "/")

            if mode == "workshopFolder":
                file_name = os.path.join(file_name, w_name, "").replace("\\", "/")
            elif mode == "versionFolder":
                file_name = os.path.join(file_name, "version", "").replace("\\", "/")
            elif mode == "componentFolder":
                file_name = os.path.join(file_name, "components", "").replace("\\", "/")
            elif mode == "noteFolder":
                file_name = os.path.join(file_name, "notes", "").replace("\\", "/")
            elif mode == "playblastFile":
                ext = "mov" if sys.platform == "darwin" else "avi"
                file_name = os.path.join(file_name, f"playblast.{ext}").replace("\\", "/")
            elif mode == "previewFile":
                file_name = os.path.join(file_name, "preview.jpg").replace("\\", "/")
            elif mode == "notesFile":
                file_name = os.path.join(file_name, "notes", "info.xml").replace("\\", "/")
            elif mode == "workshop":
                wip_dir = os.path.join(file_name, w_name)
                if os.path.isdir(wip_dir):
                    files = sorted(glob.glob(os.path.join(wip_dir, f"*{w_name}_*.{w_ext}").replace("\\", "/")))
                    if files and len(files) > offset:
                        file_name = files[-(1 + offset)].replace("\\", "/")
                    else:
                        file_name = ""
                else: file_name = ""
            elif mode == "nextWorkshop":
                item_name = level3 if level3 else level2
                parent_name = level2 if level3 else level1
                wip_dir = os.path.join(file_name, w_name).replace("\\", "/")
                files = sorted(glob.glob(os.path.join(wip_dir, f"*{w_name}_*.{w_ext}").replace("\\", "/"))) if os.path.isdir(wip_dir) else []
                latest_version = get_version_from_file(files[-1]) if files else 0
                suffix = str(latest_version + 1).zfill(4)
                prefix = f"{parent_name}_{item_name}" if level3 else item_name
                file_name = os.path.join(wip_dir, f"{prefix}_{w_name}_{suffix}.{w_ext}").replace("\\", "/")
            elif mode == "version":
                v_dir = os.path.join(file_name, "version")
                if os.path.isdir(v_dir):
                    files = sorted(glob.glob(os.path.join(v_dir, f"*version_*.{m_ext}").replace("\\", "/")))
                    if files and len(files) > offset:
                        file_name = files[-(1 + offset)].replace("\\", "/")
                    else:
                        file_name = ""
                else: file_name = ""
            elif mode == "nextVersion":
                item_name = level3 if level3 else level2
                parent_name = level2 if level3 else level1
                v_dir = os.path.join(file_name, "version").replace("\\", "/")
                files = sorted(glob.glob(os.path.join(v_dir, f"*version_*.{m_ext}").replace("\\", "/"))) if os.path.isdir(v_dir) else []
                latest_version = get_version_from_file(files[-1]) if files else 0
                suffix = str(latest_version + 1).zfill(4)
                prefix = f"{parent_name}_{item_name}" if level3 else item_name
                file_name = os.path.join(v_dir, f"{prefix}_version_{suffix}.{m_ext}").replace("\\", "/")
            elif mode == "master":
                item_name = level3 if level3 else level2
                parent_name = level2 if level3 else level1
                if level3:
                    file_name = os.path.join(file_name, f"{parent_name}_{item_name}.{m_ext}").replace("\\", "/")
                elif tab == TAB_ASSET:
                    file_name = os.path.join(file_name, f"{item_name}_asset.{m_ext}").replace("\\", "/")
                elif tab == TAB_SHOT:
                    file_name = os.path.join(file_name, f"{item_name}_shot.{m_ext}").replace("\\", "/")
            elif mode == "historyFile":
                item_name = level3 if level3 else level2
                parent_name = level2 if level3 else level1
                if level3:
                    file_name = os.path.join(file_name, "notes", f"{parent_name}_{item_name}_ComponentNote.xml").replace("\\", "/")
                elif tab == TAB_ASSET:
                    file_name = os.path.join(file_name, "notes", f"{item_name}_AssetNote.xml").replace("\\", "/")
                elif tab == TAB_SHOT:
                    file_name = os.path.join(file_name, "notes", f"{item_name}_SceneNote.xml").replace("\\", "/")
            elif mode == "childFolder":
                if depth == LEVEL_2:
                    file_name = os.path.join(file_name, "components", "").replace("\\", "/")
                else:
                    file_name = ""
            elif mode != "folder":
                file_name = ""
                logger.warning(f"unrecognized file mode: {mode}")

    return file_name


def get_children(tab, level1, level2, level3):
    """Returns the children of the given item."""
    child_path = get_file_name(tab, level1, level2, level3, "childFolder")
    if not child_path or not os.path.isdir(child_path):
        return []
    
    return [child for child in os.listdir(child_path) if not child.startswith('.') and os.path.isdir(os.path.join(child_path, child))]


def get_category(tab, level1, level2, level3):
    """Returns the category of a given item (shot, asset, component, etc.)"""
    if tab == TAB_ASSET:
        if level3: return "component"
        elif level2: return "asset"
        elif level1: return "assetType"
    elif tab == TAB_SHOT:
        if level3: return "shotComponent"
        elif level2: return "shot"
        elif level1: return "sequence"
    return ""


def get_currently_open_path():
    """Returns the path of the currently open item."""
    level1 = prefs.get_pref("ops_currOpenLevel1", "")
    level2 = prefs.get_pref("ops_currOpenLevel2", "")
    level3 = prefs.get_pref("ops_currOpenLevel3", "")
    tab = prefs.get_pref("ops_currOpenTab", 0)
    
    if tab:
        return get_file_name(tab, level1, level2, level3, "folder")
    return ""


def get_thumbnail(tab, level1, level2, level3):
    """Get the filename of an item's thumbnail image."""
    return get_file_name(tab, level1, level2, level3, "previewFile")


def get_event_notes(tab, level1, level2, level3):
    """Get an item's event history."""
    history_file = get_file_name(tab, level1, level2, level3, "historyFile")
    if os.path.isfile(history_file):
        try:
            from . import ops_notes as opsNotes
            notes_array = opsNotes.read_xml(history_file)
            return "".join(notes_array)
        except Exception:
            pass
    return ""


def get_currently_selected_item(tab, depth):
    """Get the currently selected item under the given tab in the UI."""
    level1 = level2 = level3 = ""
    from ..ui import ui_objects as UIObjects
    ui_obj = UIObjects.UIObjects()
    ui = ui_obj.opsMainUI if hasattr(ui_obj, 'opsMainUI') else None
    
    if not ui:
        return [level1, level2, level3]
    
    try:
        # Test if the underlying C++ object has been deleted (e.g., during UI teardown)
        ui.objectName()
    except RuntimeError:
        return [level1, level2, level3]

    if tab == TAB_ASSET:
        if depth >= LEVEL_1 and hasattr(ui, "ops_assetType_txtScrollList"):
            types = prefs.get_pref("ops_assetTypes", [])
            if isinstance(types, str): types = [types]
            idx = ui.ops_assetType_txtScrollList.currentRow()
            if 0 <= idx < len(types): level1 = types[idx]
            
        if depth >= LEVEL_2 and hasattr(ui, "ops_asset_scrollList"):
            assets = prefs.get_pref("ops_assets", [])
            if isinstance(assets, str): assets = [assets]
            idx = ui.ops_asset_scrollList.currentRow()
            if 0 <= idx < len(assets): level2 = assets[idx]
            
        if depth >= LEVEL_3 and hasattr(ui, "ops_componentScrollList"):
            components = prefs.get_pref("ops_components", [])
            if isinstance(components, str): components = [components]
            idx = ui.ops_componentScrollList.currentRow()
            if 0 <= idx < len(components): level3 = components[idx]
            
    elif tab == TAB_SHOT:
        if depth >= LEVEL_1 and hasattr(ui, "ops_sequenceScrollList"):
            sequences = prefs.get_pref("ops_sequences", [])
            if isinstance(sequences, str): sequences = [sequences]
            idx = ui.ops_sequenceScrollList.currentRow()
            if 0 <= idx < len(sequences): level1 = sequences[idx]
            
        if depth >= LEVEL_2 and hasattr(ui, "ops_shotScrollList"):
            shots = prefs.get_pref("ops_shots", [])
            if isinstance(shots, str): shots = [shots]
            idx = ui.ops_shotScrollList.currentRow()
            if 0 <= idx < len(shots): level2 = shots[idx]
            
        if depth >= LEVEL_3 and hasattr(ui, "ops_shotComponentScrollList"):
            components = prefs.get_pref("ops_shotComponents", [])
            if isinstance(components, str): components = [components]
            idx = ui.ops_shotComponentScrollList.currentRow()
            if 0 <= idx < len(components): level3 = components[idx]
            
    return [level1, level2, level3]