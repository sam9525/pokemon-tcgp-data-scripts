FINISH_CONFIGS = {
    "crawler": ("crawlerProgressBar", "Crawling finished!"),
    "image renamer": ("renamerProgressBar", "Renaming process finished!"),
    "json generator": ("genJsonProgressBar", "Generating process finished!"),
    "gen card name": ("genCardNameProgressBar", "Generating process finished!"),
}


CONTROLS_ENABLED = {
    "crawler": [
        "startCrawlingBtn",
        "expRadioBtn",
        "packRadioBtn",
        "expComboB",
        "packKeyComboB",
    ],
    "image renamer": [
        "browseFolderBtnInTab2",
        "clearFoldersBtnInTab2",
        "removeSelectedBtnInTab2",
        "browseFileBtnInTab2",
        "clearFileBtnInTab2",
        "startRenameBtn",
    ],
    "json generator": [
        "expansionComboBox",
        "browseFolderBtnInTab3",
        "clearBtnInTab3",
        "browseExcelBtnInTab3",
        "clearExcelBtnInTab3",
        "removeSelectedBtnInTab3",
        "startGenBtn",
    ],
    "gen card name": [
        "browseFolderBtnInTab4",
        "clearFoldersBtnInTab4",
        "removeSelectedBtnInTab4",
        "startGenCardNameBtn",
    ],
}

SELECTED_FOLDER_CONFIGS = {
    "image renamer": {
        "folders": "selected_rename_folders",
        "folder_list": "folderListWidget",
        "folder_line": "folderLineEdit",
        "count_label": "countLabel",
    },
    "json generator": {
        "folder": "selected_gen_json_folder",
        "folder_line": "folderLineEditInTab3",
    },
    "gen card name": {
        "folders": "selected_gen_card_name_folder",
        "folder_list": "folderListInTab4",
        "folder_line": "folderLineEditInTab4",
        "count_label": "countLabelInTab4",
    },
}
