import os
import importlib
import logging

logger = logging.getLogger("openPypeline.workshop")

from . import file as base_file
importlib.reload(base_file)

from ..util import prefs
importlib.reload(prefs)

class Workshop(base_file.File):
    def __init__(self):
        super().__init__()
    
    def open(self, path, item, version):
        """Resolves and returns the file path for a specific workshop version."""
        # Fetch nomenclature and format dynamically from preferences
        w_name = prefs.get_pref("ops_workshopName", "workshop")
        w_ext = prefs.get_pref("ops_workshopFormat", "ma")
        
        # Build workshop filename safely
        name = f"{item}_{w_name}_{version:04d}.{w_ext}"
        workshopPath = os.path.join(path, w_name, name).replace("\\", "/")
                
        if self.query(workshopPath):
            logger.debug(f"Found workshop: {workshopPath}")
            return workshopPath
        else:
            logger.error(f"Could not find workshop at {workshopPath}")
            return None

    
    def save(self):
        pass
