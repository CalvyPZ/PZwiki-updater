#!/usr/bin/env python

import re
from scripts.userscripts.updater_modules.vehicle.vehicle_infobox import process_infobox  # type: ignore


def orchestrate_vehicle(
    text, parser_output_path, history_path, language_code, article_name=None
):
    """
    Args:
        text (str): Original wikitext.
        parser_output_path (str)
        history_path (str)
        language_code (str)
        article_name (str|None): The name of the article, passed from the main bot system
    Returns:
        (updated_text (str), processes (list[str]))
    """
    # 1) Extract the Infobox vehicle block
    m = re.search(r"\{\{Infobox\s*vehicle(.*?)\}\}", text, re.DOTALL | re.IGNORECASE)
    if m:
        infobox_body = m.group(1)
        id_match = re.search(r"\|\s*vehicle_id\s*=\s*([^\|\n]+)", infobox_body)
        vehicle_id = id_match.group(1).strip() if id_match else None
    else:
        vehicle_id = None

    updated = text
    processes = []

    # 2) Run through each processor
    try:
        new_text, changed = process_infobox(
            updated, parser_output_path, language_code, vehicle_id, article_name
        )
        if changed:
            updated = new_text
            processes.append("Infobox")
    except (FileNotFoundError, OSError):
        pass

    return updated, processes
