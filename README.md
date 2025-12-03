# Pokemon tcgp scripts

Build the scripts for my website [Pokemon TCG Pocket Data](https://pokemon-tcg-pocket-data.com/) ([GitHub](https://github.com/sam9525/pokemon-tcg-pocket-data)).

## pokemon_crawler.py

A web crawler to crawl Pokemon cards names from [Pokemon-Zone](https://www.pokemon-zone.com/cards/).

> [!IMPORTANT]  
> The script is design for python below 3.13.

### Requirements

- Python < 3.13
- async_playwright
- pandas

### Arguments

- `--exorp`: Expansion (e) or pack key (p).
- `--set`: Set code to crawl (A1, A2, etc.).
- `--pack-key`: Pack key to crawl (AN001_0020_00_000, etc.).
- `--pack-name`: Pack name to crawl (Charizard, etc.).

### Usage Example

```bash
py -3.11 pokemon_crawler.py \
          --exorp e \
          --set A1 \
          --pack-key AN001_0020_00_000 \
          --pack-name Charizard
```

## rename_images.py

A script that renames all images in a folder based on an Excel file. The script reads the image name from the Excel file and appends the folder name to the end of each image filename.

The Excel files can be obtained using the script pokemon_crawler.py—only need to crawl the expansion.

```bash
PK_10_000110_00 -> cPK_10_000110_00_NAZONOKUSA_C_{folder_name}
```

> [!NOTE]
> The images is expected to be downloaded from [Google Drive](https://drive.google.com/drive/folders/1_2YURmd7dYnCX3VuDLQobLNSJbAeavpt?usp=drive_link)

### Requirements

- pandas

### Arguments

- `--folder` (Multiple): Folder path to rename images, separate by space.
- `--excel-file`: Excel file path.
- `--dry-run` (Default): Enable dry run mode (no changes).
- `--no-dry-run`: Disable dry run mode (execute changes).

### Usage Example

```bash
py rename_images.py \
    --folder "path/to/folder" "path/to/folder" \
    --excel-file "path/to/excel/file"
```

## generate_card_json.py

A script that generates card JSON from images and Excel files. It matches each image to the corresponding Excel file, ensuring no duplicate cards appear within the same pack (though duplicates can exist across different packs). The script uses icon list to determine card type in the specific position (top right) in the image.

### Requirements

- pandas

### Arguments

- `--image-folder`: Folder path to images.
- `--excel-files` (Multiple): Excel file paths, separate by space.
- `--output-name`: Output file name.

### Usage Example

```bash
py generate_card_json.py \
    --image-folder "path/to/image/folder" \
    --excel-files "path/to/excel/file" "path/to/excel/file" \
    --output-name "path/to/output/file"
```
