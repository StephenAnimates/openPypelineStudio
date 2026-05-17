import maya.cmds as cmds

class window():
    
    def __init__(self):
        '''
        Name: window.py
        Description: Base-class for OpenPipeline Maya Windows. The purpose of this class is to avoid writing redundant Maya UI functionality into every Maya GUI. For example, deleting a duplicate UI before building a new one. 
        Directions: This class functions through inheritance, so that a given class inherits the functionality of this class. In creating a new class that inherits from this window class, you must have a procedure called 'content' in your inheriting class.
        
        example: def content(self):
        
        This procedure entitled 'content' must return one or more Maya 'formLayout' elements as a list. Additionally, you must instantiate and define the following class attributes in order for the 'showWindow method' to work properly:
        
        self.width = (integer) example: 450
        self.height = (integer) example: 450
        self.prettyName = (string) example: 'OpenPipeline 2.0'
        self.name = (string containing only integers and numbers AKA no funky stuff) example: 'openPipelineUI'
        self.dockable = (boolean) example: 0
        
        Attributes such as self.width stupilate the width of a given window. self.dockable enables a given window as a floating dockable window (if using Maya2011). A future TODO might be to further develop and refine this dock functionality. This could be done by creating a simple drop down for each window that docks the window left, right, up or down, which might create a more desirable outcome than the somewhat still buggy 'floating but dockable' mode that is currently offered in Maya2011, which often ends up in uncontrollable window sizes.
        
        '''
    
    def showWindow(self, dockableDropdownOption=None):
        
        try: self.prettyName
        except: self.prettyName = self.name
        self.uiName = self.name.replace(" ", "")
        self.dockControl = self.uiName
        self.window = str(self.uiName)+"_window"
        
        # In modern Maya (2026/2027), dockControl is natively supported
        self.is_modern_maya = True
        
        # check if a version of this dock/window is already open, clear it
        if self.is_modern_maya and self.dockable:
            
            if cmds.workspaceControl(self.dockControl, exists=True):
                cmds.deleteUI(self.dockControl)
            
            self.window = cmds.workspaceControl(self.dockControl, retain=False, floating=True, label=self.prettyName)
            
        else: # older version of Maya
            
            self.window = self.uiName
            if cmds.window(self.window, q=True, ex=True): cmds.deleteUI(self.window)
            self.window = cmds.window(self.window, title=self.prettyName, sizeable=1)
        
        # Content command that changes depending on the instance of this class
        windowElements = self.content()
        for element in windowElements:
            cmds.formLayout( element, e=1, parent = self.window )
        
        # docking (if available) and show window
        if self.is_modern_maya and self.dockable:
            cmds.workspaceControl(self.dockControl, edit=True, resizeWidth=self.width, resizeHeight=self.height)
            self.UIObjects.addDockControl(self.dockControl)
        else:
            cmds.showWindow(self.window)
            cmds.window(self.window, e=1, width=self.width, height=self.height)
            self.UIObjects.addWindow(self.window)
  
    def deleteWindow(self):
        if self.is_modern_maya and self.dockable:
            if cmds.workspaceControl(self.dockControl, exists=True): cmds.deleteUI(self.dockControl)
        else: cmds.deleteUI(self.window)