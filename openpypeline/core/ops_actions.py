"""
File: ops_actions.py
Description: Central action handler for openPypeline Studio.
             This module contains the core logic for operations like creating items,
             saving files, and interacting with the pipeline, decoupled from the UI.
"""
import logging
import os
import ntpath
import uuid
from dataclasses import asdict

from ..ops_engine import OpsEngine
from . import ops_info
from .models import ItemContext, ProjectConfig
from .util import prefs
from .version.Version import git, perforce, svn

logger = logging.getLogger("openPypeline.actions")


class ProjectActionError(Exception):
    """An expected project operation failure that can be shown to the user."""


_MAYA_FILE_TYPES = {
    ".ma": "mayaAscii",
    ".mb": "mayaBinary",
    ".usd": "USD Export",
    ".usda": "USD Export",
    ".abc": "Alembic",
}


def _project_config_data(config: ProjectConfig) -> dict:
    """Convert project configuration to a validated, local-root-aware mapping."""
    from . import ops_project

    if not isinstance(config, ProjectConfig):
        raise ProjectActionError("Project settings are invalid.")
    project_data = asdict(config)
    project_data["name"] = str(project_data.get("name", "")).strip()
    project_root = str(project_data.get("path", "")).strip()
    if not project_data["name"]:
        raise ProjectActionError("A project name is required.")
    if not project_root:
        raise ProjectActionError("A project folder is required.")
    if str(project_data.get("status", "1")) not in {"0", "1"}:
        raise ProjectActionError("Project status must be active or inactive.")

    project_root = os.path.abspath(os.path.expanduser(project_root))
    project_root_real = os.path.realpath(project_root)
    project_data["path"] = project_root
    for folder_field in ops_project.PROJECT_FOLDER_FIELDS:
        folder = str(project_data.get(folder_field, "")).strip()
        if not folder:
            continue
        drive, _ = ntpath.splitdrive(folder)
        if os.path.isabs(folder) or ntpath.isabs(folder) or drive:
            raise ProjectActionError(f"{folder_field} must be a relative path inside the project folder.")
        folder = folder.replace("\\", "/")
        project_data[folder_field] = folder
        if any(part == ".." for part in folder.split("/")):
            raise ProjectActionError(f"{folder_field} cannot escape the project folder.")
        target = os.path.realpath(os.path.join(project_root, *folder.split("/")))
        try:
            if os.path.commonpath((project_root_real, target)) != project_root_real:
                raise ProjectActionError(f"{folder_field} must stay inside the project folder.")
        except ValueError as error:
            raise ProjectActionError(f"{folder_field} must stay inside the project folder.") from error
    return project_data


def _get_project_store():
    """Return the project registry module after checking local setup."""
    from . import ops_project

    if not ops_project.get_proj_file():
        raise ProjectActionError(
            "The local project registry location is not set. Configure it in Project Manager first."
        )
    return ops_project


def _read_registered_projects(ops_project) -> list:
    """Read the local registry without turning corruption into an empty registry."""
    try:
        return ops_project.read_projects_data()
    except (OSError, ValueError) as error:
        raise ProjectActionError(f"Could not read the local project registry: {error}") from error


def _activate_registered_project(project_data: dict) -> bool:
    """Set local preferences to use one registered, active project."""
    if str(project_data.get("status", "1")) == "0":
        raise ProjectActionError("This project is inactive and cannot be selected.")
    project_root = os.path.abspath(os.path.expanduser(str(project_data.get("path", ""))))
    if not os.path.isdir(project_root):
        raise ProjectActionError(f"The project folder does not exist: {project_root}")

    path_preferences = {
        "ops_currProjectPath": None,
        "ops_libPath": "libraryfolder",
        "ops_shotPath": "scenesfolder",
        "ops_scriptsPath": "scriptsfolder",
        "ops_rendersPath": "rendersfolder",
        "ops_particlesPath": "particlesfolder",
        "ops_texturesPath": "texturesfolder",
        "ops_archivePath": "archivefolder",
        "ops_deletePath": "deletedfolder",
    }
    prefs.set_pref("ops_currProjectName", project_data["name"])
    for preference, field in path_preferences.items():
        value = project_root if field is None else os.path.join(project_root, str(project_data.get(field, "")))
        prefs.set_pref(preference, value.replace("\\", "/"))
    prefs.set_pref("ops_wip", project_data.get("wipname", "wip"))
    prefs.set_pref("ops_wipFormat", project_data.get("wipformat", "ma"))
    prefs.set_pref("ops_masterName", project_data.get("mastername", "master"))
    prefs.set_pref("ops_masterFormat", project_data.get("masterformat", "ma"))
    return True


