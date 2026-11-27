"""External review player (Open RV / RV) launcher with OS-default fallback.

Resolves a user-configured or auto-detected Open RV / Autodesk RV executable from preferences, optionally pushes media into an already-running RV session via ``rvpush``, and falls back cleanly to the operating system's default media player when no RV binary is available.

:File: review_player.py
:License: Apache License 2.0 (Apache-2.0)
"""

from collections.abc import Sequence
import glob
import logging
import os
import re
import shutil
import subprocess
import sys

from openpypeline.core.util import prefs

#: Module logger for external review player discovery and launch events.
logger = logging.getLogger("openPypeline.review_player")

#: Candidate RV binary names searched on ``PATH`` during auto-detection.
RV_CANDIDATE_NAMES: tuple[str, ...] = (
    "rv",
    "RV",
    "rv64",
    "RV64",
    "OpenRV",
    "openrv",
)

#: Common macOS application bundle binary paths checked during auto-detection.
MACOS_RV_APP_PATHS: tuple[str, ...] = (
    "/Applications/RV.app/Contents/MacOS/RV",
    "/Applications/OpenRV.app/Contents/MacOS/OpenRV",
)


def detect_rv_executable() -> str:
    """Locate an Open RV or Autodesk RV executable on the local machine.

    Searches ``PATH`` for common RV binary names and checks standard macOS ``/Applications`` bundle locations.

    :returns: Normalized path to a discovered RV executable, or an empty string if none is found.
    """
    for candidate in RV_CANDIDATE_NAMES:
        found = shutil.which(candidate)
        if found:
            return os.path.abspath(found).replace("\\", "/")

    if sys.platform == "darwin":
        for app_bin in MACOS_RV_APP_PATHS:
            if os.path.isfile(app_bin) and os.access(app_bin, os.X_OK):
                return app_bin

    return ""


def resolve_review_player() -> str:
    """Return the configured review player executable path, if set.

    Reads ``ops_reviewPlayerPath`` from user preferences, expands user and environment variables, and resolves macOS ``.app`` bundles to their inner executable binary when necessary.

    :returns: Normalized executable path string, or an empty string when unconfigured.
    """
    configured = str(prefs.get_pref("ops_reviewPlayerPath", "") or "").strip()
    if not configured:
        return ""

    expanded = os.path.abspath(
        os.path.expanduser(os.path.expandvars(configured))
    ).replace("\\", "/")

    if sys.platform == "darwin" and expanded.endswith(".app") and os.path.isdir(expanded):
        macos_dir = os.path.join(expanded, "Contents", "MacOS")
        app_stem = os.path.splitext(os.path.basename(expanded))[0]
        candidate = os.path.join(macos_dir, app_stem)
        if os.path.isfile(candidate):
            return candidate.replace("\\", "/")
        if os.path.isdir(macos_dir):
            for entry in sorted(os.listdir(macos_dir)):
                full_entry = os.path.join(macos_dir, entry)
                if os.path.isfile(full_entry) and os.access(full_entry, os.X_OK):
                    return full_entry.replace("\\", "/")

    return expanded


def _find_rvpush(rv_executable: str) -> str:
    """Locate ``rvpush`` alongside ``rv_executable`` or on ``PATH``.

    :param rv_executable: Resolved path to the main RV binary.
    :returns: Path to ``rvpush``, or an empty string if unavailable.
    """
    rv_dir = os.path.dirname(rv_executable)
    exe_suffix = ".exe" if sys.platform.startswith("win") else ""
    sibling = os.path.join(rv_dir, f"rvpush{exe_suffix}")
    if os.path.isfile(sibling):
        return sibling
    return shutil.which("rvpush") or ""


def _resolve_sequence_for_os(media_path: str) -> str:
    """Resolve an RV ``#`` sequence mask to its first existing frame on disk.

    :param media_path: File path or RV ``#``-padded sequence pattern.
    :returns: Concrete path to the first matching frame, or an empty string if no frames match on disk.
    """
    if "#" not in media_path:
        return media_path
    pattern = re.sub(r"#+", "*", media_path)
    matches = sorted(glob.glob(pattern))
    return matches[0].replace("\\", "/") if matches else ""


def _media_exists(media_path: str) -> bool:
    """Return ``True`` if ``media_path`` is an existing file or ``#`` sequence.

    :param media_path: File path or RV ``#``-padded sequence pattern.
    :returns: ``True`` when the target file or at least one sequence frame
        exists on disk, otherwise ``False``.
    """
    if not media_path:
        return False
    if "#" in media_path:
        return bool(_resolve_sequence_for_os(media_path))
    return os.path.exists(media_path)


def open_with_os_default(filepath: str) -> bool:
    """Open a media file using the operating system's default application.

    Resolves ``#`` sequence masks to their first frame before invoking the platform opener (``open`` on macOS, ``os.startfile`` on Windows, or ``xdg-open`` on Linux).

    :param filepath: Existing filesystem path or sequence mask to open.
    :returns: ``True`` if the OS launch command succeeded, ``False`` otherwise.
    """
    target = _resolve_sequence_for_os(filepath)
    if not target or not os.path.exists(target):
        logger.warning("Target media does not exist for OS fallback: %s", filepath)
        return False

    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", target])
        elif sys.platform.startswith("win"):
            os.startfile(target)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", target])
        return True
    except Exception as error:
        logger.error("Failed to open '%s' with OS default player: %s", target, error)
        return False


def launch_review_player(media_paths: Sequence[str]) -> bool:
    """Launch Open RV / RV (or the OS default player) for one or more media paths.

    When ``ops_reviewPlayerPath`` points to a valid executable, launches it with ``media_paths`` (or pushes them into an active RV session via ``rvpush merge`` when ``ops_reviewPlayerReuseSession`` is enabled). If no review player is configured or found, opens each item with the OS default player.

    :param media_paths: Ordered sequence of playblast file or ``#`` image-sequence paths to load for review.
    :returns: ``True`` if playback was started successfully, ``False`` otherwise.
    """
    paths = [
        os.path.abspath(p).replace("\\", "/")
        for p in media_paths
        if _media_exists(p)
    ]
    if not paths:
        logger.warning("No existing media files provided to launch_review_player.")
        return False

    player_exe = resolve_review_player()
    if player_exe and os.path.isfile(player_exe):
        reuse_session = bool(prefs.get_pref("ops_reviewPlayerReuseSession", False))
        if reuse_session:
            rvpush_exe = _find_rvpush(player_exe)
            if rvpush_exe:
                try:
                    subprocess.Popen([rvpush_exe, "merge", *paths])
                    return True
                except Exception as error:
                    logger.warning(
                        "rvpush failed (%s); falling back to direct RV launch.", error
                    )

        try:
            subprocess.Popen([player_exe, *paths])
            return True
        except Exception as error:
            logger.error(
                "Failed to launch review player '%s': %s. Falling back to OS player.",
                player_exe,
                error,
            )
    elif player_exe:
        logger.warning(
            "Configured review player was not found at '%s'; falling back to OS player.",
            player_exe,
        )

    return all(open_with_os_default(path) for path in paths)
