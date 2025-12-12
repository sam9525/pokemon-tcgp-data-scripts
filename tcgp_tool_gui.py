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
from tabs.crawler import CrawlerTab
from tabs.image_renamer import ImageRenamerTab


class TCGPToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi("gui.ui", self)

        # Hide pack key group box
        self.packKeyGB.setVisible(False)

        # Initialize Tab 1
        self.tab1 = CrawlerTab(self)

        # Initialize Tab 2
        self.tab2 = ImageRenamerTab(self)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./Pikachu.ico"))
    window = TCGPToolGUI()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
