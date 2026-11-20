"""Note Management and Formatting for openPypeline Studio.

Handles reading, parsing, filtering, and formatting JSON event notes for
pipeline assets and shots. Refactored from legacy XML formats to modern JSON.

:File: ops_notes.py
:Original Framework: openPipeline by Kickstand
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    from openpypeline.core.notes import ops_notes

    formatted = ops_notes.read_notes_formatted("/projects/demo/assets/hero/notes/hero_AssetNote.json")
    total = ops_notes.count_notes("/projects/demo/assets/hero/notes/hero_AssetNote.json")
"""

import json
import os
from typing import Any, Union


def read_notes_formatted(input_path: str) -> list[str]:
    """Read and format all JSON note entries as human-readable text blocks.

    Loads notes via :func:`read_all_notes` and formats each dictionary with
    :func:`format_note`.

    :param input_path: Full path to the item's JSON note file.
    :returns: List of formatted multi-line note strings ordered newest first.
    """
    notes = read_all_notes(input_path)
    return [format_note(note) for note in notes]


def format_note(note_dict: dict[str, Any]) -> str:
    """Format a single JSON note dictionary into a display-ready string.

    Extracts ``author``, ``date``, ``time``, ``event``, and optional
    ``version`` and ``comment`` keys into a structured multi-line block.

    :param note_dict: Dictionary representing a single note entry.
    :returns: Multi-line formatted string ready for UI display.
    """
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


def read_all_notes(input_path: str) -> list[dict[str, Any]]:
    """Read all notes for a pipeline item in reverse chronological order.

    :param input_path: Full path to the item's JSON note file.
    :returns: List of note dictionaries ordered newest first, or an empty list
        if the file does not exist, is invalid JSON, or does not contain a list.
    """
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


def count_notes(input_path: str) -> int:
    """Count the total number of note entries stored for an item.

    :param input_path: Full path to the item's JSON note file.
    :returns: Total count of note entries found via :func:`read_all_notes`.
    """
    return len(read_all_notes(input_path))


def read_individual_note(input_path: str, index: int) -> dict[str, Any]:
    """Retrieve a single note entry by its reverse-chronological index.

    :param input_path: Full path to the item's JSON note file.
    :param index: Zero-based index into the newest-first note list returned by
        :func:`read_all_notes`.
    :returns: The note dictionary at ``index``, or an empty dictionary if
        ``index`` is out of range.
    """
    notes = read_all_notes(input_path)
    if 0 <= index < len(notes):
        return notes[index]
    return {}


def read_notes_by_event(input_path: str, event_type: str) -> list[dict[str, Any]]:
    """Filter an item's notes by a specific pipeline event type.

    Performs a case-insensitive comparison against each entry's ``"event"``
    field.

    :param input_path: Full path to the item's JSON note file.
    :param event_type: Event name to match (for example, ``"master"`` or
        ``"wip"``).
    :returns: List of matching note dictionaries ordered newest first.
    """
    notes = read_all_notes(input_path)
    return [
        n for n in notes if str(n.get("event", "")).lower() == str(event_type).lower()
    ]


def read_notes_by_type(input_path: str, note_type: str) -> list[dict[str, Any]]:
    """Filter an item's notes by a specific note category.

    Performs a case-insensitive comparison against each entry's ``"notetype"``
    field.

    :param input_path: Full path to the item's JSON note file.
    :param note_type: Note category identifier to match.
    :returns: List of matching note dictionaries ordered newest first.
    """
    notes = read_all_notes(input_path)
    return [
        n
        for n in notes
        if str(n.get("notetype", "")).lower() == str(note_type).lower()
    ]


def read_notes_by_version(
    input_path: str, version: Union[int, str]
) -> list[dict[str, Any]]:
    """Read and filter an item's notes for a specific version number.

    Loads notes via :func:`read_all_notes` and delegates filtering to
    :func:`cull_notes_by_version`.

    :param input_path: Full path to the item's JSON note file.
    :param version: Version number or string to match against each note's
        ``"version"`` field.
    :returns: List of matching note dictionaries ordered newest first.
    """
    notes = read_all_notes(input_path)
    return cull_notes_by_version(notes, version)


def cull_notes_by_version(
    all_notes: list[dict[str, Any]], version: Union[int, str]
) -> list[dict[str, Any]]:
    """Filter an existing list of note dictionaries by version number.

    :param all_notes: List of note dictionaries to filter.
    :param version: Version number or string to match against each note's
        ``"version"`` field.
    :returns: Subset of ``all_notes`` whose ``"version"`` matches ``version``.
    """
    return [n for n in all_notes if str(n.get("version", "")) == str(version)]
