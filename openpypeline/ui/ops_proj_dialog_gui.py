"""Shared host-agnostic project creation and editing dialog view for openPypeline Studio.

Defines :class:`OpsProjDialogGUI`, a PySide dialog window for configuring new
studio projects or modifying existing project metadata, directory structures,
naming conventions, file formats, and assigned user rosters across standalone
tools and extensible DCC host integrations.

:File: ops_proj_dialog_gui.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)
"""

from typing import Optional

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets  # type: ignore[no-redef]

from openpypeline.core.localization import localization

# --- UI Stylesheet ---
# Internal Qt stylesheet highlighting the primary project-confirmation button.
_OPS_PROJ_DIALOG_STYLESHEET: str = """
    QPushButton[styleClass="acceptBtn"] {
        background-color: #6699cc;
        color: black;
        font-weight: bold;
    }
"""

_SUPPORTED_FORMATS: tuple[str, ...] = ("ma", "mb", "usd", "usda", "abc", "fbx")


class OpsProjDialogGUI(QtWidgets.QWidget):
    """Shared PySide window class for creating or editing a studio project.

    Presents grouped form sections for core project details (name, root path,
    status, description), custom user rosters and dates, WIP/master naming
    tokens and file formats, production subfolder names, archive/deleted paths,
    validation warnings, and confirmation buttons.

    :ivar proj_name_field: Line edit capturing the project name.
    :vartype proj_name_field: QtWidgets.QLineEdit
    :ivar proj_path_field: Read-only line edit displaying the project root path.
    :vartype proj_path_field: QtWidgets.QLineEdit
    :ivar path_override_btn: Button allowing the user to select a custom project root directory.
    :vartype path_override_btn: QtWidgets.QPushButton
    :ivar desc_field: Line edit capturing the project description.
    :vartype desc_field: QtWidgets.QLineEdit
    :ivar status_combo: Dropdown selecting ``"active"`` or ``"inactive"`` project status.
    :vartype status_combo: QtWidgets.QComboBox
    :ivar custom_users_chk: Checkbox toggling per-project custom user roster overrides.
    :vartype custom_users_chk: QtWidgets.QCheckBox
    :ivar custom_users_field: Read-only line edit displaying the assigned user list.
    :vartype custom_users_field: QtWidgets.QLineEdit
    :ivar custom_users_btn: Button opening the user assignment selector.
    :vartype custom_users_btn: QtWidgets.QPushButton
    :ivar creation_date_field: Line edit holding the project creation date.
    :vartype creation_date_field: QtWidgets.QLineEdit
    :ivar deadline_field: Line edit holding the target project deadline.
    :vartype deadline_field: QtWidgets.QLineEdit
    :ivar master_name_field: Line edit specifying the published master token.
    :vartype master_name_field: QtWidgets.QLineEdit
    :ivar master_format_combo: Dropdown selecting the published master file extension.
    :vartype master_format_combo: QtWidgets.QComboBox
    :ivar wip_name_field: Line edit specifying the WIP folder/token name.
    :vartype wip_name_field: QtWidgets.QLineEdit
    :ivar wip_format_combo: Dropdown selecting the WIP scene file extension.
    :vartype wip_format_combo: QtWidgets.QComboBox
    :ivar asset_lib_field: Line edit specifying the asset library subfolder.
    :vartype asset_lib_field: QtWidgets.QLineEdit
    :ivar scripts_field: Line edit specifying the project scripts subfolder.
    :vartype scripts_field: QtWidgets.QLineEdit
    :ivar shot_lib_field: Line edit specifying the shot/scenes subfolder.
    :vartype shot_lib_field: QtWidgets.QLineEdit
    :ivar textures_field: Line edit specifying the textures/sourceimages subfolder.
    :vartype textures_field: QtWidgets.QLineEdit
    :ivar renders_field: Line edit specifying the renders output subfolder.
    :vartype renders_field: QtWidgets.QLineEdit
    :ivar particles_field: Line edit specifying the particles cache subfolder.
    :vartype particles_field: QtWidgets.QLineEdit
    :ivar archive_field: Line edit specifying the archive directory path.
    :vartype archive_field: QtWidgets.QLineEdit
    :ivar archive_btn: Button opening a folder browser for :attr:`archive_field`.
    :vartype archive_btn: QtWidgets.QPushButton
    :ivar deleted_field: Line edit specifying the deleted-items directory path.
    :vartype deleted_field: QtWidgets.QLineEdit
    :ivar deleted_btn: Button opening a folder browser for :attr:`deleted_field`.
    :vartype deleted_btn: QtWidgets.QPushButton
    :ivar validation_warning_label: Centered status label displaying form validation errors.
    :vartype validation_warning_label: QtWidgets.QLabel
    :ivar accept_btn: Primary button validating and saving the project configuration.
    :vartype accept_btn: QtWidgets.QPushButton
    :ivar cancel_btn: Button closing the dialog without saving changes.
    :vartype cancel_btn: QtWidgets.QPushButton
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize the Project Dialog window dimensions, flags, and layout.

        :param parent: Optional parent widget for host window parenting.
        """
        super().__init__(parent=parent)

        self.setWindowTitle(localization.get_string("win_createProject"))
        self.setObjectName("openPypelineProjDialog")
        self.setMinimumSize(450, 650)
        self.setWindowFlags(QtCore.Qt.Window)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the project dialog form groups, roster controls, and action buttons."""
        self.setStyleSheet(_OPS_PROJ_DIALOG_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)

        # --- Project Settings Group ---
        settings_group = QtWidgets.QGroupBox(
            localization.get_string("grp_projectSettings")
        )
        settings_layout = QtWidgets.QFormLayout(settings_group)

        self.proj_name_field = QtWidgets.QLineEdit()
        self.proj_name_field.setMaxLength(22)
        self.proj_name_field.setToolTip(localization.get_string("anno_projName"))

        path_layout = QtWidgets.QHBoxLayout()
        self.proj_path_field = QtWidgets.QLineEdit()
        self.proj_path_field.setReadOnly(True)
        self.proj_path_field.setToolTip(localization.get_string("anno_projPath"))
        self.path_override_btn = QtWidgets.QPushButton(
            localization.get_string("btn_overrideProjectPath")
        )

        path_layout.addWidget(self.proj_path_field)
        path_layout.addWidget(self.path_override_btn)

        self.desc_field = QtWidgets.QLineEdit()
        self.desc_field.setMaxLength(250)
        self.desc_field.setToolTip(localization.get_string("anno_projDesc"))

        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(["active", "inactive"])
        self.status_combo.setToolTip(localization.get_string("anno_projStatus"))

        settings_layout.addRow(
            localization.get_string("lbl_projectName"), self.proj_name_field
        )
        settings_layout.addRow(
            localization.get_string("lbl_projectPath"), path_layout
        )
        settings_layout.addRow(
            localization.get_string("lbl_description"), self.desc_field
        )
        settings_layout.addRow(
            localization.get_string("lbl_status"), self.status_combo
        )

        main_layout.addWidget(settings_group)

        # --- Users & Dates Group ---
        users_dates_group = QtWidgets.QGroupBox(
            localization.get_string("grp_usersDates")
        )
        users_dates_layout = QtWidgets.QFormLayout(users_dates_group)

        self.custom_users_chk = QtWidgets.QCheckBox(
            localization.get_string("chk_enableCustomUsers")
        )
        self.custom_users_chk.setToolTip(localization.get_string("anno_customUsers"))

        users_layout = QtWidgets.QHBoxLayout()
        self.custom_users_field = QtWidgets.QLineEdit()
        self.custom_users_field.setReadOnly(True)
        self.custom_users_field.setEnabled(False)
        self.custom_users_btn = QtWidgets.QPushButton("...")
        self.custom_users_btn.setEnabled(False)
        users_layout.addWidget(self.custom_users_field)
        users_layout.addWidget(self.custom_users_btn)

        self.creation_date_field = QtWidgets.QLineEdit("dd/mm/year")
        self.deadline_field = QtWidgets.QLineEdit("dd/mm/year")

        users_dates_layout.addRow("", self.custom_users_chk)
        users_dates_layout.addRow(localization.get_string("lbl_users"), users_layout)
        users_dates_layout.addRow(
            localization.get_string("lbl_creationDate"), self.creation_date_field
        )
        users_dates_layout.addRow(
            localization.get_string("lbl_deadline"), self.deadline_field
        )

        main_layout.addWidget(users_dates_group)

        # --- Files Group ---
        files_group = QtWidgets.QGroupBox(
            localization.get_string("grp_filesMasterWip")
        )
        files_layout = QtWidgets.QGridLayout(files_group)
        files_group.setToolTip(localization.get_string("anno_masterName"))

        files_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_masterName")), 0, 0
        )
        self.master_name_field = QtWidgets.QLineEdit("master")
        self.master_name_field.setToolTip(localization.get_string("anno_masterName"))
        files_layout.addWidget(self.master_name_field, 0, 1)

        files_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_format")), 0, 2
        )
        self.master_format_combo = QtWidgets.QComboBox()
        self.master_format_combo.addItems(_SUPPORTED_FORMATS)
        files_layout.addWidget(self.master_format_combo, 0, 3)

        files_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_wipName")), 1, 0
        )
        self.wip_name_field = QtWidgets.QLineEdit("wip")
        self.wip_name_field.setToolTip(localization.get_string("anno_wipName"))
        files_layout.addWidget(self.wip_name_field, 1, 1)
        files_layout.setColumnStretch(1, 1)

        files_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_format")), 1, 2
        )
        self.wip_format_combo = QtWidgets.QComboBox()
        self.wip_format_combo.addItems(_SUPPORTED_FORMATS)
        files_layout.addWidget(self.wip_format_combo, 1, 3)
        files_layout.setColumnStretch(3, 1)

        main_layout.addWidget(files_group)

        # --- Sub-Folders Group ---
        subfolders_group = QtWidgets.QGroupBox(
            localization.get_string("grp_subfolders")
        )
        subfolders_layout = QtWidgets.QGridLayout(subfolders_group)
        subfolders_group.setToolTip(localization.get_string("anno_subfolders"))

        self.asset_lib_field = QtWidgets.QLineEdit("scenes/assets")
        self.scripts_field = QtWidgets.QLineEdit("scripts")
        self.shot_lib_field = QtWidgets.QLineEdit("scenes")
        self.textures_field = QtWidgets.QLineEdit("sourceimages")
        self.renders_field = QtWidgets.QLineEdit("images/renders")
        self.particles_field = QtWidgets.QLineEdit("particles")

        subfolders_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_assetLibrary")), 0, 0
        )
        subfolders_layout.addWidget(self.asset_lib_field, 0, 1)
        subfolders_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_scripts")), 0, 2
        )
        subfolders_layout.addWidget(self.scripts_field, 0, 3)

        subfolders_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_shotLibrary")), 1, 0
        )
        subfolders_layout.addWidget(self.shot_lib_field, 1, 1)
        subfolders_layout.setColumnStretch(1, 1)
        subfolders_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_textures")), 1, 2
        )
        subfolders_layout.addWidget(self.textures_field, 1, 3)

        subfolders_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_renders")), 2, 0
        )
        subfolders_layout.addWidget(self.renders_field, 2, 1)
        subfolders_layout.addWidget(
            QtWidgets.QLabel(localization.get_string("lbl_particles")), 2, 2
        )
        subfolders_layout.addWidget(self.particles_field, 2, 3)
        subfolders_layout.setColumnStretch(3, 1)

        main_layout.addWidget(subfolders_group)

        # --- Archive / Deleted Group ---
        archive_group = QtWidgets.QGroupBox(
            localization.get_string("grp_archiveDeleted")
        )
        archive_layout = QtWidgets.QFormLayout(archive_group)

        arch_layout = QtWidgets.QHBoxLayout()
        self.archive_field = QtWidgets.QLineEdit("archive")
        self.archive_btn = QtWidgets.QPushButton(localization.get_string("btn_browse"))
        arch_layout.addWidget(self.archive_field)
        arch_layout.addWidget(self.archive_btn)

        del_layout = QtWidgets.QHBoxLayout()
        self.deleted_field = QtWidgets.QLineEdit("deleted")
        self.deleted_btn = QtWidgets.QPushButton(localization.get_string("btn_browse"))
        del_layout.addWidget(self.deleted_field)
        del_layout.addWidget(self.deleted_btn)

        archive_layout.addRow(localization.get_string("lbl_archive"), arch_layout)
        archive_layout.addRow(
            localization.get_string("lbl_deletedItems"), del_layout
        )

        # Ensure form inputs expand evenly across platforms (macOS defaults to fixed size hints)
        for form in (settings_layout, users_dates_layout, archive_layout):
            form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        main_layout.addWidget(archive_group)
        main_layout.addStretch()

        # --- Validation Warning Label ---
        self.validation_warning_label = QtWidgets.QLabel("")
        self.validation_warning_label.setStyleSheet("color: #cc4d4d; font-weight: bold;")
        self.validation_warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.validation_warning_label.setWordWrap(True)
        self.validation_warning_label.setMinimumHeight(20)

        main_layout.addWidget(self.validation_warning_label)

        # --- Bottom Action Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.accept_btn = QtWidgets.QPushButton(localization.get_string("btn_accept"))
        self.accept_btn.setProperty("styleClass", "acceptBtn")
        self.accept_btn.setMinimumHeight(35)

        self.cancel_btn = QtWidgets.QPushButton(localization.get_string("btn_cancel"))
        self.cancel_btn.setMinimumHeight(35)

        btn_layout.addWidget(self.accept_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)
