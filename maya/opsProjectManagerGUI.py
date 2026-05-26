"""
Module: opsProjectManagerGUI.py

Description:
    Creates the openPypeline Studio Project Manager UI.
    
"""

import maya.cmds as cmds
import importlib
import window as window
importlib.reload(window)

import UIObjects as UIObjects

class opsProjectManagerGUI(window.window):
    """
    A Maya window class for managing openPypeline Studio projects.
    It allows users to select, create, edit, and remove projects, as well as
    manage user permissions and set up default pipeline paths.
    """

    def __init__(self):
        """
        Initializes the Project Manager window. Sets up dimensions, names,
        and fetches current script and project locations from Maya's optionVars.
        """
        
        self.UIObjects = UIObjects.UIObjects()
        
        self.width=550
        self.height=460
        self.name = "openPypeline Studio Project Manager"
        self.dockable=0
        self.scriptLocation = cmds.optionVar(query="ops_scriptPath") if cmds.optionVar(exists="ops_scriptPath") else "Not Set"
        self.projectLocation = cmds.optionVar(query="ops_projectFilePath") if cmds.optionVar(exists="ops_projectFilePath") else "Not Set"
    
    def content(self):
        """
        Builds and returns the main form layout for the Project Manager UI.
        Constructs the UI in logical sections and then positions them.
        """
        # Main container for the project manager UI
        self.form1 = cmds.formLayout('opsProjectManagerGUI_form', numberOfDivisions=100)
        
        # Sequentially build logical sections of the UI
        self._build_locations_section()
        self._build_project_list_section()
        self._build_project_buttons_subform()
        self._build_project_info_section()
        self._build_action_buttons()
        
        # Organize and position all built elements within the main form
        self._attach_form_elements()
        
        # Populate the initial list of projects
        self.on_refresh_list()
        
        return [self.form1]

    def _build_locations_section(self):
        """Builds the fields displaying current script and project file locations."""
        self.ops_scriptLocation_txt = cmds.text('ops_scriptLocation_txt', parent=self.form1, align="right", l="Script Location:", w=110)
        self.ops_scriptLocation_txtField = cmds.textField('ops_scriptLocation_txtField', parent=self.form1, editable=0, tx=self.scriptLocation)
        self.ops_projFileLocation_txt = cmds.text('ops_projFileLocation_txt', parent=self.form1, align="right", l="Project File Location:", w=110)
        self.ops_projFPath_txtField = cmds.textField('ops_projFPath_txtField', parent=self.form1, editable=0, tx=self.projectLocation)
        self.ops_setup_btn = cmds.button('ops_setup_btn', parent=self.form1, l="Edit\nLocations...", h=45, c=self.on_edit_locations)
        
    def _build_project_list_section(self):
        """Builds the project selection list and the user management button."""
        self.ops_editUsers_btn = cmds.button('ops_editUsers_btn', l="Edit Users", parent=self.form1, c=self.on_edit_users, ann="Add / Remove users to system")
        self.ops_projectList_txtScrollList = cmds.textScrollList('ops_projectList_txtScrollList', parent=self.form1, sc=self.on_project_selection, doubleClickCommand=self.on_edit_project)
        
    def _build_project_buttons_subform(self):
        """Builds the sub-form layout containing project action buttons (New, Edit, Remove)."""
        self.form2 = cmds.formLayout('opsProjectManagerGUI_form2', parent=self.form1, numberOfDivisions=100)
        
        self.ops_projNew_btn = cmds.button('ops_projNew_btn', parent=self.form2, l="New...", bgc=(.6, .8, .5), c=self.on_new_project, ann="") 
        self.ops_projRm_btn = cmds.button('ops_projRm_btn', parent=self.form2, l="Remove", bgc=(.8, .3, .3), en=0, c=self.on_remove_project, ann="")
        self.ops_projEdit_btn = cmds.button('ops_projEdit_btn', parent=self.form2, l="Edit..", bgc=(.5, .7, .7), en=0, c=self.on_edit_project, ann="")

        cmds.formLayout(
            self.form2,
            edit=True,
            attachPosition=[
                (self.ops_projNew_btn, 'left', 0, 0),
                (self.ops_projNew_btn, 'right', 0, 50),
                (self.ops_projRm_btn, 'left', 0, 50),
                (self.ops_projRm_btn, 'right', 0, 100),
                (self.ops_projEdit_btn, 'left', 0, 0),
                (self.ops_projEdit_btn, 'right', 0, 100),
                (self.ops_projEdit_btn, 'bottom', 0, 100),
            ],
            attachControl=[
                (self.ops_projNew_btn, 'bottom', 2, self.ops_projEdit_btn),
                (self.ops_projRm_btn, 'bottom', 2, self.ops_projEdit_btn),
            ]
        )
        
    def _build_project_info_section(self):
        """Builds the uneditable scroll field used to display detailed project info."""
        self.ops_projInfo_txt = cmds.text('ops_projInfo_txt', parent=self.form1, l="Project Info", fn="plainLabelFont", al="left")
        self.ops_projInfo_scrollField = cmds.scrollField('ops_projInfo_scrollField', parent=self.form1, ww=1, editable=0)
        
    def _build_action_buttons(self):
        """Builds the main Refresh and Close buttons for the dialog."""
        self.ops_refresh_btn = cmds.button('ops_refresh_btn', parent=self.form1, height=30, l="Refresh List", c=self.on_refresh_list)
        self.ops_close_btn = cmds.button('ops_close_btn', parent=self.form1, height=30, l="Close", c=self.on_close)  
                
    def _attach_form_elements(self):
        """
        Positions all the created UI elements within the main form layout.
        Uses percentages (attachPosition), edges (attachForm), and 
        relative snapping (attachControl) to build a responsive grid.
        """
        cmds.formLayout(
            self.form1,
            edit=True,
            attachPosition=[
                (self.ops_scriptLocation_txtField, 'right', 90, 100),
                (self.ops_projFPath_txtField, 'right', 90, 100),
                (self.ops_projectList_txtScrollList, 'right', 0, 30),
                (self.ops_projInfo_txt, 'right', 2, 100),
                (self.ops_projInfo_scrollField, 'right', 5, 100),
                (self.ops_editUsers_btn, 'right', 0, 30),
                (self.form2, 'right', 0, 30),
                (self.ops_refresh_btn, 'right', 0, 50),
                (self.ops_close_btn, 'left', 0, 50),
                (self.ops_close_btn, 'right', 5, 100),
                (self.ops_close_btn, 'bottom', 5, 100),
                (self.ops_refresh_btn, 'bottom', 5, 100),
                (self.ops_setup_btn, 'right', 2, 100),
                (self.ops_setup_btn, 'top', 2, 0),
            ],
            attachForm=[
                (self.ops_scriptLocation_txt, 'top', 2),
                (self.ops_scriptLocation_txt, 'left', 2),
                (self.ops_scriptLocation_txtField, 'top', 2),
                (self.ops_projFileLocation_txt, 'left', 2),
                (self.ops_editUsers_btn, 'left', 10),
                (self.ops_projectList_txtScrollList, 'left', 10),
                (self.form2, 'left', 10),
                (self.ops_refresh_btn, 'left', 10),
            ],
            attachControl=[
                (self.ops_scriptLocation_txtField, 'left', 2, self.ops_scriptLocation_txt),
                (self.ops_projFileLocation_txt, 'top', 2, self.ops_scriptLocation_txtField),
                (self.ops_projFPath_txtField, 'top', 2, self.ops_scriptLocation_txtField),
                (self.ops_projFPath_txtField, 'left', 2, self.ops_projFileLocation_txt),
                (self.ops_setup_btn, 'left', 2, self.ops_scriptLocation_txtField),
                (self.ops_editUsers_btn, 'top', 30, self.ops_projFileLocation_txt),
                (self.ops_projectList_txtScrollList, 'top', 2, self.ops_editUsers_btn),
                (self.ops_projectList_txtScrollList, 'bottom', 2, self.form2),
                (self.ops_projInfo_scrollField, 'top', 30, self.ops_projInfo_txt),
                (self.ops_projInfo_txt, 'top', 50, self.ops_projFileLocation_txt),
                (self.ops_projInfo_txt, 'left', 30, self.form2),
                (self.ops_projInfo_scrollField, 'top', 2, self.ops_projInfo_txt),
                (self.ops_projInfo_scrollField, 'left', 30, self.form2),
                (self.form2, 'bottom', 20, self.ops_refresh_btn),
                (self.ops_projInfo_scrollField, 'bottom', 20, self.ops_refresh_btn),
            ]
        )

    # --- Button Callbacks ---

    def on_edit_locations(self, *args):
        """Launches the Setup UI to change the script or project paths."""
        import opsLoader
        import importlib
        importlib.reload(opsLoader)
        opsLoader.openPypelineSetup()
        
    def on_edit_users(self, *args):
        """Launches the UI to edit user permissions."""
        import opsProject
        opsProject.proj_edit_users()
        
    def on_project_selection(self, *args):
        """Updates the UI info field when a project is selected."""
        selected = cmds.textScrollList(self.ops_projectList_txtScrollList, query=True, selectItem=True)
        if not selected:
            return
        
        # Enable Edit and Remove buttons
        cmds.button(self.ops_projEdit_btn, edit=True, enable=True)
        cmds.button(self.ops_projRm_btn, edit=True, enable=True)
        
        # Fetch and display project info
        import opsProject
        info_string = opsProject.get_project_info_string(selected[0])
        cmds.scrollField(self.ops_projInfo_scrollField, edit=True, text=info_string)
        
    def on_new_project(self, *args):
        """Launches the Project Dialog window in 'New' mode."""
        self.UIObjects.opsProjDialogGUI.mode = 0
        self.UIObjects.opsProjDialogGUI.old_name = ""
        self.UIObjects.opsProjDialogGUI.showWindow()
        
    def on_edit_project(self, *args):
        """Launches the Project Dialog window in 'Edit' mode."""
        selected = cmds.textScrollList(self.ops_projectList_txtScrollList, query=True, selectItem=True)
        if not selected:
            return
            
        self.UIObjects.opsProjDialogGUI.mode = 1
        self.UIObjects.opsProjDialogGUI.old_name = selected[0]
        self.UIObjects.opsProjDialogGUI.showWindow()
        
    def on_remove_project(self, *args):
        """Prompts the user and removes the selected project configuration."""
        selected = cmds.textScrollList(self.ops_projectList_txtScrollList, query=True, selectItem=True)
        if not selected:
            return
            
        proj_name = selected[0]
        res = cmds.confirmDialog(
            title="Remove Project Confirm", 
            message=f"Are you sure you want to remove project {proj_name}?",
            button=["Yes", "Cancel"], 
            defaultButton="Yes", 
            cancelButton="Cancel", 
            dismissString="Cancel"
        )
        
        if res == "Yes":
            import opsActions
            if opsActions.remove_project(proj_name):
                self.on_refresh_list()
            else:
                cmds.error("Project was not found.")
                
    def on_refresh_list(self, *args):
        """Clears and rebuilds the list of available projects."""
        import opsProject
        import opsUtils
        
        cmds.textScrollList(self.ops_projectList_txtScrollList, edit=True, removeAll=True)
        
        proj_list = [opsUtils.get_xml_data(p, "name") for p in opsProject.get_projects_data()]
        for p in proj_list:
            cmds.textScrollList(self.ops_projectList_txtScrollList, edit=True, append=p)
            
        cmds.scrollField(self.ops_projInfo_scrollField, edit=True, text="")
        cmds.button(self.ops_projEdit_btn, edit=True, enable=False)
        cmds.button(self.ops_projRm_btn, edit=True, enable=False)
        
    def on_close(self, *args):
        """Closes the Project Manager UI."""
        import opsProject
        opsProject.close_proj_ui()