#!/usr/bin/env python3
"""Manage AHScanner YAML files."""

from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

from .base_manager import BaseManager
from item_database import ItemDatabase


class AHScannerManager(BaseManager):
    """Manage AHScanner YAML files from gen_dailies directory."""

    def __init__(self, p_dailies_directory: Path, p_items_db: Optional[ItemDatabase] = None):
        """Initialize manager."""
        super().__init__(p_dailies_directory, 'AHScanner.yaml')
        self.m_items_db = p_items_db

    def get_items_by_id(self) -> Dict[str, str]:
        """AHScanner doesn't contain item IDs, only names."""
        return {}

    def get_all_auctions_by_name(self) -> Dict[str, Dict[str, Dict[str, Dict]]]:
        """Get all prices by realm and timestamp."""
        l_result = {}
        for c_file, c_data in self.m_data.items():
            l_timestamp = c_file.parent.stem
            for c_realm, c_items in c_data.items():
                if c_realm not in l_result:
                    l_result[c_realm] = {}
                if l_timestamp not in l_result[c_realm]:
                    l_result[c_realm][l_timestamp] = {}
                l_result[c_realm][l_timestamp] = c_items
        return l_result

    def get_all_qnp_by_name(self):
        """Get all prices by realm and timestamp."""
        l_result = {}
        for c_file, c_data in self.m_data.items():
            l_timestamp = c_file.parent.stem
            for c_realm, c_items in c_data.items():
                if c_realm not in l_result:
                    l_result[c_realm] = {}
                if l_timestamp not in l_result[c_realm]:
                    l_result[c_realm][l_timestamp] = {}
                for c_item_name, c_item_data in c_items.items():
                    l_item_id = self.m_items_db.get_by_name(c_item_name)
                    if not l_item_id:
                        print(f"=== Warning: Item '{c_item_name}' not found in items database")
                        continue
                    l_result[c_realm][l_timestamp][l_item_id] = {
                        "all": {},
                        "filtered": {}
                    }

                    if "all" in c_item_data["buyout"] \
                          and "mean" in c_item_data["buyout"]["all"] \
                          and "all" in c_item_data["minBid"] \
                          and "mean" in c_item_data["minBid"]["all"]:
                       l_buyout = int(c_item_data["buyout"]["all"]["mean"])
                       l_min_bid = int(c_item_data["minBid"]["all"]["mean"])
                       l_count = c_item_data["buyout"]["all"]["count"]
                       l_result[c_realm][l_timestamp][l_item_id]["all"] = {
                           "q": l_count,
                           "p": l_buyout,
                           "m": l_min_bid
                       }

                    if "all" in c_item_data["buyout"] \
                          and "mean" in c_item_data["buyout"]["filtered"] \
                          and "filtered" in c_item_data["minBid"] \
                          and "mean" in c_item_data["minBid"]["filtered"]:
                        l_buyout = int(c_item_data["buyout"]["filtered"]["mean"])
                        l_min_bid = int(c_item_data["minBid"]["filtered"]["mean"])
                        l_count = c_item_data["buyout"]["filtered"]["count"]
                        l_result[c_realm][l_timestamp][l_item_id]["filtered"] = {
                            "q": l_count,
                            "p": l_buyout,
                            "m": l_min_bid
                        }
        return l_result
