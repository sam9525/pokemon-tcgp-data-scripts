from src.gui.config import SELECTED_FOLDER_CONFIGS, SELECTED_FILE_CONFIGS
from src.services import (
    select_paths,
    update_display,
    remove_selected_paths,
    clear_paths,
)


def select_folder_file_handler(main_window, tab, mode, file_filter=""):
    config = (
        mode == "folder" and SELECTED_FOLDER_CONFIGS[tab] or SELECTED_FILE_CONFIGS[tab]
    )

    getattr(
        main_window, mode == "folder" and config["folder"] or config["file"]
    ).clear()

    if select_paths(
        main_window,
        getattr(main_window, mode == "folder" and config["folder"] or config["file"]),
        mode=mode,
        multi=False,
        file_filter=file_filter,
    ):
        update_display(
            line_edit=getattr(
                main_window,
                mode == "folder" and config["folder_line"] or config["file_line"],
            ),
            items=getattr(
                main_window, mode == "folder" and config["folder"] or config["file"]
            ),
        )
        main_window.statusbar.showMessage(
            "Added 1 " + (mode == "folder" and "folder" or "file")
        )


def clear_folder_file_handler(main_window, tab):
    config = SELECTED_FOLDER_CONFIGS[tab]

    if clear_paths(main_window, getattr(main_window, config["folder"])):
        update_display(
            line_edit=getattr(main_window, config["folder_line"]),
            items=getattr(main_window, config["folder"]),
        )
        main_window.statusbar.showMessage("Excel File cleared")


def selected_folders_files_handler(
    main_window, tab, mode="folder", multi=False, file_filter=""
):
    config = (
        mode == "folder" and SELECTED_FOLDER_CONFIGS[tab] or SELECTED_FILE_CONFIGS[tab]
    )

    added = select_paths(
        main_window,
        getattr(main_window, mode == "folder" and config["folders"] or config["files"]),
        mode=mode,
        multi=multi,
        file_filter=file_filter,
    )
    update_display(
        list_widget=getattr(
            main_window,
            mode == "folder" and config["folder_list"] or config["files_list"],
        ),
        line_edit=getattr(
            main_window,
            mode == "folder" and config["folder_line"] or config["files_line"],
        ),
        count_label=getattr(main_window, config["count_label"]),
        items=getattr(
            main_window, mode == "folder" and config["folders"] or config["files"]
        ),
    )
    if added > 0:
        main_window.statusbar.showMessage(
            f"Added {added} folder(s). Total: {len(getattr(main_window, mode == 'folder' and config['folders'] or config['files']))}"
        )


def clear_folders_files_handler(main_window, tab, mode=""):
    config = (
        mode == "folder" and SELECTED_FOLDER_CONFIGS[tab] or SELECTED_FILE_CONFIGS[tab]
    )

    if clear_paths(
        main_window,
        getattr(main_window, mode == "folder" and config["folders"] or config["files"]),
    ):
        update_display(
            list_widget=getattr(
                main_window,
                mode == "folder" and config["folder_list"] or config["files_list"],
            ),
            line_edit=getattr(
                main_window,
                mode == "folder" and config["folder_line"] or config["files_line"],
            ),
            count_label=getattr(main_window, config["count_label"]),
            items=getattr(
                main_window, mode == "folder" and config["folders"] or config["files"]
            ),
        )
        main_window.statusbar.showMessage("All cleared")


def remove_selected_folder_file_handler(main_window, tab):
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
