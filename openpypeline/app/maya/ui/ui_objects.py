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
        """Return the shared window manager and initialize its registries once."""
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.windows = []
            cls._instance.dock_controls = []
        return cls._instance

    def addWindow(self, window=None):
        """Keep a reference to a window so it remains alive while managed."""
        if window and window not in self.windows:
            self.windows.append(window)
            
    def addDockControl(self, dock_ctrl=None):
        """Keep a reference to a dock control so it remains alive while managed."""
        if dock_ctrl and dock_ctrl not in self.dock_controls:
            self.dock_controls.append(dock_ctrl)
            
    def close_all(self):
        """Closes all tracked windows."""
        pass # Future enhancement hook

# Alias for backward compatibility across the framework
UIObjects = WindowManager