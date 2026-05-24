"""
File: opsNotes.py
Description: Note Management and Formatting for openPypeline Studio.
             Handles reading, parsing, and formatting XML event notes.
             Refactored from openPipelineNotes.mel to Python 3.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import os
import re


def read_xml(input_path):
    """Formats notes in XML format to be displayed."""
    notes = read_all_notes(input_path)
    return [format_xml(note) for note in notes]


def format_xml(line):
    """Formats an XML note to be displayed."""
    author = _extract_tag(line, "author")
    date = _extract_tag(line, "date")
    time = _extract_tag(line, "time")
    event = _extract_tag(line, "event")
    version = _extract_tag(line, "version")
    comment = _extract_tag(line, "comment")

    formatted_xml = f"Author: {author}\nDate: {date} {time}\nEvent: {event}"
    if version:
        formatted_xml += f" (Version: {version})\n"
    else:
        formatted_xml += "\n"

    if comment:
        formatted_xml += f"Comment: {comment}\n\n"
    else:
        formatted_xml += "\n"

    return formatted_xml


def _extract_tag(text, tag):
    """Helper to extract contents of an XML tag."""
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def read_all_notes(input_path):
    """Read all notes of a specified item, returned in reverse order."""
    if not os.path.isfile(input_path):
        return []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []

    # Find all notes and keep the <note> tags to match the original MEL behavior
    notes = re.findall(r"<note>(.*?)</note>", content, re.IGNORECASE | re.DOTALL)
    notes = [f"<note>{n}</note>" for n in notes]
    
    # Return in reverse order (newest first)
    return notes[::-1]


def count_notes(input_path):
    """Counts the number of note entries for a specific item."""
    return len(read_all_notes(input_path))


def read_individual_note(input_path, index):
    """Reads an individual note."""
    notes = read_all_notes(input_path)
    if 0 <= index < len(notes):
        return notes[index]
    return ""


def read_notes_by_event(input_path, event_type):
    """Read all notes that describe a particular event."""
    notes = read_all_notes(input_path)
    return [n for n in notes if re.search(f"<event>{event_type}</event>", n, re.IGNORECASE)]


def read_notes_by_type(input_path, note_type):
    """Read all notes that match a particular type."""
    notes = read_all_notes(input_path)
    return [n for n in notes if re.search(f"<notetype>{note_type}</notetype>", n, re.IGNORECASE)]


def read_notes_by_version(input_path, version):
    """Read all notes that match a particular version."""
    notes = read_all_notes(input_path)
    return cull_notes_by_version(notes, version)


def cull_notes_by_version(all_notes, version):
    """Filter notes that match a particular version."""
    return [n for n in all_notes if re.search(f"<version>{version}</version>", n, re.IGNORECASE)]