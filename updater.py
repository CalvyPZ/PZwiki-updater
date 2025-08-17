#!/usr/bin/env python

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

import os, time
import pywikibot  # type: ignore
from tqdm import tqdm
import asyncio
from typing import Dict, List, Optional


from scripts.userscripts.updater_modules.item_orchestrator import orchestrate_item  # type: ignore
from scripts.userscripts.updater_modules.tile_orchestrator import orchestrate_tile  # type: ignore
from scripts.userscripts.updater_modules.fluid_orchestrator import orchestrate_fluid  # type: ignore
from scripts.userscripts.updater_modules.vehicle_orchestrator import orchestrate_vehicle  # type: ignore
from scripts.userscripts.updater_modules.tag_orchestrator import orchestrate_tag  # type: ignore

from scripts.userscripts.updater_modules.formatter import format_wiki_text  # type: ignore
from scripts.userscripts.updater_modules.loot_orchestrator import orchestrate_loot  # type: ignore
from updater_modules.updater_search import search_wiki, process_pages  # type: ignore

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------

cpu_threads = 8
rate_limit = 0

default_language = "en"
language_pages = False  # Set to False to exclude pages with language codes

parser_output_path = os.path.join(
    os.sep, "mnt", "data", "wiki", "pz-wiki_parser", "output"
)
history_path = os.path.join(os.sep, "mnt", "data", "wiki", "history", "txt")

test_mode = False
test_page = "User:Calvy/sandbox"

# ----------------------------------------------------------------------
# Orchestrator Options
# ----------------------------------------------------------------------

enable_loot_orchestrator = False
enable_item_orchestrator = False
enable_tile_orchestrator = False
enable_fluid_orchestrator = False
enable_vehicle_orchestrator = False
enable_tag_orchestrator = True
enable_text_formatter = False

# ----------------------------------------------------------------------
# Processing
# ----------------------------------------------------------------------

# Get version
version_file_path = os.path.join(
    parser_output_path, "en", "item", "infoboxes", "Base.Axe.txt"
)
try:
    with open(version_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("|infobox_version="):
                current_version = line.split("=", 1)[1].strip()
                break
except FileNotFoundError:
    current_version = "Unknown"


def process_page_by_category(title: str, text: str, category: str) -> Optional[Dict]:
    """Process a page based on its category."""
    # Language code
    if title.startswith("User:") or "/" not in title:
        language_code = default_language
    else:
        language_code = title.rsplit("/", 1)[1]

    # Orchestrators
    if category == "item" and enable_item_orchestrator:
        new_text, processes = orchestrate_item(
            text, parser_output_path, history_path, language_code, title
        )
    elif category == "vehicle" and enable_vehicle_orchestrator:
        new_text, processes = orchestrate_vehicle(
            text, parser_output_path, history_path, language_code, title
        )
    elif category == "tile" and enable_tile_orchestrator:
        new_text, processes = orchestrate_tile(
            text, parser_output_path, history_path, language_code
        )
    elif category == "fluid" and enable_fluid_orchestrator:
        new_text, processes, was_edited = orchestrate_fluid(
            text, parser_output_path, history_path, language_code
        )
        if not was_edited:
            return None
    elif category == "tag" and enable_tag_orchestrator:
        new_text, processes, was_edited = orchestrate_tag(
            text,
            parser_output_path,
            history_path,
            language_code,
            current_version,
            title,
        )
        if not was_edited:
            return None
    else:
        return None

    # Formatter
    if enable_text_formatter:
        formatted_text = format_wiki_text(new_text)
        if formatted_text != text:
            if "Format wiki text" not in processes:
                processes.append("Format wiki text")
            return {"title": title, "new_text": formatted_text, "processes": processes}
    elif new_text != text:
        return {"title": title, "new_text": new_text, "processes": processes}

    return None


async def process_category(
    site: pywikibot.Site, titles: List[str], category: str, wiki_cache: Dict[str, str]
) -> List[Dict]:
    """Process all pages in a category using the wiki cache."""
    # Process pages using the cache
    update_queue = []
    with tqdm(total=len(titles), desc=f"Processing {category} pages") as pbar:
        for title in titles:
            # For template pages, we need to fetch them separately since they're not in the main cache
            if category == "tag" and title.startswith("Template:Tag_"):
                try:
                    page = pywikibot.Page(site, title)
                    text = page.text if page.exists() else ""
                    result = process_page_by_category(title, text, category)
                    if result:
                        result["page"] = page
                        update_queue.append(result)
                except Exception as e:
                    print(f"Error processing template page {title}: {e}")
            elif title in wiki_cache:
                result = process_page_by_category(title, wiki_cache[title], category)
                if result:
                    # Create page object only for pages that need updating
                    page = pywikibot.Page(site, title)
                    result["page"] = page
                    update_queue.append(result)
            pbar.update(1)

    return update_queue


async def main(site):
    if test_mode:
        # Create a single-item wiki cache for the sandbox
        sandbox_page = pywikibot.Page(site, test_page)
        wiki_cache = {sandbox_page.title(): sandbox_page.text}

        # Use the search module to categorize the sandbox page
        categorized_pages = await process_pages(
            wiki_cache, None, default_language, site
        )
    else:
        # Search and categorize pages
        categorized_pages, wiki_cache = await search_wiki(
            site, language_pages, cpu_threads, parser_output_path, default_language
        )

    # First update loot modules if enabled
    if enable_loot_orchestrator:
        orchestrate_loot(site, parser_output_path, rate_limit)

    # Process categories
    all_update_queues = []
    for category, titles in categorized_pages.items():
        if titles:
            update_queue = await process_category(site, titles, category, wiki_cache)
            all_update_queues.extend(update_queue)

    # Save sequentially
    for entry in tqdm(all_update_queues, desc="Saving pages"):
        entry["page"].text = entry["new_text"]
        summary = f"Automated updating: {', '.join(entry['processes'])}"
        entry["page"].save(summary=summary, tags="bot")
        time.sleep(rate_limit)


if __name__ == "__main__":
    site = pywikibot.Site()
    site.login()
    asyncio.run(main(site))
