Foundry Nuke Integration
========================

Foundry Nuke is supported through openPypeline Studio's host adapter layer. It enables compositors and visual effects artists to organize Nuke scripts, track script iterations, and import shared node setups within project hierarchies.

Support Status & Requirements
-----------------------------

* **Status:** In Development (Core Script Operations Implemented)
* **Target Versions:** Foundry Nuke 14.0, 15.0+
* **Python Runtime:** Python 3.9+, Python 3.10+ (Nuke standard internal CPython)
* **Module Path:** ``openpypeline/app/nuke/``

Setup & Menu Registration
-------------------------

To integrate openPypeline Studio into Nuke, add the initialization call to your personal ``menu.py`` file (located in ``~/.nuke/menu.py`` on macOS/Linux or ``%USERPROFILE%/.nuke/menu.py`` on Windows):

.. code-block:: python

   import sys
   # Add openPypeline to the Python search path if not already in PYTHONPATH
   ops_path = "/path/to/openPypeline"
   if ops_path not in sys.path:
       sys.path.append(ops_path)

   # Register the openPypeline menu items
   from openpypeline.app.nuke import loader
   loader.install_menu(menu_name="openPypeline")

When Nuke launches, an **openPypeline** menu appears on Nuke's top menu bar with commands to launch the studio browser and configure setup paths.

Launching Manually
~~~~~~~~~~~~~~~~~~

To launch openPypeline directly from Nuke's internal Script Editor:

.. code-block:: python

   from openpypeline.app.nuke import loader
   loader.openPypeline()

Supported File Formats
----------------------

* **Nuke Script:** ``.nk`` (ASCII node graph script).

Implemented Capabilities
------------------------

The Nuke adapter implements the following standard operations:

* **Script Opening:** ``open(filepath)`` loads existing ``.nk`` scripts via ``nuke.scriptOpen()``.
* **Script Saving:** ``save()`` writes changes to the active script via ``nuke.scriptSave()``.
* **WIP Versioning:** ``save_as(filepath)`` saves incremented WIP scripts (e.g., ``sh010_comp_wip_v0002.nk``) into the item's ``wip/`` directory.
* **Node Import / Merging:** ``import_file(filepath)`` pastes saved node graphs or external script segments into the active workspace via ``nuke.nodePaste()``.
* **Script Clearing:** ``new_file()`` resets the node graph via ``nuke.scriptClear()``.
* **Unsaved Changes Tracking:** ``is_modified()`` queries ``nuke.root().modified()`` to prevent accidental data loss.

Planned Features (Roadmap)
--------------------------

According to the project roadmap, the following features are planned for future Nuke updates:

1. **Dockable Nuke Panel (UI):** A dockable PySide widget integrated into Nuke's pane layout tabs for rapid shot and script switching.
2. **LiveGroup & Precomp Referencing:** Native management and referencing of shared Nuke LiveGroups and precomposed background plates.
3. **Write Node Path Token Integration:** Automatic path injection into Nuke Write nodes targeting the project's configured ``images/renders/`` folder.
