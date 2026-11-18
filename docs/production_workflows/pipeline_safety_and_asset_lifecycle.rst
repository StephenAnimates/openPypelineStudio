Pipeline Safety and Asset Lifecycle
-----------------------------------

OpenPypeline Studio (OPS) implements several safeguards to protect production data and prevent accidental loss.

Non-destructive deletion
~~~~~~~~~~~~~~~~~~~~~~~~
When an artist or lead removes an Asset, Component, Shot, or Asset Type using the :guilabel:`Remove` button:

* Files are **not permanently deleted** from the hard drive.
* The entire directory structure for the removed item is moved into the project's configured ``deleted/`` folder.
* If an item was removed by mistake, you can recover it directly from the ``deleted/`` folder without data loss.

Archiving and Retrieving Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As the production progresses, completed assets or abandoned shot iterations can clutter browser lists. Rather than deleting them, openPypeline provides an archiving workflow:

* **Archiving:** Right-click an asset or component and choose :menuselection:`Archive...` (or use the Archive tools under the :menuselection:`Tools` menu). This moves the scene files into the project's ``archive/`` directory and removes them from the active browser view.
* **Retrieving:** Archived items can be restored to the active pipeline at any time via the Archive tools, returning their full version history to the browser.

Shot Referencing Rules
~~~~~~~~~~~~~~~~~~~~~~
When working in the **Shot Browser** and referencing an **Asset** into an animation or layout scene:

* OpenPypeline **always resolves and references the latest published Master** for that asset.
* It will never reference an artist's in-progress **WIP** scene. This ensures animators and lighters work only with stable, approved character models and rigs.

Filesystem rules and ignored dotfiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* **Version number padding:** By default, **WIP** versions use four-digit zero padding (e.g., ``_wip_0001.ma``). If a heavily iterated asset exceeds version 9999, the version parser dynamically expands without truncating numbers.
* **Hidden directories and dotfiles:** The project scanner ignores any directory starting with a period (``.``). This prevents version control directories (``.git``, ``.svn``), system metadata (``.DS_Store``), and internal pipeline caches (``.openpypeline``) from appearing as accidental project items.
