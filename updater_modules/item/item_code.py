import os
import re
from .file_utils import read_file_with_subfolders


def process_code(text, parser_output_path):
    updated = False
    # match entire {{CodeSnip block
    pattern = re.compile(r"(?m)^\s*{{CodeSnip[\s\S]*?^\}\}\s*$", re.MULTILINE)

    for match in re.finditer(pattern, text):
        snippet = match.group(0)

        # find the |code= parameter value
        m_code = re.search(r"\|\s*code\s*=\s*\n(.*?)\n", snippet, re.DOTALL)

        raw_name = m_code.group(1).strip()

        item_name = raw_name[5:] if raw_name.startswith("Base.") else raw_name
        item_name = raw_name[5:] if raw_name.startswith("item ") else raw_name

        # sanitize filename
        sanitized = re.sub(r"[^A-Za-z0-9_.-]", "_", item_name)

        file_path = os.path.join(
            parser_output_path, "en", "item", "codesnips", f"{sanitized}.txt"
        )

        file_content, found_path = read_file_with_subfolders(file_path)
        if file_content:
            new_snippet = file_content
            if new_snippet != snippet:
                text = text.replace(snippet, new_snippet)
                updated = True

    return text, updated
