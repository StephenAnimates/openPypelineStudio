Installation and Setup
======================
This guide covers installing the current openPypeline Studio (OPS) Maya integration and creating an initial project. For tested Maya and Python versions, see the requirements in the `README <https://github.com/StephenAnimates/OpenPipeline/blob/master/README.md#-requirements>`_.

Introduction
------------
OpenPypeline Studio is a locally installed framework for managing creative production projects and workflows. Maya is its first supported host. The project is developing toward a shared, host-neutral core with application-specific integrations for additional creative software.

While designed for teams, openPypeline Studio can be used by a single artist on a single computer. The Maya integration can publish advisory file-use notices in a project folder and warn when a scene appears to be in use or has changed on disk. These notices are **not distributed locks**: sync clients may update files asynchronously, and conflicting edits or overwrites can still occur. Teams should coordinate edits and verify sync status before relying on another artist's changes.

For workflow and production guidance, see :doc:`/production_workflows/index`. For a feature overview, see the `README <https://github.com/StephenAnimates/OpenPipeline/blob/master/README.md>`_.

.. toctree::
   :maxdepth: 2

   downloading_and_installing_openPypeline_studio
   maya_project_setup
   run_OPS_setup_script
   create_join_ops_project_maya
   join_an_existing_ops_project
   start_using_ops
