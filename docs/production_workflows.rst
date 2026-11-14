Production Workflows
====================

openPypeline Studio organizes production data to separate daily creative iteration from approved studio deliverables. This guide covers project hierarchy, asset creation, the daily WIP iteration cycle, and the non-destructive mastering process.

Core concepts and terminology
-----------------------------

openPypeline organizes production data into a strict hierarchy:

* **Asset Type:** Top-level category for assets, such as ``characters``, ``props``, ``sets``, or ``vehicles``.
* **Asset:** A distinct production entity (e.g., ``hero``, ``table``, ``lamp``).
* **Component:** A functional sub-division of an asset (e.g., ``model``, ``rig``, ``shading``, ``groom``). Components allow specialists to work in parallel on the same asset.
* **Sequence:** A logical grouping of shots (e.g., ``sq01``).
* **Shot:** A specific film or sequence unit (e.g., ``sh010``, ``sh020``) where assets are animated, lit, or rendered.
* **WIP (Work in Progress):** The working scene file that artists iterate on daily (formerly called *Workshop* in legacy openPipeline).
* **Master:** An approved, frozen production scene intended for review, scene referencing, or downstream pipeline steps.

Understanding Assets and Components
-----------------------------------

A simple asset (like a prop) may be self-contained as a single asset file. Complex assets (like characters or hero vehicles) benefit from **Components**:

.. code-block:: text

   characters/
     hero/
       model/       <-- Modeler works here
       rig/         <-- Rigger references the model Master here
       textures/    <-- Texture artist works here

By separating assets into components, a rigger can reference the approved model Master into the rig component while the texture artist paints maps for the same model. When the model Master is updated, downstream component scenes receive the update automatically via Maya referencing.

Asset and Shot creation modes
-----------------------------

When creating a new Asset or Shot in the browser tabs, you are presented with three creation modes:

* **Start with empty Item:** Creates the directory structure on disk with no files. Use this when starting fresh in an empty scene.
* **Export current selection:** Extracts whatever objects are currently selected in the Maya viewport and saves them as the initial WIP version.
* **Export current scene:** Takes your entire active Maya scene and saves it as the first WIP version of the new item.

Reading browser status indicators
---------------------------------

The Asset and Shot browsers provide at-a-glance status indicators for every item in your project:

* **Bold text:** The item is currently open in your active Maya session.
* **Gold Master icon:** The item has an approved, published Master file ready for downstream production.
* **Coral / Orange WIP icon:** The item has active WIP version files, but no Master has been published yet.
* **Gray text:** The item has been registered in the pipeline but contains no scene files yet.

The daily iteration loop ("Currently Open" tab)
-----------------------------------------------

Once an asset or shot is open, the **Currently Open** tab provides day-to-day production tools:

Saving WIP versions
~~~~~~~~~~~~~~~~~~~

Click :guilabel:`Save WIP...` to save an incremented version (e.g., ``hero_wip_0001.ma``, ``hero_wip_0002.ma``). You will be prompted to enter an artist comment describing your changes. This comment is recorded in the item's history log.

Capturing viewport thumbnails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Click :guilabel:`Take Snapshot` to capture an instant image of the active Maya viewport. This thumbnail appears in the **Preview** panel across all browser tabs, allowing other artists and leads to quickly identify the asset visually.

Playblasts and review
~~~~~~~~~~~~~~~~~~~~~

Use :guilabel:`Record Playblast` to capture animation directly from your viewport and :guilabel:`View Playblast` to inspect the latest review movie.

Reviving earlier versions
~~~~~~~~~~~~~~~~~~~~~~~~~

If a creative direction changes or you need to inspect an earlier iteration, click :guilabel:`Revive...`:

1. A version browser will open displaying all numbered WIP files alongside their saved artist comments and timestamps.
2. Select an earlier version to inspect or restore.
3. openPypeline saves the revived file as the *latest* incremented WIP, ensuring older versions remain non-destructively preserved in history.

The Mastering workflow
----------------------

.. important::

   **The Golden Rule:** Never open or hand-edit a Master file directly. All creative development occurs in WIP files. When a WIP is stable and approved, publish a new Master from it.

When you click :guilabel:`Save Master...`, openPypeline executes a coordinated sequence:

1. It saves a new, incremented WIP file from your active scene (preserving your unedited working state).
2. It executes any configured scene cleanup and custom commands on the scene to be mastered.
3. It saves the Master file (e.g., ``hero_asset.ma``).
4. By default, it reopens the newly incremented WIP file, ensuring that subsequent work never contaminates the published Master.

Why Masters use static filenames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While WIP iterations are numbered (``hero_wip_0001.ma``, ``hero_wip_0002.ma``), published Master files intentionally use a **static, unversioned filename** at the item root (e.g., ``hero_asset.ma``).

This is a core design principle of openPypeline:

