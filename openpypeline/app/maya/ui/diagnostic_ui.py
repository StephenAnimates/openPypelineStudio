"""Maya-parented developer diagnostic tool subclass for openPypeline Studio.

Extends :class:`~openpypeline.ui.diagnostic_ui.DiagnosticUI` with Maya window parenting via ``MayaQWidgetBaseMixin`` and hot-reloading of Maya-specific UI controllers and loader modules.

:File: diagnostic_ui.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import importlib
from typing import Optional

try:
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
except ImportError:

    class MayaQWidgetBaseMixin:  # type: ignore[no-redef]
        """Fallback mixin stub when running outside Autodesk Maya."""


from PySide6 import QtWidgets

from openpypeline.app.maya.core import ops_loader as opsLoader
from openpypeline.ui.diagnostic_ui import DiagnosticUI

from . import ops_main_controller as opsMainController
from . import ops_main_ui as opsMainUI
from . import ops_proj_dialog_controller as opsProjDialogController
from . import ops_project_manager_controller as opsProjectManagerController
from . import ops_save_master_controller as opsSaveMasterController


class diagnosticUI(MayaQWidgetBaseMixin, DiagnosticUI):
    """Maya-parented developer dashboard for launching and inspecting GUIs."""

    def __init__(
        self,
        filePath: Optional[str] = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        """Initialize the Maya-parented diagnostic window.

        :param filePath: Optional scene or diagnostic path context.
        :param parent: Optional parent widget for Maya window parenting.
        """
        super().__init__(filePath=filePath, parent=parent)

    def _reload_modules(self) -> None:
        """Hot-reload core, shared, and Maya-specific UI and loader modules."""
        super()._reload_modules()
        for module in (
            opsSaveMasterController,
            opsProjectManagerController,
            opsProjDialogController,
            opsMainUI,
            opsMainController,
            opsLoader,
        ):
            importlib.reload(module)

    def _instantiate_controllers(self) -> None:
        """Instantiate Maya UI controllers and bind them to :attr:`UIObjects`."""
        self.UIObjects.opsMainController = opsMainController.OpsMainController()
        self.UIObjects.opsMainUI = self.UIObjects.opsMainController.view
        self.UIObjects.opsSaveMasterController = (
            opsSaveMasterController.OpsSaveMasterController()
        )
        self.UIObjects.opsProjectManagerController = (
            opsProjectManagerController.OpsProjectManagerController()
        )
        self.UIObjects.opsProjDialogController = (
            opsProjDialogController.OpsProjDialogController()
        )
