"""Maya-specific controller subclass for the openPypeline Studio Global Settings dialog.

Extends :class:`~openpypeline.ui.ops_settings_controller.OpsSettingsController` to instantiate the Maya-parented :class:`~openpypeline.app.maya.ui.ops_settings_gui.opsSettingsGUI` view.

:File: ops_settings_controller.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from openpypeline.ui.ops_settings_controller import (
    OpsSettingsController as BaseOpsSettingsController,
)

from .ops_settings_gui import opsSettingsGUI


class OpsSettingsController(BaseOpsSettingsController):
    """Maya host controller managing :class:`opsSettingsGUI`."""

    def _create_view(self) -> opsSettingsGUI:
        """Instantiate and return the Maya-parented settings view widget.

        :returns: Maya-parented :class:`opsSettingsGUI` instance.
        """
        return opsSettingsGUI()
