Create the Initial openPypeline Studio Project in Maya
======================================================

Creating a Maya project directory and setting up an openPypeline project are coordinated actions: Maya defines the current workspace, while openPypeline registers and configures that directory with project settings and pipeline folders.

When openPypeline Studio launches, it checks the local project registry. If no projects are registered yet, it automatically prompts you to choose the initial project setup:

* **Create New Project:** Select this to configure your current Maya workspace as a new openPypeline project.
* **Join Existing Project:** Select this if a teammate has already configured the project and you are connecting your local synchronized copy or version control checkout.

.. figure:: /images/choose_initial_project_setup.png
   :alt: openPypeline Studio prompt to create a new project or join an existing one
   :width: 80%
   :align: center

   The openPypeline Studio prompt to create a new project or join an existing one.

To Create a New OPS Project
---------------------------

The first artist in a team (or solo artist) creates the project by configuring the current Maya workspace as an openPypeline project. The project manifest (``.openpypeline/project.json``) and configured pipeline folders are created in that directory.

1. Choose **Create New Project** (or navigate to :menuselection:`Project` > :menuselection:`Project Manager...` > :menuselection:`New...`), the project creation dialog opens:

.. figure:: /images/create_new_project_window.png
   :alt: openPypeline Studio Create New Project dialog showing project settings and folders
   :width: 80%
   :align: center

   The openPypeline Studio Create New Project dialog.

The dialog initially populates the project path from Maya's current workspace:

2. Configure the project settings:

* **Project name and path:** Project names are limited to 22 characters. The dialog converts spaces to underscores and filters unsupported characters. By default, this matches the Maya project name, but you can change it. The project path defaults to Maya's current workspace and cannot be edited directly; use :guilabel:`Override...` only if you intentionally want openPypeline to use a different folder.

The path cannot be edited directly. Use **Override...** only if you intentionally want openPypeline to use a different folder; the confirmation explains that this does not change Maya's workspace or move existing files. The project name is a separate setting. spaces are converted to underscores and unsupported characters are filtered.

.. warning::

   Using :guilabel:`Override...` changes openPypeline's target directory without changing Maya's active workspace. To ensure relative file paths, textures, and references resolve cleanly, it is strongly recommended to keep openPypeline's project root matched to Maya's current workspace directory.

* **Description and status:** Mark the project active to make it available in the main project selector, or inactive to keep it out of that selector.
* **WIP and Master naming and formats:** Set the folder/file naming terms and choose from the formats currently offered by the Maya dialog (such as ``.ma``, ``.mb``, or ``.usd``).
* **Project folders:** Set the asset library, shot scenes, scripts, textures, renders, particles, archive, and deleted-item folders.
* **Optional project details:** Set dates and configure custom users if needed.

3. Click the :guilabel:`Accept` button. openPypeline writes its project manifest and creates the configured pipeline folders under the Maya project directory. This does not change Maya's current project/workspace.

.. warning::

   If you click the Accept button, and the project already exists, you will see the following warning. Click the **OK** button, and either create a new porject, or cancel the new project creation to join one that already exists.

.. figure:: /images/warning_existing_project.png
   :alt: The openPypeline Studio error that indicates a project with the same name and location already exists.
   :width: 40%
   :align: center

   The openPypeline Studio error that indicates a project with the same name and location already exists.

Confirm the project appears in openPypeline's Project Manager and, if marked active, in the main project selector.

OPS saves a project manifest (``.openpypeline/project.json``), creates the configured pipeline folders, and automatically activates the project in the main OPS UI.

4. Wait for cloud synchronization to finish or commit the new files, including ``.openpypeline/project.json``, to cloud storage or SVN.

For a team project, wait for cloud synchronization to finish or commit the new files, including ``.openpypeline/project.json``, to SVN before asking other artists to join. See :doc:`create_join_ops_project_maya` for the steps to add artists to the project.

Next Steps
----------
In the next step, each artist on the team synchronizes or checks out the same project folder and sets Maya's current project to their local copy, then runs the openPypeline Studio setup script and joins the existing project. See :doc:`join_an_existing_ops_project` for the detailed steps, or click the **Next** button below to continue to the next section of this guide.