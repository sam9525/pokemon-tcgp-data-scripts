import pandas as pd
import os
from src.utils import log


def load_promo_lists(pbar=None):
    """
    Load the promo lists from the Excel files.
    Args:
        pbar: Progress bar for UI updates.
    Returns:
        Tuple of two sets: (promo_a_names, promo_b_names)
    """
    promo_a_names = set()
    promo_b_names = set()

    def _load_single_promo_list(file_path, promo_set, promo_type):
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                if "Image Name" in df.columns:
                    promo_set.update(
                        df["Image Name"].astype(str).str.strip().str.split("_").str[4]
                    )
                else:
                    log(f"Warning: 'Image Name' column not found in {file_path}", pbar)
            except Exception as e:
                log(f"Error reading {file_path}: {e}", pbar)
        else:
            log(f"Warning: {file_path} not found", pbar)

    try:
        _load_single_promo_list("lists/PROMO-A.xlsx", promo_a_names, "promo-a")
        _load_single_promo_list("lists/PROMO-B.xlsx", promo_b_names, "promo-b")
    except Exception as e:
        log(f"Error loading promo lists: {e}", pbar)
        log("Please use the crawler to get the promo list first!", pbar)
        return set(), set()

    return promo_a_names, promo_b_names


def get_promo_pack(card_name):
    """
    Checks if the card_name exists in the promo lists.
    Args:
        card_name (str): The name of the card to check.
    Returns "promo-a", "promo-b", or None.
    """
    promo_a_names, promo_b_names = load_promo_lists()

    if card_name in promo_a_names:
        return "promo-a"
    if card_name in promo_b_names:
        return "promo-b"

    return None


if __name__ == "__main__":
    # Test
    promo_a_names, promo_b_names = load_promo_lists()
    print(f"Loaded {len(promo_a_names)} PROMO-A cards")
    print(f"Loaded {len(promo_b_names)} PROMO-B cards")
