#!/usr/bin/env python

import os
import time
import pywikibot # type: ignore
from typing import Dict, List, Tuple
from tqdm import tqdm

def orchestrate_loot(site: pywikibot.Site, parser_output_path: str, rate_limit: int) -> None:
    """
    Updates the Module:Loot pages with lua files from the distributions/data_files directory.
    
    Args:
        site (pywikibot.Site): The wiki site to update
        parser_output_path (str): Path to parser output directory
        rate_limit (int): Number of seconds to wait between saves
    """
    data_files_path = os.path.join(parser_output_path, 'en', 'item', "distributions", "data_files")
    
    # First process the index file
    index_file_path = os.path.join(data_files_path, "index.lua")
    if os.path.exists(index_file_path):
        with open(index_file_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
            
        index_page = pywikibot.Page(site, "Module:Loot/index")
        if index_page.text != index_content:
            index_page.text = index_content
            index_page.save(summary="Automated updating: Update Loot index module", tags="bot")
    
    # Then process all other lua files
    lua_files = [f for f in os.listdir(data_files_path) if f.endswith('.lua') and f != 'index.lua']
    
    for filename in tqdm(lua_files, desc="Updating loot modules"):
        file_path = os.path.join(data_files_path, filename)
        module_name = filename[:-4]  # Remove .lua extension
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        page = pywikibot.Page(site, f"Module:Loot/{module_name}")
        if page.text != file_content:
            page.text = file_content
            page.save(summary=f"Automated updating: Update Loot {module_name} module", tags="bot")