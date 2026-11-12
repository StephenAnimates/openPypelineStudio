import os

class Notes:
    """Query and manage XML notes attached to pipeline items."""

    def __init__(self):
        """Initialize the notes handler."""
        pass

    def create(self):
        """Provide the extension point for creating an item's notes file."""
        pass
    
    def query(self, path, element):
        """Return 1 when the item's asset-note XML file exists, else 0."""
        note = os.path.join(path, "notes", (element + "_AssetNote.xml"))
        if os.path.exists(note):
            return 1
        else:
            return 0
    
    def read(self):
        """Provide the extension point for reading an item's notes."""
        pass
    
    def write(self):
        """Provide the extension point for writing an item's notes."""
        pass