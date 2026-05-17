"""
File: openPipelineInfo.py
Description: Core data retrieval functions for openPipeline. 
             Provides information about projects, paths, versions, and items.
             Refactored from openPipelineInfo.mel to use modern Python libraries.
"""

import maya.cmds as cmds
import maya.mel as mel
import os
import glob
import datetime
import re


def get_project_list():
    """
    Returns the names of all existing projects.

    Returns:
        list: A list of project names (str).
    """
    try:
        # Calls the legacy MEL function until projects are refactored to Python
        projects_data = mel.eval('openPipelineGetProjectsData()') or []
        projects = []
        for p in projects_data:
            match = re.search(r'<name>(.*?)</name>', p)
            if match:
                projects.append(match.group(1).strip())
        return projects
    except Exception as e:
        cmds.warning(f"Failed to retrieve project list: {e}")
        return []


def get_custom_notes(tab, level1, level2, level3):
    """
    Get an item's custom notes from its info.xml file.

    Args:
        tab (int): 2 for Asset, 3 for Shot
        level1 (str): Asset Type or Sequence
        level2 (str): Asset Name or Shot Name
        level3 (str): Component Name

    Returns:
        str: The custom notes content.
    """
    notes_file = get_file_name(tab, level1, level2, level3, "notesFile")
    if not notes_file or not os.path.isfile(notes_file):
        try:
            # Trigger the default MEL initialization if it doesn't exist
            mel.eval(f'openPipelineSetCustomNotes {tab} "{level1}" "{level2}" "{level3}" " "')
        except Exception:
            pass
        return ""

    try:
        with open(notes_file, 'r') as f:
            content = f.read()
            match = re.search(r'<description>(.*?)</description>', content, re.DOTALL)
            if match:
                text = match.group(1)
                # Convert legacy XML <br> tags to standard newlines
                text = re.sub(r'<br\s*/?>', '\n', text)
                return text.strip()
        return ""
    except Exception as e:
        cmds.warning(f"Failed to read notes file {notes_file}: {e}")
        return ""


def get_date():
    """Returns the current date in MM/DD/YYYY format."""
    return datetime.datetime.now().strftime("%m/%d/%Y")


