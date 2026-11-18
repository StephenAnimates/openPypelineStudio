"""Central action handler for openPypeline Studio.

Contains the core business logic for creating pipeline items, saving files,
managing project configurations, and executing revision-control actions,
decoupled from the UI layer.

:File: ops_actions.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core import ops_actions
    from openpypeline.core.models import ItemContext, Tab

    ctx = ItemContext(tab=Tab.ASSET, level1="characters", level2="woman")
"""

from dataclasses import asdict
import logging
import ntpath
import os
from typing import Any, Optional
import uuid

from ..ops_engine import OpsEngine
from . import ops_info
from .models import ItemContext, ProjectConfig
from .util import prefs
from .version.Version import git, perforce, svn

__all__ = [
    "ProjectActionError",
    "activate_project",
    "deactivate_project",
    "create_or_edit_project",
    "join_existing_project",
    "save_master_file",
    "save_master",
]

#: Module logger for core pipeline action execution.
logger = logging.getLogger("openPypeline.actions")

#: Mapping of project ``vcs_type`` keys to revision-control publisher classes.
VCS_HANDLERS: dict[str, Any] = {
    "git": git,
    "svn": svn,
    "perforce": perforce,
}

#: Mapping of active-project path preference keys to :class:`ProjectConfig` fields.
PROJECT_PATH_PREFS: dict[str, Optional[str]] = {
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

class ProjectActionError(Exception):
    """An expected project operation failure that can be shown to the user."""


def _project_config_data(config: ProjectConfig) -> dict[str, Any]:
    """Convert project configuration to a validated, local-root-aware mapping.

    Normalizes :attr:`~openpypeline.core.models.ProjectConfig.path` to an
    expanded absolute path and verifies that all configured project subfolders
    are safe relative paths contained within the project root.

    :param config: Structured :class:`~openpypeline.core.models.ProjectConfig`
        instance containing project settings and folder names.
    :returns: Validated dictionary mapping project configuration keys to
        normalized string values.
    :raises ProjectActionError: If ``config`` is invalid, required fields
        (``name`` or ``path``) are empty, ``status`` is not ``"0"`` or ``"1"``,
        or any configured subfolder path is absolute or escapes the project root.
    """
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


def _get_project_store() -> Any:
    """Return the project registry module after checking local setup.

    Verifies that the local project registry file path preference is configured
    via :func:`~openpypeline.core.ops_project.get_proj_file`.

    :returns: The :mod:`openpypeline.core.ops_project` module ready for
        registry read/write operations.
    :raises ProjectActionError: If the local project registry location has not
        been configured in user preferences.
    """
    from . import ops_project

    if not ops_project.get_proj_file():
        raise ProjectActionError(
            "The local project registry location is not set. Configure it in Project Manager first."
        )
    return ops_project


def _read_registered_projects(ops_project: Any) -> list[dict[str, Any]]:
    """Read the local registry without turning corruption into an empty registry.

    :param ops_project: Project registry module returned by
        :func:`_get_project_store`.
    :returns: List of registered project configuration dictionaries.
    :raises ProjectActionError: If reading or parsing the local project
        registry file raises an ``OSError`` or ``ValueError``.
    """
    try:
        return ops_project.read_projects_data()
    except (OSError, ValueError) as error:
        raise ProjectActionError(f"Could not read the local project registry: {error}") from error


def _activate_registered_project(project_data: dict[str, Any]) -> bool:
    """Set local preferences to use one registered, active project.

    Validates that the project is active (``status != "0"``) and that its root
    directory exists on disk, then writes all resolved project directory paths
    and naming/format tokens into user preferences.

    :param project_data: Validated project dictionary containing ``name``,
        ``path``, folder mappings, and WIP/master naming settings.
    :returns: ``True`` once all active project preferences have been updated.
    :raises ProjectActionError: If the project is marked inactive or its root
        directory does not exist on disk.
    """
    if str(project_data.get("status", "1")) == "0":
        raise ProjectActionError("This project is inactive and cannot be selected.")
    project_root = os.path.abspath(os.path.expanduser(str(project_data.get("path", ""))))
    if not os.path.isdir(project_root):
        raise ProjectActionError(f"The project folder does not exist: {project_root}")

    prefs.set_pref("ops_currProjectName", project_data["name"])
    for preference, field in PROJECT_PATH_PREFS.items():
        value = project_root if field is None else os.path.join(project_root, str(project_data.get(field, "")))
        prefs.set_pref(preference, value.replace("\\", "/"))
    prefs.set_pref("ops_wip", project_data.get("wipname", "wip"))
    prefs.set_pref("ops_wipFormat", project_data.get("wipformat", "ma"))
    prefs.set_pref("ops_masterName", project_data.get("mastername", "master"))
    prefs.set_pref("ops_masterFormat", project_data.get("masterformat", "ma"))
    return True


def activate_project(project_name: str) -> bool:
    """Activate a registered project using this artist's local project path.

    Looks up ``project_name`` in the local project registry and delegates to
    :func:`_activate_registered_project`.

    :param project_name: Display name of the registered project to activate.
    :returns: ``True`` once the project's paths and settings have been written
        to user preferences.
    :raises ProjectActionError: If ``project_name`` is not registered locally,
        is marked inactive, or its project folder is missing on disk.
    """
    ops_project = _get_project_store()
    for project_data in _read_registered_projects(ops_project):
        if project_data.get("name") == project_name:
            return _activate_registered_project(project_data)
    raise ProjectActionError(f"Project '{project_name}' is not registered on this computer.")


def deactivate_project() -> None:
    """Clear local project preferences when no registered project is active.

    Resets ``ops_currProjectName`` and all active project directory path
    preferences to empty strings.
    """
    for key in ("ops_currProjectName", *PROJECT_PATH_PREFS.keys()):
        prefs.set_pref(key, "")


def create_or_edit_project(mode: int, old_name: str, config: ProjectConfig) -> int:
    """Create or edit a project, its shared manifest, and this artist's registry.

    Validates ``config`` via :func:`_project_config_data`, ensures the directory
    hierarchy exists on disk, writes the shared project manifest, updates the
    local project registry, and activates (or deactivates) the project in user
    preferences based on its status.

    :param mode: Operation mode flag (``0`` to create a new project, ``1`` to
        edit an existing registered project).
    :param old_name: Existing project name to locate when ``mode == 1``.
    :param config: Validated :class:`~openpypeline.core.models.ProjectConfig`
        containing the target project settings and relative subfolders.
    :returns: ``1`` upon successfully creating or updating the project.
    :raises ProjectActionError: If ``mode`` is unsupported, validation fails,
        a duplicate project name or existing manifest conflicts with the
        operation, or filesystem/registry writes fail.
    """
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
    """Register a shared project locally without creating or changing its files.

    Reads the existing project manifest from ``project_root``, validates the
    resolved configuration via :func:`_project_config_data`, registers or
    updates the entry in this artist's local project registry, and activates
    the project in user preferences if its status is active.

    :param project_root: Filesystem path to an existing shared project folder
        containing an openPypeline project manifest.
    :returns: ``1`` upon successfully registering or updating the project.
    :raises ProjectActionError: If ``project_root`` is blank or missing, the
        manifest cannot be read, or a conflicting project name or path is
        already registered locally.
    """
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

    projects.append(project_data)
    if not ops_project.rewrite_proj_file(projects):
        raise ProjectActionError("Could not update this artist's local project registry.")
    if str(project_data.get("status", "1")) != "0":
        _activate_registered_project(project_data)
    return 1


def _save_scene_file(dcc: Any, filepath: str) -> bool:
    """Save or export a scene using the active DCC's supported file operation.

    Resolves the target file type via ``dcc.get_file_type``, ``dcc.FILE_TYPES``,
    or built-in extension fallbacks (``.ma``, ``.mb``, ``.usd``, ``.usda``,
    ``.abc``), and delegates to ``dcc.export_file`` for interchange formats or
    ``dcc.save_as`` for native scene formats.

    :param dcc: Active host file-operation adapter module or object.
    :param filepath: Target destination path for the saved or exported file.
    :returns: ``True`` if the DCC save or export operation succeeded, ``False``
        otherwise.
    """
    extension = os.path.splitext(filepath)[1].lower()

    # Query the file type from the active host adapter
    file_type = None
    get_file_type = getattr(dcc, "get_file_type", None)
    if callable(get_file_type):
        file_type = get_file_type(extension)
    elif hasattr(dcc, "FILE_TYPES") and isinstance(dcc.FILE_TYPES, dict):
        file_type = dcc.FILE_TYPES.get(extension)

    # Fallback format mapping for backward compatibility and test doubles
    if not file_type:
        fallback_types = {
            ".ma": "mayaAscii",
            ".mb": "mayaBinary",
            ".usd": "USD Export",
            ".usda": "USD Export",
            ".abc": "Alembic",
        }
        file_type = fallback_types.get(extension)

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


def save_master_file(context: ItemContext, options: dict[str, Any]) -> bool:
    """Execute the full master publishing workflow for a pipeline item.

    Saves a new incremental WIP snapshot first, applies optional scene cleanup
    steps (flattening references, deleting display layers, running a custom
    command), saves the published master file, optionally commits to the
    project's configured VCS backend, and executes the requested post-master
    scene action.

    :param context: Hierarchy coordinates of the item being mastered (see
        :class:`~openpypeline.core.models.ItemContext`).
    :param options: Switchboard options dictionary controlling master behavior.
        Supported keys include:

        * ``"comment"`` (*str*): Publish commit message.
        * ``"import_references"`` (*bool*): Flatten scene references before
          saving the master file.
        * ``"delete_display_layers"`` (*bool*): Remove display layers before
          saving the master file.
        * ``"custom_command"`` (*str*): Host command string to execute prior to
          saving.
        * ``"after"`` (*int*): Post-master action (``1`` to reopen the new WIP,
          ``2`` to open the published master, or ``3`` to start a new empty
          scene).
    :returns: ``True`` if the master file was saved successfully, ``False`` if
        validation, pre-save hooks, or file operations failed.
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
    """Save a Master for the item selected in the Maya UI.

    Builds an :class:`~openpypeline.core.models.ItemContext` from the active selection preferences, delegates publishing to :func:`save_master_file`, and optionally publishes the new master version to the active production tracker when ``task_id`` is non-zero.

    :param comment: Publish note or commit message associated with the master.
    :param flatten: When ``True``, flattens or imports scene references before saving the master file.
    :param delete_disp_layers: When ``True``, removes display layers prior to saving the master file.
    :param after: Post-master scene action (``1`` to reopen the new WIP, ``2`` to open the published master, or ``3`` to start a new empty scene).
    :param custom_command: Optional host command string executed before saving the master file.
    :param task_id: Optional production tracker task ID; when non-zero, publishes the saved master file to the configured tracker.
    :returns: ``True`` if the master file was saved (even if optional tracker publishing logs a warning), otherwise ``False``.
    """
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
        from openpypeline.core import tracker_factory

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
