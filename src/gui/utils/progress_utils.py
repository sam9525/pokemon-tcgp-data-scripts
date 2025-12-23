from src.gui.config import FINISH_CONFIGS, CONTROLS_ENABLED
from PyQt6.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
)


def update_progress(
    main_window, progress: float, progress_bar_name: str = "progressBar"
):
    """
    Updates the progress bar of the main window.
    Args:
        main_window: The main window object.
        progress: The progress to add.
        progress_bar_name: The name of the progress bar attribute.
    Returns:
        The updated progress.
    """
    progress_bar = getattr(main_window, progress_bar_name)
    cur_progress = getattr(progress_bar, "_float_progress", 0.0)

    cur_progress += progress
    setattr(progress_bar, "_float_progress", cur_progress)
    progress_bar.setValue(int(cur_progress))

    return cur_progress


def update_status(main_window, message: str):
    """
    Updates the status bar message of the main window.
    Args:
        main_window: The main window object.
        message: The message to show.
    """
    main_window.statusbar.showMessage(message)


def on_finished(main_window, tab: str, dry_run=False, dry_run_log="", on_confirm=None):
    """
    Updates the progress bar of the main window.
    Args:
        main_window: The main window object.
        tab: The tab to update.
        dry_run: Whether the operation is a dry run.
        dry_run_log: The dry run log.
        on_confirm: The callback to run when the user confirms the dry run.
    """
    pb_attr, msg = FINISH_CONFIGS[tab]

    set_controls_enabled(main_window, tab, True)
    getattr(main_window, pb_attr).setValue(100)
    if dry_run:
        main_window.statusbar.showMessage(msg)
        show_dry_run_log_dialog(main_window, dry_run_log, on_confirm)
    else:
        QMessageBox.information(main_window, "Info", msg)


def on_error(main_window, tab, error: str):
    set_controls_enabled(main_window, tab, True)
    QMessageBox.critical(main_window, "Error", error)


def set_controls_enabled(main_window, tab, enabled: bool):
    """
    Set the enabled state of the controls in the specified tab.
    Args:
        main_window: The main window object.
        tab: The tab to update.
        enabled: The enabled state to set.
    """
    for control in CONTROLS_ENABLED[tab]:
        getattr(main_window, control).setEnabled(enabled)


def show_dry_run_log_dialog(main_window, messages, on_confirm_callback=None):
    """
    Show a dialog with the dry run log.
    Args:
        main_window: The main window object.
        messages: The messages to show.
        on_confirm_callback: The callback to run when the user confirms the dry run.
    """
    dialog = QDialog(main_window)
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
        if on_confirm_callback:
            on_confirm_callback()

    confirm_button.clicked.connect(on_confirm)
    layout.addWidget(confirm_button)

    # Close button
    close_button = QPushButton("Close", dialog)
    close_button.clicked.connect(dialog.reject)
    layout.addWidget(close_button)

    dialog.exec()
