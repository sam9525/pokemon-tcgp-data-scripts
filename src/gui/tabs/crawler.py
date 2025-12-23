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
from src.config import EXPANSIONS_SHORT, EXPANSIONS, PACK_KEYS, MATCH_EXP_AND_PACK
from scripts import crawler
from src.gui.utils import (
    check_file_exist,
    update_progress,
    update_status,
    on_finished,
    on_error,
    set_controls_enabled,
)


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
        for item in EXPANSIONS_SHORT:
            self.main_window.expComboB.addItem(item["name"], item["code"])

        # Connect radio buttons
        self.main_window.expRadioBtn.toggled.connect(self.on_radio_button_changed)

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

    def on_radio_button_changed(self):
        # Clear existing items before adding new ones
        self.main_window.expComboB.blockSignals(True)
        self.main_window.expComboB.clear()

        if self.main_window.expRadioBtn.isChecked():
            for item in EXPANSIONS_SHORT:
                self.main_window.expComboB.addItem(item["name"], item["code"])
        else:
            for item in EXPANSIONS:
                self.main_window.expComboB.addItem(item["name"], item["code"])

        self.main_window.expComboB.blockSignals(False)

        # Set default index
        if self.main_window.expComboB.count() > 0:
            self.main_window.expComboB.setCurrentIndex(0)

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

    def check_exp_and_pack_key(self):
        selected_exp_code = self.main_window.expComboB.itemData(
            self.main_window.expComboB.currentIndex()
        )
        selected_pack_code = self.main_window.packKeyComboB.itemData(
            self.main_window.packKeyComboB.currentIndex()
        )

        is_match = False
        if selected_exp_code in MATCH_EXP_AND_PACK:
            expected_pack = MATCH_EXP_AND_PACK[selected_exp_code]
            if isinstance(expected_pack, list):
                if selected_pack_code in expected_pack:
                    is_match = True
            elif expected_pack == selected_pack_code:
                is_match = True

        if not is_match:
            QMessageBox.warning(
                self.main_window,
                "Warning",
                f"The Expansion and Pack Key are not matched!",
            )
            return False

        return True

    def start_crawling(self):
        self.main_window.crawlerProgressBar.setMaximum(100)
        self.main_window.crawlerProgressBar.setValue(0)

        # Check the Expansion and Pack Key are matched
        if not self.check_exp_and_pack_key():
            self.main_window.statusbar.showMessage(
                "The Expansion and Pack Key are not matched!"
            )
            return

        # Set to disabled
        set_controls_enabled(self.main_window, "crawler", False)

        if self.main_window.expRadioBtn.isChecked():
            # Check if the set code excel file exist
            files_exist = check_file_exist(
                self.main_window, self.main_window.selected_exp_code, "excel"
            )
            if not files_exist:
                set_controls_enabled(self.main_window, "crawler", True)
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
                set_controls_enabled(self.main_window, "crawler", True)
                return

            self.worker = CrawlerWorker(
                "p",
                self.main_window.selected_exp_code,
                self.selected_pack_code,
                self.selected_pack_name,
            )

        self.worker.progress.connect(
            lambda n: update_progress(self.main_window, n, "crawlerProgressBar")
        )
        self.worker.log.connect(lambda msg: update_status(self.main_window, msg))
        self.worker.finished.connect(
            lambda: on_finished(self.main_window, tab="crawler")
        )
        self.worker.error.connect(lambda: on_error(self.main_window, tab="crawler"))
        self.worker.start()
