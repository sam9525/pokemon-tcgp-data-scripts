import cv2
import numpy as np
from google import genai
from google.genai import types
from src.utils import log
from src.config import CARD_REGIONS


def text_reader(image, client: genai.Client, lang: str, pbar=None):
    """
    Extracts Pokemon card name from an image using Google GenAI.
    Args:
        image: The image to extract the name from.
        client: The Google GenAI client.
        lang: The language of the card name.
    Returns:
        The extracted card name.
    """
    # Convert image to buffer, need to use for ai
    _, buffer = cv2.imencode(".png", image)

    prompt = f"""
    Extract the Pokemon card name from this image.
    The name is usually at the top of the card.
    Return the Pokemon card name from the image.
    Target Language: {lang}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            # Read prompt and image as bytes
            contents=[
                prompt,
                types.Part.from_bytes(data=buffer.tobytes(), mime_type="image/png"),
            ],
            # Response type in text
            config=types.GenerateContentConfig(response_mime_type="text/plain"),
        )
        return response.text
    except Exception as e:
        log(f"Error in text_reader: {e}", pbar)
        return None


def analyze_card_name(image_path, lang, client, pbar=None):
    """
    Reads an image from path, crops the name area, and extracts text.
    Args:
        image_path: The path to the image.
        lang: The language of the card name.
        api_key: The API key for Google GenAI (optional, used if client is None).
        client: The Google GenAI client (optional, preferred).
        pbar: The progress bar (will be None in multiprocessing worker).
    Returns:
        The extracted card name.
    """
    try:
        # Read image
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return "unknown"

        height, width = img.shape[:2]

        # Crop region covering both potential name locations
        left = int(width * CARD_REGIONS["name"]["left"])
        top = int(height * CARD_REGIONS["name"]["top"])
        right = int(width * CARD_REGIONS["name"]["right"])
        bottom = int(height * CARD_REGIONS["name"]["bottom"])

        crop = img[top:bottom, left:right]

        # Read text from image
        response_text = text_reader(crop, client, lang, pbar)

        return response_text

    except Exception as e:
        log(f"Error processing {image_path}: {e}", pbar)
        return "unknown"
