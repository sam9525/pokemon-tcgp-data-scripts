import json
import os


def check_duplicate_cards(input_file):
    """
    Checks for duplicate card IDs across different packs in the given JSON file.
    Args:
        input_file (str): Path to the input JSON file.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {input_file}")
        return

    card_pack_map = {}

    # Iterate through the data to build a map of card_id -> list of packs
    for pack_name, types in data.items():
        for type_name, card_ids in types.items():
            for card_id in card_ids:
                if card_id not in card_pack_map:
                    card_pack_map[card_id] = set()
                card_pack_map[card_id].add(pack_name)

    # Filter for cards present in more than one pack
    duplicates = {}
    for card_id, packs in card_pack_map.items():
        if len(packs) > 1:
            duplicates[card_id] = {"boosterPack": sorted(list(packs))}

    # Sort by card_id for consistent output
    sorted_duplicates = dict(sorted(duplicates.items()))

    # File name
    file_name = os.path.basename(input_file)
    file_name = os.path.splitext(file_name)[0]

    # Output the result
    with open(f"json/{file_name}_duplicates.json", "w", encoding="utf-8") as f:
        json.dump(sorted_duplicates, f, indent=2)
