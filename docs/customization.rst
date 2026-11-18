Studio Customization
====================

openPypeline Studio (OPS) is designed to adapt to your studio's specific pipeline conventions, naming standards, and visual branding. This guide outlines how technical directors and production leads can customize project appearances, directory topologies, naming tokens, user rosters, and localization strings.

Custom Project Branding & Icons
-------------------------------

Project Icon (`openPypelineIcon.png`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To customize the thumbnail image displayed for a project in the openPypeline Studio Project Selector and Project Manager:

1. Create a square graphic (e.g., your film's logo, game emblem, or mascot).
2. Name the file ``openPypelineIcon.png``.
3. Place the file directly in the **root folder** of that project (the directory containing ``.openpypeline/project.json``).

.. tip::

   **Icon Formatting Best Practices:**
   * **Dimensions:** 128x128, 256x256, or 512x512 pixels.
   * **Format:** PNG with a transparent background (alpha channel).
   * **Visual clarity:** Use bold silhouettes or high-contrast graphics that scale cleanly down to smaller UI thumbnail sizes.

UI Banner Customization
~~~~~~~~~~~~~~~~~~~~~~~

The default banner graphic shown in openPypeline headers is stored in ``openpypeline/resources/images/ops_banner.png``. Studios can replace or theme this banner to feature studio or production branding across artist workstations.

Custom Directory Topologies
---------------------------

Every studio organizes creative data differently. While openPypeline provides sensible production defaults, all directory locations can be customized per project in the **Project Manager** or directly inside ``.openpypeline/project.json``.

Configurable Folder Roles
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Pipeline Folder Settings
   :widths: 25 30 45
   :header-rows: 1

   * - Setting
     - Default Relative Path
     - Production Purpose
   * - **Asset Library**
     - ``scenes/assets``
     - Root directory for all asset types (characters, props, sets).
   * - **Shot Scenes**
     - ``scenes``
     - Root directory for film sequences and shot files.
   * - **Textures**
     - ``sourceimages``
     - Textures, PBR bitmap sets, and paint files.
   * - **Scripts**
     - ``scripts``
     - Project-specific Python/MEL scripts and automation.
   * - **Renders**
     - ``images/renders``
     - Rendered sequence frames, playblasts, and slap comps.
   * - **Particles / Cache**
     - ``particles``
     - Geometry caches, Alembic point clouds, and simulations.
   * - **Archive**
     - ``archive``
     - Non-destructive backups of superseded Master files.
   * - **Deleted Items**
     - ``deleted``
     - Safe quarantine for removed assets and shots.

.. important::

   All folder paths in ``.openpypeline/project.json`` are stored as **strictly relative paths** from the project root. This ensures that when project folders are synchronized across artists (via Google Drive, Dropbox, Perforce, or SVN), paths resolve seamlessly on both macOS and Windows.

Customizing Department Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Components divide complex assets and shots into parallel department tasks. While the standard pipeline includes components like ``model``, ``rig``, and ``surface``, you can define any custom department names:

* **3D Animation:** ``layout``, ``blocking``, ``anim``, ``cleanup``
* **Creature Effects:** ``groom``, ``hair``, ``cloth``, ``muscles``
* **Look Development:** ``texture``, ``shading``, ``light``
* **Simulation & FX:** ``fx``, ``pyro``, ``fluids``, ``crowds``

Custom Naming Conventions & Tokens
----------------------------------

openPypeline provides full control over file prefixes, version suffixes, and accepted formats.

WIP and Master Naming Terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Project Settings dialog (or via ``ProjectConfig``):
* **WIP Name Token:** Defaults to ``wip`` (e.g., ``hero_model_wip_v0004.ma``). You can customize this to ``work``, ``dev``, ``edit``, or your studio's preferred term.
* **Master Name Token:** Defaults to ``master`` (e.g., ``hero_model.ma``). You can customize this to ``publish``, ``approved``, or ``release``.

Allowed Formats
~~~~~~~~~~~~~~~

By default, openPypeline offers standard production formats (``.ma``, ``.mb``, ``.usd``, ``.usda``, ``.abc``, ``.hip``, ``.spp``, ``.nk``). The active format is configured per project and automatically validated upon file saving.

Custom User Rosters & Team Management
-------------------------------------

Global User Roster (`openpypeline_users.json`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The global user list is stored alongside your project registry in ``openpypeline_users.json``. It defines the roster of artists available for assignment across all projects:

.. code-block:: json

   {
     "users": [
       "Stephen Studyvin",
       "Jane Lead",
       "Alex Animator",
       "Sam TD"
     ]
   }

Per-Project User Assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating or editing a project in the Project Manager, you can filter which artists from the global list are assigned to that specific production. The project manifest (``.openpypeline/project.json``) records only the participating team members, ensuring that user dropdowns in the UI remain uncluttered.

Localization & String Customization
-----------------------------------

All user-interface text, button labels, error alerts, and dialog titles are centralized in language dictionaries under ``openpypeline/resources/lang/``.

Customizing English Nomenclature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your studio prefers alternative terms (such as calling *WIPs* "Working Files" or *Masters* "Publishes"), you can customize values in ``openpypeline/resources/lang/en.json``:

.. code-block:: json

   {
     "btn_newProject": "Create New Project...",
     "btn_joinProject": "Join Existing Project...",
     "lbl_workshop": "Working File (WIP)",
     "lbl_master": "Production Master"
   }

Adding New Languages
~~~~~~~~~~~~~~~~~~~~

To localize openPypeline Studio for international teams (e.g., Spanish, French, Japanese):
1. Duplicate ``openpypeline/resources/lang/en.json``.
2. Name the new file with its two-letter language code (e.g., ``es.json``, ``fr.json``, ``ja.json``).
3. Translate the string values.
4. Set the preferred language code in ``~/.openpypeline/user_prefs.json``:

   .. code-block:: json

      {
        "ops_language": "es"
      }

See Also
--------

* :doc:`configuration`: Detailed technical specifications for project manifests and user preferences.
* :doc:`production_workflows/index`: Detailed production guidelines for WIPs, Masters, and advisory locking.
* :doc:`perforce_setup`: Setting up cloud version control for distributed remote teams.
