import os


def find_file_with_subfolders(base_file_path):
    """
    Find a file by checking the base path and potential /id and /page subfolders.

    Args:
        base_file_path (str): The original file path to check

    Returns:
        str: The first valid file path found, or the original path if none exist
    """
    # First, try the original path
    if os.path.exists(base_file_path):
        return base_file_path

    # Extract directory and filename
    directory = os.path.dirname(base_file_path)
    filename = os.path.basename(base_file_path)

    # Check for /id subfolder
    id_path = os.path.join(directory, "id", filename)
    if os.path.exists(id_path):
        return id_path

    # Check for /page subfolder
    page_path = os.path.join(directory, "page", filename)
    if os.path.exists(page_path):
        return page_path

    # Return original path if nothing found (for error handling by calling code)
    return base_file_path


def read_file_with_subfolders(base_file_path, encoding="utf-8"):
    """
    Read a file by checking the base path and potential /id and /page subfolders.

    Args:
        base_file_path (str): The original file path to check
        encoding (str): File encoding, defaults to 'utf-8'

    Returns:
        tuple: (file_content, found_path) or (None, None) if file not found
    """
    found_path = find_file_with_subfolders(base_file_path)

    try:
        with open(found_path, "r", encoding=encoding) as f:
            return f.read(), found_path
    except FileNotFoundError:
        return None, None
