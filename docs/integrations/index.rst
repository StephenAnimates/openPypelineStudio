Host Integrations & Support
===========================

openPypeline Studio (OPS) is designed to unify multi-application studio pipelines. While core project configuration, versioning rules, and advisory concurrency are host-neutral, openPypeline provides application-specific integrations to interface natively with each Digital Content Creation (DCC) tool.

This page outlines the current support status, implemented capabilities, and target roadmap across all supported, in-development, and planned creative applications.

Support Status & Capability Matrix
----------------------------------

.. important::

   **Host Detection vs. Support Status:** A host being detected dynamically by ``OpsEngine``, or the presence of a file-handler module under ``openpypeline/app/<host>/``, does not necessarily mean that the full openPypeline workflow is implemented, tested, or supported for that software. Check the capability matrix below before deploying an integration into production.

.. csv-table:: Supported Software Integrations and Current Status
   :class: wrap-table
   :width: 100%
   :stub-columns: 1
   :header-rows: 1
   :widths: 18 20 38 24
   :file: ../supported_software_integrations.csv

Application Guides
------------------

.. toctree::
   :maxdepth: 2
   :caption: Host Application Guides

   maya
   houdini
   nuke
   substance_painter
   zbrush
   unity

Integration Categories
----------------------

Supported (Production Reference)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **:doc:`maya`:** Autodesk Maya is the reference integration with 100% full feature parity. It includes the complete Qt user interface (Asset/Shot browser, Project Manager), file operations (open, save, save-as, referencing, playblasts, snapshots), automatic plugin verification (USD, Alembic), and advisory concurrency tracking.

In Development (Partial Adapters)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **:doc:`houdini`:** Core file handling operations (opening, saving, WIP increments, merging scenes, clearing, unsaved changes tracking) are implemented. The dockable Houdini Python Panel UI and native HDA management are currently in active development.
* **:doc:`nuke`:** Core script operations (opening, saving, WIP increments, node pasting, clearing, unsaved changes tracking) are implemented. Dockable panel integration, LiveGroup referencing, and Write node token resolution are in development.

Planned Priority Integrations (Roadmap Phase 4)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **:doc:`substance_painter`:** In-process Python integration using the ``substance_painter`` module. Manages ``.spp`` projects, mesh ingestion from Maya/ZBrush, and automated PBR texture map export to project ``sourceimages``.
* **:doc:`zbrush`:** Script-bridged integration using dynamically generated ZScript commands and command-line execution. Manages ``.ztl`` and ``.zpr`` files and stages decimation/cage meshes for texturing.
* **:doc:`unity`:** Real-time engine integration via Python for Unity or a C# Editor Package. Manages ``.unity`` scenes, prefabs, automated DCC mesh/texture re-importing, and advisory locking.

Standalone & Headless Engine Use
--------------------------------

The openPypeline Studio engine (``OpsEngine``) and core domain logic can be imported and executed inside standard, headless Python 3.9+ environments (e.g., terminal scripts, automated CI/CD runners, and batch farm nodes). 

In standalone mode, no DCC file handler is attached, but all file-neutral operations—such as querying project topologies, calculating WIP version increments, validating naming tokens, and inspecting advisory file locks—are fully functional. Scene operations that require host SDKs (such as evaluating references or executing scene saves) require a supported host runtime.

How Support Status Changes
--------------------------

Before a host integration is officially declared **Supported**:

1. **Tested Environment:** Documented support for specific, tested application and Python versions.
2. **Interactive Validation:** Comprehensive validation of real-world artist workflows inside the host application itself (opening, saving, referencing, publishing, and advisory lock notifications).
3. **Automated Test Doubles:** Protocol compliance tests must pass headlessly in ``openpypeline/test_host_adapters.py``.
4. **User & Developer Documentation:** Complete setup instructions and workflow guidelines published in this documentation.

Developer Resources
-------------------

To build, extend, or test an adapter for an additional creative application:

* :doc:`/architecture`: Overview of the multi-tier engine, host adapter patterns, and core data models.
* :doc:`/authoring_host_integrations`: Step-by-step developer guide with copy-paste scaffolds for ``loader.py``, ``file/file.py``, and mock unit tests.
