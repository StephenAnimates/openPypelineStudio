"""Maya-specific controller subclass for the openPypeline Studio Project Dialog.

Extends :class:`~openpypeline.ui.ops_proj_dialog_controller.OpsProjDialogController` with the Maya-parented :class:`~openpypeline.app.maya.ui.ops_proj_dialog_gui.opsProjDialogGUI` view and automatic population of project paths and subfolder rules from the active Maya workspace.

:File: ops_proj_dialog_controller.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import os

from openpypeline.ui.ops_proj_dialog_controller import (
    OpsProjDialogController as BaseOpsProjDialogController,
)

from .ops_proj_dialog_gui import opsProjDialogGUI


class OpsProjDialogController(BaseOpsProjDialogController):
    """Maya host controller connecting :class:`opsProjDialogGUI` to pipeline services."""

    def _create_view(self) -> opsProjDialogGUI:
        """Instantiate and return the Maya project dialog view.

        :returns: Maya-parented :class:`opsProjDialogGUI` dialog instance.
        """
        return opsProjDialogGUI()

    def _populate_from_host(self) -> None:
        """Populate project and subfolder fields from the current Maya workspace."""
        try:
            import maya.cmds as cmds

            proj_dir = cmds.workspace(query=True, rootDirectory=True)
            if proj_dir:
                clean_dir = proj_dir.replace("\\", "/").rstrip("/")
                self.view.proj_path_field.setText(clean_dir)

                proj_name = os.path.basename(clean_dir)
                if proj_name:
                    self.view.proj_name_field.setText(proj_name)

            scene_dir = cmds.workspace(fileRuleEntry="scene")
            if scene_dir:
                self.view.shot_lib_field.setText(scene_dir)
                self.view.asset_lib_field.setText(f"{scene_dir}/assets")

            images_dir = cmds.workspace(fileRuleEntry="images")
            if images_dir:
                self.view.renders_field.setText(f"{images_dir}/renders")

            source_images_dir = cmds.workspace(fileRuleEntry="sourceImages")
            if source_images_dir:
                self.view.textures_field.setText(source_images_dir)

            scripts_dir = cmds.workspace(fileRuleEntry="scripts")
            if scripts_dir:
                self.view.scripts_field.setText(scripts_dir)

            particles_dir = cmds.workspace(fileRuleEntry="particles")
            if particles_dir:
                self.view.particles_field.setText(particles_dir)
        except ImportError:
            pass
