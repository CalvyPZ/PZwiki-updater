import os
import re


# --------------------------------------------------------------------------
# Order in which vehicle infobox parameters should appear
# --------------------------------------------------------------------------
SORT_ORDER = [
    "|name",
    "|media_title",
    "|icon",
    "|icon2",
    "|icon3",
    "|icon4",
    "|icon5",
    "|icon_name",
    "|icon_name2",
    "|icon_name3",
    "|icon_name4",
    "|icon_name5",
    "|model",
    "|model2",
    "|model3",
    "|model4",
    "|model5",
    "|category",
    "|weight",
    "|capacity",
    "|seats",
    "|max_speed",
    "|engine_force",
    "|engine_quality",
    "|engine_power",
    "|mass",
    "|suspension_damping",
    "|suspension_compression",
    "|max_suspension_force",
    "|engine_loudness",
    "|headlight_range",
    "|gas_consumption",
    "|trunk_capacity",
    "|glove_compartment_capacity",
    "|tire_friction",
    "|brake_force",
    "|condition_max",
    "|player_damage_protection",
    "|script_name",
    "|skin",
    "|skin2",
    "|skin3",
    "|skin4",
    "|skin5",
    "|vehicle_id",
    "|vehicle_id2",
    "|vehicle_id3",
    "|vehicle_id4",
    "|vehicle_id5",
    "|infobox_version",
]


def sort_infobox(infobox: str) -> str:
    lines = infobox.split("\n")
    body = lines[1:-1]

    def key_fn(line):
        key = line.split("=", 1)[0].strip()
        return SORT_ORDER.index(key) if key in SORT_ORDER else len(SORT_ORDER)

    sorted_body = sorted(body, key=key_fn)
    return "{{Infobox vehicle\n" + "\n".join(sorted_body) + "\n}}"


def process_infobox(
    text, parser_output_path, language_code, vehicle_id, article_name=None
):
    """
    Args:
        text (str): Full page wikitext
        parser_output_path (str)
        language_code (str)
        vehicle_id (str|None)
        article_name (str|None): The name of the article, passed from the main bot system

    Returns:
        (new_text (str), changed (bool))
    """

    # Import here to avoid circular imports
    from ..item.file_utils import read_file_with_subfolders

    # 1) Extract the first {{Infobox vehicle…}} block
    match = re.search(r"(\{\{Infobox\s*vehicle[\s\S]*?\n\}\})", text, re.IGNORECASE)
    if not match:
        return text, False
    infobox_block = match.group(1)

    if not vehicle_id:
        return text, False

    # 2) Parse the page's infobox into a dict
    infobox_dict = {}
    for line in infobox_block.split("\n")[1:-1]:
        if "=" in line:
            k, v = line.split("=", 1)
            infobox_dict[k.strip()] = v.strip()

    file_lines = []

    # Try with article name first if available
    if article_name:
        article_name = article_name.replace(" ", "_")
        article_name = article_name.replace("'", "%27")
        article_name = article_name.replace(":", "%3A")
        article_name = article_name.replace('"', "%22")
        article_name = article_name.replace(",", "%2C")
        article_name = article_name.replace("!", "%21")
        article_name = article_name.replace(";", "%3B")
        article_name = article_name.replace("&", "%26")
        article_name = article_name.replace("?", "%3F")
        article_file_path = os.path.join(
            parser_output_path,
            language_code,
            "vehicle",
            "infoboxes",
            f"{article_name}.txt",
        )
        file_content, found_path = read_file_with_subfolders(article_file_path)
        if file_content:
            file_lines = [ln.strip() for ln in file_content.splitlines() if ln.strip()]
        else:
            infobox_version = infobox_dict.get("infobox_version")
            if "41.78.16" in infobox_block:
                pass
            else:
                print(f"Article file not found: {article_file_path}")
                pass

    # If article name file doesn't exist or no article name provided, use vehicle_id
    if not file_lines:
        vehicle_id_file_path = os.path.join(
            parser_output_path,
            language_code,
            "vehicle",
            "infoboxes",
            f"{vehicle_id}.txt",
        )
        file_content, found_path = read_file_with_subfolders(vehicle_id_file_path)
        if file_content:
            file_lines = [ln.strip() for ln in file_content.splitlines() if ln.strip()]
        else:
            return text, False

    # 4) Parse the file lines into a dict
    file_dict = {}
    for ln in file_lines:
        if "=" in ln:
            k, v = ln.split("=", 1)
            file_dict[k.strip()] = v.strip()

    # 5) Create a new infobox dict starting fresh with the file data
    new_infobox_dict = {}
    changed = False

    # First, copy over protected parameters from the original infobox
    protected_prefixes = (
        "|icon",
        "|icon_name",
        "|model",
        "|media_title",
        "|skin",
    )
    for key, value in infobox_dict.items():
        if any(key.startswith(prefix) for prefix in protected_prefixes):
            new_infobox_dict[key] = value

    # Then add all parameters from the file_dict
    for key, value in file_dict.items():
        # Skip if it's a protected parameter
        if any(key.startswith(prefix) for prefix in protected_prefixes):
            continue

        old = infobox_dict.get(key)
        if old is None or old != value:
            changed = True
        new_infobox_dict[key] = value

    # Also mark as changed if any non-protected parameters were removed
    if len(new_infobox_dict) != len(infobox_dict):
        changed = True

    if not changed:
        return text, False

    # 6) Rebuild, sort, and replace the infobox block
    rebuilt = (
        "{{Infobox vehicle\n"
        + "\n".join(f"{k}={v}" for k, v in new_infobox_dict.items())
        + "\n}}"
    )
    sorted_infobox = sort_infobox(rebuilt)
    new_text = text.replace(infobox_block, sorted_infobox, 1)

    return new_text, True
