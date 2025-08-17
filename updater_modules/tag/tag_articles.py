import os
import re
from typing import List, Tuple, Optional


def process_tag_article(
    text: str,
    parser_output_path: str,
    language_code: str,
    version: str,
    title: str = None,
) -> Tuple[str, List[str]]:
    """
    Process tag articles by updating tables and version information.

    Args:
        text: The wiki text to process
        parser_output_path: Path to the parser output files
        language_code: Language code for the page
        version: Current game version from Base.Axe.txt

    Returns:
        Tuple containing:
        - Updated text
        - List of processes performed
    """
    processes = []

    # Update the page version template
    version_pattern = r"{{Page version\|(.*?)(?:\||}})"
    if re.search(version_pattern, text):
        text = re.sub(version_pattern, f"{{{{Page version|{version}}}}}", text)
        processes.append("Updated page version")

    # Find and replace the wikitable
    table_pattern = r"\{\| class=\"wikitable theme-blue sortable\" style=\"text-align: center;\".*?\|\}"
    table_match = re.search(table_pattern, text, re.DOTALL)

    if table_match:
        article_name = get_article_name(title) if title else None
        if not article_name:
            if title:
                print(
                    f"Error: Failed to extract article name from title '{title}' - skipping tag table update"
                )
            else:
                print(
                    f"Error: No title provided for tag processing - skipping tag table update"
                )
            return text, processes

        file_path = os.path.join(
            parser_output_path,
            language_code,
            "tags",
            "item_list",
            f"{article_name}.txt",
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                new_table = f.read().strip()
            text = text[: table_match.start()] + new_table + text[table_match.end() :]
            processes.append("Updated tag table")
        except FileNotFoundError:
            print(
                f"Error: Tag data file not found: {file_path} - skipping tag table update"
            )

    return text, processes


def get_article_name(input_text: str) -> Optional[str]:
    """
    Extract and format the article name from a page title.
    Removes '(tag)' and any whitespace, and applies URL encoding for special characters.

    Args:
        input_text: The page title to process

    Returns:
        Formatted article name or None if input is invalid
    """
    if not input_text:
        return None

    # Only process if this looks like a page title (short string without wiki markup)
    if len(input_text) > 200 or input_text.strip().startswith("{{"):
        print(f"Error: Expected page title but received wiki text for tag processing")
        return None

    article_name = input_text.strip()

    # Remove language code suffix if present (e.g., "Article/fr" -> "Article")
    if "/" in article_name:
        article_name = article_name.rsplit("/", 1)[0]

    # Clean up the article name
    # Remove "(tag)" suffix (case insensitive)
    article_name = re.sub(r"\s*\([Tt]ag\)\s*$", "", article_name)

    # Remove extra whitespace
    article_name = article_name.strip()

    if not article_name:
        print(f"Error: Could not extract valid article name from title: {input_text}")
        return None

    # Apply URL encoding for special characters (same as item/vehicle orchestrators)
    article_name = article_name.replace(" ", "_")
    article_name = article_name.replace("'", "%27")
    article_name = article_name.replace(":", "%3A")
    article_name = article_name.replace('"', "%22")
    article_name = article_name.replace(",", "%2C")
    article_name = article_name.replace("!", "%21")
    article_name = article_name.replace(";", "%3B")
    article_name = article_name.replace("&", "%26")
    article_name = article_name.replace("?", "%3F")

    return article_name
