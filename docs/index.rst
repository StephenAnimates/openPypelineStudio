Welcome to openPypeline Studio
==============================

**openPypeline Studio** is a locally installed framework for managing creative production projects and workflows. Maya is its first supported host. The project is developing toward a shared, host-neutral core with application-specific integrations for additional creative software.

Teams can keep project folders in cloud storage and sync services they already use, such as Google Drive, iCloud Drive, OneDrive, or Dropbox, and work with those folders through their local openPypeline installation.

Project direction and planned work are tracked in the `project roadmap <https://github.com/StephenAnimates/OpenPipeline/blob/master/ROADMAP.md>`_.

Current scope
-------------

The current Maya integration includes project and asset/shot browsing, project directory and naming workflows, WIP and Master file concepts, notes, and application-aware scene operations. Not every feature or integration is complete; the presence of a module does not necessarily mean its host is supported.

For a feature overview, see the `README <https://github.com/StephenAnimates/openPypelineStudio/blob/master/README.md#-features>`_.

The shared core is intended for reusable pipeline concepts and data. Host APIs, scene operations, and host-specific UI belong in application integrations. Maya is the current supported integration; support for other applications should be considered planned until their capabilities and tested versions are documented.

Synced project folders
----------------------

The Maya integration can publish advisory file-use notices in a project folder and warn when a scene appears to be in use or has changed on disk. These notices are **not distributed locks**: sync clients may update files asynchronously, and conflicting edits or overwrites can still occur. Teams should coordinate edits and verify sync status before relying on another artist's changes.

Installation and setup in Maya
------------------------------

The current user interface runs inside Maya. To set it up:

#. Clone or download the repository.
#. Open Maya and its Script Editor, and run the following, replacing the path with the repository directory that contains the ``openpypeline`` package:

   .. code-block:: python

      import sys

      ops_install_path = "/path/to/openPypeline"
      if ops_install_path not in sys.path:
          sys.path.insert(0, ops_install_path)

      from openpypeline.app.maya.core import ops_loader
      ops_loader.openPypelineSetup()

#. Follow the setup prompts to configure the project-file location.
#. After setup, launch the main UI from Maya with:

   .. code-block:: python

      from openpypeline.app.maya.core import ops_loader
      ops_loader.openPypeline()

The shared engine can detect a standalone Python process, but that does not provide a separate standalone user interface. Host-specific workflows require an integration for that application.

Getting started: creating a project
-----------------------------------

After setup, open **Project Manager...** in the main UI and choose **New...**. The project dialog lets you configure:

* **Project name and path:** Project names are limited to 22 characters. The dialog converts spaces to underscores and filters unsupported characters.
* **Description and status:** Mark the project active to make it available in the main project selector, or inactive to keep it out of that selector.
* **WIP and Master naming and formats:** Set the folder/file naming terms and choose from the formats currently offered by the Maya dialog.
* **Project folders:** Set the asset and shot locations, scripts, textures, renders, particles, archive, and deleted-item folders.
* **Optional project details:** Set dates and configure custom users if needed.

Review the project name and folder paths before accepting. Keep project files inside the folder your team uses for cloud sync if you want those files shared. Use **Project Manager...** to review or edit the project configuration later.

Custom Project Icons
--------------------

To customize the image displayed for a project in the main openPypeline Studio UI, place an image named ``openPypelineIcon.png`` in the root folder of that project.

.. note::

   Project creation and editing are being completed alongside the shared project-action API. The dialog currently describes the intended setup flow; verify creation and activation in your Maya installation before relying on it for production.

Core concepts and terminology
-----------------------------

openPypeline organizes production data into a hierarchy:

* **Asset:** A production unit such as a character, prop, or environment.
* **Component:** A piece of an asset, such as modeling, rigging, or shading.
* **Sequence:** A logical collection of shots.
* **Shot:** A unit of a sequence in which assets are animated, lit, or rendered.
* **WIP (Work in Progress):** The working scene an artist iterates on.
* **Master:** A prepared scene intended for review or downstream use.

Pipeline rules and philosophy
-----------------------------

* Use filesystem-safe names. The project dialog converts spaces to underscores and filters unsupported characters in project and folder names.
* Project configuration and preference data use JSON, while production files remain in the formats selected for the project and host application.
* Keep iterative work in numbered WIP files and treat Masters as prepared downstream deliverables. These file conventions organize work; they do not replace backups or a version-control service.

Workflow philosophy: WIPs and Masters
-------------------------------------

Keep day-to-day changes in WIP scenes. When the WIP is stable and ready for production, clean it and save a Master from it. Saving a Master first creates a new, incremented WIP file from the current scene; by default, openPypeline returns to that WIP so later development stays separate from the published Master. Do not open a Master file to make edits. Make changes in the WIP, then save a new Master when that work is ready for production.

Preparing a Master File
-----------------------

Before saving a WIP as a Master, perform the standard Maya scene cleanup: freeze transforms, delete construction history, remove unwanted display layers, and organize the scene hierarchy. The resulting Master is the latest stable, functioning production version of the model, rig, or other asset.

.. note::

   Your team may have additional cleanup requirements; follow the conventions established for your project.

openPypeline does not currently automate these cleanup steps or run a user-defined cleanup script during Master publishing. If **Import References** is selected, the current save action imports loaded references into the scene before saving the Master. Unloaded references prompt the artist to keep or remove each one. This reference handling is separate from the standard cleanup steps above; review the scene and its references before saving the Master.

For animated scenes (shot files), referenced asset models and rig files are generally kept in the scene as references so that the shot can receive updates from the latest asset model or rig Master. Importing a referenced asset model or rig into the shot file removes the live link: later changes to the rig Master will not update the imported rig. Only import a rig when the shot workflow requires it, such as when preparing the scene for rendering.

Contributing and legacy architecture
------------------------------------

The original openPipeline framework used global MEL procedures. For contributors migrating legacy scripts or tracing behavior into the current Python package, see :doc:`architecture_migration` for a historical source-to-module map and guidance on the current package boundaries.

API reference
-------------

The API reference is generated from the Python package during the documentation build.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   about
   architecture_migration
   modules

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
