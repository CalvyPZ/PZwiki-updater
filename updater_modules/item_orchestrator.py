#!/usr/bin/env python

import re, os
from scripts.userscripts.updater_modules.item.item_infobox   import process_infobox # type: ignore
from scripts.userscripts.updater_modules.item.item_body_part import process_body_parts # type: ignore
from scripts.userscripts.updater_modules.item.item_consumables import process_consumables # type: ignore
from scripts.userscripts.updater_modules.item.item_fixing import process_fixing # type: ignore
from scripts.userscripts.updater_modules.item.item_condition import process_condition # type: ignore
from scripts.userscripts.updater_modules.item.item_teached_recipes import process_teached_recipes # type: ignore
from scripts.userscripts.updater_modules.item.item_contents import process_contents # type: ignore
from scripts.userscripts.updater_modules.item.item_crafting  import process_crafting_templates # type: ignore
from scripts.userscripts.updater_modules.item.item_history   import process_history # type: ignore
from scripts.userscripts.updater_modules.item.item_code      import process_code # type: ignore
from scripts.userscripts.updater_modules.item.item_navbox    import process_navbox # type: ignore

def orchestrate_item(text, parser_output_path, history_path, language_code, article_name=None):
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
    # 1) Extract the Infobox item block
    m = re.search(r'\{\{Infobox\s*item(.*?)\}\}', text, re.DOTALL | re.IGNORECASE)
    if m:
        infobox_body = m.group(1)
        id_match = re.search(r'\|\s*item_id\s*=\s*([^\|\n]+)', infobox_body)
        item_id = id_match.group(1).strip() if id_match else None
    else:
        item_id = None

    updated = text
    processes = []

    # 2) Run through each processor
    try:
        new_text, changed = process_infobox(updated, parser_output_path, language_code, item_id, article_name)
        if changed:
            updated = new_text
            processes.append('Infobox')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_body_parts(updated, parser_output_path, language_code)
        if changed:
            updated = new_text
            processes.append('Body Parts')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_consumables(updated, parser_output_path, language_code, item_id)
        if changed:
            updated = new_text
            processes.append('Consumables')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_fixing(updated, parser_output_path, language_code)
        if changed:
            updated = new_text
            processes.append('Fixing')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_condition(updated, parser_output_path, language_code, item_id)
        if changed:
            updated = new_text
            processes.append('Condition')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_teached_recipes(updated, parser_output_path, language_code, item_id)
        if changed:
            updated = new_text
            processes.append('Teached Recipes')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_contents(updated, parser_output_path, language_code, item_id)
        if changed:
            updated = new_text
            processes.append('Container Contents')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_crafting_templates(updated, parser_output_path, item_id)
        if changed:
            updated = new_text
            processes.append('Crafting')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_history(updated, history_path)
        if changed:
            updated = new_text
            processes.append('History')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_code(updated, parser_output_path)
        if changed:
            updated = new_text
            processes.append('Code')
    except (FileNotFoundError, OSError):
        pass

    try:
        new_text, changed = process_navbox(updated)
        if changed:
            updated = new_text
            processes.append('Navbox')
    except (FileNotFoundError, OSError):
        pass

    return updated, processes
