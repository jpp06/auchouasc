#!/usr/bin/env python3
"""Manage accounting YAML files."""

from pathlib import Path
from typing import Dict, List, Any

import yaml
import csv
from collections import defaultdict
from io import StringIO

from item_database import ItemDatabase
from .base_manager import BaseManager


class AccountingManager(BaseManager):
    """Manage accounting YAML files from gen_dailies directory."""

    def __init__(self, p_dailies_directory: Path):
        """Initialize manager."""
        super().__init__(p_dailies_directory, 'TradeSkillMaster_Accounting.yaml')

    def get_global_items_by_id(self) -> Dict[str, str]:
        """Get all global items by ID from all accounting files."""
        l_result = {}
        for c_data in self.m_data.values():
            l_item_strings = c_data.get('global', {}).get('itemStrings', {})
            for c_item_name, c_item_string in l_item_strings.items():
                l_id = c_item_string.split(':')[1]
                l_result[l_id] = c_item_name
        return l_result

    def _decode_csv(self, p_field: str) -> Dict[str, str]:
        l_result = defaultdict(dict)
        for c_path, c_data in self.m_data.items():
            for c_realm, c_realm_data in c_data['realm'].items():
                l_csv = c_realm_data.get(p_field, '')
                l_csv_dict = csv.DictReader(StringIO(l_csv))
                l_result[c_path][c_realm] = l_csv_dict
            l_result[c_path] = l_result[c_path]
        return l_result

    def get_realm_items_by_id(self, p_field: str) -> Dict[str, str]:
        l_csv = self._decode_csv(p_field)
        l_result = {}
        for _, c_realms in l_csv.items():
            for _, c_csv_dict in c_realms.items():
                for c_row in c_csv_dict:
                    l_id = c_row['itemString'].split(':')[1]
                    l_result[l_id] = c_row['itemName']
        return l_result

    def get_items_by_id(self) -> Dict[str, str]:
        l_result = {}
        l_result.update(self.get_global_items_by_id())
        l_result.update(self.get_realm_items_by_id('csvBuys'))
        l_result.update(self.get_realm_items_by_id('csvCancelled'))
        l_result.update(self.get_realm_items_by_id('csvExpired'))
        l_result.update(self.get_realm_items_by_id('csvSales'))
        return l_result
