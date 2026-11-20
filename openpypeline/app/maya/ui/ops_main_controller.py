"""Maya-specific controller subclass for the main openPypeline Studio UI.

Extends :class:`~openpypeline.ui.ops_main_controller.OpsMainController` with the Maya workspace-dockable :class:`~openpypeline.app.maya.ui.ops_main_ui.opsMainUI` view, Maya add-on discovery, Maya Scene Inventory integration, and Maya ``workspaceControl`` sizing.

:File: ops_main_controller.py
:License: Common Public License 1.0 (CPL-1.0)
"""

import importlib
import os
from typing import Any

from openpypeline.core.localization import localization
from openpypeline.ui.ops_main_controller import (
    OpsMainController as BaseOpsMainController,
)

from .ops_main_ui import opsMainUI


class OpsMainController(BaseOpsMainController):
    """Maya host controller connecting :class:`opsMainUI` to pipeline services."""

    def _create_view(self) -> opsMainUI:
        """Instantiate and return the Maya dockable main UI view.

        :returns: Maya dockable :class:`opsMainUI` window instance.
        """
        return opsMainUI()

    def _get_dcc_addon_specs(self) -> list[tuple[str, str, str]]:
        """Return Maya's add-on directory specification for Tools menu loading.

        :returns: Single-element list describing ``openpypeline.app.maya.core.addons``.
        """
        maya_addons_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "core", "addons")
        ).replace("\\", "/")
        return [
            (
                maya_addons_dir,
                localization.get_string("menu_dccAddons"),
                "openpypeline.app.maya.core.addons",
            )
        ]

    def _create_project_manager_controller(self) -> Any:
        """Lazily import, hot-reload, and instantiate Maya's Project Manager controller.

        :returns: :class:`~openpypeline.app.maya.ui.ops_project_manager_controller.OpsProjectManagerController` instance.
        """
        from . import ops_project_manager_controller as opsProjectManagerController

        importlib.reload(opsProjectManagerController)
        return opsProjectManagerController.OpsProjectManagerController()

    def _create_settings_controller(self) -> Any:
        """Lazily import, hot-reload, and instantiate Maya's Global Settings controller.

        :returns: :class:`~openpypeline.app.maya.ui.ops_settings_controller.OpsSettingsController` instance.
        """
        from . import ops_settings_controller as opsSettingsController

        importlib.reload(opsSettingsController)
        return opsSettingsController.OpsSettingsController()

    def on_open_scene_inventory(self, *args: Any) -> None:
        """Launch the Maya Scene Inventory window.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        try:
            from openpypeline.app.maya.core import ops_scene_inv as opsSceneInv

            opsSceneInv.show_window()
        except ImportError:
            print(localization.get_string("msg_sceneInvNotAvailable"))

    def on_reset_window_size(self, *args: Any) -> None:
        """Reset the Main UI window and Maya ``workspaceControl`` to ``450x780``.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        super().on_reset_window_size(*args)
        try:
            import maya.cmds as cmds

            workspace_control = self.view.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(
                    workspace_control, edit=True, resizeWidth=450, resizeHeight=780
                )
        except ImportError:
            pass
