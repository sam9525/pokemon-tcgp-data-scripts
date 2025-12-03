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
