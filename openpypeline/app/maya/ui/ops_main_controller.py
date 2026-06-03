"""
Module: ops_main_controller.py

Description:
    The Controller class for the main openPypeline Studio UI.
    Handles signal routing between the ops_main_ui View and the core backend.

License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtWidgets
from openpypeline.core.localization import localization
from ..core import ops_ui_wrappers as opsUIWrappers
from ....core import ops_actions as opsActions
from ....core import ops_project as opsProject
from .ops_main_ui import opsMainUI
from openpypeline.core.models import Tab, Level

class OpsMainController:
    def __init__(self):
        # 1. Instantiate the View (UI)
        self.view = opsMainUI()
        
        # 2. Connect View signals to Controller methods
        self._connect_signals()
        
        # 3. Perform initial data population
        self._populate_initial_data()

    def _connect_signals(self):
        # Connect buttons and widgets from the View to backend logic
        self.view.ops_projName_optionMenu.currentTextChanged.connect(self.on_project_changed)
        self.view.ops_refreshUIButton.clicked.connect(opsUIWrappers.refresh_ui)
        self.view.ops_closeUIButton.clicked.connect(self.view.close)
        
        # Context Menus
        self.view.ops_asset_scrollList.customContextMenuRequested.connect(self._asset_context_menu)
        self.view.ops_componentScrollList.customContextMenuRequested.connect(self._asset_comp_context_menu)
        self.view.ops_shotScrollList.customContextMenuRequested.connect(self._shot_context_menu)
        self.view.ops_shotComponentScrollList.customContextMenuRequested.connect(self._shot_comp_context_menu)
        
        # Tab Selection
        self.view.ops_mainTabs_tabLayout.currentChanged.connect(opsUIWrappers.update_working_tab)

        # Asset Browser List Selections & Actions
        self.view.ops_assetType_txtScrollList.itemSelectionChanged.connect(lambda *args: opsUIWrappers.update_asset_list(preserve_selection=0))
        self.view.ops_asset_scrollList.itemSelectionChanged.connect(lambda *args: opsUIWrappers.asset_selected(preserve_selection=0))
        self.view.ops_asset_scrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'workshop', version_offset=0))
        self.view.ops_componentScrollList.itemSelectionChanged.connect(opsUIWrappers.component_selected)
        self.view.ops_componentScrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(Tab.ASSET, Level.COMPONENT, 'workshop', version_offset=0))

        # Shot Browser List Selections & Actions
        self.view.ops_sequenceScrollList.itemSelectionChanged.connect(lambda *args: opsUIWrappers.update_shot_list(preserve_selection=0))
        self.view.ops_shotScrollList.itemSelectionChanged.connect(lambda *args: opsUIWrappers.shot_selected(preserve_selection=0))
        self.view.ops_shotScrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'workshop', version_offset=0))
        self.view.ops_shotComponentScrollList.itemSelectionChanged.connect(opsUIWrappers.shot_component_selected)
        self.view.ops_shotComponentScrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(Tab.SHOT, Level.COMPONENT, 'workshop', version_offset=0))
        
        # Currently Open Tab Actions
        self.view.ops_currOpenSaveWorkshop_btn.clicked.connect(opsUIWrappers.prompt_save_wip)
        self.view.ops_currOpenMaster_btn.clicked.connect(self.on_open_master_clicked)
        self.view.ops_currOpenRevive_btn.clicked.connect(opsUIWrappers.prompt_revive)
        self.view.ops_currOpenClose_btn.clicked.connect(opsUIWrappers.close_current)
        self.view.ops_currOpenSnapshot_btn.clicked.connect(opsUIWrappers.take_snapshot)
        self.view.ops_currOpenRecordPlayblast_btn.clicked.connect(opsUIWrappers.record_current_playblast)
        self.view.ops_currOpenViewPlayblast_btn.clicked.connect(opsUIWrappers.view_playblast_current)
        self.view.ops_currOpenClearNote_btn.clicked.connect(opsUIWrappers.clear_note)
        self.view.ops_currOpenSaveNote_btn.clicked.connect(opsUIWrappers.save_note)
        self.view.ops_currOpenExplore_btn.clicked.connect(opsUIWrappers.explore_current)

        # Asset Browser Buttons
        self.view.ops_assetTypeNew_btn.clicked.connect(opsUIWrappers.prompt_new_asset_type)
        self.view.ops_assetTypeRemove_btn.clicked.connect(lambda *args: opsUIWrappers.remove_process(Tab.ASSET, Level.TYPE_OR_SEQUENCE))
        self.view.ops_assetNew_btn.clicked.connect(opsUIWrappers.prompt_new_asset)
        self.view.ops_assetRemove_btn.clicked.connect(lambda *args: opsUIWrappers.remove_process(Tab.ASSET, Level.ASSET_OR_SHOT))
        self.view.ops_assetRename_btn.clicked.connect(opsUIWrappers.prompt_rename_asset)
        self.view.ops_componentNewButton.clicked.connect(opsUIWrappers.prompt_new_asset_component)
        self.view.ops_componentRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(Tab.ASSET, Level.COMPONENT))
        self.view.ops_assetViewPlayblastAssetButton.clicked.connect(lambda *args: opsUIWrappers.view_playblast_selected(Tab.ASSET))
        self.view.ops_exploreAssetsButton.clicked.connect(lambda *args: opsUIWrappers.explore_selected(Tab.ASSET))

        # Shot Browser Buttons
        self.view.ops_sequenceNewButton.clicked.connect(opsUIWrappers.prompt_new_sequence)
        self.view.ops_sequenceRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(Tab.SHOT, Level.TYPE_OR_SEQUENCE))
        self.view.ops_shotNewButton.clicked.connect(opsUIWrappers.prompt_new_shot)
        self.view.ops_shotRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(Tab.SHOT, Level.ASSET_OR_SHOT))
        self.view.ops_shotComponentNewButton.clicked.connect(opsUIWrappers.prompt_new_shot_component)
        self.view.ops_shotComponentRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(Tab.SHOT, Level.COMPONENT))
        self.view.ops_shotViewPlayblastButton.clicked.connect(lambda *args: opsUIWrappers.view_playblast_selected(Tab.SHOT))
        self.view.ops_exploreShotsButton.clicked.connect(lambda *args: opsUIWrappers.explore_selected(Tab.SHOT))

        # --- Top Menu: File Actions ---
        self.view.action_save_wip.triggered.connect(opsUIWrappers.prompt_save_wip)
        self.view.action_save_master.triggered.connect(self.on_open_master_clicked)
        self.view.action_close.triggered.connect(self.view.close)
        
        # --- Top Menu: Project Actions ---
        self.view.action_project_manager.triggered.connect(self.on_project_manager_clicked)
        self.view.action_edit_users.triggered.connect(opsProject.proj_edit_users)

        # Top Menu Actions
        self.view.action_scene_inventory.triggered.connect(self.on_open_scene_inventory)
        self.view.action_reset_window_size.triggered.connect(self.on_reset_window_size)
        self.view.action_preferences.triggered.connect(self.on_open_settings)
        self.view.action_about.triggered.connect(opsUIWrappers.about_dialog)
        self.view.action_help.triggered.connect(opsUIWrappers.launch_help)

        # --- Top Menu: Create Actions ---
        self.view.action_new_asset_type.triggered.connect(opsUIWrappers.prompt_new_asset_type)
        self.view.action_new_asset.triggered.connect(opsUIWrappers.prompt_new_asset)
        self.view.action_new_asset_component.triggered.connect(opsUIWrappers.prompt_new_asset_component)
        self.view.action_new_sequence.triggered.connect(opsUIWrappers.prompt_new_sequence)
        self.view.action_new_shot.triggered.connect(opsUIWrappers.prompt_new_shot)
        self.view.action_new_shot_component.triggered.connect(opsUIWrappers.prompt_new_shot_component)

    def _populate_initial_data(self):
        # Initialize the UI with data from the Model
        self._load_addons()

    def _load_addons(self):
        """Dynamically discovers and loads core and app-specific add-ons."""
        import os
        import importlib
        
        addon_paths = [
            (os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "core", "addons")).replace("\\", "/"), localization.get_string("menu_coreAddons"), "openpypeline.core.addons"),
            (os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core", "addons")).replace("\\", "/"), localization.get_string("menu_dccAddons"), "openpypeline.app.maya.core.addons")
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
                        importlib.reload(mod) # Hot-reload for developers
                        if hasattr(mod, 'run'):
                            addon_name = getattr(mod, 'ADDON_NAME', filename[:-3].replace('_', ' ').title())
                            action = self.view.menu_tools.addAction(addon_name)
                            action.triggered.connect(mod.run)
                    except Exception as e:
                        print(localization.get_string("msg_failedAddonLoad").format(filename, e))
                        
        self.view.menu_tools.addSeparator()
        self.view.menu_tools.addAction(localization.get_string("menu_addonsHelp"), lambda: QtWidgets.QMessageBox.information(self.view, localization.get_string("menu_addons"), localization.get_string("msg_addonsHelp")))

    def on_project_manager_clicked(self):
        """Launches the Project Manager UI and ensures it is loaded into memory."""
        # Defer imports to avoid circular dependencies and speed up initial load
        import importlib
        from . import ui_objects as UIObjects
        from . import ops_project_manager_controller as opsProjectManagerController
        
        # Hot-reload the controller module for development iteration
        importlib.reload(opsProjectManagerController)
        
        # Check if the Window Manager (UIObjects singleton) already tracks this controller instance
        if not hasattr(UIObjects.UIObjects(), 'opsProjectManagerController'):
            # If not tracked, instantiate it and store it to prevent garbage collection
            UIObjects.UIObjects().opsProjectManagerController = opsProjectManagerController.OpsProjectManagerController()
            
        # Call the controller's method to bring its view to the front
        UIObjects.UIObjects().opsProjectManagerController.showWindow()

    def on_project_changed(self, text):
        """
        Handles project switching from the main dropdown.
        Activates the newly selected project and refreshes the entire UI to reflect its contents.
        """
        # Tell the backend to switch active project paths and configurations
        opsActions.activate_project(text)
        try:
            # Refresh all UI elements (dropdowns, lists, labels) to show the new project's data
            opsUIWrappers.refresh_ui()
        except Exception as e:
            print(localization.get_string("msg_failedUiRefresh").format(e))

    def on_open_master_clicked(self):
        """Opens the Save Master Dialog."""
        from . import ui_objects as UIObjects
        
        # Retrieve the Save Master Controller from the Window Manager and display it
        getattr(UIObjects.UIObjects(), 'opsSaveMasterController').showWindow()

    def on_open_scene_inventory(self, *args):
        """Launches the Scene Inventory tool."""
        try:
            # Defer import since this tool is an independent module
            from ..core import ops_scene_inv as opsSceneInv
            opsSceneInv.show_window()
        except ImportError:
            print(localization.get_string("msg_sceneInvNotAvailable"))

    def on_reset_window_size(self, *args):
        """Resets the Main UI window to its default starting dimensions."""
        self.view.resize(450, 780)
        if self.view.window():
            self.view.window().resize(450, 780)
        try:
            import maya.cmds as cmds
            workspace_control = self.view.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(workspace_control, edit=True, resizeWidth=450, resizeHeight=780)
        except ImportError:
            pass

    def on_open_settings(self, *args):
        """Launches the Global Settings Dialog."""
        # Defer imports to avoid circular dependencies
        import importlib
        from . import ui_objects as UIObjects
        from . import ops_settings_controller as opsSettingsController
        
        # Hot-reload the controller module
        importlib.reload(opsSettingsController)
        
        # Ensure the Window Manager is tracking a living instance of the Settings Controller
        if not hasattr(UIObjects.UIObjects(), 'opsSettingsController'):
            UIObjects.UIObjects().opsSettingsController = opsSettingsController.OpsSettingsController()
            
        # Command the tracked controller to show its view
        UIObjects.UIObjects().opsSettingsController.showWindow()

    def _asset_context_menu(self, position):
        """
        Builds and displays the right-click context menu for Assets.
        Triggered when the user right-clicks an item in the Asset browser list.
        """
        # Create the popup menu instance
        menu = QtWidgets.QMenu()
        
        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(localization.get_string("ctx_editAsset"), lambda: opsUIWrappers.open_currently_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'workshop', version_offset=0))
        menu.addAction(localization.get_string("ctx_openMaster"), lambda: opsUIWrappers.open_currently_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'master', version_offset=0))
        
        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.import_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'workshop'))
        imp.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.import_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'master'))
        
        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.reference_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'workshop'))
        ref.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.reference_selected(Tab.ASSET, Level.ASSET_OR_SHOT, 'master'))
        
        # Add the Archive action to the root menu
        menu.addAction(localization.get_string("ctx_archive"), lambda: opsUIWrappers.prompt_archive(Tab.ASSET, Level.ASSET_OR_SHOT))
        
        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_asset_scrollList.mapToGlobal(position))

    def _asset_comp_context_menu(self, position):
        """Builds and displays the right-click context menu for Asset Components."""
        # Create the popup menu instance
        menu = QtWidgets.QMenu()
        
        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(localization.get_string("ctx_editComponent"), lambda: opsUIWrappers.open_currently_selected(Tab.ASSET, Level.COMPONENT, 'workshop', version_offset=0))
        menu.addAction(localization.get_string("ctx_viewMaster"), lambda: opsUIWrappers.open_currently_selected(Tab.ASSET, Level.COMPONENT, 'master', version_offset=0))
        
        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.import_selected(Tab.ASSET, Level.COMPONENT, 'workshop'))
        imp.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.import_selected(Tab.ASSET, Level.COMPONENT, 'master'))
        
        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.reference_selected(Tab.ASSET, Level.COMPONENT, 'workshop'))
        ref.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.reference_selected(Tab.ASSET, Level.COMPONENT, 'master'))
        
        # Add the Archive action to the root menu
        menu.addAction(localization.get_string("ctx_archive"), lambda: opsUIWrappers.prompt_archive(Tab.ASSET, Level.COMPONENT))
        
        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_componentScrollList.mapToGlobal(position))

    def _shot_context_menu(self, position):
        """Builds and displays the right-click context menu for Shots."""
        # Create the popup menu instance
        menu = QtWidgets.QMenu()
        
        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(localization.get_string("ctx_editShot"), lambda: opsUIWrappers.open_currently_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'workshop', version_offset=0))
        menu.addAction(localization.get_string("ctx_viewMaster"), lambda: opsUIWrappers.open_currently_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'master', version_offset=0))
        
        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.import_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'workshop'))
        imp.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.import_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'master'))
        
        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.reference_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'workshop'))
        ref.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.reference_selected(Tab.SHOT, Level.ASSET_OR_SHOT, 'master'))
        
        # Add the Archive action to the root menu
        menu.addAction(localization.get_string("ctx_archive"), lambda: opsUIWrappers.prompt_archive(Tab.SHOT, Level.ASSET_OR_SHOT))
        
        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_shotScrollList.mapToGlobal(position))

    def _shot_comp_context_menu(self, position):
        """Builds and displays the right-click context menu for Shot Components."""
        # Create the popup menu instance
        menu = QtWidgets.QMenu()
        
        # Add root-level edit actions using lambdas to pass specific arguments to the wrappers
        menu.addAction(localization.get_string("ctx_editShotComponent"), lambda: opsUIWrappers.open_currently_selected(Tab.SHOT, Level.COMPONENT, 'workshop', version_offset=0))
        menu.addAction(localization.get_string("ctx_viewMaster"), lambda: opsUIWrappers.open_currently_selected(Tab.SHOT, Level.COMPONENT, 'master', version_offset=0))
        
        # Build the 'Import' sub-menu
        imp = menu.addMenu(localization.get_string("ctx_import"))
        imp.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.import_selected(Tab.SHOT, Level.COMPONENT, 'workshop'))
        imp.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.import_selected(Tab.SHOT, Level.COMPONENT, 'master'))
        
        # Build the 'Reference' sub-menu
        ref = menu.addMenu(localization.get_string("ctx_reference"))
        ref.addAction(localization.get_string("ctx_wip"), lambda: opsUIWrappers.reference_selected(Tab.SHOT, Level.COMPONENT, 'workshop'))
        ref.addAction(localization.get_string("ctx_master"), lambda: opsUIWrappers.reference_selected(Tab.SHOT, Level.COMPONENT, 'master'))
        
        # Add the Archive action to the root menu
        menu.addAction(localization.get_string("ctx_archive"), lambda: opsUIWrappers.prompt_archive(Tab.SHOT, Level.COMPONENT))
        
        # Display the menu at the cursor's global screen position
        menu.exec(self.view.ops_shotComponentScrollList.mapToGlobal(position))

    def showWindow(self):
        """Displays the Main UI Window."""
        self.view.showWindow()
