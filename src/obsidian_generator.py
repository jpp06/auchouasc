#!/usr/bin/env python3
"""Obsidian markdown generator."""

from pathlib import Path
from typing import Dict, List
from datetime import datetime

from item_database import ItemDatabase
from price_database import PriceDatabase


class ObsidianGenerator:
    """Generate Obsidian markdown files from item and price databases."""

    def __init__(self, p_items_db: ItemDatabase, p_prices_db: PriceDatabase, p_output_dir: Path):
        """Initialize generator."""
        self.m_items_db = p_items_db
        self.m_prices_db = p_prices_db
        self.m_output_dir = p_output_dir
        self.m_items_dir = p_output_dir / 'items'
        self.m_templates_dir = Path(__file__).parent.parent / 'templates'
        self.m_chart_template = self._load_template('chart.md')
        self.m_quantity_chart_template = self._load_template('quantity_chart.md')
        self.m_details_template = self._load_template('details.md')
        self.m_index_template = self._load_template('index.md')

    def generate(self) -> int:
        """Generate all Obsidian markdown files."""
        self.m_items_dir.mkdir(parents=True, exist_ok=True)

        l_all_items = self.m_items_db.get_all_by_id()
        l_index_items = []
        l_generated_count = 0

        for c_item_id, c_item_name in sorted(l_all_items.items()):
            l_item_filename = f"{c_item_name} - {c_item_id}.md"
            l_item_file = self.m_items_dir / l_item_filename

            l_markdown = self._generate_item_markdown(c_item_id, c_item_name)
            if l_markdown:
                with open(l_item_file, 'w', encoding='utf-8') as l_file:
                    l_file.write(l_markdown)
                l_item_filename_no_ext = l_item_filename.replace('.md', '')
                l_index_items.append(f"- [[{l_item_filename_no_ext}|items/{l_item_filename_no_ext}]]")
                l_generated_count += 1

        self._generate_index(l_index_items)
        return l_generated_count

    def _generate_item_markdown(self, p_item_id: str, p_item_name: str) -> str:
        """Generate markdown content for a single item."""
        l_prices_data = self.m_prices_db.m_prices_by_realm

        for c_realm, c_timestamps in l_prices_data.items():
            l_dates = []
            l_ahs_prices = []
            l_ahs_min_bid_values = []
            l_ahs_quantities = []
            l_table_rows = []
            for c_timestamp, c_sources in c_timestamps.items():
                l_timestamp_obj = datetime.strptime(c_timestamp, '%Y_%m_%dT%H_%M_%S')
                l_date_str = l_timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
                l_date_short = l_timestamp_obj.strftime('%Y-%m-%d %H:%M')

                l_ahs_item = c_sources.get('ahs', {}).get(p_item_id)
                if not l_ahs_item: # keep only item with ahs data
                    continue
                l_ahs_price = None
                l_ahs_min_bid_value = None
                l_ahs_quantity = None

                if l_ahs_item:
                    l_ahs_price = l_ahs_item.get('p')
                    l_ahs_min_bid_value = l_ahs_item.get('m')
                    l_ahs_quantity = l_ahs_item.get('q')

                if l_ahs_price is not None:
                    if l_date_str not in l_dates:
                        l_dates.append(l_date_str)
                        l_ahs_prices.append(None)
                        l_ahs_min_bid_values.append(None)
                        l_ahs_quantities.append(None)
                    l_index = l_dates.index(l_date_str)
                    if l_ahs_price is not None:
                        l_ahs_prices[l_index] = l_ahs_price
                        l_ahs_min_bid_values[l_index] = l_ahs_min_bid_value
                        l_ahs_quantities[l_index] = l_ahs_quantity
                        l_table_rows.append((l_date_short, l_ahs_price, l_ahs_quantity or 0, 'ahs'))

            if not l_dates:
                return ""

            l_price_chart_content = self._generate_price_chart_content(l_dates, l_ahs_prices, l_ahs_min_bid_values)
            l_quantity_chart_content = self._generate_quantity_chart_content(l_dates, l_ahs_quantities)

            l_markdown = f"## {c_realm}\n" + \
                f"### Prices (mean)\n" + \
                f"```chart\n" + \
                f"{l_price_chart_content}\n" + \
                f"```\n" + \
                f"### Quantities\n" + \
                f"```chart\n" + \
                f"{l_quantity_chart_content}\n" + \
                f"```\n" + \
                f"{self.m_details_template}"

            for c_row in sorted(l_table_rows):
                l_markdown += f"| {c_row[0]} | {c_row[1]} | {c_row[2]} | {c_row[3]} |\n"

        return l_markdown

    def _load_template(self, p_filename: str) -> str:
        """Load template from file."""
        l_template_path = self.m_templates_dir / p_filename
        with open(l_template_path, 'r', encoding='utf-8') as l_file:
            return l_file.read()

    def _generate_price_chart_content(self, p_dates: List[str], p_ahs_prices: List[int], p_ahs_min_bid_values: List[int]) -> str:
        """Generate chart content from dates, ahs prices and ahs min bid values."""
        l_all_prices = [p for p in p_ahs_prices + p_ahs_min_bid_values if p is not None]
        l_max_price = max(l_all_prices) if l_all_prices else 0

        l_chart_labels = '","'.join(p_dates)
        l_ahs_prices_str = ','.join('null' if p is None else str(p) for p in p_ahs_prices)
        l_ahs_min_bid_str = ','.join('null' if p is None else str(p) for p in p_ahs_min_bid_values)

        return self.m_chart_template.format(
            labels=l_chart_labels,
            ahs_prices=l_ahs_prices_str,
            ahs_min_bid=l_ahs_min_bid_str,
            max_price=l_max_price + 10
        )

    def _generate_quantity_chart_content(self, p_dates: List[str], p_ahs_quantities: List[int]) -> str:
        """Generate quantity chart content from dates and quantities."""
        l_ahs_quantites_filtered = [q for q in p_ahs_quantities if q is not None]
        l_max_quantity = max(l_ahs_quantites_filtered) if l_ahs_quantites_filtered else 0
        l_max_quantity = max(l_max_quantity, max(l_ahs_quantites_filtered)) if l_ahs_quantites_filtered else l_max_quantity

        l_chart_labels = '","'.join(p_dates)
        l_ahs_quantities_str = ','.join('null' if q is None else str(q) for q in p_ahs_quantities)

        return self.m_quantity_chart_template.format(
            labels=l_chart_labels,
            ahs_quantities=l_ahs_quantities_str,
            max_quantity=l_max_quantity + 10
        )

    def _generate_index(self, p_index_items: List[str]) -> None:
        """Generate Item Index.md file."""
        l_index_file = self.m_output_dir / 'Item Index.md'
        l_index_content = self.m_index_template + '\n'.join(sorted(p_index_items)) + '\n'

        with open(l_index_file, 'w', encoding='utf-8') as l_file:
            l_file.write(l_index_content)
