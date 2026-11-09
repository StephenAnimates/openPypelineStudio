Host Support
============

This page distinguishes the application's current support status from host detection and partial adapter code. A host being detected by the engine, or having a file-handler module, does not mean that the full openPypeline workflow is implemented, tested, or supported there.

Support summary
---------------

.. list-table::
   :header-rows: 1
   :widths: 18 24 30 28

   * - Host
     - Status
     - Code present
     - Version and validation
   * - Autodesk Maya
     - Current supported integration
     - Main UI and Maya scene/file operations, including open, save, import, reference, playblast, and thumbnail helpers.
     - The README declares Maya 2026 or newer. The repository does not document a Maya runtime smoke-test matrix; the CI Maya-version matrix does not run the test suite because its pytest step is commented out.
   * - Houdini
     - Partial adapter; not declared supported
     - File-handler code for opening, saving, clearing, and merging Houdini scenes. Export is explicitly unimplemented.
     - No supported Houdini version or runtime validation is documented.
   * - Nuke
     - Partial adapter; not declared supported
     - File-handler code for opening, saving, clearing, and saving scripts. Export is explicitly unimplemented.
     - No supported Nuke version or runtime validation is documented.
   * - Blender
     - Not currently supported
     - The engine can detect Blender's ``bpy`` module, but no Blender file-handler package is present.
     - No supported version or runtime validation is documented.
   * - Unreal Engine
     - Not currently supported
     - The engine can detect the ``unreal`` module, but no Unreal file-handler package is present.
     - No supported version or runtime validation is documented.
   * - Standalone Python
     - Shared-core use only; no standalone UI
     - The engine detects a standalone process but does not load a host file handler.
     - The project does not define a standalone application support or validation matrix.

Maya capabilities
-----------------

Maya is the only integration currently described as supported by the project. Its integration includes the user interface and operations backed by Maya's Python APIs. Some operations depend on Maya plugins, such as Maya USD or Alembic plugins, being available in the installation.

The README lists Maya 2026 or newer as a requirement. This is a declared requirement, not evidence that every version in that range has passed interactive validation. The CI configuration contains Maya/Python version entries, but the automated test command is currently commented out and those CI jobs do not launch Maya. Confirm compatibility in the target Maya installation before production use.

Partial adapters
----------------

The Houdini and Nuke modules provide some scene or script file operations, but they do not supply the complete Maya UI or all operations expected by shared workflows. Their code should be treated as partial implementation rather than supported integrations. In particular, both adapters currently return failure for export operations.

The engine also recognizes Blender and Unreal Python modules during host detection. Detection alone does not provide usable integration behavior: the corresponding file-handler packages are not present in the repository.

Standalone use
--------------

The shared engine can be imported in a normal Python process, but the project does not currently provide a separate standalone user interface. Operations that require a host file handler are unavailable without a supported host. The phrase “shared core” describes the intended code boundary and does not guarantee that every module is importable without optional host or UI dependencies; see :doc:`architecture` for current coupling points.

How support status should change
--------------------------------

Before declaring another host supported, document the tested application and version, installation and dependency requirements, and implemented capabilities. Validate the integration in the host itself, including the user workflows that depend on its file handler. Tests using mocks or adapter doubles are useful for shared logic, but do not replace host runtime validation.

For planned integration work, see the `project roadmap <https://github.com/StephenAnimates/OpenPipeline/blob/master/ROADMAP.md>`_.
