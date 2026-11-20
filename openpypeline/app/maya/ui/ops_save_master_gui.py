"""Maya-specific UI view subclass for publishing production master files.

Extends :class:`~openpypeline.ui.ops_save_master_gui.OpsSaveMasterGUI` with Maya window parenting via ``MayaQWidgetBaseMixin``.

:File: ops_save_master_gui.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Optional

try:
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
except ImportError:

    class MayaQWidgetBaseMixin:  # type: ignore[no-redef]
        """Fallback mixin stub when running outside Autodesk Maya."""


from PySide6 import QtWidgets

from openpypeline.ui.ops_save_master_gui import OpsSaveMasterGUI


class opsSaveMasterGUI(MayaQWidgetBaseMixin, OpsSaveMasterGUI):
    """Maya-parented Save Master switchboard dialog."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the Maya-parented master-save dialog.

        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(parent=parent)