* **Insulated Artist Iteration:** Artists are free to test, experiment, and save dozens of daily WIP versions without affecting other team members.
* **Seamless Downstream Updates:** Downstream scenes (such as rigs referencing models, or shots referencing rigs) link to the static Master file (``hero_asset.ma``). Whenever a new Master is published, that file is replaced in place. Every shot referencing it automatically receives the latest upstream model or rig upon opening—without anyone having to repath references or update filenames manually.

The Save Master Switchboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **Save Master** dialog exposes several publishing options:

* **Import References:**
  - *For Asset Masters:* Importing references bakes referenced components (such as a model inside a rig) directly into the file. Unloaded references prompt you to keep or remove them.
  - *For Shot Masters:* Shot files generally **keep references live** so animated shots continuously receive updates from asset Masters. Only import references when freezing a shot for final caching or rendering.
* **Delete Display Layers:** Automatically removes temporary artist display layers, leaving a clean Outliner hierarchy for lighting and rendering.
* **Custom Master Command:** A custom Python or MEL command executed immediately before saving the Master.
* **Comment:** A publication note recorded in the version history and passed to version control.
* **Post-Master Action:** Choose whether to return to the incremented WIP (recommended) or open the Master file directly.

Non-destructive cleanup scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In animation pipelines, artists often need to retain construction history, input graphs, and un-frozen transforms in their working WIP scenes for easy modifications. However, downstream departments (rigging, lighting, rendering) require clean meshes with frozen transforms and no history.

Custom Master commands solve this non-destructively:

.. code-block:: text

   Working WIP File (Contains History, Pivot Tweaks, Non-frozen Transforms)
         |
         +---> Save Master Action Triggered
         |         |
         |         +---> Custom Command Runs: Freezes Transforms & Deletes History
         |         |
         |         +---> Clean Master Saved (Published for downstream departments)
         |
         v
   New WIP Resumed (Artist continues with full history intact!)

Example custom Master command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can define a helper procedure in Maya and enter it into the :guilabel:`Custom Command` field. For example, a Python or MEL procedure that freezes transforms on all polygon meshes and deletes construction history:

.. code-block:: python

   # Python example: clean meshes before mastering
   import maya.cmds as cmds

   def clean_model_for_master():
       meshes = cmds.ls(type="mesh", long=True) or []
       transforms = list({cmds.listRelatives(m, parent=True, fullPath=True)[0] for m in meshes})
       if transforms:
           cmds.makeIdentity(transforms, apply=True, translate=True, rotate=True, scale=True)
           cmds.delete(transforms, constructionHistory=True)

Because this runs during the mastering step, the frozen transforms and cleared history apply exclusively to the published Master, while the artist's working WIP keeps its construction history completely intact.

Automated Version Control (VCS) publishing
------------------------------------------

If your project configuration specifies a version control system (``git``, ``svn``, or ``perforce``):

1. openPypeline automatically invokes the corresponding VCS handler upon saving a Master.
2. The file is staged/reconciled, committed with your Master comment, and submitted to the server automatically.
3. If publishing encounters a network or conflict error, openPypeline alerts you in Maya's Script Editor log while preserving the local Master on disk.

Pipeline safety and asset lifecycle
-----------------------------------

openPypeline Studio implements several safeguards to protect production data and prevent accidental loss.

Non-destructive deletion
~~~~~~~~~~~~~~~~~~~~~~~~

When an artist or lead removes an Asset, Component, Shot, or Asset Type using the :guilabel:`Remove` button:

* Files are **never permanently deleted** from the hard drive.
* The entire directory structure for the removed item is moved into the project's configured ``deleted/`` folder.
* If an item was removed by mistake, you can recover it directly from the ``deleted/`` folder without data loss.

Archiving and retrieving items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As production progresses, completed assets or abandoned shot iterations can clutter browser lists. Rather than deleting them, openPypeline provides an archiving workflow:

* **Archiving:** Right-click an asset or component and choose :menuselection:`Archive...` (or use the Archive tools under the :menuselection:`Tools` menu). This moves the scene files into the project's ``archive/`` directory and removes them from the active browser view.
* **Retrieving:** Archived items can be restored to the active pipeline at any time via the Archive tools, returning their full version history to the browser.

Shot referencing rules
~~~~~~~~~~~~~~~~~~~~~~

When working in the Shot Browser and referencing an Asset into an animation or layout scene:

* openPypeline **always resolves and references the latest published Master** for that asset.
* It will never reference an artist's in-progress WIP scene. This ensures animators and lighters work only with stable, approved character models and rigs.

Filesystem rules and ignored dotfiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Version number padding:** By default, WIP versions use four-digit zero padding (e.g., ``_wip_0001.ma``). If a heavily iterated asset exceeds version 9999, the version parser dynamically expands without truncating numbers.
* **Hidden directories and dotfiles:** The project scanner ignores any directory starting with a period (``.``). This prevents version control directories (``.git``, ``.svn``), system metadata (``.DS_Store``), and internal pipeline caches (``.openpypeline``) from appearing as accidental project items.

