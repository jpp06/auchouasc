#!/usr/bin/env python3
"""Main entry point for Lua to YAML converters."""

from pathlib import Path

import typer

from converters.ahscanner_converter import AHScannerConverter
from item_database import ItemDatabase
from price_database import PriceDatabase
from auction_database import AuctionDatabase
from managers.ahscanner_manager import AHScannerManager
from obsidian_generator import ObsidianGenerator
from ahscanner_obsidian_generator import AHScannerObsidianGenerator

app = typer.Typer(help="Lua to YAML converter")

@app.command()
def update_item_db(item_database_file: Path = typer.Option(Path('datas/items.yaml'), help="Path to item database file"),
                   price_database_file: Path = typer.Option(Path('datas/qnp.yaml'), help="Path to price and quantity database file"),
                   auction_database_file: Path = typer.Option(Path('datas/auctions.yaml'), help="Path to auction database file"),
                   dailies_directory: Path = typer.Option(Path('gen_dailies'), help="Directory containing generated dailies files")):
    """
    Update the item database.

    Args:
        item_database_file: Path to item database file
    """
    item_database_file.parent.mkdir(parents=True, exist_ok=True)

    l_items_db = ItemDatabase(item_database_file)
    l_prices_db = PriceDatabase(price_database_file)
    l_auction_database = AuctionDatabase(auction_database_file)

    l_items_added = 0
    l_ahscanner_manager = AHScannerManager(dailies_directory, l_items_db)
    l_ahscanner_manager.load_all()
    l_items = l_ahscanner_manager.get_all_qnp_by_name()
    for c_realm, c_prices in l_items.items():
        l_prices_db.add_realm(c_realm)
        for c_timestamp, c_prices in c_prices.items():
            l_prices_db.add_timestamp(c_realm, c_timestamp)
            l_prices_db.add_source(c_realm, c_timestamp, 'ahs')
            for c_item_id, c_qnp in c_prices.items():
                l_prices_db.add_qnp(c_item_id, c_qnp, c_realm, c_timestamp, "ahs")
                l_items_added += 1
    print(f"--- Added {l_items_added} ahs prices to price database")
    l_prices_db.save()

    l_auctions = l_ahscanner_manager.get_all_auctions_by_name()
    for c_realm, c_auctions in l_auctions.items():
        l_auction_database.add_realm(c_realm)
        for c_timestamp, c_auction_data in c_auctions.items():
            l_auction_database.add_timestamp(c_realm, c_timestamp)
            for c_item_name, c_auction_data in c_auction_data.items():
                l_item_id = l_items_db.get_by_name(c_item_name)
                if not l_item_id:
                    print(f"=== Warning: Item '{c_item_name}' not found in items database")
                    continue
                l_auction_database.add_item_auction_data(l_item_id, c_auction_data, c_realm, c_timestamp)
    l_auction_database.save()

    print("--- Done.")

@app.command()
def convert(dailies_dir: Path = typer.Argument(Path('dailies'), help="Directory containing subdirectories with Lua files")):
    """
    Convert Lua files to YAML.

    Scans all subdirectories in dailies_dir and converts all supported Lua files found:
    - AHScanner.lua

    Args:
        dailies_dir: Directory containing subdirectories with Lua files
    """
    if not dailies_dir.is_dir():
        print(f"*** Error: Not a directory: {dailies_dir}")
        raise typer.Exit(1)

    # Find 'dailies' in the path and create gen_dailies at the same level
    l_parts = dailies_dir.parts
    if 'dailies' in l_parts:
        l_dailies_index = l_parts.index('dailies')
        l_base_parts = l_parts[:l_dailies_index]
        l_output_base = Path(*l_base_parts) / 'gen_dailies'
    else:
        # Fallback: create gen_dailies next to the directory
        l_output_base = dailies_dir.parent / 'gen_dailies'
    l_output_base.mkdir(parents=True, exist_ok=True)

    l_files_to_convert = [
        ('AHScanner.lua', AHScannerConverter),
    ]

    l_total_converted = 0
    l_subdirs = [c_path for c_path in dailies_dir.iterdir() if c_path.is_dir()]
    for c_subdir in l_subdirs:
        l_output_dir = l_output_base / c_subdir.name
        l_converted_count = 0
        for l_filename, l_converter_class in l_files_to_convert:
            l_file_path = c_subdir / l_filename
            #print("---", l_file_path)
            if not l_file_path.exists():
                print(f"=== Warning: {l_filename} in {c_subdir.name} (not found)")
                continue

            l_converter = l_converter_class(l_file_path)
            l_converter.load()
            l_output_path = l_output_dir / l_filename.replace('.lua', '.yaml')
            if l_converter.save_yaml(l_output_path):
                l_converted_count += 1
        l_total_converted += l_converted_count
    print(f"--- Total: {l_total_converted} file(s) converted")


@app.command()
def obsidian(item_database_file: Path = typer.Option(Path('datas/items.yaml'), help="Path to item database file"),
             price_database_file: Path = typer.Option(Path('datas/qnp.yaml'), help="Path to price and quantity database file"),
             output_dir: Path = typer.Option(Path('obsidian'), help="Output directory for Obsidian files")):
    """
    Generate Obsidian markdown files from item and price databases.

    Args:
        item_database_file: Path to item database file
        price_database_file: Path to price database file
        output_dir: Output directory for Obsidian files
    """
    l_items_db = ItemDatabase(item_database_file)
    l_prices_db = PriceDatabase(price_database_file)

    l_generator = ObsidianGenerator(l_items_db, l_prices_db, output_dir)
    l_generated_count = l_generator.generate()

    print(f"--- Generated {l_generated_count} item files in {output_dir / 'items'}")
    print(f"--- Generated index file: {output_dir / 'Item Index.md'}")


@app.command()
def obsidian_auctions(item_database_file: Path = typer.Option(Path('datas/items.yaml'), help="Path to item database file"),
                      auction_database_file: Path = typer.Option(Path('datas/auctions.yaml'), help="Path to auction database file"),
                      output_dir: Path = typer.Option(Path('obsidian/auctions'), help="Output directory for Obsidian auction files")):
    """
    Generate Obsidian markdown files from AHScanner auction files.

    Args:
        item_database_file: Path to item database file
        auction_database_file: Path to auction database file
        output_dir: Output directory for Obsidian auction files
    """
    l_items_db = ItemDatabase(item_database_file)
    l_auction_database = AuctionDatabase(auction_database_file)
    l_generator = AHScannerObsidianGenerator(l_items_db, l_auction_database, output_dir)
    l_generated_count = l_generator.generate()

    print(f"--- Generated {l_generated_count} auction files in {output_dir}")
    print(f"--- Generated index file: {output_dir / 'Auction Index.md'}")


if __name__ == '__main__':
    app()

