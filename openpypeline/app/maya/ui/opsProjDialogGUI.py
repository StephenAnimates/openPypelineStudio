"""
Module: opsProjDialogGUI.py

Description:
    Opens the Project Dialog Window. This is used either for creating a new project 
    or editing an existing project.
    
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds
import window as window
import UIObjects as UIObjects
import opsProject

class opsProjDialogGUI(window.window):
    """
    A Maya window class for creating or editing an openPypeline Studio project.
    """

    def __init__(self):
        """
        Initialize the Project Dialog window. Sets up window dimensions, names, 
        and default string values used as placeholders in the UI fields.
        """
        self.UIObjects = UIObjects.UIObjects()
        
        self.width=380
        self.height=700
        self.name = "Create New Project"
        self.dockable=0
        
        self.lfMargin = 5
        self.rtMargin = 5
        
        # Default directory and settings nomenclature
        self.ops_creationDate = 'dd/mm/year'
        self.ops_deadline = 'dd/mm/year'
        self.ops_masterFilesName = 'master'
        self.ops_workshopFilesName = 'workshop'
        self.ops_assetLibrary = 'lib'
        self.ops_scripts = 'scripts'
        self.ops_shotLibrary = 'scenes'
        self.ops_textures = 'textures'
        self.ops_renders = 'renders'
        self.ops_particles = 'particles'
        self.ops_archive = 'archive'
        self.ops_deleted = 'deleted'
    
    def content(self):
        """
        Builds and returns the main form layout for the Project Dialog UI.
        The process involves creating a master formLayout, constructing each UI 
        section sequentially, and then attaching them to their final positions.
        """
        # Main container for the dialog UI
        self.form1 = cmds.formLayout('opsProjDialogGUI_form', numberOfDivisions=100)
        
        # Sequentially build logical sections of the UI
        self._build_project_name_section()
        self._build_project_path_section()
        self._build_description_section()
        self._build_project_status_section()
        self._build_custom_users_section()
        self._build_dates_section()
        self._build_master_files_section()
        self._build_workshop_files_section()
        self._build_sub_folder_section()
        self._build_archive_deleted_section()
        self._build_action_buttons()
        
        # Organize and position all built elements within the main form
        self._attach_form_elements()
        self._populate_fields()
        
        return [self.form1]

    def _build_project_name_section(self):
        """Builds the input fields for the project's name."""
        self.ops_projName_txt =  cmds.text('ops_projName_txt', parent=self.form1, fn="boldLabelFont", label="Project  Name (max length: 22):", align="left", width=220)
        self.ops_projName_txtField = cmds.textField('ops_projName_txtField', parent=self.form1, h=20)
        self.ops_separator1 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_project_path_section(self):
        """Builds the directory browser section to define the project's root path."""
        self.ops_projPath_txt =  cmds.text('ops_projPath_txt', parent=self.form1, fn="boldLabelFont", label="Project Path:", align="left", width=90)
        self.ops_projPathParens_txt =  cmds.text('ops_projPathParens_txt', parent=self.form1, label="(folders which don't already exist will be created)", align="left", width=250)
        self.ops_pathField_txtField = cmds.textField('ops_pathField_txtField', parent=self.form1, h=20)
        self.ops_pathBrowse_btn = cmds.button('ops_pathBrowse_btn', parent=self.form1, w=60, l="Browse...", c=lambda *args: opsProject._browse_path("ops_pathField_txtField", "ops_projName_txtField"))
        self.ops_separator2 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_description_section(self):
        """Builds the project description input section."""
        self.ops_description_txt =  cmds.text('ops_description_txt', parent=self.form1, fn="boldLabelFont", label="Description:", align="left", width=80)
        self.ops_description_txtField = cmds.textField('ops_description_txtField', parent=self.form1, h=20)
        self.ops_separator3 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_project_status_section(self):
        """Builds the dropdown to set the project as active or inactive."""
        self.ops_status_txt =  cmds.text('ops_status_txt', parent=self.form1, fn="boldLabelFont", label="Project Status:", align="left", width=100)
        self.ops_status_optMenu = cmds.optionMenu('ops_status_optMenu', parent=self.form1)
        cmds.menuItem(label="active", parent=self.ops_status_optMenu)
        cmds.menuItem(label="inactive", parent=self.ops_status_optMenu)
        self.ops_statusParens_txt = cmds.text('ops_statusParens_txt', parent=self.form1, fn="smallPlainLabelFont", label="(inactive projects won't appear in main openPipeline window)", align="left", width=340)
        self.ops_separator4 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_custom_users_section(self):
        """Builds the custom users management section."""
        self.ops_customUsers_checkBox = cmds.checkBox('ops_customUsers_checkBox', parent=self.form1, label="")
        self.ops_enableCustomUsers_txt = cmds.text('ops_enableCustomUsers_txt', parent=self.form1, fn="boldLabelFont", label="Enable Custom Users", align="left", width=320)
        self.ops_customUsers_txt = cmds.text('ops_customUsers_txt', parent=self.form1, fn="boldLabelFont", label="Users:", align="left", width=80)
        self.ops_customUsers_txtField = cmds.textField('ops_customUsers_txtField', parent=self.form1, enable=0, h=20)
        self.ops_customUsers_btn = cmds.button('ops_customUsers_btn', parent=self.form1, l="...")
        self.ops_separator5 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_dates_section(self):
        """Builds the fields to establish project creation and deadline dates."""
        self.ops_creationDate_txt = cmds.text('ops_creationDate_txt', parent=self.form1, fn="boldLabelFont", label="Creation Date:", align="left", width=100)
        self.ops_creationDate_txtField = cmds.textField('ops_creationDate_txtField', text=self.ops_creationDate, parent=self.form1, h=20)
        self.ops_deadline_txt = cmds.text('ops_deadline_txt', parent=self.form1, fn="boldLabelFont", label="Deadline:", align="center", width=70)
        self.ops_deadline_txtField = cmds.textField('ops_deadline_txtField', text=self.ops_deadline, parent=self.form1, h=20)
        self.ops_separator6 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_master_files_section(self):
        """Builds the settings for finalized 'Master' files (format and nomenclature)."""
        self.ops_masterFiles_txt = cmds.text('ops_masterFiles_txt', parent=self.form1, fn="boldLabelFont", label="Master Files:", align="left", width=100)
        self.ops_masterFilesParens_txt = cmds.text('ops_masterFilesParens_txt', parent=self.form1, fn="smallPlainLabelFont", label="(finalized versions with flattened references)", align="left", width=240)
        self.ops_masterFilesName_txt = cmds.text('ops_masterFilesName_txt', parent=self.form1, fn="smallPlainLabelFont", label="Name:", align="left", width=50)
        self.ops_masterFilesName_txtField = cmds.textField('ops_masterFilesName_txtField', text=self.ops_masterFilesName, parent=self.form1, h=20)
        self.ops_masterFileFormat_txt = cmds.text('ops_masterFileFormat_txt', parent=self.form1, fn="smallPlainLabelFont", label="File Format:", align="center")
        self.ops_masterFileFormat_optMenu = cmds.optionMenu('ops_masterFileFormat_optMenu', parent=self.form1)
        cmds.menuItem(label="mb", parent=self.ops_masterFileFormat_optMenu)
        cmds.menuItem(label="ma", parent=self.ops_masterFileFormat_optMenu)
        self.ops_separator7 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_workshop_files_section(self):
        """Builds the settings for work-in-progress 'Workshop' files (format and nomenclature)."""
        self.ops_workshopFiles_txt = cmds.text('ops_workshopFiles_txt', parent=self.form1, fn="boldLabelFont", label="Workshop Files:", align="left", width=100)
        self.ops_workshopFilesParens_txt = cmds.text('ops_workshopFilesParens_txt', parent=self.form1, fn="smallPlainLabelFont", label="(preliminary and test versions)", align="left", width=240)
        self.ops_workshopFilesName_txt = cmds.text('ops_workshopFilesName_txt', parent=self.form1, fn="smallPlainLabelFont", label="Name:", align="left", width=50)
        self.ops_workshopFilesName_txtField = cmds.textField('ops_workshopFilesName_txtField', parent=self.form1, text=self.ops_workshopFilesName, h=20)
        self.ops_workshopFileFormat_txt = cmds.text('ops_workshopFileFormat_txt', parent=self.form1, fn="smallPlainLabelFont", label="File Format:", align="center")
        self.ops_workshopFileFormat_optMenu = cmds.optionMenu('ops_workshopFileFormat_optMenu', parent=self.form1)
        cmds.menuItem(label="mb", parent=self.ops_workshopFileFormat_optMenu)
        cmds.menuItem(label="ma", parent=self.ops_workshopFileFormat_optMenu)
        self.ops_separator8 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_sub_folder_section(self):
        """Builds the configuration inputs to define custom names for standard subdirectories."""
        self.ops_subFolderNames_txt = cmds.text('ops_subFolderNames_txt', parent=self.form1, fn="boldLabelFont", label="Sub-Folder Names:", align="left", width=200)
        self.ops_assetLibrary_txt = cmds.text('ops_assetLibrary_txt', fn="smallPlainLabelFont", parent=self.form1, label="Asset Library:", align="left", width=70)
        self.ops_assetLibrary_txtField = cmds.textField('ops_assetLibrary_txtField', parent=self.form1, text=self.ops_assetLibrary, h=20)
        self.ops_scripts_txt = cmds.text('ops_scripts_txt', parent=self.form1, fn="smallPlainLabelFont", label="Scripts:", align="center", width=50)
        self.ops_scripts_txtField = cmds.textField('ops_scripts_txtField', parent=self.form1, text=self.ops_scripts, h=20)
        
        self.ops_shotLibrary_txt = cmds.text('ops_shotLibrary_txt', fn="smallPlainLabelFont", parent=self.form1, label="Shot Library:", align="left", width=70)
        self.ops_shotLibrary_txtField = cmds.textField('ops_shotLibrary_txtField', parent=self.form1, text=self.ops_shotLibrary, h=20)
        self.ops_textures_txt = cmds.text('ops_textures_txt', parent=self.form1, fn="smallPlainLabelFont", label="Textures:", align="center", width=50)
        self.ops_textures_txtField = cmds.textField('ops_textures_txtField', parent=self.form1, text=self.ops_textures, h=20)
        
        self.ops_renders_txt = cmds.text('ops_renders_txt', fn="smallPlainLabelFont", parent=self.form1, label="Renders:", align="left", width=70)
        self.ops_renders_txtField = cmds.textField('ops_renders_txtField', parent=self.form1, text=self.ops_renders, h=20)
        self.ops_particles_txt = cmds.text('ops_particles_txt', parent=self.form1, fn="smallPlainLabelFont", label="Particles:", align="center", width=50)
        self.ops_particles_txtField = cmds.textField('ops_particles_txtField', parent=self.form1, text=self.ops_particles, h=20)
        
    def _build_archive_deleted_section(self):
        """Builds the directory browser section to define locations for archived/deleted data."""
        self.ops_archiveDeletedItems_txt = cmds.text('ops_archiveDeletedItems_txt', parent=self.form1, fn="boldLabelFont", label="Archived and Deleted Items Locations:", align="left", width=70)
        self.ops_archive_txt = cmds.text('ops_archive_txt', fn="smallPlainLabelFont", parent=self.form1, label="Archive:", align="left", width=70)
        self.ops_archive_txtField = cmds.textField('ops_archive_txtField', parent=self.form1, text=self.ops_archive, h=20)
        self.ops_archiveBrowse_btn = cmds.button('ops_archiveBrowse_btn', parent=self.form1, width=70, l="Browse...", c=lambda *args: opsProject._browse_path("ops_archive_txtField"))
        self.ops_deletedItems_txt = cmds.text('ops_deletedItems_txt', fn="smallPlainLabelFont", parent=self.form1, label="Deleted Items:", align="left", width=70)
        self.ops_deletedItems_txtField = cmds.textField('ops_deletedItems_txtField', parent=self.form1, text=self.ops_deleted, h=20)
        self.ops_deletedItems_btn = cmds.button('ops_deletedItems_btn', parent=self.form1, width=70, l="Browse...", c=lambda *args: opsProject._browse_path("ops_deletedItems_txtField"))
        self.ops_separator9 = cmds.separator(parent=self.form1, h=5, st="out")
        
    def _build_action_buttons(self):
        """Builds the main Accept and Cancel buttons for the dialog."""
        self.ops_accept_btn = cmds.button('ops_accept_btn', parent=self.form1, l="Accept")
        self.ops_cancel_btn = cmds.button('ops_cancel_btn', parent=self.form1, l="Cancel")
        
    def _attach_form_elements(self):
        """
        Positions all the created UI elements within the main form layout.
        Uses a combination of attachPosition (percentages), attachForm (edges), 
        and attachControl (relative to other elements) to construct the grid.
        """
        cmds.formLayout(
            self.form1,
            edit=True,
            attachPosition=[
                
                # Project Name Section
                (self.ops_projName_txt, 'top', 6, 0),
                (self.ops_projName_txtField, 'top', 6, 0),
                (self.ops_projName_txt, 'left', self.lfMargin, 0),
                (self.ops_projName_txtField, 'right', self.rtMargin, 100),
                (self.ops_separator1, 'left', self.lfMargin, 0),
                (self.ops_separator1, 'right', self.rtMargin, 100),
                
                # Project Path Section
                (self.ops_projPath_txt, 'left', self.lfMargin, 0),
                (self.ops_pathField_txtField, 'left', self.lfMargin, 0),
                (self.ops_pathField_txtField, 'right', 70, 100),
                (self.ops_pathBrowse_btn, 'right', self.rtMargin, 100),
                (self.ops_separator2, 'left', self.lfMargin, 0),
                (self.ops_separator2, 'right', self.rtMargin, 100),
                
                # Description Section
                (self.ops_description_txt, 'left', self.lfMargin, 0),
                (self.ops_description_txtField, 'right', self.rtMargin, 100),
                (self.ops_separator3, 'left', self.lfMargin, 0),
                (self.ops_separator3, 'right', self.rtMargin, 100),
                
                # Project Status Section
                (self.ops_status_txt, 'left', self.lfMargin, 0),
                (self.ops_statusParens_txt, 'left', self.lfMargin, 0),
                (self.ops_separator4, 'left', self.lfMargin, 0),
                (self.ops_separator4, 'right', self.rtMargin, 100),
                
                # Custom Users Section
                (self.ops_customUsers_checkBox, 'left', self.lfMargin, 0),
                (self.ops_customUsers_txt, 'left', self.lfMargin, 0),
                (self.ops_customUsers_txtField, 'right', 50, 100),
                (self.ops_customUsers_btn, 'right', self.rtMargin, 100),
                (self.ops_separator5, 'left', self.lfMargin, 0),
                (self.ops_separator5, 'right', self.rtMargin, 100),
                
                # Creation Date & Deadline Section
                (self.ops_creationDate_txt, 'left', self.lfMargin, 0),
                (self.ops_creationDate_txtField, 'right', 0, 50),
                (self.ops_deadline_txtField, 'right', self.rtMargin, 100),
                (self.ops_separator6, 'left', self.lfMargin, 0),
                (self.ops_separator6, 'right', self.rtMargin, 100),
                
                # Master Files Section
                (self.ops_masterFiles_txt, 'left', self.lfMargin, 0),
                (self.ops_masterFilesName_txt, 'left', self.lfMargin, 0),
                (self.ops_masterFileFormat_optMenu, 'right', self.rtMargin, 100),
                (self.ops_separator7, 'left', self.lfMargin, 0),
                (self.ops_separator7, 'right', self.rtMargin, 100),
                
                # Workshop Files Section
                (self.ops_workshopFiles_txt, 'left', self.lfMargin, 0),
                (self.ops_workshopFilesName_txt, 'left', self.lfMargin, 0),
                (self.ops_workshopFileFormat_optMenu, 'right', self.rtMargin, 100),
                (self.ops_separator8, 'left', self.lfMargin, 0),
                (self.ops_separator8, 'right', self.rtMargin, 100),
                
                # Sub-Folder Section
                (self.ops_subFolderNames_txt, 'left', self.lfMargin, 0),
                (self.ops_assetLibrary_txt, 'left', self.lfMargin, 0),
                (self.ops_assetLibrary_txtField, 'right', 0, 50),
                (self.ops_scripts_txtField, 'right', self.rtMargin, 100),
                
                (self.ops_shotLibrary_txt, 'left', self.lfMargin, 0),
                (self.ops_shotLibrary_txtField, 'right', 0, 50),
                (self.ops_textures_txtField, 'right', self.rtMargin, 100),
                
                (self.ops_renders_txt, 'left', self.lfMargin, 0),
                (self.ops_renders_txtField, 'right', 0, 50),
                (self.ops_particles_txtField, 'right', self.rtMargin, 100),
                
                # Archived and Deleted Items
                (self.ops_archiveDeletedItems_txt, 'left', self.lfMargin, 0),
                (self.ops_archive_txt, 'left', self.lfMargin, 0),
                (self.ops_archiveBrowse_btn, 'right', self.rtMargin, 100),
                (self.ops_deletedItems_txt, 'left', self.lfMargin, 0),
                (self.ops_deletedItems_btn, 'right', self.rtMargin, 100),
                (self.ops_separator9, 'left', self.lfMargin, 0),
                (self.ops_separator9, 'right', self.rtMargin, 100),
                
                # Accept & Cancel Buttons
                (self.ops_accept_btn, 'left', self.lfMargin, 0),
                (self.ops_accept_btn, 'right', 0, 50),
                (self.ops_cancel_btn, 'right', self.rtMargin, 100),
                (self.ops_cancel_btn, 'left', 0, 50),
                (self.ops_accept_btn, 'bottom', 2, 100),
                (self.ops_cancel_btn, 'bottom', 2, 100),
                
            ],
            attachForm=[
            ],
            attachControl=[
                
                # Project Name Section
                (self.ops_projName_txtField, 'left', 2, self.ops_projName_txt),
                (self.ops_separator1, 'top', 6, self.ops_projName_txtField),
                
                # Project Path Section
                (self.ops_projPath_txt, 'top', 5, self.ops_separator1),
                (self.ops_projPathParens_txt, 'top', 5, self.ops_separator1),
                (self.ops_projPathParens_txt, 'left', 6, self.ops_projPath_txt),
                (self.ops_pathField_txtField, 'top', 6, self.ops_projPath_txt),
                (self.ops_pathBrowse_btn, 'top', 6, self.ops_projPath_txt),
                (self.ops_pathBrowse_btn, 'left', 2, self.ops_pathField_txtField),
                (self.ops_separator2, 'top', 6, self.ops_pathField_txtField),
                
                # Description Section
                (self.ops_description_txt, 'top', 6, self.ops_separator2),
                (self.ops_description_txtField, 'top', 6, self.ops_separator2),
                (self.ops_description_txtField, 'left', 6, self.ops_description_txt),
                (self.ops_separator3, 'top', 6, self.ops_description_txtField),
                
                # Project Status Section
                (self.ops_status_txt, 'top', 6, self.ops_separator3),
                (self.ops_status_optMenu, 'top', 6, self.ops_separator3),
                (self.ops_status_optMenu, 'left', 2, self.ops_status_txt),
                (self.ops_statusParens_txt, 'top', 6, self.ops_status_txt),
                (self.ops_separator4, 'top', 6, self.ops_statusParens_txt),
                
                # Custom Users Section
                (self.ops_customUsers_checkBox, 'top', 6, self.ops_separator4),
                (self.ops_enableCustomUsers_txt, 'top', 6, self.ops_separator4),
                (self.ops_enableCustomUsers_txt, 'left', 6, self.ops_customUsers_checkBox),
                (self.ops_customUsers_txt, 'top', 6, self.ops_enableCustomUsers_txt),
                (self.ops_customUsers_txtField, 'left', 6, self.ops_customUsers_txt),
                (self.ops_customUsers_txtField, 'top', 6, self.ops_enableCustomUsers_txt),
                (self.ops_customUsers_btn, 'top', 6, self.ops_enableCustomUsers_txt),
                (self.ops_customUsers_btn, 'left', 6, self.ops_customUsers_txtField),
                (self.ops_separator5, 'top', 6, self.ops_customUsers_btn),
                
                # Creation Date & Deadline Section
                (self.ops_creationDate_txt, 'top', 6, self.ops_separator5),
                (self.ops_creationDate_txtField, 'top', 6, self.ops_separator5),
                (self.ops_creationDate_txtField, 'left', 6, self.ops_creationDate_txt),
                (self.ops_deadline_txt, 'top', 6, self.ops_separator5),
                (self.ops_deadline_txt, 'left', 6, self.ops_creationDate_txtField),
                (self.ops_deadline_txtField, 'top', 6, self.ops_separator5),
                (self.ops_deadline_txtField, 'left', 6, self.ops_deadline_txt),
                (self.ops_separator6, 'top', 6, self.ops_deadline_txtField),
                
                # Master Files Section
                (self.ops_masterFiles_txt, 'top', 6, self.ops_separator6),
                (self.ops_masterFilesParens_txt, 'top', 6, self.ops_separator6),
                (self.ops_masterFilesParens_txt, 'left', 6, self.ops_masterFiles_txt),
                (self.ops_masterFilesName_txt, 'top', 10, self.ops_masterFiles_txt),
                (self.ops_masterFilesName_txtField, 'top', 10, self.ops_masterFiles_txt),
                (self.ops_masterFilesName_txtField, 'left', 6, self.ops_masterFilesName_txt),
                (self.ops_masterFilesName_txtField, 'right', 6, self.ops_masterFileFormat_txt),
                (self.ops_masterFileFormat_txt, 'top', 10, self.ops_masterFiles_txt),
                (self.ops_masterFileFormat_txt, 'right', 6, self.ops_masterFileFormat_optMenu),
                (self.ops_masterFileFormat_optMenu, 'top', 10, self.ops_masterFiles_txt),
                (self.ops_separator7, 'top', 6, self.ops_masterFilesName_txtField),
                
                # Workshop Files Section
                (self.ops_workshopFiles_txt, 'top', 6, self.ops_separator7),
                (self.ops_workshopFilesParens_txt, 'top', 6, self.ops_separator7),
                (self.ops_workshopFilesParens_txt, 'left', 6, self.ops_workshopFiles_txt),
                (self.ops_workshopFilesName_txt, 'top', 10, self.ops_workshopFiles_txt),
                (self.ops_workshopFilesName_txtField, 'top', 10, self.ops_workshopFiles_txt),
                (self.ops_workshopFilesName_txtField, 'left', 6, self.ops_workshopFilesName_txt),
                (self.ops_workshopFilesName_txtField, 'right', 6, self.ops_workshopFileFormat_txt),
                (self.ops_workshopFileFormat_txt, 'top', 10, self.ops_workshopFiles_txt),
                (self.ops_workshopFileFormat_txt, 'right', 10, self.ops_workshopFileFormat_optMenu),
                (self.ops_workshopFileFormat_optMenu, 'top', 10, self.ops_workshopFiles_txt),
                (self.ops_separator8, 'top', 6, self.ops_workshopFilesName_txtField),
                
                # Sub-Folder Section
                (self.ops_subFolderNames_txt, 'top', 6, self.ops_separator8),
                (self.ops_assetLibrary_txt, 'top', 10, self.ops_subFolderNames_txt),
                (self.ops_assetLibrary_txtField, 'left', 6, self.ops_assetLibrary_txt),
                (self.ops_assetLibrary_txtField, 'top', 10, self.ops_subFolderNames_txt),
                (self.ops_scripts_txt, 'top', 10, self.ops_subFolderNames_txt),
                (self.ops_scripts_txt, 'left', 6, self.ops_assetLibrary_txtField),
                (self.ops_scripts_txtField, 'top', 10, self.ops_subFolderNames_txt),
                (self.ops_scripts_txtField, 'left', 6, self.ops_scripts_txt),
                
                (self.ops_shotLibrary_txt, 'top', 6, self.ops_assetLibrary_txtField),
                (self.ops_shotLibrary_txtField, 'left', 6, self.ops_shotLibrary_txt),
                (self.ops_shotLibrary_txtField, 'top', 6, self.ops_assetLibrary_txtField),
                (self.ops_textures_txt, 'top', 6, self.ops_assetLibrary_txtField),
                (self.ops_textures_txt, 'left', 6, self.ops_shotLibrary_txtField),
                (self.ops_textures_txtField, 'top', 6, self.ops_assetLibrary_txtField),
                (self.ops_textures_txtField, 'left', 6, self.ops_textures_txt),
                
                (self.ops_renders_txt, 'top', 6, self.ops_shotLibrary_txtField),
                (self.ops_renders_txtField, 'left', 6, self.ops_renders_txt),
                (self.ops_renders_txtField, 'top', 6, self.ops_shotLibrary_txtField),
                (self.ops_particles_txt, 'top', 6, self.ops_shotLibrary_txtField),
                (self.ops_particles_txt, 'left', 6, self.ops_renders_txtField),
                (self.ops_particles_txtField, 'top', 6, self.ops_shotLibrary_txtField),
                (self.ops_particles_txtField, 'left', 6, self.ops_particles_txt),
                
                # Archived and Deleted Items
                (self.ops_archiveDeletedItems_txt, 'top', 10, self.ops_renders_txtField),
                (self.ops_archive_txt, 'top', 10, self.ops_archiveDeletedItems_txt),
                (self.ops_archive_txtField, 'top', 10, self.ops_archiveDeletedItems_txt),
                (self.ops_archive_txtField, 'left', 10, self.ops_archive_txt),
                (self.ops_archive_txtField, 'right', 10, self.ops_archiveBrowse_btn),
                (self.ops_archiveBrowse_btn, 'top', 10, self.ops_archiveDeletedItems_txt),
                (self.ops_deletedItems_txt, 'top', 10, self.ops_archive_txtField),
                (self.ops_deletedItems_txtField, 'top', 10, self.ops_archive_txtField),
                (self.ops_deletedItems_txtField, 'left', 10, self.ops_deletedItems_txt),
                (self.ops_deletedItems_txtField, 'right', 10, self.ops_deletedItems_btn),
                (self.ops_deletedItems_btn, 'top', 10, self.ops_archive_txtField),
                (self.ops_separator9, 'top', 10, self.ops_deletedItems_txtField),
                
                # Accept & Cancel Buttons
                (self.ops_accept_btn, 'top', 10, self.ops_separator9),
                (self.ops_cancel_btn, 'top', 10, self.ops_separator9),
        
            ]
            )

    def _populate_fields(self):
        """Auto-populates the UI fields if editing an existing project."""
        import opsInfo
        import opsProject
        import opsUtils
        
        date_str = opsInfo.get_date()
        cmds.textField(self.ops_creationDate_txtField, edit=True, text=date_str)
        cmds.textField(self.ops_deadline_txtField, edit=True, text=date_str)
        
        if self.mode == 1 and self.old_name:
            proj_xml = opsProject.get_single_project_xml(self.old_name)
            if proj_xml:
                cmds.textField(self.ops_projName_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "name"))
                cmds.textField(self.ops_pathField_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "path"))
                cmds.textField(self.ops_description_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "description"))
                cmds.textField(self.ops_creationDate_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "date"))
                cmds.textField(self.ops_deadline_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "deadline"))
                
                cmds.textField(self.ops_assetLibrary_txtField, edit=True, editable=False, text=opsUtils.get_xml_data(proj_xml, "libraryfolder"))
                cmds.textField(self.ops_shotLibrary_txtField, edit=True, editable=False, text=opsUtils.get_xml_data(proj_xml, "scenesfolder"))
                cmds.textField(self.ops_archive_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "archivefolder"))
                cmds.textField(self.ops_deletedItems_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "deletedfolder"))
                cmds.textField(self.ops_renders_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "rendersfolder"))
                cmds.textField(self.ops_particles_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "particlesfolder"))
                cmds.textField(self.ops_textures_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "texturesfolder"))
                cmds.textField(self.ops_scripts_txtField, edit=True, text=opsUtils.get_xml_data(proj_xml, "scriptsfolder"))
                
                cmds.textField(self.ops_masterFilesName_txtField, edit=True, editable=False, text=opsUtils.get_xml_data(proj_xml, "mastername"))
                cmds.optionMenu(self.ops_masterFileFormat_optMenu, edit=True, enable=False, value=opsUtils.get_xml_data(proj_xml, "masterformat"))
                cmds.textField(self.ops_workshopFilesName_txtField, edit=True, editable=False, text=opsUtils.get_xml_data(proj_xml, "workshopname"))
                cmds.optionMenu(self.ops_workshopFileFormat_optMenu, edit=True, enable=False, value=opsUtils.get_xml_data(proj_xml, "workshopformat"))
                
                # status: active=1, inactive=0. Option menu indexes: active=1, inactive=2.
                status = int(opsUtils.get_xml_data(proj_xml, "status") or 1)
                cmds.optionMenu(self.ops_status_optMenu, edit=True, select=(2 - status))
                
                user_mode = int(opsUtils.get_xml_data(proj_xml, "userMode") or 0)
                cmds.checkBox(self.ops_customUsers_checkBox, edit=True, value=user_mode)
                cmds.button(self.ops_customUsers_btn, edit=True, enable=bool(user_mode))
                
                curr_users = opsUtils.get_xml_data(proj_xml, "users")
                if curr_users:
                    global_users = opsProject.get_users()
                    valid_users = [u for u in curr_users.split(",") if u in global_users]
                    cmds.textField(self.ops_customUsers_txtField, edit=True, text=",".join(valid_users))
                else:
                    cmds.textField(self.ops_customUsers_txtField, edit=True, text="")
        else:
            cmds.checkBox(self.ops_customUsers_checkBox, edit=True, value=0)
            cmds.button(self.ops_customUsers_btn, edit=True, enable=False)
            
            # Clear text fields for new project mode
            cmds.textField(self.ops_projName_txtField, edit=True, text="")
            cmds.textField(self.ops_pathField_txtField, edit=True, text="")
            cmds.textField(self.ops_description_txtField, edit=True, text="")
            cmds.textField(self.ops_customUsers_txtField, edit=True, text="")

    # --- Button Callbacks ---

    def on_accept(self, *args):
        """Gathers data from the UI and passes it to the core opsActions module."""
        import opsActions
        
        new_name = cmds.textField(self.ops_projName_txtField, query=True, text=True).strip()
        new_path = cmds.textField(self.ops_pathField_txtField, query=True, text=True).strip()
        new_description = cmds.textField(self.ops_description_txtField, query=True, text=True).strip()
        
        # OptionMenu: 1="active", 2="inactive". We want "1" for active, "0" for inactive.
        new_status = str(2 - cmds.optionMenu(self.ops_status_optMenu, query=True, select=True))
        
        new_date = cmds.textField(self.ops_creationDate_txtField, query=True, text=True).strip()
        new_deadline = cmds.textField(self.ops_deadline_txtField, query=True, text=True).strip()
        
        new_master_name = cmds.textField(self.ops_masterFilesName_txtField, query=True, text=True).strip()
        new_master_format = cmds.optionMenu(self.ops_masterFileFormat_optMenu, query=True, value=True).strip()
        
        new_workshop_name = cmds.textField(self.ops_workshopFilesName_txtField, query=True, text=True).strip()
        new_workshop_format = cmds.optionMenu(self.ops_workshopFileFormat_optMenu, query=True, value=True).strip()
        
        new_lib_loc = cmds.textField(self.ops_assetLibrary_txtField, query=True, text=True).strip()
        new_shot_loc = cmds.textField(self.ops_shotLibrary_txtField, query=True, text=True).strip()
        new_renders_loc = cmds.textField(self.ops_renders_txtField, query=True, text=True).strip()
        new_scripts_loc = cmds.textField(self.ops_scripts_txtField, query=True, text=True).strip()
        new_textures_loc = cmds.textField(self.ops_textures_txtField, query=True, text=True).strip()
        new_particles_loc = cmds.textField(self.ops_particles_txtField, query=True, text=True).strip()
        
        new_archive_loc = cmds.textField(self.ops_archive_txtField, query=True, text=True).strip()
        new_deleted_loc = cmds.textField(self.ops_deletedItems_txtField, query=True, text=True).strip()
        
        new_users = cmds.textField(self.ops_customUsers_txtField, query=True, text=True).strip()
        user_mode = str(int(cmds.checkBox(self.ops_customUsers_checkBox, query=True, value=True)))
        
        result = opsActions.create_or_edit_project(
            self.mode, self.old_name, new_name, new_path, new_description, new_status, new_date, new_deadline,
            new_master_name, new_master_format, new_workshop_name, new_workshop_format, new_lib_loc,
            new_shot_loc, new_renders_loc, new_scripts_loc, new_textures_loc, new_particles_loc,
            new_archive_loc, new_deleted_loc, new_users, user_mode
        )
        
        if result:
            self.deleteWindow()
            # Refresh main UI if open
            import opsUIWrappers
            opsUIWrappers.refresh_ui()
            # Trigger the list refresh on the Project Manager window if it's currently open
            if hasattr(self.UIObjects, 'opsProjectManagerGUI'):
                try: self.UIObjects.opsProjectManagerGUI.on_refresh_list()
                except: pass
                
    def on_cancel(self, *args):
        """Closes the UI without saving."""
        self.deleteWindow()