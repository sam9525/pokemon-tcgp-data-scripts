from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton
from folder_file_selection import (
    select_folders,
    select_single_folder,
    select_single_file,
    clear_all,
    remove_selected,
    show_folder_info,
    update_folder_display,
    update_file_display,
    get_selected_folders,
    clear_file,
)

from rename_images import rename_images
from messages import dry_run_log


class RenamerWorker(QThread):
    progress = pyqtSignal(int)
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
            lambda: select_folders(self.main_window)
        )
        self.main_window.clearFoldersBtnInTab2.clicked.connect(
            lambda: clear_all(self.main_window)
        )
        self.main_window.removeSelectedBtnInTab2.clicked.connect(
            lambda: remove_selected(self.main_window)
        )
        self.main_window.folderListWidget.itemDoubleClicked.connect(
            lambda: show_folder_info(self.main_window)
        )

        # Select file
        self.main_window.browseFileBtnInTab2.clicked.connect(
            lambda: select_single_file(self.main_window)
        )
        self.main_window.clearFileBtnInTab2.clicked.connect(
            lambda: clear_file(self.main_window)
        )
        self.main_window.startRenameBtn.clicked.connect(
            lambda: self.run_renamer(dry_run=None)
        )

    def update_progress(self, n):
        self.main_window.renamerProgressBar.setValue(
            self.main_window.renamerProgressBar.value() + n
        )

    def update_status(self, message):
        self.main_window.statusbar.showMessage(message)

    def show_dry_run_log_dialog(self, messages):
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Dry Run Log")
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        text_edit.setText("\n".join(messages))
        layout.addWidget(text_edit)

        # Confirm button
        confirm_button = QPushButton("Confirm", dialog)

        def on_confirm():
            dialog.accept()
            self.run_renamer(dry_run=False)

        confirm_button.clicked.connect(on_confirm)
        layout.addWidget(confirm_button)

        # Close button
        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(close_button)

        dialog.exec()

    def on_renamer_finished(self):
        self.main_window.startRenameBtn.setEnabled(True)

        if self.worker.dry_run:
            self.main_window.statusbar.showMessage("Dry run completed.")
            self.show_dry_run_log_dialog(self.worker.dry_run_log)
        else:
            self.main_window.statusbar.showMessage("Renaming process finished.")
            QMessageBox.information(
                self.main_window, "Info", "Renaming process finished!"
            )

    def on_renamer_error(self, err):
        self.main_window.startRenameBtn.setEnabled(True)
        self.main_window.statusbar.showMessage(f"Error: {err}")

    def run_renamer(self, dry_run=None):
        if not self.main_window.selected_rename_folders:
            self.main_window.statusbar.showMessage("No folders selected.")
            return

        if not self.main_window.selected_rename_file:
            self.main_window.statusbar.showMessage("No Excel file selected.")
            return

        if dry_run is not None:
            isDryRun = dry_run
        else:
            isDryRun = self.main_window.dryRunCB.isChecked()
        folders = self.main_window.selected_rename_folders
        excel_path = self.main_window.selected_rename_file

        # Worker setup
        self.worker = RenamerWorker(folders, excel_path, isDryRun)

        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_status)
        self.worker.finished.connect(self.on_renamer_finished)
        self.worker.error.connect(self.on_renamer_error)

        # Reset UI
        self.main_window.startRenameBtn.setEnabled(False)
        self.main_window.renamerProgressBar.setValue(0)

        # Start thread
        self.worker.start()
