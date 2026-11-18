SideFX Houdini Integration
==========================

SideFX Houdini is supported through openPypeline Studio's host adapter layer. It enables procedural artists, FX TDs, and technical directors to manage Houdini scene files, increment WIP versions, and merge production assets within the openPypeline hierarchy.

Support Status & Requirements
-----------------------------

* **Status:** In Development (Core File Operations Implemented)
* **Target Versions:** SideFX Houdini 20.0, 20.5+
* **Python Runtime:** Python 3.10+ (Houdini standard internal CPython)
* **Module Path:** ``openpypeline/app/houdini/``

Setup & Shelf Installation
--------------------------

To use openPypeline Studio in Houdini, ensure the ``openPypeline`` package directory is added to your ``sys.path`` or ``PYTHONPATH`` (for example, in your ``houdini.env`` file).

Installing the Shelf Tool
~~~~~~~~~~~~~~~~~~~~~~~~~

You can automatically generate an openPypeline shelf tool by running the following snippet in Houdini's **Python Source Editor** (:menuselection:`Windows` > :menuselection:`Python Source Editor`) or the interactive Python Shell:

.. code-block:: python

   import sys
   # Replace with the path containing the openpypeline package
   sys.path.append("/path/to/openPypeline")

   from openpypeline.app.houdini import loader
   loader.install_shelf(shelf_name="openPypeline")

This creates an **openPypeline** shelf tab containing a launch button.

Launching Manually
~~~~~~~~~~~~~~~~~~

To launch openPypeline manually from any Python session in Houdini:

.. code-block:: python

   from openpypeline.app.houdini import loader
   loader.openPypeline()

If your project path has not been configured yet, Houdini will prompt you with the openPypeline Studio Setup dialog to select your local project registry.

Supported File Formats
----------------------

Houdini's file handler natively recognizes all standard Houdini scene extensions:

.. list-table:: Houdini Supported Formats
   :widths: 25 35 40
   :header-rows: 1

   * - Extension
     - Format Name
     - Description
   * - ``.hip``
     - Houdini Scene
     - Standard commercial scene format.
   * - ``.hiplc``
     - Houdini Limited Commercial
     - Houdini Indie license scene format.
   * - ``.hipnc``
     - Houdini Non-Commercial
     - Houdini Apprentice license format.

Implemented Capabilities
------------------------

The Houdini adapter currently implements the following operations:

* **Scene Opening:** ``open(filepath)`` loads existing ``.hip``, ``.hiplc``, or ``.hipnc`` files via ``hou.hipFile.load()``.
* **Scene Saving:** ``save()`` writes current scene changes via ``hou.hipFile.save()``.
* **WIP Versioning:** ``save_as(filepath)`` saves incremented WIP scene files into the item's ``wip/`` directory.
* **Scene Merging:** ``import_file(filepath)`` merges another scene's nodes into the current network via ``hou.hipFile.merge()``.
* **Scene Clearing:** ``new_file()`` resets the Houdini session via ``hou.hipFile.clear()``.
* **Unsaved Changes Tracking:** ``is_modified()`` queries ``hou.hipFile.hasUnsavedChanges()`` to prevent accidental data loss.

Planned Features (Roadmap)
--------------------------

According to the project roadmap, the following features are planned for future Houdini updates:

1. **Houdini Python Panel (UI):** A dockable PySide panel embedding the openPypeline Asset and Shot browser directly inside Houdini's workspace pane tabs.
2. **Houdini Digital Asset (HDA) Management:** Native versioning, referencing, and installation of ``.hda`` and ``.otl`` asset definitions.
3. **Solaris & USD Publishing:** Automatic publishing of USD sublayers and payload stages directly into openPypeline project trees.
