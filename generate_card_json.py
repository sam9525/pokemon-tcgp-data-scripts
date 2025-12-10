import pandas as pd
import os
import glob
import json
import cv2
import numpy as np
import argparse
from check_duplicate_cards import check_duplicate_cards
from load_match_icon import load_icons, match_icon


def get_image_type(image_path, icons):
    """
    Get image type from image path.
    By match the specific position (top right) in the image with the icons.
    Using cv2.matchTemplate to match the icons.
    Args:
        image_path (str): Path to image.
        icons (dict): Dictionary of icons.
    """
    try:
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return "unknown"

        height, width = img.shape[:2]

        # Crop top right
        left = int(width * 0.88)
        top = int(height * 0.03)
        right = int(width * 0.95)
        bottom = int(height * 0.09)

        crop = img[top:bottom, left:right]

        best_type = match_icon(crop, icons, threshold=0.5)

        if best_type:
            return best_type
        else:
            return "unknown"

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return "unknown"


def generate_json(folder_path, excel_paths):
    """
    Generate card JSON.
    Args:
        folder_path (str): Path to folder.
        excel_paths (list): List of Excel file paths.
        output_path (str): Output file path.
    """

    # Load Excel files, and use files name as pack name
    EXCEL_FILES = {}
    for path in excel_paths:
        filename = os.path.basename(path)
        if "_" in filename:
            pack_name = os.path.splitext(filename.split("_")[1])[0]
        else:
            pack_name = os.path.splitext(filename)[0]
        EXCEL_FILES[pack_name] = path

    print("Loading icons...")
    icons = load_icons()
    print(f"Loaded {len(icons)} icons.")

    print("Loading Excel files...")
    pack_data = {}
    for pack_name, path in EXCEL_FILES.items():
        try:
            df = pd.read_excel(path, usecols=["Image Name"])
            # Extract IDs from Excel: cPK_10_008570_00 -> 008570
            ids = set()
            for name in df["Image Name"].astype(str).str.strip():
                try:
                    parts = name.split("_")
                    if len(parts) > 3:
                        if parts[3] == "02":
                            continue
                        ids.add(parts[2])
                except Exception:
                    continue
            pack_data[pack_name] = ids
            print(f"Loaded {len(pack_data[pack_name])} items for {pack_name}")
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return

    print("Scanning images...")
    image_files = glob.glob(os.path.join(folder_path, "*.png"))

    # Create result array with pack name as key
    result = {pack_name: {} for pack_name in EXCEL_FILES.keys()}

    # Initialize type lists
    types = [
        "grass",
        "fire",
        "water",
        "lightning",
        "psychic",
        "fighting",
        "darkness",
        "metal",
        "colorless",
        "dragon",
    ]
    for p in result:
        for t in types:
            result[p][t] = []

    count = 0
    for img_path in image_files:
        filename = os.path.basename(img_path)

        # Extract ID: PK_10_005820_00.png -> 005820
        try:
            parts = filename.split("_")
            card_id = parts[2]
        except IndexError:
            print(f"Skipping malformed filename: {filename}")
            continue

        # Match to pack
        clean_name = os.path.splitext(filename)[0]

        # Loop through each pack
        for pack_name in EXCEL_FILES.keys():
            pack = None
            # Match by ID
            if card_id in pack_data[pack_name]:
                pack = pack_name

            if pack:
                # Get image type
                card_type = get_image_type(img_path, icons)
                if card_type in result[pack]:
                    # If card_id is not exist in the same pack
                    # Add card ID to type list
                    if card_id not in result[pack][card_type]:
                        result[pack][card_type].append(card_id)

                count += 1
                if count % 10 == 0:
                    print(f"Processed {count} cards...", end="\r")
            else:
                pass

    print(f"\nProcessing complete. Processed {count} cards.")

    # Sort lists
    for p in result:
        for t in result[p]:
            result[p][t].sort()

    # Remove empty types
    final_result = {}
    for p in result:
        final_result[p] = {k: v for k, v in result[p].items() if v}

    return final_result


def main():
    parser = argparse.ArgumentParser(description="Generate card JSON from images.")
    parser.add_argument("--image-folder", help="Path to image folder", required=True)
    parser.add_argument(
        "--excel-files", nargs="+", help="Path to Excel files", required=True
    )
    parser.add_argument("--output-name", help="Output JSON file", required=True)

    args = parser.parse_args()

    final_result = generate_json(args.image_folder, args.excel_files)

    OUTPUT_FILE = f"json/{args.output_name}.json"

    print(f"Writing to {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2)

    # Check duplicates
    print("Generating json file for duplicates...")
    duplicate_list = check_duplicate_cards(OUTPUT_FILE)

    # File name
    file_name = os.path.basename(OUTPUT_FILE)
    file_name = os.path.splitext(file_name)[0]

    # Output the result
    with open(f"json/{file_name}_duplicates.json", "w", encoding="utf-8") as f:
        json.dump(duplicate_list, f, indent=2)

    print("Done.")


if __name__ == "__main__":
    main()
