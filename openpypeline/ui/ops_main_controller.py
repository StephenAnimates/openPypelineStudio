"""Shared host-agnostic controller for the main openPypeline Studio UI.

Handles signal routing, menu actions, context menus, and event coordination between :class:`~openpypeline.ui.ops_main_ui.OpsMainUI` and the core :mod:`~openpypeline.core.ops_actions`, :mod:`~openpypeline.core.ops_project`, and :mod:`~openpypeline.ui.ops_ui_wrappers` backends across standalone tools and extensible DCC host integrations.

:File: ops_main_controller.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

import importlib.util
import os
import sys
from typing import Any

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets  # type: ignore[no-redef]

from openpypeline.core import ops_actions as opsActions
from openpypeline.core import ops_project as opsProject
from openpypeline.core.localization import localization
from openpypeline.core.models import Level, Tab
from openpypeline.core.util import prefs
from openpypeline.ui import ops_ui_wrappers as opsUIWrappers
from openpypeline.ui.ops_main_ui import OpsMainUI


class OpsMainController:
    """Connect main-window controls to pipeline actions and refresh handlers.

    Instantiates the main UI view via :meth:`_create_view`, wires Qt signals for asset/shot browsing, scene publishing, and context menus to :mod:`~openpypeline.ui.ops_ui_wrappers` and :mod:`~openpypeline.core.ops_project`, and populates initial project data.

    :ivar view: Main PySide window widget managed by this controller.
    :vartype view: openpypeline.ui.ops_main_ui.OpsMainUI
    """

    def __init__(self) -> None:
        """Create the main view and initialize its signals and project state."""
        self.view: OpsMainUI = self._create_view()
        self._connect_signals()
        self._populate_initial_data()

    def _create_view(self) -> OpsMainUI:
        """Instantiate and return the main UI view widget.

        Host-specific subclasses should override this method to return their DCC-parented or dockable view subclass.

        :returns: Main window view instance.
        """
        return OpsMainUI()

    def _get_dcc_addon_specs(self) -> list[tuple[str, str, str]]:
        """Return host-specific add-on directory tuples ``(dir_path, menu_title, package_path)``.

        :returns: List of add-on discovery specifications for the active DCC host.
        """
        return []

    def _create_project_manager_controller(self) -> Any:
        """Instantiate and return the host's Project Manager controller.

        :returns: Project Manager controller instance exposing ``showWindow()``, ``on_new_project()``, and ``on_join_project()``, or ``None``.
        """
        return None

    def _create_settings_controller(self) -> Any:
        """Instantiate and return the host's Global Settings controller.

        :returns: Settings controller instance exposing ``showWindow()``, or ``None``.
        """
        return None

    def _connect_signals(self) -> None:
        """Connect main-window controls and list selections to their handlers."""
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

        Queries registered projects via :func:`~openpypeline.core.ops_project.get_projects_data`, filters out inactive projects (``status == "0"``), populates ``ops_projName_optionMenu`` without triggering selection signals, activates the stored project via :func:`~openpypeline.core.ops_actions.activate_project`, and updates ``ops_projPath_txtField``.
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

    def _import_addon_module(
        self, addon_dir: str, filename: str, package_path: str | None
    ) -> Any:
        """Import (or reload) an add-on Python module from a package or directory.

        Uses standard package imports when ``package_path`` is provided, and falls back to file-path loading via :mod:`importlib.util` for external studio directories defined in ``OPENPYPELINE_ADDONS_PATH``.

        :param addon_dir: Absolute directory containing the add-on script.
        :param filename: Python filename ending in ``.py``.
        :param package_path: Dotted package path (e.g. ``"openpypeline.core.addons"``), or ``None`` when loading from an external filesystem folder.
        :returns: Loaded Python module object.
        :raises ImportError: If a module spec cannot be created for an external file.
        """
        stem = filename[:-3]
        if package_path:
            mod = importlib.import_module(f"{package_path}.{stem}")
            return importlib.reload(mod)

        # Load external studio add-ons directly by path without requiring sys.path edits
        filepath = os.path.join(addon_dir, filename)
        mod_name = f"openpypeline_ext_addon_{stem}"
        spec = importlib.util.spec_from_file_location(mod_name, filepath)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create module spec for {filepath}")

        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        return mod

    def _load_addons(self) -> None:
        """Discover and register core, host-specific, and external studio add-ons.

        Scans three sources in order and populates sections in ``menu_tools``:

        1. Built-in host-agnostic add-ons under ``openpypeline/core/addons/``.
        2. Active DCC host add-ons returned by :meth:`_get_dcc_addon_specs`.
        3. External studio directories listed in ``OPENPYPELINE_ADDONS_PATH``.

        Each discovered module must expose a callable ``run()`` entry point and may optionally define ``ADDON_NAME``, ``ADDON_ENABLED``, and
        ``ADDON_TOOLTIP``.
        """

        core_addons_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "core", "addons")
        ).replace("\\", "/")

        addon_paths: list[tuple[str, str, str | None]] = [
            (
                core_addons_dir,
                localization.get_string("menu_coreAddons"),
                "openpypeline.core.addons",
            ),
            *self._get_dcc_addon_specs(),
        ]

        # Append optional studio-external directories from OPENPYPELINE_ADDONS_PATH
        extra_dirs = os.environ.get("OPENPYPELINE_ADDONS_PATH", "")
        for idx, extra_dir in enumerate(
            d.strip() for d in extra_dirs.split(os.pathsep) if d.strip()
        ):
            addon_paths.append(
                (
                    os.path.abspath(extra_dir).replace("\\", "/"),
                    localization.get_string("menu_studioAddons")
                    if idx == 0
                    else f"{localization.get_string('menu_studioAddons')} ({idx + 1})",
                    None,
                )
            )

        for addon_dir, menu_title, package_path in addon_paths:
            if not os.path.isdir(addon_dir):
                continue

            # Skip dunder modules (such as __init__.py) and non-Python files
            py_files = [
                f
                for f in sorted(os.listdir(addon_dir))
                if f.endswith(".py") and not f.startswith("__")
            ]
            if not py_files:
                continue

            self.view.menu_tools.addSection(menu_title)
            for filename in py_files:
                try:
                    mod = self._import_addon_module(addon_dir, filename, package_path)
                    # Allow authors to disable work-in-progress add-ons via ADDON_ENABLED = False
                    if not getattr(mod, "ADDON_ENABLED", True):
                        continue
                    if not hasattr(mod, "run"):
                        continue

                    addon_name = getattr(
                        mod,
                        "ADDON_NAME",
                        filename[:-3].replace("_", " ").title(),
                    )
                    action = self.view.menu_tools.addAction(addon_name)

                    tooltip = getattr(mod, "ADDON_TOOLTIP", "")
                    if tooltip:
                        action.setToolTip(tooltip)
                        action.setStatusTip(tooltip)

                    # Swallow QAction.triggered's bool argument so zero-arg run() functions work cleanly
                    action.triggered.connect(
                        lambda _checked=False, fn=mod.run: fn()
                    )
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
        from openpypeline.ui import ui_objects as UIObjects

        if not hasattr(UIObjects.UIObjects(), "opsProjectManagerController"):
            controller = self._create_project_manager_controller()
            if controller is not None:
                UIObjects.UIObjects().opsProjectManagerController = controller
        return getattr(UIObjects.UIObjects(), "opsProjectManagerController", None)

    def on_project_manager_clicked(self) -> None:
        """Launch the Project Manager UI and ensure it is loaded into memory."""
        pm = self._ensure_project_manager()
        if pm is not None:
            pm.showWindow()

    def on_project_changed(self, text: str) -> None:
        """Activate the newly selected project and refresh the entire UI.

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
            opsUIWrappers.refresh_ui()
        except Exception as e:
            print(localization.get_string("msg_failedUiRefresh").format(e))

    def on_open_master_clicked(self) -> None:
        """Open the Save Master dialog via :class:`~openpypeline.ui.ui_objects.UIObjects`."""
        from openpypeline.ui import ui_objects as UIObjects

        controller = getattr(
            UIObjects.UIObjects(), "opsSaveMasterController", None
        )
        if controller is not None:
            controller.showWindow()

    def on_open_scene_inventory(self, *args: Any) -> None:
        """Launch the host Scene Inventory window when implemented by a subclass.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        print(localization.get_string("msg_sceneInvNotAvailable"))

    def on_reset_window_size(self, *args: Any) -> None:
        """Reset the Main UI window to its default ``450x780`` dimensions.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        self.view.resize(450, 780)
        if self.view.window():
            self.view.window().resize(450, 780)

    def on_open_settings(self, *args: Any) -> None:
        """Launch the Global Settings dialog when configured by the host.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        """
        del args
        from openpypeline.ui import ui_objects as UIObjects

        if not hasattr(UIObjects.UIObjects(), "opsSettingsController"):
            controller = self._create_settings_controller()
            if controller is not None:
                UIObjects.UIObjects().opsSettingsController = controller

        controller = getattr(
            UIObjects.UIObjects(), "opsSettingsController", None
        )
        if controller is not None:
            controller.showWindow()

    def _build_item_context_menu(
        self,
        position: QtCore.QPoint,
        list_widget: QtWidgets.QListWidget,
        tab: Tab,
        level: Level,
        edit_label_key: str,
        master_label_key: str,
    ) -> None:
        """Build and display a standard browser right-click context menu.

        :param position: Cursor position relative to ``list_widget``.
        :param list_widget: Source list widget emitting the context-menu signal.
        :param tab: Active browser tab (:attr:`Tab.ASSET` or :attr:`Tab.SHOT`).
        :param level: Item hierarchy level targeted by the menu actions.
        :param edit_label_key: Localization key for the open-workshop action.
        :param master_label_key: Localization key for the open-master action.
        """
        menu = QtWidgets.QMenu()

        menu.addAction(
            localization.get_string(edit_label_key),
            lambda: opsUIWrappers.open_currently_selected(
                tab, level, "workshop", version_offset=0
            ),
        )
        menu.addAction(
            localization.get_string(master_label_key),
            lambda: opsUIWrappers.open_currently_selected(
                tab, level, "master", version_offset=0
            ),
        )

        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.import_selected(tab, level, "workshop"),
        )
        imp.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.import_selected(tab, level, "master"),
        )

        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(
            localization.get_string("ctx_wip"),
            lambda: opsUIWrappers.reference_selected(tab, level, "workshop"),
        )
        ref.addAction(
            localization.get_string("ctx_master"),
            lambda: opsUIWrappers.reference_selected(tab, level, "master"),
        )

        menu.addAction(
            localization.get_string("ctx_archive"),
            lambda: opsUIWrappers.prompt_archive(tab, level),
        )

        menu.exec(list_widget.mapToGlobal(position))

    def _asset_context_menu(self, position: QtCore.QPoint) -> None:
        """Display the right-click context menu for Assets."""
        self._build_item_context_menu(
            position,
            self.view.ops_asset_scrollList,
            Tab.ASSET,
            Level.ASSET_OR_SHOT,
            "ctx_editAsset",
            "ctx_openMaster",
        )

    def _asset_comp_context_menu(self, position: QtCore.QPoint) -> None:
        """Display the right-click context menu for Asset Components."""
        self._build_item_context_menu(
            position,
            self.view.ops_componentScrollList,
            Tab.ASSET,
            Level.COMPONENT,
            "ctx_editComponent",
            "ctx_viewMaster",
        )

    def _shot_context_menu(self, position: QtCore.QPoint) -> None:
        """Display the right-click context menu for Shots."""
        self._build_item_context_menu(
            position,
            self.view.ops_shotScrollList,
            Tab.SHOT,
            Level.ASSET_OR_SHOT,
            "ctx_editShot",
            "ctx_viewMaster",
        )

    def _shot_comp_context_menu(self, position: QtCore.QPoint) -> None:
        """Display the right-click context menu for Shot Components."""
        self._build_item_context_menu(
            position,
            self.view.ops_shotComponentScrollList,
            Tab.SHOT,
            Level.COMPONENT,
            "ctx_editShotComponent",
            "ctx_viewMaster",
        )

    def showWindow(self) -> None:
        """Display the Main UI window and prompt for setup if no projects exist."""
        self.view.showWindow()
        projects = opsProject.get_projects_data()
        if not projects:
            QtCore.QTimer.singleShot(100, self.prompt_first_time_project)

    def prompt_first_time_project(self) -> None:
        """Prompt the artist to create or join a project if the registry is empty."""
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
        box.addButton(
            localization.get_string("btn_cancel", "Later"),
            QtWidgets.QMessageBox.RejectRole,
        )

        box.exec()
        clicked = box.clickedButton()

        if clicked == btn_new:
            pm = self._ensure_project_manager()
            if pm is not None:
                pm.on_new_project()
        elif clicked == btn_join:
            pm = self._ensure_project_manager()
            if pm is not None:
                pm.on_join_project()
