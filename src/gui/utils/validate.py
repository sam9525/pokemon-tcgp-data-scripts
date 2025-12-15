import os
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


def check_file_exist(main_window, selected_exp_code, mode):
    if mode == "excel" and os.path.exists(f"lists/{selected_exp_code}.xlsx"):
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Do you want to continue?")
        dialog.setFixedSize(300, 100)

        # Message
        layout = QVBoxLayout(dialog)
        message_label = QLabel("Set code excel file does exist!", dialog)
        layout.addWidget(message_label)

        # Buttons
        confirm_btn = QPushButton("Yes", dialog)
        confirm_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("No", dialog)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Accepted:
            return True
        else:
            return False

    elif (
        mode == "json"
        and os.path.exists(f"json/{selected_exp_code}.json")
        and os.path.exists(f"json/{selected_exp_code}_duplicates.json")
        and os.path.exists(f"json/{selected_exp_code}_special.json")
    ):
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Do you want to continue?")
        dialog.setFixedSize(300, 100)

        # Message
        layout = QVBoxLayout(dialog)
        message_label = QLabel("JSON files do exist!", dialog)
        layout.addWidget(message_label)

        # Buttons
        confirm_btn = QPushButton("Yes", dialog)
        confirm_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("No", dialog)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Accepted:
            return True
        else:
            return False

    return False
