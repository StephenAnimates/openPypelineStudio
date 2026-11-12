Welcome to openPypeline Studio
==============================

**openPypeline Studio** is a locally installed framework for managing creative production projects and workflows. Maya is its first supported host. The project is developing toward a shared, host-neutral core with application-specific integrations for additional creative software.

Teams can keep project folders in cloud storage and sync services they already use, such as Google Drive, iCloud Drive, OneDrive, or Dropbox, and work with those folders through their local openPypeline installation.

Project direction and planned work are tracked in the `project roadmap <https://github.com/StephenAnimates/OpenPipeline/blob/master/ROADMAP.md>`_.

Current scope
-------------

The current Maya integration includes project and asset/shot browsing, project directory and naming workflows, WIP and Master file concepts, notes, and application-aware scene operations. Not every feature or integration is complete; the presence of a module does not necessarily mean its host is supported.

For a feature overview, see the `README <https://github.com/StephenAnimates/openPypelineStudio/blob/master/README.md#-features>`_.

The shared core is intended for reusable pipeline concepts and data. Host APIs, scene operations, and host-specific UI belong in application integrations. Maya is the current supported integration; support for other applications should be considered planned until their capabilities and tested versions are documented.

Synced project folders
----------------------

The Maya integration can publish advisory file-use notices in a project folder and warn when a scene appears to be in use or has changed on disk. These notices are **not distributed locks**: sync clients may update files asynchronously, and conflicting edits or overwrites can still occur. Teams should coordinate edits and verify sync status before relying on another artist's changes.

For Maya installation and first-project guidance, see :doc:`getting_started`. For production naming and WIP/Master workflows, see :doc:`production_workflows`.

The original openPipeline framework used global MEL procedures. Contributors migrating legacy scripts can see :doc:`architecture_migration` for a historical source-to-module map and guidance on current package boundaries.

API reference
-------------

The API reference is generated from the Python package during the documentation build.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   about
   getting_started
   production_workflows
   architecture
   architecture_migration
   configuration
   host_support
   perforce_setup
   modules

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
