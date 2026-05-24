"""
File: opsInfo.py
Description: Info Retrieval functions for openPypeline Studio.
             Handles fetching the current state of the pipeline, reading 
             paths, versions, UI states, etc.
             Refactored from openPipelineInfo.mel to Python 3.
"""

import maya.cmds as cmds
import os
import glob
import datetime
import re


def get_project_list():
    """Returns the names of all existing projects."""
    try:
        import opsProject
        import opsUtils
        proj_data = opsProject.get_projects_data() or []
        return [opsUtils.get_xml_data(proj, "name") for proj in proj_data]
    except Exception:
        return []


def get_custom_notes(tab, level1, level2, level3):
    """Get an item's custom notes."""
    notes_file = get_file_name(tab, level1, level2, level3, "notesFile")
    if not os.path.isfile(notes_file):
        try:
            import opsActions
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
    master = get_file_name(tab, level1, level2, level3, "master")
    return bool(master and os.path.isfile(master))


def has_playblast(tab, level1, level2, level3):
    """Returns whether an item has a playblast."""
    pb_file = get_file_name(tab, level1, level2, level3, "playblastFile")
    return bool(pb_file and os.path.isfile(pb_file))


def get_workshops(tab, level1, level2, level3, archive=0):
    """Returns the workshop files for a given item, from newest to oldest."""
    folder = get_file_name(tab, level1, level2, level3, "workshopFolder", 0, archive)
    w_name = cmds.optionVar(query="ops_workshopName") if cmds.optionVar(exists="ops_workshopName") else "workshop"
    w_ext = cmds.optionVar(query="ops_workshopFormat") if cmds.optionVar(exists="ops_workshopFormat") else "ma"
    
    if os.path.isdir(folder):
        files = sorted(glob.glob(os.path.join(folder, f"*{w_name}_*.{w_ext}").replace("\\", "/")), reverse=True)
        return [f.replace("\\", "/") for f in files]
    return []


def get_versions(tab, level1, level2, level3, archive=0):
    """Returns all of the version files for a given item, from newest to oldest."""
    folder = get_file_name(tab, level1, level2, level3, "versionFolder", 0, archive)
    m_ext = cmds.optionVar(query="ops_masterFormat") if cmds.optionVar(exists="ops_masterFormat") else "ma"
    
    if os.path.isdir(folder):
        files = sorted(glob.glob(os.path.join(folder, f"*version_*.{m_ext}").replace("\\", "/")), reverse=True)
        return [f.replace("\\", "/") for f in files]
    return []


def get_num_workshops(tab, level1, level2, level3, archive=0):
    """Returns the number of workshops an item has."""
    return len(get_workshops(tab, level1, level2, level3, archive))


def get_num_versions(tab, level1, level2, level3, archive=0):
    """Returns the number of versions an item has."""
    return len(get_versions(tab, level1, level2, level3, archive))


def get_version_from_file(filepath):
    """Extracts the integer version number suffix from a given filename."""
    match = re.search(r'_(\d+)\.[a-zA-Z0-9]+$', filepath)
    if match:
        return int(match.group(1))
    return 0


def get_latest_workshop_version(tab, level1, level2, level3):
    """Returns the version of the latest workshop for a given item."""
    latest_ws = get_file_name(tab, level1, level2, level3, "workshop")
    if latest_ws:
        return get_version_from_file(latest_ws)
    return 0


