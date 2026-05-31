"""
File: ops_utils.py
Description:
    General utility functions for openPypeline Studio.
    Replaces the legacy openPipelineUtility.mel script.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""
import os
import re


def is_valid_folder(path):
    """Returns whether a folder exists and doesn't start with a period (e.g. .svn)."""
    if not os.path.isdir(path):
        return False
    return not os.path.basename(path.rstrip("/\\")).startswith(".")

def get_folder_from_path(path, offset_from_last):
    """Returns the folder name at a given depth of a path."""
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    idx = len(parts) - 1 - offset_from_last
    if idx >= 0 and idx < len(parts):
        return parts[idx]
    return ""