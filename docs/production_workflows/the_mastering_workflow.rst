The Mastering Workflow
======================
The mastering workflow is a non-destructive process that separates daily creative iteration from approved progress files. Artists work in **WIP** files, saving incremental versions as they refine their work. When a WIP is stable and approved, it is published as a **Master** file for **Referencing**.

.. important::

   **The Golden Rule:** Never open or hand-edit a **Master** file directly. All creative development occurs in **WIP** files. When a WIP is stable and approved, publish a new Master from it.

When you click :guilabel:`Save Master...`, openPypeline executes a coordinated sequence:

1. It saves a new, incremented WIP file from your active scene (preserving your unedited working state).
2. It executes any configured scene cleanup and custom commands on the scene to be mastered.
3. It saves the Master file (e.g., ``hero_asset.ma``).
4. By default, it reopens the newly incremented WIP file, ensuring that subsequent work never contaminates the published Master.

Why Masters use Static Filenames
--------------------------------
While WIP iterations are numbered (``hero_wip_0001.ma``, ``hero_wip_0002.ma``), published Master files intentionally use a **static, unversioned filename** at the item root (e.g., ``hero_asset.ma``).

This is a core design principle of openPypeline:

* **Insulated Artist Iteration:** Artists are free to test, experiment, and save dozens of daily WIP versions without affecting other team members.
* **Seamless Downstream Updates:** Downstream scenes (such as rigs referencing models, or shots referencing rigs) link to the static Master file (``hero_asset.ma``). Whenever a new Master is published, that file is replaced in place. Every shot referencing it automatically receives the latest upstream model or rig upon opening—without anyone having to repath references or update filenames manually.

The Save Master Switchboard
---------------------------
The **Save Master** dialog exposes several publishing options:

* **Import References:**
  - *For Asset Masters:* Importing references bakes referenced components (such as a model inside a rig) directly into the file. Unloaded references prompt you to keep or remove them.
  - *For Shot Masters:* Shot files generally **keep references live** so animated shots continuously receive updates from asset Masters. Only import references when freezing a shot for final caching or rendering.
* **Delete Display Layers:** Automatically removes temporary artist display layers, leaving a clean Outliner hierarchy for lighting and rendering.
* **Custom Master Command:** A custom Python or MEL command executed immediately before saving the Master.
* **Comment:** A publication note recorded in the version history and passed to version control.
* **Post-Master Action:** Choose whether to return to the incremented WIP (recommended) or open the Master file directly.

Non-destructive Cleanup Scripts
-------------------------------
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

Example Custom Master Command
-----------------------------
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
