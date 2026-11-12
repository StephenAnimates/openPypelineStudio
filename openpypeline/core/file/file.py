import os

class File:
    """Base interface for querying and bundling pipeline files."""

    def __init__(self):
        """Initialize the base file handler."""
        pass
  
    def query(self, path):
        """Return 1 when a path exists and 0 otherwise."""
        if os.path.exists(path):
            return 1
        else:
            return 0

    def bundle(self):
        """Provide the extension point for bundling a managed file."""
        pass        
   