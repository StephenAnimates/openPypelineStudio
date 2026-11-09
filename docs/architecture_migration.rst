Legacy architecture and contributor guide
==========================================

The original openPipeline implementation used global MEL procedures, including
``openPipelineFile.mel``, ``openPipelineUI.mel``, and
``openPipelineProject.mel``. openPypeline Studio is being developed as a
Python package with shared pipeline code in ``openpypeline/core/`` and
application-specific behavior in ``openpypeline/app/<host>/``.

This table maps historical areas of responsibility to current code locations.
It is a contributor's navigation aid, not a one-to-one API compatibility
promise; some workflows and host integrations remain incomplete.

.. list-table::
   :header-rows: 1
   :widths: 32 40 28

   * - Legacy area
     - Current code to inspect
     - Notes
   * - ``openPipelineFile.mel`` and ``openPipeline.mel``
     - ``openpypeline/core/ops_actions.py`` and ``openpypeline/app/maya/file/file.py``
     - Shared actions should call host behavior through an adapter.
   * - ``openPipelineUtility.mel``
     - ``openpypeline/core/ops_info.py`` and ``openpypeline/app/maya/core/ops_utils.py``
     - Path, project, and utility behavior is split between shared and Maya code.
   * - ``openPipelineUI.mel``
     - ``openpypeline/app/maya/ui/`` and ``openpypeline/app/maya/core/ops_ui_wrappers.py``
     - Maya window/view code and UI action wrappers are host-specific.
   * - ``openPipelineProject.mel``
     - ``openpypeline/core/ops_project.py`` and ``openpypeline/core/models.py``
     - Project configuration and data models.
   * - ``openPipelineSceneInv.mel``
     - ``openpypeline/app/maya/core/ops_scene_inv.py``
     - Maya scene inventory UI and scene-specific behavior.
   * - ``openPipelineNotes.mel``
     - ``openpypeline/core/ops_notes.py`` and ``openpypeline/core/notes/``
     - Notes-related shared logic and storage.
   * - ``openPipelineInit.mel``
     - ``openpypeline/core/util/prefs.py`` and ``openpypeline/app/maya/core/ops_init.py``
     - Shared JSON preferences and Maya startup defaults.

Contributor guidance
--------------------

* Keep reusable data and workflow logic in ``openpypeline/core/``.
* Keep host SDK imports, scene operations, and host-bound UI in that host's
  application package.
* Check the current implementation and tests before assuming a legacy operation
  still exists or behaves the same way.
* Add or update tests when migrating behavior, using host doubles for shared
  logic and host-specific smoke tests where the application is available.

The generated :doc:`modules` reference documents the current Python package.
