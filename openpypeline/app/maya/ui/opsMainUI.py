"""
Module: openPipelineMainUI.py

Description: 
    Creates and manages the main openPypeline Studio UI in Maya.
    This module defines the `openPipelineMainUI` class, which inherits from 
    the base `window` class. It constructs the primary user interface containing 
    the Asset Browser, Shot Browser, and "Currently Open" working area tabs.
    
    This UI serves as the central hub for artists to interact with the 
    openPypeline Studio framework, manage their files, and navigate the project hierarchy.
        
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)

    (Phase 2 Modernization Complete: Fully migrated to PySide6 and DCC-agnostic preferences.)
"""

import os
import logging
from PySide6 import QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import UIObjects
import opsUIWrappers
import opsProject
import opsActions

logger = logging.getLogger(__name__)

# --- UI Index Constants ---
TAB_ASSET = 2
TAB_SHOT = 3
LEVEL_1 = 1  # Asset Type / Sequence
LEVEL_2 = 2  # Asset / Shot
LEVEL_3 = 3  # Component

# --- UI Stylesheet ---
OPS_STYLESHEET = """
    QLabel[styleClass="headingBold"] {
        font-weight: bold;
    }
    QPushButton[styleClass="positiveAction"] {
        background-color: #99cc80; 
        color: black;
    }
    QPushButton[styleClass="negativeAction"] {
        background-color: #cc4d4d; 
        color: white;
    }
    QPushButton[styleClass="saveWipBtn"] {
        background-color: #cc9980; 
        color: black;
    }
    QPushButton[styleClass="masterBtn"] {
        background-color: #e6b366; 
        color: black;
    }
    QPushButton[styleClass="reviveBtn"] {
        background-color: #80b3b3; 
        color: black;
    }
    QPushButton[styleClass="neutralAction"] {
        background-color: #cccccc; 
        color: black;
    }
"""

class opsMainUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.UIObjects = UIObjects.UIObjects()
        self.setWindowTitle("openPypeline Studio")
        self.setObjectName("openPypelineUI")
        self.setMinimumSize(450, 780)
        
        ui_dir = os.path.dirname(__file__)
        self.ops_icon_filePath = os.path.join(ui_dir, 'opsIcon.png').replace("\\", "/")
        self.ops_currOpenPreview_filePath = os.path.join(ui_dir, 'noPreview.png').replace("\\", "/")
        self.ops_defaultPreview_filePath = os.path.join(ui_dir, 'defaultPreview.png').replace("\\", "/")
        
        self.anno_projectList="Select from the available Projects."
        self.anno_projectManager="Open the Project Manager, where you can add or remove Projects."
        self.anno_saveWorkshop="Save a WIP file for the current Asset/Shot/Component."
        self.anno_master="Save a master file for the current Asset/Shot/Component."
        self.anno_revive="Revive an old version of the current Asset/Shot/Component."
        self.anno_closeFile="Close the currently open file."
        self.anno_assetTypeList="Choose an Asset Type."
        self.anno_newAssetType="Create a new Asset Type"
        self.anno_removeAssetType="Remove the selected Asset Type(s) from the inventory."
        self.anno_removeAsset="Remove the selected Asset from the inventory."
        self.anno_editAsset="Open the Asset for editing."
        self.anno_viewAsset="Open the master file for the Asset."
        self.anno_importAssetWorkshop="Import the Asset's latest WIP file into the current scene."
        self.anno_importAssetMaster="Import the Asset's master file into the current scene."
        self.anno_referenceAssetWorkshop="Reference the Asset's latest WIP file into the current scene."
        self.anno_referenceAssetMaster="Reference the Asset's master file into the current scene."
        self.anno_assetList="Double-click to edit Asset. Hold right mouse button for more options."
        self.anno_renameAsset="Rename the selected Asset."
        self.anno_editComponent="Open the Component for editing."
        self.anno_viewComponent="Open the master file for the Component."
        self.anno_importComponentWorkshop="Import the Component's latest WIP file into the current scene."
        self.anno_importComponentMaster="Import the Component's master file into the current scene."
        self.anno_referenceComponentWorkshop="Reference the Component's latest WIP file into the current scene."
        self.anno_referenceComponentMaster="Reference the Component's master file into the current scene."
        self.anno_componentList="Double-click to edit Component. Hold down right mouse button for more options."
        self.anno_newComponent="Create a new Component for the selected Asset."
        self.anno_removeComponent="Remove the selected Component from the inventory."
        self.anno_close="Close openPipeline."
        self.anno_sequenceList="Choose a Sequence."
        self.anno_newSequence="Create a new Sequence"
        self.anno_removeSequence="Remove the selected Sequence from the inventory."
        self.anno_editShotComponent="Open the Component for editing."
        self.anno_viewShot="Open the master file for the Shot."
        self.anno_importShotWorkshop="Import the Shot's latest WIP file into the current scene."
        self.anno_editShot="Open the Shot for editing."
        self.anno_importShotMaster="Import the Shot's master file into the current scene."
        self.anno_referenceShotWorkshop="Reference the Shot's latest WIP file into the current scene."
        self.anno_referenceShotMaster="Reference the Shot's master file into the current scene."
        self.anno_shotList="Double-click to Edit Shot. Hold down right mouse button for more options."
        self.anno_newShot="Create a new Shot."
        self.anno_removeShot="Remove the selected Shot."
        self.anno_viewShotComponent="Open the master file for the Component."
        self.anno_importShotComponentWorkshop="Import the Component's latest WIP file into the current scene."
        self.anno_importShotComponentMaster="Import the Component's master file into the current scene."
        self.anno_referenceShotComponentWorkshop="Reference the Component's latest WIP file into the current scene."
        self.anno_referenceShotComponentMaster="Reference the Component's master file into the current scene."
        self.anno_shotComponentList="Double-click to edit Component. Hold down right mouse button for more options."
        self.anno_newShotComponent="Create a new Component for the selected Asset."
        self.anno_removeShotComponent="Remove the selected Component from the inventory."
    
        self._build_ui()

    def showWindow(self):
        """Shows the window as a dockable panel."""
        self.show(dockable=True, floating=True)
        # Safely try to refresh the UI in case the wrappers are still using cmds
        try:
            opsUIWrappers.refresh_ui()
        except Exception as e:
            logger.warning(f"Could not automatically refresh UI on show: {e}")

    def _build_ui(self):
        """Constructs the UI using PySide widgets and layouts."""
        self.setStyleSheet(OPS_STYLESHEET)
        self._build_top_menu()
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        self._build_basic_info(self.main_layout)
        
        self.ops_mainTabs_tabLayout = QtWidgets.QTabWidget()
        self.ops_mainTabs_tabLayout.currentChanged.connect(opsUIWrappers.update_working_tab)
        self.main_layout.addWidget(self.ops_mainTabs_tabLayout)
        
        self._build_asset_browser_tab()
        self._build_shot_browser_tab()
        self._build_currently_open_tab()
        self._build_bottom_buttons(self.main_layout)

    def _build_top_menu(self):
        menubar = self.menuBar()
        
        tools = menubar.addMenu("Tools")
        tools.addAction("Scene Inventory", self.on_open_scene_inventory)
        
        # Conditionally add Maya tools only if running inside Maya
        import opsEngine
        engine = opsEngine.OpsEngine()
        if engine.host_app == 'maya':
            import maya.cmds as cmds
            maya_tools = menubar.addMenu("Maya Tools")
            maya_tools.addAction("Maya Reference Editor", lambda: cmds.ReferenceEditor())
            maya_tools.addAction("Maya Project Manager", lambda: cmds.projectSetup(2))
        
        addons = menubar.addMenu("Add-ons")
        addons.addAction("How to add to this menu...", lambda: QtWidgets.QMessageBox.information(self, 'Add-ons', 'Add Python plugins directly to the addons folder.'))
        
        settings = menubar.addMenu("Settings")
        settings.addAction("Preferences...", self.on_open_settings)
        
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About openPipeline...", opsUIWrappers.about_dialog)
        help_menu.addAction("Help...", opsUIWrappers.launch_help)
        
        # --- Main Toolbar ---
        toolbar = QtWidgets.QToolBar("openPypeline Tools")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction("Scene Inventory", self.on_open_scene_inventory)

    def _build_basic_info(self, parent_layout):
        header_layout = QtWidgets.QHBoxLayout()
        info_layout = QtWidgets.QFormLayout()
        
        self.ops_userName_optionMenu = QtWidgets.QComboBox()
        self.ops_userName_optionMenu.setEnabled(False)
        info_layout.addRow("User Name:", self.ops_userName_optionMenu)
        
        proj_layout = QtWidgets.QHBoxLayout()
        self.ops_projName_optionMenu = QtWidgets.QComboBox()
        self.ops_projName_optionMenu.currentTextChanged.connect(self._on_project_changed)
        
        self.ops_projManager_btn = QtWidgets.QPushButton("Project Manager...")
        self.ops_projManager_btn.clicked.connect(lambda: getattr(self.UIObjects, 'opsProjectManagerGUI').showWindow())
        
        proj_layout.addWidget(self.ops_projName_optionMenu)
        proj_layout.addWidget(self.ops_projManager_btn)
        info_layout.addRow("Project Name:", proj_layout)
        
        self.ops_projPath_txtField = QtWidgets.QLineEdit()
        self.ops_projPath_txtField.setReadOnly(True)
        info_layout.addRow("Project Path:", self.ops_projPath_txtField)
        header_layout.addLayout(info_layout)
        
        self.ops_icon_image = QtWidgets.QLabel()
        self.ops_icon_image.setPixmap(QtGui.QPixmap(self.ops_icon_filePath))
        self.ops_icon_image.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        header_layout.addWidget(self.ops_icon_image)
        
        parent_layout.addLayout(header_layout)

    def _on_project_changed(self, text):
        opsActions.activate_project(text)
        try:
            opsUIWrappers.refresh_ui()
        except Exception as e:
            logger.warning(f"Could not refresh UI after project change: {e}")

    def _build_currently_open_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        header_lyt = QtWidgets.QHBoxLayout()
        self.ops_currOpenHeading_txt = QtWidgets.QLabel("CURRENTLY OPEN:")
        self.ops_currOpenHeading_txt.setProperty("styleClass", "headingBold")
        self.ops_currOpenHeadingVersion_txt = QtWidgets.QLabel(" ")
        self.ops_currOpenHeadingVersion_txt.setProperty("styleClass", "headingBold")
        header_lyt.addWidget(self.ops_currOpenHeading_txt)
        header_lyt.addWidget(self.ops_currOpenHeadingVersion_txt)
        header_lyt.addStretch()
        layout.addLayout(header_lyt)
        
        top_row = QtWidgets.QHBoxLayout()
        actions_group = QtWidgets.QGroupBox("Actions")
        actions_layout = QtWidgets.QGridLayout(actions_group)
        
        self.ops_currOpenSaveWorkshop_btn = QtWidgets.QPushButton("Save WIP...")
        self.ops_currOpenSaveWorkshop_btn.setProperty("styleClass", "saveWipBtn")
        self.ops_currOpenSaveWorkshop_btn.clicked.connect(opsUIWrappers.prompt_save_wip)
        
        self.ops_currOpenMaster_btn = QtWidgets.QPushButton("MASTER...")
        self.ops_currOpenMaster_btn.setProperty("styleClass", "masterBtn")
        self.ops_currOpenMaster_btn.clicked.connect(lambda: getattr(self.UIObjects, 'opsSaveMasterGUI').showWindow())
        
        self.ops_currOpenRevive_btn = QtWidgets.QPushButton("Revive...")
        self.ops_currOpenRevive_btn.setProperty("styleClass", "reviveBtn")
        self.ops_currOpenRevive_btn.clicked.connect(opsUIWrappers.prompt_revive)
        
        self.ops_currOpenClose_btn = QtWidgets.QPushButton("Close")
        self.ops_currOpenClose_btn.setProperty("styleClass", "neutralAction")
        self.ops_currOpenClose_btn.clicked.connect(opsUIWrappers.close_current)
        
        actions_layout.addWidget(self.ops_currOpenSaveWorkshop_btn, 0, 0, 1, 2)
        actions_layout.addWidget(self.ops_currOpenMaster_btn, 1, 0, 1, 2)
        actions_layout.addWidget(self.ops_currOpenRevive_btn, 2, 0)
        actions_layout.addWidget(self.ops_currOpenClose_btn, 2, 1)
        top_row.addWidget(actions_group)
        
        history_group = QtWidgets.QGroupBox("History")
        history_layout = QtWidgets.QVBoxLayout(history_group)
        self.ops_currOpenAssetNote_scrollField = QtWidgets.QTextEdit()
        self.ops_currOpenAssetNote_scrollField.setReadOnly(True)
        history_layout.addWidget(self.ops_currOpenAssetNote_scrollField)
        top_row.addWidget(history_group)
        layout.addLayout(top_row)
        
        mid_row = QtWidgets.QHBoxLayout()
        preview_group = QtWidgets.QGroupBox("Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        self.ops_currOpenPreview_img = QtWidgets.QLabel()
        self.ops_currOpenPreview_img.setPixmap(QtGui.QPixmap(self.ops_currOpenPreview_filePath))
        preview_layout.addWidget(self.ops_currOpenPreview_img)
        
        self.ops_currOpenSnapshot_btn = QtWidgets.QPushButton("Take Snapshot")
        self.ops_currOpenSnapshot_btn.clicked.connect(opsUIWrappers.take_snapshot)
        preview_layout.addWidget(self.ops_currOpenSnapshot_btn)
        
        pb_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenRecordPlayblast_btn = QtWidgets.QPushButton("Rec Playblast")
        self.ops_currOpenRecordPlayblast_btn.clicked.connect(opsUIWrappers.record_current_playblast)
        self.ops_currOpenViewPlayblast_btn = QtWidgets.QPushButton("View Playblast")
        self.ops_currOpenViewPlayblast_btn.clicked.connect(opsUIWrappers.view_playblast_current)
        pb_row.addWidget(self.ops_currOpenRecordPlayblast_btn)
        pb_row.addWidget(self.ops_currOpenViewPlayblast_btn)
        preview_layout.addLayout(pb_row)
        mid_row.addWidget(preview_group)
        
        notes_group = QtWidgets.QGroupBox("Notes")
        notes_layout = QtWidgets.QVBoxLayout(notes_group)
        self.ops_currOpen_scrollField = QtWidgets.QTextEdit()
        notes_layout.addWidget(self.ops_currOpen_scrollField)
        
        note_btn_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenClearNote_btn = QtWidgets.QPushButton("Clear")
        self.ops_currOpenClearNote_btn.clicked.connect(opsUIWrappers.clear_note)
        self.ops_currOpenSaveNote_btn = QtWidgets.QPushButton("Save")
        self.ops_currOpenSaveNote_btn.clicked.connect(opsUIWrappers.save_note)
        note_btn_row.addWidget(self.ops_currOpenClearNote_btn)
        note_btn_row.addWidget(self.ops_currOpenSaveNote_btn)
        notes_layout.addLayout(note_btn_row)
        mid_row.addWidget(notes_group)
        layout.addLayout(mid_row)
        
        loc_layout = QtWidgets.QFormLayout()
        loc_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenLocation_txtField = QtWidgets.QLineEdit()
        self.ops_currOpenLocation_txtField.setReadOnly(True)
        self.ops_currOpenExplore_btn = QtWidgets.QPushButton("explore...")
        self.ops_currOpenExplore_btn.clicked.connect(opsUIWrappers.explore_current)
        loc_row.addWidget(self.ops_currOpenLocation_txtField)
        loc_row.addWidget(self.ops_currOpenExplore_btn)
        loc_layout.addRow("Location:", loc_row)
        layout.addLayout(loc_layout)
        
        self.ops_mainTabs_tabLayout.addTab(tab, "Currently Open")

    def _build_asset_browser_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        cols_layout = QtWidgets.QHBoxLayout()
        
        self._build_asset_types_column(cols_layout)
        self._build_assets_column(cols_layout)
        self._build_asset_components_column(cols_layout)
        
        layout.addLayout(cols_layout)
        self._build_asset_info_section(layout)
        
        self.ops_mainTabs_tabLayout.addTab(tab, "Asset Browser")

    def _build_asset_types_column(self, parent_layout):
        col1 = QtWidgets.QGroupBox("Asset Types")
        col1_layout = QtWidgets.QVBoxLayout(col1)
        self.ops_assetType_txtScrollList = QtWidgets.QListWidget()
        self.ops_assetType_txtScrollList.itemSelectionChanged.connect(lambda: opsUIWrappers.update_asset_list(preserve_selection=0))
        col1_layout.addWidget(self.ops_assetType_txtScrollList)
        
        btn_lyt1 = QtWidgets.QHBoxLayout()
        self.ops_assetTypeNew_btn = QtWidgets.QPushButton("New...")
        self.ops_assetTypeNew_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetTypeNew_btn.clicked.connect(opsUIWrappers.prompt_new_asset_type)
        self.ops_assetTypeRemove_btn = QtWidgets.QPushButton("Delete")
        self.ops_assetTypeRemove_btn.setProperty("styleClass", "negativeAction")
        self.ops_assetTypeRemove_btn.clicked.connect(lambda: opsUIWrappers.remove_process(TAB_ASSET, LEVEL_1))
        btn_lyt1.addWidget(self.ops_assetTypeNew_btn)
        btn_lyt1.addWidget(self.ops_assetTypeRemove_btn)
        col1_layout.addLayout(btn_lyt1)
        parent_layout.addWidget(col1)

    def _build_assets_column(self, parent_layout):
        col2 = QtWidgets.QGroupBox("Assets")
        col2_layout = QtWidgets.QVBoxLayout(col2)
        self.ops_asset_scrollList = QtWidgets.QListWidget()
        self.ops_asset_scrollList.itemSelectionChanged.connect(lambda: opsUIWrappers.asset_selected(preserve_selection=0))
        self.ops_asset_scrollList.itemDoubleClicked.connect(lambda: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_2, 'workshop', version_offset=0))
        self.ops_asset_scrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ops_asset_scrollList.customContextMenuRequested.connect(self._asset_context_menu)
        col2_layout.addWidget(self.ops_asset_scrollList)
        
        btn_lyt2 = QtWidgets.QGridLayout()
        self.ops_assetNew_btn = QtWidgets.QPushButton("New...")
        self.ops_assetNew_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetNew_btn.clicked.connect(opsUIWrappers.prompt_new_asset)
        self.ops_assetRemove_btn = QtWidgets.QPushButton("Delete")
        self.ops_assetRemove_btn.setProperty("styleClass", "negativeAction")
        self.ops_assetRemove_btn.clicked.connect(lambda: opsUIWrappers.remove_process(TAB_ASSET, LEVEL_2))
        self.ops_assetRename_btn = QtWidgets.QPushButton("Rename...")
        self.ops_assetRename_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetRename_btn.clicked.connect(opsUIWrappers.prompt_rename_asset)
        btn_lyt2.addWidget(self.ops_assetNew_btn, 0, 0)
        btn_lyt2.addWidget(self.ops_assetRemove_btn, 0, 1)
        btn_lyt2.addWidget(self.ops_assetRename_btn, 1, 0, 1, 2)
        col2_layout.addLayout(btn_lyt2)
        parent_layout.addWidget(col2)

    def _build_asset_components_column(self, parent_layout):
        col3 = QtWidgets.QGroupBox("Components")
        col3_layout = QtWidgets.QVBoxLayout(col3)
        self.ops_componentScrollList = QtWidgets.QListWidget()
        self.ops_componentScrollList.itemSelectionChanged.connect(opsUIWrappers.component_selected)
        self.ops_componentScrollList.itemDoubleClicked.connect(lambda: opsUIWrappers.open_currently_selected(TAB_ASSET, LEVEL_3, 'workshop', version_offset=0))
        self.ops_componentScrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ops_componentScrollList.customContextMenuRequested.connect(self._asset_comp_context_menu)
        col3_layout.addWidget(self.ops_componentScrollList)
        
        btn_lyt3 = QtWidgets.QHBoxLayout()
        self.ops_componentNewButton = QtWidgets.QPushButton("New...")
        self.ops_componentNewButton.setProperty("styleClass", "positiveAction")
        self.ops_componentNewButton.clicked.connect(opsUIWrappers.prompt_new_asset_component)
        self.ops_componentRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_componentRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_componentRemoveButton.clicked.connect(lambda: opsUIWrappers.remove_process(TAB_ASSET, LEVEL_3))
        btn_lyt3.addWidget(self.ops_componentNewButton)
        btn_lyt3.addWidget(self.ops_componentRemoveButton)
        col3_layout.addLayout(btn_lyt3)
        parent_layout.addWidget(col3)

    def _build_asset_info_section(self, parent_layout):
        info_layout = QtWidgets.QHBoxLayout()
        prev_group = QtWidgets.QGroupBox("Preview")
        prev_layout = QtWidgets.QVBoxLayout(prev_group)
        self.ops_assetPreviewImage = QtWidgets.QLabel()
        self.ops_assetPreviewImage.setPixmap(QtGui.QPixmap(self.ops_defaultPreview_filePath))
        prev_layout.addWidget(self.ops_assetPreviewImage)
        self.ops_assetViewPlayblastAssetButton = QtWidgets.QPushButton("View Playblast")
        self.ops_assetViewPlayblastAssetButton.clicked.connect(lambda: opsUIWrappers.view_playblast_selected(TAB_ASSET))
        prev_layout.addWidget(self.ops_assetViewPlayblastAssetButton)
        info_layout.addWidget(prev_group)
        
        hist_group = QtWidgets.QGroupBox("History & Notes")
        hist_layout = QtWidgets.QVBoxLayout(hist_group)
        self.ops_commentField = QtWidgets.QTextEdit()
        self.ops_commentField.setReadOnly(True)
        hist_layout.addWidget(QtWidgets.QLabel("History:"))
        hist_layout.addWidget(self.ops_commentField)
        self.ops_assetNoteField = QtWidgets.QTextEdit()
        self.ops_assetNoteField.setReadOnly(True)
        self.ops_assetNoteField.setMaximumHeight(60)
        hist_layout.addWidget(QtWidgets.QLabel("Notes:"))
        hist_layout.addWidget(self.ops_assetNoteField)
        info_layout.addWidget(hist_group)
        parent_layout.addLayout(info_layout)
        
        loc_layout = QtWidgets.QFormLayout()
        loc_row = QtWidgets.QHBoxLayout()
        self.ops_assetLocationField = QtWidgets.QLineEdit()
        self.ops_assetLocationField.setReadOnly(True)
        self.ops_exploreAssetsButton = QtWidgets.QPushButton("explore...")
        self.ops_exploreAssetsButton.clicked.connect(lambda: opsUIWrappers.explore_selected(TAB_ASSET))
        loc_row.addWidget(self.ops_assetLocationField)
        loc_row.addWidget(self.ops_exploreAssetsButton)
        loc_layout.addRow("Location:", loc_row)
        parent_layout.addLayout(loc_layout)

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
        menu.exec(self.ops_asset_scrollList.mapToGlobal(position))

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
        menu.exec(self.ops_componentScrollList.mapToGlobal(position))

    def _build_shot_browser_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        cols_layout = QtWidgets.QHBoxLayout()
        
        self._build_sequences_column(cols_layout)
        self._build_shots_column(cols_layout)
        self._build_shot_components_column(cols_layout)
        
        layout.addLayout(cols_layout)
        self._build_shot_info_section(layout)
        
        self.ops_mainTabs_tabLayout.addTab(tab, "Shot Browser")

    def _build_sequences_column(self, parent_layout):
        col1 = QtWidgets.QGroupBox("Sequence")
        col1_layout = QtWidgets.QVBoxLayout(col1)
        self.ops_sequenceScrollList = QtWidgets.QListWidget()
        self.ops_sequenceScrollList.itemSelectionChanged.connect(lambda: opsUIWrappers.update_shot_list(preserve_selection=0))
        col1_layout.addWidget(self.ops_sequenceScrollList)
        
        btn_lyt1 = QtWidgets.QHBoxLayout()
        self.ops_sequenceNewButton = QtWidgets.QPushButton("New...")
        self.ops_sequenceNewButton.setProperty("styleClass", "positiveAction")
        self.ops_sequenceNewButton.clicked.connect(opsUIWrappers.prompt_new_sequence)
        self.ops_sequenceRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_sequenceRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_sequenceRemoveButton.clicked.connect(lambda: opsUIWrappers.remove_process(TAB_SHOT, LEVEL_1))
        btn_lyt1.addWidget(self.ops_sequenceNewButton)
        btn_lyt1.addWidget(self.ops_sequenceRemoveButton)
        col1_layout.addLayout(btn_lyt1)
        parent_layout.addWidget(col1)

    def _build_shots_column(self, parent_layout):
        col2 = QtWidgets.QGroupBox("Shot")
        col2_layout = QtWidgets.QVBoxLayout(col2)
        self.ops_shotScrollList = QtWidgets.QListWidget()
        self.ops_shotScrollList.itemSelectionChanged.connect(lambda: opsUIWrappers.shot_selected(preserve_selection=0))
        self.ops_shotScrollList.itemDoubleClicked.connect(lambda: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_2, 'workshop', version_offset=0))
        self.ops_shotScrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ops_shotScrollList.customContextMenuRequested.connect(self._shot_context_menu)
        col2_layout.addWidget(self.ops_shotScrollList)
        
        btn_lyt2 = QtWidgets.QHBoxLayout()
        self.ops_shotNewButton = QtWidgets.QPushButton("New...")
        self.ops_shotNewButton.setProperty("styleClass", "positiveAction")
        self.ops_shotNewButton.clicked.connect(opsUIWrappers.prompt_new_shot)
        self.ops_shotRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_shotRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_shotRemoveButton.clicked.connect(lambda: opsUIWrappers.remove_process(TAB_SHOT, LEVEL_2))
        btn_lyt2.addWidget(self.ops_shotNewButton)
        btn_lyt2.addWidget(self.ops_shotRemoveButton)
        col2_layout.addLayout(btn_lyt2)
        parent_layout.addWidget(col2)

    def _build_shot_components_column(self, parent_layout):
        col3 = QtWidgets.QGroupBox("Components")
        col3_layout = QtWidgets.QVBoxLayout(col3)
        self.ops_shotComponentScrollList = QtWidgets.QListWidget()
        self.ops_shotComponentScrollList.itemSelectionChanged.connect(opsUIWrappers.shot_component_selected)
        self.ops_shotComponentScrollList.itemDoubleClicked.connect(lambda: opsUIWrappers.open_currently_selected(TAB_SHOT, LEVEL_3, 'workshop', version_offset=0))
        self.ops_shotComponentScrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ops_shotComponentScrollList.customContextMenuRequested.connect(self._shot_comp_context_menu)
        col3_layout.addWidget(self.ops_shotComponentScrollList)
        
        btn_lyt3 = QtWidgets.QHBoxLayout()
        self.ops_shotComponentNewButton = QtWidgets.QPushButton("New...")
        self.ops_shotComponentNewButton.setProperty("styleClass", "positiveAction")
        self.ops_shotComponentNewButton.clicked.connect(opsUIWrappers.prompt_new_shot_component)
        self.ops_shotComponentRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_shotComponentRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_shotComponentRemoveButton.clicked.connect(lambda: opsUIWrappers.remove_process(TAB_SHOT, LEVEL_3))
        btn_lyt3.addWidget(self.ops_shotComponentNewButton)
        btn_lyt3.addWidget(self.ops_shotComponentRemoveButton)
        col3_layout.addLayout(btn_lyt3)
        parent_layout.addWidget(col3)

    def _build_shot_info_section(self, parent_layout):
        info_layout = QtWidgets.QHBoxLayout()
        prev_group = QtWidgets.QGroupBox("Preview")
        prev_layout = QtWidgets.QVBoxLayout(prev_group)
        self.ops_shotPreviewImage = QtWidgets.QLabel()
        self.ops_shotPreviewImage.setPixmap(QtGui.QPixmap(self.ops_defaultPreview_filePath))
        prev_layout.addWidget(self.ops_shotPreviewImage)
        self.ops_shotViewPlayblastButton = QtWidgets.QPushButton("View Playblast")
        self.ops_shotViewPlayblastButton.clicked.connect(lambda: opsUIWrappers.view_playblast_selected(TAB_SHOT))
        prev_layout.addWidget(self.ops_shotViewPlayblastButton)
        info_layout.addWidget(prev_group)
        
        hist_group = QtWidgets.QGroupBox("History & Notes")
        hist_layout = QtWidgets.QVBoxLayout(hist_group)
        self.ops_shotCommentField = QtWidgets.QTextEdit()
        self.ops_shotCommentField.setReadOnly(True)
        hist_layout.addWidget(QtWidgets.QLabel("History:"))
        hist_layout.addWidget(self.ops_shotCommentField)
        self.ops_shotInfoField = QtWidgets.QTextEdit()
        self.ops_shotInfoField.setReadOnly(True)
        self.ops_shotInfoField.setMaximumHeight(60)
        hist_layout.addWidget(QtWidgets.QLabel("Notes:"))
        hist_layout.addWidget(self.ops_shotInfoField)
        info_layout.addWidget(hist_group)
        parent_layout.addLayout(info_layout)
        
        loc_layout = QtWidgets.QFormLayout()
        loc_row = QtWidgets.QHBoxLayout()
        self.ops_shotLocationField = QtWidgets.QLineEdit()
        self.ops_shotLocationField.setReadOnly(True)
        self.ops_exploreShotsButton = QtWidgets.QPushButton("explore...")
        self.ops_exploreShotsButton.clicked.connect(lambda: opsUIWrappers.explore_selected(TAB_SHOT))
        loc_row.addWidget(self.ops_shotLocationField)
        loc_row.addWidget(self.ops_exploreShotsButton)
        loc_layout.addRow("Location:", loc_row)
        parent_layout.addLayout(loc_layout)

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
        menu.exec(self.ops_shotScrollList.mapToGlobal(position))

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
        menu.exec(self.ops_shotComponentScrollList.mapToGlobal(position))

    def _build_bottom_buttons(self, parent_layout):
        bottom_layout = QtWidgets.QHBoxLayout()
        self.ops_refreshUIButton = QtWidgets.QPushButton("Refresh UI")
        self.ops_refreshUIButton.setMinimumHeight(35)
        self.ops_refreshUIButton.clicked.connect(opsUIWrappers.refresh_ui)
        
        self.ops_closeUIButton = QtWidgets.QPushButton("Close")
        self.ops_closeUIButton.setMinimumHeight(35)
        self.ops_closeUIButton.clicked.connect(self.close)
        
        bottom_layout.addWidget(self.ops_refreshUIButton)
        bottom_layout.addWidget(self.ops_closeUIButton)
        
        parent_layout.addLayout(bottom_layout)

    # --- Menu Callbacks ---
    def on_open_scene_inventory(self, *args):
        import opsSceneInv
        opsSceneInv.show_window()

    def on_open_settings(self, *args):
        import opsSettingsGUI
        import importlib
        importlib.reload(opsSettingsGUI)
        if not hasattr(self.UIObjects, 'opsSettingsGUI'):
            self.UIObjects.opsSettingsGUI = opsSettingsGUI.opsSettingsGUI()
        self.UIObjects.opsSettingsGUI.showWindow()