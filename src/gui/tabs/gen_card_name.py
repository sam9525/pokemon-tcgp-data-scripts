from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from src.config import LANGUAGES
from src.utils import extract_folder
from src.services import (
    select_paths,
    update_display,
    remove_selected_paths,
    clear_paths,
)
from scripts import gen_card_name_list


class GenCardNameWorker(QThread):
    progress = pyqtSignal(float)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, folders):
        super().__init__()
        self.folders = folders

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
            for folder in self.folders:
                lang_code = extract_folder(folder)
                gen_card_name_list(
                    folder, lang_code, pbar, folders_len=len(self.folders)
                )

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class GenCardNameTab:
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        # Select folder
        self.main_window.browseFolderBtnInTab4.clicked.connect(
            self.select_folders_handler
        )
        self.main_window.clearFoldersBtnInTab4.clicked.connect(
            self.clear_folder_handler
        )
        self.main_window.removeSelectedBtnInTab4.clicked.connect(
            self.remove_selected_handler
        )

        # Start generating
        self.main_window.startGenCardNameBtn.clicked.connect(
            lambda: self.run_gen_card_name()
        )

    def select_folders_handler(self):
        added = select_paths(
            self.main_window,
            self.main_window.selected_gen_card_name_folder,
            mode="folder",
            multi=True,
        )
        update_display(
            list_widget=self.main_window.folderListInTab4,
            line_edit=self.main_window.folderLineEditInTab4,
            count_label=self.main_window.countLabelInTab4,
            items=self.main_window.selected_gen_card_name_folder,
        )
        if added > 0:
            self.main_window.statusbar.showMessage(
                f"Added {added} folder(s). Total: {len(self.main_window.selected_gen_card_name_folder)}"
            )

    def clear_folder_handler(self):
        if clear_paths(
            self.main_window,
            self.main_window.selected_gen_card_name_folder,
            confirm=False,
        ):
            update_display(
                line_edit=self.main_window.folderLineEditInTab4,
                items=self.main_window.selected_gen_card_name_folder,
            )
            self.main_window.statusbar.showMessage("Excel File cleared")

    def remove_selected_handler(self):
        removed = remove_selected_paths(
            self.main_window.folderListInTab4,
            self.main_window.selected_gen_card_name_folder,
        )
        if removed > 0:
            update_display(
                list_widget=self.main_window.folderListInTab4,
                line_edit=self.main_window.folderLineEditInTab4,
                count_label=self.main_window.countLabelInTab4,
                items=self.main_window.selected_gen_card_name_folder,
            )
            self.main_window.statusbar.showMessage(f"Removed {removed} folder(s)")

    def lang_changed_handler(self):
        combobox = self.main_window.sender()
        currentIndex = combobox.currentIndex()

        self.main_window.selected_lang_name = combobox.currentText()
        self.main_window.selected_lang_code = combobox.itemData(currentIndex)

    def update_progress(self, n):
        self.current_progress_value += n
        self.main_window.cardNameProgressBar.setValue(int(self.current_progress_value))

    def update_status(self, message):
        self.main_window.statusbar.showMessage(message)

    def on_finished(self):
        self.set_controls_enabled(True)
        self.main_window.cardNameProgressBar.setValue(100)

        self.main_window.statusbar.showMessage("Generating process finished.")
        QMessageBox.information(
            self.main_window, "Info", "Generating process finished!"
        )

    def on_error(self, error):
        self.set_controls_enabled(True)
        self.main_window.statusbar.showMessage(error)
        QMessageBox.critical(self.main_window, "Error", error)

    def set_controls_enabled(self, enabled: bool):
        self.main_window.browseFolderBtnInTab4.setEnabled(enabled)
        self.main_window.clearFoldersBtnInTab4.setEnabled(enabled)
        self.main_window.removeSelectedBtnInTab4.setEnabled(enabled)
        self.main_window.startGenCardNameBtn.setEnabled(enabled)

    def run_gen_card_name(self):
        self.set_controls_enabled(False)

        self.worker = GenCardNameWorker(self.main_window.selected_gen_card_name_folder)

        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        # Reset UI
        self.main_window.cardNameProgressBar.setValue(0)
        self.current_progress_value = 0.0

        # Start thread
        self.worker.start()
