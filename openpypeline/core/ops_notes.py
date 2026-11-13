"""
File: ops_notes.py
Description: Note Management and Formatting for openPypeline Studio. Handles reading, parsing, and formatting JSON event notes. Refactored from XML legacy formats to modern JSON.

Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import json


def read_notes_formatted(input_path):
    """Formats notes in JSON format to be displayed as text."""
    notes = read_all_notes(input_path)
    return [format_note(note) for note in notes]


def format_note(note_dict):
    """Formats a JSON note dictionary to be displayed."""
    author = note_dict.get("author", "")
    date = note_dict.get("date", "")
    time = note_dict.get("time", "")
    event = note_dict.get("event", "")
    version = note_dict.get("version", "")
    comment = note_dict.get("comment", "")

    formatted_note = f"Author: {author}\nDate: {date} {time}\nEvent: {event}"
    if version:
        formatted_note += f" (Version: {version})\n"
    else:
        formatted_note += "\n"

    if comment:
        formatted_note += f"Comment: {comment}\n\n"
    else:
        formatted_note += "\n"

    return formatted_note


def read_all_notes(input_path):
    """Read all notes of a specified item, returned in reverse order."""
    if not os.path.isfile(input_path):
        return []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        if isinstance(content, list):
            # Return in reverse order (newest first)
            return content[::-1]
        return []
    except Exception:
        return []


def count_notes(input_path):
    """Counts the number of note entries for a specific item."""
    return len(read_all_notes(input_path))


def read_individual_note(input_path, index):
    """Reads an individual note."""
    notes = read_all_notes(input_path)
    if 0 <= index < len(notes):
        return notes[index]
    return {}


def read_notes_by_event(input_path, event_type):
    """Read all notes that describe a particular event."""
    notes = read_all_notes(input_path)
    return [n for n in notes if str(n.get("event", "")).lower() == str(event_type).lower()]


def read_notes_by_type(input_path, note_type):
    """Read all notes that match a particular type."""
    notes = read_all_notes(input_path)
    return [n for n in notes if str(n.get("notetype", "")).lower() == str(note_type).lower()]


def read_notes_by_version(input_path, version):
    """Read all notes that match a particular version."""
    notes = read_all_notes(input_path)
    return cull_notes_by_version(notes, version)


def cull_notes_by_version(all_notes, version):
    """Filter notes that match a particular version."""
    return [n for n in all_notes if str(n.get("version", "")) == str(version)]