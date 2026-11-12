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
2. Open the **Script Editor**
3. Open a new Python tab.
4. Copy the following setup python code.
5. Update the path in the code for your operating system and replacing it with your actual install location. The path must point to the directory containing the ``openpypeline`` package.
6. Execute the code (press the return key)
This will add the openPypeline package to your Python path and run the setup function. The setup function will prompt you to define your Script Path and Project Path.

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

Follow the setup prompts to define your Script Path and Project Path.

The shared engine can detect a standalone Python process, but that does not provide a separate standalone user interface. Host-specific workflows require an integration for that application.

Create a project
----------------

After setup, open **Project Manager...** in the main UI and choose **New...**. The project dialog lets you configure:

* **Project name and path:** Project names are limited to 22 characters. The dialog converts spaces to underscores and filters unsupported characters.
* **Description and status:** Mark the project active to make it available in the main project selector, or inactive to keep it out of that selector.
* **WIP and Master naming and formats:** Set the folder/file naming terms and choose from the formats currently offered by the Maya dialog.
* **Project folders:** Set the asset and shot locations, scripts, textures, renders, particles, archive, and deleted-item folders.
* **Optional project details:** Set dates and configure custom users if needed.

Review the project name and folder paths before accepting. Keep project files inside the folder your team uses for cloud sync if you want those files shared. Use **Project Manager...** to review or edit the project configuration later.

.. note::

   Project creation and editing are being completed alongside the shared project-action API. The dialog describes the intended setup flow; verify creation and activation in your Maya installation before relying on it for production.

Custom project icons
--------------------

To customize the image displayed for a project in the main openPypeline Studio UI, place an image named ``openPypelineIcon.png`` in the root folder of that project.
