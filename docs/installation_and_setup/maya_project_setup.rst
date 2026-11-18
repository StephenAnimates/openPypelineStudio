Set Up a Maya Project for openPypeline Studio
=============================================

This guide explains how to set Maya's project/workspace directory and prepare it for use with openPypeline Studio.

Setting Up a Maya Project Directory
-------------------------------------------------------
Maya needs to have a project directory set to use openPypeline Studio (OPS). OPS will only use the Maya project directory to store a configuration file, but the pipeline folders for a project is created by OPS in a seperate folder than the Maya Project directory. The Maya project directory can be anywhere on your computer, but for a shared project, it should be in a cloud-synchronized folder or a working copy managed by `Apache Subversion (SVN) <https://subversion.apache.org/>`_, a centralized version-control system.

* **Maya project/workspace:** The directory Maya treats as the current project.
* **openPypeline project:** The project settings and pipeline folders openPypeline creates under the Maya project directory. Its project settings are stored in ``.openpypeline/project.json``.

The openPypeline script installation and the local ``openpypeline_projects.json`` registry are separate from the Maya project directory. Keep those local to each artist's computer; share or synchronize the Maya project directory itself, and not the openPypeline project directory.

If you are already familiar with Maya project directories, you can skip to the next section. Otherwise, read on for a brief overview of setting up and managing Maya project directories.

To Set Up a New or Select an Existing Project Directory
-------------------------------------------------------

After the openPypeline Studio script folder is in the proper Maya script location, open Maya. Then create a new Maya project or set an existing one as the current workspace. 

.. attention::

   The Maya project directory is the folder Maya uses as its current project/workspace. OpenPypeline Studio uses that same folder as its project root and adds its settings, manifest, and configured pipeline folders there.

* If a Maya project directory does not exist yet:
   1. In Maya's main User Interface (UI), choose :menuselection:`File` > :menuselection:`Project Window`.
   2. Click the :guilabel:`New` button.
   3. Enter a name for the new project, and set its location.
   4. Click the :guilabel:`Accept` button to create the new Maya project directory. This will also create a ``workspace.mel`` file and the project folders, such as ``scenes``, ``sourceimages``, and ``images``.

.. figure:: /images/maya_project_window.png
   :alt: Maya's New Project window
   :width: 80%
   :align: center

   The Maya New Project window.

The Maya project directory can be anywhere on your computer, but for a shared team project, it needs to be in a cloud-synchronized folder or a working copy managed by `Apache Subversion (SVN) <https://subversion.apache.org/>`_, a centralized version-control system.

* If a Maya project directory already exists:
   1. In Maya's main User Interface (UI), choose :menuselection:`File` > :menuselection:`Set Project` and select the existing Maya project directory. This will be the directory with the ``workspace.mel`` file and the project folders, such as ``scenes``, ``sourceimages``, and ``images``).
   2. Confirm that Maya's current project/workspace points to the intended directory.


Choose the Maya project directory
---------------------------------

Decide where the project directory should live before setting up either application:

* **Cloud storage:** Use a project-specific folder under the team's synchronized directory, such as ``Projects/<MayaProjectName>``. Each team member will synchronize this folder to their own personal computer.
* **SVN:** Use the repository checkout root if the repository is dedicated to this Maya project. If the repository contains multiple projects, use this project's subfolder. Each artist should check out or update the same repository folder; the local checkout paths may differ.




Next Steps
----------
In the next step, we will run the openPypeline Studio setup script to configure the Maya environment for the project. See :doc:`run_OPS_setup_script` for the detailed steps, or click the **Next** button below to continue to the next section of this guide.