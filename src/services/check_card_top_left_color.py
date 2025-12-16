import cv2
import numpy as np
import colorsys
from src.config import CARD_REGIONS


def check_top_left_color(image_path):
    """
    Check the trainer color of a Pokemon card image
    Cropping the card top-left
    Using HSV to check the color
    Args:
        image_path (str): Path to the image file
    """
    # Use imdecode and fromfile to handle unicode paths on Windows
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return

    height, width = img.shape[:2]

    # Top 3-6%, Left 5-15%
    top = int(height * CARD_REGIONS["trainer"]["top"])
    bottom = int(height * CARD_REGIONS["trainer"]["bottom"])
    left = int(width * CARD_REGIONS["trainer"]["left"])
    right = int(width * CARD_REGIONS["trainer"]["right"])

    crop = img[top:bottom, left:right]

    if crop.size == 0:
        print("Error: Crop is empty. Check coordinates.")
        return

    # Calculate average color
    avg_color_per_row = np.average(crop, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)

    # avg_color is [B, G, R]
    b, g, r = avg_color

    # Convert to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    hue_degrees = h * 360

    # Orange: 15-45
    # Blue: 180-260
    # Purple: 260-330

    if 15 <= hue_degrees < 45:
        return "orange"
    elif 180 <= hue_degrees < 260:
        return "blue"
    elif 260 <= hue_degrees < 330 or hue_degrees >= 330 or hue_degrees < 15:
        return "purple"
    else:
        # Find closest by hue distance
        distances = {
            "orange": min(abs(hue_degrees - 30), 360 - abs(hue_degrees - 30)),
            "blue": min(abs(hue_degrees - 220), 360 - abs(hue_degrees - 220)),
            "purple": min(abs(hue_degrees - 290), 360 - abs(hue_degrees - 290)),
        }
        return min(distances, key=distances.get)
