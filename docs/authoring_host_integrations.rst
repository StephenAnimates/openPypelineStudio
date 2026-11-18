Authoring Host Integrations
===========================
OpenPypeline Studio (OPS) uses a modular host-adapter architecture to connect creative digital content creation (DCC) software to its core pipeline workflows. 

The core pipeline logic—such as asset naming tokens, 3-level hierarchy traversal (``ItemContext``), WIP version increments, Master publication, advisory heartbeat concurrency (``file_use.py``), and version control operations—is **100% host-agnostic** and resides entirely in ``openpypeline/core/``.

When adding or extending an integration for a new host application, **you do not need to modify any core files**. All host-specific behavior is encapsulated inside a self-contained package under ``openpypeline/app/<host>/``.

This guide details the integration architecture, execution archetypes, standardized file protocols, bootstrapper patterns, and automated testing strategies for authoring new host integrations.

Host Execution Archetypes
-------------------------
Creative production software integrates Python in different ways. Before developing an integration, identify which type best matches your target application:

1. In-Process Python Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Host applications that embeds a standard CPython interpreter and exposes an internal Python API, such as ``Autodesk Maya``, ``SideFX Houdini``, ``Foundry Nuke``, or ``Adobe Substance 3D Painter``.

* **How openPypeline runs:** Runs directly inside the host's memory space.
* **Host Detection:** ``OpsEngine`` detects the active environment by inspecting ``sys.modules`` for the host's signature package.
* **File Operations:** Directly invokes the host's Python API to open, save, merge, and export scene files.

2. Script-Bridged or Subprocess Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Host applications that do not embed an internal Python runtime or uses a proprietary scripting language (such as ZScript in ZBrush).

* **How openPypeline runs:** Runs as an external Python process, a system tray utility, or within a companion DCC (e.g., launching from Maya or standalone UI).
* **Communication Bridge:** The adapter communicates with the host via temporary command script files (e.g., executing a dynamically generated ZScript via command-line arguments or memory-mapped buffers), file watches, or an IPC socket.
* **File Operations:** The adapter prepares files on disk, triggers the host's external command to load or save tools (``.ztl``) or projects (``.zpr``), and verifies the output.

3. Game Engines & Real-Time Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Real-time editors often use C# (Unity) or C++/Python plugins, such as Unity and Unreal engine.

