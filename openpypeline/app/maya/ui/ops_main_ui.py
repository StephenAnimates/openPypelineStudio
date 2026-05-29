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

from openpypeline.core.localization import localization

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
        self.setWindowTitle("openPypeline Studio")
        self.setObjectName("openPypelineUI")
        
        # Clean up orphaned workspace control from any previous instances
        try:
            import maya.cmds as cmds
            workspace_control = self.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.deleteUI(workspace_control)
                
            # Delete any orphaned PySide widgets from previous instances
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if widget.objectName() == self.objectName() and widget != self:
                    widget.close()
                    widget.deleteLater()
        except ImportError:
            pass
            
        self.setMinimumSize(450, 780)
        
        ui_dir = os.path.dirname(__file__)
        self.ops_icon_filePath = os.path.join(ui_dir, 'ops_banner.png').replace("\\", "/")
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
    
        # Load localization strings
        localization.load_language()

        self._build_ui()

    def showWindow(self):
        """Shows the window as a dockable panel."""
        try:
            import maya.cmds as cmds
            workspace_control = self.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(workspace_control, edit=True, restore=True)
                return
        except ImportError:
            pass
            
        self.show(dockable=True, floating=True)

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
        self.main_layout.addWidget(self.ops_mainTabs_tabLayout)
        
        self._build_asset_browser_tab()
        self._build_shot_browser_tab()
        self._build_currently_open_tab()
        self._build_bottom_buttons(self.main_layout)

    def _build_top_menu(self):
        menubar = self.menuBar()
        
        tools = menubar.addMenu("Tools")
        self.action_scene_inventory = tools.addAction("Scene Inventory")
        
        # Conditionally add Maya tools only if running inside Maya
        try:
            import maya.cmds as cmds
            import maya.mel as mel
            maya_tools = menubar.addMenu("Maya Tools")
            maya_tools.addAction("Maya Reference Editor", lambda: mel.eval("ReferenceEditor"))
            maya_tools.addAction("Maya Project Manager", lambda: mel.eval('projectViewer "NewProject"'))
        except ImportError:
            pass
        
        addons = menubar.addMenu("Add-ons")
        addons.addAction("How to add to this menu...", lambda: QtWidgets.QMessageBox.information(self, 'Add-ons', 'Add Python plugins directly to the addons folder.'))
        
        settings = menubar.addMenu("Settings")
        self.action_preferences = settings.addAction("Preferences...")
        
        help_menu = menubar.addMenu("Help")
        self.action_about = help_menu.addAction("About openPypeline Studio...")
        self.action_help = help_menu.addAction("Help...")
        
        # --- Main Toolbar ---
        toolbar = QtWidgets.QToolBar("openPypeline Tools")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        self.action_toolbar_scene_inventory = toolbar.addAction("Scene Inventory")

    def _build_basic_info(self, parent_layout):
        header_layout = QtWidgets.QHBoxLayout()
        info_layout = QtWidgets.QFormLayout()
        
        self.ops_userName_optionMenu = QtWidgets.QComboBox()
        self.ops_userName_optionMenu.setEnabled(False)
        info_layout.addRow("User Name:", self.ops_userName_optionMenu)
        
        proj_layout = QtWidgets.QHBoxLayout()
        self.ops_projName_optionMenu = QtWidgets.QComboBox()
        self.ops_projName_optionMenu.setToolTip(localization.get_string("anno_projectList"))
        
        self.ops_projManager_btn = QtWidgets.QPushButton("Project Manager...")
        self.ops_projManager_btn.setToolTip(localization.get_string("anno_projectManager"))
        
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
        self.ops_currOpenSaveWorkshop_btn.setToolTip(localization.get_string("anno_saveWorkshop"))
        
        self.ops_currOpenMaster_btn = QtWidgets.QPushButton("MASTER...")
        self.ops_currOpenMaster_btn.setProperty("styleClass", "masterBtn")
        self.ops_currOpenMaster_btn.setToolTip(localization.get_string("anno_master"))
        
        self.ops_currOpenRevive_btn = QtWidgets.QPushButton("Revive...")
        self.ops_currOpenRevive_btn.setProperty("styleClass", "reviveBtn")
        self.ops_currOpenRevive_btn.setToolTip(localization.get_string("anno_revive"))
        
        self.ops_currOpenClose_btn = QtWidgets.QPushButton("Close")
        self.ops_currOpenClose_btn.setProperty("styleClass", "neutralAction")
        self.ops_currOpenClose_btn.setToolTip(localization.get_string("anno_closeFile"))
        
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
        preview_layout.addWidget(self.ops_currOpenSnapshot_btn)
        
        pb_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenRecordPlayblast_btn = QtWidgets.QPushButton("Rec Playblast")
        self.ops_currOpenViewPlayblast_btn = QtWidgets.QPushButton("View Playblast")
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
        self.ops_currOpenSaveNote_btn = QtWidgets.QPushButton("Save")
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
        loc_row.addWidget(self.ops_currOpenLocation_txtField)
        loc_row.addWidget(self.ops_currOpenExplore_btn)
        loc_layout.addRow("Location:", loc_row)
        layout.addLayout(loc_layout)
        
        self.ops_mainTabs_tabLayout.addTab(tab, "Currently Open")

    def _build_asset_browser_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._build_asset_types_column(splitter)
        self._build_assets_column(splitter)
        self._build_asset_components_column(splitter)
        
        layout.addWidget(splitter, stretch=1)
        self._build_asset_info_section(layout)
        
        self.ops_mainTabs_tabLayout.addTab(tab, "Asset Browser")

    def _build_asset_types_column(self, parent_layout):
        col1 = QtWidgets.QGroupBox("Asset Types")
        col1_layout = QtWidgets.QVBoxLayout(col1)
        self.ops_assetType_txtScrollList = QtWidgets.QListWidget()
        self.ops_assetType_txtScrollList.setToolTip(localization.get_string("anno_assetTypeList"))
        col1_layout.addWidget(self.ops_assetType_txtScrollList)
        
        btn_lyt1 = QtWidgets.QHBoxLayout()
        self.ops_assetTypeNew_btn = QtWidgets.QPushButton("New...")
        self.ops_assetTypeNew_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetTypeNew_btn.setToolTip(localization.get_string("anno_newAssetType"))
        self.ops_assetTypeRemove_btn = QtWidgets.QPushButton("Delete")
        self.ops_assetTypeRemove_btn.setProperty("styleClass", "negativeAction")
        self.ops_assetTypeRemove_btn.setToolTip(localization.get_string("anno_removeAssetType"))
        btn_lyt1.addWidget(self.ops_assetTypeNew_btn)
        btn_lyt1.addWidget(self.ops_assetTypeRemove_btn)
        col1_layout.addLayout(btn_lyt1)
        parent_layout.addWidget(col1)

    def _build_assets_column(self, parent_layout):
        col2 = QtWidgets.QGroupBox("Assets")
        col2_layout = QtWidgets.QVBoxLayout(col2)
        self.ops_asset_scrollList = QtWidgets.QListWidget()
        self.ops_asset_scrollList.setToolTip(localization.get_string("anno_assetList"))
        self.ops_asset_scrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        col2_layout.addWidget(self.ops_asset_scrollList)
        
        btn_lyt2 = QtWidgets.QGridLayout()
        self.ops_assetNew_btn = QtWidgets.QPushButton("New...")
        self.ops_assetNew_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetNew_btn.setToolTip(localization.get_string("anno_newAsset"))
        self.ops_assetRemove_btn = QtWidgets.QPushButton("Delete")
        self.ops_assetRemove_btn.setProperty("styleClass", "negativeAction")
        self.ops_assetRemove_btn.setToolTip(localization.get_string("anno_removeAsset"))
        self.ops_assetRename_btn = QtWidgets.QPushButton("Rename...")
        self.ops_assetRename_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetRename_btn.setToolTip(localization.get_string("anno_renameAsset"))
        btn_lyt2.addWidget(self.ops_assetNew_btn, 0, 0)
        btn_lyt2.addWidget(self.ops_assetRemove_btn, 0, 1)
        btn_lyt2.addWidget(self.ops_assetRename_btn, 1, 0, 1, 2)
        col2_layout.addLayout(btn_lyt2)
        parent_layout.addWidget(col2)

    def _build_asset_components_column(self, parent_layout):
        col3 = QtWidgets.QGroupBox("Components")
        col3_layout = QtWidgets.QVBoxLayout(col3)
        self.ops_componentScrollList = QtWidgets.QListWidget()
        self.ops_componentScrollList.setToolTip(localization.get_string("anno_componentList"))
        self.ops_componentScrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        col3_layout.addWidget(self.ops_componentScrollList)
        
        btn_lyt3 = QtWidgets.QHBoxLayout()
        self.ops_componentNewButton = QtWidgets.QPushButton("New...")
        self.ops_componentNewButton.setProperty("styleClass", "positiveAction")
        self.ops_componentNewButton.setToolTip(localization.get_string("anno_newComponent"))
        self.ops_componentRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_componentRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_componentRemoveButton.setToolTip(localization.get_string("anno_removeComponent"))
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
        loc_row.addWidget(self.ops_assetLocationField)
        loc_row.addWidget(self.ops_exploreAssetsButton)
        loc_layout.addRow("Location:", loc_row)
        parent_layout.addLayout(loc_layout)

    def _build_shot_browser_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._build_sequences_column(splitter)
        self._build_shots_column(splitter)
        self._build_shot_components_column(splitter)
        
        layout.addWidget(splitter, stretch=1)
        self._build_shot_info_section(layout)
        
        self.ops_mainTabs_tabLayout.addTab(tab, "Shot Browser")

    def _build_sequences_column(self, parent_layout):
        col1 = QtWidgets.QGroupBox("Sequence")
        col1_layout = QtWidgets.QVBoxLayout(col1)
        self.ops_sequenceScrollList = QtWidgets.QListWidget()
        self.ops_sequenceScrollList.setToolTip(localization.get_string("anno_sequenceList"))
        col1_layout.addWidget(self.ops_sequenceScrollList)
        
        btn_lyt1 = QtWidgets.QHBoxLayout()
        self.ops_sequenceNewButton = QtWidgets.QPushButton("New...")
        self.ops_sequenceNewButton.setProperty("styleClass", "positiveAction")
        self.ops_sequenceNewButton.setToolTip(localization.get_string("anno_newSequence"))
        self.ops_sequenceRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_sequenceRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_sequenceRemoveButton.setToolTip(localization.get_string("anno_removeSequence"))
        btn_lyt1.addWidget(self.ops_sequenceNewButton)
        btn_lyt1.addWidget(self.ops_sequenceRemoveButton)
        col1_layout.addLayout(btn_lyt1)
        parent_layout.addWidget(col1)

    def _build_shots_column(self, parent_layout):
        col2 = QtWidgets.QGroupBox("Shot")
        col2_layout = QtWidgets.QVBoxLayout(col2)
        self.ops_shotScrollList = QtWidgets.QListWidget()
        self.ops_shotScrollList.setToolTip(localization.get_string("anno_shotList"))
        self.ops_shotScrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        col2_layout.addWidget(self.ops_shotScrollList)
        
        btn_lyt2 = QtWidgets.QHBoxLayout()
        self.ops_shotNewButton = QtWidgets.QPushButton("New...")
        self.ops_shotNewButton.setProperty("styleClass", "positiveAction")
        self.ops_shotNewButton.setToolTip(localization.get_string("anno_newShot"))
        self.ops_shotRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_shotRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_shotRemoveButton.setToolTip(localization.get_string("anno_removeShot"))
        btn_lyt2.addWidget(self.ops_shotNewButton)
        btn_lyt2.addWidget(self.ops_shotRemoveButton)
        col2_layout.addLayout(btn_lyt2)
        parent_layout.addWidget(col2)

    def _build_shot_components_column(self, parent_layout):
        col3 = QtWidgets.QGroupBox("Components")
        col3_layout = QtWidgets.QVBoxLayout(col3)
        self.ops_shotComponentScrollList = QtWidgets.QListWidget()
        self.ops_shotComponentScrollList.setToolTip(localization.get_string("anno_shotComponentList"))
        self.ops_shotComponentScrollList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        col3_layout.addWidget(self.ops_shotComponentScrollList)
        
        btn_lyt3 = QtWidgets.QHBoxLayout()
        self.ops_shotComponentNewButton = QtWidgets.QPushButton("New...")
        self.ops_shotComponentNewButton.setProperty("styleClass", "positiveAction")
        self.ops_shotComponentNewButton.setToolTip(localization.get_string("anno_newShotComponent"))
        self.ops_shotComponentRemoveButton = QtWidgets.QPushButton("Delete")
        self.ops_shotComponentRemoveButton.setProperty("styleClass", "negativeAction")
        self.ops_shotComponentRemoveButton.setToolTip(localization.get_string("anno_removeShotComponent"))
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
        loc_row.addWidget(self.ops_shotLocationField)
        loc_row.addWidget(self.ops_exploreShotsButton)
        loc_layout.addRow("Location:", loc_row)
        parent_layout.addLayout(loc_layout)

    def _build_bottom_buttons(self, parent_layout):
        bottom_layout = QtWidgets.QHBoxLayout()
        self.ops_refreshUIButton = QtWidgets.QPushButton("Refresh UI")
        self.ops_refreshUIButton.setMinimumHeight(35)
        
        self.ops_closeUIButton = QtWidgets.QPushButton("Close")
        self.ops_closeUIButton.setMinimumHeight(35)
        self.ops_closeUIButton.setToolTip(localization.get_string("anno_close"))
        
        bottom_layout.addWidget(self.ops_refreshUIButton)
        bottom_layout.addWidget(self.ops_closeUIButton)
        
        parent_layout.addLayout(bottom_layout)