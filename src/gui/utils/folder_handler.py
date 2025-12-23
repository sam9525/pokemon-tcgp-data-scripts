from src.gui.config import SELECTED_FOLDER_CONFIGS
from src.services import (
    select_paths,
    update_display,
    remove_selected_paths,
    clear_paths,
)


def select_folder_handler(main_window, tab):
    config = SELECTED_FOLDER_CONFIGS[tab]

    getattr(main_window, config["folder"]).clear()

    if select_paths(
        main_window,
        getattr(main_window, config["folder"]),
        mode="folder",
        multi=False,
    ):
        update_display(
            line_edit=getattr(main_window, config["folder_line"]),
            items=getattr(main_window, config["folder"]),
        )
        main_window.statusbar.showMessage("Added 1 folder.")


def clear_folder_handler(main_window, tab):
    config = SELECTED_FOLDER_CONFIGS[tab]

    if clear_paths(main_window, getattr(main_window, config["folder"])):
        update_display(
            line_edit=getattr(main_window, config["folder_line"]),
            items=getattr(main_window, config["folder"]),
        )
        main_window.statusbar.showMessage("Excel File cleared")


def selected_folders_handler(main_window, tab, mode="folder", multi=False):
    config = SELECTED_FOLDER_CONFIGS[tab]

    added = select_paths(
        main_window,
        getattr(main_window, config["folders"]),
        mode=mode,
        multi=multi,
    )
    update_display(
        list_widget=getattr(main_window, config["folder_list"]),
        line_edit=getattr(main_window, config["folder_line"]),
        count_label=getattr(main_window, config["count_label"]),
        items=getattr(main_window, config["folders"]),
    )
    if added > 0:
        main_window.statusbar.showMessage(
            f"Added {added} folder(s). Total: {len(getattr(main_window, config['folders']))}"
        )


def clear_folders_handler(main_window, tab):
    config = SELECTED_FOLDER_CONFIGS[tab]

    if clear_paths(main_window, getattr(main_window, config["folders"])):
        update_display(
            list_widget=getattr(main_window, config["folder_list"]),
            line_edit=getattr(main_window, config["folder_line"]),
            count_label=getattr(main_window, config["count_label"]),
            items=getattr(main_window, config["folders"]),
        )
        main_window.statusbar.showMessage("All cleared")


def remove_selected_folder_handler(main_window, tab):
    config = SELECTED_FOLDER_CONFIGS[tab]

    removed = remove_selected_paths(
        getattr(main_window, config["folder_list"]),
        getattr(main_window, config["folders"]),
    )
    if removed > 0:
        update_display(
            list_widget=getattr(main_window, config["folder_list"]),
            line_edit=getattr(main_window, config["folder_line"]),
            count_label=getattr(main_window, config["count_label"]),
            items=getattr(main_window, config["folders"]),
        )
        main_window.statusbar.showMessage(f"Removed {removed} folder(s)")
