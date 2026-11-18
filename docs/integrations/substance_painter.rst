Adobe Substance 3D Painter Integration
======================================

Adobe Substance 3D Painter is a primary focus area on the openPypeline Studio roadmap. As the industry standard for 3D texturing and PBR material authoring, Substance 3D Painter bridges geometry authoring in Maya, Houdini, and ZBrush with downstream look development and game engine deployment in Unity.

Support Status & Target Specifications
--------------------------------------

* **Status:** Planned Priority (Roadmap Phase 4)
* **Target Versions:** Adobe Substance 3D Painter 9.x, 10.x+
* **Integration Archetype:** Native In-Process Python (Archetype 1)
* **Internal Python Module:** ``substance_painter``
* **Module Path:** ``openpypeline/app/substance_painter/``

Role in the Production Pipeline
-------------------------------

In a typical openPypeline production pipeline, Substance 3D Painter occupies the texturing and surface look development phase:

1. **Upstream Ingestion:** Substance Painter ingests clean geometry (OBJ, FBX, USD, or Alembic) published as a Master from the modeling/sculpting department (e.g., Maya or ZBrush).
2. **Texturing & Iteration:** Texture artists paint materials, bake mesh maps, and save incremented project files (``.spp``) directly within the asset's component folder.
3. **Downstream Publishing:** Approved textures are exported directly to the project's configured ``sourceimages/`` or textures directory, ready for automatic pickup by Maya Arnold shaders, Houdini Karma materials, or Unity shaders.

Planned Package Architecture
----------------------------

The Substance 3D Painter integration will adhere to openPypeline's standard adapter scaffold:

.. code-block:: text

   openpypeline/app/substance_painter/
   ├── __init__.py
   ├── loader.py             # Registers UI actions in Painter's toolbar
   ├── file/
   │   ├── __init__.py
   │   └── file.py           # Maps substance_painter.project API
   └── ui/
       └── ...               # Custom Painter dockable widget

API Protocol Mapping
--------------------

The adapter will map openPypeline's standard 10-method File Handler Protocol to Painter's native Python API:

.. list-table:: Protocol Mapping in Substance 3D Painter
   :widths: 30 70
   :header-rows: 1

   * - Protocol Method
     - Substance Painter API Implementation
   * - ``open(filepath)``
     - ``substance_painter.project.open(filepath)``
   * - ``save()``
     - ``substance_painter.project.save()``
   * - ``save_as(filepath)``
     - ``substance_painter.project.save_as(filepath, substance_painter.project.ProjectExportOptions.Default)``
   * - ``is_modified()``
     - ``substance_painter.project.needs_saving()``
   * - ``new_file()``
     - Prompts or creates a fresh project using target mesh templates.
   * - ``get_file_type(ext)``
     - Maps ``.spp`` to ``"Substance Painter Project"``.

Planned Texture Publishing Workflows
------------------------------------

Beyond scene file management, the Substance Painter adapter will introduce automated texture set exports:

* **Automated Texture Naming:** Using openPypeline naming tokens (e.g., ``<asset>_<component>_<textureSet>_<channel>.png``).
* **Target Resolution:** Directly routing baked Normal, BaseColor, Roughness, Metallic, and Height maps to the asset's production texture directory.
* **Manifest Generation:** Writing a texture metadata JSON manifest allowing Maya or Unity shader builders to automatically link texture channels without manual re-wiring.
