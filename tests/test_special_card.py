import unittest
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_card_json import generate_json
from check_duplicate_cards import check_duplicate_cards
from generate_special_card_json import generate_special_card_data

image_folder = r"./A1-test-jp"
duplicates_list = r"./A1_duplicates.json"

# Verify image exists
if not os.path.exists(image_folder):
    unittest.skip(f"Image folder not found at {image_folder}")


class TestCardGenerator(unittest.TestCase):
    def test_card_generator(self):
        # Expected output
        with open(r"./A1_expected_result.json", "r") as f:
            expected_data = json.load(f)

        # Run the generation
        result = generate_json(
            image_folder,
            ["./A1_Charizard.xlsx", "./A1_Mewtwo.xlsx", "./A1_Pikachu.xlsx"],
        )

        # Assertions
        self.assertEqual(result, expected_data)


class TestDuplicateCard(unittest.TestCase):
    def test_duplicate_card(self):
        # Expected output
        with open(duplicates_list, "r") as f:
            expected_data = json.load(f)

        # Run the generation
        result = check_duplicate_cards("./A1_expected_result.json")

        # Assertions
        self.assertEqual(result, expected_data)


class TestSpecialCard(unittest.TestCase):
    def test_special_card(self):

        # Expected output
        with open(r"./A1_expected_special_result.json", "r") as f:
            expected_data = json.load(f)

        # Run the generation
        result = generate_special_card_data(image_folder, duplicates_list)

        # Assertions
        self.assertEqual(result, expected_data)


if __name__ == "__main__":
    unittest.main()
