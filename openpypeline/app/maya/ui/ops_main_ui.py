"""Main openPypeline Studio UI view for Autodesk Maya.

Defines :class:`opsMainUI`, a Maya workspace-dockable subclass of :class:`~openpypeline.ui.ops_main_ui.OpsMainUI` that integrates Maya's ``workspaceControl`` docking lifecycle and Maya-specific Tools menu items.

:File: ops_main_ui.py
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Optional

try:
    from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
except ImportError:

    class MayaQWidgetDockableMixin:  # type: ignore[no-redef]
        """Fallback mixin stub when running outside Autodesk Maya."""


from PySide6 import QtWidgets

from openpypeline.core.localization import localization
from openpypeline.ui.ops_main_ui import OpsMainUI

class opsMainUI(MayaQWidgetDockableMixin, OpsMainUI):
    """Build the Maya workspace-dockable main window for openPypeline Studio.

    Extends :class:`~openpypeline.ui.ops_main_ui.OpsMainUI` with Maya ``workspaceControl`` cleanup and restoration as well as Maya Reference Editor and Project Window menu shortcuts.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the Maya dockable main window.

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

    def _populate_host_tools_menu(self, menu_tools: QtWidgets.QMenu) -> None:
        """Append Maya-specific Reference Editor and Project Window actions.

        :param menu_tools: Top-level Tools :class:`~PySide6.QtWidgets.QMenu`.
        """
        try:
            import maya.mel as mel

            menu_tools.addSection(localization.get_string("menu_mayaTools"))
            menu_tools.addAction(
                localization.get_string("menu_mayaReferenceEditor"),
                lambda: mel.eval("ReferenceEditor;"),
            )
            menu_tools.addAction(
                localization.get_string("menu_mayaProjectWindow"),
                lambda: mel.eval("ProjectWindow;"),
            )
        except ImportError:
            pass

    def showWindow(self) -> None:
        """Show the window as a dockable panel, restoring any existing workspace control."""
        try:
            import maya.cmds as cmds

            workspace_control = self.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(workspace_control, edit=True, restore=True)
                return
        except ImportError:
            pass

        self.show(dockable=True, floating=True)
