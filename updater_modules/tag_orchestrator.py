from typing import Dict, List, Optional, Tuple
import os

from .tag.tag_articles import process_tag_article
from .tag.tag_templates import process_tag_template


def orchestrate_tag(
    text: str,
    parser_output_path: str,
    history_path: str,
    language_code: str,
    version: str,
    title: str = None,
) -> Tuple[str, List[str], bool]:
    """
    Orchestrate the tag updates.

    Args:
        text: The wiki text to process
        parser_output_path: Path to the parser output
        history_path: Path to the history files
        language_code: Language code for the page
        version: Current game version

    Returns:
        Tuple containing:
        - Updated text
        - List of processes performed
        - Boolean indicating if any changes were made
    """
    processes = []
    was_edited = False

    # Process tag article
    new_text, article_processes = process_tag_article(
        text, parser_output_path, language_code, version, title
    )
    if article_processes:
        processes.extend(article_processes)
        was_edited = True
        text = new_text

    # Process tag template
    new_text, template_processes = process_tag_template(
        text, parser_output_path, language_code, title
    )
    if template_processes:
        processes.extend(template_processes)
        was_edited = True
        text = new_text

    return text, processes, was_edited
