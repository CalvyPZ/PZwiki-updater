import os
import re
from .file_utils import read_file_with_subfolders


def process_history(
    text,
    history_path,
):
    """
    Args:
        text (str): full page wikitext
        parser_output_path (str)
        history_path (str)
        language_code (str)
        item_id (str): not used, each history table has its own item_id

    Returns:
        (updated_text (str), changed (bool))
    """
    updated = False
    result = text

    # Find all history table blocks
    pattern = re.compile(
        r"(?m)^\s*{{HistoryTable\|(.*?)^\s*}}\s*$", re.MULTILINE | re.DOTALL
    )

    # Keep track of processed blocks to handle spacing
    processed_blocks = []

    for match in re.finditer(pattern, text):
        history_block = match.group(0)
        block_content = match.group(1)

        # Extract item_id from the history block
        id_match = re.search(r"\|\s*item_id\s*=\s*([^\|\n]+)", block_content)
        if not id_match:
            continue

        block_item_id = id_match.group(1).strip()

        # Look for corresponding history file
        history_file = os.path.join(history_path, f"{block_item_id}.txt")

        file_content, found_path = read_file_with_subfolders(history_file)
        if file_content:
            new_history = (
                file_content.strip()
            )  # Strip to remove any trailing whitespace

            if new_history != history_block:
                processed_blocks.append((history_block, new_history))
                updated = True
        else:
            continue

    # Apply all replacements while ensuring proper spacing
    if processed_blocks:
        for old_block, new_block in processed_blocks:
            # Replace the block while ensuring it's surrounded by newlines
            result = result.replace(old_block, f"\n{new_block}\n")

        # Clean up any potential multiple consecutive newlines
        result = re.sub(r"\n{3,}", "\n\n", result)

    return result, updated