def activate_project(project_name: str) -> bool:
    """Activate a registered project using this artist's local project path."""
    ops_project = _get_project_store()
    for project_data in _read_registered_projects(ops_project):
        if project_data.get("name") == project_name:
            return _activate_registered_project(project_data)
    raise ProjectActionError(f"Project '{project_name}' is not registered on this computer.")


def deactivate_project() -> None:
    """Clear local project preferences when no registered project is active."""
    for key in (
        "ops_currProjectName",
        "ops_currProjectPath",
        "ops_libPath",
        "ops_shotPath",
        "ops_scriptsPath",
        "ops_rendersPath",
        "ops_particlesPath",
        "ops_texturesPath",
        "ops_archivePath",
        "ops_deletePath",
    ):
        prefs.set_pref(key, "")


def create_or_edit_project(mode: int, old_name: str, config: ProjectConfig) -> int:
    """Create or edit a project, its shared manifest, and this artist's registry."""
    if mode not in (0, 1):
        raise ProjectActionError(f"Unsupported project operation mode: {mode}")
    ops_project = _get_project_store()
    project_data = _project_config_data(config)
    projects = _read_registered_projects(ops_project)
    existing_index = next(
        (index for index, project in enumerate(projects) if project.get("name") == old_name),
        None,
    ) if mode == 1 else None
    if mode == 1 and existing_index is None:
        raise ProjectActionError(f"Project '{old_name}' is not registered on this computer.")
    if any(
        project.get("name") == project_data["name"] and index != existing_index
        for index, project in enumerate(projects)
    ):
        raise ProjectActionError(f"A project named '{project_data['name']}' is already registered.")

    existing_project = projects[existing_index] if existing_index is not None else {}
    manifest_path = ops_project.get_project_manifest_path(project_data["path"])
    if mode == 0 and os.path.exists(manifest_path):
        raise ProjectActionError(
            "This folder already has an openPypeline project manifest. Use Join Existing instead."
        )

    project_id = str(existing_project.get("project_id") or uuid.uuid4())
    if mode == 1 and os.path.isfile(manifest_path):
        try:
            manifest = ops_project.read_project_manifest(project_data["path"])
        except (OSError, ValueError) as error:
            raise ProjectActionError(str(error)) from error
        manifest_id = manifest["project_id"]
        if existing_project.get("project_id") and existing_project["project_id"] != manifest_id:
            raise ProjectActionError("The local project registration does not match this folder's manifest.")
        project_id = manifest_id

    try:
        os.makedirs(project_data["path"], exist_ok=True)
        for field in ops_project.PROJECT_FOLDER_FIELDS:
            folder = str(project_data.get(field, "")).strip()
            if folder:
                os.makedirs(
                    os.path.join(project_data["path"], *folder.split("/")),
                    exist_ok=True,
                )
    except OSError as error:
        raise ProjectActionError(f"Could not create the project folder structure: {error}") from error

    if not ops_project.write_project_manifest(project_data["path"], project_id, project_data):
        raise ProjectActionError("Could not write the shared project manifest.")

    project_data["project_id"] = project_id
    if existing_index is None:
        projects.append(project_data)
    else:
        projects[existing_index] = project_data
    if not ops_project.rewrite_proj_file(projects):
        raise ProjectActionError("Could not update this artist's local project registry.")

    if str(project_data.get("status", "1")) == "0":
        if prefs.get_pref("ops_currProjectName", "") in {old_name, project_data["name"]}:
            deactivate_project()
    else:
        _activate_registered_project(project_data)
    return 1


