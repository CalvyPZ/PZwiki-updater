#!/usr/bin/env python

import re
import os

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
EXCLUDED_PARAMS = [] # [r'^icon\d*$', r'^category$']

CORRECT_ORDER = [
    "name", "icon", "icon_name", "icon2", "icon_name2", "icon3", "icon_name3", "icon4", "icon_name4",
    "icon5", "icon_name5", "icon6", "icon_name6", "icon7", "icon_name7", "icon8", "icon_name8",
    "icon9", "icon_name9", "category", "weight", "size", "placement", "function", "type", "container",
    "health", "capacity", "liquid_capacity", "freezer_capacity", "fuel", "contents", "strength", "animals",
    "bed_type", "is_table_top", "is_low", "build_skill", "build_level", "build_tool", "ingredients",
    "move_skill", "move_level", "move_tool", "move_type", "pickup_skill", "pickup_level",
    "pickup_tool", "pickup_tool_tag", "place_tool", "place_tool_tag", "disassemble_skill", "disassemble_level",
    "disassemble_tool", "disassemble_tool2", "disassemble_tool3", "disassemble_tool4",
    "disassemble_tool_tag", "disassemble_tool_tag2", "disassemble_tool_tag3", "disassemble_tool_tag4",
    "products", "tags", "item_id", "item_id_more", "tile_id", "tile_id2",
    "tile_id3", "tile_id4", "tile_id5", "tile_id6", "tile_id7", "tile_id8", "tile_id9",
    "sprite_id", "sprite_id2", "sprite_id3", "sprite_id4", "sprite_id5", "sprite_id6", "sprite_id7", "sprite_id8", "sprite_id9",
    "sprite_id_more", "infobox_version"
]

def parse_infobox(infobox_text):
    """Parse an infobox into a dictionary of parameters."""
    infobox_params = {}
    lines = infobox_text.split('\n')
    for line in lines:
        match = re.match(r'\|\s*([^=]+)\s*=\s*(.*)', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            infobox_params[key] = value
    return infobox_params

def ensure_icon_naming_convention(params):
    """Rename imageX to iconX and ensure icon_nameX follows each iconX."""
    updated_params = {}
    icon_name_template = "icon_name{}"

    for key, value in params.items():
        # Replace imageX with iconX
        image_match = re.match(r'^image(\d*)$', key)
        if image_match:
            index = image_match.group(1)
            new_key = f"icon{index}"
            updated_params[new_key] = value
            icon_name_key = icon_name_template.format(index)
            if icon_name_key not in params:
                updated_params[icon_name_key] = f"default_icon_name{index}"
        else:
            updated_params[key] = value

    return updated_params

def rebuild_infobox(params):
    """Rebuild the infobox from parameters, following the correct order."""
    rebuilt_infobox = "{{Infobox tile\n"
    # Rebuild in the correct order
    for key in CORRECT_ORDER:
        if key in params:
            rebuilt_infobox += f"|{key}={params[key]}\n"
    # Add any parameters that aren't in the order list
    for key, value in params.items():
        if key not in CORRECT_ORDER:
            rebuilt_infobox += f"|{key}={value}\n"
    rebuilt_infobox += "}}"
    return rebuilt_infobox

def update_infobox(page_params, local_params):
    """Compare infoboxes and update the page's infobox."""
    updated_params = page_params.copy()

    for key, local_value in local_params.items():
        # Skip excluded parameters
        if any(re.match(pattern, key) for pattern in EXCLUDED_PARAMS):
            continue

        # Update if parameter is missing or different
        page_value = page_params.get(key, None)
        if page_value != local_value:
            updated_params[key] = local_value

    # Ensure icon naming conventions
    updated_params = ensure_icon_naming_convention(updated_params)

    # Add missing parameters from correct order
    for key in CORRECT_ORDER:
        if key in local_params and key not in updated_params:
            updated_params[key] = local_params[key]

    return updated_params

def process_infobox(text, parser_output_path, language_code, infobox_name, sprite_ids, tile_ids):
    """
    Process the tile infobox section.
    
    Args:
        text (str): Original wikitext
        parser_output_path (str): Path to parser output
        language_code (str): Language code
        infobox_name (str): Name from infobox
        sprite_ids (list): List of sprite IDs
        tile_ids (list): List of tile IDs
    
    Returns:
        tuple: (updated_text, changed)
    """
    
    # Find the infobox block
    match = re.search(r'(\{\{Infobox\s*tile[\s\S]*?\n\}\})', text, re.IGNORECASE)
    if not match:
        return text, False
    infobox_block = match.group(1)

    # Check if infobox name is provided
    if not infobox_name:
        return text, False

    # Parse the page's infobox
    page_params = parse_infobox(infobox_block)

    # Build and load the pre-parsed infobox file
    file_path = os.path.join(
        parser_output_path,
        language_code,
        'tiles',
        'infoboxes',
        f'{infobox_name}.txt'
    )
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_lines = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        return text, False

    # Parse the file lines into a dict
    local_params = parse_infobox('\n'.join(file_lines))

    # Update the infobox
    updated_params = update_infobox(page_params, local_params)

    # Check if any changes were made
    if updated_params == page_params:
        return text, False

    # Rebuild and replace the infobox
    updated_infobox = rebuild_infobox(updated_params)
    new_text = text.replace(infobox_block, updated_infobox, 1)

    return new_text, True 