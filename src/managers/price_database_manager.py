#!/usr/bin/env python3
"""Manage price database YAML files."""

from pathlib import Path
from typing import Dict, List, Any

import yaml

from .base_manager import BaseManager


class PriceDatabaseManager(BaseManager):
    """Manage price database YAML files from gen_dailies directory."""

    def __init__(self, p_dailies_directory: Path):
        super().__init__(p_dailies_directory, 'Auctionator_Price_Database.yaml')

    def get_all_prices_by_name(self) -> Dict[str, Dict[str, int]]:
        l_result = {}
        for c_file, c_data in self.m_data.items():
            l_timestamp = c_file.parent.stem
            for c_realm_name, c_realm_data in c_data.items():
                if c_realm_name == '__dbversion':
                    continue
                if c_realm_name not in l_result:
                    l_result[c_realm_name] = {}
                if l_timestamp not in l_result[c_realm_name]:
                    l_result[c_realm_name][l_timestamp] = {}
                for c_item_name, c_price in c_realm_data.items():
                    l_result[c_realm_name][l_timestamp][c_item_name] = int(c_price)
        return l_result

    def fill_database(self, p_database) -> int:
        raise NotImplementedError("Not implemented")
