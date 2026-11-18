Architecture
============

OpenPypeline Studio (OPS) is a modular, multi-tier Python framework designed to manage digital asset production, scene versioning, and project workflows across creative Digital Content Creation (DCC) applications.

The framework is architected to balance two competing requirements:
1. **Host-Neutral Pipeline Logic:** Reusable asset management, version tracking, project resolution, and cloud synchronization logic that can execute in any Python environment (including headless render nodes, CI/CD runners, and standalone tools).
2. **Deep DCC Integration:** Native, context-aware integration with host application SDKs (Autodesk Maya, SideFX Houdini, Foundry Nuke, etc.) for scene manipulation, referencing, file export, and in-app artist dialogs.

This page documents the structural tiers, core data models, DCC abstraction patterns, persistence models, and ongoing architectural evolution of openPypeline Studio.

Multi-Tier Layered Architecture
-------------------------------

OpenPypeline Studio is organized into five distinct architectural layers. Dependencies flow strictly downward: upper layers may import and call lower layers, but lower layers never depend directly on the presentation or host application SDKs.

.. code-block:: text

   +-------------------------------------------------------------------------+
   |                        1. PRESENTATION LAYER                            |
   |   Host-Specific UI (app/maya/ui/)      |  UI Resources & Localization   |
   |   (Views, Controllers, Dialogs)         |  (resources/lang/, icons)      |
   +------------------------------------+------------------------------------+
                                        |
                                        v
   +-------------------------------------------------------------------------+
   |                   2. HOST INTEGRATION & ADAPTER LAYER                   |
   |   app/maya/core/ops_loader.py      |  app/maya/core/ops_ui_wrappers.py  |
   |   app/maya/file/file.py            |  app/houdini/file/file.py          |
   |   app/nuke/file/file.py            |  (Planned: Substance Painter,      |
   |                                    |   ZBrush, Unity, Blender, Unreal)  |
   +------------------------------------+------------------------------------+
                                        |
                                        v
   +-------------------------------------------------------------------------+
   |                     3. ENGINE & DISPATCHER LAYER                        |
   |                       openpypeline/ops_engine.py                        |
   |   - Environment sensing (inspects sys.modules for DCC APIs)             |
   |   - Dynamic binding and dispatch to active host file handler            |
   +------------------------------------+------------------------------------+
                                        |
                                        v
   +-------------------------------------------------------------------------+
   |                     4. CORE DOMAIN & ACTIONS LAYER                      |
   |                       openpypeline/core/                                |
   |   - Actions & Workflow Orchestration:  ops_actions.py                   |
   |   - Unified Data Models & Enums:       models.py (ItemContext, Config)  |
   |   - Path & Version Resolvers:          ops_info.py                      |
   |   - File & Inventory Logic:            file/ (wip, master, inventory)   |
   |   - Advisory Concurrency:              file_use.py (heartbeat notices)  |
   |   - Version Control Subsystem:         version/ (SVN, Perforce, Git)    |
   |   - Metadata & Notes:                  notes/ (ops_notes.py)            |
   |   - System Preferences & Utilities:    util/prefs.py, localization.py   |
   +------------------------------------+------------------------------------+
                                        |
                                        v
   +-------------------------------------------------------------------------+
   |                   5. PERSISTENCE & STORAGE LAYER                        |
   |   - User Preferences:      ~/.openpypeline/user_prefs.json              |
   |   - Machine Registry:      <configured_path>/openpypeline_projects.json |
   |   - Shared Manifest:       <project_root>/.openpypeline/project.json    |
   |   - Concurrency Registry:  <project_root>/.openpypeline/file_use/      |
   |   - Production Asset Tree: <project_root>/scenes/, textures/, etc.      |
   +-------------------------------------------------------------------------+

Layer Responsibilities
~~~~~~~~~~~~~~~~~~~~~~

1. **Presentation Layer:** Implemented in PySide6/Qt. It presents pipeline assets and shot hierarchies to the artist. Controllers react to user gestures, collect context, and delegate operations to ``core/ops_actions.py``.
2. **Host Integration & Adapter Layer:** Houses code that directly invokes a specific DCC's SDK (such as ``maya.cmds``, ``hou``, or ``nuke``). It implements scene loading, saving, referencing, and plugin verification.
3. **Engine & Dispatcher Layer:** The ``OpsEngine`` acts as a dynamic bridge. It inspects the Python runtime, identifies the host environment, and loads the corresponding adapter module without hardcoding host imports into the core.
4. **Core Domain & Actions Layer:** Pure, reusable pipeline logic. It manages item naming rules, directory resolution, WIP version increments, master publish promotions, advisory concurrency tracking, and VCS operations.
5. **Persistence & Storage Layer:** Governs how project configurations, user options, advisory lock heartbeats, and production scenes are organized and isolated on the filesystem.

