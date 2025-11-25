#!/usr/bin/env python3
"""Price database management."""

from pathlib import Path
from typing import Dict
import yaml


class PriceDatabase:
    """Manage price database with lookup by item name and realm."""

    def __init__(self, p_database_file: Path):
        """Initialize empty database."""
        self.m_filename = p_database_file
        self.m_prices_by_realm = {}
        if not p_database_file.exists():
            self.m_prices_by_realm = {}
            return
        with open(p_database_file, 'r', encoding='utf-8') as l_file:
            self.m_prices_by_realm = yaml.safe_load(l_file) or {}
    def save(self) -> None:
        with open(self.m_filename, 'w', encoding='utf-8') as l_file:
            yaml.dump(self.m_prices_by_realm, l_file, default_flow_style=False, allow_unicode=True, sort_keys=True)

    def add_realm(self, p_realm: str) -> None:
        if p_realm not in self.m_prices_by_realm:
            self.m_prices_by_realm[p_realm] = {}
    def add_timestamp(self, p_realm: str, p_timestamp: str) -> None:
        if p_realm not in self.m_prices_by_realm:
            raise ValueError(f"*** Error: Realm '{p_realm}' does not exist. Use add_realm() first.")
        if p_timestamp not in self.m_prices_by_realm[p_realm]:
            self.m_prices_by_realm[p_realm][p_timestamp] = {}
    def add_source(self, p_realm: str, p_timestamp: str, p_source: str) -> None:
        if p_realm not in self.m_prices_by_realm:
            raise ValueError(f"*** Error: Realm '{p_realm}' does not exist. Use add_realm() first.")
        if p_timestamp not in self.m_prices_by_realm[p_realm]:
            raise ValueError(f"*** Error: Timestamp '{p_timestamp}' does not exist. Use add_timestamp() first.")
        if p_source not in self.m_prices_by_realm[p_realm][p_timestamp]:
            self.m_prices_by_realm[p_realm][p_timestamp][p_source] = {}

    def add_qnp(self, p_item_id: str, p_qnp: Dict, p_realm: str, p_timestamp: str, p_source: str) -> None:
        if not p_item_id or not all(c in '0123456789' for c in p_item_id):
            raise ValueError(f"*** Error: Item ID must contain only digits: '{p_item_id}'. At {p_timestamp} in {p_realm}")
        if p_realm not in self.m_prices_by_realm:
            raise ValueError(f"*** Error: Realm '{p_realm}' does not exist. Use add_realm() first. At {p_timestamp} in {p_realm}")
        if p_timestamp not in self.m_prices_by_realm[p_realm]:
            raise ValueError(f"*** Error: Timestamp '{p_timestamp}' does not exist. Use add_timestamp() first. At {p_timestamp} in {p_realm}")
        if p_source not in self.m_prices_by_realm[p_realm][p_timestamp]:
            raise ValueError(f"*** Error: Source '{p_source}' does not exist. Use add_source() first. At {p_timestamp} in {p_realm}")
        self.m_prices_by_realm[p_realm][p_timestamp][p_source][p_item_id] = p_qnp
