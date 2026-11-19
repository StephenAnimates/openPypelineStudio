"""Maya-specific file handling operations for openPypeline Studio.

Dynamically loaded by :class:`~openpypeline.ops_engine.OpsEngine` when Autodesk
Maya is detected in ``sys.modules``. Provides standardized scene opening,
saving, importing, referencing, and workspace query helpers backed by
``maya.cmds``.

:File: file.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import logging
import os
from typing import Optional

import maya.cmds as cmds

#: Module logger for Maya file and plugin operations.
logger = logging.getLogger("openPypeline.maya.file")

#: Mapping of lowercase file extensions to Maya internal file type identifiers.
FILE_TYPES: dict[str, str] = {
    ".ma": "mayaAscii",
    ".mb": "mayaBinary",
    ".usd": "USD Export",
    ".usda": "USD Export",
    ".usdc": "USD Export",
    ".abc": "Alembic",
}


def get_file_type(extension: Optional[str]) -> Optional[str]:
    """Return Maya's internal file type identifier for the given extension.

    :param extension: File extension including leading dot (for example,
        ``".ma"`` or ``".abc"``).
    :returns: Maya file type string from :data:`FILE_TYPES`, or ``None`` if
        ``extension`` is empty or unsupported.
    """
    return FILE_TYPES.get(extension.lower()) if extension else None


def get_workspace_root() -> str:
    """Return Maya's active workspace root directory.

    Queries ``cmds.workspace(query=True, rootDirectory=True)`` and falls back
    to ``os.getcwd()`` if the workspace query raises an exception.

    :returns: Absolute path to the active Maya workspace root directory.
    """
    try:
        return cmds.workspace(query=True, rootDirectory=True)
    except Exception as e:
        logger.warning(f"Failed to query Maya workspace root: {e}")
        return os.getcwd()


def _ensure_plugins_loaded(
    filepath: Optional[str] = None, file_type: Optional[str] = None
) -> None:
    """Ensure required Maya plugins are loaded based on file extension or type.

    Loads ``mayaUsdPlugin`` for USD formats (``.usd``, ``.usda``, ``.usdc``)
    and ``AbcImport`` / ``AbcExport`` for Alembic (``.abc``) when not already
    loaded.

    :param filepath: Optional target file path used to inspect the extension.
    :param file_type: Optional Maya file type string (for example,
        ``"USD Export"`` or ``"Alembic"``).
    """
    ext = os.path.splitext(filepath)[-1].lower() if filepath else ""

    if ext in [".usd", ".usda", ".usdc"] or file_type == "USD Export":
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            try:
                cmds.loadPlugin("mayaUsdPlugin")
            except Exception as e:
                logger.error(f"Failed to load Maya USD Plugin: {e}")

    if ext == ".abc" or file_type == "Alembic":
        for plugin in ["AbcImport", "AbcExport"]:
            if not cmds.pluginInfo(plugin, query=True, loaded=True):
                try:
                    cmds.loadPlugin(plugin)
                except Exception as e:
                    logger.error(f"Failed to load {plugin}: {e}")


def open(filepath: str) -> bool:
    """Open a Maya scene file or supported interchange container.

    Verifies that ``filepath`` exists on disk, loads required USD/Alembic
    plugins via :func:`_ensure_plugins_loaded`, and calls
    ``cmds.file(filepath, force=True, open=True)``.

    :param filepath: Full path to the Maya scene (``.ma``, ``.mb``) or
        supported container file to open.
    :returns: ``True`` if the file opened successfully, ``False`` if the file
        does not exist or ``cmds.file`` raises an error.
    """
    if not os.path.exists(filepath):
        cmds.warning(f"openPypeline Studio: File does not exist: {filepath}")
        return False

    _ensure_plugins_loaded(filepath=filepath)

    try:
        cmds.file(filepath, force=True, open=True)
        logger.info(f"Successfully opened {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to open {filepath}. Error: {e}")
        return False
def save() -> bool:
    """Save the current Maya scene.

    :returns: ``True`` if ``cmds.file(save=True)`` succeeded, ``False`` if an
        exception occurred.
    """
    try:
        cmds.file(save=True)
        logger.info("Successfully saved scene.")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to save. Error: {e}")
        return False


def import_file(filepath: str) -> bool:
    """Import a file into the current Maya scene.

    Ensures required USD or Alembic plugins are loaded via
    :func:`_ensure_plugins_loaded` before calling ``cmds.file(filepath, i=True)``.

    :param filepath: Full path to the scene or interchange file to import.
    :returns: ``True`` if the file imported successfully, ``False`` otherwise.
    """
    _ensure_plugins_loaded(filepath=filepath)

    try:
        cmds.file(filepath, i=True)
        logger.info(f"Successfully imported {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to import {filepath}. Error: {e}")
        return False


def reference_file(filepath: str) -> bool:
    """Reference a file into the current Maya scene.

    Ensures required USD or Alembic plugins are loaded via
    :func:`_ensure_plugins_loaded` before calling
    ``cmds.file(filepath, reference=True)``.

    :param filepath: Full path to the scene or interchange file to reference.
    :returns: ``True`` if the file was referenced successfully, ``False``
        otherwise.
    """
    _ensure_plugins_loaded(filepath=filepath)

    try:
        cmds.file(filepath, reference=True)
        logger.info(f"Successfully referenced {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to reference {filepath}. Error: {e}")
        return False


def new_file() -> bool:
    """Create a new empty Maya scene.

    :returns: ``True`` if ``cmds.file(force=True, newFile=True)`` succeeded,
        ``False`` otherwise.
    """
    try:
        cmds.file(force=True, newFile=True)
        logger.info("Created new scene.")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to create new scene. Error: {e}")
        return False


def save_as(filepath: str, file_type: Optional[str] = None) -> bool:
    """Rename and save the current Maya scene to ``filepath``.

    :param filepath: Destination file path for the saved scene.
    :param file_type: Optional Maya file type identifier (for example,
        ``"mayaAscii"`` or ``"mayaBinary"``).
    :returns: ``True`` if renaming and saving succeeded, ``False`` otherwise.
    """
    try:
        cmds.file(rename=filepath)
        kwargs: dict[str, Any] = {"save": True}
        if file_type:
            kwargs["type"] = file_type
        cmds.file(**kwargs)
        logger.info(f"Successfully saved as {filepath}")
        return True
    except Exception as e:
        cmds.warning(f"openPypeline Studio: Failed to save as {filepath}. Error: {e}")
        return False
def execute_command(command: str) -> bool:
    """Execute a user-authored Python command in Maya's scene context.

    Evaluates ``command`` with ``maya.cmds`` exposed as ``cmds`` in the local
    namespace.

    :param command: Python source string to execute before mastering.
    :returns: ``True`` if execution completed without errors, ``False``
        otherwise.
    """
    try:
        exec(command, {"cmds": cmds})
        return True
    except Exception as e:
        logger.error(f"Failed to execute Master command: {e}")
        return False


def export_file(
    filepath: str, file_type: Optional[str] = None, selected: bool = False
) -> bool:
    """Export the current Maya scene or active selection to ``filepath``.

    Loads required USD or Alembic plugins via :func:`_ensure_plugins_loaded`
    and passes native Maya export flags when ``file_type`` is ``"mayaAscii"``,
    ``"mayaBinary"``, or ``None``.

    :param filepath: Destination file path for the exported asset.
    :param file_type: Optional Maya file type identifier (for example,
        ``"mayaAscii"``, ``"USD Export"``, or ``"Alembic"``).
    :param selected: When ``True``, exports only selected objects; when
        ``False``, exports the entire scene.
    :returns: ``True`` if ``cmds.file`` export succeeded, ``False`` otherwise.
    """
    _ensure_plugins_loaded(filepath=filepath, file_type=file_type)

    try:
        kwargs: dict[str, Any] = {"force": True}
        if file_type:
            kwargs["type"] = file_type

        if selected:
            kwargs["exportSelected"] = True
        else:
            kwargs["exportAll"] = True
            # Only pass Maya-specific export flags if using a native Maya format
            if file_type in ["mayaAscii", "mayaBinary", None]:
                kwargs["preserveReferences"] = True
                kwargs["constructionHistory"] = True
                kwargs["channels"] = True
                kwargs["constraints"] = True
                kwargs["expressions"] = True
                kwargs["shader"] = True

        cmds.file(filepath, **kwargs)
        logger.info(f"Successfully exported to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to export {filepath}. Error: {e}")
        return False


def flatten_references(master_name: str, workshop_name: str) -> None:
    """Flatten the scene by importing all loaded referenced files.

    Prompts the user via ``cmds.confirmDialog`` to keep or remove any unloaded
    (deferred) references before importing active references into the master
    scene.

    :param master_name: Display name of the target master file shown in the
        unloaded-reference prompt.
    :param workshop_name: Display name of the source workshop file shown in
        the unloaded-reference prompt.
    """
    referenced_files = cmds.file(query=True, reference=True) or []
    if not referenced_files:
        logger.warning("openPypeline Studio: no references to import")
        return

    for ref in referenced_files:
        if cmds.file(ref, query=True, deferReference=True):
            msg = (
                f"Referenced file '{ref}' is currently unloaded and cannot be imported.\n"
                f"Would you like to keep or remove this reference in the {master_name} file (it will remain in the {workshop_name} file)?"
            )
            result = cmds.confirmDialog(
                title="openPypeline Studio",
                message=msg,
                button=["Keep", "Remove"],
                defaultButton="Keep",
            )
            if result == "Remove":
                cmds.file(ref, removeReference=True)
        else:
            cmds.file(ref, importReference=True)
            logger.info(f"{ref} imported into current file")


def delete_display_layers() -> None:
    """Delete all Maya display layers except ``defaultLayer``."""
    layers = cmds.ls(type="displayLayer") or []
    for layer in layers:
        if layer != "defaultLayer":
            cmds.delete(layer)


def set_workspace(proj_path: str, rules: dict[str, str]) -> bool:
    """Configure Maya file rules and activate the project workspace.

    :param proj_path: Root directory path of the Maya workspace to open.
    :param rules: Mapping of Maya workspace file rule names (such as
        ``"scene"`` or ``"sourceImages"``) to relative directory paths.
    :returns: ``True`` if the workspace rules and active project were set
        successfully, ``False`` otherwise.
    """
    try:
        for rule_name, rule_path in rules.items():
            if rule_path:
                cmds.workspace(fileRule=[rule_name, rule_path])
        cmds.workspace(proj_path, openWorkspace=True)
        logger.info(f"Set workspace to {proj_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to set workspace: {e}")
        return False
def is_modified() -> bool:
    """Return ``True`` if the current Maya scene has unsaved changes.

    :returns: ``True`` when ``cmds.file(query=True, modified=True)`` is
        truthy, otherwise ``False``.
    """
    return bool(cmds.file(query=True, modified=True))


def record_playblast(filepath: str) -> bool:
    """Record a movie playblast of the current viewport to ``filepath``.

    :param filepath: Destination file path for the recorded movie playblast.
    :returns: ``True`` if ``cmds.playblast`` succeeded, ``False`` otherwise.
    """
    try:
        cmds.playblast(
            filename=filepath,
            forceOverwrite=True,
            format="movie",
            viewer=False,
            showOrnaments=False,
        )
        logger.info(f"Playblast recorded to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to record playblast: {e}")
        return False


def create_thumbnail(filepath: str) -> bool:
    """Capture a 164x105 JPEG viewport snapshot at the current frame.

    Temporarily sets ``defaultRenderGlobals.imageFormat`` to JPEG (``8``),
    captures a single-frame playblast image to ``filepath``, and restores the
    previous render image format setting.

    :param filepath: Destination file path for the generated thumbnail image.
    :returns: ``True`` if thumbnail capture succeeded, ``False`` otherwise.
    """
    try:
        curr_frame = cmds.currentTime(query=True)
        format_val = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # JPEG
        cmds.playblast(
            frame=curr_frame,
            format="image",
            completeFilename=filepath,
            showOrnaments=False,
            viewer=False,
            widthHeight=(164, 105),
            percent=100,
        )
        cmds.setAttr("defaultRenderGlobals.imageFormat", format_val)
        logger.info(f"Thumbnail created at {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to create thumbnail: {e}")
        return False