def get_time():
    """Returns the current time in HH:MM:SS format."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def has_workshop(tab, level1, level2, level3):
    """Returns whether an item has at least one workshop."""
    return bool(get_file_name(tab, level1, level2, level3, "workshop"))


def has_master(tab, level1, level2, level3):
    """Returns whether an item has at least one master."""
    master_file = get_file_name(tab, level1, level2, level3, "master")
    return bool(master_file and os.path.isfile(master_file))


def has_playblast(tab, level1, level2, level3):
    """Returns whether an item has a playblast file."""
    pb_file = get_file_name(tab, level1, level2, level3, "playblastFile")
    return bool(pb_file and os.path.isfile(pb_file))


def get_workshops(tab, level1, level2, level3, archive=0):
    """Returns a list of all workshop files for a given item."""
    workshops = []
    i = 0
    while True:
        ws = get_file_name(tab, level1, level2, level3, "workshop", offset=i, archive=archive)
        if ws:
            workshops.append(ws)
            i += 1
        else:
            break
    return workshops


def get_versions(tab, level1, level2, level3, archive=0):
    """Returns a list of all version files for a given item."""
    versions = []
    i = 0
    while True:
        v = get_file_name(tab, level1, level2, level3, "version", offset=i, archive=archive)
        if v:
            versions.append(v)
            i += 1
        else:
            break
    return versions


def get_num_workshops(tab, level1, level2, level3, archive=0):
    """Returns the number of workshops an item has."""
    return len(get_workshops(tab, level1, level2, level3, archive))


def get_num_versions(tab, level1, level2, level3, archive=0):
    """Returns the number of versions an item has."""
    return len(get_versions(tab, level1, level2, level3, archive))


def get_version_from_file(filename):
    """
    Extracts the 4-digit version padding from an openPipeline filename.
    e.g. 'model_v0034.mb' -> 34
    """
    match = re.search(r'(\d{4})\.m[ab]$', filename)
    if match:
        return int(match.group(1))
    return 0


def get_latest_workshop_version(tab, level1, level2, level3):
    """Returns the integer version of the latest workshop for a given item."""
    ws = get_file_name(tab, level1, level2, level3, "workshop")
    if ws:
        return get_version_from_file(ws)
    return 0


def get_file_name(tab, level1, level2, level3, mode, offset=0, archive=0):
    """
    Returns the full path of a folder or filename pertinent to the given item.
    This dictates openPipeline's file naming conventions.

    Args:
        tab (int): The UI tab index (2 for Asset, 3 for Shot).
        level1 (str): First hierarchy level (e.g., Asset Type or Sequence).
        level2 (str): Second hierarchy level (e.g., Asset Name or Shot Name).
        level3 (str): Third hierarchy level (e.g., Component).
        mode (str): What to retrieve (e.g., "folder", "workshopFolder", "master", etc.).
        offset (int): Offset from the latest file if mode is 'workshop' or 'version' (0 is latest).
        archive (int): 1 to search in the archive path, 0 for normal project path.

    Returns:
        str: The full normalized path to the requested file or folder.
    """
    level1 = level1 or ""
    level2 = level2 or ""
    level3 = level3 or ""
    
    depth = sum(1 for lvl in [level1, level2, level3] if lvl)

    if mode == "parentFolder":
        if depth == 3:
            return get_file_name(tab, level1, level2, "", "folder", 0, 0)
        elif depth == 2:
            return get_file_name(tab, level1, "", "", "folder", 0, 0)
        elif depth == 1:
            return cmds.optionVar(query="op_currProjectPath") or ""
        return ""

    # Determine base path from OptionVars
    if tab == 2:
        base_path = cmds.optionVar(query="op_libPath") or ""
    elif tab == 3:
        base_path = cmds.optionVar(query="op_shotPath") or ""
    else:
        return ""

    # Handle Archive routing
    if archive:
        proj_path = cmds.optionVar(query="op_currProjectPath") or ""
        arch_path = cmds.optionVar(query="op_archivePath") or ""
        if proj_path and arch_path:
            base_path = base_path.replace(proj_path, arch_path)

    # Construct the directory tree hierarchically
    path_parts = [base_path]
    if level1:
        path_parts.append(level1)
        if level2:
            path_parts.append(level2)
            if level3:
                path_parts.extend(["components", level3])

    # Normalize to forward slashes for Maya
    current_dir = os.path.join(*path_parts).replace("\\", "/") + "/"
    
    if not level1: 
        return current_dir if mode == "folder" else ""

    w_name = cmds.optionVar(query="op_workshopName") or "workshop"
    w_ext = cmds.optionVar(query="op_workshopFormat") or "ma"
    m_name = cmds.optionVar(query="op_masterName") or "master"
    m_ext = cmds.optionVar(query="op_masterFormat") or "ma"

    item_name = level3 or level2 or level1
    parent_name = level2 if level3 else level1 if level2 else ""

    # --- Handle Folder Modes ---
    if mode == "folder":
        return current_dir
    elif mode == "workshopFolder":
        return os.path.join(current_dir, w_name).replace("\\", "/") + "/"
    elif mode == "versionFolder":
        return os.path.join(current_dir, "version").replace("\\", "/") + "/"
    elif mode == "componentFolder":
        return os.path.join(current_dir, "components").replace("\\", "/") + "/"
    elif mode == "noteFolder":
        return os.path.join(current_dir, "notes").replace("\\", "/") + "/"
    elif mode == "childFolder":
        if depth == 2:
            return os.path.join(current_dir, "components").replace("\\", "/") + "/"
        elif depth == 3:
            return ""
        return current_dir

    # --- Handle File Modes ---
    elif mode == "playblastFile":
        ext = "mov" if cmds.about(os=True) == "mac" else ("avi" if cmds.about(os=True) in ["nt", "win64"] else "mv")
        return os.path.join(current_dir, f"playblast.{ext}").replace("\\", "/")
    elif mode == "previewFile":
        return os.path.join(current_dir, "preview.png").replace("\\", "/")
    elif mode == "notesFile":
        return os.path.join(current_dir, "notes", "info.xml").replace("\\", "/")
    
    # --- Handle Workshop/Version Discovery Modes ---
    elif mode == "workshop":
        search_path = os.path.join(current_dir, w_name, f"*{w_name}*.{w_ext}")
        files = sorted(glob.glob(search_path))
        if files and len(files) > offset:
            return files[-(1 + offset)].replace("\\", "/")
        return ""
        
    elif mode == "nextWorkshop":
        search_path = os.path.join(current_dir, w_name, f"*{w_name}*.{w_ext}")
        files = sorted(glob.glob(search_path))
        latest_version = get_version_from_file(files[-1]) if files else 0
        suffix = str(latest_version + 1).zfill(4)
        prefix = f"{parent_name}_{item_name}" if level3 else item_name
        filename = f"{prefix}_{w_name}_{suffix}.{w_ext}"
        return os.path.join(current_dir, w_name, filename).replace("\\", "/")

    elif mode == "version":
        search_path = os.path.join(current_dir, "version", f"*version_*.{m_ext}")
        files = sorted(glob.glob(search_path))
        if files and len(files) > offset:
            return files[-(1 + offset)].replace("\\", "/")
        return ""

    elif mode == "nextVersion":
        search_path = os.path.join(current_dir, "version", f"*{item_name}*version_*.{m_ext}")
        files = sorted(glob.glob(search_path))
        latest_version = get_version_from_file(files[-1]) if files else 0
        suffix = str(latest_version + 1).zfill(4)
        prefix = f"{parent_name}_{item_name}" if level3 else item_name
        filename = f"{prefix}_version_{suffix}.{m_ext}"
        return os.path.join(current_dir, "version", filename).replace("\\", "/")

    elif mode == "master":
        if level3:
            filename = f"{parent_name}_{item_name}.{m_ext}"
        elif tab == 2:
            filename = f"{item_name}_asset.{m_ext}"
        elif tab == 3:
            filename = f"{item_name}_shot.{m_ext}"
        else:
            filename = f"{item_name}.{m_ext}"
        return os.path.join(current_dir, filename).replace("\\", "/")

    elif mode == "historyFile":
        if level3:
            filename = f"{parent_name}_{item_name}_ComponentNote.xml"
        elif tab == 2:
            filename = f"{item_name}_AssetNote.xml"
        elif tab == 3:
            filename = f"{item_name}_SceneNote.xml"
        else:
            filename = "Note.xml"
        return os.path.join(current_dir, "notes", filename).replace("\\", "/")

    else:
        cmds.warning(f"openPipelineInfo: unrecognized file mode '{mode}'")
        return ""


def get_children(tab, level1, level2, level3):
    """Returns the sub-folder names (children) of the given item."""
    child_path = get_file_name(tab, level1, level2, level3, "childFolder")
    if not child_path or not os.path.isdir(child_path):
        return []
        
    valid_children = []
    for child in os.listdir(child_path):
        if not child.startswith(".") and os.path.isdir(os.path.join(child_path, child)):
            valid_children.append(child)
    return valid_children


def get_category(tab, level1, level2, level3):
    """Returns the category of a given item (shot, asset, component, etc.)"""
    if tab == 2:
        if level3: return "component"
        if level2: return "asset"
        if level1: return "assetType"
    elif tab == 3:
        if level3: return "shotComponent"
        if level2: return "shot"
        if level1: return "sequence"
    return ""


def get_currently_open_path():
    """Returns the path of the currently open item based on OptionVars."""
    level1 = cmds.optionVar(query="op_currOpenLevel1") or ""
    level2 = cmds.optionVar(query="op_currOpenLevel2") or ""
    level3 = cmds.optionVar(query="op_currOpenLevel3") or ""
    tab = cmds.optionVar(query="op_currOpenTab") or 0
    return get_file_name(tab, level1, level2, level3, "folder")


def get_thumbnail(tab, level1, level2, level3):
    """Gets the filename of an item's thumbnail preview image."""
    return get_file_name(tab, level1, level2, level3, "previewFile")


