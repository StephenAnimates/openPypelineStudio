"""Maya-specific Project Manager UI view subclass for openPypeline Studio.

Extends :class:`~openpypeline.ui.ops_project_manager_gui.OpsProjectManagerGUI` with Maya window parenting, ``workspaceControl`` cleanup/restoration, and Maya's :func:`~openpypeline.app.maya.core.ops_loader.openPypelineSetup` launcher.

:File: ops_project_manager_gui.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from typing import Any, Optional

try:
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
except ImportError:

    class MayaQWidgetBaseMixin:  # type: ignore[no-redef]
        """Fallback mixin stub when running outside Autodesk Maya."""


from PySide6 import QtWidgets

from openpypeline.app.maya.core import ops_loader as opsLoader
from openpypeline.ui.ops_project_manager_gui import OpsProjectManagerGUI


class opsProjectManagerGUI(MayaQWidgetBaseMixin, OpsProjectManagerGUI):
    """Maya-parented PySide6 window for managing openPypeline Studio projects."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the Maya-parented project manager window.

        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(parent=parent)

    def _pre_ui_setup(self) -> None:
        """Remove any orphaned Maya ``workspaceControl`` before building widgets."""
        try:
            import maya.cmds as cmds

            workspace_control = self.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.deleteUI(workspace_control)
        except ImportError:
            pass

    def _resolve_script_location(self) -> str:
        """Return Maya loader's resolved openPypeline root path.

        :returns: Root path tracked by :mod:`openpypeline.app.maya.core.ops_loader`.
        """
        return opsLoader._root_path

    def showWindow(self) -> None:
        """Show the window, restoring any existing Maya ``workspaceControl``."""
        try:
            import maya.cmds as cmds

            workspace_control = self.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(workspace_control, edit=True, restore=True)
                return
        except ImportError:
            pass

        self.show()

    def on_edit_locations(self, *args: Any) -> None:
        """Launch Maya's Setup UI to change the script or project paths.

        Delegates to :func:`~openpypeline.app.maya.core.ops_loader.openPypelineSetup`.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        opsLoader.openPypelineSetup()
