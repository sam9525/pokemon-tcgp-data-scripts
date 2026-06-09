import cv2
import numpy as np
import os
import sys
import argparse

# Add parent directory to path so it can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import CARD_REGIONS


def visualize_crops(image_path, output_path="visualized_crops.png"):
    # Load image using imdecode to handle Unicode paths safely on Windows
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print(f"Error: Could not read image from {image_path}")
        return

    height, width = img.shape[:2]
    annotated_img = img.copy()

    # Define colors for different regions (B, G, R)
    colors = {
        "type": (0, 255, 0),  # Green
        "weakness": (0, 0, 255),  # Red
        "attack": (255, 0, 0),  # Blue
        "trainer": (255, 255, 0),  # Cyan
        "name": (255, 0, 255),  # Magenta
        "name_pokemon": (0, 165, 255),  # Orange
    }

    # Check if the card is a Pokemon card or a Trainer card based on filename
    filename = os.path.basename(image_path)
    is_pokemon = filename.startswith("cPK") or "_cPK_" in filename

    if is_pokemon:
        relevant_regions = ["type", "weakness", "attack", "name_pokemon"]
        print("Detected Pokemon card: Hiding trainer and name regions.")
    else:
        relevant_regions = ["trainer", "name"]
        print(
            "Detected Trainer/non-Pokemon card: Hiding type, weakness, attack, and name_pokemon regions."
        )

    print(f"Image Resolution: {width}x{height}")
    print("-" * 50)
    print(
        f"{'Region':<15} | {'Coords (top, bottom, left, right)':<35} | {'Pixel Box (x1, y1) -> (x2, y2)'}"
    )
    print("-" * 50)

    for region_name, coords in CARD_REGIONS.items():
        if region_name not in relevant_regions:
            continue

        top = coords["top"]
        bottom = coords["bottom"]
        left = coords["left"]
        right = coords["right"]

        # Convert relative float coordinates to pixel integers
        x1 = int(width * left)
        y1 = int(height * top)
        x2 = int(width * right)
        y2 = int(height * bottom)

        color = colors.get(region_name, (255, 255, 255))

        # Draw the rectangle bounding box
        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)

        # Place label text slightly offset from the box
        label_y = y1 - 5 if y1 > 20 else y2 + 20
        cv2.putText(
            annotated_img,
            region_name,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )

        print(
            f"{region_name:<15} | {top:.2f}, {bottom:.2f}, {left:.2f}, {right:.2f} | ({x1}, {y1}) -> ({x2}, {y2})"
        )

    cv2.imwrite(output_path, annotated_img)
    print("-" * 50)
    print(f"Saved crop visualization to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize relevant CARD_REGIONS cropping coordinates on one or more card images."
    )
    parser.add_argument(
        "--images",
        nargs="+",
        help="Paths to card images or directories containing images to visualize.",
        default=[
            # Pokemon
            r"tests\A1-test-jp\cPK_10_000010_00_FUSHIGIDANE_C_M_M_ja_JP.png",
            # Second Evolution Pokemon
            r"tests\A1-test-jp\cPK_90_000890_00_GEKKOUGA_R_M_M_ja_JP.png",
            # Others, Trainer
            r"tests\A1-test-jp\cTR_20_000130_00_KATSURA_SR_M_M_ja_JP.png",
        ],
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save the annotated images.",
        default=".",
    )

    args = parser.parse_args()

    # Determine absolute script directory
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    resolved_images = []

    for path_item in args.images:
        # Resolve path relative to script directory if not absolute
        target_path = path_item
        if not os.path.isabs(target_path):
            target_path = os.path.join(script_dir, target_path)

        if not os.path.exists(target_path):
            # Try fallback to absolute path as-is
            target_path = path_item

        if os.path.isdir(target_path):
            # Scan directory for images
            for f in os.listdir(target_path):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    resolved_images.append(os.path.join(target_path, f))
        elif os.path.isfile(target_path):
            resolved_images.append(target_path)
        else:
            print(f"Warning: Path not found or invalid: {path_item}")

    if not resolved_images:
        print("Error: No valid images found to process.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    out_dir = args.output_dir
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(script_dir, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Processing {len(resolved_images)} images...")
    for idx, img_path in enumerate(resolved_images):
        filename = os.path.basename(img_path)
        output_filename = f"visualized_{filename}"
        output_path = os.path.join(out_dir, output_filename)

        print(f"\n[{idx + 1}/{len(resolved_images)}] Processing: {filename}")
        visualize_crops(img_path, output_path)


if __name__ == "__main__":
    main()
