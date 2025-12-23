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
from src.gui.utils import (
    update_progress,
    update_status,
    on_finished,
    on_error,
    set_controls_enabled,
    selected_folders_handler,
    clear_folders_handler,
    remove_selected_folder_handler,
)


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
            lambda: selected_folders_handler(
                self.main_window, "gen card name", mode="folder", multi=True
            )
        )
        self.main_window.clearFoldersBtnInTab4.clicked.connect(
            lambda: clear_folders_handler(self.main_window, "gen card name")
        )
        self.main_window.removeSelectedBtnInTab4.clicked.connect(
            lambda: remove_selected_folder_handler(self.main_window, "gen card name")
        )

        # Start generating
        self.main_window.startGenCardNameBtn.clicked.connect(
            lambda: self.run_gen_card_name()
        )

    def run_gen_card_name(self):
        set_controls_enabled(self.main_window, "gen card name", False)

        self.worker = GenCardNameWorker(self.main_window.selected_gen_card_name_folder)

        # Connect signals
        self.worker.progress.connect(
            lambda n: update_progress(self.main_window, n, "cardNameProgressBar")
        )
        self.worker.log.connect(lambda msg: update_status(self.main_window, msg))
        self.worker.finished.connect(
            lambda: on_finished(self.main_window, tab="gen card name")
        )
        self.worker.error.connect(
            lambda: on_error(self.main_window, tab="gen card name")
        )

        # Reset UI
        self.main_window.cardNameProgressBar.setValue(0)
        self.current_progress_value = 0.0

        # Start thread
        self.worker.start()
