import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMessageBox,
    QLabel,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
)
from src.config import EXPANSIONS, PACK_KEYS
from scripts import crawler
from src.gui.utils import check_file_exist


class CrawlerWorker(QThread):
    progress = pyqtSignal(float)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, exorp, set_code, pack_code=None, pack_name=None):
        super().__init__()
        self.exorp = exorp
        self.set_code = set_code
        self.pack_code = pack_code
        self.pack_name = pack_name

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
            asyncio.run(
                crawler(
                    self.exorp,
                    self.set_code,
                    self.pack_code,
                    self.pack_name,
                    pbar=pbar,
                )
            )
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class CrawlerTab:
    def __init__(self, main_window):
        self.main_window = main_window
        self.selected_pack_name = "Charizard"
        self.selected_pack_code = "AN001_0020_00_000"
        self.setup_ui()

    def setup_ui(self):
        # Init Expansion code
        for item in EXPANSIONS:
            self.main_window.expComboB.addItem(item["name"], item["code"])

        # Set default expansion
        self.main_window.expComboB.setCurrentIndex(
            self.main_window.expComboB.findData(self.main_window.selected_exp_code)
        )

        self.main_window.expComboB.currentIndexChanged.connect(self.on_combobox_changed)

        # Init pack key combo box
        for item in PACK_KEYS:
            self.main_window.packKeyComboB.addItem(item["name"], item["code"])

        self.main_window.packKeyComboB.currentIndexChanged.connect(
            self.on_combobox_changed
        )

        # Handle start button
        self.main_window.startCrawlingBtn.clicked.connect(self.start_crawling)

    def on_combobox_changed(self):
        combobox = self.main_window.sender()
        current_index = combobox.currentIndex()

        if combobox == self.main_window.expComboB:
            self.main_window.selected_exp_name = combobox.currentText()
            self.main_window.selected_exp_code = combobox.itemData(current_index)

            # Change the expansion combobox in json generator tab
            self.main_window.expansionComboBox.setCurrentIndex(
                self.main_window.expansionComboBox.findData(
                    self.main_window.selected_exp_code
                )
            )
        elif combobox == self.main_window.packKeyComboB:
            self.selected_pack_name = combobox.currentText()
            self.selected_pack_code = combobox.itemData(current_index)

    def update_progress(self, n):
        self.current_progress_value += n
        self.main_window.crawlerProgressBar.setValue(int(self.current_progress_value))

    def log_message(self, msg):
        self.main_window.statusbar.showMessage(msg)

    def crawling_finished(self):
        self.set_controls_enabled(True)
        self.main_window.crawlerProgressBar.setValue(100)
        QMessageBox.information(self.main_window, "Info", "Crawling finished!")

    def crawling_error(self, err):
        self.set_controls_enabled(True)
        QMessageBox.critical(self.main_window, "Error", f"An error occurred: {err}")

    def set_controls_enabled(self, enabled: bool):
        self.main_window.startCrawlingBtn.setEnabled(enabled)
        self.main_window.expRadioBtn.setEnabled(enabled)
        self.main_window.packRadioBtn.setEnabled(enabled)
        self.main_window.expComboB.setEnabled(enabled)
        self.main_window.packKeyComboB.setEnabled(enabled)

    def start_crawling(self):
        self.main_window.crawlerProgressBar.setMaximum(100)
        self.main_window.crawlerProgressBar.setValue(0)
        self.current_progress_value = 0.0

        # Set to disabled
        self.set_controls_enabled(False)

        if self.main_window.expRadioBtn.isChecked():
            # Check if the set code excel file exist
            files_exist = check_file_exist(
                self.main_window, self.main_window.selected_exp_code, "excel"
            )
            if not files_exist:
                self.set_controls_enabled(True)
                return

            self.worker = CrawlerWorker("e", self.main_window.selected_exp_code)

            # Add the excel file path to the renamer tab
            self.main_window.fileLineEdit.setText(
                f"lists/{self.main_window.selected_exp_code}.xlsx"
            )
            self.main_window.selected_rename_file.append(
                f"lists/{self.main_window.selected_exp_code}.xlsx"
            )
        elif self.main_window.packRadioBtn.isChecked():
            # Check if the set code excel file exist
            files_exist = check_file_exist(
                self.main_window,
                self.main_window.selected_exp_code + "_" + self.selected_pack_name,
                "excel",
            )
            if not files_exist:
                self.set_controls_enabled(True)
                return

            self.worker = CrawlerWorker(
                "p",
                self.main_window.selected_exp_code,
                self.selected_pack_code,
                self.selected_pack_name,
            )

        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.crawling_finished)
        self.worker.error.connect(self.crawling_error)
        self.worker.start()
