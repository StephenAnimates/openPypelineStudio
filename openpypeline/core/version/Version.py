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
        [name]_workshop_####.type
    
    Examples:
        testMaster_workshop_0003.mb
    
    '''
    def __init__(self):
        pass

    def getByIndex(self, index):
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
        
        # Retrieve the workshop folder name from preferences (defaulting to 'workshop')
        w_name = prefs.get_pref("ops_workshopName", "workshop")
        
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
    pass

class git(Version):
    pass

class cvs(Version):
    pass