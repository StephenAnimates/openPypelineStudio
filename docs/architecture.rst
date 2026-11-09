Architecture
============

openPypeline Studio is a Python package organized around shared pipeline code and application-specific integrations. The intended boundary is that reusable project, file, and workflow logic lives in ``openpypeline/core/``, while code that calls a host application's SDK lives in ``openpypeline/app/<host>/``. The boundary is still evolving, so some current modules cross it.

Runtime structure
-----------------

The current user interface runs in Maya. Its loader initializes the Maya UI, whose views and controllers route user actions to shared pipeline functions and Maya-specific UI wrappers. Shared code can request scene operations through the engine's active file handler.

.. code-block:: text

   Maya
     |
     v
   app/maya/core/ops_loader.py
     |
     v
   app/maya/ui/ (views and controllers)
     |
     +----> app/maya/core/ops_ui_wrappers.py
     |
     v
   core/ (actions, project/file metadata, versions, notes, preferences)
     |
     v
   openpypeline/ops_engine.py
     |
     v
   app/<detected host>/file/file.py
     |
     v
   Host SDK and scene

``OpsEngine`` detects a host by checking which host SDK modules are loaded in the Python process. It then attempts to import ``openpypeline.app.<host>.file.file`` as the file handler. In a standalone process, no host file handler is loaded. Host detection and the presence of a file handler do not imply that every feature is implemented or supported in that host.

Code layout
-----------

* ``openpypeline/ops_engine.py`` detects the active host and loads its file handler. It also provides engine-level operations that coordinate shared file logic with the handler.
* ``openpypeline/core/models.py`` defines shared data structures such as ``ItemContext`` and ``ProjectConfig``, plus enums for browser tabs and hierarchy levels.
* ``openpypeline/core/ops_actions.py`` coordinates pipeline actions, including saving WIPs and publishing Masters, and delegates scene operations through the engine's file handler.
* ``openpypeline/core/ops_info.py`` resolves project and item paths, naming conventions, WIP versions, and related state from preferences and the filesystem.
* ``openpypeline/core/file/`` contains file inventory, WIP, and Master helpers. ``openpypeline/core/version/`` handles version discovery and version-control integrations. ``openpypeline/core/notes/`` and ``openpypeline/core/ops_notes.py`` handle notes.
* ``openpypeline/core/util/prefs.py`` stores user preferences in ``~/.openpypeline/user_prefs.json``.
* ``openpypeline/app/maya/ui/`` contains Maya UI views and controllers. ``openpypeline/app/maya/file/file.py`` implements Maya scene operations.
* ``openpypeline/app/<host>/`` contains host-specific code. Current file-handler modules exist for Maya, Houdini, and Nuke, but their capabilities differ; some operations are unimplemented.

Project data and scene files
----------------------------

User preferences are stored separately from project records. The project-file location is selected in preferences; under that location, the project registry is stored in ``openpypeline_projects.json`` and the optional shared user list in ``openpypeline_users.json``. Project configuration describes paths, naming terms, formats, and other project settings. Production scenes and related files are stored in the project's configured folders rather than inside the Python package.

For an item operation, the UI selection is represented by an ``ItemContext``: a browser tab and up to three hierarchy levels. Shared path and file helpers combine that context with the selected project's configuration and naming preferences to find the relevant item, WIP, or Master on disk. WIP versions are numbered files; a Master is the named production version. The Maya integration performs host-specific operations such as opening or saving scenes.

Current boundaries and limitations
----------------------------------

The architecture is not yet a strict host-neutral core. For example, ``openpypeline/core/ops_project.py`` currently imports PySide6 and Maya utilities, and shared actions import the engine and version-control implementations. These are known coupling points when considering refactors; do not assume that importing every module under ``core`` works outside Maya or without optional dependencies.

Maya is the current supported UI integration. The engine can detect other host SDKs and load corresponding file-handler modules when present, but that does not constitute end-to-end support. Check the relevant implementation and tests before relying on a host operation; Houdini and Nuke file handlers, for example, do not implement every operation exposed by the Maya handler.

Contributor guidance
--------------------

When adding or changing functionality:

* Keep reusable behavior and data in the shared core where practical, and route host SDK calls through the corresponding host integration.
* Treat host-specific capabilities as optional; do not import a host SDK from a shared module unless the dependency is deliberately isolated and documented.
* Preserve the distinction between intended architecture and implemented behavior. Update tests and user or contributor documentation when capabilities change.
* Use host-independent tests or test doubles for shared logic, and run host-specific smoke tests in the relevant application when available.

For the mapping from the original MEL framework to current modules, see :doc:`architecture_migration`. For generated module and symbol documentation, see :doc:`modules`.
