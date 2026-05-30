"""
Module: ops_project_manager_gui.py

Description:
    Creates the openPypeline Studio Project Manager UI using PySide6.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

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
        self.setStyleSheet(OPS_PROJ_MANAGER_STYLESHEET)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # --- Top Locations Section ---
        locations_group = QtWidgets.QGroupBox("Locations")
        locations_layout = QtWidgets.QFormLayout(locations_group)
        locations_layout.setSpacing(5)

        self.script_location_field = QtWidgets.QLineEdit()
        self.script_location_field.setReadOnly(True)

        self.project_location_field = QtWidgets.QLineEdit()
        self.project_location_field.setReadOnly(True)

        self.edit_locations_btn = QtWidgets.QPushButton("Edit Locations...")
        self.edit_locations_btn.setMinimumHeight(35)

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

        self.project_list_widget = QtWidgets.QListWidget()

        project_buttons_layout = QtWidgets.QHBoxLayout()
        self.new_proj_btn = QtWidgets.QPushButton("New...")
        self.new_proj_btn.setProperty("styleClass", "positiveAction")

        self.remove_proj_btn = QtWidgets.QPushButton("Remove")
        self.remove_proj_btn.setProperty("styleClass", "negativeAction")
        self.remove_proj_btn.setEnabled(False)

        project_buttons_layout.addWidget(self.new_proj_btn)
        project_buttons_layout.addWidget(self.remove_proj_btn)

        self.edit_proj_btn = QtWidgets.QPushButton("Edit...")
        self.edit_proj_btn.setProperty("styleClass", "editAction")
        self.edit_proj_btn.setEnabled(False)

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

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setMinimumHeight(30)

        bottom_buttons_layout.addWidget(self.refresh_btn)
        bottom_buttons_layout.addWidget(self.close_btn)

        main_layout.addLayout(bottom_buttons_layout)