The Core Data Model
-------------------

To eliminate long, error-prone argument lists inherited from legacy pipeline scripts, openPypeline Studio encapsulates operations in strongly typed dataclasses defined in ``openpypeline/core/models.py``.

The Unified 3-Level Hierarchy (ItemContext)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All creative assets and shot tasks in OPS are represented by a standardized 3-level tree encapsulated in an ``ItemContext`` dataclass:

.. code-block:: python

   @dataclass
   class ItemContext:
       tab: int          # Tab.ASSET (2) or Tab.SHOT (3)
       level1: str = ""  # Asset Type or Sequence
       level2: str = ""  # Asset Name or Shot Number
       level3: str = ""  # Component / Sub-process / Department

This unified structure allows the same core actions, versioning logic, and file helpers to operate polymorphically across both assets and shots:

.. list-table:: Hierarchy Mapping
   :widths: 20 25 25 30
   :header-rows: 1

   * - UI Tab
     - Level 1
     - Level 2
     - Level 3 (Optional)
   * - **Asset Browser** (Tab 2)
     - **Type** (e.g., ``characters``, ``props``, ``vehicles``)
     - **Asset** (e.g., ``hero``, ``sword``, ``car``)
     - **Component** (e.g., ``model``, ``rig``, ``texture``, ``surface``)
   * - **Shot Browser** (Tab 3)
     - **Sequence** (e.g., ``seq01``, ``seq_intro``)
     - **Shot** (e.g., ``sh010``, ``sh020``)
     - **Process / Department** (e.g., ``layout``, ``anim``, ``light``, ``fx``)

Helper properties on ``ItemContext`` provide instant contextual awareness:
* ``depth``: Returns integer depth (1 to 3) to validate whether an action can be performed.
* ``item_name``: Returns the leaf item name regardless of hierarchy depth.
* ``parent_name``: Returns the immediate parent name for relative file naming tokens.

Project Configuration Model (ProjectConfig)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ProjectConfig`` dataclass encapsulates the full configuration manifest for a project, replacing legacy 22-parameter function calls:

* **Identity:** Project name, root filesystem path, description, status (active/inactive), creation date, and deadline.
* **Naming Conventions:** WIP folder name (default: ``wip``), Master base name (default: ``master``), and file formats (``.ma``, ``.mb``, ``.usd``, ``.abc``).
* **Folder Structure:** Relative subdirectories for asset libraries (``scenes/assets``), shots (``scenes``), textures (``sourceimages``), scripts (``scripts``), renders (``images/renders``), archives (``archive``), and deleted items (``deleted``).

Host Abstraction & Dynamic Engine Dispatch
------------------------------------------

Host abstraction is governed by ``openpypeline/ops_engine.py`` using the Adapter and Facade patterns.

Dynamic Host Detection
~~~~~~~~~~~~~~~~~~~~~~

When ``OpsEngine`` initializes, it inspects ``sys.modules`` to dynamically identify which DCC environment is hosting the Python process:

.. code-block:: python

   def _detect_host_app(self):
       if "maya.cmds" in sys.modules or "maya" in sys.modules:
           return "maya"
       elif "hou" in sys.modules:
           return "houdini"
       elif "nuke" in sys.modules:
           return "nuke"
       return "standalone"

Based on the detected host, ``OpsEngine`` dynamically imports ``openpypeline.app.<host>.file.file`` as its active ``file_handler``. In standalone mode (e.g., during terminal scripts or automated tests), no DCC handler is attached.

The File Handler Protocol
~~~~~~~~~~~~~~~~~~~~~~~~~

Every host adapter module must conform to a common file handling protocol:

* ``open(filepath) -> bool``: Opens an existing scene file, prompting or forcing scene reset according to host semantics.
* ``save() -> bool``: Saves changes to the currently active scene.
* ``save_as(filepath, file_type=None) -> bool``: Saves the scene to a target path, ensuring appropriate export formats and file extensions.
* ``import_file(filepath) -> bool``: Merges or imports geometry/nodes into the current scene.
* ``reference_file(filepath) -> bool``: Creates a non-destructive scene reference (e.g., Maya file reference).
* ``new_file() -> bool``: Clears the workspace and initializes a fresh, empty scene.
* ``export_file(filepath, file_type=None, selected=False) -> bool``: Exports the active scene or selected nodes.
* ``is_modified() -> bool``: Queries whether the scene currently has unsaved changes.
* ``get_file_type(extension) -> str | None``: Translates a file extension (e.g., ``.ma``, ``.hip``, ``.spp``, ``.ztl``) to the host application's internal format identifier.
* ``get_workspace_root() -> str``: Returns the active workspace root directory from the host application, falling back to the working directory.
* ``_ensure_plugins_loaded(filepath, file_type)``: Pre-flight check that automatically loads required host plugins (e.g., ``mayaUsdPlugin``, ``AbcImport``, ``AbcExport``) before attempting I/O.

