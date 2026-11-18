Joining an Existing Project
===========================

When working on a collaborative team project, only the first artist creates and initializes the project. Once the initial project folder and its manifest (``.openpypeline/project.json``) are committed to version control or synchronized across cloud storage, all other team members simply **join** the existing project.

Each artist must install openPypeline Studio and configure their own local script and project-registry paths on their personal computer. 

.. important::

   **Do not synchronize your local registry:** Never share, commit, or cloud-sync your local ``openpypeline_projects.json`` file or your local Maya scripts directory. Only share the actual production project folder containing the ``.openpypeline/project.json`` manifest.

Step-by-Step: How to Join
-------------------------

1. **Synchronize or Check Out the Project:**
   Ensure the shared project folder is fully synchronized to your local computer via your team's cloud storage (Google Drive, Dropbox, OneDrive) or checked out from Perforce / SVN.

2. **Set Your Host Workspace:**
   Open Maya (or your host DCC) and set its active project directory to your local synchronized copy (:menuselection:`File` > :menuselection:`Set Project`).

3. **Launch openPypeline Studio:**
   Run the openPypeline launcher script. If no projects are registered in your local registry yet, openPypeline automatically displays the welcome prompt:

   .. figure:: /images/choose_initial_project_setup.png
      :alt: openPypeline Studio prompt to create a new project or join an existing one
      :width: 80%
      :align: center

      The initial project setup prompt.

4. **Select Join Existing Project:**
   In the prompt (or via :menuselection:`Project` > :menuselection:`Project Manager...` > :menuselection:`Join Existing...`), click **Join Existing Project**.

5. **Browse to the Project Folder:**
   Select the local folder containing ``.openpypeline/project.json``.

6. **Activation:**
   openPypeline records the project path in your local machine registry and activates it in the main UI without recreating or overwriting existing project files.

Why Joining Works Across Different OSes
---------------------------------------

The shared manifest (``.openpypeline/project.json``) stores only project-relative settings (such as folder names and WIP/Master conventions), not machine-specific absolute file paths. 

This architecture allows each artist's local registry to point to their own local path—even if team members work across different operating systems (for example, ``/Users/Shared/Projects/Film/`` on macOS vs. ``D:\Projects\Film\`` on Windows).

.. note::

   **Advisory File Locks:** When collaborating across shared cloud storage, openPypeline's file-use notices are **advisory**, warning you when a teammate has a scene open. Cloud sync services update files asynchronously and cannot guarantee real-time distributed file locks. Always confirm sync status before modifying shared files.

Next Steps
----------

Now that you have joined the project, you are ready to begin production work. Proceed to :doc:`start_using_ops` to learn daily launch shortcuts and shelf integration.
