import json
import os
from src.utils import log, update_pbar
import pandas as pd


def check_duplicate_cards(input_file, pbar=None):
    """
    Checks for duplicate card IDs across different packs in the given JSON file.
    Args:
        input_file (str): Path to the input JSON file.
        pbar (QProgressBar): Progress bar.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        log(f"Error: File not found: {input_file}", pbar)
        return
    except json.JSONDecodeError:
        log(f"Error: Invalid JSON format in file: {input_file}", pbar)
        return

    update_pbar(5, pbar)

    card_pack_map = {}

    total_items = len(data.items())

    # Iterate through the data to build a map of card_id -> list of packs
    for pack_name, types in data.items():
        for type_name, card_ids in types.items():
            for card_id in card_ids:
                if card_id not in card_pack_map:
                    card_pack_map[card_id] = set()
                card_pack_map[card_id].add(pack_name)

        update_pbar(20 / total_items, pbar)

    # Filter for cards present in more than one pack
    duplicates = {}
    for card_id, packs in card_pack_map.items():
        if len(packs) > 1:
            duplicates[card_id] = {"boosterPack": sorted(list(packs))}

    update_pbar(5, pbar)

    # Sort by card_id for consistent output
    sorted_duplicates = dict(sorted(duplicates.items()))

    return sorted_duplicates


def check_duplicate_specific_card(image_path, excel_files, pbar=None):
    """
    Checks which Excel files (packs) contain a specific card identified by image_path.

    Args:
        image_path (str): Path to the image file, from which the card name is extracted.
        excel_files (dict): A dictionary where keys are pack names (str) and values are
        pbar: Progress bar for UI updates.

    Returns:
        target_card_name (str): The name of the card being checked.
        found_in_packs (set): A set of pack names (strings) where the specified card was found.
            Returns an empty set if the card name cannot be extracted or no packs are found.
    """
    filename = os.path.basename(image_path)
    parts = filename.split("_")
    if len(parts) <= 4:
        log(f"Error: Could not extract card name from image path: {image_path}", pbar)
        return set()
    target_card_name = parts[4]

    found_in_packs = set()

    for pack_name, path in excel_files.items():
        df = pd.read_excel(path, usecols=["Image Name"])

        # Extract card names from image names
        card_names_in_pack = (
            df["Image Name"]
            .astype(str)
            .apply(
                lambda name: (name.split("_")[4] if len(name.split("_")) > 4 else None)
            )
            .dropna()
        )

        if target_card_name in card_names_in_pack.values:
            found_in_packs.add(pack_name)

    return target_card_name, list(found_in_packs)
