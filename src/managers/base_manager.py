#!/usr/bin/env python3
"""Base class for YAML file managers."""

from pathlib import Path
from typing import Dict, List, Any

import yaml

from item_database import ItemDatabase


class BaseManager:
    """Base class for managing YAML files from gen_dailies directory."""

    def __init__(self, p_dailies_directory: Path, p_filename_pattern: str):
        """
        Initialize manager.

        Args:
            p_dailies_directory: Directory containing generated dailies files
            p_filename_pattern: Filename pattern to search for (e.g., 'TradeSkillMaster_Accounting.yaml')
        """
        self.m_dailies_directory = p_dailies_directory
        self.m_filename_pattern = p_filename_pattern
        self.m_files: List[Path] = []
        self.m_data: Dict[Path, Dict[str, Any]] = {}

    def load_all(self) -> None:
        """Load all matching YAML files."""
        self.m_files = list(self.m_dailies_directory.rglob(self.m_filename_pattern))
        self.m_data = {}
        for c_file in self.m_files:
            with open(c_file, 'r', encoding='utf-8') as l_file:
                self.m_data[c_file] = yaml.safe_load(l_file) or {}

    def get_files(self) -> List[Path]:
        return self.m_files.copy()

    def fill_database(self, p_database: ItemDatabase) -> int:
        self.load_all()
        l_count = 0
        l_items_by_id = self.get_items_by_id()
        for l_item_id, l_item_name in l_items_by_id.items():
            p_database.add_item(l_item_id, l_item_name)
            l_count += 1
        return l_count