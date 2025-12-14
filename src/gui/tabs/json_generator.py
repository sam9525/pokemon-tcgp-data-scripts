from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton
import os
import json
from src.config import expansion_code
from src.services import (
    check_duplicate_cards,
    select_paths,
    update_display,
    remove_selected_paths,
    clear_paths,
)
from scripts import generate_json, generate_special_card_data


class JsonGeneratorWorker(QThread):
    progress = pyqtSignal(float)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, selected_exp_code, selected_folder, selected_files):
        super().__init__()
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
            result = generate_json(folder_path, self.selected_files, pbar=pbar)

            self.log.emit(f"Writing to {self.OUTPUT_FILE}...")
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            with open(self.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            # Check duplicates
            self.log.emit("Generating duplicate json file...")
            duplicate_list = check_duplicate_cards(self.OUTPUT_FILE, pbar=pbar)

            # Output the duplicate result
            with open(self.DUPLICATE_FILE, "w", encoding="utf-8") as f:
                json.dump(duplicate_list, f, indent=2)

            self.log.emit("Completed generating duplicate json file.")

            # Generate special card data
            self.log.emit("Generating special card data...")
            special_results = generate_special_card_data(
                folder_path, self.DUPLICATE_FILE, pbar=pbar
            )

            self.log.emit(f"Writing to {self.SPECIAL_FILE}...")
            with open(self.SPECIAL_FILE, "w", encoding="utf-8") as f:
                json.dump(special_results, f, indent=2)

            self.log.emit("Completed generating special card data.")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class JsonGeneratorTab:
    def __init__(self, main_window):
        self.main_window = main_window
        self.selected_exp_name = "A1_genetic-apex"
        self.selected_exp_code = "A1"
        self.setup_ui()

    def setup_ui(self):
        # Init Expansion code
        for item in expansion_code:
            self.main_window.expansionComboBox.addItem(item["name"], item["code"])

        self.main_window.expansionComboBox.currentIndexChanged.connect(
            self.on_exp_combobox_changed
        )

        # Select folder
        self.main_window.browseFolderBtnInTab3.clicked.connect(
            self.select_folder_handler
        )
        self.main_window.clearBtnInTab3.clicked.connect(self.clear_folder_handler)

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

        self.selected_exp_name = combobox.currentText()
        self.selected_exp_code = combobox.itemData(currentIndex)

    def select_folder_handler(self):
        if select_paths(
            self.main_window,
            self.main_window.selected_gen_json_folder,
            mode="folder",
            multi=False,
        ):
            update_display(
                line_edit=self.main_window.folderLineEditInTab3,
                count_label=self.main_window.countExcelLabel,
                items=self.main_window.selected_gen_json_folder,
            )
            self.main_window.statusbar.showMessage("Added 1 folder.")

    def clear_folder_handler(self):
        if clear_paths(
            self.main_window, self.main_window.selected_gen_json_folder, confirm=False
        ):
            update_display(
                line_edit=self.main_window.folderLineEditInTab3,
                items=self.main_window.selected_gen_json_folder,
            )
            self.main_window.statusbar.showMessage("Excel File cleared")

    def select_excel_handler(self):
        added = select_paths(
            self.main_window,
            self.main_window.selected_gen_json_files,
            mode="file",
            multi=True,
            file_filter="Excel Files (*.xlsx *.xls);;All Files (*)",
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

    def update_progress(self, n):
        self.current_progress_value += n
        self.main_window.genJsonProgressBar.setValue(int(self.current_progress_value))

    def update_status(self, message):
        self.main_window.statusbar.showMessage(message)

    def on_json_generator_finished(self):
        self.main_window.startGenBtn.setEnabled(True)
        self.main_window.genJsonProgressBar.setValue(100)

        self.main_window.statusbar.showMessage("Generating process finished.")
        QMessageBox.information(
            self.main_window, "Info", "Generating process finished!"
        )

    def on_json_generator_error(self, err):
        self.main_window.startGenBtn.setEnabled(True)
        self.main_window.statusbar.showMessage(f"Error: {err}")

    def run_gen_json(self):
        # Worker setup
        self.worker = JsonGeneratorWorker(
            self.selected_exp_code,
            self.main_window.selected_gen_json_folder,
            self.main_window.selected_gen_json_files,
        )

        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_status)
        self.worker.finished.connect(self.on_json_generator_finished)
        self.worker.error.connect(self.on_json_generator_error)

        # Reset UI
        self.main_window.startGenBtn.setEnabled(False)
        self.main_window.genJsonProgressBar.setValue(0)
        self.current_progress_value = 0.0

        # Start thread
        self.worker.start()
