import cv2
import numpy as np
import os
import json
import argparse
import pandas as pd
from load_match_icon import load_icons, match_icon, find_all_icons
from check_card_top_left_color import check_top_left_color


weakness_map = {
    "grass": "fire",
    "fire": "water",
    "water": "lightning",
    "lightning": "fighting",
    "psychic": "darkness",
    "fighting": "grass",
    "darkness": "fighting",
    "metal": "fire",
    "colorless": "fighting",
    "dragon": "none",
}


def analyze_image(image_path, icons, duplicate_data, key, gold_card):
    # Use imdecode and fromfile to handle unicode paths on Windows
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return None

    height, width = img.shape[:2]
    results = {}

    # 1. Card Type (Top Right)
    # Top 3-9%, Left 88-95%
    top_type = int(height * 0.03)
    bottom_type = int(height * 0.09)
    left_type = int(width * 0.88)
    right_type = int(width * 0.95)
    crop_type = img[top_type:bottom_type, left_type:right_type]

    card_type = match_icon(crop_type, icons)

    # Check if card_type is None, either tool or trainer
    if card_type is None and check_top_left_color(image_path) == "orange":
        results["trainer"] = "trainer"
        return results
    elif card_type is None and check_top_left_color(image_path) == "purple":
        results["trainer"] = "pokemon tool"
        return results
    elif card_type is None and check_top_left_color(image_path) == "blue":
        results["trainer"] = "tool"
        return results

    results["type"] = card_type

    # 2. Weakness (Bottom Left)
    # Bottom 86-89%, Left 28-33%
    top_weak = int(height * 0.86)
    bottom_weak = int(height * 0.89)
    left_weak = int(width * 0.28)
    right_weak = int(width * 0.33)
    crop_weak = img[top_weak:bottom_weak, left_weak:right_weak].copy()

    # Remove white background
    lower_white = np.array([200, 200, 200], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(crop_weak, lower_white, upper_white)
    crop_weak[mask > 0] = [0, 0, 0]

    # Weakness icon is smaller, around 0.15 scale
    weakness_scales = np.linspace(0.12, 0.18, 5)
    weakness_type = match_icon(
        crop_weak,
        icons,
        threshold=0.3,
        scales=weakness_scales,
        method=cv2.TM_CCOEFF_NORMED,
    )

    if card_type == "dragon":
        results["weakness"] = "none"
    elif weakness_type != weakness_map[card_type]:
        results["weakness"] = weakness_type

    # 3. Fight Energy / Attack Cost (Middle Left)
    # Bottom 55-80%, Left 5-30%
    top_atk = int(height * 0.55)
    bottom_atk = int(height * 0.80)
    left_atk = int(width * 0.05)
    right_atk = int(width * 0.30)
    crop_atk = img[top_atk:bottom_atk, left_atk:right_atk]

    # Find ALL icons (e.g. fighting, colorless)
    # But only return if Fight Energy doesn't match card type
    fight_energy = find_all_icons(crop_atk, icons)
    if results["type"] in fight_energy:
        results["fightEnergy"] = []
    else:
        results["fightEnergy"] = fight_energy

    # Check if the card is exist in all booster pack in same set
    if key in duplicate_data:
        results["boosterPack"] = duplicate_data[key]["boosterPack"]
    elif gold_card:
        results["boosterPack"] = sorted(
            set(
                pack for card in duplicate_data.values() for pack in card["boosterPack"]
            )
        )

    return results


def process_single_card(image_path, duplicate_data):
    # Extract ID from filename
    filename = os.path.basename(image_path)
    key = None
    gold_card = False

    try:
        # Expected format: cTR_20_000590_00_LILIE_SR_zh_TW.png -> 000590
        parts = filename.split("_")
        if len(parts) >= 3:
            key = parts[2]
            if parts[3] == "02":
                gold_card = True
    except:
        pass

    # Analyze image
    print(f"Analyzing {image_path}...")
    icons = load_icons()
    analysis = analyze_image(image_path, icons, duplicate_data, key, gold_card)

    if analysis and (
        analysis.get("trainer") == "trainer"
        or analysis.get("trainer") == "pokemon tool"
        or analysis.get("trainer") == "tool"
    ):
        # Extract card name from filename
        parts = filename.split("_")
        if len(parts) >= 4:
            key = parts[4]

        final_result = {
            "type": "none",
            "trainer": analysis.get("trainer"),
            "fightEnergy": "none",
            "weakness": "none",
            **(
                {"boosterPack": analysis.get("boosterPack")}
                if analysis.get("boosterPack")
                else {}
            ),
        }
    else:
        final_result = {
            **(
                {"weakness": analysis.get("weakness")}
                if analysis.get("weakness")
                else {}
            ),
            **(
                {"fightEnergy": analysis.get("fightEnergy")}
                if analysis.get("fightEnergy")
                else {}
            ),
            **(
                {"boosterPack": analysis.get("boosterPack")}
                if analysis.get("boosterPack")
                else {}
            ),
        }

    return key, final_result


def generate_card_data(image_folder, duplicate_list):
    results = {}
    non_pokemon = {}

    # Check if path exists
    if not os.path.exists(image_folder):
        print(f"Error: Folder {image_folder} does not exist.")
        return results

    with open(duplicate_list, "r", encoding="utf-8") as f:
        duplicate_data = json.load(f)

    # Iterate over all files in the folder
    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(image_folder, filename)
            key, data = process_single_card(image_path, duplicate_data)
            if key and data:
                if (
                    data.get("trainer") == "trainer"
                    or data.get("trainer") == "pokemon tool"
                    or data.get("trainer") == "tool"
                ):
                    non_pokemon[key] = data
                else:
                    results[key] = data

    # Combine non-pokemon at the top of the results
    results = {**non_pokemon, **results}

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generating the special Pokemon card image."
    )
    parser.add_argument(
        "--image-folder", required=True, help="Path to the image folder:"
    )
    parser.add_argument(
        "--duplicate-list", required=True, help="Path to duplicate list json file:"
    )
    parser.add_argument("--output", required=True, help="Output JSON file")

    args = parser.parse_args()

    final_results = generate_card_data(args.image_folder, args.duplicate_list)

    if final_results:
        OUTPUT_FILE = f"json/{args.output}.json"
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        # Write JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_results, f, indent=2)


if __name__ == "__main__":
    main()
