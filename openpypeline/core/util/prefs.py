"""
File: prefs.py
Description: A completely DCC-agnostic wrapper for getting and setting preferences.
"""

import sys

def get_host_app():
    """Detects which host application is currently running."""
    if 'maya' in sys.modules or 'maya.cmds' in sys.modules:
        return 'maya'
    elif 'nuke' in sys.modules:
        return 'nuke'
    elif 'hou' in sys.modules:
        return 'houdini'
    elif 'bpy' in sys.modules:
        return 'blender'
    elif 'unreal' in sys.modules:
        return 'unreal'
    return 'standalone'

def get_pref(key, default=None):
    """Retrieves a preference value from the host application."""
    host = get_host_app()
    
    if host == 'maya':
        import maya.cmds as cmds
        if cmds.optionVar(exists=key):
            return cmds.optionVar(query=key)
            
    # Future Nuke / Houdini / Blender hooks go here...
    
    return default

def set_pref(key, value):
    """Sets a preference value in the host application."""
    host = get_host_app()
    
    if host == 'maya':
        import maya.cmds as cmds
        if isinstance(value, str):
            cmds.optionVar(stringValue=(key, value))
        elif isinstance(value, int):
            cmds.optionVar(intValue=(key, value))
        elif isinstance(value, float):
            cmds.optionVar(floatValue=(key, value))

def get_workspace_root(default=""):
    """Retrieves the active project or workspace root directory."""
    if get_host_app() == 'maya':
        import maya.cmds as cmds
        return cmds.workspace(query=True, rootDirectory=True)
    return default