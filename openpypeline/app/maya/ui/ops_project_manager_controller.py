"""
Module: ops_project_manager_controller.py

Description:
    The Controller class for the openPypeline Studio Project Manager.
    Handles logic for browsing locations, refreshing the list of projects,
    and launching the creation/edit dialogues.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

from PySide6 import QtWidgets, QtCore

from . import ui_objects as UIObjects
from ..core import ops_loader as opsLoader
from ..core import ops_project as opsProject
from ..core import ops_actions as opsActions
from ..core import ops_utils as opsUtils
from openpypeline.core.util import prefs
from .ops_project_manager_gui import opsProjectManagerGUI

class OpsProjectManagerController(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.UIObjects = UIObjects.UIObjects()
        self.view = opsProjectManagerGUI()
        
        self._connect_signals()
        self._populate_initial_data()

    def showWindow(self):
        self.view.showWindow()

    def _connect_signals(self):
        self.view.edit_locations_btn.clicked.connect(self.on_edit_locations)
        self.view.edit_users_btn.clicked.connect(self.on_edit_users)
        self.view.project_list_widget.itemSelectionChanged.connect(self.on_project_selection)
        self.view.project_list_widget.itemDoubleClicked.connect(self.on_edit_project)
        self.view.new_proj_btn.clicked.connect(self.on_new_project)
        self.view.remove_proj_btn.clicked.connect(self.on_remove_project)
        self.view.edit_proj_btn.clicked.connect(self.on_edit_project)
        self.view.refresh_btn.clicked.connect(self.on_refresh_list)
        self.view.close_btn.clicked.connect(self.on_close)

    def _populate_initial_data(self):
        self.view.script_location_field.setText(opsLoader._root_path)
        self.view.project_location_field.setText(prefs.get_pref("ops_projectFilePath", "Not Set"))
        self.on_refresh_list()

    def on_edit_locations(self, *args):
        opsLoader.openPypelineSetup()
        
    def on_edit_users(self, *args):
        opsProject.proj_edit_users()
        
    def on_project_selection(self, *args):
        selected_items = self.view.project_list_widget.selectedItems()
        if not selected_items:
            self.view.edit_proj_btn.setEnabled(False)
            self.view.remove_proj_btn.setEnabled(False)
            return
        
        self.view.edit_proj_btn.setEnabled(True)
        self.view.remove_proj_btn.setEnabled(True)
        
        info_string = opsProject.get_project_info_string(selected_items[0].text())
        self.view.project_info_field.setPlainText(info_string)
        
    def on_new_project(self, *args):
        self._ensure_dialog_exists()
        self.UIObjects.opsProjDialogController.mode = 0
        self.UIObjects.opsProjDialogController.old_name = ""
        self.UIObjects.opsProjDialogController.showWindow()
        
    def on_edit_project(self, *args):
        selected_items = self.view.project_list_widget.selectedItems()
        if not selected_items:
            return
        self._ensure_dialog_exists()
        self.UIObjects.opsProjDialogController.mode = 1
        self.UIObjects.opsProjDialogController.old_name = selected_items[0].text()
        self.UIObjects.opsProjDialogController.showWindow()
        
    def _ensure_dialog_exists(self):
        import importlib
        from . import ops_proj_dialog_controller
        importlib.reload(ops_proj_dialog_controller)
        if not hasattr(self.UIObjects, 'opsProjDialogController'):
            self.UIObjects.opsProjDialogController = ops_proj_dialog_controller.OpsProjDialogController()

    def on_remove_project(self, *args):
        selected_items = self.view.project_list_widget.selectedItems()
        if not selected_items: return
        proj_name = selected_items[0].text()
        reply = QtWidgets.QMessageBox.question(self.view, "Remove Project Confirm", f"Are you sure you want to remove project {proj_name}?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.Cancel, QtWidgets.QMessageBox.StandardButton.Cancel)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if opsActions.remove_project(proj_name): self.on_refresh_list()
            else: QtWidgets.QMessageBox.warning(self.view, "Error", "Project was not found.")
                
    def on_refresh_list(self, *args):
        self.view.project_list_widget.clear()
        proj_list = [opsUtils.get_xml_data(p, "name") for p in opsProject.get_projects_data()]
        if proj_list: self.view.project_list_widget.addItems(proj_list)
        self.view.project_info_field.clear()
        self.view.edit_proj_btn.setEnabled(False)
        self.view.remove_proj_btn.setEnabled(False)
        
    def on_close(self, *args):
        opsProject.close_proj_ui()
        self.view.close()