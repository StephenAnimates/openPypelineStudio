Welcome to openPypeline Studio's documentation!
===============================================

openPypeline Studio is an open-source framework for managing animation production data and workflows. 

Originally developed as a MEL-based plug-in by Kickstand, **openPypeline Studio** has been completely modernized and refactored into **Python 3** to natively support modern Autodesk Maya environments (Maya 2026+) and acts as a foundation for a DCC-agnostic pipeline. It handles specific, critical aspects of production: automatic directory structures, file naming conventions, revision control, and modularity that makes multi-artist workflows seamless.

Key Features
------------

* **Automated Directory Structures:** Ensures all project files are strictly organized and standardized across your team.
* **Strict Naming Conventions:** Eliminates messy file names; the framework handles naming and versioning automatically.
* **Revision Control:** Built-in system for managing Work-in-Progress (formerly Workshop) and Master (approved) files.
* **Asset & Shot Browsers:** Dedicated UI tabs for managing Assets, Sequences, Shots, and their respective components.
* **Playblast & Notes Management:** Integrated tools for taking snapshots, recording playblasts, and leaving notes for artists.
* **Modern Python API:** Extensible and fully accessible via Python 3.

Installation & Setup
--------------------

1. Clone or download this repository.
2. Copy or move the folder to your Maya user scripts directory (e.g., ``/Users/Shared/Autodesk/maya/scripts``) or a common network scripts directory.
3. Open **Autodesk Maya**.
4. Open the **Script Editor** (Python tab).
a. You can locate the Maya user scripts directory by opening Maya and running the following code in the Script Editor:
``python
import maya.cmds as cmds
print(cmds.internalVar(userScriptDir=True))
```
b. In the **Script Editor Output**, you will see the path to your user scripts directory. Place the openPypeline Studio folder in that directory. For example: `~/Library/Preferences/Autodesk/maya/2026/scripts/`
5. Run the following code to initialize the setup UI, replacing the path with your actual installation directory:

.. code-block:: python

   import sys

   # Path to the directory containing the 'openpypeline' folder
   repo_path = "/Users/Shared/Autodesk/maya/scripts/openPypeline"

   if repo_path not in sys.path:
       sys.path.insert(0, repo_path)
       
   import opsLoader
   opsLoader.openPypelineSetup()

5. Follow the on-screen prompts to define your **Project Path** and **Project Path**.

Getting Started: Creating Your First Project
--------------------------------------------

Once openPypeline Studio is installed, you need to create a Project to begin working. 

1. Launch the UI and click the **Project Manager...** button.
2. Click **New...** to open the Create New Project dialog.
3. Configure your project parameters:

   * **Project Name & Path:** The name (limited to 22 characters, no spaces) and the root directory where all assets and shots will be stored.
   * **Status:** Selecting "active" makes the project available in the main openPypeline dropdown. "Inactive" hides it from the main UI but keeps it in the Project Manager.
   * **Files (Master / WIP):** Define your preferred nomenclature (e.g., `master`, `publish`, `wip`, `workshop`) and default export formats (`.ma`, `.mb`, `.usd`, `.abc`). *Note: To ensure path stability, these cannot be edited after the project is created.*
   * **Sub-Folder Names:** Customize the internal directory structure (Asset Library, Shot Library, Textures, etc.). Like the file formats, these lock upon creation.
   * **Archived & Deleted Locations:** Designate where old versions and deleted items are moved to keep your active directories clean.

4. Click **Accept** to generate the project directories and the XML database file.

.. tip::
   **Custom Project Icons**
   
   You can customize the image displayed in the main openPypeline Studio UI for your specific project! 
   Simply place an image file named ``openPypelineIcon.png`` in the root folder of your project.

Core Concepts & Terminology
---------------------------

openPypeline Studio adheres to the original structural design of openPipeline, organizing production data into a strict hierarchy:

* **Asset:** A unit of production such as a character, prop, or environment, which can be made up of components.
* **Component:** The individual pieces required to build an asset. For example, a character asset may have *model*, *rig*, and *shading* components.
* **Sequence:** A logical collection of shots.
* **Shot:** A composed collection of assets that are animated, lit, and rendered.
* **WIP File (formerly Workshop):** The insulated environment where daily, iterative artist work occurs.
* **Master File:** The finalized, published asset. Stripped of dependencies, clean, and ready to be referenced by other downstream files.

Pipeline Rules & Philosophy
---------------------------

Since its original specification in 2007, the framework has been guided by three core technical rules to ensure cross-platform compatibility and stability:

1. **No spaces in any names.** Strict naming conventions prevent path resolution issues across different operating systems and render farms.
2. **Descriptive information is stored in generic XML files.** Ensuring production metadata is easily readable and parsable outside of any specific DCC application.
3. **Incremental saves are the default form of revision control.** Separating insulated artist work (WIP files) from published, flattened, and cleaned upstream files (Master files).

Workflow Philosophy: WIPs vs. Masters
-------------------------------------

The pipeline distinguishes strictly between working files and published files to protect production data:

* **Never hand-edit a Master file.**
* Artists do all iterative work in **WIP (Work-in-Progress)** files.
* When an asset is ready, the artist saves a **Master**. The framework procedurally cleans the file (flattening references, removing display layers) and publishes it for use downstream.
* Saving a Master automatically generates a new, incremented WIP file so the artist can safely continue working without touching the newly published Master.

Custom Master Scripts
---------------------

At the moment of mastering, you often need to execute cleanup routines—like freezing transforms, deleting construction history, or reorganizing hierarchies. openPypeline Studio provides a **Custom Command** field when saving a Master. 

This executes a custom Python or MEL command specifically on the Master file being published. Because this happens in an isolated step, it is entirely non-destructive: your modeling history and transforms remain fully intact in your WIP file, but the downstream Master file is kept perfectly clean.

Architecture & API Mapping
--------------------------

The original 2007 openPipeline relied on a vast library of global MEL procedures (e.g., ``openPipelineFile.mel``, ``openPipelineUI.mel``). **openPypeline Studio** has fully deprecated MEL in favor of a modular, object-oriented Python 3 API and PySide6 interfaces.

If you are migrating legacy scripts, here is how the old MEL architecture maps to the new Python backend:

* **openPipelineFile.mel & openPipeline.mel** ➡️ :doc:`opsActions` (Core file operations, importing, referencing, and project creation).
* **openPipelineUtility.mel** ➡️ :doc:`opsInfo` and :doc:`opsUtils` (Information retrieval, path resolution, padding, and data parsing).
* **openPipelineUI.mel** ➡️ :doc:`opsUIWrappers`, :doc:`opsMainUI`, and the ``ui/`` package (PySide6 interfaces and Qt signal wrappers).
* **openPipelineProject.mel** ➡️ :doc:`opsProject` (Project data parsing and global user management).
* **openPipelineSceneInv.mel** ➡️ :doc:`opsSceneInv` (Now utilizing high-performance Qt ``QTreeWidget`` components).
* **openPipelineNotes.mel** ➡️ :doc:`opsActions` and the ``core/notes/`` module.
* **openPipelineInit.mel** ➡️ :doc:`openpypeline.core.util.prefs` (Replaces Maya ``optionVars`` with a DCC-agnostic JSON preferences system).

Detailed API documentation for the new modules is automatically generated from the Python source code below.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`