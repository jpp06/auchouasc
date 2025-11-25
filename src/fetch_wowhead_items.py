#!/usr/bin/env python3
"""Fetch item names from JudgeHype."""

import re
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from item_database import ItemDatabase


class JudgeHypeFetcher:
    """Fetch item names from JudgeHype."""

    def __init__(self, p_item_database: ItemDatabase):
        """Initialize fetcher."""
        self.m_item_db = p_item_database
        self.m_session = requests.Session()
        self.m_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_item_name(self, p_item_id: str) -> Optional[str]:
        """Fetch item name from JudgeHype."""
        print(f"Fetching item name for {p_item_id}")
        l_url = f"https://wowclassic.judgehype.com/database/en/item/{p_item_id}/"
        try:
            l_response = self.m_session.get(l_url, timeout=10)
            l_response.raise_for_status()
            l_soup = BeautifulSoup(l_response.text, 'html.parser')
            l_title = l_soup.find('title')
            if l_title:
                l_title_text = l_title.get_text()
                l_match = re.search(r'^(.+?)\s*-\s*JudgeHype', l_title_text, re.IGNORECASE)
                if l_match:
                    return l_match.group(1).strip()
            l_h1 = l_soup.find('h1')
            if l_h1:
                return l_h1.get_text().strip()
            return None
        except Exception as l_e:
            print(f"*** Error fetching item {p_item_id}: {l_e}", file=__import__('sys').stderr)
            return None

    def fetch_all_from_file(self, p_item_id_file: Path, p_delay: float = 0.5) -> int:
        """Fetch all item names from file and update database."""
        l_added_count = 0
        l_skipped_count = 0
        l_error_count = 0

        with open(p_item_id_file, 'r', encoding='utf-8') as l_file:
            l_item_ids = [l_line.strip() for l_line in l_file if l_line.strip()]

        l_total = len(l_item_ids)
        print(f"--- Processing {l_total} item IDs from {p_item_id_file}")

        for c_idx, c_item_id in enumerate(l_item_ids, 1):
            if self.m_item_db.get_by_id(c_item_id):
                print(f"--- Item {c_item_id} already exists in database")
                l_skipped_count += 1
                if c_idx % 100 == 0:
                    print(f"--- Progress: {c_idx}/{l_total} (added: {l_added_count}, "
                          f"skipped: {l_skipped_count}, errors: {l_error_count})")
                continue

            l_item_name = self.fetch_item_name(c_item_id)
            if l_item_name:
                try:
                    self.m_item_db.add_item(c_item_id, l_item_name)
                    l_added_count += 1
                    if l_added_count % 10 == 0:
                        self.m_item_db.save()
                        print(f"--- Progress: {c_idx}/{l_total} (added: {l_added_count}, "
                              f"skipped: {l_skipped_count}, errors: {l_error_count})")
                except ValueError as l_e:
                    print(f"*** Error adding item {c_item_id}: {l_e}", file=__import__('sys').stderr)
                    l_error_count += 1
            else:
                print(f"--- Item {c_item_id} not found on JudgeHype")
                l_error_count += 1

            if c_idx < l_total:
                time.sleep(p_delay)

        self.m_item_db.save()
        print(f"--- Completed: added {l_added_count}, skipped {l_skipped_count}, "
              f"errors {l_error_count}")
        return l_added_count


def main():
    """Main entry point."""
    import sys
    l_item_db_file = Path('datas/items.yaml')
    l_item_id_file = Path('itemId.txt')

    if not l_item_id_file.exists():
        print(f"*** Error: {l_item_id_file} not found", file=sys.stderr)
        sys.exit(1)

    l_item_db = ItemDatabase(l_item_db_file)
    l_fetcher = JudgeHypeFetcher(l_item_db)
    l_fetcher.fetch_all_from_file(l_item_id_file)


if __name__ == '__main__':
    main()

