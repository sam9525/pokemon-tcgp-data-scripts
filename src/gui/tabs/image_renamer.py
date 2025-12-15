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
            self.select_folders_handler
        )
        self.main_window.clearFoldersBtnInTab2.clicked.connect(
            self.clear_folders_handler
        )
        self.main_window.removeSelectedBtnInTab2.clicked.connect(
            self.remove_selected_handler
        )

        # Select file
        self.main_window.browseFileBtnInTab2.clicked.connect(self.select_file_handler)
        self.main_window.clearFileBtnInTab2.clicked.connect(self.clear_file_handler)
        self.main_window.startRenameBtn.clicked.connect(
            lambda: self.run_renamer(dry_run=None)
        )

    def select_folders_handler(self):
        added = select_paths(
            self.main_window,
            self.main_window.selected_rename_folders,
            mode="folder",
            multi=True,
        )
        update_display(
            list_widget=self.main_window.folderListWidget,
            line_edit=self.main_window.folderLineEdit,
            count_label=self.main_window.countLabel,
            items=self.main_window.selected_rename_folders,
        )
        if added > 0:
            self.main_window.statusbar.showMessage(
                f"Added {added} folder(s). Total: {len(self.main_window.selected_rename_folders)}"
            )

    def clear_folders_handler(self):
        if clear_paths(self.main_window, self.main_window.selected_rename_folders):
            update_display(
                list_widget=self.main_window.folderListWidget,
                line_edit=self.main_window.folderLineEdit,
                count_label=self.main_window.countLabel,
                items=self.main_window.selected_rename_folders,
            )
            self.main_window.statusbar.showMessage("All folders cleared")

    def remove_selected_handler(self):
        removed = remove_selected_paths(
            self.main_window.folderListWidget, self.main_window.selected_rename_folders
        )
        if removed > 0:
            update_display(
                list_widget=self.main_window.folderListWidget,
                line_edit=self.main_window.folderLineEdit,
                count_label=self.main_window.countLabel,
                items=self.main_window.selected_rename_folders,
            )
            self.main_window.statusbar.showMessage(f"Removed {removed} folder(s)")

    def select_file_handler(self):
        self.main_window.selected_rename_file.clear()

        select_paths(
            self.main_window,
            self.main_window.selected_rename_file,
            mode="file",
            multi=False,
            file_filter=f"Excel Files ({';'.join(SUPPORTED_EXCEL_FORMATS)});;All Files (*)",
        )

        update_display(
            line_edit=self.main_window.fileLineEdit,
            items=self.main_window.selected_rename_file,
        )
        if self.main_window.selected_rename_file:
            self.main_window.statusbar.showMessage(
                f"Selected file: {self.main_window.selected_rename_file[0]}"
            )

    def clear_file_handler(self):
        if clear_paths(
            self.main_window, self.main_window.selected_rename_file, confirm=False
        ):
            update_display(
                line_edit=self.main_window.fileLineEdit,
                items=self.main_window.selected_rename_file,
            )
            self.main_window.statusbar.showMessage("Excel File cleared")

    def update_progress(self, n):
        self.current_progress_value += n
        self.main_window.renamerProgressBar.setValue(int(self.current_progress_value))

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
        self.main_window.renamerProgressBar.setValue(100)

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

        excel_path = self.main_window.selected_rename_file[0]

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
        self.current_progress_value = 0.0

        # Start thread
        self.worker.start()
