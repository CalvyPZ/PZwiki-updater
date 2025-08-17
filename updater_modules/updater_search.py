#!/usr/bin/env python

import re
import asyncio
import os
import pywikibot  # type: ignore
from pywikibot import pagegenerators  # type: ignore
from tqdm import tqdm
from typing import Dict, List, Set, Tuple
import concurrent.futures
import multiprocessing
from datetime import datetime

# Search patterns for different infobox types
SEARCH_PATTERNS = {
    "item": r"\{\{Infobox\s*item",
    "tile": r"\{\{Infobox\s*tile",
    "vehicle": r"\{\{Infobox\s*vehicle(?!\s+part)",
    "vehicle_part": r"\{\{Infobox\s*vehicle\s+part",
    "fluid": r"\{\{Infobox\s*fluid",
    "modding": r"\{\{Header\|Modding\|Item\s+tags",
}

# Increase batch sizes and concurrency
BATCH_SIZE = 500
MAX_WORKERS = multiprocessing.cpu_count() * 2


def fetch_page_batch(site, titles: List[str]) -> Dict[str, str]:
    """Fetch a batch of pages using PreloadingGenerator."""
    pages = [pywikibot.Page(site, title) for title in titles]
    preloaded_gen = pagegenerators.PreloadingGenerator(pages, groupsize=len(titles))
    return {page.title(): page.text for page in preloaded_gen}


