# openPypeline Studio - Project Roadmap

This document tracks openPypeline Studio's evolution from a Maya-first tool into a modular Python pipeline framework for multiple creative applications.

## Project Principles
- The application runs locally and works with project folders that users synchronize through services such as Google Drive, iCloud Drive, OneDrive, or Dropbox.
- Be aware that synchronized project files may be temporarily unavailable, out of date, or in conflict while a sync client propagates changes.
- Keep shared pipeline concepts and data models in `openpypeline/core/`; keep application APIs, UI bindings, and host-specific behavior in that application's integration.
- Treat integrations as optional: importing or using the shared core should not require every supported application's SDK or Python package.
- Reuse common workflows where applications support them, but allow integrations to expose capabilities that are specific to a host.
- A directory or an importable module alone does not mean an application is supported. Mark an integration as supported only after its documented capabilities and validation requirements are met.

An application integration should document the host and version tested, its installation/dependency requirements, and the pipeline capabilities it implements (for example open/save, publish, export, or UI). Unsupported capabilities should be explicit rather than silently assumed.

File-use notifications or locks should operate on project metadata within the user-managed synchronized folder, not attempt to implement synchronization. Because sync clients may propagate updates asynchronously and may create conflict copies, a lock file in that folder is advisory rather than a guaranteed distributed lock. The UI should communicate this limitation and avoid claiming that concurrent edits are impossible.

## Phase 1: Structural Foundation & Packaging (In Progress)
- [x] Isolate DCC-specific code (Move Maya scripts to `/openpypeline/app/maya/`).
- [x] Rename and reorganize the legacy `/openpypeline/app/maya/core/openPypelineStudio` directory and its contents.
- [x] Establish a pure agnostic `/openpypeline/core/` directory.
- [x] Remove legacy OptionVars in favor of JSON-based agnostic preferences.
- [x] Clean up Python packaging (Add `__init__.py` files, transition to absolute/relative package imports).
- [x] Remove excessive `sys.path` injection from entry scripts (`ops_loader.py`, `ops_dev_launcher.py`).
- [x] Enforce standard PEP 8 Pythonic naming conventions across all files and directories (`opsActions.py` -> `ops_actions.py`, `camelCase` to `snake_case`).

## Phase 2: UI Modernization & MVC Architecture (In Progress)
- [x] Port all legacy UIs to PySide6.
- [x] Implement MVC for `ops_main_ui` (formerly `opsMainUI`) (Separating View from Controller).
- [x] Implement MVC for `ops_proj_dialog_gui` (formerly `opsProjDialogGUI`).
- [x] Implement MVC for `ops_save_master_gui` (formerly `opsSaveMasterGUI`) (Moved async TaskFetcher to controller).
- [x] Implement MVC for `ops_settings_gui` (formerly `opsSettingsGUI`).
- [x] Implement MVC for `ops_project_manager_gui` (formerly `opsProjectManagerGUI`).
- [x] Evaluate and refactor the `ui_objects.py` (formerly `UIObjects.py`) Singleton pattern (Consider an overarching `App` or `Window Manager` class).
- [x] Consolidate Main UI menus (Added `File`, `Project`, and `Create` menus, reorganized `Tools`).
- [x] Implement an automatic dynamic Add-on discovery system for drop-in Python tools.
- [x] Create legacy XML to JSON migration Add-ons (`ops_migrate_legacy_data`, `ops_migrate_legacy_notes`).

## Phase 3: Core Contracts & Host Adapter Architecture
- [x] Audit `ops_actions` and `ops_ui_wrappers` (formerly `opsActions` and `opsUIWrappers`) to ensure absolutely NO Maya commands (`import maya.cmds`) are used in the core logic.
- [x] Relocate Agnostic Core Files (`ops_actions.py`, `ops_info.py`, `ops_project.py`, `ops_notes.py`) to the `/openpypeline/core/` directory.
- [x] Upgrade legacy XML-based project tracking to JSON.
- [x] Upgrade legacy XML-based history notes to JSON.
- [x] Standardize Add-on System (Split Core-agnostic Add-ons vs DCC-specific Add-ons).
- [ ] Define a host adapter contract for common operations (for example open/save, publish, and supported exports), with explicit optional capabilities.
- [ ] Route host-specific operations through adapters without importing application SDKs from the shared core.
- [ ] Define host discovery and standalone behavior, including a clear result when an operation is unsupported by the active host.
- [ ] Add adapter contract tests using lightweight test doubles so core behavior can be tested without installing DCC applications.
- [ ] Implement FBX export/import support alongside USD and Alembic.
- [x] Implement Data Classes (`ItemContext`, `ProjectConfig`) to replace excessive backend parameters.
- [x] Replace Magic Numbers (`tab == 2`) and Strings with `Enum` classes for safer type checking.
- [ ] Transition cross-platform path handling to `pathlib`.

