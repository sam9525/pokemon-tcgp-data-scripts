import pandas as pd
import os
import glob
import json
import cv2
import numpy as np
import argparse
from check_duplicate_cards import check_duplicate_cards


def load_icons():
    """
    Load icons from type-icons folder.
    """
    icons = {}
    for icon_path in glob.glob(os.path.join("type-icons", "*.png")):
        name = os.path.splitext(os.path.basename(icon_path))[0]
        img = cv2.imread(icon_path, cv2.IMREAD_COLOR)
        if img is not None:
            icons[name] = img
    return icons


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
        img = cv2.imread(image_path)
        if img is None:
            return "unknown"

        height, width = img.shape[:2]

        # Crop top right
        left = int(width * 0.88)
        top = int(height * 0.03)
        right = int(width * 0.95)
        bottom = int(height * 0.09)

        crop = img[top:bottom, left:right]

        best_score = -1
        best_type = "unknown"

        # Search scales around 0.25
        scales = np.linspace(0.25, 0.35, 5)

        for scale in scales:
            # Try to match each icon and the best one will be returned
            for name, icon in icons.items():
                # Resize icon
                new_width = int(icon.shape[1] * scale)
                new_height = int(icon.shape[0] * scale)
                resized_icon = cv2.resize(
                    icon, (new_width, new_height), interpolation=cv2.INTER_AREA
                )

                if (
                    resized_icon.shape[0] > crop.shape[0]
                    or resized_icon.shape[1] > crop.shape[1]
                ):
                    continue

                res = cv2.matchTemplate(crop, resized_icon, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                if max_val > best_score:
                    best_score = max_val
                    best_type = name

        # Threshold check
        # If the best score is larger than 0.6
        # Means the icon is matched well enough
        if best_score > 0.6:
            return best_type
        else:
            return "unknown"

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return "unknown"


def generate_json(folder_path, excel_paths, output_path):
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

    OUTPUT_FILE = f"json/{output_path}.json"

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

    print(f"Writing to {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2)

    # Check duplicates
    print("Generating json file for duplicates...")
    check_duplicate_cards(OUTPUT_FILE)

    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Generate card JSON from images.")
    parser.add_argument("--image-folder", help="Path to image folder", required=True)
    parser.add_argument(
        "--excel-files", nargs="+", help="Path to Excel files", required=True
    )
    parser.add_argument("--output-name", help="Output JSON file", required=True)

    args = parser.parse_args()

    generate_json(args.image_folder, args.excel_files, args.output_name)


if __name__ == "__main__":
    main()
