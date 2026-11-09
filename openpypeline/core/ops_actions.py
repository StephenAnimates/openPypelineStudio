"""
File: ops_actions.py
Description: Central action handler for openPypeline Studio.
             This module contains the core logic for operations like creating items,
             saving files, and interacting with the pipeline, decoupled from the UI.
"""
import logging
import os

from ..ops_engine import OpsEngine
from . import ops_info
from .models import ItemContext
from .util import prefs
from .version.Version import git, perforce, svn

logger = logging.getLogger("openPypeline.actions")

_MAYA_FILE_TYPES = {
    ".ma": "mayaAscii",
    ".mb": "mayaBinary",
    ".usd": "USD Export",
    ".usda": "USD Export",
    ".abc": "Alembic",
}


def _save_scene_file(dcc, filepath: str) -> bool:
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