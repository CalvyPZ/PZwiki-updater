import re
import os

def update_fluid_infobox(text, parser_output_path, history_path, language_code):
    """Update the fluid infobox with content from the parser output file."""
    
    # Find the infobox
    infobox_pattern = r'\{\{Infobox fluid.*?\n\}\}'
    infobox_match = re.search(infobox_pattern, text, re.DOTALL)
    if not infobox_match:
        return text, [], False
    
    # Find the fluid_id
    fluid_id_match = re.search(r'\|fluid_id=(.*?)$', infobox_match.group(0), re.MULTILINE)
    if not fluid_id_match:
        return text, [], False
    
    fluid_id = fluid_id_match.group(1).strip()
    if fluid_id.startswith('Base.'):
        fluid_id = fluid_id[5:]  # Remove 'Base.' prefix
    
    # Construct the path to the infobox file
    infobox_path = os.path.join(parser_output_path, language_code, 'fluid_infoboxes', f'{fluid_id}.txt')
    
    # Read the new infobox content
    try:
        with open(infobox_path, 'r', encoding='utf-8') as f:
            new_infobox = f.read().strip()
    except FileNotFoundError:
        return text, [], False
    
    # Replace the old infobox with the new one
    new_text = text[:infobox_match.start()] + new_infobox + text[infobox_match.end():]
    
    # Check if any changes were made
    was_edited = new_text != text
    
    return new_text, ['fluid_infobox'] if was_edited else [], was_edited 