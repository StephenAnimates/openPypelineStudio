# openPypeline Studio for Maya

openPypeline Studio is an open-source framework for managing animation production data and workflows. 

Originally developed as a MEL-based plug-in by Kickstand, **openPypeline Studio** has been completely modernized and refactored into **Python 3** to natively support modern Autodesk Maya environments (Maya 2026+). It handles specific, critical aspects of production: automatic directory structures, file naming conventions, revision control, and modularity that makes multi-artist workflows seamless.

## ✨ Features
* **Automated Directory Structures:** Ensures all project files are strictly organized and standardized across your team.
* **Strict Naming Conventions:** Eliminates messy file names; the framework handles naming and versioning automatically.
* **Revision Control:** Built-in system for managing `Work-in-Progress` (formerly Workshop) and `Master` (approved) files.
* **Asset & Shot Browsers:** Dedicated UI tabs for managing Assets, Sequences, Shots, and their respective components.
* **Playblast & Notes Management:** Integrated tools for taking snapshots, recording playblasts, and leaving notes for artists.
* **Modern Python API:** Extensible and fully accessible via Python 3.

## 🗺️ Roadmap & Planned Integrations
Expanding openPypeline Studio to be a fully DCC-agnostic, modern pipeline framework. Planned upcoming features include:
* **VFX Reference Platform Standards:** Full support for **OpenUSD** (Universal Scene Description), **OpenColorIO (OCIO)**, **OpenImageIO (OIIO)**, and **Alembic (.abc)**.
* **Production Tracking:** Abstracted API support for major trackers including **Autodesk Flow Production Tracking (ShotGrid)**, **Ftrack**, and **Kitsu**.
* **Expanded DCC Support:**
  * **Substance 3D Suite:** Painter, Designer (Mac/Windows), and Modeler (Windows).
  * **Sculpting:** ZBrush.
  * **Real-time & Game Engines:** Unity and Unreal Engine.
  * **Compositing & FX:** Nuke and Houdini.

## ⚙️ Current Requirements
* **Autodesk Maya 2026** (or newer recommended)
* Python 3.11+ (Native to modern Maya)

## 🚀 Installation & Setup
1. Clone or download this repository to your Maya user scripts directory (e.g., `~/maya/scripts/`) or a common network scripts directory.
2. Open **Autodesk Maya**.
3. Open the **Script Editor** (Python tab).
4. Run the following code to initialize the setup UI, replacing the path with your actual installation directory:

```python
import sys

# Path to the directory containing the 'openpypeline' folder
repo_path = "/path/to/openPypeline/maya"

if repo_path not in sys.path:
    sys.path.insert(0, repo_path)
    
import opsLoader
opsLoader.openPypelineSetup()
```
5. Follow the on-screen prompts to define your Script Path and Project Path.

## 📖 Usage
Once installed and configured, you can launch the main UI at any time using:
```python
import opsLoader
opsLoader.openPypeline()
```
*(Tip: Highlight the snippet above and drag it to a Maya shelf to create a quick-launch button!)*

## ⚖️ License & Attribution
**Original Framework:** openPipeline by Kickstand  
**Original Summary:** openPipeline is a framework for animation production. The initial iteration is a plugin for Autodesk Maya. This framework handles file naming, revision control, collaborative notation and scene referencing.  
**Last Update:** 2013-04-22  
**License:** Common Public License 1.0 (See `LICENSE.md` file for details)  
