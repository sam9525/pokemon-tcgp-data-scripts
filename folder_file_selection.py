import os
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QListView,
    QTreeView,
    QMessageBox,
)


def select_folders(window):
    """Open dialog to select multiple folders"""
    # Try the multiple selection method first
    try:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        # Enable multiple selection
        file_view = dialog.findChild(QListView, "listView")
        if file_view:
            file_view.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

        tree_view = dialog.findChild(QTreeView)
        if tree_view:
            tree_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)

        if dialog.exec():
            new_folders = dialog.selectedFiles()

            # Add only unique folders
            added_count = 0
            for folder in new_folders:
                if folder not in window.selected_folders:
                    window.selected_folders.append(folder)
                    added_count += 1

            update_folder_display(window)
            if added_count > 0:
                window.statusbar.showMessage(
                    f"Added {added_count} folder(s). Hold Ctrl/Cmd to select multiple folders.",
                    5000,
                )
    except Exception as e:
        print(f"Error in select_folders: {e}")
        # Fallback to simple single folder selection
        select_single_folder(window)


def select_single_folder(window):
    """Fallback method to select a single folder"""
    folder = QFileDialog.getExistingDirectory(
        None,
        "Select Folder",
        "",
        QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
    )

    if folder:
        if folder not in window.selected_folders:
            window.selected_folders.append(folder)
            update_folder_display(window)
            window.statusbar.showMessage(
                f"Added 1 folder. Click Browse again to add more folders.", 5000
            )
        else:
            window.statusbar.showMessage("Folder already in the list", 3000)


def select_single_file(window):
    """Fallback method to select a single file"""
    file = QFileDialog.getOpenFileName(
        None,
        "Select File",
        "",
        "Excel Files (*.xlsx *.xls);;All Files (*)",
    )

    if file:
        window.selected_file = file[0]
        update_file_display(window)
        filename = os.path.basename(file[0])
        window.statusbar.showMessage(
            f"Added {filename}. Click Browse again to choose another excel file.",
            5000,
        )


def clear_all(window):
    """Clear all selected folders"""
    if window.selected_folders:
        reply = QMessageBox.question(
            window,
            "Clear All",
            "Are you sure you want to clear all selected folders?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            window.selected_folders.clear()
            update_folder_display(window)
            window.statusbar.showMessage("All folders cleared", 3000)
    else:
        window.statusbar.showMessage("No folders to clear", 3000)


def remove_selected(window):
    """Remove selected items from the list"""
    selected_items = window.folderListWidget.selectedItems()

    if not selected_items:
        window.statusbar.showMessage("No items selected to remove", 3000)
        return

    for item in selected_items:
        folder_path = item.text()
        if folder_path in window.selected_folders:
            window.selected_folders.remove(folder_path)

    update_folder_display(window)
    window.statusbar.showMessage(f"Removed {len(selected_items)} folder(s)", 3000)


def show_folder_info(item):
    """Show information about the double-clicked folder"""
    folder_path = item.text()
    QMessageBox.information(None, "Folder Path", f"Full path:\n{folder_path}")


def update_folder_display(window):
    """Update the display with current folder selection"""
    # Update the line edit with semi-colon separated paths
    if window.selected_folders:
        window.folderLineEdit.setText(" ".join(window.selected_folders))
    else:
        window.folderLineEdit.clear()

    # Update the list widget
    window.folderListWidget.clear()
    window.folderListWidget.addItems(window.selected_folders)

    # Update the count label
    count = len(window.selected_folders)
    window.countLabel.setText(f"Total folders: {count}")


def update_file_display(window):
    """Update the display with current file selection"""
    if window.selected_file:
        window.fileLineEdit.setText(window.selected_file)
    else:
        window.fileLineEdit.clear()


def clear_file(window):
    """Clear the selected file"""
    window.selected_file = None
    update_file_display(window)
    window.statusbar.showMessage("Excel File cleared", 3000)


def get_selected_folders(window):
    """Return the list of selected folders"""
    return window.selected_folders.copy()
