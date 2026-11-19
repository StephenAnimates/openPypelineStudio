"""Main openPypeline Studio UI view for Autodesk Maya.

Defines :class:`opsMainUI`, a dockable PySide6 window serving as the central
artist hub for navigating project hierarchies, browsing assets and shots,
managing active working scenes, and launching pipeline dialogs.

:File: ops_main_ui.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import logging
import os
from typing import Optional

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide6 import QtCore, QtGui, QtWidgets

from openpypeline.core.localization import localization

#: Module logger for main Maya UI view operations.
logger = logging.getLogger(__name__)

# --- UI Stylesheet ---
# Internal Qt stylesheet defining semantic heading and button color classes.
_OPS_STYLESHEET: str = """
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
    """Build the dockable main window for browsing and managing pipeline items.

    Constructs the primary Maya workspace-dockable window containing the
    top menu bar, header banner, project selector, Asset Browser tab, Shot
    Browser tab, Currently Open scene workspace tab, and footer controls.

    :ivar ops_icon_filePath: Path to the header banner PNG resource.
    :vartype ops_icon_filePath: str
    :ivar ops_currOpenPreview_filePath: Path to the placeholder thumbnail used
        when no active scene preview exists.
    :vartype ops_currOpenPreview_filePath: str
    :ivar ops_defaultPreview_filePath: Path to the default fallback preview
        image for asset and shot browsers.
    :vartype ops_defaultPreview_filePath: str
    :ivar main_layout: Root vertical layout inside the central widget.
    :vartype main_layout: QtWidgets.QVBoxLayout
    :ivar ops_icon_image: Label rendering the top openPypeline Studio banner.
    :vartype ops_icon_image: QtWidgets.QLabel
    :ivar ops_mainTabs_tabLayout: Primary tab widget hosting the Asset Browser,
        Shot Browser, and Currently Open tabs.
    :vartype ops_mainTabs_tabLayout: QtWidgets.QTabWidget
    :ivar menu_tools: Top-level Tools menu populated with core and Maya-specific
        utilities and dynamic add-ons.
    :vartype menu_tools: QtWidgets.QMenu
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize resources, localization, and the main window layout.

        Cleans up any orphaned Maya ``workspaceControl`` or top-level Qt
        widget instances with the same object name before resolving image
        resources, loading localization strings, and constructing the UI.

        :param parent: Optional parent widget for Maya window parenting.
        """
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

        base_dir = os.path.dirname(__file__)
        resources_dir = os.path.abspath(
            os.path.join(base_dir, "..", "..", "..", "resources")
        ).replace("\\", "/")
        self.ops_icon_filePath: str = os.path.join(
            resources_dir, "images", "ops_banner.png"
        ).replace("\\", "/")
        self.ops_currOpenPreview_filePath: str = os.path.join(
            resources_dir, "images", "ops_no_preview.png"
        ).replace("\\", "/")
        self.ops_defaultPreview_filePath: str = os.path.join(
            resources_dir, "images", "ops_default_preview.png"
        ).replace("\\", "/")

        # Load localization strings
        localization.load_language()

        self._build_ui()

    def showWindow(self) -> None:
        """Show the window as a dockable panel, restoring any existing workspace control."""
        try:
            import maya.cmds as cmds

            workspace_control = self.objectName() + "WorkspaceControl"
            if cmds.workspaceControl(workspace_control, exists=True):
                cmds.workspaceControl(workspace_control, edit=True, restore=True)
                return
        except ImportError:
            pass

        self.show(dockable=True, floating=True)

    def _build_ui(self) -> None:
        """Construct the top menus, banner, tab container, and footer controls."""
        self.setStyleSheet(_OPS_STYLESHEET)
        self._build_top_menu()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # --- Banner Image at the top ---
        self.ops_icon_image = QtWidgets.QLabel()
        self.ops_icon_image.setPixmap(QtGui.QPixmap(self.ops_icon_filePath))
        self.ops_icon_image.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.ops_icon_image)

        self._build_basic_info(self.main_layout)

        self.ops_mainTabs_tabLayout = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.ops_mainTabs_tabLayout)

        self._build_asset_browser_tab()
        self._build_shot_browser_tab()
        self._build_currently_open_tab()

        # Center and stabilize preview thumbnails so varying image dimensions don't shift layouts
        for preview_lbl in (
            self.ops_currOpenPreview_img,
            self.ops_assetPreviewImage,
            self.ops_shotPreviewImage,
        ):
            preview_lbl.setAlignment(QtCore.Qt.AlignCenter)
            preview_lbl.setMinimumSize(160, 120)

        self._build_bottom_buttons(self.main_layout)

    def _build_top_menu(self) -> None:
        """Create the localized menus for file, project, creation, and app actions."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu(localization.get_string("menu_file"))
        self.action_save_wip = file_menu.addAction(
            localization.get_string("menu_saveWip")
        )
        self.action_save_master = file_menu.addAction(
            localization.get_string("menu_saveMaster")
        )
        file_menu.addSeparator()
        self.action_close = file_menu.addAction(localization.get_string("menu_close"))

        project_menu = menubar.addMenu(localization.get_string("menu_project"))
        self.action_project_manager = project_menu.addAction(
            localization.get_string("menu_projectManager")
        )
        self.action_edit_users = project_menu.addAction(
            localization.get_string("menu_editUsers")
        )

        create_menu = menubar.addMenu(localization.get_string("menu_create"))
        create_menu.addSection(localization.get_string("menu_createAssets"))
        self.action_new_asset_type = create_menu.addAction(
            localization.get_string("menu_newAssetType")
        )
        self.action_new_asset = create_menu.addAction(
            localization.get_string("menu_newAsset")
        )
        self.action_new_asset_component = create_menu.addAction(
            localization.get_string("menu_newAssetComponent")
        )
        create_menu.addSection(localization.get_string("menu_createShots"))
        self.action_new_sequence = create_menu.addAction(
            localization.get_string("menu_newSequence")
        )
        self.action_new_shot = create_menu.addAction(
            localization.get_string("menu_newShot")
        )
        self.action_new_shot_component = create_menu.addAction(
            localization.get_string("menu_newShotComponent")
        )

        self.menu_tools = menubar.addMenu(localization.get_string("menu_tools"))
        self.action_scene_inventory = self.menu_tools.addAction(
            localization.get_string("menu_sceneInventory")
        )

        # Conditionally add Maya tools only if running inside Maya
        try:
            import maya.mel as mel

            self.menu_tools.addSection(localization.get_string("menu_mayaTools"))
            self.menu_tools.addAction(
                localization.get_string("menu_mayaReferenceEditor"),
                lambda: mel.eval("ReferenceEditor;"),
            )
            self.menu_tools.addAction(
                localization.get_string("menu_mayaProjectWindow"),
                lambda: mel.eval("ProjectWindow;"),
            )
        except ImportError:
            pass

        settings = menubar.addMenu(localization.get_string("menu_settings"))
        self.action_preferences = settings.addAction(
            localization.get_string("menu_preferences")
        )

        window_menu = menubar.addMenu(localization.get_string("menu_window"))
        self.action_reset_window_size = window_menu.addAction(
            localization.get_string("menu_resetWindowSize")
        )

        help_menu = menubar.addMenu(localization.get_string("menu_help"))
        self.action_about = help_menu.addAction(localization.get_string("menu_about"))
        self.action_help = help_menu.addAction(
            localization.get_string("menu_helpAction")
        )

    def _build_basic_info(self, parent_layout: QtWidgets.QVBoxLayout) -> None:
        """Add user, project selector, and project path controls to ``parent_layout``.

        :param parent_layout: Parent vertical box layout receiving the header
            project summary form.
        """
        info_layout = QtWidgets.QFormLayout()
        info_layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )

        self.ops_userName_optionMenu = QtWidgets.QComboBox()
        self.ops_userName_optionMenu.setEnabled(False)
        info_layout.addRow(
            localization.get_string("lbl_userName"), self.ops_userName_optionMenu
        )

        self.ops_projName_optionMenu = QtWidgets.QComboBox()
        self.ops_projName_optionMenu.setToolTip(
            localization.get_string("anno_projectList")
        )
        info_layout.addRow(
            localization.get_string("lbl_projectName"),
            self.ops_projName_optionMenu,
        )

        self.ops_projPath_txtField = QtWidgets.QLineEdit()
        self.ops_projPath_txtField.setReadOnly(True)
        info_layout.addRow(
            localization.get_string("lbl_projectPath"),
            self.ops_projPath_txtField,
        )

        parent_layout.addLayout(info_layout)

    def _build_currently_open_tab(self) -> None:
        """Create the tab for actions, preview, notes, and history of the open item."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        header_lyt = QtWidgets.QHBoxLayout()
        self.ops_currOpenHeading_txt = QtWidgets.QLabel(
            localization.get_string("lbl_currentlyOpen")
        )
        self.ops_currOpenHeading_txt.setProperty("styleClass", "headingBold")
        self.ops_currOpenHeadingVersion_txt = QtWidgets.QLabel(" ")
        self.ops_currOpenHeadingVersion_txt.setProperty("styleClass", "headingBold")
        header_lyt.addWidget(self.ops_currOpenHeading_txt)
        header_lyt.addWidget(self.ops_currOpenHeadingVersion_txt)
        header_lyt.addStretch()
        layout.addLayout(header_lyt)

        top_row = QtWidgets.QHBoxLayout()
        actions_group = QtWidgets.QGroupBox(localization.get_string("grp_actions"))
        actions_layout = QtWidgets.QGridLayout(actions_group)

        self.ops_currOpenSaveWorkshop_btn = QtWidgets.QPushButton(
            localization.get_string("btn_saveWip")
        )
        self.ops_currOpenSaveWorkshop_btn.setProperty("styleClass", "saveWipBtn")
        self.ops_currOpenSaveWorkshop_btn.setToolTip(
            localization.get_string("anno_saveWorkshop")
        )

        self.ops_currOpenMaster_btn = QtWidgets.QPushButton(
            localization.get_string("btn_master")
        )
        self.ops_currOpenMaster_btn.setProperty("styleClass", "masterBtn")
        self.ops_currOpenMaster_btn.setToolTip(
            localization.get_string("anno_master")
        )

        self.ops_currOpenRevive_btn = QtWidgets.QPushButton(
            localization.get_string("btn_revive")
        )
        self.ops_currOpenRevive_btn.setProperty("styleClass", "reviveBtn")
        self.ops_currOpenRevive_btn.setToolTip(
            localization.get_string("anno_revive")
        )

        self.ops_currOpenClose_btn = QtWidgets.QPushButton(
            localization.get_string("btn_close")
        )
        self.ops_currOpenClose_btn.setProperty("styleClass", "neutralAction")
        self.ops_currOpenClose_btn.setToolTip(
            localization.get_string("anno_closeFile")
        )

        actions_layout.addWidget(self.ops_currOpenSaveWorkshop_btn, 0, 0, 1, 2)
        actions_layout.addWidget(self.ops_currOpenMaster_btn, 1, 0, 1, 2)
        actions_layout.addWidget(self.ops_currOpenRevive_btn, 2, 0)
        actions_layout.addWidget(self.ops_currOpenClose_btn, 2, 1)
        top_row.addWidget(actions_group)

        history_group = QtWidgets.QGroupBox(localization.get_string("grp_history"))
        history_layout = QtWidgets.QVBoxLayout(history_group)
        self.ops_currOpenAssetNote_scrollField = QtWidgets.QTextEdit()
        self.ops_currOpenAssetNote_scrollField.setReadOnly(True)
        history_layout.addWidget(self.ops_currOpenAssetNote_scrollField)
        top_row.addWidget(history_group)
        layout.addLayout(top_row)

        mid_row = QtWidgets.QHBoxLayout()
        preview_group = QtWidgets.QGroupBox(localization.get_string("grp_preview"))
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        self.ops_currOpenPreview_img = QtWidgets.QLabel()
        self.ops_currOpenPreview_img.setPixmap(
            QtGui.QPixmap(self.ops_currOpenPreview_filePath)
        )
        preview_layout.addWidget(self.ops_currOpenPreview_img)

        self.ops_currOpenSnapshot_btn = QtWidgets.QPushButton(
            localization.get_string("btn_takeSnapshot")
        )
        preview_layout.addWidget(self.ops_currOpenSnapshot_btn)

        pb_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenRecordPlayblast_btn = QtWidgets.QPushButton(
            localization.get_string("btn_recPlayblast")
        )
        self.ops_currOpenViewPlayblast_btn = QtWidgets.QPushButton(
            localization.get_string("btn_viewPlayblast")
        )
        pb_row.addWidget(self.ops_currOpenRecordPlayblast_btn)
        pb_row.addWidget(self.ops_currOpenViewPlayblast_btn)
        preview_layout.addLayout(pb_row)
        mid_row.addWidget(preview_group)

        notes_group = QtWidgets.QGroupBox(localization.get_string("grp_notes"))
        notes_layout = QtWidgets.QVBoxLayout(notes_group)
        self.ops_currOpen_scrollField = QtWidgets.QTextEdit()
        notes_layout.addWidget(self.ops_currOpen_scrollField)

        note_btn_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenClearNote_btn = QtWidgets.QPushButton(
            localization.get_string("btn_clear")
        )
        self.ops_currOpenSaveNote_btn = QtWidgets.QPushButton(
            localization.get_string("btn_save")
        )
        note_btn_row.addWidget(self.ops_currOpenClearNote_btn)
        note_btn_row.addWidget(self.ops_currOpenSaveNote_btn)
        notes_layout.addLayout(note_btn_row)
        mid_row.addWidget(notes_group)
        layout.addLayout(mid_row)

        loc_layout = QtWidgets.QFormLayout()
        loc_row = QtWidgets.QHBoxLayout()
        self.ops_currOpenLocation_txtField = QtWidgets.QLineEdit()
        self.ops_currOpenLocation_txtField.setReadOnly(True)
        self.ops_currOpenExplore_btn = QtWidgets.QPushButton(
            localization.get_string("btn_explore")
        )
        loc_row.addWidget(self.ops_currOpenLocation_txtField)
        loc_row.addWidget(self.ops_currOpenExplore_btn)
        loc_layout.addRow(localization.get_string("lbl_location"), loc_row)
        layout.addLayout(loc_layout)

        self.ops_mainTabs_tabLayout.addTab(
            tab, localization.get_string("tab_currentlyOpen")
        )

    def _create_list_column(
        self,
        parent_layout: QtWidgets.QSplitter,
        group_key: str,
        list_tooltip_key: str,
        new_tooltip_key: str,
        remove_tooltip_key: str,
        context_menu: bool = False,
    ) -> tuple[QtWidgets.QListWidget, QtWidgets.QPushButton, QtWidgets.QPushButton]:
        """Build a browser column group containing a list widget and New/Delete buttons.

        Creates button row once and reuses it
        
        :returns: list_widget, new_btn, remove_btn
        """
        group = QtWidgets.QGroupBox(localization.get_string(group_key))
        col_layout = QtWidgets.QVBoxLayout(group)

        list_widget = QtWidgets.QListWidget()
        list_widget.setToolTip(localization.get_string(list_tooltip_key))
        if context_menu:
            list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        col_layout.addWidget(list_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        new_btn = QtWidgets.QPushButton(localization.get_string("btn_new"))
        new_btn.setProperty("styleClass", "positiveAction")
        new_btn.setToolTip(localization.get_string(new_tooltip_key))

        remove_btn = QtWidgets.QPushButton(localization.get_string("btn_delete"))
        remove_btn.setProperty("styleClass", "negativeAction")
        remove_btn.setToolTip(localization.get_string(remove_tooltip_key))

        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(remove_btn)
        col_layout.addLayout(btn_layout)
        parent_layout.addWidget(group)

        return list_widget, new_btn, remove_btn

    def _build_asset_browser_tab(self) -> None:
        """Create the asset-browser tab and its inventory and information sections."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        self._build_asset_types_column(splitter)
        self._build_assets_column(splitter)
        self._build_asset_components_column(splitter)

        layout.addWidget(splitter, stretch=1)
        self._build_asset_info_section(layout)

        self.ops_mainTabs_tabLayout.addTab(
            tab, localization.get_string("tab_assetBrowser")
        )

    def _build_asset_types_column(
        self, parent_layout: QtWidgets.QSplitter
    ) -> None:
        """Add the asset-type list and its create and delete controls."""
        (
            self.ops_assetType_txtScrollList,
            self.ops_assetTypeNew_btn,
            self.ops_assetTypeRemove_btn,
        ) = self._create_list_column(
            parent_layout,
            "grp_assetTypes",
            "anno_assetTypeList",
            "anno_newAssetType",
            "anno_removeAssetType",
        )

    def _build_asset_components_column(
        self, parent_layout: QtWidgets.QSplitter
    ) -> None:
        """Add the component list and its create and delete controls."""
        (
            self.ops_componentScrollList,
            self.ops_componentNewButton,
            self.ops_componentRemoveButton,
        ) = self._create_list_column(
            parent_layout,
            "grp_components",
            "anno_componentList",
            "anno_newComponent",
            "anno_removeComponent",
            context_menu=True,
        )

    def _build_shot_browser_tab(self) -> None:
        """Create the shot-browser tab and its inventory and information sections."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        self._build_sequences_column(splitter)
        self._build_shots_column(splitter)
        self._build_shot_components_column(splitter)

        layout.addWidget(splitter, stretch=1)
        self._build_shot_info_section(layout)

        self.ops_mainTabs_tabLayout.addTab(
            tab, localization.get_string("tab_shotBrowser")
        )

    def _build_sequences_column(
        self, parent_layout: QtWidgets.QSplitter
    ) -> None:
        """Add the sequence list and its create and delete controls."""
        (
            self.ops_sequenceScrollList,
            self.ops_sequenceNewButton,
            self.ops_sequenceRemoveButton,
        ) = self._create_list_column(
            parent_layout,
            "grp_sequence",
            "anno_sequenceList",
            "anno_newSequence",
            "anno_removeSequence",
        )

    def _build_shots_column(self, parent_layout: QtWidgets.QSplitter) -> None:
        """Add the shot list and its create and delete controls."""
        (
            self.ops_shotScrollList,
            self.ops_shotNewButton,
            self.ops_shotRemoveButton,
        ) = self._create_list_column(
            parent_layout,
            "grp_shot",
            "anno_shotList",
            "anno_newShot",
            "anno_removeShot",
            context_menu=True,
        )

    def _build_shot_components_column(
        self, parent_layout: QtWidgets.QSplitter
    ) -> None:
        """Add the shot-component list and its create and delete controls."""
        (
            self.ops_shotComponentScrollList,
            self.ops_shotComponentNewButton,
            self.ops_shotComponentRemoveButton,
        ) = self._create_list_column(
            parent_layout,
            "grp_components",
            "anno_shotComponentList",
            "anno_newShotComponent",
            "anno_removeShotComponent",
            context_menu=True,
        )

    def _build_assets_column(self, parent_layout: QtWidgets.QSplitter) -> None:
        """Add the asset list and its create, delete, and rename controls.

        :param parent_layout: Horizontal splitter hosting the asset browser
            columns.
        """
        col2 = QtWidgets.QGroupBox(localization.get_string("grp_assets"))
        col2_layout = QtWidgets.QVBoxLayout(col2)
        self.ops_asset_scrollList = QtWidgets.QListWidget()
        self.ops_asset_scrollList.setToolTip(
            localization.get_string("anno_assetList")
        )
        self.ops_asset_scrollList.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        col2_layout.addWidget(self.ops_asset_scrollList)

        btn_lyt2 = QtWidgets.QGridLayout()
        self.ops_assetNew_btn = QtWidgets.QPushButton(
            localization.get_string("btn_new")
        )
        self.ops_assetNew_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetNew_btn.setToolTip(
            localization.get_string("anno_newAsset")
        )
        self.ops_assetRemove_btn = QtWidgets.QPushButton(
            localization.get_string("btn_delete")
        )
        self.ops_assetRemove_btn.setProperty("styleClass", "negativeAction")
        self.ops_assetRemove_btn.setToolTip(
            localization.get_string("anno_removeAsset")
        )
        self.ops_assetRename_btn = QtWidgets.QPushButton(
            localization.get_string("btn_rename")
        )
        self.ops_assetRename_btn.setProperty("styleClass", "positiveAction")
        self.ops_assetRename_btn.setToolTip(
            localization.get_string("anno_renameAsset")
        )
        btn_lyt2.addWidget(self.ops_assetNew_btn, 0, 0)
        btn_lyt2.addWidget(self.ops_assetRemove_btn, 0, 1)
        btn_lyt2.addWidget(self.ops_assetRename_btn, 1, 0, 1, 2)
        col2_layout.addLayout(btn_lyt2)
        parent_layout.addWidget(col2)

    def _build_asset_info_section(
        self, parent_layout: QtWidgets.QVBoxLayout
    ) -> None:
        """Add the selected asset's metadata and location controls.

        :param parent_layout: Vertical box layout of the Asset Browser tab
            receiving the preview, history/notes, and path bar.
        """
        info_layout = QtWidgets.QHBoxLayout()
        prev_group = QtWidgets.QGroupBox(localization.get_string("grp_preview"))
        prev_layout = QtWidgets.QVBoxLayout(prev_group)
        self.ops_assetPreviewImage = QtWidgets.QLabel()
        self.ops_assetPreviewImage.setPixmap(
            QtGui.QPixmap(self.ops_defaultPreview_filePath)
        )
        prev_layout.addWidget(self.ops_assetPreviewImage)
        self.ops_assetViewPlayblastAssetButton = QtWidgets.QPushButton(
            localization.get_string("btn_viewPlayblast")
        )
        prev_layout.addWidget(self.ops_assetViewPlayblastAssetButton)
        info_layout.addWidget(prev_group)

        hist_group = QtWidgets.QGroupBox(
            localization.get_string("grp_historyNotes")
        )
        hist_layout = QtWidgets.QVBoxLayout(hist_group)
        self.ops_commentField = QtWidgets.QTextEdit()
        self.ops_commentField.setReadOnly(True)
        hist_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_history"))
        )
        hist_layout.addWidget(self.ops_commentField)
        self.ops_assetNoteField = QtWidgets.QTextEdit()
        self.ops_assetNoteField.setReadOnly(True)
        self.ops_assetNoteField.setMaximumHeight(60)
        hist_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_notes"))
        )
        hist_layout.addWidget(self.ops_assetNoteField)
        info_layout.addWidget(hist_group)
        parent_layout.addLayout(info_layout)

        loc_layout = QtWidgets.QFormLayout()
        loc_row = QtWidgets.QHBoxLayout()
        self.ops_assetLocationField = QtWidgets.QLineEdit()
        self.ops_assetLocationField.setReadOnly(True)
        self.ops_exploreAssetsButton = QtWidgets.QPushButton(
            localization.get_string("btn_explore")
        )
        loc_row.addWidget(self.ops_assetLocationField)
        loc_row.addWidget(self.ops_exploreAssetsButton)
        loc_layout.addRow(localization.get_string("lbl_location"), loc_row)
        parent_layout.addLayout(loc_layout)

    def _build_shot_info_section(
        self, parent_layout: QtWidgets.QVBoxLayout
    ) -> None:
        """Add the selected shot's metadata and location controls.

        :param parent_layout: Vertical box layout of the Shot Browser tab
            receiving the preview, history/notes, and path bar.
        """
        info_layout = QtWidgets.QHBoxLayout()
        prev_group = QtWidgets.QGroupBox(localization.get_string("grp_preview"))
        prev_layout = QtWidgets.QVBoxLayout(prev_group)
        self.ops_shotPreviewImage = QtWidgets.QLabel()
        self.ops_shotPreviewImage.setPixmap(
            QtGui.QPixmap(self.ops_defaultPreview_filePath)
        )
        prev_layout.addWidget(self.ops_shotPreviewImage)
        self.ops_shotViewPlayblastButton = QtWidgets.QPushButton(
            localization.get_string("btn_viewPlayblast")
        )
        prev_layout.addWidget(self.ops_shotViewPlayblastButton)
        info_layout.addWidget(prev_group)

        hist_group = QtWidgets.QGroupBox(
            localization.get_string("grp_historyNotes")
        )
        hist_layout = QtWidgets.QVBoxLayout(hist_group)
        self.ops_shotCommentField = QtWidgets.QTextEdit()
        self.ops_shotCommentField.setReadOnly(True)
        hist_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_history"))
        )
        hist_layout.addWidget(self.ops_shotCommentField)
        self.ops_shotInfoField = QtWidgets.QTextEdit()
        self.ops_shotInfoField.setReadOnly(True)
        self.ops_shotInfoField.setMaximumHeight(60)
        hist_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_notes"))
        )
        hist_layout.addWidget(self.ops_shotInfoField)
        info_layout.addWidget(hist_group)
        parent_layout.addLayout(info_layout)

        loc_layout = QtWidgets.QFormLayout()
        loc_row = QtWidgets.QHBoxLayout()
        self.ops_shotLocationField = QtWidgets.QLineEdit()
        self.ops_shotLocationField.setReadOnly(True)
        self.ops_exploreShotsButton = QtWidgets.QPushButton(
            localization.get_string("btn_explore")
        )
        loc_row.addWidget(self.ops_shotLocationField)
        loc_row.addWidget(self.ops_exploreShotsButton)
        loc_layout.addRow(localization.get_string("lbl_location"), loc_row)
        parent_layout.addLayout(loc_layout)

    def _build_bottom_buttons(
        self, parent_layout: QtWidgets.QVBoxLayout
    ) -> None:
        """Add the bottom-row refresh and close controls to ``parent_layout``.

        :param parent_layout: Root vertical box layout receiving the footer
            action buttons.
        """
        bottom_layout = QtWidgets.QHBoxLayout()
        self.ops_refreshUIButton = QtWidgets.QPushButton(
            localization.get_string("btn_refreshUi")
        )
        self.ops_refreshUIButton.setMinimumHeight(35)

        self.ops_closeUIButton = QtWidgets.QPushButton(
            localization.get_string("btn_close")
        )
        self.ops_closeUIButton.setMinimumHeight(35)
        self.ops_closeUIButton.setToolTip(localization.get_string("anno_close"))

        bottom_layout.addWidget(self.ops_refreshUIButton)
        bottom_layout.addWidget(self.ops_closeUIButton)

        parent_layout.addLayout(bottom_layout)
