import re
import os
from .file_utils import read_file_with_subfolders


def process_consumables(text, parser_output_path, language_code, item_id):
    """
    Process consumables templates in the text.
    """
    pattern = re.compile(r"(\{\{Consumables.*?\n)(.*?\n)*?(\}\})", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return text, False

    consumables_template = match.group(0)
    file_path = os.path.join(
        parser_output_path,
        language_code,
        "item",
        "consumable_properties",
        f"{item_id}.txt",
    )

    new_content, found_path = read_file_with_subfolders(file_path)
    if not new_content:
        # Try English fallback
        en_file_path = os.path.join(
            parser_output_path, "en", "item", "consumable_properties", f"{item_id}.txt"
        )
        new_content, found_path = read_file_with_subfolders(en_file_path)
        if not new_content:
            return text, False

    new_content = new_content.strip()

    updated = text.replace(consumables_template, new_content)
    return updated, True
