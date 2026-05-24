import os

class Inventory:
    def __init__(self, elements):
        self.elements = elements
        pass
    
    def getPath(self):
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
        if path == "":
            path = self.getPath()

        # Create list and remove hidden OS files            
        inventory = [f for f in os.listdir(path) if not f.startswith('.')]
        return inventory
    
    def count(self):
        path = self.getPath()
        file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        return file_count
    
    