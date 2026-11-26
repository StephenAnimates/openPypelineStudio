"""Project creation and editing dialog view for openPypeline Studio in Maya.

Provides :class:`opsProjDialogGUI`, a Maya-parented subclass of :class:`~openpypeline.ui.ops_proj_dialog_gui.OpsProjDialogGUI` for configuring new studio projects or modifying existing project metadata, directory structures, naming conventions, file formats, and assigned user rosters.

:File: ops_proj_dialog_gui.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from typing import Optional

try:
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
except ImportError:

    class MayaQWidgetBaseMixin:  # type: ignore[no-redef]
        """Fallback mixin stub when running outside Autodesk Maya."""

from PySide6 import QtWidgets

from openpypeline.ui.ops_proj_dialog_gui import OpsProjDialogGUI


class opsProjDialogGUI(MayaQWidgetBaseMixin, OpsProjDialogGUI):
    """Maya-parented PySide6 window class for creating or editing a studio project.

    Extends :class:`~openpypeline.ui.ops_proj_dialog_gui.OpsProjDialogGUI` with
    Maya window parenting via :class:`MayaQWidgetBaseMixin`.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the Maya-parented Project Dialog window.

        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(parent=parent)
