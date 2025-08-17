#!/usr/bin/env python

import re
import os


def extract_sprite_from_codesnip(codesnip):
    """
    Extract the sprite parameter from a code snippet.

    Args:
        codesnip (str): The code snippet text

    Returns:
        str: The sprite value or None if not found
    """
    # Find the sprite value in the code
    sprite_match = re.search(r'"sprite":\s*"([^"]+)"', codesnip)
    if sprite_match:
        sprite = sprite_match.group(1)
        return sprite
    return None


def process_code(
    text, parser_output_path, infobox_name, sprite_ids, tile_ids, language_code
):
    """
    Process the tile code section.

    Args:
        text (str): Original wikitext
        parser_output_path (str): Path to parser output
        infobox_name (str): Name from infobox
        sprite_ids (list): List of sprite IDs
        tile_ids (list): List of tile IDs
        language_code (str): Language code

    Returns:
        tuple: (updated_text, changed)
    """

    # Find the Code section
    code_section_match = re.search(r"==Code==\s*(.*?)(?=\n==|\Z)", text, re.DOTALL)
    if not code_section_match:
        return text, False

    code_section = code_section_match.group(1)

    # Find all code snippets
    codesnips = re.finditer(r"{{CodeSnip(.*?)}}", code_section, re.DOTALL)

    updated_section = code_section
    changed = False

    for codesnip in codesnips:
        codesnip_text = codesnip.group(0)

        sprite = extract_sprite_from_codesnip(codesnip_text)

        if sprite:
            # Construct the file path
            file_path = os.path.join(
                parser_output_path, language_code, "tiles", "codesnips", f"{sprite}.txt"
            )

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read().strip()

                # Replace the codesnip with the file content
                updated_section = updated_section.replace(codesnip_text, file_content)
                changed = True
            except FileNotFoundError:
                continue

    text = text.replace(code_section, updated_section)

    return text, changed