.. note::

   Host capabilities vary. Maya is the reference integration and implements all operations. Houdini and Nuke implement scene-level operations (open, save, save-as, import), while advanced referencing or playblasting may be host-specific. See :doc:`integrations/index` for a detailed capability matrix.

Three-Tier State & Persistence Architecture
-------------------------------------------

openPypeline Studio cleanly separates local user configuration, machine-specific paths, shared project definitions, and runtime concurrency notices.

.. list-table:: Configuration and Storage Scopes
   :widths: 20 25 35 20
   :header-rows: 1

   * - Scope
     - Storage Location
     - Purpose
     - Sync / VCS Rule
   * - **User Preferences**
     - ``~/.openpypeline/user_prefs.json``
     - Local artist settings: preferred user name, window layouts, last active project, and credentials.
     - **Never share** (User-private).
   * - **Machine Project Registry**
     - ``<configured_path>/openpypeline_projects.json``
     - Local registry mapping project names to local machine paths.
     - **Never share** (Machine-specific absolute paths).
   * - **Shared Project Manifest**
     - ``<project_root>/.openpypeline/project.json``
     - Portable project settings: relative folder layout, naming tokens, active file formats, and user roster.
     - **Always share** (Commit to SVN/Git or sync via cloud).
   * - **Advisory Concurrency**
     - ``<project_root>/.openpypeline/file_use/``
     - Ephemeral ``.use`` JSON notices tracking active scenes, heartbeats, user names, and host machines.
     - **Sync automatically** via cloud storage or VCS.

.. important::

   **Why the Machine Registry Must Not Be Synced:** Different team members frequently mount or clone projects at different absolute paths (e.g., ``/Users/Shared/Projects/...`` on macOS vs. ``D:\Projects\...`` on Windows). The local machine registry maps project names to local paths, whereas the project manifest inside ``<project_root>/.openpypeline/project.json`` uses strictly relative paths.

Lifecycle & Data Flow Walkthroughs
----------------------------------

To understand how layers interact during production, consider two primary pipeline workflows:

Workflow 1: Saving a WIP Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an artist clicks **Save WIP** in the Maya interface:

.. code-block:: text

   Artist Action: Click "Save WIP"
        |
        v
   app/maya/ui/ops_main_controller.py
        | collects active ItemContext and artist notes
        v
   core/ops_actions.py: save_wip(context, comment)
        |
        +---> core/ops_info.py: resolve_next_wip_path(context)
        |     (Inspects filesystem, calculates increment: e.g., hero_wip_v004.ma)
        |
        +---> openpypeline/ops_engine.py: engine.file_handler.save_as(wip_path)
        |     (Delegates to app/maya/file/file.py -> calls cmds.file(rename=..., save=True))
        |
        +---> core/file_use.py: registry.register_use(wip_path)
        |     (Writes .openpypeline/file_use/<hash>.use with active heartbeat)
        |
        +---> core/notes/ops_notes.py: record_version_note(wip_path, comment)
              (Appends timestamped artist comment to component note history)

Workflow 2: Publishing a Production Master
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a department lead or artist promotes an approved WIP to a production Master:

.. code-block:: text

   Artist Action: Click "Publish Master"
        |
        v
   app/maya/ui/ops_main_controller.py
        | validates permissions and prompts for publish release notes
        v
   core/ops_actions.py: publish_master(context, source_wip_path, notes)
        |
        +---> core/ops_info.py: resolve_master_path(context)
        |     (Resolves static downstream reference path: e.g., hero_model.ma)
        |
        +---> core/file/master.py: archive_existing_master()
        |     (If an older master exists, safely archives a timestamped copy)
        |
        +---> openpypeline/ops_engine.py: engine.file_handler.save_as(master_path)
        |     (Overwrites static master file with pristine published contents)
        |
        +---> core/version/Version.py: vcs.commit_file(master_path, message)
              (If Subversion or Perforce is enabled, submits file to the repository)

Notice that downstream department scenes (such as Rigging or Surfacing) reference the static Master filename (``hero_model.ma``). Publishing updates the master in place without breaking referencing links in downstream scenes. See :doc:`production_workflows/index` for comprehensive production rules.

