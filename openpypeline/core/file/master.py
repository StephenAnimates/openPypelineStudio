import os
import importlib

from . import file as base_file
importlib.reload(base_file)

from ..util import prefs
importlib.reload(prefs)

class Master(base_file.File):
    """Represent the published master file for a pipeline item."""

    def __init__(self):
        """Initialize the master handler through the shared file base."""
        super().__init__()
        
    def getMaster(self):
        """Provide the extension point for resolving an item's master file."""
        pass
        
    def open(self):
        """Provide the extension point for opening the master file."""
        pass
    
    def process(self):
        """Provide the extension point for processing a master file."""
        pass
        
    def preMasterCommand(self):
        """Provide the extension point for commands run before mastering."""
        pass
    
    def postMasterCommand(self):
        """Provide the extension point for commands run after mastering."""
        pass
    
    def close(self):
        """Provide the extension point for closing the master file."""
        pass
    