def join_existing_project(project_root: str) -> int:
    """Register a shared project locally without creating or changing its files."""
    ops_project = _get_project_store()
    selected_root = str(project_root).strip()
    if not selected_root:
        raise ProjectActionError("Select a project folder to join.")
    root = os.path.abspath(os.path.expanduser(selected_root))
    if not os.path.isdir(root):
        raise ProjectActionError(f"The selected project folder does not exist: {root}")

    try:
        manifest = ops_project.read_project_manifest(root)
    except (OSError, ValueError) as error:
        raise ProjectActionError(str(error)) from error

    manifest_project = dict(manifest["project"])
    config_fields = set(ProjectConfig.__dataclass_fields__)
    config_data = {
        key: value
        for key, value in manifest_project.items()
        if key in config_fields
    }
    config_data["path"] = root
    project_data = _project_config_data(ProjectConfig(**config_data))
    project_data["project_id"] = manifest["project_id"]

    projects = _read_registered_projects(ops_project)
    for existing in projects:
        if (
            existing.get("name") == project_data["name"]
            and existing.get("project_id") != manifest["project_id"]
        ):
            raise ProjectActionError(
                f"A different project named '{project_data['name']}' is already registered."
            )
    for index, existing in enumerate(projects):
        if existing.get("project_id") == manifest["project_id"]:
            existing_path = os.path.abspath(os.path.expanduser(str(existing.get("path", ""))))
            if existing_path != root:
                raise ProjectActionError(
                    f"Project '{project_data['name']}' is already registered at {existing_path}."
                )
            projects[index] = project_data
            if not ops_project.rewrite_proj_file(projects):
                raise ProjectActionError("Could not update this artist's local project registry.")
            if str(project_data.get("status", "1")) != "0":
                _activate_registered_project(project_data)
            elif prefs.get_pref("ops_currProjectName", "") == existing.get("name"):
                deactivate_project()
            return 1

    if not os.path.isdir(root):
        raise ProjectActionError(f"The selected project folder does not exist: {root}")
    projects.append(project_data)
    if not ops_project.rewrite_proj_file(projects):
        raise ProjectActionError("Could not update this artist's local project registry.")
    if str(project_data.get("status", "1")) != "0":
        _activate_registered_project(project_data)
    return 1


def _save_scene_file(dcc, filepath: str) -> bool:
    """Save or export a scene using the active DCC's supported file operation."""
    extension = os.path.splitext(filepath)[1].lower()
    file_type = _MAYA_FILE_TYPES.get(extension)
    if file_type in {"USD Export", "Alembic"}:
        export_file = getattr(dcc, "export_file", None)
        if not callable(export_file):
            logger.error("The active DCC cannot export %s files.", extension)
            return False
        return bool(export_file(filepath, file_type, selected=False))

    save_as = getattr(dcc, "save_as", None)
    if not callable(save_as):
        logger.error("The active DCC cannot save scene files.")
        return False
    if file_type:
        return bool(save_as(filepath, file_type))
    return bool(save_as(filepath))


