# openpypeline/app/maya/ui/opsMainController.py

from PySide6 import QtWidgets
from ..core import ops_ui_wrappers as opsUIWrappers
from ..core import ops_actions as opsActions
from .ops_main_ui import (
    opsMainUI,
    TAB_ASSET, TAB_SHOT, LEVEL_1, LEVEL_2, LEVEL_3
)

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
        self.view.ops_projManager_btn.clicked.connect(self.on_project_manager_clicked)
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
        self.view.ops_asset_scrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_2, 'workshop', version_offset=0))
        self.view.ops_componentScrollList.itemSelectionChanged.connect(opsUIWrappers.component_selected)
        self.view.ops_componentScrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_3, 'workshop', version_offset=0))

        # Shot Browser List Selections & Actions
        self.view.ops_sequenceScrollList.itemSelectionChanged.connect(lambda *args: opsUIWrappers.update_shot_list(preserve_selection=0))
        self.view.ops_shotScrollList.itemSelectionChanged.connect(lambda *args: opsUIWrappers.shot_selected(preserve_selection=0))
        self.view.ops_shotScrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_2, 'workshop', version_offset=0))
        self.view.ops_shotComponentScrollList.itemSelectionChanged.connect(opsUIWrappers.shot_component_selected)
        self.view.ops_shotComponentScrollList.itemDoubleClicked.connect(lambda *args: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_3, 'workshop', version_offset=0))
        
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
        self.view.ops_assetTypeRemove_btn.clicked.connect(lambda *args: opsUIWrappers.remove_process(TAB_ASSET, LEVEL_1))
        self.view.ops_assetNew_btn.clicked.connect(opsUIWrappers.prompt_new_asset)
        self.view.ops_assetRemove_btn.clicked.connect(lambda *args: opsUIWrappers.remove_process(TAB_ASSET, LEVEL_2))
        self.view.ops_assetRename_btn.clicked.connect(opsUIWrappers.prompt_rename_asset)
        self.view.ops_componentNewButton.clicked.connect(opsUIWrappers.prompt_new_asset_component)
        self.view.ops_componentRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(TAB_ASSET, LEVEL_3))
        self.view.ops_assetViewPlayblastAssetButton.clicked.connect(lambda *args: opsUIWrappers.view_playblast_selected(TAB_ASSET))
        self.view.ops_exploreAssetsButton.clicked.connect(lambda *args: opsUIWrappers.explore_selected(TAB_ASSET))

        # Shot Browser Buttons
        self.view.ops_sequenceNewButton.clicked.connect(opsUIWrappers.prompt_new_sequence)
        self.view.ops_sequenceRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(TAB_SHOT, LEVEL_1))
        self.view.ops_shotNewButton.clicked.connect(opsUIWrappers.prompt_new_shot)
        self.view.ops_shotRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(TAB_SHOT, LEVEL_2))
        self.view.ops_shotComponentNewButton.clicked.connect(opsUIWrappers.prompt_new_shot_component)
        self.view.ops_shotComponentRemoveButton.clicked.connect(lambda *args: opsUIWrappers.remove_process(TAB_SHOT, LEVEL_3))
        self.view.ops_shotViewPlayblastButton.clicked.connect(lambda *args: opsUIWrappers.view_playblast_selected(TAB_SHOT))
        self.view.ops_exploreShotsButton.clicked.connect(lambda *args: opsUIWrappers.explore_selected(TAB_SHOT))

        # Top Menu Actions
        self.view.action_scene_inventory.triggered.connect(self.on_open_scene_inventory)
        self.view.action_toolbar_scene_inventory.triggered.connect(self.on_open_scene_inventory)
        self.view.action_preferences.triggered.connect(self.on_open_settings)
        self.view.action_about.triggered.connect(opsUIWrappers.about_dialog)
        self.view.action_help.triggered.connect(opsUIWrappers.launch_help)

    def _populate_initial_data(self):
        # Initialize the UI with data from the Model
        pass

    def on_project_manager_clicked(self):
        from . import ui_objects as UIObjects
        getattr(UIObjects.UIObjects(), 'opsProjectManagerGUI').showWindow()

    def on_project_changed(self, text):
        opsActions.activate_project(text)
        try:
            opsUIWrappers.refresh_ui()
        except Exception as e:
            print(f"Could not refresh UI after project change: {e}")

    def on_open_master_clicked(self):
        from . import ui_objects as UIObjects
        getattr(UIObjects.UIObjects(), 'opsSaveMasterController').showWindow()

    def on_open_scene_inventory(self, *args):
        try:
            from ..core import ops_scene_inv as opsSceneInv
            opsSceneInv.show_window()
        except ImportError:
            print("Scene Inventory module not available.")

    def on_open_settings(self, *args):
        import importlib
        from . import ui_objects as UIObjects
        from . import ops_settings_controller as opsSettingsController
        importlib.reload(opsSettingsController)
        if not hasattr(UIObjects.UIObjects(), 'opsSettingsController'):
            UIObjects.UIObjects().opsSettingsController = opsSettingsController.OpsSettingsController()
        UIObjects.UIObjects().opsSettingsController.showWindow()

    def _asset_context_menu(self, position):
        menu = QtWidgets.QMenu()
        menu.addAction("Edit Asset", lambda: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_2, 'workshop', version_offset=0))
        menu.addAction("Open Master", lambda: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_2, 'master', version_offset=0))
        imp = menu.addMenu("Import")
        imp.addAction("WIP", lambda: opsUIWrappers.import_selected(TAB_ASSET, LEVEL_2, 'workshop'))
        imp.addAction("Master", lambda: opsUIWrappers.import_selected(TAB_ASSET, LEVEL_2, 'master'))
        ref = menu.addMenu("Reference")
        ref.addAction("WIP", lambda: opsUIWrappers.reference_selected(TAB_ASSET, LEVEL_2, 'workshop'))
        ref.addAction("Master", lambda: opsUIWrappers.reference_selected(TAB_ASSET, LEVEL_2, 'master'))
        menu.addAction("Archive...", lambda: opsUIWrappers.prompt_archive(TAB_ASSET, LEVEL_2))
        menu.exec(self.view.ops_asset_scrollList.mapToGlobal(position))

    def _asset_comp_context_menu(self, position):
        menu = QtWidgets.QMenu()
        menu.addAction("Edit Component", lambda: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_3, 'workshop', version_offset=0))
        menu.addAction("View Master", lambda: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_3, 'master', version_offset=0))
        imp = menu.addMenu("Import")
        imp.addAction("WIP", lambda: opsUIWrappers.import_selected(TAB_ASSET, LEVEL_3, 'workshop'))
        imp.addAction("Master", lambda: opsUIWrappers.import_selected(TAB_ASSET, LEVEL_3, 'master'))
        ref = menu.addMenu("Reference")
        ref.addAction("WIP", lambda: opsUIWrappers.reference_selected(TAB_ASSET, LEVEL_3, 'workshop'))
        ref.addAction("Master", lambda: opsUIWrappers.reference_selected(TAB_ASSET, LEVEL_3, 'master'))
        menu.addAction("Archive...", lambda: opsUIWrappers.prompt_archive(TAB_ASSET, LEVEL_3))
        menu.exec(self.view.ops_componentScrollList.mapToGlobal(position))

    def _shot_context_menu(self, position):
        menu = QtWidgets.QMenu()
        menu.addAction("Edit Shot", lambda: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_2, 'workshop', version_offset=0))
        menu.addAction("View Master", lambda: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_2, 'master', version_offset=0))
        imp = menu.addMenu("Import")
        imp.addAction("WIP", lambda: opsUIWrappers.import_selected(TAB_SHOT, LEVEL_2, 'workshop'))
        imp.addAction("Master", lambda: opsUIWrappers.import_selected(TAB_SHOT, LEVEL_2, 'master'))
        ref = menu.addMenu("Reference")
        ref.addAction("WIP", lambda: opsUIWrappers.reference_selected(TAB_SHOT, LEVEL_2, 'workshop'))
        ref.addAction("Master", lambda: opsUIWrappers.reference_selected(TAB_SHOT, LEVEL_2, 'master'))
        menu.addAction("Archive...", lambda: opsUIWrappers.prompt_archive(TAB_SHOT, LEVEL_2))
        menu.exec(self.view.ops_shotScrollList.mapToGlobal(position))

    def _shot_comp_context_menu(self, position):
        menu = QtWidgets.QMenu()
        menu.addAction("Edit Shot Component", lambda: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_3, 'workshop', version_offset=0))
        menu.addAction("View Master", lambda: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_3, 'master', version_offset=0))
        imp = menu.addMenu("Import")
        imp.addAction("WIP", lambda: opsUIWrappers.import_selected(TAB_SHOT, LEVEL_3, 'workshop'))
        imp.addAction("Master", lambda: opsUIWrappers.import_selected(TAB_SHOT, LEVEL_3, 'master'))
        ref = menu.addMenu("Reference")
        ref.addAction("WIP", lambda: opsUIWrappers.reference_selected(TAB_SHOT, LEVEL_3, 'workshop'))
        ref.addAction("Master", lambda: opsUIWrappers.reference_selected(TAB_SHOT, LEVEL_3, 'master'))
        menu.addAction("Archive...", lambda: opsUIWrappers.prompt_archive(TAB_SHOT, LEVEL_3))
        menu.exec(self.view.ops_shotComponentScrollList.mapToGlobal(position))

    def show(self):
        self.view.showWindow()
