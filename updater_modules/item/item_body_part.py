import re
import os
from .file_utils import read_file_with_subfolders


def process_body_parts(text, parser_output_path, language_code):
    """
    Process body part templates in the text.
    """
    pattern = re.compile(r"\{\{Body part.*?\}\}", re.DOTALL)
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text, False

    updated = text
    has_changes = False

    for match in matches:
        template = match.group(0)
        id_match = re.search(r"\|id\s*=\s*([^\|\n]+)", template)
        if not id_match:
            continue

        body_part_id = id_match.group(1).strip()
        file_path = os.path.join(
            parser_output_path,
            language_code,
            "item",
            "body_parts",
            f"{body_part_id}.txt",
        )

        file_content, found_path = read_file_with_subfolders(file_path)
        if file_content:
            new_content = file_content.strip()
            updated = updated.replace(template, new_content)
            has_changes = True

    return updated, has_changes
