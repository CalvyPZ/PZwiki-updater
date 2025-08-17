#!/usr/bin/env python

import re
from scripts.userscripts.updater_modules.tile.tile_infobox import process_infobox # type: ignore
from scripts.userscripts.updater_modules.tile.tile_crafting import process_crafting # type: ignore
from scripts.userscripts.updater_modules.tile.tile_code import process_code # type: ignore
from scripts.userscripts.updater_modules.tile.tile_navbox import process_navbox # type: ignore

def extract_tile_identifiers(text):
    """
    Extract tile identifiers from the infobox.
    Returns:
        tuple: (infobox_name, sprite_ids, tile_ids)
    """
    # Find the infobox block
    m = re.search(r'\{\{Infobox\s*tile(.*?)\}\}', text, re.DOTALL | re.IGNORECASE)
    if not m:
        return None, [], []

    infobox_body = m.group(1)
    
    # Extract infobox name
    name_match = re.search(r'\|\s*name\s*=\s*([^\|\n]+)', infobox_body)
    infobox_name = name_match.group(1).strip().replace(" ", "_") if name_match else None

    # Extract sprite IDs
    sprite_ids = []
    sprite_pattern = r'\|\s*sprite_id(?:\d+)?\s*=\s*([^\|\n]+)'
    for match in re.finditer(sprite_pattern, infobox_body):
        sprite_ids.append(match.group(1).strip())

    # Extract tile IDs
    tile_ids = []
    tile_pattern = r'\|\s*tile_id(?:\d+)?\s*=\s*([^\|\n]+)'
    for match in re.finditer(tile_pattern, infobox_body):
        tile_ids.append(match.group(1).strip())

    return infobox_name, sprite_ids, tile_ids

def orchestrate_tile(text, parser_output_path, history_path, language_code):
    """
    Args:
        text (str): Original wikitext.
        parser_output_path (str)
        history_path (str)
        language_code (str)
    Returns:
        (updated_text (str), processes (list[str]))
    """
    # Extract identifiers
    infobox_name, sprite_ids, tile_ids = extract_tile_identifiers(text)

    updated = text
    processes = []

    # Process each module
    try:
        new_text, changed = process_infobox(updated, parser_output_path, language_code, infobox_name, sprite_ids, tile_ids)
        if changed:
            updated = new_text
            processes.append('Infobox')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_crafting(updated, parser_output_path, infobox_name, sprite_ids, tile_ids, language_code)
        if changed:
            updated = new_text
            processes.append('Crafting')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_code(updated, parser_output_path, infobox_name, sprite_ids, tile_ids, language_code)
        if changed:
            updated = new_text
            processes.append('Code')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_navbox(updated)
        if changed:
            updated = new_text
            processes.append('Navbox')
    except (FileNotFoundError, OSError):
        pass

    return updated, processes
