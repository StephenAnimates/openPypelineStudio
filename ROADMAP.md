# openPypeline Studio - Project Roadmap

This document tracks the modernization and feature expansion of openPypeline Studio as it transitions into a modern, DCC-agnostic Python 3 pipeline framework.

## Phase 1: Structural Foundation & Packaging (In Progress)
- [x] Isolate DCC-specific code (Move Maya scripts to `/openpypeline/app/maya/`).
- [x] Rename and reorganize the legacy `/openpypeline/app/maya/core/openPypelineStudio` directory and its contents.
- [x] Establish a pure agnostic `/openpypeline/core/` directory.
- [x] Remove legacy OptionVars in favor of JSON-based agnostic preferences.
- [x] Clean up Python packaging (Add `__init__.py` files, transition to absolute/relative package imports).
- [x] Remove excessive `sys.path` injection from entry scripts (`opsLoader.py`, `begin.py`).
- [ ] Enforce standard PEP 8 Pythonic naming conventions across all files and directories (`opsActions.py` -> `ops_actions.py`, `camelCase` to `snake_case`).

## Phase 2: UI Modernization & MVC Architecture (In Progress)
- [x] Port all legacy UIs to PySide6.
- [x] Implement MVC for `opsMainUI` (Separating View from Controller).
- [x] Implement MVC for `opsProjDialogGUI`.
- [x] Implement MVC for `opsSaveMasterGUI` (Moved async TaskFetcher to controller).
- [x] Implement MVC for `opsSettingsGUI`.
- [ ] Implement MVC for `opsProjectManagerGUI`.
- [ ] Evaluate and refactor the `UIObjects.py` Singleton pattern (Consider an overarching `App` or `Window Manager` class).

## Phase 3: Core Agnosticism & Backend Decoupling
- [x] Audit `opsActions` and `opsUIWrappers` to ensure absolutely NO Maya commands (`import maya.cmds`) are used in the core logic.
- [ ] Implement a DCC Interface/Adapter pattern (e.g., `core` asks the active `app` adapter to "save file" or "export Alembic").
- [ ] Upgrade legacy XML-based project tracking to JSON or SQLite for better performance and cross-compatibility.
- [ ] Implement FBX export/import support alongside USD and Alembic.

## Phase 4: Localization & Polish
- [x] Create a core localization manager (`localization.py`).
- [x] Apply localization to `opsMainUI` tooltips.
- [ ] Extract all hardcoded UI text strings across all View files into localization dictionary files.
- [ ] Extract controller warning/error messages into localization.
- [ ] Update application and UI icons to modern, high-resolution formats.
- [ ] Implement language hot-swapping in `opsSettingsGUI`.

## Phase 5: Quality Assurance & Pipeline Testing
- [ ] Write Unit Tests for Controller classes (Mocking the Views).
- [ ] Write Unit Tests for core preferences and file operations.
- [ ] Implement automated end-to-end testing for OpenUSD (`.usd`, `.usda`) and Alembic (`.abc`) project creation and exports.

## Phase 6: Application Expansion
- [ ] Create Nuke integration (`/openpypeline/app/nuke/`).
- [ ] Create Substance 3D Painter integration (`/openpypeline/app/substance_painter/`).
- [ ] Create Substance 3D Designer integration (`/openpypeline/app/substance_designer/`).
- [ ] Create Substance 3D Modeler integration (`/openpypeline/app/substance_modeler/`).
- [ ] Create ZBrush integration (`/openpypeline/app/zbrush/`).
- [ ] Create Houdini integration (`/openpypeline/app/houdini/`).
- [ ] Create Unity integration (`/openpypeline/app/unity/`).
- [ ] Create Unreal Engine integration (`/openpypeline/app/unreal_engine/`).
- [ ] Create Blender integration (`/openpypeline/app/blender/`).
- [ ] Develop a Standalone / Headless execution mode.

## Phase 7: Production Tracking & API Integrations
- [ ] Fully implement Autodesk Flow Production Tracking (ShotGrid) API integration (`/openpypeline/core/trackers/shotgrid.py`).
- [ ] Create ftrack integration (Optional).
- [ ] Create Kitsu integration (Optional).