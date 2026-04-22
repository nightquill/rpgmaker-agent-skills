"""Shared event traversal helpers for RPG Maker MV/MZ project files."""

from __future__ import annotations

import glob
import json
import os


def iter_event_lists(project_path: str):
    """Yield (source_label, event_list) for every event command list in the project.

    Covers CommonEvents.json and all Map[0-9]*.json files.
    Skips null entries. Handles both MV (array) and MZ (object) events fields.

    Args:
        project_path: Path to RPG Maker project root directory.

    Yields:
        Tuples of (source_label: str, event_list: list[dict]).
    """
    data_dir = os.path.join(project_path, "data")

    # CommonEvents.json
    ce_path = os.path.join(data_dir, "CommonEvents.json")
    if os.path.exists(ce_path):
        with open(ce_path, encoding="utf-8") as f:
            common_events = json.load(f)
        for entry in common_events:
            if entry is None:
                continue
            label = f"CommonEvent:{entry['id']}:{entry.get('name', '')}"
            yield (label, entry.get("list", []))

    # Map files (exclude MapInfos.json via Map[0-9]*.json glob)
    map_pattern = os.path.join(data_dir, "Map[0-9]*.json")
    for map_path in sorted(glob.glob(map_pattern)):
        map_basename = os.path.basename(map_path)
        with open(map_path, encoding="utf-8") as f:
            map_data = json.load(f)
        events = map_data.get("events", [])
        if isinstance(events, list):
            event_iter = (e for e in events if e is not None)
        else:
            event_iter = (e for e in events.values() if e is not None)
        for event in event_iter:
            event_id = event.get("id", "?")
            event_name = event.get("name", "")
            for page_idx, page in enumerate(event.get("pages", [])):
                label = f"{map_basename}:Event{event_id}:{event_name}:Page{page_idx}"
                yield (label, page.get("list", []))


def iter_event_pages(project_path: str):
    """Yield (source_label, event_dict, page_index, page_dict) for every event page.

    Useful for inspecting page conditions (switch1Id, selfSwitchCh, etc.)
    in addition to the command list.

    Args:
        project_path: Path to RPG Maker project root directory.

    Yields:
        Tuples of (source_label: str, event: dict, page_idx: int, page: dict).
    """
    data_dir = os.path.join(project_path, "data")

    # CommonEvents.json (no pages -- common events have a single list, not pages)
    # Skip -- common events don't have page conditions

    # Map files
    map_pattern = os.path.join(data_dir, "Map[0-9]*.json")
    for map_path in sorted(glob.glob(map_pattern)):
        map_basename = os.path.basename(map_path)
        with open(map_path, encoding="utf-8") as f:
            map_data = json.load(f)
        events = map_data.get("events", [])
        if isinstance(events, list):
            event_iter = (e for e in events if e is not None)
        else:
            event_iter = (e for e in events.values() if e is not None)
        for event in event_iter:
            event_id = event.get("id", "?")
            event_name = event.get("name", "")
            for page_idx, page in enumerate(event.get("pages", [])):
                label = f"{map_basename}:Event{event_id}:{event_name}:Page{page_idx}"
                yield (label, event, page_idx, page)
