#!/usr/bin/env python3
"""Manage shopping YAML files."""

from pathlib import Path
from typing import Dict, List, Any

import yaml

from .base_manager import BaseManager


class ShoppingManager(BaseManager):
    """Manage shopping YAML files from gen_dailies directory."""

    def __init__(self, p_dailies_directory: Path):
        """Initialize manager."""
        super().__init__(p_dailies_directory, 'TradeSkillMaster_Shopping.yaml')

    def get_destroying_items_by_id(self) -> Dict[str, str]:
        """
        Get all items by ID from all shopping files.

        Returns:
            Dictionary mapping item IDs to item names
        """
        l_result = {}
        for c_data in self.m_data.values():
            l_destroying_items = c_data.get('global', {}).get('destroyingTargetItems', {})
            for c_item_string, c_item_name in l_destroying_items.items():
                l_id = c_item_string.split(':')[1]
                l_result[l_id] = c_item_name
        return l_result

    def get_items_by_id(self) -> Dict[str, str]:
        l_result = {}
        l_result.update(self.get_destroying_items_by_id())
        return l_result


