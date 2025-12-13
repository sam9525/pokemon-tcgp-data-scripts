import json
import os
from messages import log, update_pbar


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
