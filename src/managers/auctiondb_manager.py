#!/usr/bin/env python3
"""Manage auction DB YAML files."""

from pathlib import Path
from typing import Dict, Tuple

import yaml

from .base_manager import BaseManager
from .scan_data_decoder import ScanDataDecoder


class AuctionDBManager(BaseManager):
    """Manage auction DB YAML files from gen_dailies directory."""

    def __init__(self, p_dailies_directory: Path):
        """Initialize manager."""
        super().__init__(p_dailies_directory, 'TradeSkillMaster_AuctionDB.yaml')
        self.m_decoder = ScanDataDecoder()

    def get_all_qnp_by_name(self) -> Dict[str, Dict[str, Dict[str, Dict]]]:
        """Get all prices by realm and timestamp."""
        l_result = {}
        for c_file, c_data in self.m_data.items():
            l_timestamp = c_file.parent.stem
            for c_realm_name, c_realm_data in c_data.get('realm', {}).items():
                if c_realm_name not in l_result:
                    l_result[c_realm_name] = {}
                if l_timestamp not in l_result[c_realm_name]:
                    l_result[c_realm_name][l_timestamp] = {}
                l_scan_data = c_realm_data.get('scanData', '')
                if not l_scan_data:
                    continue
                l_items = self.m_decoder.decode_scandata(l_scan_data)
                for c_item in l_items:
                    l_item_id = c_item.get('itemID')
                    l_market_value = c_item.get('marketValue')
                    l_min_buyout = c_item.get('minBuyout')
                    l_quantity = c_item.get('quantity')
                    l_result[c_realm_name][l_timestamp][l_item_id] = {
                        "q": l_quantity,
                        "p": l_market_value,
                        "m": l_min_buyout
                    }
        return l_result
