Production Workflows
====================

Core concepts and terminology
-----------------------------

openPypeline organizes production data into a hierarchy:

* **Asset:** A production unit such as a character, prop, or environment.
* **Component:** A piece of an asset, such as modeling, rigging, or shading.
* **Sequence:** A logical collection of shots.
* **Shot:** A unit of a sequence in which assets are animated, lit, or rendered.
* **WIP (Work in Progress):** The working scene an artist iterates on.
* **Master:** A prepared scene intended for review or downstream use.

Pipeline rules
--------------

* Use filesystem-safe names. The project dialog converts spaces to underscores and filters unsupported characters in project and folder names.
* Project configuration and preference data use JSON, while production files remain in the formats selected for the project and host application.
* Keep iterative work in numbered WIP files and treat Masters as prepared downstream deliverables. These file conventions organize work; they do not replace backups or a version-control service.

WIP and Master workflow
-----------------------

Keep day-to-day changes in WIP scenes. When the WIP is stable and ready for production, clean it and save a Master from it. Saving a Master first creates a new, incremented WIP file from the current scene; by default, openPypeline returns to that WIP so later development stays separate from the published Master. Do not open a Master file to make edits. Make changes in the WIP, then save a new Master when that work is ready for production.

Prepare a Master file
---------------------

Before saving a WIP as a Master, perform the standard Maya scene cleanup: freeze transforms, delete construction history, remove unwanted display layers, and organize the scene hierarchy. The resulting Master is the latest stable, functioning production version of the model, rig, or other asset.

.. note::

   Your team may have additional cleanup requirements; follow the conventions established for your project.

openPypeline does not currently automate these cleanup steps or run a user-defined cleanup script during Master publishing. If **Import References** is selected, the current save action imports loaded references into the scene before saving the Master. Unloaded references prompt the artist to keep or remove each one. This reference handling is separate from the standard cleanup steps above; review the scene and its references before saving the Master.

For animated scenes (shot files), referenced asset models and rig files are generally kept in the scene as references so that the shot can receive updates from the latest asset model or rig Master. Importing a referenced asset model or rig into the shot file removes the live link: later changes to the rig Master will not update the imported rig. Only import a rig when the shot workflow requires it, such as when preparing the scene for rendering.
