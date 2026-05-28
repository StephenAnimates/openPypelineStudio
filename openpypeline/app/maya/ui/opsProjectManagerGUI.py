"""
Module: opsProjectManagerGUI.py

Description:
    Creates the openPypeline Studio Project Manager UI using PySide6.
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import UIObjects as UIObjects
import opsLoader
import opsProject
import opsActions
import opsUtils
from openpypeline.core.util import prefs

# --- UI Stylesheet ---
OPS_PROJ_MANAGER_STYLESHEET = """
    QPushButton[styleClass="positiveAction"] {
        background-color: #99cc80; 
        color: black;
    }
    QPushButton[styleClass="negativeAction"] {
        background-color: #cc4d4d; 
        color: white;
    }
    QPushButton[styleClass="editAction"] {
        background-color: #80b3b3; 
        color: black;
    }
"""

class opsProjectManagerGUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """
    A PySide-based Maya window for managing openPypeline Studio projects.
    It allows users to select, create, edit, and remove projects, and manage users.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.UIObjects = UIObjects.UIObjects()

        self.setWindowTitle("openPypeline Studio Project Manager")
        self.setObjectName("openPypelineStudioProjectManager")
        
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
            
        self.setMinimumSize(550, 460)

        # Fetch initial paths
        self.scriptLocation = prefs.get_pref("ops_scriptPath", "Not Set")
        self.projectLocation = prefs.get_pref("ops_projectFilePath", "Not Set")

        self._build_ui()
        self.on_refresh_list()

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
        self.setStyleSheet(OPS_PROJ_MANAGER_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # --- Top Locations Section ---
        locations_group = QtWidgets.QGroupBox("Locations")
        locations_layout = QtWidgets.QFormLayout(locations_group)
        locations_layout.setSpacing(5)

        self.script_location_field = QtWidgets.QLineEdit(self.scriptLocation)
        self.script_location_field.setReadOnly(True)

        self.project_location_field = QtWidgets.QLineEdit(self.projectLocation)
        self.project_location_field.setReadOnly(True)

        self.edit_locations_btn = QtWidgets.QPushButton("Edit Locations...")
        self.edit_locations_btn.setMinimumHeight(35)
        self.edit_locations_btn.clicked.connect(self.on_edit_locations)

        locations_layout.addRow("Script Location:", self.script_location_field)
        locations_layout.addRow("Project File Location:", self.project_location_field)
        locations_layout.addRow("", self.edit_locations_btn)

        main_layout.addWidget(locations_group)

        # --- Main Content Section (Projects & Info) ---
        main_content_layout = QtWidgets.QHBoxLayout()

        # Left side: Project List
        project_list_group = QtWidgets.QGroupBox("Projects")
        project_list_layout = QtWidgets.QVBoxLayout(project_list_group)

        self.edit_users_btn = QtWidgets.QPushButton("Edit Users")
        self.edit_users_btn.setToolTip("Add / Remove users to system")
        self.edit_users_btn.clicked.connect(self.on_edit_users)

        self.project_list_widget = QtWidgets.QListWidget()
        self.project_list_widget.itemSelectionChanged.connect(self.on_project_selection)
        self.project_list_widget.itemDoubleClicked.connect(self.on_edit_project)

        project_buttons_layout = QtWidgets.QHBoxLayout()
        self.new_proj_btn = QtWidgets.QPushButton("New...")
        self.new_proj_btn.setProperty("styleClass", "positiveAction")
        self.new_proj_btn.clicked.connect(self.on_new_project)

        self.remove_proj_btn = QtWidgets.QPushButton("Remove")
        self.remove_proj_btn.setProperty("styleClass", "negativeAction")
        self.remove_proj_btn.setEnabled(False)
        self.remove_proj_btn.clicked.connect(self.on_remove_project)

        project_buttons_layout.addWidget(self.new_proj_btn)
        project_buttons_layout.addWidget(self.remove_proj_btn)

        self.edit_proj_btn = QtWidgets.QPushButton("Edit...")
        self.edit_proj_btn.setProperty("styleClass", "editAction")
        self.edit_proj_btn.setEnabled(False)
        self.edit_proj_btn.clicked.connect(self.on_edit_project)

        project_list_layout.addWidget(self.edit_users_btn)
        project_list_layout.addWidget(self.project_list_widget)
        project_list_layout.addLayout(project_buttons_layout)
        project_list_layout.addWidget(self.edit_proj_btn)

        # Right side: Project Info
        project_info_group = QtWidgets.QGroupBox("Project Info")
        project_info_layout = QtWidgets.QVBoxLayout(project_info_group)
        self.project_info_field = QtWidgets.QTextEdit()
        self.project_info_field.setReadOnly(True)
        project_info_layout.addWidget(self.project_info_field)

        main_content_layout.addWidget(project_list_group, 1)
        main_content_layout.addWidget(project_info_group, 2)

        main_layout.addLayout(main_content_layout)

        # --- Bottom Action Buttons ---
        bottom_buttons_layout = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton("Refresh List")
        self.refresh_btn.setMinimumHeight(30)
        self.refresh_btn.clicked.connect(self.on_refresh_list)

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setMinimumHeight(30)
        self.close_btn.clicked.connect(self.on_close)

        bottom_buttons_layout.addWidget(self.refresh_btn)
        bottom_buttons_layout.addWidget(self.close_btn)

        main_layout.addLayout(bottom_buttons_layout)

    # --- Button Callbacks ---

    def on_edit_locations(self, *args):
        """Launches the Setup UI to change the script or project paths."""
        opsLoader.openPypelineSetup()
        
    def on_edit_users(self, *args):
        """Launches the UI to edit user permissions."""
        opsProject.proj_edit_users()
        
    def on_project_selection(self, *args):
        """Updates the UI info field when a project is selected."""
        selected_items = self.project_list_widget.selectedItems()
        if not selected_items:
            self.edit_proj_btn.setEnabled(False)
            self.remove_proj_btn.setEnabled(False)
            return
        
        self.edit_proj_btn.setEnabled(True)
        self.remove_proj_btn.setEnabled(True)
        
        info_string = opsProject.get_project_info_string(selected_items[0].text())
        self.project_info_field.setPlainText(info_string)
        
    def on_new_project(self, *args):
        """Launches the Project Dialog window in 'New' mode."""
        self.UIObjects.opsProjDialogGUI.mode = 0
        self.UIObjects.opsProjDialogGUI.old_name = ""
        self.UIObjects.opsProjDialogGUI.showWindow()
        
    def on_edit_project(self, *args):
        """Launches the Project Dialog window in 'Edit' mode."""
        selected_items = self.project_list_widget.selectedItems()
        if not selected_items:
            return
            
        self.UIObjects.opsProjDialogGUI.mode = 1
        self.UIObjects.opsProjDialogGUI.old_name = selected_items[0].text()
        self.UIObjects.opsProjDialogGUI.showWindow()
        
    def on_remove_project(self, *args):
        """Prompts the user and removes the selected project configuration."""
        selected_items = self.project_list_widget.selectedItems()
        if not selected_items:
            return
            
        proj_name = selected_items[0].text()
        reply = QtWidgets.QMessageBox.question(
            self,
            "Remove Project Confirm",
            f"Are you sure you want to remove project {proj_name}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Cancel
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if opsActions.remove_project(proj_name):
                self.on_refresh_list()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Project was not found.")
                
    def on_refresh_list(self, *args):
        """Clears and rebuilds the list of available projects."""
        self.project_list_widget.clear()
        
        proj_list = [opsUtils.get_xml_data(p, "name") for p in opsProject.get_projects_data()]
        if proj_list:
            self.project_list_widget.addItems(proj_list)
            
        self.project_info_field.clear()
        self.edit_proj_btn.setEnabled(False)
        self.remove_proj_btn.setEnabled(False)
        
    def on_close(self, *args):
        """Closes the Project Manager UI."""
        opsProject.close_proj_ui()
        self.close()