async def load_wiki_cache(site) -> Dict[str, str]:
    """Load all wiki pages into memory using concurrent processing and tqdm progress bars."""
    print("Loading wiki pages into memory...")
    all_pages = list(site.allpages(namespace=0, total=None, filterredir=False))
    all_titles = [page.title() for page in all_pages]
    total = len(all_titles)

    if total == 0:
        print("No pages found to cache")
        return {}

    # Split into batches
    batches = [all_titles[i : i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
    wiki_cache = {}
    start_ts = datetime.now()

    # Process batches concurrently with progress tracking
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {
            executor.submit(fetch_page_batch, site, batch): len(batch)
            for batch in batches
        }

        with tqdm(total=total, desc="Loading pages") as pbar:
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    batch_dict = future.result()
                    wiki_cache.update(batch_dict)
                    batch_size = future_to_batch[future]
                    pbar.update(batch_size)

                    # Calculate and display ETA
                    done = pbar.n
                    elapsed = (datetime.now() - start_ts).total_seconds() or 0.001
                    eta = int((total - done) * (elapsed / done))
                    pbar.set_postfix(eta=f"{eta}s")
                except Exception as e:
                    print(f"Error loading batch: {e}")

    print(f"Loaded {len(wiki_cache)} pages into memory")
    return wiki_cache


def categorize_page(text: str) -> Set[str]:
    """Categorize a page based on its content."""
    categories = set()

    # Check each pattern
    for category, pattern in SEARCH_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            categories.add(category)

    return categories


def process_batch(batch: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Process a batch of pages using multiple threads."""
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Create a list of futures for parallel processing
        futures = []
        for title, text in batch:
            future = executor.submit(categorize_page, text)
            futures.append((title, future))

        # Process results as they complete
        for title, future in futures:
            categories = future.result()
            for category in categories:
                if category not in results:
                    results[category] = []
                results[category].append(title)

    return results


def scan_template_files(
    site: pywikibot.Site, parser_output_path: str, language_code: str
) -> List[str]:
    """
    Scan template files and return list of template page titles that need updating.

    Args:
        site: Pywikibot site object
        parser_output_path: Path to the parser output files
        language_code: Language code for the page

    Returns:
        List of template page titles that need updating
    """
    template_titles = []

    # Construct the path to the templates folder
    templates_folder = os.path.join(
        parser_output_path, language_code, "tags", "articles", "templates"
    )

    if not os.path.exists(templates_folder):
        print(f"Templates folder not found: {templates_folder}")
        return template_titles

    # Get all .txt files in the templates folder
    try:
        template_files = [f for f in os.listdir(templates_folder) if f.endswith(".txt")]
    except Exception as e:
        print(f"Error reading templates folder {templates_folder}: {e}")
        return template_titles

    for template_file in template_files:
        # Extract template name (remove .txt extension)
        template_name = template_file[:-4]  # Remove .txt
        page_title = f"Template:Tag_{template_name}"
        file_path = os.path.join(templates_folder, template_file)

        try:
            # Read the template file content
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Get the wiki page
            page = pywikibot.Page(site, page_title)

            # Check if page content differs from file content
            if page.exists():
                if page.text.strip() == file_content.strip():
                    # Content matches, skip this page
                    continue

            # Content differs or page doesn't exist, add to list
            template_titles.append(page_title)

        except Exception as e:
            print(f"Error processing template file {file_path}: {e}")
            continue

    return template_titles


async def process_pages(
    wiki_cache: Dict[str, str],
    parser_output_path: str = None,
    language_code: str = "en",
    site: pywikibot.Site = None,
) -> Dict[str, List[str]]:
    """Process all pages and categorize them using multiple threads with progress bar."""
    print("Categorizing pages...")

    # Initialize category lists
    categorized_pages = {
        "item": [],
        "tile": [],
        "vehicle": [],
        "vehicle_part": [],
        "fluid": [],
        "modding": [],
        "tag": [],
    }

    # Split into larger batches for parallel processing
    items = list(wiki_cache.items())
    batches = [items[i : i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]

    # Process batches concurrently using ThreadPoolExecutor with progress bar
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all batch processing tasks
        future_to_batch = {
            executor.submit(process_batch, batch): batch for batch in batches
        }

        # Process results as they complete with progress bar
        with tqdm(total=len(batches), desc="Processing batches") as pbar:
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    batch_result = future.result()
                    for category, titles in batch_result.items():
                        categorized_pages[category].extend(titles)
                    pbar.update(1)
                except Exception as e:
                    print(f"Error processing batch: {e}")

    # Scan template files and add to tag category (if parser_output_path provided)
    if parser_output_path and site:
        print("Scanning tag template files...")
        template_titles = scan_template_files(site, parser_output_path, language_code)
        categorized_pages["tag"].extend(template_titles)
        print(f"Found {len(template_titles)} tag templates to update")

    # Sort each category list alphabetically
    for category in categorized_pages:
        categorized_pages[category].sort()

    return categorized_pages


async def search_wiki(
    site,
    language_pages=None,
    cpu_threads=None,
    parser_output_path=None,
    language_code="en",
) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Main function to search and categorize wiki pages.

    Args:
        site: The wiki site to search
        language_pages: If True or None, process all pages. If False, exclude pages with language codes.
                      If a list, only process those specific pages.
        cpu_threads: Optional number of CPU threads to use for processing
        parser_output_path: Path to parser output files for template scanning
        language_code: Language code for template scanning
    """
    global MAX_WORKERS
    if cpu_threads is not None:
        MAX_WORKERS = cpu_threads

    # Load all pages into memory
    wiki_cache = await load_wiki_cache(site)

    # Handle language pages filtering
    if isinstance(language_pages, list):
        # If language_pages is a list, only include those specific pages
        wiki_cache = {
            title: content
            for title, content in wiki_cache.items()
            if title in language_pages
        }
    elif language_pages is False:
        # If language_pages is False, exclude pages with language codes
        wiki_cache = {
            title: content
            for title, content in wiki_cache.items()
            if "/" not in title or title.startswith("User:")
        }

    # Process and categorize pages
    categorized_pages = await process_pages(
        wiki_cache, parser_output_path, language_code, site
    )

    return categorized_pages, wiki_cache  # Return both categorized pages and wiki cache


def get_ordered_page_list(categorized_pages: Dict[str, List[str]]) -> List[str]:
    """Get an ordered list of pages based on category priority."""
    # Define the order of categories
    category_order = ["item", "tile", "vehicle", "vehicle_part", "fluid", "modding"]

    # Combine lists in order
    ordered_list = []
    for category in category_order:
        if category in categorized_pages:
            ordered_list.extend(categorized_pages[category])

    return ordered_list
