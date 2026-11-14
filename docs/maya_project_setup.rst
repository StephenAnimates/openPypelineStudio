Set Up a Maya Project for openPypeline Studio
=============================================

This guide explains how to set Maya's project/workspace directory and register that directory with openPypeline Studio.

Maya and openPypeline use the same project directory, but their setup steps are separate:

* **Maya project/workspace:** The directory Maya treats as the current project.
* **openPypeline project:** The project settings and pipeline folders openPypeline creates under the Maya project directory. Its project settings are stored in ``.openpypeline/project.json``.

The openPypeline script installation and the local ``openpypeline_projects.json`` registry are separate from the Maya project directory. Keep those local to each artist's computer; share or synchronize the Maya project directory instead.

Choose the Maya project directory
---------------------------------

Decide where the project directory should live before setting up either application:

* **Cloud storage:** Use a project-specific folder under the team's synchronized directory, such as ``Projects/CreatureFeature``. The team should synchronize this folder to each artist's computer.
* **SVN:** Use the repository checkout root if the repository is dedicated to this Maya project. If the repository contains multiple projects, use this project's subfolder. Each artist should check out or update the same repository folder; the local checkout paths may differ.

Set or create the Maya project
------------------------------

Existing Maya project directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. In Maya, choose **File** > **Set Project**.
2. Select the existing project directory and confirm.
3. Check that Maya's current project/workspace points to the intended directory.

New Maya project directory
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. In Maya, choose **File** > **Project Window**.
2. Click :guilabel:`New`.
3. Enter a project name and choose the location for the new project directory. Use the shared cloud-synchronized location or the appropriate folder in the SVN working copy.
4. Confirm the new project in Maya's :guilabel:`Project Window` and check that Maya's current project/workspace points to the new directory.

Create the openPypeline project
-------------------------------

After Maya is using the intended project directory:

1. Open openPypeline Studio's **Project Manager...** and choose **New...**.
2. The project path is initially populated from Maya's current workspace. Confirm that it is the same directory you selected or created in Maya. The path cannot be edited directly. Use **Override...** only if you intentionally want openPypeline to use a different folder; the confirmation explains that this does not change Maya's workspace or move existing files. The project name is a separate setting.
3. Configure the project name, status, WIP and Master naming, and folder locations. Project names are limited to 22 characters; spaces are converted to underscores and unsupported characters are filtered.
4. Accept the dialog. openPypeline writes its project manifest and creates the configured pipeline folders under the Maya project directory. This does not change Maya's current project/workspace.
5. Confirm the project appears in openPypeline's Project Manager and, if marked active, in the main project selector.

For a team project, wait for cloud synchronization to finish or commit the new files, including ``.openpypeline/project.json``, to SVN before asking other artists to join. See :doc:`getting_started` for the multi-artist join steps.
