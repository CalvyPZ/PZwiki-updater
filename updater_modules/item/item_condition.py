import re
import os
from .file_utils import read_file_with_subfolders


def process_condition(text, parser_output_path, language_code, item_id):
    """
    Process condition/durability templates in the text.
    """
    pattern = r"(\{\{Durability weapon.*?\}\})"
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        return text, False

    old_template = match.group(0)
    file_path = os.path.join(
        parser_output_path, language_code, "item", "infoboxes", f"{item_id}.txt"
    )

    infobox_text, found_path = read_file_with_subfolders(file_path)
    if not infobox_text:
        # Try English fallback
        en_file_path = os.path.join(
            parser_output_path, "en", "item", "infoboxes", f"{item_id}.txt"
        )
        infobox_text, found_path = read_file_with_subfolders(en_file_path)
        if not infobox_text:
            return text, False

    def extract_value(key):
        m = re.search(rf"\|{key}\s*=\s*(.*)", infobox_text)
        return m.group(1).strip() if m else ""

    skill_type = extract_value("skill_type")
    if skill_type.startswith("[[") and skill_type.endswith("]]"):
        skill_type = skill_type[2:-2].capitalize()
    condition_max = extract_value("condition_max")
    condition_lower_chance = extract_value("condition_lower_chance")

    new_template = f"{{{{Durability weapon|{condition_lower_chance}|{condition_max}|skill={skill_type}}}}}"
    updated = text.replace(old_template, new_template)
    has_changes = new_template != old_template
    return updated, has_changes
