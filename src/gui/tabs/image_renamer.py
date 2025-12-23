import os
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton
from src.services import (
    select_paths,
    update_display,
    remove_selected_paths,
    clear_paths,
)

from scripts import rename_images
from src.utils import dry_run_log
from src.config import SUPPORTED_EXCEL_FORMATS
from src.utils import extract_folder_prefix, extract_excel_prefix
from src.gui.utils import (
    update_progress,
    update_status,
    on_finished,
    on_error,
    set_controls_enabled,
    select_folder_file_handler,
    clear_folder_file_handler,
    selected_folders_files_handler,
    clear_folders_files_handler,
    remove_selected_folder_file_handler,
)


class RenamerWorker(QThread):
    progress = pyqtSignal(float)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, folders, excel_path, dry_run):
        super().__init__()
        self.folders = folders
        self.excel_path = excel_path
        self.dry_run = dry_run
        self.dry_run_log = []

    def run(self):
        class SignalProgressBar:
            def __init__(self, worker):
                self.worker = worker

            def update(self, n=1):
                self.worker.progress.emit(n)

            def write(self, msg):
                self.worker.log.emit(msg)

            def write_dry_run_log(self, msg):
                self.worker.dry_run_log.append(msg)

        pbar = SignalProgressBar(self)

        try:
            for folder in self.folders:
                pbar.write(f"Starting process for folder: {folder}")
                rename_images(
                    folder,
                    self.excel_path,
                    self.dry_run,
                    pbar=pbar,
                )
        except Exception as e:
            self.error.emit(str(e))
        finally:

            self.finished.emit()


class ImageRenamerTab:

    def __init__(self, main_window):
        self.main_window = main_window

        # Select folders
        self.main_window.browseFolderBtnInTab2.clicked.connect(
            lambda: selected_folders_files_handler(
                self.main_window, "image renamer", mode="folder", multi=True
            )
        )
        self.main_window.clearFoldersBtnInTab2.clicked.connect(
            lambda: clear_folders_files_handler(
                self.main_window, "image renamer", mode="folder"
            )
        )
        self.main_window.removeSelectedBtnInTab2.clicked.connect(
            lambda: remove_selected_folder_file_handler(
                self.main_window, "image renamer"
            )
        )

        # Select file
        self.main_window.browseFileBtnInTab2.clicked.connect(
            lambda: select_folder_file_handler(
                self.main_window,
                "image renamer",
                mode="file",
                file_filter=f"Excel Files ({';'.join(SUPPORTED_EXCEL_FORMATS)});;All Files (*)",
            )
        )
        self.main_window.clearFileBtnInTab2.clicked.connect(
            lambda: clear_folder_file_handler(self.main_window, "image renamer")
        )
        self.main_window.startRenameBtn.clicked.connect(
            lambda: self.run_renamer(dry_run=None)
        )

    def check_folder_excel_match(self, folders, excel_path):
        # Check if the folder name and excel file name match
        # Match the name before _
        unmatched_paths = []

        # Check excel file name
        excel_name = os.path.basename(excel_path)
        excel_prefix = extract_excel_prefix(excel_path, separator="_")

        # Check folder name
        for folder in folders:
            folder_prefix = extract_folder_prefix(folder)

            if folder_prefix != excel_prefix:
                unmatched_paths.append(folder)

        if unmatched_paths:
            set_controls_enabled(self.main_window, "image renamer", True)
            unmatched_list_str = "\n".join(unmatched_paths)
            QMessageBox.warning(
                self.main_window,
                "Input Error",
                f"The following folders do not match the Excel file '{excel_name}':\n{unmatched_list_str}",
            )
            return False

        return True

    def run_renamer(self, dry_run=None):
        if not self.main_window.selected_rename_folders:
            set_controls_enabled(self.main_window, "image renamer", True)
            QMessageBox.warning(self.main_window, "Input Error", "No folders selected.")
            return

        if not self.main_window.selected_rename_file:
            set_controls_enabled(self.main_window, "image renamer", True)
            QMessageBox.warning(
                self.main_window, "Input Error", "No Excel file selected."
            )
            return

        folders = self.main_window.selected_rename_folders
        excel_path = self.main_window.selected_rename_file[0]

        # Check if the folder name and excel file name match
        if not self.check_folder_excel_match(folders, excel_path):
            self.main_window.statusbar.showMessage(
                "Folder name and excel file name do not match."
            )
            return

        # Set to disabled
        set_controls_enabled(self.main_window, "image renamer", False)

        if dry_run is not None:
            isDryRun = dry_run
        else:
            isDryRun = self.main_window.dryRunCB.isChecked()

        # Worker setup
        self.worker = RenamerWorker(folders, excel_path, isDryRun)

        # Connect signals
        self.worker.progress.connect(
            lambda n: update_progress(self.main_window, n, "renamerProgressBar")
        )
        self.worker.log.connect(lambda msg: update_status(self.main_window, msg))
        self.worker.finished.connect(
            lambda: on_finished(
                self.main_window,
                tab="image renamer",
                dry_run=self.worker.dry_run,
                dry_run_log=self.worker.dry_run_log,
                on_confirm=lambda: self.run_renamer(dry_run=False),
            )
        )
        self.worker.error.connect(
            lambda: on_error(self.main_window, tab="image renamer")
        )

        # Reset UI
        self.main_window.renamerProgressBar.setValue(0)
        self.current_progress_value = 0.0

        # Set the first folder path to the folder line in json generator tab
        self.main_window.folderLineEditInTab3.setText(
            self.main_window.selected_rename_folders[0]
        )

        # Start thread
        self.worker.start()
