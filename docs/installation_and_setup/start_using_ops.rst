Start Using openPypeline Studio
================================

Once openPypeline Studio is installed and your initial project is configured, you do not need to run the setup script again. 

Daily Launch Shortcut
---------------------

Launch the main openPypeline Studio user interface at any time by running:

.. code-block:: python

   from openpypeline.app.maya import loader
   loader.openPypeline()

.. tip::

   **Create a Maya Shelf Button:** Highlight the Python snippet above in Maya's Script Editor and drag it with the :kbd:`MMB` (Middle Mouse Button)  to your active Maya shelf tab to create a convenient single-click launch button!

Where to Go Next
----------------

Now that your project environment is running:

* **Learn Production Workflows:** Explore :doc:`/production_workflows/index` for a complete walkthrough of daily WIP iteration, non-destructive Master publishing, and parallel component workflows.
* **Explore Host Integrations:** See :doc:`/integrations/index` for application-specific guides covering Maya, Houdini, Nuke, Adobe Substance 3D Painter, Maxon ZBrush, and Unity.
* **Pipeline Administration:** If you are a technical director or project lead, see :doc:`/configuration` and :doc:`/customization` to tailor naming tokens, directory structures, and user rosters.
