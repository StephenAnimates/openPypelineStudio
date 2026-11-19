"""Cross-DCC PySide setup dialog for configuring openPypeline Studio paths.

Provides :class:`OpsSetupDialog` for selecting and validating the project registry directory in any Qt-enabled host (Autodesk Maya, SideFX Houdini, or standalone PySide).

:File: ops_setup_dialog.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)
"""

import os
from typing import Any, Callable, Optional

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets  # type: ignore[no-redef]

from openpypeline.core import ops_loader as core_loader
from openpypeline.core.util import prefs


class OpsSetupDialog(QtWidgets.QDialog):
    """PySide dialog for initializing openPypeline Studio paths.

    Allows the user to accept the default project registry directory inside
    ``openpypeline/`` or specify a custom directory path before invoking an
    optional post-setup launch callback.

    :ivar project_path_initial: Initial project registry directory passed when
        constructing the dialog.
    :vartype project_path_initial: str
    :ivar on_success: Optional zero-argument callable invoked after paths are
        validated and persisted.
    :vartype on_success: Optional[Callable[[], None]]
    :ivar proj_field: Line edit displaying ``"[Default]"`` or the custom
        project registry path.
    :vartype proj_field: QtWidgets.QLineEdit
    :ivar proj_toggle_btn: Button toggling :attr:`proj_field` between default
        and editable custom modes.
    :vartype proj_toggle_btn: QtWidgets.QPushButton
    :ivar proj_browse_btn: Button opening a directory chooser for
        :attr:`proj_field`.
    :vartype proj_browse_btn: QtWidgets.QPushButton
    """

    def __init__(
        self,
        project_path: str,
        parent: Optional[QtWidgets.QWidget] = None,
        on_success: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the setup dialog and prefill any configured project path.

        :param project_path: Existing project registry path from user
            preferences, or an empty string if unset.
        :param parent: Optional parent widget for modal dialog centering.
        :param on_success: Optional callback executed after setup succeeds
            (for example, launching the host's main entry point).
        """
        super().__init__(parent)
        self.setWindowTitle("openPypeline Studio Setup")
        self.setMinimumSize(405, 200)
        self.project_path_initial = project_path
        self.on_success = on_success
        self._build_ui()

        default_proj_path = core_loader.get_default_project_file_path()
        if (
            self.project_path_initial
            and self.project_path_initial != default_proj_path
        ):
            self.toggle_project_path_field(
                force_custom=True, path=self.project_path_initial
            )

    def _build_ui(self) -> None:
        """Build the project-path editor, browse control, and accept/cancel buttons."""
        layout = QtWidgets.QVBoxLayout(self)

        # Project File Setup
        proj_label = QtWidgets.QLabel("Project File Setup:")
        proj_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(proj_label)

        proj_desc = QtWidgets.QLabel(
            'By default, the Project File will be located in the "openpypeline" folder.\n'
            "You may set a different location for the Project File here."
        )
        proj_desc.setWordWrap(True)
        layout.addWidget(proj_desc)

        proj_layout = QtWidgets.QHBoxLayout()
        self.proj_field = QtWidgets.QLineEdit("[Default]")
        self.proj_field.setReadOnly(True)
        self.proj_toggle_btn = QtWidgets.QPushButton("Edit")
        self.proj_toggle_btn.clicked.connect(self.toggle_project_path_field)
        self.proj_browse_btn = QtWidgets.QPushButton("Browse...")
        self.proj_browse_btn.setEnabled(False)
        self.proj_browse_btn.clicked.connect(self.browse_proj_path)

        proj_layout.addWidget(self.proj_field)
        proj_layout.addWidget(self.proj_toggle_btn)
        proj_layout.addWidget(self.proj_browse_btn)
        layout.addLayout(proj_layout)

        layout.addStretch()

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        accept_btn = QtWidgets.QPushButton("Accept")
        accept_btn.clicked.connect(self.setup_exec)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(accept_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_proj_path(self) -> None:
        """Choose a directory and populate the project-path field."""
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Folder"
        )
        if dir_path:
            self.proj_field.setText(
                os.path.join(dir_path, "").replace("\\", "/")
            )

    def toggle_project_path_field(
        self, *args: Any, force_custom: bool = False, path: str = ""
    ) -> None:
        """Switch between the default project path and an editable custom path.

        :param args: Optional variadic arguments passed by Qt signals (ignored).
        :param force_custom: When ``True``, forces :attr:`proj_field` into
            editable custom-path mode using ``path``.
        :param path: Custom directory path to populate when ``force_custom`` is
            ``True``.
        """
        del args
        if not self.proj_field.isReadOnly() and not force_custom:
            self.proj_field.setReadOnly(True)
            self.proj_field.setText("[Default]")
            self.proj_toggle_btn.setText("Edit")
            self.proj_browse_btn.setEnabled(False)
        else:
            project_path = (
                path
                if force_custom
                else prefs.get_pref(core_loader.PROJECT_PATH_PREF, "")
            )
            self.proj_field.setReadOnly(False)
            self.proj_field.setText(project_path)
            self.proj_toggle_btn.setText("Default")
            self.proj_browse_btn.setEnabled(True)

    def setup_exec(self) -> None:
        """Validate paths, save the project location, and run :attr:`on_success`."""
        if not self.proj_field.isReadOnly():
            proj_file_path = self.proj_field.text()
        else:
            proj_file_path = core_loader.get_default_project_file_path()

        proj_file_path = os.path.join(proj_file_path, "").replace("\\", "/")

        error = ""
        root_path = core_loader.get_root_path()
        if not core_loader.is_valid_script_path(root_path):
            error += (
                f'Core framework path not valid. Missing essential files in "{root_path}".\n'
            )
        elif not core_loader.is_valid_project_file_path(proj_file_path):
            error += (
                f'Project File path not valid. Make sure path "{proj_file_path}" exists.\n'
            )

        if not error:
            prefs.set_pref(core_loader.PROJECT_PATH_PREF, proj_file_path)
            self.accept()
            if self.on_success:
                self.on_success()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "openPypeline Studio - Project Setup Error",
                "Could not complete openPypeline Studio setup:\n" + error,
            )
