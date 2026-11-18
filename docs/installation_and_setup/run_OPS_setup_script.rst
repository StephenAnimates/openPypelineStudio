Run the openPypeline Studio setup script in Maya
================================================
To install openPypeline Studio (OPS) in Maya, you need to run the setup script to configure the Python path and project registry location. This is a one-time setup step for each artist's computer.

1. Open the **Script Editor** window (:menuselection:`Windows` > :menuselection:`General Editors` > :menuselection:`Script Editor`).
2. Open a new Python tab (:menuselection:`Tabs` > :menuselection:`New Tab` then choose **Python** from the :guilabel:`Source Type` window)
3. Copy the following setup python code.

.. code-block:: python

   import sys

   # macOS example - the path to the directory containing the downloaded openpypeline package
   ops_install_path = "/Users/Shared/Autodesk/maya/scripts/openPypelineStudio"

   # Windows example - the path to the directory containing the downloaded openpypeline
   # package (uncomment the line below and comment out the macOS example above)
   # ops_install_path = r"C:\Users\YourName\maya\scripts\openPypelineStudio"

   if ops_install_path not in sys.path:
       sys.path.insert(0, ops_install_path)

   from openpypeline.app.maya.core import ops_loader
   ops_loader.openPypelineSetup()

4. Change the path in the code for your operating system and replace it with your actual install location. The path must point to the directory containing the downloaded ``openpypeline`` package.
5. Execute the code (:menuselection:`Command` > :menuselection:`Execute` or press :kbd:`Ctrl` + :kbd:`Enter` on Windows or :kbd:`Cmd` + :kbd:`Enter` on macOS).

.. tip::

   On Windows, always prefix your path with an ``r`` (e.g., ``r"C:\Users\..."``) or use forward slashes (``"C:/Users/..."``) so Python does not misinterpret backslashes as escape characters.

This will add the openPypeline package to your Python path and open the **openPypeline Studio Setup** window.

* **Default configuration:** The project file path is prefilled with the default location. For standard installations, simply click :guilabel:`Accept` to complete setup and launch the main openPypeline Studio UI.
* **Advanced customization:** If you need to customize where the project registry (``openpypeline_projects.json``) is stored:
  - Click the :guilabel:`Edit` button to unlock the field.
  - Click the :guilabel:`Browse...` button to choose a custom directory.
  - Click the :guilabel:`Default` button at any time to restore the prefilled default path.

.. figure:: /images/openPypelineStudio_Setup_window.png
   :alt: openPypeline Studio Setup window showing the default project registry path
   :width: 80%
   :align: center

   The openPypeline Studio Setup window showing the default project registry path.

6. Click the :guilabel:`Accept` button to save the configuration and launch openPypeline Studio.
7. Close the **Script Editor** window.

Next Steps
----------
After running the setup script, you can create or join an OPS project in Maya. See :doc:`create_join_ops_project_maya` for instructions, or click the **Next** button.