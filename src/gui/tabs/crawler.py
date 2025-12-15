import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from src.config import EXPANSIONS, PACK_KEYS
from scripts import crawler


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
        self.selected_exp_name = "A1_genetic-apex"
        self.selected_exp_code = "A1"
        self.selected_pack_name = "Charizard"
        self.selected_pack_code = "AN001_0020_00_000"
        self.setup_ui()

    def setup_ui(self):
        # Init Expansion code
        for item in EXPANSIONS:
            self.main_window.expComboB.addItem(item["name"], item["code"])

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
            self.selected_exp_name = combobox.currentText()
            self.selected_exp_code = combobox.itemData(current_index)
        elif combobox == self.main_window.packKeyComboB:
            self.selected_pack_name = combobox.currentText()
            self.selected_pack_code = combobox.itemData(current_index)

    def update_progress(self, n):
        self.current_progress_value += n
        self.main_window.crawlerProgressBar.setValue(int(self.current_progress_value))

    def log_message(self, msg):
        self.main_window.statusbar.showMessage(msg)

    def crawling_finished(self):
        self.main_window.startCrawlingBtn.setEnabled(True)
        self.main_window.crawlerProgressBar.setValue(100)
        QMessageBox.information(self.main_window, "Info", "Crawling finished!")

    def crawling_error(self, err):
        self.main_window.startCrawlingBtn.setEnabled(True)
        QMessageBox.critical(self.main_window, "Error", f"An error occurred: {err}")

    def start_crawling(self):
        self.main_window.crawlerProgressBar.setMaximum(100)
        self.main_window.crawlerProgressBar.setValue(0)
        self.current_progress_value = 0.0
        self.main_window.startCrawlingBtn.setEnabled(False)

        if self.main_window.expRadioBtn.isChecked():
            self.worker = CrawlerWorker("e", self.selected_exp_code)
        elif self.main_window.packRadioBtn.isChecked():
            self.worker = CrawlerWorker(
                "p",
                self.selected_exp_code,
                self.selected_pack_code,
                self.selected_pack_name,
            )

        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.crawling_finished)
        self.worker.error.connect(self.crawling_error)
        self.worker.start()
