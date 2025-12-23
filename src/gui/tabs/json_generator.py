from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton
import os
from src.utils import safe_dump_json
from src.config import SUPPORTED_EXCEL_FORMATS, EXPANSIONS
from src.services import (
    check_duplicate_cards,
    select_paths,
    update_display,
    remove_selected_paths,
    clear_paths,
)
from scripts import generate_json, generate_special_card_data
from src.utils import extract_folder_prefix, extract_excel_prefix
from src.gui.utils import check_file_exist
from src.gui.utils import (
    update_progress,
    update_status,
    on_finished,
    on_error,
    set_controls_enabled,
    select_folder_handler,
    clear_folder_handler,
)


class JsonGeneratorWorker(QThread):
    progress = pyqtSignal(float)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, selected_exp_code, selected_folder, selected_files):
        super().__init__()
        self.selected_exp_code = selected_exp_code
        self.OUTPUT_FILE = f"json/{selected_exp_code}.json"
        self.DUPLICATE_FILE = f"json/{selected_exp_code}_duplicates.json"
        self.SPECIAL_FILE = f"json/{selected_exp_code}_special.json"
        self.selected_folder = selected_folder
        self.selected_files = selected_files

    def run(self):
        class SignalProgressBar:
            def __init__(self, worker):
                self.worker = worker

            def update(self, n=1):
                self.worker.progress.emit(n)

            def write(self, msg):
                self.worker.log.emit(msg)

        pbar = SignalProgressBar(self)

        try:
            folder_path = self.selected_folder[0]

            # Generate json which include card types
            result, non_pokemon_booster_pack = generate_json(
                folder_path, self.selected_files, pbar=pbar
            )

            self.log.emit(f"Writing to {self.OUTPUT_FILE}...")
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            safe_dump_json(result, self.OUTPUT_FILE)

            # Check duplicates
            self.log.emit("Generating duplicate json file...")
            duplicate_list = check_duplicate_cards(self.OUTPUT_FILE, pbar=pbar)

            # Output the duplicate result
            if duplicate_list:
                safe_dump_json(duplicate_list, self.DUPLICATE_FILE)

            self.log.emit("Completed generating duplicate json file.")

            # Generate special card data
            self.log.emit("Generating special card data...")
            if duplicate_list:
                special_results = generate_special_card_data(
                    folder_path, self.DUPLICATE_FILE, pbar=pbar
                )
            else:
                special_results = generate_special_card_data(folder_path, "", pbar=pbar)

            # Combine the non pokemon booster pack
            for key, value in non_pokemon_booster_pack.items():
                if (
                    key in special_results
                    and isinstance(special_results[key], dict)
                    and isinstance(value, dict)
                ):
                    special_results[key].update(value)
                else:
                    special_results[key] = value

            self.log.emit("Combine non pokemon booster pack...")

            self.log.emit(f"Writing to {self.SPECIAL_FILE}...")
            safe_dump_json(special_results, self.SPECIAL_FILE)

            self.log.emit("Completed generating special card data.")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class JsonGeneratorTab:
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        # Init Expansion code
        for item in EXPANSIONS:
            self.main_window.expansionComboBox.addItem(item["name"], item["code"])

        # Set default expansion
        self.main_window.expansionComboBox.setCurrentIndex(
            self.main_window.expansionComboBox.findData(
                self.main_window.selected_exp_code
            )
        )

        self.main_window.expansionComboBox.currentIndexChanged.connect(
            self.on_exp_combobox_changed
        )

        # Select folder
        self.main_window.browseFolderBtnInTab3.clicked.connect(
            lambda: select_folder_handler(self.main_window, "json generator")
        )
        self.main_window.clearBtnInTab3.clicked.connect(
            lambda: clear_folder_handler(self.main_window, "json generator")
        )

        # Select excel files
        self.main_window.browseExcelBtnInTab3.clicked.connect(self.select_excel_handler)
        self.main_window.clearExcelBtnInTab3.clicked.connect(self.clear_excel_handler)
        self.main_window.removeSelectedBtnInTab3.clicked.connect(
            self.remove_selected_handler
        )

        # Start generating
        self.main_window.startGenBtn.clicked.connect(lambda: self.run_gen_json())

    def on_exp_combobox_changed(self):
        combobox = self.main_window.sender()
        currentIndex = combobox.currentIndex()

        self.main_window.selected_exp_name = combobox.currentText()
        self.main_window.selected_exp_code = combobox.itemData(currentIndex)

        # Change the expansion combobox in crawler tab
        if not self.main_window.expRadioBtn.isChecked():
            self.main_window.expComboB.setCurrentIndex(
                self.main_window.expComboB.findData(self.main_window.selected_exp_code)
            )

    def select_excel_handler(self):
        added = select_paths(
            self.main_window,
            self.main_window.selected_gen_json_files,
            mode="file",
            multi=True,
            file_filter=f"Excel Files ({';'.join(SUPPORTED_EXCEL_FORMATS)});;All Files (*)",
        )
        update_display(
            list_widget=self.main_window.excelListWidget,
            line_edit=self.main_window.filesLineEditInTab3,
            count_label=self.main_window.countExcelLabel,
            items=self.main_window.selected_gen_json_files,
        )

        if added > 0:
            self.main_window.statusbar.showMessage(
                f"Added {added} file(s). Total: {len(self.main_window.selected_gen_json_files)}"
            )

    def clear_excel_handler(self):
        if clear_paths(self.main_window, self.main_window.selected_gen_json_files):
            update_display(
                list_widget=self.main_window.excelListWidget,
                line_edit=self.main_window.filesLineEditInTab3,
                count_label=self.main_window.countExcelLabel,
                items=self.main_window.selected_gen_json_files,
            )
            self.main_window.statusbar.showMessage("Excel File cleared")

    def remove_selected_handler(self):
        removed = remove_selected_paths(
            self.main_window.excelListWidget, self.main_window.selected_gen_json_files
        )
        if removed > 0:
            update_display(
                list_widget=self.main_window.excelListWidget,
                line_edit=self.main_window.filesLineEditInTab3,
                count_label=self.main_window.countExcelLabel,
                items=self.main_window.selected_gen_json_files,
            )
            self.main_window.statusbar.showMessage(f"Removed {removed} file(s)")

    def check_exp_folder_excel_match(self, exp_code):
        # Check if the folder name and expansion code match
        unmatched_paths = []

        # Check folder name
        folder_prefix = extract_folder_prefix(
            self.main_window.selected_gen_json_folder[0]
        )
        if folder_prefix != exp_code:
            unmatched_paths.append(self.main_window.selected_gen_json_folder[0])

        # Check excel files name
        excel_paths = self.main_window.selected_gen_json_files

        for excel_path in excel_paths:
            excel_prefix = extract_excel_prefix(excel_path, separator="_")
            if excel_prefix != exp_code:
                unmatched_paths.append(excel_path)

        if unmatched_paths:
            set_controls_enabled(self.main_window, "json generator", True)
            unmatched_list_str = "\n".join(unmatched_paths)
            QMessageBox.warning(
                self.main_window,
                "Input Error",
                f"The following folder or excel files do not match the expansion code '{exp_code}':\n{unmatched_list_str}",
            )
            return False

        return True

    def run_gen_json(self):
        if not self.main_window.selected_gen_json_folder:
            set_controls_enabled(self.main_window, "json generator", True)
            QMessageBox.warning(self.main_window, "Input Error", "No folder selected.")
            return

        if not self.main_window.selected_gen_json_files:
            set_controls_enabled(self.main_window, "json generator", True)
            QMessageBox.warning(
                self.main_window, "Input Error", "No Excel file selected."
            )
            return

        # Check if the folder name and expansion code match
        if not self.check_exp_folder_excel_match(
            self.main_window.selected_exp_code,
        ):
            self.main_window.statusbar.showMessage(
                "Folder name and excel files do not match with expansion code."
            )
            return

        # Set to disabled
        set_controls_enabled(self.main_window, "json generator", False)

        self.worker = JsonGeneratorWorker(
            self.main_window.selected_exp_code,
            self.main_window.selected_gen_json_folder,
            self.main_window.selected_gen_json_files,
        )

        # Connect signals
        self.worker.progress.connect(
            lambda n: update_progress(self.main_window, n, "genJsonProgressBar")
        )
        self.worker.log.connect(lambda msg: update_status(self.main_window, msg))
        self.worker.finished.connect(
            lambda: on_finished(self.main_window, tab="json generator")
        )
        self.worker.error.connect(
            lambda: on_error(self.main_window, tab="json generator")
        )

        # Reset UI
        self.main_window.genJsonProgressBar.setValue(0)
        self.current_progress_value = 0.0

        # Check if the set code excel file exist
        files_exist = check_file_exist(
            self.main_window, self.main_window.selected_exp_code, mode="json"
        )
        if not files_exist:
            set_controls_enabled(self.main_window, "json generator", True)
            return

        # Start thread
        self.worker.start()
