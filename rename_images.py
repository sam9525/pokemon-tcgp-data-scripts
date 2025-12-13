import os
import pandas as pd
import argparse
from pathlib import Path
from messages import log, dry_run_log, update_pbar


def rename_images(folder_path, excel_path, dry_run=True, pbar=None):
    """
    Renames images in the folder based on names in the Excel file.

    Args:
        folder_path (str): Path to the folder containing images.
        excel_path (str): Path to the Excel file.
        dry_run (bool): If True, only prints what would happen.
        pbar (object, optional): Progress bar object with write, update.
    """

    log(f"Processing folder: {folder_path}", pbar)
    log(f"Using Excel file: {excel_path}", pbar)
    log(f"Dry run mode: {'ON' if dry_run else 'OFF'}", pbar)

    log(f"Reading Excel file...", pbar)

    # Read the Excel file
    try:
        if os.path.exists(excel_path):
            file_to_read = excel_path
        elif os.path.exists(os.path.join("./lists/", excel_path)):
            file_to_read = os.path.join("./lists/", excel_path)
        else:
            msg = f"Error: Excel file '{excel_path}' not found."
            log(msg, pbar)
            return

        df = pd.read_excel(file_to_read)
        if "Image Name" not in df.columns:
            msg = "Error: 'Image Name' column not found in Excel file."
            log(msg, pbar)
            return

        # Get list of valid new names, drop NaNs and convert to string just in case
        new_names = df["Image Name"].dropna().astype(str).tolist()

    except Exception as e:
        msg = f"Error reading Excel file: {e}"
        log(msg, pbar)
        return

    # Process the folder
    if isinstance(folder_path, str):
        folder_path = folder_path.strip().strip('"').strip("'")

    folder = Path(folder_path)
    if not folder.exists():
        msg = f"Error: Folder '{folder_path}' does not exist."
        log(msg, pbar)
        return

    count_renamed = 0

    # First, collect all files to process to determine total count
    files_to_process = []
    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue
        # Skip hidden files or temporary files
        if file_path.name.startswith("~$") or file_path.name.startswith("."):
            continue
        files_to_process.append(file_path)

    update_pbar(10, pbar)

    total_files = len(files_to_process)

    # Process all files in the folder
    for i, file_path in enumerate(files_to_process):
        # Update progress
        update_pbar(int(total_files / 90), pbar)

        # Get the old name without extension
        old_name_stem = file_path.stem

        log(f"Processing: {file_path.name}", pbar)

        # Find a match in new_names
        match = None
        for new_name in new_names:
            if old_name_stem in new_name:
                match = new_name
                break

        # If a match is found, rename the file
        if match:
            # Construct new filename
            new_filename = f"{match}_{folder.name}{file_path.suffix}"
            new_file_path = folder / new_filename

            # Skip if the file is already named correctly
            if file_path.name == new_filename:
                continue

            if dry_run:
                dry_run_log(
                    f"Match found: '{file_path.name}' -> '{new_filename}'", pbar
                )
            else:
                log(f"Match found: '{file_path.name}' -> '{new_filename}'", pbar)

            # Rename the file if not in dry run mode
            if not dry_run:
                try:
                    file_path.rename(new_file_path)
                    log(f"  Renamed successfully.", pbar)
                    count_renamed += 1
                except Exception as e:
                    log(f"  Error renaming: {e}", pbar)
            else:
                log("  (Dry run) Would rename.", pbar)
                count_renamed += 1

    msg = f"Total files {'would be ' if dry_run else ''}renamed: {count_renamed}"
    if dry_run:
        dry_run_log(msg, pbar)
    else:
        log(msg, pbar)


def main():
    parser = argparse.ArgumentParser(description="Rename images based on Excel file.")
    parser.add_argument("--folder", nargs="+", help="Folder(s) containing images")
    parser.add_argument("--excel", help="Excel file with names")
    parser.add_argument(
        "--dry-run", action="store_true", help="Enable dry run mode (no changes)"
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Disable dry run mode (execute changes)",
    )
    parser.set_defaults(dry_run=True)

    args = parser.parse_args()

    for folder in args.folder:
        rename_images(folder, args.excel, args.dry_run)


if __name__ == "__main__":
    main()
