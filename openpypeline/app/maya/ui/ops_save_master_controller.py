"""Maya-specific controller subclass for the openPypeline Studio Save Master dialog.

Extends :class:`~openpypeline.ui.ops_save_master_controller.OpsSaveMasterController` with the Maya-parented :class:`~openpypeline.app.maya.ui.ops_save_master_gui.opsSaveMasterGUI` view.

:File: ops_save_master_controller.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from openpypeline.ui.ops_save_master_controller import (
    OpsSaveMasterController as BaseOpsSaveMasterController,
)
from openpypeline.ui.ops_save_master_controller import TaskFetcher

from .ops_save_master_gui import opsSaveMasterGUI

__all__ = ["OpsSaveMasterController", "TaskFetcher"]


class OpsSaveMasterController(BaseOpsSaveMasterController):
    """Maya host controller connecting :class:`opsSaveMasterGUI` to master publishing."""

    def _create_view(self) -> opsSaveMasterGUI:
        """Instantiate and return the Maya-parented Save Master dialog view.

        :returns: Maya-parented :class:`opsSaveMasterGUI` widget instance.
        """
        return opsSaveMasterGUI()
