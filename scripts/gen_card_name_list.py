import os
import sys
import argparse
from dotenv import load_dotenv
import json
from multiprocessing import Pool
from google import genai
from src.services import analyze_card_name
from src.utils import log, update_pbar, safe_load_json, safe_dump_json


# Worker global variable
worker_client = None


def init_worker(api_key):
    global worker_client
    worker_client = genai.Client(api_key=api_key)


def process_image(args):
    image_path, lang = args
    # Use the global worker_client
    return analyze_card_name(image_path, lang, worker_client)


def gen_card_name_list(image_folder, lang, pbar=None, folders_len=1):
    # Initialize Reader
    log("Initializing genai...", pbar)
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")

    log("genai initialized", pbar)

    if not api_key:
        log("Error: GOOGLE_API_KEY not found in environment variables.", pbar)
        return []

    # Load existing data first to filter processed images
    # Handle PyInstaller bundle path
    if getattr(sys, "frozen", False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    json_output_dir = os.path.join(application_path, "json")
    os.makedirs(json_output_dir, exist_ok=True)
    output_file = os.path.join(json_output_dir, "card_names.json")

    existing_data = {}
    if os.path.exists(output_file):
        existing_data = safe_load_json(output_file)

    # Get all image paths
    all_image_paths = [
        os.path.join(image_folder, img) for img in os.listdir(image_folder)
    ]

    images_to_process = []

    for img_path in all_image_paths:
        filename = os.path.basename(img_path)
        try:
            # Get part 5 as key (index 4)
            key = filename.split("_")[4]
        except IndexError:
            key = filename

        # Check if already processed for this language
        if key not in existing_data or lang not in existing_data[key]:
            images_to_process.append(img_path)

    log(
        f"Found {len(images_to_process)} new images to process out of {len(all_image_paths)} total.",
        pbar,
    )
    update_pbar(10 // folders_len, pbar)

    folder_name = (
        os.path.basename(os.path.dirname(image_folder))
        + "/"
        + os.path.basename(image_folder)
    )
    results_list = []

    if images_to_process:
        # Use half of the cpu processes
        processes_count = os.cpu_count() // 2

        log(f"Starting processing {folder_name}...", pbar)

        with Pool(
            processes=processes_count, initializer=init_worker, initargs=(api_key,)
        ) as pool:
            # Create args list for map
            tasks = [(path, lang) for path in images_to_process]

            for result in pool.imap(process_image, tasks):
                results_list.append(result)
                # Calculate progress step
                step = (75) // folders_len / len(images_to_process)
                update_pbar(step, pbar)

        log(f"Finished processing language {folder_name}", pbar)

        # Update data
        for img_path, text in zip(images_to_process, results_list):
            filename = os.path.basename(img_path)
            try:
                key = filename.split("_")[4]
            except IndexError:
                key = filename

            if key not in existing_data:
                existing_data[key] = {}

            existing_data[key][lang] = text

    else:
        log("No new images to process.", pbar)
        update_pbar(75 // folders_len, pbar)

    log("Saving data to json/card_names.json", pbar)
    safe_dump_json(existing_data, output_file)

    update_pbar(15 // folders_len, pbar)

    return results_list


def main():
    parser = argparse.ArgumentParser(description="Generate card name list.")
    parser.add_argument(
        "--image-folder", type=str, required=True, help="Image folder path"
    )
    parser.add_argument("--lang", type=str, required=True, help="Language")

    args = parser.parse_args()

    results_list = gen_card_name_list(args.image_folder, args.lang, folders_len=1)


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    main()
