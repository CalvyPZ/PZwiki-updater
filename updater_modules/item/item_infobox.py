import os
import re
from .file_utils import read_file_with_subfolders

# --------------------------------------------------------------------------
# Order in which infobox parameters should appear
# --------------------------------------------------------------------------
SORT_ORDER = [
    "|name",
    "|media_title",
    "|icon",
    "|icon2",
    "|icon3",
    "|icon4",
    "|icon5",
    "|icon6",
    "|icon7",
    "|icon8",
    "|icon9",
    "|icon10",
    "|icon11",
    "|icon12",
    "|icon13",
    "|icon14",
    "|icon15",
    "|icon16",
    "|icon17",
    "|icon18",
    "|icon19",
    "|icon20",
    "|model",
    "|model2",
    "|model3",
    "|model4",
    "|model5",
    "|model6",
    "|model7",
    "|model8",
    "|model9",
    "|model10",
    "|model11",
    "|model12",
    "|model13",
    "|model14",
    "|model15",
    "|model16",
    "|model17",
    "|model18",
    "|model19",
    "|model20",
    "|icon_name",
    "|icon_name2",
    "|icon_name3",
    "|icon_name4",
    "|icon_name5",
    "|icon_name6",
    "|icon_name7",
    "|icon_name8",
    "|icon_name9",
    "|icon_name10",
    "|icon_name11",
    "|icon_name12",
    "|icon_name13",
    "|icon_name14",
    "|icon_name15",
    "|icon_name16",
    "|icon_name17",
    "|icon_name18",
    "|icon_name19",
    "|icon_name20",
    "|category",
    "|weight",
    "|weight_full",
    "|weight_reduction",
    "|max_units",
    "|equipped",
    "|attachment_type",
    "|body_location",
    "|body_location2",
    "|body_location3",
    "|body_location4",
    "|body_location5",
    "|body_location6",
    "|body_location7|attachment_type",
    "|attachments_provided",
    "|function",
    "|primary_use",
    "|weapon",
    "|weapon1",
    "|weapon2",
    "|weapon3",
    "|weapon4",
    "|weapon5",
    "|weapon6",
    "|weapon7",
    "|weapon8",
    "|weapon9",
    "|weapon10",
    "|part_type",
    "|skill_type",
    "|ammo_type",
    "|clip_size",
    "|material",
    "|material_value",
    "|metal_value",
    "|burn_time",
    "|contents",
    "|can_boil_water",
    "|consumed",
    "|writable",
    "|recipes",
    "|skill_trained",
    "|page_number",
    "|vol_number",
    "|packaged",
    "|feed_type",
    "|rain_factor",
    "|days_fresh",
    "|days_rotten",
    "|cant_be_frozen",
    "|condition_max",
    "|condition_lower_chance",
    "|run_speed",
    "|stomp_power",
    "|combat_speed",
    "|scratch_defense",
    "|bite_defense",
    "|bullet_defense",
    "|neck_protection",
    "|insulation",
    "|wind_resistance",
    "|water_resistance",
    "|discomfort_mod",
    "|endurance_mod",
    "|light_distance",
    "|light_strength",
    "|torch_cone",
    "|wet_cooldown",
    "|sensor_range",
    "|energy_source",
    "|two_way",
    "|mic_range",
    "|transmit_range",
    "|min_channel",
    "|max_channel",
    "|damage_type",
    "|min_damage",
    "|max_damage",
    "|door_damage",
    "|tree_damage",
    "|sharpness",
    "|min_range",
    "|max_range",
    "|min_range_mod",
    "|max_range_mod",
    "|hit_chance",
    "|recoil_delay",
    "|sound_radius",
    "|base_speed",
    "|swing_time",
    "|push_back",
    "|knockdown",
    "|aiming_time",
    "|aiming_mod",
    "|reload_time",
    "|crit_chance",
    "|crit_multiplier",
    "|angle_mod",
    "|kill_move",
    "|weight_mod",
    "|reload_mod",
    "|aiming_change",
    "|reloading_change",
    "|effect_type",
    "|type",
    "|effect_power",
    "|effect_range",
    "|effect_duration",
    "|effect_timer",
    "|hunger_change",
    "|thirst_change",
    "|calories",
    "|carbohydrates",
    "|proteins",
    "|lipids",
    "|unhappy_change",
    "|boredom_change",
    "|carpentry_change",
    "|cooking_change",
    "|farming_change",
    "|foraging_change",
    "|first_aid_change",
    "|electrical_change",
    "|metalworking_change",
    "|mechanics_change",
    "|tailoring_change",
    "|stress_change",
    "|panic_change",
    "|fatigue_change",
    "|endurance_change",
    "|flu_change",
    "|pain_change",
    "|sick_change",
    "|alcoholic",
    "|alcohol_power",
    "|reduce_infection_power",
    "|bandage_power",
    "|poison_power",
    "|cook_minutes",
    "|burn_minutes",
    "|dangerous_uncooked",
    "|bad_microwaved",
    "|good_hot",
    "|bad_cold",
    "|spice",
    "|evolved_recipe",
    "|workstation",
    "|tool",
    "|ingredients",
    "|tag",
    "|tag2",
    "|tag3",
    "|tag4",
    "|tag5",
    "|tag6",
    "|tag7",
    "|tag8",
    "|tag9",
    "|tag10",
    "|capacity",
    "|fluid_capacity",
    "|container_name",
    "|clothing_item",
    "|itemdisplayname",
    "|recmedia",
    "|guid",
    "|guid2",
    "|guid3",
    "|guid4",
    "|guid5",
    "|guid6",
    "|guid7",
    "|guid8",
    "|guid9",
    "|guid10",
    "|guid11",
    "|guid12",
    "|guid13",
    "|guid14",
    "|guid15",
    "|guid16",
    "|guid17",
    "|guid18",
    "|guid19",
    "|guid20",
    "|item_id",
    "|item_id2",
    "|item_id3",
    "|item_id4",
    "|item_id5",
    "|item_id6",
    "|item_id7",
    "|item_id8",
    "|item_id9",
    "|item_id10",
    "|infobox_version",
]


