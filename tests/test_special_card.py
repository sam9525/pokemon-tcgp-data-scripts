import unittest
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import generate_json, generate_special_card_data
from src.services import check_duplicate_cards

image_folder = r"./tests/A1-test-jp"
duplicates_list = r"./tests/A1_duplicates.json"
non_pokemon_booster_pack = {}

# Verify image exists
if not os.path.exists(image_folder):
    unittest.skip(f"Image folder not found at {image_folder}")


class TestCardGenerator(unittest.TestCase):
    def test_card_generator(self):
        # Expected output
        with open(r"./tests/A1_expected_result.json", "r") as f:
            expected_data = json.load(f)

        # Run the generation
        global non_pokemon_booster_pack
        result, non_pokemon_booster_pack = generate_json(
            image_folder,
            [
                "./tests/A1_Charizard.xlsx",
                "./tests/A1_Mewtwo.xlsx",
                "./tests/A1_Pikachu.xlsx",
            ],
        )

        # Assertions
        self.assertEqual(result, expected_data)


class TestDuplicateCard(unittest.TestCase):
    def test_duplicate_card(self):
        # Expected output
        with open(duplicates_list, "r") as f:
            expected_data = json.load(f)

        # Run the generation
        result = check_duplicate_cards("./tests/A1_expected_result.json")

        # Assertions
        self.assertEqual(result, expected_data)


class TestSpecialCard(unittest.TestCase):
    def test_special_card(self):

        # Expected output
        with open(r"./tests/A1_expected_special_result.json", "r") as f:
            expected_data = json.load(f)

        # Run the generation
        result = generate_special_card_data(image_folder, duplicates_list)

        # Combine the non pokemon booster pack
        for key, value in non_pokemon_booster_pack.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key].update(value)
            else:
                result[key] = value

        # Assertions
        self.assertEqual(result, expected_data)


if __name__ == "__main__":
    unittest.main()
