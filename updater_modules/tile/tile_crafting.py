#!/usr/bin/env python

import re
import os

def find_table_boundaries(text, section_header):
    """
    Find the start and end of a table in a section.
    
    Args:
        text (str): The full text
        section_header (str): The section header to find (e.g. "===Breakage===")
    
    Returns:
        tuple: (start_index, end_index) or (None, None) if not found
    """
    
    # Find the section
    section_match = re.search(f'{re.escape(section_header)}\\s*(.*?)(?=\\n==|\\Z)', text, re.DOTALL)
    if not section_match:
        return None, None
        
    section_text = section_match.group(1)
    
    # Find the table start
    if "Breakage" in section_header:
        table_start = section_text.find('{| class="wikitable theme-red sortable"')
    else:  # Dismantling
        table_start = section_text.find('{| class="wikitable theme-red"')
        
    if table_start == -1:
        return None, None
        
    # Find the table end
    table_end = section_text.find('|}', table_start)
    if table_end == -1:
        return None, None
        
    # Convert to absolute positions in the text
    section_start = section_match.start(1)
    return section_start + table_start, section_start + table_end + 2

def process_crafting(text, parser_output_path, infobox_name, sprite_ids, tile_ids, language_code):
    """
    Process the tile crafting section.
    
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
    
    if not infobox_name:
        return text, False
        
    changed = False
    updated_text = text
    
    # Process Breakage section
    if "===Breakage===" in text:
        breakage_file = os.path.join(
            parser_output_path,
            language_code,
            'tiles',
            'crafting',
            f'{infobox_name}_breakage.txt'
        )
        
        try:
            with open(breakage_file, 'r', encoding='utf-8') as f:
                breakage_content = f.read().strip()
                
            start, end = find_table_boundaries(text, "===Breakage===")
            if start is not None and end is not None:
                updated_text = updated_text[:start] + breakage_content + updated_text[end:]
                changed = True
        except FileNotFoundError:
            pass
            
    # Process Dismantling section
    if "===Dismantling===" in text:
        dismantling_file = os.path.join(
            parser_output_path,
            language_code,
            'tiles',
            'crafting',
            f'{infobox_name}_scrapping.txt'
        )
        
        try:
            with open(dismantling_file, 'r', encoding='utf-8') as f:
                dismantling_content = f.read().strip()

            start, end = find_table_boundaries(text, "===Dismantling===")
            if start is not None and end is not None:
                updated_text = updated_text[:start] + dismantling_content + updated_text[end:]
                changed = True
        except FileNotFoundError:
            pass
            
    return updated_text, changed 