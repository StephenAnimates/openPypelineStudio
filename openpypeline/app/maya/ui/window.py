"""
File: window.py
Description: Base-class for openPypeline Studio Maya UI windows.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import maya.cmds as cmds

class window():
    
    def __init__(self):
        '''
        Name: window.py
        Description: Base-class for openPypeline Studio Maya UI windows. The purpose of this class is to avoid writing redundant Maya UI functionality into every Maya GUI. For example, deleting a duplicate UI before building a new one. 
        Directions: This class functions through inheritance, so that a given class inherits the functionality of this class. In creating a new class that inherits from this window class, you must have a procedure called 'content' in your inheriting class.
        
        example: def content(self):
        
        This procedure entitled 'content' must return one or more Maya 'formLayout' elements as a list. Additionally, you must instantiate and define the following class attributes in order for the 'showWindow method' to work properly:
        
        self.width = (integer) example: 450
        self.height = (integer) example: 450
        self.displayName = (string) example: 'openPypeline Studio'
        self.name = (string containing only integers and numbers AKA no funky stuff) example: 'openPipelineUI'
        self.dockable = (boolean) example: 0
        
        Attributes such as self.width stupilate the width of a given window. self.dockable enables a given window as a floating dockable window (if using Maya2011). 
        
        TODO: Phase 2 Modernization - Migrate UI to PySide6 / PyQt6.
        Once the core Python 3 refactoring and backend `maya.cmds` stabilization is complete, this base class and its inheriting UI modules should be entirely rewritten using Qt widgets and layouts.
        '''
    
    def showWindow(self, dockableDropdownOption=None):
        
        # Fallback to the internal name if a display name wasn't provided
        try: self.displayName
        except AttributeError: self.displayName = self.name
        
        # Create safe, space-free names for the internal Maya UI components
        self.uiName = self.name.replace(" ", "")
        self.dockControl = self.uiName
        self.window = f"{self.uiName}_window"
        
        # In modern Maya (2026/2027), dockControl is natively supported
        self.is_modern_maya = True
        
        # Check if a version of this dock/window is already open, and clear it to avoid duplicates
        if self.is_modern_maya and self.dockable:
            
            # Delete existing workspace control if it exists
            if cmds.workspaceControl(self.dockControl, exists=True):
                cmds.deleteUI(self.dockControl)
            
            # Create a new floating workspace control
            self.window = cmds.workspaceControl(self.dockControl, retain=False, floating=True, label=self.displayName)
            
        else: # Older version of Maya or non-dockable window
            
            self.window = self.uiName
            # Delete existing standard window if it exists
            if cmds.window(self.window, q=True, ex=True): cmds.deleteUI(self.window)
            
            # Create a new standard window
            self.window = cmds.window(self.window, title=self.displayName, sizeable=1)
        
        # Call the subclass's content() method to generate the UI layouts
        windowElements = self.content()
        
        # Parent the generated layouts to the main window or workspace control
        for element in windowElements:
            cmds.formLayout( element, e=1, parent = self.window )
        
        # Finalize display and register the UI with the central UI manager
        if self.is_modern_maya and self.dockable:
            # Resize and register the dockable workspace control
            cmds.workspaceControl(self.dockControl, edit=True, resizeWidth=self.width, resizeHeight=self.height)
            self.UIObjects.addDockControl(self.dockControl)
        else:
            # Show, resize, and register the standard window
            cmds.showWindow(self.window)
            cmds.window(self.window, e=1, width=self.width, height=self.height)
            self.UIObjects.addWindow(self.window)
  
    def deleteWindow(self):
        # Safely delete the UI element based on whether it is a workspace control or a standard window
        if self.is_modern_maya and self.dockable:
            if cmds.workspaceControl(self.dockControl, exists=True): cmds.deleteUI(self.dockControl)
        else: cmds.deleteUI(self.window)