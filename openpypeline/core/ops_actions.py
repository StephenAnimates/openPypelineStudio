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

    master_name = os.path.basename(new_master_filepath)
    dcc = OpsEngine().file_handler
    if dcc is None:
        logger.error("No DCC file handler is available. Aborting.")
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

    if not dcc.save_as(new_master_filepath):
        logger.error("Failed to save master file. Aborting.")
        return False

    from . import ops_project

    project_name = prefs.get_pref("ops_currProjectName", "")
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

    logger.info("Master process completed successfully.")
    return True