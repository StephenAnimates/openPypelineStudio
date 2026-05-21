'''
import sys
sys.path.append("/path/to/openPypeline/openpypeline")

import opsEngine
import importlib
importlib.reload(opsEngine)

opsEngine.OpsEngine().ui()
'''

import os
import importlib
import maya.cmds as cmds

class OpsEngine:
    def __init__(self):
        # can we tell which app we're using? or set it?
        print("the BIG __init__")
        pass
        
    def ui(self):
        from core.file import inventory
        importlib.reload(inventory)

        from core.version import Version
        importlib.reload(Version)
        
        from core.file import master
        importlib.reload(master)

        from core.file import workshop
        importlib.reload(workshop)
        
        from core.notes import notes
        importlib.reload(notes)
        
        from app.maya.file import file as mayafile
        importlib.reload(mayafile)
        
        project = cmds.optionVar(query="op_currProjectPath") if cmds.optionVar(exists="op_currProjectPath") else ""
        if not project:
            print("Warning: 'op_currProjectPath' optionVar is not set. Using Maya's current workspace root as fallback.")
            project = cmds.workspace(query=True, rootDirectory=True)
            
        # Dynamically fetch the active working item from optionVars, with fallbacks for testing
        tab = cmds.optionVar(query="op_currOpenTab") if cmds.optionVar(exists="op_currOpenTab") else 2
        module = "lib" if tab == 2 else "scenes"
        
        level1 = cmds.optionVar(query="op_currOpenLevel1") if cmds.optionVar(exists="op_currOpenLevel1") else ""
        item_type = level1 if level1 else "characters"
        
        level2 = cmds.optionVar(query="op_currOpenLevel2") if cmds.optionVar(exists="op_currOpenLevel2") else ""
        asset = level2 if level2 else "woman"
        
        level3 = cmds.optionVar(query="op_currOpenLevel3") if cmds.optionVar(exists="op_currOpenLevel3") else ""
        component = level3 if level3 else "model"
        
        elements = [e for e in [project, module, item_type, asset, component] if e]
        
        inv = inventory.Inventory(elements).list()
        print(inv)
        for item in inv:
            path = inventory.Inventory(elements).getPath()
            fullpath = os.path.join(path, item)
            print(fullpath)
            
            versions = Version.Version().all(fullpath)
            print("versions:")
            print(versions)
            
            hasMaster = master.Master().query(fullpath)
            if hasMaster == 1:
                print(f"{item}: mastered")
            else:
                print(f"{item}: not mastered")
            
            hasNotes = notes.Notes().query(fullpath, item)
            if hasNotes == 1:
                print(f"{item}: has notes")
            else:
                print(f"{item}: no notes")
                
            getLatestWorkshopNumber = Version.Version().latest(fullpath)
            if getLatestWorkshopNumber is not None:
                latestWorkshop = workshop.Workshop().open(fullpath, item, getLatestWorkshopNumber)
                mayafile.open(latestWorkshop)
                