import re
import os
from .file_utils import read_file_with_subfolders


def process_fixing(text, parser_output_path, language_code):
    """
    Process fixing templates in the text.
    """
    pattern = re.compile(r"(\{\{Fixing.*?\n)(.*?\n)*?\}\}", re.DOTALL)
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text, False

    updated = text
    has_changes = False

    for match in matches:
        fixing_template = match.group(0)
        fixing_id_match = re.search(r"\|fixing_id\s*=\s*([^\|\n]+)", fixing_template)
        if not fixing_id_match:
            continue

        fixing_id = fixing_id_match.group(1).strip()
        file_path = os.path.join(
            parser_output_path, language_code, "fixing", f"{fixing_id}.txt"
        )

        file_content, found_path = read_file_with_subfolders(file_path)
        if file_content:
            new_content = file_content.strip()
            updated = updated.replace(fixing_template, new_content)
            has_changes = True

    return updated, has_changes