def get_event_notes(tab, level1, level2, level3):
    """Returns a string containing the item's event history."""
    history_file = get_file_name(tab, level1, level2, level3, "historyFile")
    if history_file and os.path.isfile(history_file):
        try:
            with open(history_file, 'r') as f:
                return f.read()
        except Exception as e:
            cmds.warning(f"Could not read history file {history_file}: {e}")
    return ""


def get_currently_selected_item(tab, depth):
    """
    Gets the currently selected item under the given tab directly from the UI.
    Note: This couples the script to the active UI state. 
    """
    levels = ["", "", ""]
    ui_lists = []
    
    if tab == 2:
        ui_lists = [("op_assetTypes", "op_assetTypeScrollList"), 
                    ("op_assets", "op_assetScrollList"), 
                    ("op_components", "op_componentScrollList")]
    elif tab == 3:
        ui_lists = [("op_sequences", "op_sequenceScrollList"), 
                    ("op_shots", "op_shotScrollList"), 
                    ("op_shotComponents", "op_shotComponentScrollList")]

    for i in range(min(depth, len(ui_lists))):
        var_key, ui_list_name = ui_lists[i]
        if cmds.optionVar(exists=var_key) and cmds.textScrollList(ui_list_name, query=True, exists=True):
            items = cmds.optionVar(query=var_key) or []
            selected_indices = cmds.textScrollList(ui_list_name, query=True, sii=True) or []
            if selected_indices and len(items) >= selected_indices[0]:
                levels[i] = items[selected_indices[0] - 1]

    return levels