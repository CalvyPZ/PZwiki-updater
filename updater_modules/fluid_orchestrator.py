from scripts.userscripts.updater_modules.fluid.fluid_infobox import update_fluid_infobox # type: ignore
from scripts.userscripts.updater_modules.fluid.fluid_navbox import update_fluid_navbox # type: ignore

def orchestrate_fluid(text, parser_output_path, history_path, language_code):
    """Orchestrate the updating of fluid pages."""
    processes = []
    original_text = text
    
    # Update infobox
    try:
        text, infobox_processes, infobox_edited = update_fluid_infobox(text, parser_output_path, history_path, language_code)
        if infobox_edited:
            processes.extend(infobox_processes)
    except (FileNotFoundError, OSError):
        pass
    
    # Update navbox
    try:
        text, navbox_processes, navbox_edited = update_fluid_navbox(text, parser_output_path, history_path, language_code)
        if navbox_edited:
            processes.extend(navbox_processes)
    except (FileNotFoundError, OSError):
        pass
    
    # Check if any changes were made
    was_edited = text != original_text
    
    return text, processes, was_edited