* **How openPypeline runs:** Runs either via in-engine embedded Python runtimes (e.g., the *Python for Unity* package or Unreal's embedded Python plugin) or through an editor TCP/REST socket bridge.
* **File Operations:** Interacts with the engine's asset database and scene management APIs (e.g., ``UnityEditor.SceneManagement.EditorSceneManager``) to manage scenes, prefabs, and textures.

Package Scaffold
----------------
Every DCC integration in openPypeline follows a standardized three-part package structure:

.. code-block:: text

   openpypeline/app/<host>/
   ├── __init__.py           # Package docstring and namespace declaration
   ├── loader.py             # Host bootstrapper: shelf buttons, menus, and UI initialization
   ├── file/
   │   ├── __init__.py
   │   └── file.py           # Implements the standard File Handler Protocol
   └── ui/
       ├── __init__.py
       └── ...               # Host-specific window docking, panels, or widgets (optional)

Step-by-Step Implementation Guide
---------------------------------

Step 1: Create the Host Directory Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create the directory for your target host under ``openpypeline/app/`` (for example, ``openpypeline/app/substance_painter/`` or ``openpypeline/app/zbrush/``):

.. code-block:: bash

   mkdir -p openpypeline/app/<host>/file
   mkdir -p openpypeline/app/<host>/ui
   touch openpypeline/app/<host>/__init__.py
   touch openpypeline/app/<host>/file/__init__.py
   touch openpypeline/app/<host>/ui/__init__.py

Step 2: Implement the File Handler Protocol (`file/file.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file handler is loaded dynamically by ``OpsEngine`` whenever the host is active. Create ``openpypeline/app/<host>/file/file.py`` and implement the 10 standard protocol functions:

.. code-block:: python

   """
   File: file.py
   Description: <Host>-specific file handling operations for openPypeline Studio.
   Dynamically loaded by OpsEngine when <Host> is detected.
   """

   import os
   import logging

   try:
       import <host_sdk>  # e.g., substance_painter, hou, nuke
   except ImportError:
       <host_sdk> = None

   logger = logging.getLogger("openPypeline.<host>.file")

   # Map file extensions to format names
   FILE_TYPES = {
       ".ext": "<Host> Scene Format",
   }

   def get_file_type(extension: str) -> str | None:
       """Return the host application's format identifier for the extension."""
       return FILE_TYPES.get(extension.lower()) if extension else None

   def get_workspace_root() -> str:
       """Return the active workspace root directory from the host, or cwd."""
       # Query host SDK for active project/scene path; fallback to os.getcwd()
       return os.getcwd()

   def open(filepath: str) -> bool:
       """Open an existing scene or project file."""
       if not os.path.exists(filepath):
           logger.error(f"File does not exist: {filepath}")
           return False
       try:
           # Call host SDK to open filepath
           logger.info(f"Successfully opened {filepath}")
           return True
       except Exception as e:
           logger.error(f"Failed to open {filepath}: {e}")
           return False

   def save() -> bool:
       """Save the currently active scene."""
       try:
           # Call host SDK to save
           logger.info("Successfully saved scene.")
           return True
       except Exception as e:
           logger.error(f"Failed to save scene: {e}")
           return False

   def save_as(filepath: str, file_type: str = None) -> bool:
       """Save the active scene to a target path with the given format."""
       try:
           # Call host SDK to save as filepath
           logger.info(f"Successfully saved as {filepath}")
           return True
       except Exception as e:
           logger.error(f"Failed to save as {filepath}: {e}")
           return False

   def import_file(filepath: str) -> bool:
       """Merge or import an asset into the active scene."""
       try:
           # Call host SDK to import/merge
           logger.info(f"Successfully imported {filepath}")
           return True
       except Exception as e:
           logger.error(f"Failed to import {filepath}: {e}")
           return False

   def reference_file(filepath: str) -> bool:
       """Reference an upstream production master into the scene."""
       # If referencing is not supported in this host, return False
       logger.warning("reference_file is not implemented for <host>.")
       return False

   def new_file() -> bool:
       """Reset and initialize a blank scene."""
       try:
           # Call host SDK to clear/reset scene
           logger.info("Created new scene.")
           return True
       except Exception as e:
           logger.error(f"Failed to create new scene: {e}")
           return False

   def export_file(filepath: str, file_type: str = None, selected: bool = False) -> bool:
       """Export the entire scene or active selection to disk."""
       logger.warning("export_file is not implemented for <host>.")
       return False

   def is_modified() -> bool:
       """Query whether the active scene has unsaved modifications."""
       # Query host SDK if available; return False if unable to query
       return False

Step 3: Implement the Host Bootstrapper (`loader.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``openpypeline/app/<host>/loader.py`` to manage initial path configuration, shelf tools, and top-level menu registration:

.. code-block:: python

   """
   File: loader.py
   Description: Setup and launcher entry point for openPypeline Studio in <Host>.
   """

   import os
   import sys
   import logging

   # Ensure openpypeline package root is on sys.path
   _root_path = os.path.abspath(
       os.path.join(os.path.dirname(__file__), "..", "..", "..")
   ).replace("\\", "/")
   if _root_path not in sys.path:
       sys.path.insert(0, _root_path)

   from openpypeline.core.util import prefs

   logger = logging.getLogger("openPypeline.<host>.loader")
   PROJECT_PATH_PREF = "ops_projectFilePath"

   def is_valid_project_file_path(folder: str) -> bool:
       """Validate that the configured project folder exists."""
       return isinstance(folder, str) and os.path.isdir(folder)

   def install_menu():
       """Register openPypeline actions in the host application's menu bar."""
       # Host-specific menu code (e.g. substance_painter.ui.add_action)
       pass

   def openPypelineSetup():
       """Launch the setup dialog to configure project registry paths."""
       project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
       logger.info(f"Configuring openPypeline paths (current: '{project_path}')...")
       # Launch PySide/Qt setup dialog parented to host window
       pass

   def openPypeline():
       """Main entry point to launch openPypeline in this host."""
       project_path = prefs.get_pref(PROJECT_PATH_PREF, "")
       if not is_valid_project_file_path(project_path):
           logger.warning("Project path is not configured. Launching setup...")
           openPypelineSetup()
           return

       from openpypeline.ops_engine import OpsEngine
       engine = OpsEngine()
       engine.ui()

Step 4: Register Host Detection in `ops_engine.py`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add your host's signature module to ``_detect_host_app()`` in ``openpypeline/ops_engine.py``:

.. code-block:: python

   def _detect_host_app(self):
       """Detect which host application is currently running the engine."""
       if "maya" in sys.modules or "maya.cmds" in sys.modules:
           return "maya"
       elif "nuke" in sys.modules:
           return "nuke"
       elif "hou" in sys.modules:
           return "houdini"
       elif "substance_painter" in sys.modules:
           return "substance_painter"
       elif "UnityEngine" in sys.modules or "UnityEditor" in sys.modules:
           return "unity"
       return "standalone"

When running inside that host, ``OpsEngine`` will automatically resolve and load ``openpypeline.app.<host>.file.file``.

Step 5: Write Mock-Based Unit Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add automated test coverage to ``openpypeline/test_host_adapters.py`` using Python's standard ``unittest`` and ``unittest.mock`` libraries. This ensures your adapter is verified in headless CI/CD environments without requiring an interactive license of the software:

.. code-block:: python

   class TestHostFileOperations(unittest.TestCase):
       """Verify that the host file handler functions execute correctly."""

       def setUp(self):
           self.mock_sdk = MagicMock()
           self.patcher = patch.dict("sys.modules", {"<host_sdk>": self.mock_sdk})
           self.patcher.start()

       def tearDown(self):
           self.patcher.stop()

       def test_save_success(self):
           from openpypeline.app.<host>.file import file as host_file
           host_file.<host_sdk> = self.mock_sdk
           result = host_file.save()
           self.assertTrue(result)
           self.mock_sdk.save.assert_called_once()

Case Study: Substance 3D Painter Adapter
----------------------------------------

Adobe Substance 3D Painter is a Python-native application (Archetype 1) with an official Python API under the ``substance_painter`` package:

* **File Format:** ``.spp`` (Substance Painter Project).
* **Open:** ``substance_painter.project.open(filepath)``
* **Save:** ``substance_painter.project.save()``
* **Save As:** ``substance_painter.project.save_as(filepath, substance_painter.project.ProjectExportOptions(...))``
* **Unsaved Changes:** ``substance_painter.project.needs_saving()``
* **Menu Integration:** ``substance_painter.ui.add_action()`` adds openPypeline buttons directly to the Painter top toolbar.

Case Study: ZBrush Adapter
--------------------------

Pixologic / Maxon ZBrush operates as a Script-Bridged application (Archetype 2) using ZScript commands and command-line execution:

* **File Formats:** ``.ztl`` (ZTool) and ``.zpr`` (ZProject).
* **Execution Bridge:** The adapter generates a small ZScript text file on disk containing commands such as:

  .. code-block:: text

     [IPress, Tool:Load Tool]
     [FileNameSetNext, "C:/Projects/hero/hero_wip_v001.ztl"]

* **Execution Trigger:** The adapter invokes ZBrush using Python's ``subprocess.run()`` passing the script path:

  .. code-block:: text

     "C:\Program Files\Pixologic\ZBrush\ZBrush.exe" "C:/Temp/open_tool.zsc"

* **State Tracking:** Because ZBrush does not run in-process Python, openPypeline's advisory concurrency registry (``file_use.py``) tracks artist heartbeats from the launcher or companion UI while ZBrush is active.

Best Practices for Host Adapters
--------------------------------

1. **Never Import Host SDKs Top-Level Unconditionally:** Always wrap imports of proprietary libraries (``maya.cmds``, ``hou``, ``nuke``, ``substance_painter``) in ``try...except ImportError`` blocks so modules can be imported headlessly in tests.
2. **Always Return Booleans for File Operations:** Methods like ``open()``, ``save()``, and ``save_as()`` must return ``True`` on success and ``False`` on failure.
3. **Catch and Log Exceptions:** Never allow unhandled host exceptions to crash the UI. Log detailed errors using standard Python ``logging`` and present user-friendly error notices.
4. **Isolate UI from File Handling:** Keep UI logic (PySide/Qt widgets, dockable controls) in ``app/<host>/ui/`` and scene logic in ``app/<host>/file/``. This enables running batch/headless operations on render farm nodes without loading UI libraries.
5. **Preserve Master Referencing Stability:** Ensure host referencing operations link to the static production Master path (e.g., ``hero_model.ext``) so downstream departments receive updates automatically upon publish.

See Also
--------

* :doc:`architecture`: Complete architectural overview of tiers, data models, and concurrency.
* :doc:`integrations/index`: Current capability matrix and individual host application guides.
* :doc:`production_workflows/index`: Detailed production guidelines for WIPs, Masters, and advisory locking.
