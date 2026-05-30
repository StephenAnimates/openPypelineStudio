"""
File: ui_objects.py
Description: Window Manager for openPypeline Studio.
             A modern Singleton that maintains references to active UI instances
             to prevent garbage collection and allows cross-communication.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

class WindowManager:
    """ 
    A modern Singleton Window Manager for tracking open UIs.
    Replaces the legacy 'singleton.py' implementation.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.windows = []
            cls._instance.dock_controls = []
        return cls._instance

    def addWindow(self, window=None):
        if window and window not in self.windows:
            self.windows.append(window)
            
    def addDockControl(self, dock_ctrl=None):
        if dock_ctrl and dock_ctrl not in self.dock_controls:
            self.dock_controls.append(dock_ctrl)
            
    def close_all(self):
        """Closes all tracked windows."""
        pass # Future enhancement hook

# Alias for backward compatibility across the framework
UIObjects = WindowManager