import os
import importlib

from . import file as base_file
importlib.reload(base_file)

from ..util import prefs
importlib.reload(prefs)

class Master(base_file.File):
    def __init__(self):
        super().__init__()
        
    def getMaster(self):
        pass
        
    def open(self):
        pass
    
    def process(self):
        pass
        
    def preMasterCommand(self):
        pass
    
    def postMasterCommand(self):
        pass
    
    def close(self):
        pass
    