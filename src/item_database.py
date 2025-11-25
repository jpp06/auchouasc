#!/usr/bin/env python3
"""Item database management."""

from typing import Dict, Optional, Any

from pathlib import Path
import yaml


class ItemDatabase:
    """Manage item database with efficient lookup by ID and name."""

    def __init__(self, p_database_file: Path):
        """Initialize empty database."""
        self.m_filename = p_database_file
        self.m_items_by_id: Dict[str, str] = {}
        self.m_items_by_name: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        """Load data from database file."""
        if not self.m_filename.exists():
            return
        with open(self.m_filename, 'r', encoding='utf-8') as l_file:
            l_data = yaml.safe_load(l_file) or {}
        self.m_items_by_id = {}
        self.m_items_by_name = {}

        # Data structure: {item_id: item_name}
        for c_item_id, c_item_name in l_data.items():
            if not isinstance(c_item_name, str):
                raise ValueError(f"*** Error: Item name must be a string: {c_item_name}")
            # Check for collision: same item name with different ID
            if c_item_name not in self.m_items_by_name and c_item_id not in self.m_items_by_id:
                self.m_items_by_name[c_item_name] = c_item_id
                self.m_items_by_id[c_item_id] = c_item_name
                continue

            if c_item_name in self.m_items_by_name:
                l_existing_id = self.m_items_by_name[c_item_name]
                if l_existing_id != c_item_id and "Adventurer's Cache" != c_item_name:
                    raise ValueError(
                        f"*** Error: Collision detected: "
                        f"item '{c_item_name}' already exists with ID '{l_existing_id}', "
                        f"trying to add with ID '{c_item_id}'")
            if c_item_id in self.m_items_by_id:
                l_existing_name = self.m_items_by_id[c_item_id]
                if l_existing_name != c_item_name and "Adventurer's Cache" != c_item_id:
                    raise ValueError(
                        f"*** Error: Collision detected: "
                        f"item ID '{c_item_id}' already exists with name '{l_existing_name}', "
                        f"trying to add with name '{c_item_name}'")
    def save(self) -> None:
        l_sorted_items = dict(sorted(self.m_items_by_id.items(), key=lambda x: int(x[0])))
        with open(self.m_filename, 'w', encoding='utf-8') as l_file:
            yaml.dump(l_sorted_items, l_file, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def get_by_id(self, p_item_id: str) -> Optional[str]:
        return self.m_items_by_id.get(p_item_id)
    def get_all_by_id(self) -> Dict[str, str]:
        return self.m_items_by_id
    def get_by_name(self, p_item_name: str) -> Optional[str]:
        return self.m_items_by_name.get(p_item_name)

    def add_item(self, p_item_id: str, p_item_name: str) -> None:
        if p_item_name not in self.m_items_by_name and p_item_id not in self.m_items_by_id:
            self.m_items_by_id[p_item_id] = p_item_name
            self.m_items_by_name[p_item_name] = p_item_id
            return
        if "Adventurer's Cache" == p_item_name:
            self.m_items_by_id[p_item_id] = p_item_name
            self.m_items_by_name[p_item_name] = p_item_id
            return
        if p_item_name in self.m_items_by_name and p_item_id in self.m_items_by_id \
                and self.m_items_by_name[p_item_name] == p_item_id and self.m_items_by_id[p_item_id] == p_item_name:
            return
        raise ValueError(f"*** Error: Inconsistent database: "
                         f"item ID '{p_item_id}' with name '{p_item_name}'")
