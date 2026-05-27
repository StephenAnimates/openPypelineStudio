"""
File: tracker_factory.py
Description: Factory for creating and connecting to a production tracker instance.
             Dynamically loads the appropriate tracker based on user settings.
"""

import logging
from openpypeline.core.util import prefs

logger = logging.getLogger("openPypeline.tracking.factory")

def get_tracker(tracker_type=None, url=None, user=None, key=None):
    """
    Factory function to get an instance of the configured production tracker.
    Reads pipeline preferences to determine which tracker to instantiate and connect to.
    
    Returns:
        An instance of a ProductionTracker subclass if successful, otherwise None.
    """
    if tracker_type is None:
        tracker_type = prefs.get_pref("ops_tracker_type", "none")
    
    if tracker_type == "none" or not tracker_type:
        logger.info("No production tracker is configured.")
        return None
        
    if url is None:
        url = prefs.get_pref("ops_tracker_url", "")
    if user is None:
        user = prefs.get_pref("ops_tracker_user", "")
    if key is None:
        key = prefs.get_pref("ops_tracker_key", "")
    
    if not all([url, user, key]):
        logger.warning(f"Tracker '{tracker_type}' is configured, but URL/Auth details are missing. Check your settings.")
        return None
        
    tracker = None
    
    if tracker_type == "shotgrid":
        try:
            from shotgrid_tracker import ShotGridTracker
            tracker = ShotGridTracker(url, user, key)
        except ImportError:
            logger.error("Failed to import ShotGridTracker. Make sure shotgrid_tracker.py is available.")
            return None
    else:
        logger.error(f"Unknown tracker type configured: {tracker_type}")
        return None
        
    if tracker and tracker.connect():
        logger.info(f"Successfully initialized and connected to {tracker_type}.")
        return tracker
    else:
        logger.error(f"Failed to connect to tracker: {tracker_type}")
        return None