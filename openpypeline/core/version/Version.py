"""
File: Version.py
Description: Core version control management for openPypeline Studio.
             Handles parsing, incrementing, and verifying file versions.
             Designed to be extensible for custom integrations like Git, SVN, or CVS.
"""

import os
import re
import importlib
import logging

logger = logging.getLogger("openPypeline.version")

from ..util import prefs
importlib.reload(prefs)

class Version():
    '''
    The Version class contains the functionality for legacy OpenPipeline 1.0
    file version control, which is just making copies of files. Simple but it
    works.  Classes for SVN or CVS can derive from this to take advantage of
    other other revision control schemas.
    
    Default naming:
        [name]_wip_####.type
    
    Examples:
        testMaster_wip_0003.mb
    
    '''
    def __init__(self):
        """Initialize the version manager."""
        pass

    def getByIndex(self, index):
        """Provide the extension point for resolving a version by index."""
        pass
    
    def latest(self, path):
        '''
        Get latest version
        '''
        # Retrieve a list of all existing version numbers in the directory
        all_versions = self.all(path)
        if all_versions:
            # Return the highest version number if the list is not empty
            return max(all_versions)
        # Return None if no versions were found
        return None
        
    def verify(self, path):
        '''
        Verify that version exists
        '''
        # Check if the exact filepath exists on the filesystem
        if os.path.exists(path):
            return 1
        return 0
        
    def next(self, filepath):
        '''
        Get the next version
        '''     
        # Split the filepath to isolate the base name and the extension
        basename, ext = os.path.splitext(filepath)
        
        # Use regex to find the version number at the end of the base name
        match = re.search(r'_(\d+)$', basename)
        if match:
            # If a version number is found, parse it as an integer and increment by 1
            version = int(match.group(1))
            next_version = version + 1
            logger.info(f"Current version is {version:04d}. Next version is {next_version:04d}.")
            return next_version
        
        # If no version number could be parsed, default to version 1
        logger.warning("Could not determine version from filename.")
        return 1
       
        
    def all(self, path):
        '''
        Get a list of all the versions
        '''
        # Initialize an empty list to store discovered version numbers
        versions = []
        
        # Retrieve the work-in-progress folder name from preferences (defaulting to 'wip')
        w_name = prefs.get_pref("ops_wip", "wip")
        
        # Construct the full path to the versions directory
        versionspath = os.path.join(path, w_name)
        if not os.path.isdir(versionspath):
            # If the directory doesn't exist, return the empty list
            return versions
            
        # List all files in the directory, filtering out hidden OS files (starting with '.')
        inventory = [f for f in os.listdir(versionspath) if not f.startswith('.')]
        for version_file in inventory:
            # Safely extract version using regex to avoid issues with underscores in item names or arbitrary extensions
            match = re.search(r'_(\d+)\.[a-zA-Z0-9]+$', version_file)
            if match:
                # If a valid version string is found, convert it to an integer and add it to the list
                versions.append(int(match.group(1)))
                
        # Sort the list of versions in ascending order before returning
        versions.sort()
        return versions
    
    
class svn(Version):
    """Publish versioned files through Subversion."""

    def publish(self, filepath, comment="Publishing new version"):
        """Publishes a file to SVN."""
        import subprocess
        import os
        repo_dir = os.path.dirname(filepath)
        try:
            subprocess.run(["svn", "add", filepath], cwd=repo_dir, check=False, capture_output=True)
            subprocess.run(["svn", "commit", "-m", comment, filepath], cwd=repo_dir, check=True, capture_output=True)
            logger.info(f"Successfully published {filepath} to SVN.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"SVN publish failed: {e.stderr.decode('utf-8').strip() if e.stderr else e}")
            return False

class git(Version):
    """Publish versioned files through Git."""

    def publish(self, filepath, comment="Publishing new version"):
        """Publishes a file to Git."""
        import subprocess
        import os
        repo_dir = os.path.dirname(filepath)
        try:
            subprocess.run(["git", "add", filepath], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", comment], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "push"], cwd=repo_dir, check=True, capture_output=True)
            logger.info(f"Successfully published {filepath} to Git.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git publish failed: {e.stderr.decode('utf-8').strip() if e.stderr else e}")
            return False

class cvs(Version):
    """Version manager reserved for CVS-backed publishing."""

    pass

class perforce(Version):
    """Publish versioned files through Perforce."""

    def publish(self, filepath, comment="Publishing new version"):
        """Publishes a file to Perforce."""
        import subprocess
        try:
            subprocess.run(["p4", "reconcile", filepath], check=False, capture_output=True)
            subprocess.run(["p4", "submit", "-d", comment, filepath], check=True, capture_output=True)
            logger.info(f"Successfully published {filepath} to Perforce.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Perforce publish failed: {e.stderr.decode('utf-8').strip() if e.stderr else e}")
            return False