## Phase 4: Localization & Polish
- [x] Create a core localization manager (`localization.py`).
- [x] Apply localization to `ops_main_ui` (formerly `opsMainUI`) tooltips.
- [ ] Extract all hardcoded UI text strings across all View files into localization dictionary files.
- [ ] Extract controller warning/error messages into localization.
- [x] Centralize UI assets (images/icons) into a DCC-agnostic `/resources/` folder and enforce `snake_case` naming.
- [ ] Test the centralized UI assets across different DCCs and display resolutions.
- [ ] Update application and UI icons to modern, high-resolution formats.
- [ ] Implement language hot-swapping in `ops_settings_gui` (formerly `opsSettingsGUI`).
- [ ] Evaluate supporting regional dialects for localization (e.g., `en_us.json` vs `en_uk.json`).

## Phase 5: Quality Assurance & Integration Validation
- [x] Set up Sphinx documentation generation for the core Python API (`docs/conf.py`).
- [ ] Create a development environment for testing the shared core independently of any DCC.
- [ ] Document a host/version support matrix, integration dependencies, and tested capabilities.
- [ ] Create repeatable interactive smoke-test instructions for each host integration.
- [ ] Write Unit Tests for Controller classes (Mocking the Views).
- [ ] Write Unit Tests for core preferences and file operations.
- [ ] Add automated tests for common file-format workflows where the host adapter supports them (including OpenUSD and Alembic).
- [ ] Require core tests and the relevant host smoke tests before marking an integration supported.

## Phase 6: Application Integrations
Integrations are developed and validated incrementally against the host adapter contract. The sequence below preserves the project's current priority order; existing application directories are starting points, not proof of complete or supported integrations.
- [ ] Develop Substance 3D Painter integration (`/openpypeline/app/substance_painter/`).
- [ ] Develop a ZBrush integration (`/openpypeline/app/zbrush/`).
- [ ] Develop a Unity integration (`/openpypeline/app/unity/`).
- [ ] Develop or validate the Nuke integration (`/openpypeline/app/nuke/`).
- [ ] Develop Substance 3D Designer integration (`/openpypeline/app/substance_designer/`).
- [ ] Develop Substance 3D Modeler integration (`/openpypeline/app/substance_modeler/`).
- [ ] Develop or validate the Houdini integration (`/openpypeline/app/houdini/`).
- [ ] Develop an Unreal Engine integration (`/openpypeline/app/unreal_engine/`).
- [ ] Develop a Blender integration (`/openpypeline/app/blender/`).
- [ ] Develop a standalone/headless mode for workflows that do not require a DCC.

## Phase 7: Production Services & External Integrations
Keep service integrations such as version control and production tracking separate from DCC adapters so they can be reused across hosts. Projects remain local; users may place them in folders synchronized by a service they already use. Git, SVN, and Perforce handlers are available in the codebase, but self-hosted VCS setup is not the default workflow.
- [x] Implement core VCS base and subprocess handlers (Git, SVN, Perforce) in `Version.py`.
- [x] Hook VCS `publish()` method into `ops_actions.py` for mastering workflows.
- [ ] Implement Autodesk Flow Production Tracking (ShotGrid) API integration (`/openpypeline/core/trackers/shotgrid.py`).
- [ ] Add VCS selection dropdown to the Project Editor dialog.
- [x] Add Maya advisory file-in-use notices under the active project root, without integrating with or providing file synchronization.
- [x] Record session, user, machine, file, start time, and heartbeat; show expired notices as possibly stale rather than deleting them automatically.
- [x] Before Maya saves, warn and ask for confirmation when another notice exists or the on-disk file size/modification time changed since open.
- [ ] Test simultaneous opens, edits, saves, offline use, and sync-client conflict behavior across supported synchronization services.
- [x] Document that synchronized-folder notices are best-effort advisory locks, not guaranteed mutual exclusion; keep Perforce locking/checkout optional for teams that use Perforce.
- [ ] Implement equivalent file-use notices and save checks for other supported host applications.
- [ ] Create ftrack integration (Optional).
- [ ] Create Kitsu integration (Optional).