Autodesk Maya Integration
=========================
Autodesk Maya is openPypeline Studio's reference host integration, featuring 100% full pipeline and user-interface capabilities. 

All core pipeline operations—including project management, asset and shot hierarchy browsing, WIP increments, Master publishing, scene referencing, and advisory concurrency warnings—are natively integrated into Maya's Python runtime.

Support Status & Requirements
-----------------------------

* **Status:** Supported (Production Reference Implementation)
* **Tested Versions:** Autodesk Maya 2024, 2025, 2026+
* **Python Runtime:** Python 3.9+ (Maya standard internal CPython)
* **UI Framework:** PySide6 / Qt

Quick Launch & Shelf Setup
--------------------------
After downloading openPypeline Studio into your Maya scripts folder and completing the initial setup dialog (see :doc:`/installation_and_setup/index`), you can launch openPypeline at any time using:

.. code-block:: python

   from openpypeline.app.maya import loader
   loader.openPypeline()

.. tip::

   **Create a Maya Shelf Button:** Open Maya's Script Editor (:menuselection:`Windows` > :menuselection:`General Editors` > :menuselection:`Script Editor`), paste the snippet above into a Python tab, highlight it, and drag it with the :kbd:`MMB` (Middle Mouse Button) to your active Maya shelf tab.

Workspace Synchronization
-------------------------
OpenPypeline coordinates with Maya's native workspace system:

* **Maya Workspace:** Defined by ``workspace.mel`` and standard Maya directories (``scenes``, ``sourceimages``, ``images``).
* **openPypeline Project Root:** Contains the ``.openpypeline/project.json`` manifest and configures pipeline folder aliases.

.. important::

   Always ensure that Maya's current workspace (:menuselection:`File` > :menuselection:`Set Project`) matches openPypeline's active project root. Keeping them identical ensures that textures, scene references, and cache paths resolve reliably using relative paths.

Supported File Formats & Plugins
--------------------------------

openPypeline's Maya file handler automatically loads required Maya plugins when opening or exporting scenes:

* **Maya Native:** ``.ma`` (Maya ASCII) and ``.mb`` (Maya Binary).
* **Universal Scene Description (USD):** ``.usd``, ``.usda``, ``.usdc`` (automatically verifies and loads ``mayaUsdPlugin``).
* **Alembic Caches:** ``.abc`` (automatically verifies and loads ``AbcImport`` and ``AbcExport``).

Key Maya Features
-----------------

Asset & Shot Browser
~~~~~~~~~~~~~~~~~~~~
Browse your production hierarchy directly inside Maya:
* **Assets (Tab 2):** ``Type`` (e.g., characters, props) $\rightarrow$ ``Asset`` $\rightarrow$ ``Component`` (e.g., model, rig, surface).
* **Shots (Tab 3):** ``Sequence`` $\rightarrow$ ``Shot`` $\rightarrow$ ``Process`` (e.g., layout, anim, light, fx).

WIP Iteration
~~~~~~~~~~~~~
Clicking **Save WIP** creates an incremented version file (e.g., ``hero_wip_v0004.ma``) in the item's ``wip/`` subdirectory, updates advisory file-use notices, and logs artist comments to the component's note history.

Master Publishing & Referencing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When an asset or shot milestone is approved:
1. Promoting a WIP to Master creates or overwrites the clean static Master file (e.g., ``hero_model.ma``).
2. Any previously existing Master is safely moved to an archive directory with a timestamp.
3. Downstream artists (e.g., Riggers or Animators) reference the static Master file using Maya's native file referencing (:menuselection:`File` > :menuselection:`Create Reference`). When a new Master is published, downstream scenes automatically reflect the update upon opening.

Advisory File Locks
~~~~~~~~~~~~~~~~~~~
When opening or editing a scene, openPypeline broadcasts an advisory lock file (``.use``) to ``<project_root>/.openpypeline/file_use/``. If another artist on your team opens the same file in a shared cloud folder, Maya displays a non-blocking warning notice identifying who has the scene open.

Scene Tools
~~~~~~~~~~~
The Maya integration also includes built-in helpers for:
* **Playblasts:** Recording viewport animations directly to the item's preview directory.
* **Thumbnails:** Generating square viewport snapshots to represent the item in the browser.
* **Display Layers:** Cleanly stripping transient display layers during master export.
