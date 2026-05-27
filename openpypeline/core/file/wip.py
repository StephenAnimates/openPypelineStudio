import os
import importlib
import logging

logger = logging.getLogger("openPypeline.wip")

from . import file as base_file
importlib.reload(base_file)

from ..util import prefs
importlib.reload(prefs)

class WIP(base_file.File):
    def __init__(self):
        super().__init__()
    
    def open(self, path, item, version):
        """Resolves and returns the file path for a specific Work-in-Progress version."""
        # Fetch nomenclature and format dynamically from preferences
        w_name = prefs.get_pref("ops_wip", "wip")
        w_ext = prefs.get_pref("ops_wipFormat", "ma")
        
        # Build Work-in-Progress filename safely
        name = f"{item}_{w_name}_{version:04d}.{w_ext}"
        wipPath = os.path.join(path, w_name, name).replace("\\", "/")
                
        if self.query(wipPath):
            logger.debug(f"Found Work-in-Progress: {wipPath}")
            return wipPath
        else:
            logger.error(f"Could not find Work-in-Progress at {wipPath}")
            return None

    
    def save(self):
        pass
