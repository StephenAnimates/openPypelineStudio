"""Build and query filesystem paths for pipeline inventory structures."""

import os

class Inventory:
    """Build filesystem paths and list entries for a pipeline inventory."""

    def __init__(self, elements):
        """Store the ordered path elements that identify this inventory."""
        self.elements = elements
        pass
    
    def getPath(self):
        """Construct the directory path represented by the stored elements."""
        depth = len(self.elements)
        path = ""
        count = 0
        
        for item in self.elements:
            if depth == 5 and count == 3:
                path = os.path.join(path, item, "components")
            else:
                path = os.path.join(path, item)
            count = count + 1
        
        return path    
    
    def list(self, path=""):
        """List non-hidden entries under the supplied or constructed path."""
        if path == "":
            path = self.getPath()

        # Create list and remove hidden OS files            
        inventory = [f for f in os.listdir(path) if not f.startswith('.')]
        return inventory
    
    def count(self):
        """Count regular files directly inside the constructed path."""
        path = self.getPath()
        file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        return file_count
    
    