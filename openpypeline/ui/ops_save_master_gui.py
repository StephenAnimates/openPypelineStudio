"""Shared host-agnostic UI view for publishing production master files.

Presents the Save Master switchboard window allowing artists to configure scene cleanup options (importing references and removing display layers), select the post-master scene state, bind a production tracker task, enter a custom command or release comment, and trigger publishing across standalone tools and extensible DCC host integrations.

:File: ops_save_master_gui.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

from typing import Optional

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets  # type: ignore[no-redef]

from openpypeline.core.localization import localization

# --- UI Stylesheet ---
# Internal Qt stylesheet highlighting the primary master-publish action button.
_OPS_SAVE_MASTER_STYLESHEET: str = """
    QPushButton[styleClass="masterBtn"] {
        background-color: #e6b366;
        color: black;
        font-weight: bold;
    }
"""


class OpsSaveMasterGUI(QtWidgets.QWidget):
    """Present controls for configuring and submitting a master save.

    Constructs the Save Master switchboard dialog containing cleanup checkboxes, post-publish scene-state radio buttons, production tracker task selection, custom command/comment inputs, and action buttons.

    :ivar mName: Display label used for the master publish button and custom command prompt.
    :vartype mName: str
    :ivar masterImportReferencesBox_checkBox: Checkbox toggling reference import cleanup prior to mastering.
    :vartype masterImportReferencesBox_checkBox: QtWidgets.QCheckBox
    :ivar masterDeleteLayersBox_checkBox: Checkbox toggling display layer removal prior to mastering.
    :vartype masterDeleteLayersBox_checkBox: QtWidgets.QCheckBox
    :ivar after_radio_group: Button group mapping post-master scene actions to IDs ``1`` (WIP), ``2`` (Master), and ``3`` (New Scene).
    :vartype after_radio_group: QtWidgets.QButtonGroup
    :ivar radio_workshop: Radio button selecting post-master reopen of the next WIP (ID ``1``).
    :vartype radio_workshop: QtWidgets.QRadioButton
    :ivar radio_master: Radio button selecting post-master reopen of the published master (ID ``2``).
    :vartype radio_master: QtWidgets.QRadioButton
    :ivar radio_new: Radio button selecting creation of a blank new scene after mastering (ID ``3``).
    :vartype radio_new: QtWidgets.QRadioButton
    :ivar tracker_group: Group box housing production tracking task selection.
    :vartype tracker_group: QtWidgets.QGroupBox
    :ivar task_combo: Dropdown listing available production tracker tasks for the active item.
    :vartype task_combo: QtWidgets.QComboBox
    :ivar ops_masterCommandField_txtField: Line edit capturing an optional pre/post master command string.
    :vartype ops_masterCommandField_txtField: QtWidgets.QLineEdit
    :ivar ops_masterCommentField_scrollField: Multi-line text edit capturing release notes for the published master.
    :vartype ops_masterCommentField_scrollField: QtWidgets.QTextEdit
    :ivar save_btn: Primary button triggering master publishing.
    :vartype save_btn: QtWidgets.QPushButton
    :ivar cancel_btn: Button closing the dialog without publishing.
    :vartype cancel_btn: QtWidgets.QPushButton
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the master-save options, task selector, and action buttons.

        :param parent: Optional parent widget for host window parenting.
        """
        super().__init__(parent=parent)

        self.mName: str = "Master"

        self.setWindowTitle(localization.get_string("win_masterSwitchboard"))
        self.setObjectName("opsSaveMasterGUI")
        self.setMinimumSize(350, 260)
        self.setWindowFlags(QtCore.Qt.Window)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the switchboard controls using PySide widgets and layouts."""
        self.setStyleSheet(_OPS_SAVE_MASTER_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Options Section ---
        options_group = QtWidgets.QGroupBox(
            localization.get_string("grp_options")
        )
        options_layout = QtWidgets.QVBoxLayout(options_group)

        self.masterImportReferencesBox_checkBox = QtWidgets.QCheckBox(
            localization.get_string("chk_importReferences")
        )
        self.masterImportReferencesBox_checkBox.setChecked(True)
        self.masterDeleteLayersBox_checkBox = QtWidgets.QCheckBox(
            localization.get_string("chk_deleteDisplayLayers")
        )
        self.masterDeleteLayersBox_checkBox.setChecked(True)

        options_layout.addWidget(self.masterImportReferencesBox_checkBox)
        options_layout.addWidget(self.masterDeleteLayersBox_checkBox)

        after_layout = QtWidgets.QHBoxLayout()
        after_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_afterMasterOpen"))
        )

        self.after_radio_group = QtWidgets.QButtonGroup(self)
        self.radio_workshop = QtWidgets.QRadioButton(
            localization.get_string("rad_wip")
        )
        self.radio_workshop.setChecked(True)
        self.radio_master = QtWidgets.QRadioButton(
            localization.get_string("rad_master")
        )
        self.radio_new = QtWidgets.QRadioButton(
            localization.get_string("rad_new")
        )

        self.after_radio_group.addButton(self.radio_workshop, 1)
        self.after_radio_group.addButton(self.radio_master, 2)
        self.after_radio_group.addButton(self.radio_new, 3)

        after_layout.addWidget(self.radio_workshop)
        after_layout.addWidget(self.radio_master)
        after_layout.addWidget(self.radio_new)
        after_layout.addStretch()

        options_layout.addLayout(after_layout)
        main_layout.addWidget(options_group)

        # --- Tracker Section ---
        self.tracker_group = QtWidgets.QGroupBox(
            localization.get_string("grp_productionTracking")
        )
        tracker_layout = QtWidgets.QFormLayout(self.tracker_group)
        self.task_combo = QtWidgets.QComboBox()
        tracker_layout.addRow(
            localization.get_string("lbl_selectTask"), self.task_combo
        )
        main_layout.addWidget(self.tracker_group)

        # --- Command & Comment Section ---
        cmd_layout = QtWidgets.QFormLayout()
        self.ops_masterCommandField_txtField = QtWidgets.QLineEdit()
        cmd_layout.addRow(
            localization.get_string("lbl_customCommand").format(self.mName),
            self.ops_masterCommandField_txtField,
        )

        self.ops_masterCommentField_scrollField = QtWidgets.QTextEdit()
        self.ops_masterCommentField_scrollField.setMaximumHeight(60)
        cmd_layout.addRow(
            localization.get_string("lbl_comment"),
            self.ops_masterCommentField_scrollField,
        )

        main_layout.addLayout(cmd_layout)

        # --- Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton(self.mName)
        self.save_btn.setProperty("styleClass", "masterBtn")
        self.save_btn.setMinimumHeight(35)

        self.cancel_btn = QtWidgets.QPushButton(
            localization.get_string("btn_cancel")
        )
        self.cancel_btn.setMinimumHeight(35)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)
