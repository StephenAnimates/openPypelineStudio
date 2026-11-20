"""DCC-agnostic path validation, module sourcing, and setup utilities.

Provides host-independent repository root resolution, project registry path validation, and dynamic Python module sourcing shared across Autodesk Maya, SideFX Houdini, and standalone tools.

:File: ops_loader.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import importlib
import logging
import os
import sys
from typing import Optional

# Resolve the repository root directory (parent of the 'openpypeline' package)
_root_path: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
).replace("\\", "/")
if _root_path not in sys.path:
    sys.path.insert(0, _root_path)

#: Module logger for core loader and path validation operations.
logger = logging.getLogger("openPypeline.loader")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)

#: Preference key storing the active project registry directory path.
PROJECT_PATH_PREF: str = "ops_projectFilePath"


def get_root_path() -> str:
    """Return the normalized forward-slash path to the repository root.

    :returns: Absolute path to the directory containing ``openpypeline/``.
    """
    return _root_path


def get_default_project_file_path() -> str:
    """Return the default directory path used for the project registry file.

    :returns: Normalized path ending in ``openpypeline/``.
    """
    return os.path.join(_root_path, "openpypeline/").replace("\\", "/")


def is_valid_script_path(root_path: Optional[str] = None) -> bool:
    """Check whether ``root_path`` contains a valid openPypeline package.

    :param root_path: Optional directory path to check; defaults to
        :data:`_root_path`.
    :returns: ``True`` if ``root_path`` contains ``openpypeline/__init__.py``,
        ``False`` otherwise.
    """
    target_root = root_path if root_path is not None else _root_path
    if not target_root or not os.path.isdir(target_root):
        return False

    package_init = os.path.join(
        target_root, "openpypeline", "__init__.py"
    ).replace("\\", "/")
    return os.path.isfile(package_init)


def is_valid_project_file_path(folder: object) -> bool:
    """Check whether ``folder`` is a valid existing project registry directory.

    :param folder: Candidate directory path to validate.
    :returns: ``True`` if ``folder`` is a ``str`` pointing to an existing
        directory on disk, ``False`` otherwise.
    """
    return isinstance(folder, str) and os.path.isdir(folder)


def source_python_module(path: str) -> None:
    """Add ``path`` to ``sys.path`` and import/reload all Python modules within it.

    Skips silently if ``path`` does not exist on disk. Otherwise iterates over
    non-dunder ``.py`` files in ``path``, importing and reloading each module
    via :mod:`importlib`.

    :param path: Directory path containing Python modules to source.
    """
    if not os.path.isdir(path):
        logger.debug("Optional module path not found (skipping): %s", path)
        return

    if path not in sys.path:
        sys.path.append(path)
        logger.info("Appending %s to sys.path", path)

    logger.info("----- Sourcing Python from %s ------", path)
    for file_name in os.listdir(path):
        if file_name.endswith(".py") and not file_name.startswith("__"):
            module_name = os.path.splitext(file_name)[0]
            logger.info("//// Python Source: %s", module_name)
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
            except Exception as e:
                logger.warning(
                    "Failed to load python module %s: %s", module_name, e
                )
