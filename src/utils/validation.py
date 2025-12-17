import os


def extract_folder_prefix(folder_path: str) -> str:
    """
    Extracts the prefix from the parent folder name.
    Assumes the parent folder name is in the format "Prefix - Description" or just "Prefix".
    Args:
        folder_path (str): The full path to the folder.
    Returns:
        str: The extracted prefix.
    """
    parent_name = os.path.basename(os.path.dirname(folder_path))
    # Split by " - " and take the first part
    return os.path.splitext(parent_name)[0].split(" - ")[0]


def extract_excel_prefix(file_path: str, separator: str = None) -> str:
    """
    Extracts the prefix from the excel file name.
    Args:
        file_path (str): The full path to the excel file.
        separator (str, optional): The separator to split the filename.
    Returns:
        str: The extracted prefix.
    """
    filename = os.path.basename(file_path)
    stem = os.path.splitext(filename)[0]

    if separator:
        return stem.split(separator)[0]
    return stem
