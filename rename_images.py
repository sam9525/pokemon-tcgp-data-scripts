import pandas as pd
import argparse
from pathlib import Path


def rename_images(folder_path, excel_path, dry_run=True):
    """
    Renames images in the folder based on names in the Excel file.

    Args:
        folder_path (str): Path to the folder containing images.
        excel_path (str): Path to the Excel file.
        dry_run (bool): If True, only prints what would happen.
    """
    print(f"Processing folder: {folder_path}")
    print(f"Using Excel file: {excel_path}")
    print(f"Dry run mode: {'ON' if dry_run else 'OFF'}")

    # Read the Excel file
    try:
        df = pd.read_excel(excel_path)
        if "Image Name" not in df.columns:
            print("Error: 'Image Name' column not found in Excel file.")
            return

        # Get list of valid new names, drop NaNs and convert to string just in case
        new_names = df["Image Name"].dropna().astype(str).tolist()

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Process the folder
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    count_renamed = 0

    # Process all files in the folder
    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue

        # Skip hidden files or temporary files if needed, but for now process all files
        if file_path.name.startswith("~$") or file_path.name.startswith("."):
            continue

        # Get the old name without extension
        old_name_stem = file_path.stem

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

            print(f"Match found: '{file_path.name}' -> '{new_filename}'")

            # Rename the file if not in dry run mode
            if not dry_run:
                try:
                    file_path.rename(new_file_path)
                    print(f"  Renamed successfully.")
                    count_renamed += 1
                except Exception as e:
                    print(f"  Error renaming: {e}")
            else:
                print("  (Dry run) Would rename.")
                count_renamed += 1

    print(f"\nTotal files {'would be ' if dry_run else ''}renamed: {count_renamed}")


if __name__ == "__main__":
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
