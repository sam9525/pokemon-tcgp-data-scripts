import unittest
from src.utils import extract_folder_prefix, extract_excel_prefix


class TestValidation(unittest.TestCase):
    def test_extract_folder_prefix(self):
        # Case 1: Standard case "Prefix - Description"
        path1 = "/path/to/A1_genetic-apex - Some Description/images"
        self.assertEqual(extract_folder_prefix(path1), "A1_genetic-apex")

        # Case 2: Just Prefix
        path2 = "/path/to/A1a/images"
        self.assertEqual(extract_folder_prefix(path2), "A1a")

        # Case 3: Windows path
        path3 = "C:\\path\\to\\A1_genetic-apex - Description\\images"
        self.assertEqual(extract_folder_prefix(path3), "A1_genetic-apex")

    def test_extract_excel_prefix(self):
        # Case 1: With separator "_"
        path1 = "/path/to/A1_genetic-apex_cards.xlsx"
        self.assertEqual(extract_excel_prefix(path1, separator="_"), "A1")

        # Case 2: Without separator (default)
        path2 = "/path/to/A1_genetic-apex.xlsx"
        self.assertEqual(extract_excel_prefix(path2), "A1_genetic-apex")

        # Case 3: Separator not present
        path3 = "/path/to/A1_genetic-apex.xlsx"
        self.assertEqual(
            extract_excel_prefix(path3, separator="_"), "A1"
        )  # First split part is whole string if separator used to split whole string logic?
        # wait, stem is A1_genetic-apex. split('_') -> ['A1', 'genetic-apex']. So [0] is 'A1'. Correct.

        path4 = "/path/to/SimpleName.xlsx"
        self.assertEqual(extract_excel_prefix(path4, separator="_"), "SimpleName")
