import sys
import os
import asyncio
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QListView,
    QTreeView,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from src.gui.tabs import CrawlerTab, ImageRenamerTab, JsonGeneratorTab


class TCGPToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi(os.path.join("src", "gui", "gui.ui"), self)

        # Default expansion
        self.selected_exp_name = "A1_genetic-apex"
        self.selected_exp_code = "A1"

        # Hide pack key group box
        self.packKeyGB.setVisible(False)

        # Initialize selected folders list
        self.selected_rename_folders = []

        # Initialize selected files list
        self.selected_rename_file = []

        # Initialize selected folders list
        self.selected_gen_json_folder = []

        # Initialize selected files list
        self.selected_gen_json_files = []

        # Initialize Tab 1
        self.tab1 = CrawlerTab(self)

        # Initialize Tab 2
        self.tab2 = ImageRenamerTab(self)

        # Initialize Tab 3
        self.tab3 = JsonGeneratorTab(self)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./Pikachu.ico"))
    window = TCGPToolGUI()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