def sort_infobox(infobox: str) -> str:
    lines = infobox.split("\n")
    body = lines[1:-1]

    def key_fn(line):
        key = line.split("=", 1)[0].strip()
        return SORT_ORDER.index(key) if key in SORT_ORDER else len(SORT_ORDER)

    sorted_body = sorted(body, key=key_fn)
    return "{{Infobox item\n" + "\n".join(sorted_body) + "\n}}"


def process_infobox(
    text, parser_output_path, language_code, item_id, article_name=None
):
    """
    Args:
        text (str): Full page wikitext
        parser_output_path (str)
        language_code (str)
        item_id (str|None)
        article_name (str|None): The name of the article, passed from the main bot system

    Returns:
        (new_text (str), changed (bool))
    """

    # 1) Extract the first {{Infobox item…}} block
    match = re.search(r"(\{\{Infobox\s*item[\s\S]*?\n\}\})", text, re.IGNORECASE)
    if not match:
        return text, False
    infobox_block = match.group(1)

    if not item_id:
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
            "item",
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

    # If article name file doesn't exist or no article name provided, use item_id
    if not file_lines:
        item_id_file_path = os.path.join(
            parser_output_path, language_code, "item", "infoboxes", f"{item_id}.txt"
        )
        file_content, found_path = read_file_with_subfolders(item_id_file_path)
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
        "|boredom_change",
        "|itemdisplayname",
        "|media_title",
        "|recipes",
        "|cooking_change",
        "|carpentry_change",
        "|farming_change",
        "|first_aid_change",
        "|electrical_change",
        "|metalworking_change",
        "|mechanics_change",
        "|tailoring_change",
        "|aiming_change",
        "|reloading_change",
        "|fishing_change",
        "|trapping_change",
        "|foraging_change",
        "|long_blunt_change",
        "|short_blade_change",
        "|lightfooted_change",
        "|unhappy_change",
        "|boredom_change",
        "|stress_change",
        "panic_change",
        "|fatigue_change",
        "|endurance_change",
        "|fitness_change",
    )
    for key, value in infobox_dict.items():
        if any(key.startswith(prefix) for prefix in protected_prefixes):
            new_infobox_dict[key] = value
        # Special handling for name parameter with VHS/Disc items
        elif (
            key.startswith("|name")
            and item_id
            and item_id.startswith(("Base.VHS_", "Base.Disc_"))
        ):
            new_infobox_dict[key] = value

    # Then add all parameters from the file_dict
    for key, value in file_dict.items():
        # Skip if it's a protected parameter
        if any(key.startswith(prefix) for prefix in protected_prefixes):
            continue
        # Skip name parameter for VHS/Disc items
        if (
            key.startswith("|name")
            and item_id
            and item_id.startswith(("Base.VHS_", "Base.Disc_"))
        ):
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
        "{{Infobox item\n"
        + "\n".join(f"{k}={v}" for k, v in new_infobox_dict.items())
        + "\n}}"
    )
    sorted_infobox = sort_infobox(rebuilt)
    new_text = text.replace(infobox_block, sorted_infobox, 1)

    return new_text, True
