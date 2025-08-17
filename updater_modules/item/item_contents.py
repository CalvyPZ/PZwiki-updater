import re
import os
from .file_utils import read_file_with_subfolders


def process_contents(text, parser_output_path, language_code, item_id):
    """
    Process container contents tables in the text.
    """
    # Find the table with either collapsible or collapsed class
    pattern = r'{\| class="wikitable theme-red sortable mw-collapsible(?: mw-collapsed)?" id="contents-([^"]+)"'
    match = re.search(pattern, text)
    if not match:
        return text, False

    contents_id = match.group(1).strip()

    # Check for the file
    file_path = os.path.join(
        parser_output_path,
        language_code,
        "item",
        "container_contents",
        f"contents-{contents_id}.txt",
    )
    new_content, found_path = read_file_with_subfolders(file_path)
    if not new_content:
        return text, False

    new_content = new_content.strip()

    # Find the table to replace (from start to first |})
    start_pattern = r'{\| class="wikitable theme-red sortable mw-collapsible(?: mw-collapsed)?" id="contents-[^"]+"'
    start_match = re.search(start_pattern, text)

    if not start_match:
        return text, False

    # Find the end of the table
    remaining_text = text[start_match.start() :]
    end_match = re.search(r"\|\}", remaining_text)

    if not end_match:
        return text, False

    # Replace the entire table
    start_pos = start_match.start()
    end_pos = start_match.start() + end_match.end()
    old_table = text[start_pos:end_pos]

    updated = text.replace(old_table, new_content)
    return updated, True