def get_file_name(tab, level1, level2, level3, mode, offset=0, archive=0):
    """
    Returns the full path of a folder or filename pertinent to the given item, 
    dictating openPypeline's file naming conventions.
    """
    depth = sum(1 for lvl in [level1, level2, level3] if lvl)
    file_name = ""
    w_name = cmds.optionVar(query="ops_workshopName") if cmds.optionVar(exists="ops_workshopName") else "workshop"
    w_ext = cmds.optionVar(query="ops_workshopFormat") if cmds.optionVar(exists="ops_workshopFormat") else "ma"
    m_name = cmds.optionVar(query="ops_masterName") if cmds.optionVar(exists="ops_masterName") else "master"
    m_ext = cmds.optionVar(query="ops_masterFormat") if cmds.optionVar(exists="ops_masterFormat") else "ma"

    if mode == "parentFolder":
        if depth == 3: return get_file_name(tab, level1, level2, "", "folder", 0, 0)
        elif depth == 2: return get_file_name(tab, level1, "", "", "folder", 0, 0)
        elif depth == 1: return cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
        else: return ""

    if tab == 2:
        file_name = cmds.optionVar(query="ops_libPath") if cmds.optionVar(exists="ops_libPath") else ""
    elif tab == 3:
        file_name = cmds.optionVar(query="ops_shotPath") if cmds.optionVar(exists="ops_shotPath") else ""
    else:
        return ""

    if archive:
        proj_path = cmds.optionVar(query="ops_currProjectPath") if cmds.optionVar(exists="ops_currProjectPath") else ""
        arch_path = cmds.optionVar(query="ops_archivePath") if cmds.optionVar(exists="ops_archivePath") else ""
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
                ext = "mov" if cmds.about(os=True) == "mac" else "avi"
                file_name = os.path.join(file_name, f"playblast.{ext}").replace("\\", "/")
            elif mode == "previewFile":
                file_name = os.path.join(file_name, "preview.jpg").replace("\\", "/")
            elif mode == "notesFile":
                file_name = os.path.join(file_name, "notes", "info.xml").replace("\\", "/")
            elif mode == "workshop":
                ws_dir = os.path.join(file_name, w_name)
                if os.path.isdir(ws_dir):
                    files = sorted(glob.glob(os.path.join(ws_dir, f"*{w_name}_*.{w_ext}").replace("\\", "/")))
                    if files and len(files) > offset:
                        file_name = files[-(1 + offset)].replace("\\", "/")
                    else:
                        file_name = ""
                else: file_name = ""
            elif mode == "nextWorkshop":
                item_name = level3 if level3 else level2
                parent_name = level2 if level3 else level1
                ws_dir = os.path.join(file_name, w_name).replace("\\", "/")
                files = sorted(glob.glob(os.path.join(ws_dir, f"*{w_name}_*.{w_ext}").replace("\\", "/"))) if os.path.isdir(ws_dir) else []
                latest_version = get_version_from_file(files[-1]) if files else 0
                suffix = str(latest_version + 1).zfill(4)
                prefix = f"{parent_name}_{item_name}" if level3 else item_name
                file_name = os.path.join(ws_dir, f"{prefix}_{w_name}_{suffix}.{w_ext}").replace("\\", "/")
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
                elif tab == 2:
                    file_name = os.path.join(file_name, f"{item_name}_asset.{m_ext}").replace("\\", "/")
                elif tab == 3:
                    file_name = os.path.join(file_name, f"{item_name}_shot.{m_ext}").replace("\\", "/")
            elif mode == "historyFile":
                item_name = level3 if level3 else level2
                parent_name = level2 if level3 else level1
                if level3:
                    file_name = os.path.join(file_name, "notes", f"{parent_name}_{item_name}_ComponentNote.xml").replace("\\", "/")
                elif tab == 2:
                    file_name = os.path.join(file_name, "notes", f"{item_name}_AssetNote.xml").replace("\\", "/")
                elif tab == 3:
                    file_name = os.path.join(file_name, "notes", f"{item_name}_SceneNote.xml").replace("\\", "/")
            elif mode == "childFolder":
                if depth == 2:
                    file_name = os.path.join(file_name, "components", "").replace("\\", "/")
                else:
                    file_name = ""
            elif mode != "folder":
                file_name = ""
                cmds.warning(f"openPypeline Studio (get_file_name) unrecognized file mode: {mode}")

    return file_name


