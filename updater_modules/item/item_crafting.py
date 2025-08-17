import os
import re
from typing import Tuple
from .file_utils import read_file_with_subfolders


def process_evolved_recipes(
    page_text: str, crafting_output_dir: str, item_id: str
) -> Tuple[str, bool]:
    """
    Process evolved recipes template in the page text.

    Args:
        page_text: The text content of the page
        crafting_output_dir: Base directory for crafting recipe files
        item_id: The ID of the item being processed (used as fallback)

    Returns:
        Tuple containing:
        - Updated page text
        - Boolean flag indicating if any changes were made
    """
    # Find evolved recipes template with proper nesting handling
    template_pattern = r"\{\{EvolvedRecipesForItem(?:[^{}]|(?:\{\{[^{}]*\}\}))*\}\}"
    template_match = re.search(template_pattern, page_text, re.DOTALL)

    if not template_match:
        return page_text, False

    template = template_match.group(0)
    template_start = template_match.start()

    # Try to find ID parameter in template
    id_match = re.search(r"\|id=([^\n|]+)", template)
    recipe_id = id_match.group(1).strip() if id_match else item_id

    # Construct the evolved recipes file path
    recipe_path = os.path.join(
        crafting_output_dir, "evolved_recipes", f"{recipe_id}.txt"
    )

    # Check if recipe file exists and replace template
    try:
        recipe_content, found_path = read_file_with_subfolders(recipe_path)
        if recipe_content:
            recipe_content = recipe_content.strip()
            # Replace the template with the recipe content
            updated_text = (
                page_text[:template_start]
                + recipe_content
                + page_text[template_start + len(template) :]
            )
            return updated_text, True
    except (OSError, IOError):
        pass

    return page_text, False


def process_crafting_templates(
    page_text: str, crafting_output_dir: str, item_id: str = None
) -> Tuple[str, bool]:
    """
    Process all crafting and building templates in the page text.

    Args:
        page_text: The text content of the page
        crafting_output_dir: Base directory for crafting recipe files
        item_id: Optional item ID for evolved recipes processing

    Returns:
        Tuple containing:
        - Updated page text
        - Boolean flag indicating if any changes were made
    """
    # First process evolved recipes if we have an item_id
    if item_id:
        page_text, evolved_changes = process_evolved_recipes(
            page_text, crafting_output_dir, item_id
        )
    else:
        evolved_changes = False

    # Find all crafting and building templates with proper nesting handling
    template_pattern = (
        r"\{\{(?:Crafting|Building)/sandbox(?:[^{}]|(?:\{\{[^{}]*\}\}))*\}\}"
    )
    templates = list(re.finditer(template_pattern, page_text, re.DOTALL))

    changes_made = False
    updated_text = page_text

    # Process templates in reverse order to maintain correct positions
    for template_match in reversed(templates):
        template = template_match.group(0)
        template_start = template_match.start()

        # Find the item ID
        item_match = re.search(r"\|item=([^\n|]+)", template)
        if not item_match:
            continue

        item_id = item_match.group(1).strip()

        # Determine if it's a crafting or building template
        is_crafting = "{{Crafting" in template
        recipe_type = "crafting" if is_crafting else "building"

        # Construct the recipe file path
        recipe_path = os.path.join(
            crafting_output_dir, "recipes", recipe_type, f"{item_id}.txt"
        )

        # Check if recipe file exists and replace template
        try:
            recipe_content, found_path = read_file_with_subfolders(recipe_path)
            if recipe_content:
                recipe_content = recipe_content.strip()
                # Replace the template with the recipe content
                updated_text = (
                    updated_text[:template_start]
                    + recipe_content
                    + updated_text[template_start + len(template) :]
                )
                changes_made = True
        except (OSError, IOError):
            continue

    return updated_text, (changes_made or evolved_changes)
