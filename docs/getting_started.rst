Maya Setup and Getting Started
==============================

This guide covers installing the current Maya integration and creating a first project. For tested Maya and Python versions, see the requirements in the `README <https://github.com/StephenAnimates/OpenPipeline/blob/master/README.md#-requirements>`_.

Install and set up Maya
-----------------------

Download ``openPypelineStudio.zip`` from the `GitHub nightly releases <https://github.com/StephenAnimates/OpenPipeline/releases>`_ and extract it into your Maya scripts directory. The archive creates an ``openPypelineStudio`` folder. If you decide to clone the repository instead, name the checkout folder ``openPypelineStudio``.

Typical scripts locations are:

* **macOS:** ``~/maya/scripts/`` or ``/Users/Shared/Autodesk/maya/scripts``
* **Windows:** ``%USERPROFILE%\maya\scripts\`` or ``C:\Users\YourName\maya\scripts``

1. Open Maya
2. Open the **Script Editor** (:menuselection:`Windows` > :menuselection:`General Editors` > :menuselection:`Script Editor`).
3. Open a new Python tab (:menuselection:`Tabs` > :menuselection:`New Tab` then choose **Python** from the :guilabel:`Source Type` window)
4. Copy the setup python code.

.. code-block:: python

   import sys

   # macOS example
   ops_install_path = "/Users/Shared/Autodesk/maya/scripts/openPypelineStudio"

   # Windows example
   # ops_install_path = r"C:\Users\YourName\maya\scripts\openPypelineStudio"

   if ops_install_path not in sys.path:
       sys.path.insert(0, ops_install_path)

   from openpypeline.app.maya.core import ops_loader
   ops_loader.openPypelineSetup()

5. Change the path in the code for your operating system and replace it with your actual install location. The path must point to the directory containing the downloaded ``openpypeline`` package.
6. Execute the code (:menuselection:`Command` > :menuselection:`Execute` or press :kbd:`Ctrl+Enter` on Windows or :kbd:`Cmd+Enter` on macOS).

This will add the openPypeline package to your Python path and run the setup function. The setup function will prompt you to define your **Script Path** and **Project Path**.

1. If this is an initial project setup, in the :guilabel:`openPypeline Studio Setup` window, either choose the default **Script Path** and **Project Path** or click the :guilabel:`Browse` button to select your own. The default paths are:

   * **Script Path:** ``~/maya/scripts/openPypelineStudio`` (macOS) or ``%USERPROFILE%\maya\scripts\openPypelineStudio`` (Windows)
   * **Project Path:** ``~/maya/projects/openPypeline`` (macOS) or ``%USERPROFILE%\maya\projects\openPypeline`` (Windows)

2. Click the :guilabel:`Accept` button to save the paths and complete the setup.

The setup function will create the default project folder structure if it does not already exist.

Follow the setup prompts to define your **Script Path** and **Project Path**.

The shared engine can detect a standalone Python process, but that does not provide a separate standalone user interface. Host-specific workflows require an integration for that application.

Create a Maya/openPypeline Studio project
-----------------------------------------

The Maya project directory is the folder Maya uses as its current project/workspace. OpenPypeline Studio uses that same folder as its project root and adds its settings, manifest, and configured pipeline folders there. These are separate actions. Maya's :guilabel:`Project Window` creates or selects the Maya project directory; openPypeline's :menuselection:`Project Manager...` > :menuselection:`New...` registers and configures that directory for the openPypeline project. The openPypeline action does not change Maya's current workspace.

1. Create a new Maya project or set an existing one as the current workspace. The Maya project directory can be anywhere on your computer, but for a shared project, it should be in a cloud-synchronized folder or a working copy managed by `Apache Subversion (SVN) <https://subversion.apache.org/>`_, a centralized version-control system.

* If a Maya project directory already exists:
   In Maya's main User Interface (UI), choose :menuselection:`File` > :menuselection:`Set Project` and select the existing Maya project directory. This will be the directory with the workspace.mel file and the project folders, such as ``scenes``, ``sourceimages``, and ``images``). Confirm that Maya's current project/workspace points to the intended directory.
* If a Maya project directory does not exist yet:
   In Maya's main User Interface (UI), choose :menuselection:`File` > :menuselection:`Project Window`, click the :guilabel:`New` button, name the new project, and set its location.

For detailed step-by-step instructions, see :doc:`maya_project_setup`.

Once Maya is using a project directory, in the **openPypeline UI**, go to :menuselection:`Project` > :menuselection:`Project Manager...` and choose :menuselection:`New...`. The dialog initially uses Maya's current workspace as the openPypeline project path. Confirm it points to the same Maya project directory.

The openPypeline project dialog lets you configure:

* **Project name and path:** Project names are limited to 22 characters. The dialog converts spaces to underscores and filters unsupported characters. By default this will use the same name as the Maya project, but you can change it. The project path is initially set to Maya's current workspace and cannot be edited directly. Use :guilabel:`Override...` only if you intentionally want openPypeline to use a different folder; the confirmation explains that this does not change Maya's workspace or move existing files.
* **Description and status:** Mark the project active to make it available in the main project selector, or inactive to keep it out of that selector.
* **WIP and Master naming and formats:** Set the folder/file naming terms and choose from the formats currently offered by the Maya dialog.
* **Project folders:** Set the asset and shot locations, scripts, textures, renders, particles, archive, and deleted-item folders.
* **Optional project details:** Set dates and configure custom users if needed.

Review the project name and folder paths before accepting. Keep project files inside the folder your team uses for cloud sync if you want those files shared. Use **Project Manager...** to review or edit the project configuration later.

Share a project with other artists
-----------------------------------

Each artist should install openPypeline Studio and configure its script and project-registry locations on their own computer. Do not share or synchronize the Maya scripts installation or the local ``openpypeline_projects.json`` file registry.

For a shared project, keep the Maya project folder in the team's synchronized cloud-drive location or in SVN. With SVN, use the checkout root if the repository is dedicated to this project; otherwise, use the same project subfolder from the repository on every artist's computer.

1. The first artist sets or creates the Maya project in that shared location, then uses :menuselection:`Project Manager...` > :menuselection:`New...` to configure it for openPypeline. See :doc:`maya_project_setup` for the detailed steps.
2. Wait for cloud synchronization to finish or commit the new files, including ``.openpypeline/project.json``, to SVN.
3. Each other artist synchronizes or checks out the same project folder, sets Maya's current project to their local copy, and chooses :menuselection:`Project Manager...` > :menuselection:`Join Existing...`. Select the local folder containing ``.openpypeline/project.json``.
4. Joining adds the project to that artist's local registry without recreating or overwriting shared project folders. Active projects appear in the main project selector; inactive projects remain registered but are not selectable.

The shared manifest stores project settings, not an absolute machine-specific path, so each artist's local registry can point to their own synchronized folder or SVN working copy.

Custom project icons
--------------------

To customize the image displayed for a project in the main openPypeline Studio UI, place an image named ``openPypelineIcon.png`` in the root folder of that project.