def get_children(tab, level1, level2, level3):
    """Returns the children of the given item."""
    child_path = get_file_name(tab, level1, level2, level3, "childFolder")
    if not child_path or not os.path.isdir(child_path):
        return []
    
    return [child for child in os.listdir(child_path) if not child.startswith('.') and os.path.isdir(os.path.join(child_path, child))]


def get_category(tab, level1, level2, level3):
    """Returns the category of a given item (shot, asset, component, etc.)"""
    if tab == 2:
        if level3: return "component"
        elif level2: return "asset"
        elif level1: return "assetType"
    elif tab == 3:
        if level3: return "shotComponent"
        elif level2: return "shot"
        elif level1: return "sequence"
    return ""


def get_currently_open_path():
    """Returns the path of the currently open item."""
    level1 = cmds.optionVar(query="ops_currOpenLevel1") if cmds.optionVar(exists="ops_currOpenLevel1") else ""
    level2 = cmds.optionVar(query="ops_currOpenLevel2") if cmds.optionVar(exists="ops_currOpenLevel2") else ""
    level3 = cmds.optionVar(query="ops_currOpenLevel3") if cmds.optionVar(exists="ops_currOpenLevel3") else ""
    tab = cmds.optionVar(query="ops_currOpenTab") if cmds.optionVar(exists="ops_currOpenTab") else 0
    
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
            import opsNotes
            notes_array = opsNotes.read_xml(history_file)
            return "".join(notes_array)
        except Exception:
            pass
    return ""


def get_currently_selected_item(tab, depth):
    """Get the currently selected item under the given tab in the UI."""
    level1 = level2 = level3 = ""
    
    if tab == 2:
        if depth > 0 and cmds.optionVar(exists="ops_assetTypes") and cmds.textScrollList("ops_assetType_txtScrollList", exists=True):
            types = cmds.optionVar(query="ops_assetTypes") or []
            selected = cmds.textScrollList("ops_assetType_txtScrollList", query=True, selectIndexedItem=True) or []
            if selected: level1 = types[selected[0] - 1]
            
        if depth > 1 and cmds.optionVar(exists="ops_assets") and cmds.textScrollList("ops_asset_scrollList", exists=True):
            assets = cmds.optionVar(query="ops_assets") or []
            selected = cmds.textScrollList("ops_asset_scrollList", query=True, selectIndexedItem=True) or []
            if selected: level2 = assets[selected[0] - 1]
            
        if depth > 2 and cmds.optionVar(exists="ops_components") and cmds.textScrollList("ops_componentScrollList", exists=True):
            components = cmds.optionVar(query="ops_components") or []
            selected = cmds.textScrollList("ops_componentScrollList", query=True, selectIndexedItem=True) or []
            if selected: level3 = components[selected[0] - 1]
            
    elif tab == 3:
        if depth > 0 and cmds.optionVar(exists="ops_sequences") and cmds.textScrollList("ops_sequenceScrollList", exists=True):
            sequences = cmds.optionVar(query="ops_sequences") or []
            selected = cmds.textScrollList("ops_sequenceScrollList", query=True, selectIndexedItem=True) or []
            if selected: level1 = sequences[selected[0] - 1]
            
        if depth > 1 and cmds.optionVar(exists="ops_shots") and cmds.textScrollList("ops_shotScrollList", exists=True):
            shots = cmds.optionVar(query="ops_shots") or []
            selected = cmds.textScrollList("ops_shotScrollList", query=True, selectIndexedItem=True) or []
            if selected: level2 = shots[selected[0] - 1]
            
        if depth > 2 and cmds.optionVar(exists="ops_shotComponents") and cmds.textScrollList("ops_shotComponentScrollList", exists=True):
            components = cmds.optionVar(query="ops_shotComponents") or []
            selected = cmds.textScrollList("ops_shotComponentScrollList", query=True, selectIndexedItem=True) or []
            if selected: level3 = components[selected[0] - 1]
            
    return [level1, level2, level3]