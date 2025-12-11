import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
import argparse


async def crawler(exorp, set, pack_key, pack_name):
    """
    Crawl Pokemon cards names from Pokemon-Zone.
    Args:
        exorp (str): Expansion (e) or pack key (p).
        set (str): Set code to crawl (A1, A2, etc.).
        pack_key (str): Pack key to crawl (AN001_0020_00_000, etc.).
        pack_name (str): Pack name to crawl (Charizard, etc.).
    """
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)

        # Add user agent and viewport
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        # Check if we are crawling an expansion or a pack
        if exorp == "e":
            url = f"https://www.pokemon-zone.com/cards/?expansions={set}"
        elif exorp == "p":
            url = f"https://www.pokemon-zone.com/cards/?pack_keys={pack_key}"

        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded")

        print("Waiting for page to load...")
        await page.wait_for_timeout(5000)

        # Check if we have any cards initially
        count = await page.locator("div.card-grid__cell").count()
        print(f"Initial card count: {count}")

        if count == 0:
            print(
                "No cards found initially. Taking debug screenshot and dumping HTML..."
            )

        # Handle infinite scroll
        last_height = await page.evaluate("document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 50

        # Scroll until we reach the bottom
        while scroll_attempts < max_scroll_attempts:
            print(f"Scrolling... (Attempt {scroll_attempts + 1})")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)  # Wait for load

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print("No height change, waiting longer...")
                await page.wait_for_timeout(5000)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    print("Reached bottom of page.")
                    break

            last_height = new_height
            scroll_attempts += 1

            # Print count to see progress
            current_count = await page.locator("div.card-grid__cell").count()
            print(f"Current card count: {current_count}")

        print("Finished scrolling. Extracting images...")

        # Extract images
        images = await page.locator(
            "div.card-grid__cell img.game-card-image__img"
        ).all()

        image_data = []
        for i, img in enumerate(images):
            src = await img.get_attribute("src")
            if src:
                try:
                    # Example: https://assets.pokemon-zone.com/game-assets/CardPreviews/cPK_10_010830_00_KAILIOS_C.webp?width=350&quality=100
                    # Fetch only the filename, in part five
                    part_five = src.split("/")[5]
                    clean_name = part_five.split("?")[0]

                    # without .webp suffix
                    if clean_name.endswith(".webp"):
                        clean_name = clean_name[:-5]

                    image_data.append({"Image Name": clean_name})
                except IndexError:
                    print(f"Warning: Could not parse URL format: {src}")
                    image_data.append({"Image Name": src})

            if i % 50 == 0:
                print(f"Processed {i} images...")

        print(f"Total found: {len(image_data)} images.")

        await browser.close()

        if image_data:
            df = pd.DataFrame(image_data)

            # Create a filename based on the arguments
            output_file = ""
            if exorp == "e":
                output_file = f"{set}.xlsx"
            elif exorp == "p":
                output_file = f"{set}_{pack_name}.xlsx"

            # Create a directory for the output file
            os.makedirs("lists", exist_ok=True)
            df.to_excel(os.path.join("lists", output_file), index=False)
            print(
                f"Successfully saved to {os.path.abspath(os.path.join('lists', output_file))}"
            )
        else:
            print("No images found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl Pokemon cards from Pokemon-Zone."
    )

    parser.add_argument("--exorp", help="Expansion (e) or pack key (p):", required=True)
    parser.add_argument(
        "--set",
        help="Set code to crawl (A1, A2, etc.):",
        required=True,
    )
    parser.add_argument(
        "--pack-key",
        help="Pack key to crawl (AN001_0020_00_000, etc.):",
        required=False,
    )
    parser.add_argument(
        "--pack-name",
        help="Pack name to crawl (Charizard, etc.):",
        required=False,
    )

    args = parser.parse_args()

    asyncio.run(crawler(args.exorp, args.set, args.pack_key, args.pack_name))
