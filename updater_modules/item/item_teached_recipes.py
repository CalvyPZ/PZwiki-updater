import re
import os
from .file_utils import read_file_with_subfolders


def process_teached_recipes(text, parser_output_path, language_code, item_id):
    """
    Process teached recipes templates in the text.
    """
    # Single regex: capture the start-flag, the id, the body, and the end-flag
    pattern = re.compile(
        r"(?P<start><!--\s*Bot flag\|TeachedRecipes\|id=(?P<id>[^>]+)\s*-->)"
        r".*?"
        r"(?P<end><!--\s*Bot flag end\|TeachedRecipes\|id=(?P=id)\s*-->)",
        re.DOTALL,
    )

    m = pattern.search(text)
    if not m:
        return text, False

    recipe_id = m.group("id").strip()

    # Load new content from file
    file_path = os.path.join(
        parser_output_path, "recipes", "teachedrecipes", f"{recipe_id}_Teached.txt"
    )
    new_content, found_path = read_file_with_subfolders(file_path)
    if not new_content:
        return text, False

    new_content = new_content.strip()

    # Replace the entire matched section with just the new content
    updated_text = pattern.sub(new_content, text)
    return updated_text, True
