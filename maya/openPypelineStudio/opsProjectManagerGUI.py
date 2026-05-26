"""
Module: opsProjectManagerGUI.py

Description:
    Creates the openPypeline Studio Project Manager UI.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import importlib

import window as window
importlib.reload(window)

import UIObjects as UIObjects

class opsProjectManagerGUI(window.window):

    def __init__(self):
        
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
        """
        self.form1 = cmds.formLayout('opsProjectManagerGUI_form', numberOfDivisions=100)
        
        self._build_locations_section()
        self._build_project_list_section()
        self._build_project_buttons_subform()
        self._build_project_info_section()
        self._build_action_buttons()
        
        self._attach_form_elements()
        
        self.on_refresh_list()
        
        return [self.form1]

    def _build_locations_section(self):
        self.projManagerScriptLocation_txt = cmds.text('projManagerScriptLocation_txt', parent=self.form1, align="right", l="Script Location:", w=110)
        self.projManagerScriptLocation_txtField = cmds.textField('projManagerScriptLocation_txtField', parent=self.form1, editable=0, tx=self.scriptLocation)
        self.projManagerProjFileLocation_txt = cmds.text('projManagerProjFileLocation_txt', parent=self.form1, align="right", l="Project File Location:", w=110)
        self.projManagerProjFPath_txtField = cmds.textField('projManagerProjFPath_txtField', parent=self.form1, editable=0, tx=self.projectLocation)
        self.projManagerOpenPipelineSetup_btn = cmds.button('projManagerOpenPipelineSetup_btn', parent=self.form1, l="Edit\nLocations...", h=45, c=self.on_edit_locations)
        
    def _build_project_list_section(self):
        self.projManagerEditUsers_btn = cmds.button('projManagerEditUsers_btn', l="Edit Users", parent=self.form1, c=self.on_edit_users, ann="Add / Remove users to system")
        self.projManagerProjectList_txtScrollList = cmds.textScrollList('projManagerProjectList_txtScrollList', parent=self.form1, sc=self.on_project_selection, doubleClickCommand=self.on_edit_project)
        
    def _build_project_buttons_subform(self):
        self.form2 = cmds.formLayout('opsProjectManagerGUI_form2', parent=self.form1, numberOfDivisions=100)
        
        self.projManagerProjNew_btn = cmds.button('projManagerProjNew_btn', parent=self.form2, l="New...", bgc=(.6, .8, .5), c=self.on_new_project, ann="") 
        self.projManagerProjRm_btn = cmds.button('projManagerProjRm_btn', parent=self.form2, l="Remove", bgc=(.8, .3, .3), en=0, c=self.on_remove_project, ann="")
        self.projManagerProjEdit_btn = cmds.button('projManagerProjEdit_btn', parent=self.form2, l="Edit..", bgc=(.5, .7, .7), en=0, c=self.on_edit_project, ann="")

        cmds.formLayout(
            self.form2,
            edit=True,
            attachPosition=[
                (self.projManagerProjNew_btn, 'left', 0, 0),
                (self.projManagerProjNew_btn, 'right', 0, 50),
                (self.projManagerProjRm_btn, 'left', 0, 50),
                (self.projManagerProjRm_btn, 'right', 0, 100),
                (self.projManagerProjEdit_btn, 'left', 0, 0),
                (self.projManagerProjEdit_btn, 'right', 0, 100),
                (self.projManagerProjEdit_btn, 'bottom', 0, 100),
            ],
            attachControl=[
                (self.projManagerProjNew_btn, 'bottom', 2, self.projManagerProjEdit_btn),
                (self.projManagerProjRm_btn, 'bottom', 2, self.projManagerProjEdit_btn),
            ]
        )
        
    def _build_project_info_section(self):
        self.projManagerProjInfo_txt = cmds.text('projManagerProjInfo_txt', parent=self.form1, l="Project Info", fn="plainLabelFont", al="left")
        self.projManagerProjInfo_scrollField = cmds.scrollField('projManagerProjInfo_scrollField', parent=self.form1, ww=1, editable=0)
        
    def _build_action_buttons(self):
        self.projManagerRefresh_btn = cmds.button('projManagerRefresh_btn', parent=self.form1, height=30, l="Refresh List", c=self.on_refresh_list)
        self.projManagerClose_btn = cmds.button('projManagerClose_btn', parent=self.form1, height=30, l="Close", c=self.on_close)  
                
    def _attach_form_elements(self):
        cmds.formLayout(
            self.form1,
            edit=True,
            attachPosition=[
                (self.projManagerScriptLocation_txtField, 'right', 90, 100),
                (self.projManagerProjFPath_txtField, 'right', 90, 100),
                (self.projManagerProjectList_txtScrollList, 'right', 0, 30),
                (self.projManagerProjInfo_txt, 'right', 2, 100),
                (self.projManagerProjInfo_scrollField, 'right', 5, 100),
                (self.projManagerEditUsers_btn, 'right', 0, 30),
                (self.form2, 'right', 0, 30),
                (self.projManagerRefresh_btn, 'right', 0, 50),
                (self.projManagerClose_btn, 'left', 0, 50),
                (self.projManagerClose_btn, 'right', 5, 100),
                (self.projManagerClose_btn, 'bottom', 5, 100),
                (self.projManagerRefresh_btn, 'bottom', 5, 100),
                (self.projManagerOpenPipelineSetup_btn, 'right', 2, 100),
                (self.projManagerOpenPipelineSetup_btn, 'top', 2, 0),
            ],
            attachForm=[
                (self.projManagerScriptLocation_txt, 'top', 2),
                (self.projManagerScriptLocation_txt, 'left', 2),
                (self.projManagerScriptLocation_txtField, 'top', 2),
                (self.projManagerProjFileLocation_txt, 'left', 2),
                (self.projManagerEditUsers_btn, 'left', 10),
                (self.projManagerProjectList_txtScrollList, 'left', 10),
                (self.form2, 'left', 10),
                (self.projManagerRefresh_btn, 'left', 10),
            ],
            attachControl=[
                (self.projManagerScriptLocation_txtField, 'left', 2, self.projManagerScriptLocation_txt),
                (self.projManagerProjFileLocation_txt, 'top', 2, self.projManagerScriptLocation_txtField),
                (self.projManagerProjFPath_txtField, 'top', 2, self.projManagerScriptLocation_txtField),
                (self.projManagerProjFPath_txtField, 'left', 2, self.projManagerProjFileLocation_txt),
                (self.projManagerOpenPipelineSetup_btn, 'left', 2, self.projManagerScriptLocation_txtField),
                (self.projManagerEditUsers_btn, 'top', 30, self.projManagerProjFileLocation_txt),
                (self.projManagerProjectList_txtScrollList, 'top', 2, self.projManagerEditUsers_btn),
                (self.projManagerProjectList_txtScrollList, 'bottom', 2, self.form2),
                (self.projManagerProjInfo_scrollField, 'top', 30, self.projManagerProjInfo_txt),
                (self.projManagerProjInfo_txt, 'top', 50, self.projManagerProjFileLocation_txt),
                (self.projManagerProjInfo_txt, 'left', 30, self.form2),
                (self.projManagerProjInfo_scrollField, 'top', 2, self.projManagerProjInfo_txt),
                (self.projManagerProjInfo_scrollField, 'left', 30, self.form2),
                (self.form2, 'bottom', 20, self.projManagerRefresh_btn),
                (self.projManagerProjInfo_scrollField, 'bottom', 20, self.projManagerRefresh_btn),
            ]
        )

    # --- Button Callbacks ---

    def on_edit_locations(self, *args):
        """Launches the Setup UI to change the script or project paths."""
        import opsLoader
        opsLoader.openPypelineSetup()
        
    def on_edit_users(self, *args):
        """Launches the UI to edit user permissions."""
        import opsProject
        opsProject.proj_edit_users()
        
    def on_project_selection(self, *args):
        """Updates the UI info field when a project is selected."""
        selected = cmds.textScrollList(self.projManagerProjectList_txtScrollList, query=True, selectItem=True)
        if not selected:
            return
        
        # Enable Edit and Remove buttons
        cmds.button(self.projManagerProjEdit_btn, edit=True, enable=True)
        cmds.button(self.projManagerProjRm_btn, edit=True, enable=True)
        
        # Fetch and display project info
        import opsProject
        info_string = opsProject.get_project_info_string(selected[0])
        cmds.scrollField(self.projManagerProjInfo_scrollField, edit=True, text=info_string)
        
    def on_new_project(self, *args):
        """Launches the Project Dialog window in 'New' mode."""
        self.UIObjects.opsProjDialogGUI.showWindow()
        
    def on_edit_project(self, *args):
        """Launches the Project Dialog window in 'Edit' mode."""
        self.UIObjects.opsProjDialogGUI.showWindow()
        
    def on_remove_project(self, *args):
        """Prompts the user and removes the selected project configuration."""
        selected = cmds.textScrollList(self.projManagerProjectList_txtScrollList, query=True, selectItem=True)
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
        
        cmds.textScrollList(self.projManagerProjectList_txtScrollList, edit=True, removeAll=True)
        
        proj_list = [opsUtils.get_xml_data(p, "name") for p in opsProject.get_projects_data()]
        for p in proj_list:
            cmds.textScrollList(self.projManagerProjectList_txtScrollList, edit=True, append=p)
            
        cmds.scrollField(self.projManagerProjInfo_scrollField, edit=True, text="")
        cmds.button(self.projManagerProjEdit_btn, edit=True, enable=False)
        cmds.button(self.projManagerProjRm_btn, edit=True, enable=False)
        
    def on_close(self, *args):
        """Closes the Project Manager UI."""
        import opsProject
        opsProject.close_proj_ui()