Welcome to openPypeline Studio
==============================

**openPypeline Studio** (OPS) is a locally installed framework for managing creative production projects and workflows. Maya is its first supported host. The project is developing toward a shared, host-neutral core with application-specific integrations for additional creative software.

Animation Teams using openPypeline Studio are able to keep project folders in cloud storage and sync services they already use, such as *Google Drive*, *iCloud Drive*, *OneDrive*, or *Dropbox*, and work with those folders through their local OPS installation.

Project direction and planned work are tracked in the `project roadmap <https://github.com/StephenAnimates/openPypelineStudio/blob/master/ROADMAP.md>`_.

Current Scope
-------------
The current Maya integration includes project and asset/shot browsing, project directory and naming workflows, WIP and Master file concepts, notes, and application-aware scene operations. Not every feature or integration is complete; the presence of a software integration module does not necessarily mean it is already supported.

For a feature overview, see the `README <https://github.com/StephenAnimates/openPypelineStudio/blob/master/README.md#-features>`_.

The shared core is intended for reusable pipeline concepts and data. Host APIs, scene operations, and host-specific UI belong in application integrations. Maya is the current supported integration; support for other applications should be considered planned until their capabilities and tested versions are documented.

Synced project folders
----------------------
The Maya integration can publish advisory file-use notices in a project folder and warn when a scene appears to be in use or has changed on disk. These notices are **not distributed locks**: sync clients may update files asynchronously, and conflicting edits or overwrites can still occur. Teams should coordinate edits and verify sync status before relying on another artist's changes.

* For Maya installation and first-project guidance, see :doc:`installation_and_setup/index`.
* For production naming and pipeline workflows, see :doc:`production_workflows/index`.

.. note::

   The original openPipeline framework used global MEL procedures. Contributors migrating legacy scripts can see :doc:`architecture_migration` for a historical source-to-module map and guidance on current package boundaries.

API reference
-------------

The API reference is generated from the Python package during the documentation build.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started & Artist Guides

   about
   installation_and_setup/index
   integrations/index
   production_workflows/index

.. toctree::
   :maxdepth: 2
   :caption: Studio Setup & Administration

   configuration
   host_support
   customization
   perforce_setup

.. toctree::
   :maxdepth: 2
   :caption: Architecture & Development

   architecture
   authoring_host_integrations
   architecture_migration
   modules
   tests

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