def save_master_file(context: ItemContext, options: dict):
    """
    Handles the entire process of saving a master file.

    Args:
        context (ItemContext): The context of the item being mastered.
        options (dict): A dictionary of options from the Master Switchboard UI,
                        e.g., {"comment": "...", "import_references": True}.
    """
    logger.info(f"Beginning master process for {context.item_name}...")

    new_master_filepath = ops_info.get_file_name(context, "master")
    if not new_master_filepath:
        logger.error("Could not determine the master file path. Aborting.")
        return False

    new_wip_filepath = ops_info.get_file_name(context, "nextWorkshop")
    if not new_wip_filepath:
        logger.error("Could not determine the next WIP path. Aborting.")
        return False
    if os.path.exists(new_wip_filepath):
        logger.error(
            "The next WIP file already exists; refusing to overwrite it: %s",
            new_wip_filepath,
        )
        return False

    after = options.get("after", 1)
    if after not in (1, 2, 3):
        logger.error("Invalid post-Master action: %s", after)
        return False

    master_name = os.path.basename(new_master_filepath)
    dcc = OpsEngine().file_handler
    if dcc is None:
        logger.error("No DCC file handler is available. Aborting.")
        return False

    os.makedirs(os.path.dirname(new_wip_filepath), exist_ok=True)
    if not _save_scene_file(dcc, new_wip_filepath):
        logger.error(
            "Could not save the next WIP file; Master was not published."
        )
        return False

    if options.get("import_references", False):
        wip_path = ops_info.get_file_name(context, "workshop")
        wip_name = os.path.basename(wip_path) if wip_path else "WIP"
        flatten_references = getattr(dcc, "flatten_references", None)
        if not callable(flatten_references):
            logger.error(
                "The active DCC does not support flattening references. Aborting."
            )
            return False
        flatten_references(master_name, wip_name)

    if options.get("delete_display_layers", False):
        delete_display_layers = getattr(dcc, "delete_display_layers", None)
        if not callable(delete_display_layers):
            logger.error(
                "The active DCC does not support deleting display layers."
            )
            return False
        delete_display_layers()

    custom_command = options.get("custom_command", "").strip()
    if custom_command:
        execute_command = getattr(dcc, "execute_command", None)
        if not callable(execute_command):
            logger.error(
                "The active DCC cannot execute the requested Master command."
            )
            return False
        if not execute_command(custom_command):
            logger.error("The custom Master command failed.")
            return False

    if not _save_scene_file(dcc, new_master_filepath):
        logger.error("Failed to save master file. Aborting.")
        return False

    project_name = prefs.get_pref("ops_currProjectName", "")
    project_data = {}
    if project_name:
        from . import ops_project
        project_data = ops_project.get_project(project_name)
    vcs_type = str(project_data.get("vcs_type") or "none").lower()
    vcs_comment = options.get(
        "comment",
        f"Published master for {context.item_name}",
    )

    if vcs_type != "none":
        vcs_handler = None
        if vcs_type == "git":
            vcs_handler = git()
        elif vcs_type == "svn":
            vcs_handler = svn()
        elif vcs_type == "perforce":
            vcs_handler = perforce()

        if vcs_handler:
            logger.info(f"Publishing '{new_master_filepath}' to {vcs_type.upper()}...")
            success = vcs_handler.publish(filepath=new_master_filepath, comment=vcs_comment)
            if not success:
                logger.error(f"Failed to publish to {vcs_type.upper()}.")
                # Optionally, show a warning to the user via a UI call
        else:
            logger.warning(f"Unknown VCS type configured in project settings: '{vcs_type}'")

    if after == 1:
        open_file = getattr(dcc, "open", None)
        if callable(open_file) and open_file(new_wip_filepath):
            prefs.set_pref("ops_currOpenType", "workshop")
            prefs.set_pref(
                "ops_currOpenVersion",
                ops_info.get_version_from_file(new_wip_filepath),
            )
        else:
            logger.error(
                "Master was saved, but the new WIP could not be reopened: %s",
                new_wip_filepath,
            )
    elif after == 2:
        open_file = getattr(dcc, "open", None)
        if callable(open_file):
            if open_file(new_master_filepath):
                prefs.set_pref("ops_currOpenType", "master")
                prefs.set_pref("ops_currOpenVersion", 0)
            else:
                logger.error(
                    "Master was saved, but could not be opened: %s",
                    new_master_filepath,
                )
    else:
        new_file = getattr(dcc, "new_file", None)
        if callable(new_file):
            if new_file():
                prefs.set_pref("ops_currOpenType", "")
                prefs.set_pref("ops_currOpenVersion", 0)
            else:
                logger.error(
                    "Master was saved, but the DCC could not create a new scene."
                )

    logger.info("Master process completed successfully.")
    return True


def save_master(
    comment: str,
    flatten: bool,
    delete_disp_layers: bool,
    after: int,
    custom_command: str = "",
    task_id: int = 0,
) -> bool:
    """Save a Master for the item selected in the Maya UI."""
    context = ItemContext(
        tab=prefs.get_pref("ops_currOpenTab", 0),
        level1=prefs.get_pref("ops_currOpenLevel1", ""),
        level2=prefs.get_pref("ops_currOpenLevel2", ""),
        level3=prefs.get_pref("ops_currOpenLevel3", ""),
    )
    saved = save_master_file(
        context,
        {
            "comment": comment,
            "import_references": flatten,
            "delete_display_layers": delete_disp_layers,
            "after": after,
            "custom_command": custom_command,
        },
    )
    if not saved:
        return False

    if task_id:
        from openpypeline.app.maya.core import tracker_factory

        tracker = tracker_factory.get_tracker()
        if tracker is None:
            logger.warning(
                "Master was saved, but no production tracker is available "
                "to publish it."
            )
        elif not tracker.publish_version(
            task_id,
            ops_info.get_file_name(context, "master"),
            0,
            comment,
        ):
            logger.warning(
                "Master was saved, but publishing it to task %s failed.",
                task_id,
            )

    return True