"""
File: ops_actions.py
Description: Central action handler for openPypeline Studio.
             This module contains the core logic for operations like creating items,
             saving files, and interacting with the pipeline, decoupled from the UI.
"""
import logging
import os

# Assuming these modules exist based on project structure
from . import ops_project
from . import ops_item
from .opsEngine import opsEngine
from .models import ItemContext

# Import the version control classes
from .version import Version, git, svn, perforce

logger = logging.getLogger("openPypeline.actions")


def save_master_file(context: ItemContext, options: dict):
    """
    Handles the entire process of saving a master file.

    Args:
        context (ItemContext): The context of the item being mastered.
        options (dict): A dictionary of options from the Master Switchboard UI,
                        e.g., {"comment": "...", "import_references": True}.
    """
    logger.info(f"Beginning master process for {context.get_item_name()}...")

    # This is a hypothetical reconstruction of the mastering process.
    # Your actual implementation may vary.

    # 1. Get file paths and names from the item context
    item_data = ops_item.get_item_data(context)
    master_path = item_data.get("master_path")  # e.g., /path/to/project/assets/chars/man/model/master/
    master_name = item_data.get("master_name")  # e.g., man_model_master.mb
    new_master_filepath = os.path.join(master_path, master_name)

    # 2. Perform pre-save operations (like flattening references)
    dcc = opsEngine.get_dcc_handler()
    if options.get("import_references", False):
        wip_name = item_data.get("wip_name", "WIP")
        dcc.flatten_references(master_name, wip_name)

    # 3. Save the actual master file
    if not dcc.save_as(new_master_filepath):
        logger.error("Failed to save master file. Aborting.")
        return False

    # 4. --- HOOK: Add to Version Control ---
    # This is the new integration point for the publish() method.
    project_data = ops_project.get_project_data(context.project)
    vcs_type = project_data.get("vcs_type", "none").lower()
    vcs_comment = options.get("comment", f"Published master for {context.get_item_name()}")

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

    # 5. Perform post-save operations (e.g., update history, create thumbnail)
    # ... existing logic would go here ...

    logger.info("Master process completed successfully.")
    return True

# ... other action functions like create_new_item, remove_project, etc. ...