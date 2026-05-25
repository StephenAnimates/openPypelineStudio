Welcome to openPypeline Studio's documentation!
===============================================

openPypeline Studio is an open-source framework for managing animation production data and workflows. 

Originally developed as a MEL-based plug-in by Kickstand, **openPypeline Studio** has been completely modernized and refactored into **Python 3** to natively support modern Autodesk Maya environments (Maya 2026+) and acts as a foundation for a DCC-agnostic pipeline. It handles specific, critical aspects of production: automatic directory structures, file naming conventions, revision control, and modularity that makes multi-artist workflows seamless.

Key Features
------------

* **Automated Directory Structures:** Ensures all project files are strictly organized and standardized across your team.
* **Strict Naming Conventions:** Eliminates messy file names; the framework handles naming and versioning automatically.
* **Revision Control:** Built-in system for managing ``Workshop`` (work-in-progress) and ``Master`` (approved) files.
* **Asset & Shot Browsers:** Dedicated UI tabs for managing Assets, Sequences, Shots, and their respective components.
* **Playblast & Notes Management:** Integrated tools for taking snapshots, recording playblasts, and leaving notes for artists.
* **Modern Python API:** Extensible and fully accessible via Python 3.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`