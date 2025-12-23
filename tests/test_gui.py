import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

# Add scripts directory to path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
sys.path.append(scripts_dir)

# Ensure we can find the UI file regardless of where the test is run from
# TCGPToolGUI uses relative path "src\gui\gui.ui", so we might need to change cwd
# However, for now assuming running from scripts dir as per plan

from unittest.mock import MagicMock

# Mock playwright to avoid dependency issues during GUI testing
mock_playwright = MagicMock()
sys.modules["playwright"] = mock_playwright
sys.modules["playwright.async_api"] = mock_playwright

# Mock google.genai to avoid dependency issues
mock_google = MagicMock()
sys.modules["google"] = mock_google
sys.modules["google.genai"] = mock_google

from tcgp_tool_gui import TCGPToolGUI
from PyQt6.QtWidgets import QMessageBox

from unittest.mock import patch

# Single QApplication instance for all tests
# Check if one already exists (e.g. if run by some other runner)
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestTCGPToolGUI(unittest.TestCase):
    def setUp(self):
        # We need to make sure we are in the scripts directory so relative paths in TCGPToolGUI work
        self.original_cwd = os.getcwd()
        os.chdir(scripts_dir)

        # Setup patches
        self.patches = []

        # Patch Workers
        self.crawler_worker_patch = patch("src.gui.tabs.crawler.CrawlerWorker")
        self.renamer_worker_patch = patch("src.gui.tabs.image_renamer.RenamerWorker")
        self.json_worker_patch = patch(
            "src.gui.tabs.json_generator.JsonGeneratorWorker"
        )

        # Patch check_file_exist in different modules
        self.crawler_check_patch = patch(
            "src.gui.tabs.crawler.check_file_exist", return_value=True
        )
        self.json_check_patch = patch(
            "src.gui.tabs.json_generator.check_file_exist", return_value=True
        )  # Also used in json_generator

        # Start patches
        self.mock_crawler_worker = self.crawler_worker_patch.start()
        self.mock_renamer_worker = self.renamer_worker_patch.start()
        self.mock_json_worker = self.json_worker_patch.start()
        self.mock_crawler_check = self.crawler_check_patch.start()
        self.mock_json_check = self.json_check_patch.start()

        self.patches.extend(
            [
                self.crawler_worker_patch,
                self.renamer_worker_patch,
                self.json_worker_patch,
                self.crawler_check_patch,
                self.json_check_patch,
            ]
        )

        # Patch select_paths in folder_handler to avoid opening dialogs
        self.select_paths_patch = patch("src.gui.utils.folder_handler.select_paths")
        self.mock_select_paths = self.select_paths_patch.start()
        self.patches.append(self.select_paths_patch)

        # Create the GUI instance
        self.window = TCGPToolGUI()
        self.window.show()

    def test_init(self):
        """Verify the main window initializes without error."""
        self.assertIsNotNone(self.window)

    def test_window_title(self):
        """Verify the window title is correct."""
        self.assertEqual(self.window.windowTitle(), "TCGP Tool")

    def test_tabs_initialization(self):
        """Verify that tab objects are initialized."""
        self.assertIsNotNone(self.window.tab1)
        self.assertIsNotNone(self.window.tab2)
        self.assertIsNotNone(self.window.tab3)

    def test_tab_widgets_presence(self):
        """Check if the tab widget actually contains tabs."""
        # Assuming the UI file adds the tabs to a QTabWidget named 'tabWidget'
        self.assertGreater(self.window.tabWidget.count(), 0)

    def test_crawler_tab(self):
        """Verify Crawler tab functionality."""
        # Check default state
        self.assertTrue(self.window.expRadioBtn.isChecked())
        self.assertFalse(self.window.packKeyGB.isVisible())
        self.assertEqual(self.window.selected_exp_name, "A1_genetic-apex")

        # Test Radio Button interactions
        self.window.packRadioBtn.setChecked(True)
        self.assertTrue(self.window.packKeyGB.isVisible())

        self.window.expRadioBtn.setChecked(True)
        self.assertFalse(self.window.packKeyGB.isVisible())

        # Check all controls are enabled
        self.assertTrue(self.window.expRadioBtn.isEnabled())
        self.assertTrue(self.window.packRadioBtn.isEnabled())
        self.assertTrue(self.window.expComboB.isEnabled())
        self.assertTrue(self.window.packKeyComboB.isEnabled())
        self.assertTrue(self.window.startCrawlingBtn.isEnabled())

        # Click the button (Mocked Worker will be initialized instead of real one)
        self.window.startCrawlingBtn.click()

        # Verify Worker was initialized and started
        self.mock_crawler_worker.assert_called()
        # The worker instance is the return value of the class mock
        worker_instance = self.mock_crawler_worker.return_value
        worker_instance.start.assert_called_once()

        # Check all controls are disabled when running
        self.assertFalse(self.window.expRadioBtn.isEnabled())
        self.assertFalse(self.window.packRadioBtn.isEnabled())
        self.assertFalse(self.window.expComboB.isEnabled())
        self.assertFalse(self.window.packKeyComboB.isEnabled())
        self.assertFalse(self.window.startCrawlingBtn.isEnabled())

    def test_renamer_tab(self):
        """Verify Image Renamer tab functionality."""
        # Check default state
        self.assertTrue(self.window.dryRunCB.isChecked())
        self.assertEqual(self.window.folderListWidget.count(), 0)
        self.assertEqual(self.window.selected_rename_folders, [])

        # Test Clear Folders Handler
        # Manually add some dummy data
        self.window.selected_rename_folders.append("/dummy/path")

        # Patch QMessageBox to automatically say "Yes"
        with patch(
            "PyQt6.QtWidgets.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            self.window.clearFoldersBtnInTab2.click()

        # Verify cleared
        self.assertEqual(self.window.selected_rename_folders, [])
        self.assertEqual(self.window.folderListWidget.count(), 0)

        # Check all controls are enabled
        self.assertTrue(self.window.browseFolderBtnInTab2.isEnabled())
        self.assertTrue(self.window.clearFoldersBtnInTab2.isEnabled())
        self.assertTrue(self.window.removeSelectedBtnInTab2.isEnabled())
        self.assertTrue(self.window.browseFileBtnInTab2.isEnabled())
        self.assertTrue(self.window.clearFileBtnInTab2.isEnabled())
        self.assertTrue(self.window.startRenameBtn.isEnabled())

        # Prepare for start run
        self.window.selected_rename_folders = ["/path/to/A1 - Set/images"]
        self.window.selected_rename_file = ["/path/to/A1_list.xlsx"]

        # Click start button
        self.window.startRenameBtn.click()

        # Verify Worker was initialized and started
        self.mock_renamer_worker.assert_called()
        worker_instance = self.mock_renamer_worker.return_value
        worker_instance.start.assert_called_once()

        # Check all controls are disabled when running
        self.assertFalse(self.window.browseFolderBtnInTab2.isEnabled())
        self.assertFalse(self.window.clearFoldersBtnInTab2.isEnabled())
        self.assertFalse(self.window.removeSelectedBtnInTab2.isEnabled())
        self.assertFalse(self.window.browseFileBtnInTab2.isEnabled())
        self.assertFalse(self.window.clearFileBtnInTab2.isEnabled())
        self.assertFalse(self.window.startRenameBtn.isEnabled())

    def test_renamer_tab_validation(self):
        """Verify validation logic in renamer tab re-enables controls and shows warning."""
        # Ensure nothing selected
        self.window.selected_rename_folders = []
        self.window.selected_rename_file = []

        # Patch QMessageBox.warning
        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            # Click start - should fail validation
            self.window.startRenameBtn.click()

            # Verify warning was shown
            mock_warning.assert_called()

        # Check controls are still enabled
        self.assertTrue(self.window.startRenameBtn.isEnabled())

    def test_json_generator_tab(self):
        """Verify JSON Generator tab functionality."""
        # Check default state
        self.assertEqual(self.window.selected_gen_json_folder, [])
        self.assertEqual(self.window.selected_gen_json_files, [])

        # Manually add some dummy data
        self.window.selected_gen_json_folder.append("/path/to/A1 - Set/json_output")

        self.window.selected_gen_json_files.append("/path/to/A1.xlsx")

        # Check all controls are enabled
        self.assertTrue(self.window.expansionComboBox.isEnabled())
        self.assertTrue(self.window.browseFolderBtnInTab3.isEnabled())
        self.assertTrue(self.window.clearBtnInTab3.isEnabled())
        self.assertTrue(self.window.browseExcelBtnInTab3.isEnabled())
        self.assertTrue(self.window.clearExcelBtnInTab3.isEnabled())
        self.assertTrue(self.window.removeSelectedBtnInTab3.isEnabled())
        self.assertTrue(self.window.startGenBtn.isEnabled())

        # Click start button
        self.window.startGenBtn.click()

        # Verify Worker was initialized and started
        self.mock_json_worker.assert_called()
        worker_instance = self.mock_json_worker.return_value
        worker_instance.start.assert_called_once()

        # Check all controls are disabled when running
        self.assertFalse(self.window.expansionComboBox.isEnabled())
        self.assertFalse(self.window.browseFolderBtnInTab3.isEnabled())
        self.assertFalse(self.window.clearBtnInTab3.isEnabled())
        self.assertFalse(self.window.browseExcelBtnInTab3.isEnabled())
        self.assertFalse(self.window.clearExcelBtnInTab3.isEnabled())
        self.assertFalse(self.window.removeSelectedBtnInTab3.isEnabled())
        self.assertFalse(self.window.startGenBtn.isEnabled())

    def test_json_generator_validation(self):
        """Verify validation logic in json generator tab."""
        # Ensure nothing selected
        self.window.selected_gen_json_folder = []
        self.window.selected_gen_json_files = []

        # Patch QMessageBox.warning
        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            # Click start - should fail validation
            self.window.startGenBtn.click()

            # Verify warning was shown
            mock_warning.assert_called()

        # Check controls are still enabled
        self.assertTrue(self.window.startGenBtn.isEnabled())

    def test_renamer_tab_folder_selection(self):
        """Verify folder selection in renamer tab."""
        # Configure mock to simulate user selecting a folder
        test_folder = "/path/to/selected/folder"

        def side_effect(
            parent, current_paths, mode="folder", multi=True, file_filter=""
        ):
            current_paths.append(test_folder)
            return 1

        self.mock_select_paths.side_effect = side_effect

        # Click browse button
        self.window.browseFolderBtnInTab2.click()

        # Verify select_paths was called
        self.mock_select_paths.assert_called()

        # Verify folder was added (logic inside folder_handler handles UI update, but we can check state)
        self.assertIn(test_folder, self.window.selected_rename_folders)
        self.assertEqual(self.window.folderListWidget.count(), 1)
        self.assertEqual(self.window.folderListWidget.item(0).text(), test_folder)

    def test_renamer_tab_file_selection(self):
        """Verify file selection in renamer tab."""
        # Configure mock to simulate user selecting a file
        test_file = "/path/to/selected/file.xlsx"

        def side_effect(
            parent, current_paths, mode="file", multi=False, file_filter=""
        ):
            current_paths.append(test_file)
            return 1

        self.mock_select_paths.side_effect = side_effect

        # Click browse button
        self.window.browseFileBtnInTab2.click()

        # Verify select_paths was called
        self.mock_select_paths.assert_called()

        self.assertEqual(self.window.fileLineEdit.text(), test_file)

    def test_json_generator_tab_folder_selection(self):
        """Verify folder selection in json generator tab."""
        test_folder = "/path/to/json/folder"

        def side_effect(
            parent, current_paths, mode="folder", multi=True, file_filter=""
        ):
            current_paths.append(test_folder)
            return 1

        self.mock_select_paths.side_effect = side_effect

        self.window.browseFolderBtnInTab3.click()

        self.mock_select_paths.assert_called()
        self.assertIn(test_folder, self.window.selected_gen_json_folder)
        self.assertEqual(self.window.folderLineEditInTab3.text(), test_folder)

    def test_json_generator_tab_excel_selection(self):
        """Verify excel file selection in json generator tab."""
        test_file = "/path/to/excel/file.xlsx"

        def side_effect(parent, current_paths, mode="file", multi=True, file_filter=""):
            current_paths.append(test_file)
            return 1

        self.mock_select_paths.side_effect = side_effect

        self.window.browseExcelBtnInTab3.click()

        self.mock_select_paths.assert_called()
        self.assertIn(test_file, self.window.selected_gen_json_files)
        self.assertEqual(self.window.excelListWidget.count(), 1)
        self.assertEqual(self.window.excelListWidget.item(0).text(), test_file)

    def tearDown(self):
        self.window.close()

        # Stop patches
        for p in self.patches:
            p.stop()

        # Restore CWD
        os.chdir(self.original_cwd)


if __name__ == "__main__":
    unittest.main()
