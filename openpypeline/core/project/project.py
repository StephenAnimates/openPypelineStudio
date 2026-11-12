"""Manage project configuration and project-list persistence."""

import os
import importlib

from ..util import XML
importlib.reload(XML)

class Project():
    '''
    Core project methods.
    '''

    def __init__(self):
        """Initialize the project configuration path and project-list name."""
        self.openPipeline_projectFilePath = ""
        self.openPipeline_projList = ""
    
    def create():
        """Provide the extension point for creating a project."""
        pass
    
    def remove():
        """Provide the extension point for removing a project."""
        pass
        
    def list():
        """Provide the extension point for listing configured projects."""
        pass
    
    def set():
        """Provide the extension point for selecting a project."""
        # app specific?
        pass
    
    def validateProject(self):
        """Provide the extension point for validating project settings."""
        pass
    
    def validateProjectFile(self):
        """Provide the extension point for validating the project file."""
        pass
        
    def path(self):
        '''
        Description: 	Returns the full path of the Project File
        Input: 		none
        Returns: 	The full path of the Project File (string)
        '''
        
        projectFilePath = os.path.join(self.openPipeline_projectFilePath, self.openPipeline_projList)
        return projectFilePath
