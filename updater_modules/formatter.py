def format_wiki_text(text: str) -> str:
    """
    Cleans up whitespace, ensures blank lines around top-level headings,
    collapses extra blank lines, and skips anything inside {{Codebox…==See also==}}
    or {{Infobox…}}.
    Returns the new text if changes were made, or the original text unchanged.
    """
    lines = text.split('\n')
    made_changes = False
    i = 0
    in_codebox_section = False

    while i < len(lines):
        line = lines[i]
        if line.startswith('{{Codebox'):
            in_codebox_section = True
        if in_codebox_section and line.startswith('==See also=='):
            in_codebox_section = False
        if in_codebox_section:
            i += 1
            continue

        original_line = lines[i]
        cleaned_line = original_line.rstrip()
        if cleaned_line != original_line:
            lines[i] = cleaned_line
            made_changes = True

        # strip blank lines after Infobox close
        if line.startswith('{{Infobox'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('}}'):
                j += 1
            if j < len(lines) and lines[j].startswith('}}'):
                k = j + 1
                while k < len(lines) and not lines[k].strip():
                    lines.pop(k)
                    made_changes = True
            i = j + 1
            continue

        # ensure blank line before == header
        if line.startswith('==') and not line.startswith('==='):
            if i > 0 and lines[i - 1].strip():
                lines.insert(i, '')
                made_changes = True
                i += 1
            # remove extra blank lines after
            if i + 1 < len(lines):
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    lines.pop(j)
                    made_changes = True
                i = j - 1

        # similar logic for === sub-headers
        if line.startswith('===') and not line.startswith('===='):
            if i > 0:
                prev = lines[i - 1].strip()
                if prev == '' or prev.startswith('=='):
                    pass  # already has blank line
                else:
                    lines.insert(i, '')
                    made_changes = True
                    i += 1

        # ensure blank line after {{Navbox…}}
        if line.startswith('{{Navbox'):
            if i + 1 < len(lines) and lines[i + 1].strip():
                lines.insert(i + 1, '')
                made_changes = True

        i += 1

    # collapse multiple blank lines
    cleaned = []
    prev_empty = False
    for line in lines:
        if not line.strip():
            if not prev_empty:
                cleaned.append(line)
            else:
                made_changes = True
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False

    return '\n'.join(cleaned) if made_changes else text 