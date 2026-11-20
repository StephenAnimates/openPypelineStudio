"""Global Preferences and Settings UI for openPypeline Studio in Maya.

Provides :class:`opsSettingsGUI`, a Maya-parented subclass of :class:`~openpypeline.ui.ops_settings_gui.OpsSettingsGUI` using :class:`~maya.app.general.mayaMixin.MayaQWidgetBaseMixin`.

:File: ops_settings_gui.py
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

from openpypeline.ui.ops_settings_gui import OpsSettingsGUI


class opsSettingsGUI(MayaQWidgetBaseMixin, OpsSettingsGUI):
    """Maya window class for managing global openPypeline Studio settings.

    Inherits all localization, pipeline default, and production tracking controls from :class:`~openpypeline.ui.ops_settings_gui.OpsSettingsGUI` while binding the window lifecycle to Maya's main window via :class:`~maya.app.general.mayaMixin.MayaQWidgetBaseMixin`.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the Maya-parented settings dialog.

        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(parent=parent)