Concurrency & Version Control Subsystems
----------------------------------------

Advisory Concurrency (file_use.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working across cloud-synchronized folders (such as Google Drive, OneDrive, or Dropbox), file systems lack real-time distributed file locking. openPypeline Studio solves this with an advisory heartbeat registry:

1. When a scene is opened or saved, ``FileUseRegistry`` generates a unique session lock file in ``<project_root>/.openpypeline/file_use/<file_hash>.use``.
2. The notice contains the user name, hostname, file path, initial timestamp, and recurring heartbeat timestamp.
3. If another artist attempts to open or save the same file, openPypeline detects the active lock, inspects the heartbeat, and warns the artist if the scene is in use.
4. Heartbeats expire after a configurable threshold (default: 5 minutes) to ensure stale locks from crashed sessions do not permanently block teammates.

Version Control Subsystem
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``openpypeline/core/version/`` package provides abstraction adapters for production version-control systems:
* **Subversion (SVN):** Supports centralized repository checkouts, automated add/commit operations on master publishing, and advisory lock integration.
* **Perforce (Helix Core):** Interfaces with Perforce client workspaces via `p4` CLI commands for automated checkouts, revisions, and changelist submission. See :doc:`perforce_setup` for workspace setup instructions.
* **Git:** Basic support for local checkout validation and repository tagging.

Target Architecture & Technical Debt
------------------------------------

As openPypeline Studio transitions from its historical MEL roots to a unified Python architecture, several legacy coupling points are scheduled for refactoring:

Current Technical Debt
~~~~~~~~~~~~~~~~~~~~~~

* **Qt Coupling in Core:** ``openpypeline/core/ops_project.py`` currently imports ``PySide6`` and Maya utility wrappers. This prevents running project operations headlessly in environments without Qt libraries installed.
* **Implicit File Handler Protocol:** The host file handler contract in ``openpypeline/app/<host>/file/file.py`` is currently structural (duck-typed) rather than enforced via Python type checking.
* **Monolithic Controllers:** Maya UI controllers manage both data transformation and dialog life-cycles.

Target Architecture (Roadmap Alignment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

According to the project `Roadmap <https://github.com/StephenAnimates/OpenPipeline/blob/master/ROADMAP.md>`_, the architecture is evolving toward:

1. **Strictly Headless Core:** Decoupling all Qt and host dependencies from ``openpypeline/core/``. The core will be importable in pure Python 3.9+ environments for automated tests, CLI utilities, and render farm automation.
2. **Formal HostFileHandlerBase Protocol:** Introducing an explicit Python ``Protocol`` or ``ABC`` with type annotations defining the exact contract for DCC adapters.
3. **Decoupled Event Bus:** Implementing an observer/event pattern so host callbacks (scene opened, before save, selection changed) publish events rather than directly calling UI controller methods.
4. **Standalone App Launcher:** Enabling openPypeline's Qt UI to run as a standalone asset browser outside any DCC, with the ability to launch scenes into Maya, Houdini, or Nuke on demand.

Contributor Guidance
--------------------

When contributing new features or host integrations:

* **Keep Reusable Code in Core:** Asset resolution, naming validation, and workflow logic belong in ``openpypeline/core/``. Never import DCC SDKs (``maya``, ``hou``, ``nuke``) inside ``core/``.
* **Adding a New DCC:** To add support for a new creative application (such as Substance 3D Painter, ZBrush, Unity, Blender, or Unreal Engine):
  1. Create ``openpypeline/app/<host>/loader.py`` exposing ``openPypeline()`` and ``openPypelineSetup()`` (plus host shelf/menu installers).
  2. Create ``openpypeline/app/<host>/file/file.py`` implementing the standard File Handler Protocol (``open``, ``save``, ``save_as``, ``import_file``, ``reference_file``, ``new_file``, ``export_file``, ``is_modified``, ``get_file_type``, and ``get_workspace_root``).
  3. Register host signature detection in ``OpsEngine._detect_host_app()``.
  4. Add corresponding mock-based unit tests in ``openpypeline/test_host_adapters.py``.

  For a complete step-by-step developer walkthrough, code scaffolds, and host execution models, see :doc:`authoring_host_integrations`.
* **Unit Testing with Test Doubles:** Core logic should have 100% test coverage using standard Python ``unittest`` or ``pytest``. Host SDK calls should be mocked using ``unittest.mock`` to ensure tests run swiftly without requiring proprietary DCC licenses.

For a detailed historical mapping of original MEL procedures to the modern Python modules, see :doc:`architecture_migration`. For generated API reference documentation, see :doc:`modules`.
