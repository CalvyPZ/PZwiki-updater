import os
import re
from typing import List, Tuple, Dict, Optional
import pywikibot


def scan_and_update_templates(
    site: pywikibot.Site, parser_output_path: str, language_code: str
) -> List[Dict]:
    """
    Scan template files and create update queue for corresponding wiki pages.

    For each .txt file in {parser_output_path}/{language_code}/tags/articles/templates/,
    check the corresponding Template:Tag_{filename} page and queue for update if different.

    Args:
        site: Pywikibot site object
        parser_output_path: Path to the parser output files
        language_code: Language code for the page

    Returns:
        List of dictionaries with update information
    """
    update_queue = []

    # Construct the path to the templates folder
    templates_folder = os.path.join(
        parser_output_path, language_code, "tags", "articles", "templates"
    )

    if not os.path.exists(templates_folder):
        print(f"Templates folder not found: {templates_folder}")
        return update_queue

    # Get all .txt files in the templates folder
    try:
        template_files = [f for f in os.listdir(templates_folder) if f.endswith(".txt")]
    except Exception as e:
        print(f"Error reading templates folder {templates_folder}: {e}")
        return update_queue

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

            # Content differs or page doesn't exist, add to update queue
            update_queue.append(
                {
                    "title": page_title,
                    "page": page,
                    "new_text": file_content,
                    "processes": ["Updated tag template"],
                }
            )

        except Exception as e:
            print(f"Error processing template file {file_path}: {e}")
            continue

    return update_queue


def process_tag_template(
    text: str, parser_output_path: str, language_code: str, title: str = None
) -> Tuple[str, List[str]]:
    """
    Legacy function for individual template processing.
    This is now mainly used as a fallback for individual page processing.
    The main template processing should use scan_and_update_templates().

    Args:
        text: The wiki text to process
        parser_output_path: Path to the parser output files
        language_code: Language code for the page
        title: The page title being processed

    Returns:
        Tuple containing:
        - Updated text
        - List of processes performed
    """
    processes = []

    # Only process if this is a Template:Tag_ page
    if not title or not title.startswith("Template:Tag_"):
        return text, processes

    # Extract the template name from the title (remove "Template:Tag_" prefix)
    template_name = title[len("Template:Tag_") :]

    # Construct the path to the template file
    template_file_path = os.path.join(
        parser_output_path,
        language_code,
        "tags",
        "articles",
        "templates",
        f"{template_name}.txt",
    )

    try:
        with open(template_file_path, "r", encoding="utf-8") as f:
            new_content = f.read()

        # Check if content is different
        if new_content.strip() != text.strip():
            processes.append("Updated tag template")
            return new_content, processes
        else:
            return text, processes

    except FileNotFoundError:
        print(
            f"Error: Template file not found: {template_file_path} - skipping template update"
        )
        return text, processes
    except Exception as e:
        print(
            f"Error: Failed to read template file {template_file_path}: {e} - skipping template update"
        )
        return text, processes
