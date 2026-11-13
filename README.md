# openPypeline Studio

openPypeline Studio is a locally installed, open-source framework for managing animation and other creative-production data and workflows, with a focus on helping independent studios collaborate remotely. Teams can keep project files in folders synchronized by services they already use, while openPypeline provides shared pipeline tools and application integrations.

Originally developed as a MEL-based Autodesk Maya plug-in by Kickstand called OpenPipeline, the project has been redesigned and rebadged as **openPypeline Studio**, then modernized in **Python 3**. Maya remains the first supported host, while the project is moving toward a host-neutral core and modular adapters for additional software. The shared core focuses on production needs such as directory structures, file naming, versioning, and workflow data; host-specific modules provide application-aware behavior and UI.

**Project documentation:** [Read the documentation](https://stephenanimates.github.io/openPypelineStudio/).

## ✨ Features
* **Automated Directory Structures:** Ensures all project files are strictly organized and standardized across your team.
* **Strict Naming Conventions:** Eliminates messy file names; the framework handles naming and versioning automatically.
* **Revision Control:** Built-in system for managing `Work-in-Progress` (formerly Workshop) and `Master` (approved) files.
* **Asset & Shot Browsers:** Dedicated UI tabs for managing Assets, Sequences, Shots, and their respective components.
* **Playblast & Notes Management:** Integrated tools for taking snapshots, recording playblasts, and leaving notes for artists.
* **Dynamic Add-on System:** Drop custom Python scripts into the `addons` folder to automatically expose them in the UI without modifying core code.
* **Modern Python API:** Extensible and fully accessible via Python 3.

## 🗺️ Project Direction & Roadmap
The project is evolving from a Maya-first tool into a modular pipeline framework for multiple creative applications and remote teams. The intended architecture keeps shared pipeline concepts in the core and puts host-specific operations behind separate integrations. openPypeline runs locally and works with project folders that teams keep synchronized through services such as Google Drive, iCloud Drive, OneDrive, or Dropbox.

Maya is the initial integration; support for other applications is planned and should not be assumed complete until documented and tested. The initial Maya file-use feature writes advisory notices under `.openpypeline/file_use` in the active project folder, warns when a scene has another session's notice, and asks for confirmation before saving when a notice exists or the on-disk file size or modification time changed. The sync client remains responsible for synchronization. Since its updates may be delayed or preserve file timestamps, these notices and checks cannot guarantee that simultaneous edits or overwrites are prevented. For a detailed, step-by-step checklist of progress, see the [Project Roadmap](ROADMAP.md).

Planned upcoming features include:
* **VFX Reference Platform Standards:** Full support for **OpenUSD** (Universal Scene Description), **OpenColorIO (OCIO)**, **OpenImageIO (OIIO)**, and **Alembic (.abc)**.
* **Production Tracking:** Abstracted API support for major trackers including **Autodesk Flow Production Tracking (ShotGrid)**, **Ftrack**, and **Kitsu**.
* **Expanded DCC Support:**
  * **Substance 3D Suite:** Painter, Designer (Mac/Windows), and Modeler (Windows).
  * **Sculpting:** ZBrush.
  * **Real-time & Game Engines:** Unity and Unreal Engine.
  * **Compositing & FX:** Nuke and Houdini.

## ⚙️ Requirements
* Python 3.11+ for the shared project code.
* Autodesk Maya 2026 or newer for the current Maya integration. Other host integrations may have their own requirements as they are developed.

## 🚀 Maya Installation & Setup
The instructions below set up the current Maya integration.

1. Download `openPypelineStudio.zip` from the nightly GitHub release and extract it into your Maya scripts directory. It creates an `openPypelineStudio` folder. If you clone the repository instead, name the checkout folder `openPypelineStudio`. Use the location that matches your operating system:
   - macOS: `~/maya/scripts/` or `/Users/Shared/Autodesk/maya/scripts`
   - Windows: `%USERPROFILE%\maya\scripts\` or `C:\Users\YourName\maya\scripts`
2. Open **Autodesk Maya**.
3. Open the **Script Editor** (Python tab).
4. Run the following code to initialize the setup UI, replacing the path with your actual installation directory. Use the example that matches your OS:

```python
import sys

# macOS example
ops_install_path = "/Users/Shared/Autodesk/maya/scripts/openPypelineStudio"

# Windows example
# ops_install_path = r"C:\Users\YourName\maya\scripts\openPypelineStudio"

if ops_install_path not in sys.path:
    sys.path.insert(0, ops_install_path)

from openpypeline.app.maya.core import ops_loader
ops_loader.openPypelineSetup()
```
5. Follow the on-screen prompts to define your Script Path and Project Path.

For maintainer instructions on publishing nightly releases, see [Contributing](CONTRIBUTING.md).

## 📖 Maya Usage
Once installed and configured, you can launch the main UI at any time using:
```python
from openpypeline.app.maya.core import ops_loader
ops_loader.openPypeline()
```
*(Tip: Highlight the snippet above and drag it to a Maya shelf to create a quick-launch button!)*

## ♻️ Upgrading from Legacy openPipeline
If you are upgrading from the original **openPipeline 1.0** or an earlier alpha version of openPypeline Studio that used XML databases, you can automatically migrate your projects to the new JSON-based backend without any data loss!

1. Launch openPypeline Studio.
2. Navigate to the top menu: **Tools** > **Add-ons**.
3. Click **Migrate Legacy XML Data** to convert your `openPipeline_projects.xml` and user databases.
4. Click **Migrate Legacy Notes** to safely translate all of your item history and custom notes into the modern format.

## ⚖️ License & Attribution
**Original Framework:** openPipeline by Kickstand  
**Original Summary:** openPipeline is a framework for animation production. The initial iteration is a plugin for Autodesk Maya. This framework handles file naming, revision control, collaborative notation and scene referencing.  
**Last Update:** 2013-04-22  
**License:** Common Public License 1.0 (See `LICENSE.md` file for details)  
