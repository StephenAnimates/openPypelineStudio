"""Controller class for the main openPypeline Studio UI.

Handles signal routing, menu actions, and event coordination between the
:class:`~openpypeline.app.maya.ui.ops_main_ui.opsMainUI` view and the core
:mod:`~openpypeline.core.ops_actions`, :mod:`~openpypeline.core.ops_project`,
and :mod:`~openpypeline.ui.ops_ui_wrappers` backends.

:File: ops_main_controller.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Any, Optional

from PySide6 import QtCore, QtWidgets

from openpypeline.core import ops_actions as opsActions
from openpypeline.core import ops_project as opsProject
from openpypeline.core.localization import localization
from openpypeline.core.models import Level, Tab
from openpypeline.core.util import prefs
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers

from .ops_main_ui import opsMainUI
class OpsMainController:
    """Connect main-window controls to pipeline actions and refresh handlers.

    Instantiates the :class:`~openpypeline.app.maya.ui.ops_main_ui.opsMainUI`
    view, wires Qt signals for asset/shot browsing, scene publishing, and
    context menus to :mod:`~openpypeline.ui.ops_ui_wrappers` and
    :mod:`~openpypeline.core.ops_project`, and populates initial project data.

    :ivar view: Main PySide6 window widget managed by this controller.
    :vartype view: openpypeline.app.maya.ui.ops_main_ui.opsMainUI
    """

    def __init__(self) -> None:
        """Create the main view and initialize its signals and project state."""
        # 1. Instantiate the View (UI)
        self.view = opsMainUI()

        # 2. Connect View signals to Controller methods
        self._connect_signals()

        # 3. Perform initial data population
        self._populate_initial_data()

    def _connect_signals(self) -> None:
        """Connect main-window controls and list selections to their handlers."""
        # Connect buttons and widgets from the View to backend logic
        self.view.ops_projName_optionMenu.currentTextChanged.connect(
            self.on_project_changed
        )
        self.view.ops_refreshUIButton.clicked.connect(opsUIWrappers.refresh_ui)
        self.view.ops_closeUIButton.clicked.connect(self.view.close)

        # Context Menus
        self.view.ops_asset_scrollList.customContextMenuRequested.connect(
            self._asset_context_menu
        )
        self.view.ops_componentScrollList.customContextMenuRequested.connect(
            self._asset_comp_context_menu
        )
        self.view.ops_shotScrollList.customContextMenuRequested.connect(
            self._shot_context_menu
        )
        self.view.ops_shotComponentScrollList.customContextMenuRequested.connect(
            self._shot_comp_context_menu
        )

        # Tab Selection
        self.view.ops_mainTabs_tabLayout.currentChanged.connect(
            opsUIWrappers.update_working_tab
        )

        # Asset Browser List Selections & Actions
        self.view.ops_assetType_txtScrollList.itemSelectionChanged.connect(
            lambda *args: opsUIWrappers.update_asset_list(preserve_selection=0)
        )
        self.view.ops_asset_scrollList.itemSelectionChanged.connect(
            lambda *args: opsUIWrappers.asset_selected(preserve_selection=0)
        )
        self.view.ops_asset_scrollList.itemDoubleClicked.connect(
            lambda *args: opsUIWrappers.open_currently_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "workshop", version_offset=0
            )
        )
        self.view.ops_componentScrollList.itemSelectionChanged.connect(
            opsUIWrappers.component_selected
        )
        self.view.ops_componentScrollList.itemDoubleClicked.connect(
            lambda *args: opsUIWrappers.open_currently_selected(
                Tab.ASSET, Level.COMPONENT, "workshop", version_offset=0
            )
        )

        # Shot Browser List Selections & Actions
        self.view.ops_sequenceScrollList.itemSelectionChanged.connect(
            lambda *args: opsUIWrappers.update_shot_list(preserve_selection=0)
        )
        self.view.ops_shotScrollList.itemSelectionChanged.connect(
            lambda *args: opsUIWrappers.shot_selected(preserve_selection=0)
        )
        self.view.ops_shotScrollList.itemDoubleClicked.connect(
            lambda *args: opsUIWrappers.open_currently_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "workshop", version_offset=0
            )
        )
        self.view.ops_shotComponentScrollList.itemSelectionChanged.connect(
            opsUIWrappers.shot_component_selected
        )
        self.view.ops_shotComponentScrollList.itemDoubleClicked.connect(
            lambda *args: opsUIWrappers.open_currently_selected(
                Tab.SHOT, Level.COMPONENT, "workshop", version_offset=0
            )
        )

        # Currently Open Tab Actions
        self.view.ops_currOpenSaveWorkshop_btn.clicked.connect(
            opsUIWrappers.prompt_save_wip
        )
        self.view.ops_currOpenMaster_btn.clicked.connect(
            self.on_open_master_clicked
        )
        self.view.ops_currOpenRevive_btn.clicked.connect(
            opsUIWrappers.prompt_revive
        )
        self.view.ops_currOpenClose_btn.clicked.connect(
            opsUIWrappers.close_current
        )
        self.view.ops_currOpenSnapshot_btn.clicked.connect(
            opsUIWrappers.take_snapshot
        )
        self.view.ops_currOpenRecordPlayblast_btn.clicked.connect(
            opsUIWrappers.record_current_playblast
        )
        self.view.ops_currOpenViewPlayblast_btn.clicked.connect(
            opsUIWrappers.view_playblast_current
        )
        self.view.ops_currOpenClearNote_btn.clicked.connect(
            opsUIWrappers.clear_note
        )
        self.view.ops_currOpenSaveNote_btn.clicked.connect(
            opsUIWrappers.save_note
        )
        self.view.ops_currOpenExplore_btn.clicked.connect(
            opsUIWrappers.explore_current
        )

        # Asset Browser Buttons
        self.view.ops_assetTypeNew_btn.clicked.connect(
            opsUIWrappers.prompt_new_asset_type
        )
        self.view.ops_assetTypeRemove_btn.clicked.connect(
            lambda *args: opsUIWrappers.remove_process(
                Tab.ASSET, Level.TYPE_OR_SEQUENCE
            )
        )
        self.view.ops_assetNew_btn.clicked.connect(
            opsUIWrappers.prompt_new_asset
        )
        self.view.ops_assetRemove_btn.clicked.connect(
            lambda *args: opsUIWrappers.remove_process(
                Tab.ASSET, Level.ASSET_OR_SHOT
            )
        )
        self.view.ops_assetRename_btn.clicked.connect(
            opsUIWrappers.prompt_rename_asset
        )
        self.view.ops_componentNewButton.clicked.connect(
            opsUIWrappers.prompt_new_asset_component
        )
        self.view.ops_componentRemoveButton.clicked.connect(
            lambda *args: opsUIWrappers.remove_process(
                Tab.ASSET, Level.COMPONENT
            )
        )
        self.view.ops_assetViewPlayblastAssetButton.clicked.connect(
            lambda *args: opsUIWrappers.view_playblast_selected(Tab.ASSET)
        )
        self.view.ops_exploreAssetsButton.clicked.connect(
            lambda *args: opsUIWrappers.explore_selected(Tab.ASSET)
        )

        # Shot Browser Buttons
        self.view.ops_sequenceNewButton.clicked.connect(
            opsUIWrappers.prompt_new_sequence
        )
        self.view.ops_sequenceRemoveButton.clicked.connect(
            lambda *args: opsUIWrappers.remove_process(
                Tab.SHOT, Level.TYPE_OR_SEQUENCE
            )
        )
        self.view.ops_shotNewButton.clicked.connect(
            opsUIWrappers.prompt_new_shot
        )
        self.view.ops_shotRemoveButton.clicked.connect(
            lambda *args: opsUIWrappers.remove_process(
                Tab.SHOT, Level.ASSET_OR_SHOT
            )
        )
        self.view.ops_shotComponentNewButton.clicked.connect(
            opsUIWrappers.prompt_new_shot_component
        )
        self.view.ops_shotComponentRemoveButton.clicked.connect(
            lambda *args: opsUIWrappers.remove_process(
                Tab.SHOT, Level.COMPONENT
            )
        )
        self.view.ops_shotViewPlayblastButton.clicked.connect(
            lambda *args: opsUIWrappers.view_playblast_selected(Tab.SHOT)
        )
        self.view.ops_exploreShotsButton.clicked.connect(
            lambda *args: opsUIWrappers.explore_selected(Tab.SHOT)
        )

        # --- Top Menu: File Actions ---
        self.view.action_save_wip.triggered.connect(opsUIWrappers.prompt_save_wip)
        self.view.action_save_master.triggered.connect(self.on_open_master_clicked)
        self.view.action_close.triggered.connect(self.view.close)

        # --- Top Menu: Project Actions ---
        self.view.action_project_manager.triggered.connect(
            self.on_project_manager_clicked
        )
        self.view.action_edit_users.triggered.connect(opsProject.proj_edit_users)

        # Top Menu Actions
        self.view.action_scene_inventory.triggered.connect(
            self.on_open_scene_inventory
        )
        self.view.action_reset_window_size.triggered.connect(
            self.on_reset_window_size
        )
        self.view.action_preferences.triggered.connect(self.on_open_settings)
        self.view.action_about.triggered.connect(opsUIWrappers.about_dialog)
        self.view.action_help.triggered.connect(opsUIWrappers.launch_help)

        # --- Top Menu: Create Actions ---
        self.view.action_new_asset_type.triggered.connect(
            opsUIWrappers.prompt_new_asset_type
        )
        self.view.action_new_asset.triggered.connect(
            opsUIWrappers.prompt_new_asset
        )
        self.view.action_new_asset_component.triggered.connect(
            opsUIWrappers.prompt_new_asset_component
        )
        self.view.action_new_sequence.triggered.connect(
            opsUIWrappers.prompt_new_sequence
        )
        self.view.action_new_shot.triggered.connect(
            opsUIWrappers.prompt_new_shot
        )
        self.view.action_new_shot_component.triggered.connect(
            opsUIWrappers.prompt_new_shot_component
        )
    def _populate_initial_data(self) -> None:
        """Initialize the main window with project data and available add-ons."""
        self.refresh_project_selector()
        self._load_addons()

    def refresh_project_selector(self) -> None:
        """Populate active local projects and restore the artist's selected project.

        Queries registered projects via
        :func:`~openpypeline.core.ops_project.get_projects_data`, filters out
        inactive projects (``status == "0"``), populates
        ``ops_projName_optionMenu`` without triggering selection signals,
        activates the stored project via
        :func:`~openpypeline.core.ops_actions.activate_project`, and updates
        ``ops_projPath_txtField``.
        """
        projects = [
            project
            for project in opsProject.get_projects_data()
            if str(project.get("status", "1")) != "0"
        ]
        project_names = [
            project.get("name", "") for project in projects if project.get("name")
        ]
        current_name = prefs.get_pref("ops_currProjectName", "")
        if current_name not in project_names:
            current_name = ""
            opsActions.deactivate_project()

        # Block signals while rebuilding the dropdown so currentTextChanged does not fire prematurely
        combo = self.view.ops_projName_optionMenu
        previous_block_state = combo.blockSignals(True)
        combo.clear()
        combo.addItems(project_names)
        if current_name:
            combo.setCurrentText(current_name)
        else:
            combo.setCurrentIndex(-1)
        combo.blockSignals(previous_block_state)

        if current_name:
            try:
                opsActions.activate_project(current_name)
            except opsActions.ProjectActionError as error:
                QtWidgets.QMessageBox.warning(
                    self.view, "Project Unavailable", str(error)
                )
                opsActions.deactivate_project()
                previous_block_state = combo.blockSignals(True)
                combo.setCurrentIndex(-1)
                combo.blockSignals(previous_block_state)
        self.view.ops_projPath_txtField.setText(
            prefs.get_pref("ops_currProjectPath", "")
        )

    def _load_addons(self) -> None:
        """Dynamically discover and register core and Maya-specific add-ons."""
        import importlib
        import os

        addon_paths = [
            (
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..", "..", "core", "addons")
                ).replace("\\", "/"),
                localization.get_string("menu_coreAddons"),
                "openpypeline.core.addons",
            ),
            (
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "core", "addons")
                ).replace("\\", "/"),
                localization.get_string("menu_dccAddons"),
                "openpypeline.app.maya.core.addons",
            ),
        ]

        for addon_dir, menu_title, package_path in addon_paths:
            if not os.path.exists(addon_dir):
                continue

            self.view.menu_tools.addSection(menu_title)
            for filename in os.listdir(addon_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    mod_name = f"{package_path}.{filename[:-3]}"
                    try:
                        mod = importlib.import_module(mod_name)
                        importlib.reload(mod)  # Hot-reload for developers
                        if hasattr(mod, "run"):
                            addon_name = getattr(
                                mod,
                                "ADDON_NAME",
                                filename[:-3].replace("_", " ").title(),
                            )
                            action = self.view.menu_tools.addAction(addon_name)
                            action.triggered.connect(mod.run)
                    except Exception as e:
                        print(
                            localization.get_string("msg_failedAddonLoad").format(
                                filename, e
                            )
                        )

        self.view.menu_tools.addSeparator()
        self.view.menu_tools.addAction(
            localization.get_string("menu_addonsHelp"),
            lambda: QtWidgets.QMessageBox.information(
                self.view,
                localization.get_string("menu_addons"),
                localization.get_string("msg_addonsHelp"),
            ),
        )

    def _ensure_project_manager(self) -> Any:
        """Lazily initialize and return the project manager controller."""
        import importlib

        from openpypeline.ui import ui_objects as UIObjects

        from . import ops_project_manager_controller as opsProjectManagerController

        # Hot-reload the controller module for development iteration
        importlib.reload(opsProjectManagerController)
        if not hasattr(UIObjects.UIObjects(), "opsProjectManagerController"):
            UIObjects.UIObjects().opsProjectManagerController = (
                opsProjectManagerController.OpsProjectManagerController()
            )
        return UIObjects.UIObjects().opsProjectManagerController

    def on_project_manager_clicked(self) -> None:
        """Launch the Project Manager UI and ensure it is loaded into memory."""
        self._ensure_project_manager().showWindow()

    def on_project_changed(self, text: str) -> None:
        """Activate the newly selected project and refresh the entire UI.

        Invoked when ``ops_projName_optionMenu`` changes selection. Activates
        ``text`` via :func:`~openpypeline.core.ops_actions.activate_project`,
        displays a warning dialog on
        :exc:`~openpypeline.core.ops_actions.ProjectActionError`, updates
        ``ops_projPath_txtField``, and calls
        :func:`~openpypeline.ui.ops_ui_wrappers.refresh_ui`.

        :param text: Display name of the newly selected project.
        """
        if not text:
            return
        try:
            opsActions.activate_project(text)
        except opsActions.ProjectActionError as error:
            QtWidgets.QMessageBox.warning(
                self.view, "Could Not Activate Project", str(error)
            )
            return
        self.view.ops_projPath_txtField.setText(
            prefs.get_pref("ops_currProjectPath", "")
        )
        try:
            # Refresh all UI elements (dropdowns, lists, labels) to show the new project's data
            opsUIWrappers.refresh_ui()
        except Exception as e:
            print(localization.get_string("msg_failedUiRefresh").format(e))

    def on_open_master_clicked(self) -> None:
        """Open the Save Master dialog via the shared :class:`~openpypeline.ui.ui_objects.UIObjects` manager."""
        from openpypeline.ui import ui_objects as UIObjects

        # Retrieve the Save Master Controller from the Window Manager and display it
        getattr(UIObjects.UIObjects(), "opsSaveMasterController").showWindow()

    def on_open_scene_inventory(self, *args: Any) -> None:
        """Launch the Maya Scene Inventory window.

        Imports and invokes :func:`~openpypeline.app.maya.core.ops_scene_inv.show_window`,
        printing a localized fallback message if unavailable.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        try:
            # Defer import since this tool is an independent module
            from openpypeline.app.maya.core import ops_scene_inv as opsSceneInv

            opsSceneInv.show_window()
        except ImportError:
            print(localization.get_string("msg_sceneInvNotAvailable"))

    def on_reset_window_size(self, *args: Any) -> None:
        """Reset the Main UI window (and Maya workspace control) to default dimensions.

        Resizes :attr:`view` and its top-level window to ``450x780`` and updates
        the corresponding Maya ``workspaceControl`` when running inside Maya.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        self.view.resize(450, 780)
        if self.view.window():
            self.view.window().resize(450, 780)
        try:
            import maya.cmds as cmds

            workspace_control = self.view.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(
                    workspace_control, edit=True, resizeWidth=450, resizeHeight=780
                )
        except ImportError:
            pass

    def on_open_settings(self, *args: Any) -> None:
        """Launch the Global Settings dialog.

        Lazily imports and hot-reloads
        :mod:`~openpypeline.app.maya.ui.ops_settings_controller`, caches the
        controller on :class:`~openpypeline.ui.ui_objects.UIObjects`, and shows
        its window.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        # Defer imports to avoid circular dependencies
        import importlib

        from openpypeline.ui import ui_objects as UIObjects

        from . import ops_settings_controller as opsSettingsController

        # Hot-reload the controller module
        importlib.reload(opsSettingsController)

        # Ensure the Window Manager is tracking a living instance of the Settings Controller
        if not hasattr(UIObjects.UIObjects(), "opsSettingsController"):
            UIObjects.UIObjects().opsSettingsController = (
                opsSettingsController.OpsSettingsController()
            )

        # Command the tracked controller to show its view
        UIObjects.UIObjects().opsSettingsController.showWindow()

    def _asset_context_menu(self, position: QtCore.QPoint) -> None:
        """Build and display the right-click context menu for Assets.

        Triggered when the user right-clicks an item in ``ops_asset_scrollList``.

        :param position: Cursor position relative to ``ops_asset_scrollList``.
        """
        # Create the popup menu instance
        menu = QtWidgets.QMenu()

        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(
            localization.get_string("ctx_editAsset"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "workshop", version_offset=0
            ),
        )
        menu.addAction(
            localization.get_string("ctx_openMaster"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "master", version_offset=0
            ),
        )

        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.import_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "workshop"
            ),
        )
        imp.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.import_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "master"
            ),
        )

        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.reference_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "workshop"
            ),
        )
        ref.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.reference_selected(
                Tab.ASSET, Level.ASSET_OR_SHOT, "master"
            ),
        )

        # Add the Archive action to the root menu
        menu.addAction(
            localization.get_string("ctx_archive"),
            lambda: opsUIWrappers.prompt_archive(
                Tab.ASSET, Level.ASSET_OR_SHOT
            ),
        )

        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_asset_scrollList.mapToGlobal(position))

    def _asset_comp_context_menu(self, position: QtCore.QPoint) -> None:
        """Build and display the right-click context menu for Asset Components.

        Triggered when the user right-clicks an item in
        ``ops_componentScrollList``.

        :param position: Cursor position relative to ``ops_componentScrollList``.
        """
        # Create the popup menu instance
        menu = QtWidgets.QMenu()

        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(
            localization.get_string("ctx_editComponent"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.ASSET, Level.COMPONENT, "workshop", version_offset=0
            ),
        )
        menu.addAction(
            localization.get_string("ctx_viewMaster"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.ASSET, Level.COMPONENT, "master", version_offset=0
            ),
        )

        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.import_selected(
                Tab.ASSET, Level.COMPONENT, "workshop"
            ),
        )
        imp.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.import_selected(
                Tab.ASSET, Level.COMPONENT, "master"
            ),
        )

        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.reference_selected(
                Tab.ASSET, Level.COMPONENT, "workshop"
            ),
        )
        ref.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.reference_selected(
                Tab.ASSET, Level.COMPONENT, "master"
            ),
        )

        # Add the Archive action to the root menu
        menu.addAction(
            localization.get_string("ctx_archive"),
            lambda: opsUIWrappers.prompt_archive(Tab.ASSET, Level.COMPONENT),
        )

        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_componentScrollList.mapToGlobal(position))

    def _shot_context_menu(self, position: QtCore.QPoint) -> None:
        """Build and display the right-click context menu for Shots.

        Triggered when the user right-clicks an item in ``ops_shotScrollList``.

        :param position: Cursor position relative to ``ops_shotScrollList``.
        """
        # Create the popup menu instance
        menu = QtWidgets.QMenu()

        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(
            localization.get_string("ctx_editShot"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "workshop", version_offset=0
            ),
        )
        menu.addAction(
            localization.get_string("ctx_viewMaster"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "master", version_offset=0
            ),
        )

        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.import_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "workshop"
            ),
        )
        imp.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.import_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "master"
            ),
        )

        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.reference_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "workshop"
            ),
        )
        ref.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.reference_selected(
                Tab.SHOT, Level.ASSET_OR_SHOT, "master"
            ),
        )

        # Add the Archive action to the root menu
        menu.addAction(
            localization.get_string("ctx_archive"),
            lambda: opsUIWrappers.prompt_archive(Tab.SHOT, Level.ASSET_OR_SHOT),
        )

        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_shotScrollList.mapToGlobal(position))

    def _shot_comp_context_menu(self, position: QtCore.QPoint) -> None:
        """Build and display the right-click context menu for Shot Components.

        Triggered when the user right-clicks an item in
        ``ops_shotComponentScrollList``.

        :param position: Cursor position relative to
            ``ops_shotComponentScrollList``.
        """
        # Create the popup menu instance
        menu = QtWidgets.QMenu()

        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(
            localization.get_string("ctx_editShotComponent"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.SHOT, Level.COMPONENT, "workshop", version_offset=0
            ),
        )
        menu.addAction(
            localization.get_string("ctx_viewMaster"),
            lambda: opsUIWrappers.open_currently_selected(
                Tab.SHOT, Level.COMPONENT, "master", version_offset=0
            ),
        )

        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.import_selected(
                Tab.SHOT, Level.COMPONENT, "workshop"
            ),
        )
        imp.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.import_selected(
                Tab.SHOT, Level.COMPONENT, "master"
            ),
        )

        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.reference_selected(
                Tab.SHOT, Level.COMPONENT, "workshop"
            ),
        )
        ref.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.reference_selected(
                Tab.SHOT, Level.COMPONENT, "master"
            ),
        )

        # Add the Archive action to the root menu
        menu.addAction(
            localization.get_string("ctx_archive"),
            lambda: opsUIWrappers.prompt_archive(Tab.SHOT, Level.COMPONENT),
        )

        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_shotComponentScrollList.mapToGlobal(position))

    def showWindow(self) -> None:
        """Display the Main UI window and prompt for setup if no projects exist.

        Calls :meth:`~openpypeline.app.maya.ui.ops_main_ui.opsMainUI.showWindow`
        and schedules :meth:`prompt_first_time_project` when
        :func:`~openpypeline.core.ops_project.get_projects_data` is empty.
        """
        self.view.showWindow()
        # If no projects exist in the registry, prompt to create or join one
        projects = opsProject.get_projects_data()
        if not projects:
            QtCore.QTimer.singleShot(100, self.prompt_first_time_project)

    def prompt_first_time_project(self) -> None:
        """Prompt the artist to create or join a project if the registry is empty.

        Displays a modal welcome dialog offering **Create New Project**,
        **Join Existing Project**, or **Later**, delegating onboarding to
        the Project Manager controller when chosen.
        """
        projects = opsProject.get_projects_data()
        if projects:
            return

        box = QtWidgets.QMessageBox(self.view)
        box.setWindowTitle(
            localization.get_string("win_welcome", "Welcome to openPypeline Studio")
        )
        box.setText(
            localization.get_string(
                "msg_noProjectsPrompt",
                "No registered projects were found in your project registry.\n\n"
                "Would you like to create a new project or join an existing one?",
            )
        )
        box.setIcon(QtWidgets.QMessageBox.Information)

        btn_new = box.addButton(
            localization.get_string("btn_newProject", "Create New Project"),
            QtWidgets.QMessageBox.ActionRole,
        )
        btn_join = box.addButton(
            localization.get_string("btn_joinProject", "Join Existing Project"),
            QtWidgets.QMessageBox.ActionRole,
        )
        btn_cancel = box.addButton(
            localization.get_string("btn_cancel", "Later"),
            QtWidgets.QMessageBox.RejectRole,
        )

        box.exec()
        clicked = box.clickedButton()

        if clicked == btn_new:
            pm = self._ensure_project_manager()
            pm.on_new_project()
        elif clicked == btn_join:
            pm = self._ensure_project_manager()
            pm.on_join_project()
