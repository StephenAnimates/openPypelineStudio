Add-on Developer Guide
======================

OpenPypeline Studio features zero-configuration **Add-on Discovery** allowing Pipeline Technical Directors (TDs) and developers to add custom Python tools directly into the **Tools** menu without modifying core framework code.

The following guide explains where to place add-ons, the required module interface, optional metadata attributes, and how to access active project context and host adapters from your scripts.

Where Add-ons Live
------------------

When the Main UI initializes, :meth:`~openpypeline.ui.ops_main_controller.OpsMainController._load_addons` scans three locations in order and groups discovered scripts into separate sections under the **Tools** menu:

.. list-table:: Add-on Discovery Locations
   :widths: 22 38 40
   :header-rows: 1

   * - Scope
     - Directory Location
     - Purpose
   * - **Core Add-ons**
     - ``openpypeline/core/addons/``
     - Host-agnostic utilities (project migration, batch file checks, note tools) available across every DCC.
   * - **Host-Specific Add-ons**
     - ``openpypeline/app/<host>/core/addons/``
     - Tools tailored to a specific DCC SDK (for example ``maya.cmds``, ``hou``, or ``nuke``).
   * - **External Studio Add-ons**
     - Directories listed in ``OPENPYPELINE_ADDONS_PATH``
     - Site-specific studio tools stored outside the openPypeline repository so framework updates never overwrite custom scripts.

.. note::

   Any ``.py`` file inside these directories is evaluated automatically in alphabetical order. Files starting with ``__`` (such as ``__init__.py``) are ignored.

Minimal Add-on Structure
------------------------

Every add-on is a standard Python module exposing a zero-argument ``run()`` function:

.. code-block:: python

   """Example custom studio add-on for openPypeline Studio."""

   from PySide6 import QtWidgets

   ADDON_NAME = "Hello Studio"
   ADDON_ENABLED = True
   ADDON_TOOLTIP = "Display a confirmation message from a custom add-on."


   def run() -> None:
       """Entry point invoked when the user clicks the menu action."""
       QtWidgets.QMessageBox.information(
           None,
           ADDON_NAME,
           "Custom add-on executed successfully.",
       )

Module Metadata Attributes
--------------------------

The loader inspects the following module-level attributes when building the **Tools** menu:

* ``run()`` *(Required)*: Callable entry point executed when the menu item is triggered. Must accept zero required arguments.
* ``ADDON_NAME`` *(Optional, ``str``)*: Display label shown in the **Tools** menu. If omitted, openPypeline formats the filename automatically (for example, ``batch_export.py`` becomes ``Batch Export``).
* ``ADDON_ENABLED`` *(Optional, ``bool``)*: Defaults to ``True``. Set to ``False`` to temporarily hide an experimental or work-in-progress add-on from the menu without deleting the file.
* ``ADDON_TOOLTIP`` *(Optional, ``str``)*: Optional hover tooltip and status bar description attached to the menu action.

Configuring External Source Add-on Folders
------------------------------------------

To load studio tools from an external network share or local repository without copying files into the openPypeline installation directory, set the ``OPENPYPELINE_ADDONS_PATH`` environment variable before launching your DCC:

**macOS / Linux:**

.. code-block:: bash

   export OPENPYPELINE_ADDONS_PATH="/studio/pipeline/ops_addons"

**Windows (PowerShell):**

.. code-block:: powershell

   $env:OPENPYPELINE_ADDONS_PATH = "Z:\pipeline\ops_addons"

Multiple directories can be separated using the platform path separator (``:`` on macOS/Linux, ``;`` on Windows). External add-ons are imported dynamically via :mod:`importlib.util` and do not require an ``__init__.py`` file or ``sys.path`` modifications.

Accessing Pipeline Context & Services
-------------------------------------

Add-ons can import core services, data models, and the active host engine directly:

.. code-block:: python

   """Inspect the active project and current scene workspace."""

   from openpypeline.core import ops_info
   from openpypeline.ops_engine import OpsEngine

   ADDON_NAME = "Print Active Project Info"
   ADDON_TOOLTIP = "Log the active project configuration and host workspace."


   def run() -> None:
       engine = OpsEngine()
       project_name = ops_info.get_current_project_name()
       workspace = engine.file_handler.get_workspace_root()
       print(f"Host: {engine.host_app} | Project: {project_name} | Workspace: {workspace}")

Refreshing the UI After Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your add-on creates or modifies projects, assets, or shots on disk and you want the active openPypeline window to reflect those changes immediately, access the shared window manager:

.. code-block:: python

   from openpypeline.ui.ui_objects import ui_objects

   if getattr(ui_objects, "opsMainController", None) is not None:
       ui_objects.opsMainController.view.ops_refreshUIButton.click()

Best Practices for Add-on Authors
---------------------------------

* **Keep Core Add-ons Host-Agnostic:** Do not import ``maya.cmds``, ``hou``, or ``nuke`` inside ``openpypeline/core/addons/``. Place DCC-dependent scripts under ``openpypeline/app/<host>/core/addons/``.
* **Handle Missing Projects Gracefully:** Artists may open the **Tools** menu before selecting or creating a project. Always verify that an active project is configured before reading or writing project files.
* **Reloading During Development:** Built-in package add-ons are automatically reloaded with ``importlib.reload()`` each time the Main UI opens, allowing you to iterate on scripts without restarting your DCC.
* **Include Sphinx Docstrings:** Add a module docstring, ``:File:``, and ``:License:`` header so ``sphinx-apidoc`` includes your add-on cleanly in the generated API reference.
