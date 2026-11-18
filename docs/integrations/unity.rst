Unity Integration
=================

Unity is a prioritized target for openPypeline Studio's real-time engine integrations. Designed for game developers, virtual production teams, and real-time interactive experiences, the Unity integration connects openPypeline's versioned creative assets directly into Unity projects.

Support Status & Target Specifications
--------------------------------------

* **Status:** Planned Priority (Roadmap)
* **Target Versions:** Unity 2022 LTS, 2023 LTS, Unity 6+
* **Integration Archetype:** Real-Time Engine & Editor Bridge (Archetype 3)
* **Implementation Options:** *Python for Unity* package or Unity C# Editor Package
* **Module Path:** ``openpypeline/app/unity/``

Role in the Production Pipeline
-------------------------------

In modern real-time workflows, Unity serves as the central assembly and interactive deployment engine:

1. **Asset Ingestion:** Consuming published Masters from upstream DCCs:
   * 3D Meshes and Rigs (FBX, USD) from Autodesk Maya.
   * PBR Textures (BaseColor, Metallic, Roughness, Normal) from Adobe Substance 3D Painter.
2. **Scene Management:** Organizing Unity scene files (``.unity``) and prefabs (``.prefab``) within openPypeline shot and sequence hierarchies.
3. **Automated Re-importing:** When a new model or texture Master is published, the Unity integration triggers automatic asset refreshes and updates prefab variants without breaking scene references.

Integration Approaches
----------------------

openPypeline provides two complementary pathways for Unity connectivity:

1. In-Engine Python (via "Python for Unity")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unity provides an official **Python for Unity** package that embeds Python directly inside the Unity Editor process:

* **Detection:** ``OpsEngine`` detects ``UnityEngine`` and ``UnityEditor`` in ``sys.modules``.
* **Native C# Access:** The Python adapter directly manipulates Unity's C# APIs using the Python/.NET reflection bridge:

  .. code-block:: python

     import UnityEditor.SceneManagement as SceneMgr

     # Open a Unity scene file
     SceneMgr.EditorSceneManager.OpenScene(filepath)

     # Save the active Unity scene
     SceneMgr.EditorSceneManager.SaveOpenScenes()

2. Unity C# Editor Package & IPC Bridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For projects that prefer pure C# editor workflows without embedding Python:

* openPypeline Studio runs as a standalone desktop launcher or companion window.
* A lightweight openPypeline C# package in Unity listens for file events or TCP commands on a local port.
* Artists can browse openPypeline projects directly inside Unity's **Project Window** and inspect WIP/Master status.

Supported File Formats
----------------------

.. list-table:: Unity Supported Formats
   :widths: 20 30 50
   :header-rows: 1

   * - Extension
     - Format Name
     - Description
   * - ``.unity``
     - Unity Scene
     - Level layout, lighting, cameras, and game object hierarchies.
   * - ``.prefab``
     - Unity Prefab
     - Reusable, instanced asset templates combining meshes, shaders, and scripts.
   * - ``.fbx`` / ``.usd``
     - Model Master
     - Upstream geometry imported from Maya or ZBrush.

Advisory Scene Locking in Real-Time Teams
-----------------------------------------

Because Unity scenes are large YAML text files that are notoriously difficult to merge when edited simultaneously, openPypeline's advisory concurrency registry (``file_use.py``) is particularly crucial:

* When a level designer or lighter opens a scene in Unity, openPypeline registers an active heartbeat notice.
* Other team members see real-time notices indicating that the scene is actively checked out, eliminating destructive scene merge conflicts.
