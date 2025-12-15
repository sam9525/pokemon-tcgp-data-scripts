import pandas as pd
import os
import glob
import json
import cv2
import numpy as np
import argparse
from src.services import check_duplicate_cards
from src.services import load_icons, match_icon
from src.utils import log, update_pbar
from multiprocessing import Pool
from functools import partial
from src.config import CARD_REGIONS


def get_image_type(image_path, icons, pbar=None):
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
        left = int(width * CARD_REGIONS["type"]["left"])
        top = int(height * CARD_REGIONS["type"]["top"])
        right = int(width * CARD_REGIONS["type"]["right"])
        bottom = int(height * CARD_REGIONS["type"]["bottom"])

        crop = img[top:bottom, left:right]

        best_type = match_icon(crop, icons, threshold=0.5)

        if best_type:
            return best_type
        else:
            return "unknown"

    except Exception as e:
        log(f"Error processing {image_path}: {e}", pbar)
        return "unknown"


def generate_json(folder_path, excel_paths, pbar=None):
    """
    Generate card JSON.
    Args:
        folder_path (str): Path to folder.
        excel_paths (list): List of Excel file paths.
        pbar (QProgressBar): Progress bar.
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

    log("Loading icons...", pbar)
    icons = load_icons()
    log(f"Loaded {len(icons)} icons.", pbar)

    log("Loading Excel files...", pbar)
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
            log(f"Loaded {len(pack_data[pack_name])} items for {pack_name}", pbar)
        except Exception as e:
            log(f"Error loading {path}: {e}", pbar)
            return

    log("Scanning images...", pbar)
    update_pbar(5, pbar)

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
            result[p][t] = set()

    # Create reversed map for faster lookup in O(1)
    card_to_packs = {}
    for pack_name, ids in pack_data.items():
        for card_id in ids:
            if card_id not in card_to_packs:
                card_to_packs[card_id] = []
            card_to_packs[card_id].append(pack_name)

    count = 0

    # Prepare tasks
    task_paths = []
    task_metadata = []
    for img_path in image_files:
        filename = os.path.basename(img_path)
        try:
            parts = filename.split("_")
            card_id = parts[2]
            matched_packs = card_to_packs.get(card_id)
            if matched_packs:
                task_paths.append(img_path)
                task_metadata.append((matched_packs, card_id))
        except IndexError:
            continue

    total_images = len(task_paths)
    log(f"Found {total_images} valid cards to process.", pbar)

    process_func = partial(get_image_type, icons=icons)

    # Using half of the cpu processes
    half_processes = os.cpu_count() // 2

    # Process images in parallel
    with Pool(processes=half_processes) as pool:
        results_list = list(pool.imap(process_func, task_paths))

    update_pbar(15, pbar)

    # Aggregate results
    count = 0
    for (matched_packs, card_id), card_type in zip(task_metadata, results_list):
        update_pbar(10 / len(results_list), pbar)

        if card_type == "unknown":
            continue

        for pack_name in matched_packs:
            if card_type in result[pack_name]:
                result[pack_name][card_type].add(card_id)
                count += 1

    log(f"\nProcessing complete. Processed {count} cards.", pbar)

    # Sort lists
    for p in result:
        for t in result[p]:
            result[p][t] = sorted(list(result[p][t]))

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
