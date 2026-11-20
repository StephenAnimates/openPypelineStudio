"""Factory for creating and connecting to a production tracker instance.

Dynamically resolves tracker configuration from user preferences (or explicit
arguments) and instantiates the matching production tracking backend.

:File: tracker_factory.py
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    from openpypeline.core import tracker_factory

    tracker = tracker_factory.get_tracker()
    if tracker:
        tracker.publish_version(task_id=42, file_path="/projects/demo/hero.ma", version_num=1)
"""

import logging
from typing import Any, Optional

from openpypeline.core.util import prefs

#: Module logger for production tracker instantiation and connection events.
logger = logging.getLogger("openPypeline.tracking.factory")


def get_tracker(
    tracker_type: Optional[str] = None,
    url: Optional[str] = None,
    user: Optional[str] = None,
    key: Optional[str] = None,
) -> Optional[Any]:
    """Instantiate and connect to the configured production tracker.

    Reads missing connection parameters from user preferences (``ops_tracker_type``,
    ``ops_tracker_url``, ``ops_tracker_user``, and ``ops_tracker_key``),
    initializes the matching tracker backend, and verifies connectivity via
    ``tracker.connect()``.

    :param tracker_type: Tracker backend identifier (for example,
        ``"shotgrid"`` or ``"none"``). Defaults to the ``ops_tracker_type``
        preference.
    :param url: Base server URL for the production tracker. Defaults to the
        ``ops_tracker_url`` preference.
    :param user: Login username or script name used for authentication.
        Defaults to the ``ops_tracker_user`` preference.
    :param key: API key or password used for authentication. Defaults to the
        ``ops_tracker_key`` preference.
    :returns: A connected :class:`~openpypeline.core.tracker.ProductionTracker`
        subclass instance, or ``None`` if tracking is disabled, misconfigured,
        or fails to connect.
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
        logger.warning(
            f"Tracker '{tracker_type}' is configured, but URL/Auth details are missing. Check your settings."
        )
        return None

    tracker = None

    if tracker_type == "shotgrid":
        try:
            from openpypeline.core.shotgrid_tracker import ShotGridTracker

            tracker = ShotGridTracker(url, user, key)
        except ImportError:
            logger.error(
                "Failed to import ShotGridTracker. Make sure shotgrid_tracker.py is available."
            )
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
