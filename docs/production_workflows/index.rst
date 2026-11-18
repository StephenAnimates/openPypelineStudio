Production Workflows
======================
This guide covers the production workflows and best practices for using openPypeline Studio. It is intended for artists, leads, and technical directors who are responsible for managing production data and ensuring a smooth creative process.

Introduction
------------
OpenPypeline Studio organizes production data to separate daily creative iteration from approved studio deliverables. This guide covers project hierarchy, asset creation, the daily WIP iteration cycle, and the non-destructive mastering process.

Starting up After Installation
------------------------------
Launch the main openPypeline Studio UI at any time by running:

.. code-block:: python

   from openpypeline.app.maya.core import ops_loader
   ops_loader.openPypeline()

.. tip::

   Highlight the Python launch code snippet (from above) in your host application's Script Editor (or shelf tool editor) and drag it to your shelf tab to create a convenient single-click launch button.

Core Concepts and Terminology
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

.. toctree::
   :maxdepth: 2

   daily_iterations
   the_mastering_workflow
   automated_version_control_publishing
   pipeline_safety_and_asset_lifecycle
