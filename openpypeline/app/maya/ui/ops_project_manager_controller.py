"""Maya-specific controller subclass for the openPypeline Studio Project Manager.

Extends :class:`~openpypeline.ui.ops_project_manager_controller.OpsProjectManagerController` with Maya's :class:`~openpypeline.app.maya.ui.ops_project_manager_gui.opsProjectManagerGUI` view, active Maya workspace directory defaults, and Maya's :func:`~openpypeline.app.maya.core.ops_loader.openPypelineSetup` launcher.

:File: ops_project_manager_controller.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import importlib
from typing import Any

from openpypeline.app.maya.core import ops_loader as opsLoader
from openpypeline.ui.ops_project_manager_controller import (
    OpsProjectManagerController as BaseOpsProjectManagerController,
)

from .ops_project_manager_gui import opsProjectManagerGUI


class OpsProjectManagerController(BaseOpsProjectManagerController):
    """Maya host controller connecting :class:`opsProjectManagerGUI` to project services."""

    def _create_view(self) -> opsProjectManagerGUI:
        """Instantiate and return the Maya-parented Project Manager view.

        :returns: Maya-parented :class:`opsProjectManagerGUI` widget instance.
        """
        return opsProjectManagerGUI()

    def _resolve_script_location(self) -> str:
        """Return Maya loader's resolved openPypeline root path.

        :returns: Root path tracked by :mod:`openpypeline.app.maya.core.ops_loader`.
        """
        return opsLoader._root_path

    def _get_default_join_path(self) -> str:
        """Return Maya's active workspace root directory when available.

        :returns: Active Maya project directory or the configured registry path.
        """
        start_path = ""
        try:
            import maya.cmds as cmds

            start_path = cmds.workspace(q=True, rootDirectory=True) or ""
        except Exception:
            pass
        return start_path or super()._get_default_join_path()

    def _create_proj_dialog_controller(self) -> Any:
        """Lazily import, hot-reload, and instantiate Maya's Project Dialog controller.

        :returns: :class:`~openpypeline.app.maya.ui.ops_proj_dialog_controller.OpsProjDialogController`
            instance.
        """
        from . import ops_proj_dialog_controller

        importlib.reload(ops_proj_dialog_controller)
        return ops_proj_dialog_controller.OpsProjDialogController()

    def on_edit_locations(self, *args: Any) -> None:
        """Open Maya's setup dialog for project and script locations.

        Delegates to :func:`~openpypeline.app.maya.core.ops_loader.openPypelineSetup`.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        opsLoader.openPypelineSetup()
