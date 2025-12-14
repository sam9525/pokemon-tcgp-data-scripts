import os
from PyQt6.QtWidgets import (
    QFileDialog,
    QListView,
    QTreeView,
    QMessageBox,
)


def select_paths(
    parent, current_paths, mode="folder", multi=True, file_filter="All Files (*)"
):
    """
    Open dialog to select multiple folders or files.
    Returns True if paths were added, False otherwise.

    Args:
        parent: The parent widget.
        current_paths: List of current paths.
        mode: "folder" or "file".
        multi: Whether to allow multiple selection.
        file_filter: File filter for file selection.
    Returns:
        True if paths were added, False otherwise.
    """
    added_count = 0
    new_paths = []

    if mode == "folder":
        if multi:
            # Try the multiple selection method first
            try:
                dialog = QFileDialog()
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
                dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

                # Enable multiple selection
                file_view = dialog.findChild(QListView, "listView")
                if file_view:
                    file_view.setSelectionMode(
                        QListView.SelectionMode.ExtendedSelection
                    )

                tree_view = dialog.findChild(QTreeView)
                if tree_view:
                    tree_view.setSelectionMode(
                        QTreeView.SelectionMode.ExtendedSelection
                    )

                if dialog.exec():
                    new_paths = dialog.selectedFiles()
            except Exception as e:
                print(f"Error in select_paths (multi-folder): {e}")
                return select_paths(parent, current_paths, mode="folder", multi=False)
        else:
            folder = QFileDialog.getExistingDirectory(
                parent,
                "Select Folder",
                "",
                QFileDialog.Option.ShowDirsOnly
                | QFileDialog.Option.DontResolveSymlinks,
            )
            if folder:
                new_paths = [folder]

    elif mode == "file":
        if multi:
            files, _ = QFileDialog.getOpenFileNames(
                parent,
                "Select Files",
                "",
                file_filter,
            )
            if files:
                new_paths = files
        else:
            file, _ = QFileDialog.getOpenFileName(
                parent,
                "Select File",
                "",
                file_filter,
            )
            if file:
                new_paths = [file]

    # Process new paths
    for path in new_paths:
        if path not in current_paths:
            current_paths.append(path)
            added_count += 1

    return added_count


def update_display(list_widget=None, line_edit=None, count_label=None, items=None):
    """
    Update the display with current selection

    Args:
        list_widget: The list widget to update.
        line_edit: The line edit to update.
        count_label: The count label to update.
        items: The items to display.
    """
    if items is None:
        items = []

    # Update the line edit with semi-colon separated paths
    if line_edit is not None:
        if items:
            line_edit.setText(" ".join(items))
        else:
            line_edit.clear()

    # Update the list widget
    if list_widget is not None:
        list_widget.clear()
        list_widget.addItems(items)

    # Update the count label
    if count_label is not None:
        count = len(items)
        count_label.setText(f"Total items: {count}")


def remove_selected_paths(list_widget, current_paths):
    """
    Remove selected items from the list and return number of removed items

    Args:
        list_widget: The list widget to update.
        current_paths: List of current paths.

    Returns:
        Number of removed items.
    """
    if list_widget is None or not current_paths:
        return 0

    selected_items = list_widget.selectedItems()
    if not selected_items:
        return 0

    removed_count = 0
    for item in selected_items:
        path = item.text()
        if path in current_paths:
            current_paths.remove(path)
            removed_count += 1

    return removed_count


def clear_paths(parent, current_paths, confirm=True):
    """
    Clear all selected paths. Returns True if cleared, False if cancelled.

    Args:
        parent: The parent widget.
        current_paths: List of current paths.
        confirm: Whether to confirm the action.

    Returns:
        True if cleared, False if cancelled.
    """
    if not current_paths:
        return False

    if confirm:
        reply = QMessageBox.question(
            parent,
            "Clear All",
            "Are you sure you want to clear all selected items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return False

    current_paths.clear()
    return True
