Project and User Configuration
==============================

openPypeline Studio has two kinds of configuration: user preferences that apply to the local installation, and project settings that describe a production project. The Maya setup and settings dialogs expose these values; the shared project configuration model is defined by ``ProjectConfig`` in ``openpypeline/core/models.py``.

Configuration files
-------------------

The preference module stores local user preferences in ``~/.openpypeline/user_prefs.json``. These include the configured project-registry location, current project and browser selection, WIP and Master naming, date/time display formats, and production-tracker connection settings. Do not share or commit this file: tracker credentials may be stored there.

The configured project-registry location contains ``openpypeline_projects.json``, which the project module reads as a list of project records, and ``openpypeline_users.json``, which stores the global list of user names used by the project dialog. These files are distinct from each project's production folder. The registry location is selected during Maya setup.

Project settings
----------------

The project dialog and ``ProjectConfig`` model cover the following settings:

* **Identity and status:** project name, root path, description, active/inactive status, creation date, and deadline. Project names are limited to 22 characters in the dialog.
* **WIP and Master naming:** WIP folder/name and Master name, with a selected file format. The model defaults to ``wip`` and ``master`` and ``ma``; available dialog formats are ``ma``, ``mb``, ``usd``, ``usda``, ``abc``, and ``fbx``.
* **Project folders:** asset library, shot scenes, scripts, textures, renders, particles, archive, and deleted-item locations. The model defaults include ``scenes/assets`` for the asset library, ``scenes`` for shots, ``scripts``, ``sourceimages``, ``images/renders``, ``particles``, ``archive``, and ``deleted``.
* **Users:** an optional per-project user list selected from the global user list.

Folder values are project-relative locations in the dialog's normal workflow. The dialog changes spaces to underscores, removes characters outside letters, numbers, underscores, and slashes, and converts backslashes to forward slashes. Review the resolved paths and naming terms before using a project in production.

The project-configuration UI and shared project-action API are still being completed. Treat the settings described here as the current model and dialog contract, not a guarantee that every create, edit, or activation path is fully implemented in every installation.

Production folder and file layout
---------------------------------

Shared path resolution uses the selected project paths together with the browser selection. The general structure is:

.. code-block:: text

   <project root>/
     <asset library>/<asset type>/<asset>/
       <wip name>/
         <asset>_<wip name>_<number>.<WIP format>
       <asset>_asset.<Master format>
       components/<component>/
         <wip name>/
           <asset>_<component>_<wip name>_<number>.<WIP format>
         <asset>_<component>.<Master format>
     <shot scenes>/<sequence>/<shot>/
       <wip name>/
         <shot>_<wip name>_<number>.<WIP format>
       <shot>_shot.<Master format>
       components/<component>/
         <wip name>/

WIP files are placed in a subfolder named for the WIP term (``wip`` by default), with a four-digit incrementing suffix. Asset or shot Masters are named at the item root. Component file names include the parent asset or shot name. Actual extensions and paths depend on the selected project settings and browser context.

The project model also includes archive and deleted-item folder locations. Their presence in the model does not mean every action involving those locations has identical behavior across hosts.

Maya user preferences
---------------------

The Maya **Settings** dialog exposes date and time display formats, default WIP and Master names, a default scene format, and production-tracker settings. The tracker credentials are local user preferences, not project-shared configuration. The current tracker selector offers ``none`` and ShotGrid; connection and publishing features depend on the tracker integration being configured and available.

For general installation and project setup steps, see :doc:`index`. For the relationship between shared code and host integrations, see :doc:`architecture`.
