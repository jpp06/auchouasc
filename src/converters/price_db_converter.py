#!/usr/bin/env python3
"""Convert Auctionator Price Database to YAML."""

from pathlib import Path

from .lua_to_yaml import LuaToYamlConverter


class PriceDatabaseConverter(LuaToYamlConverter):
    """Convert Auctionator Price Database Lua to YAML."""

    def __init__(self, p_file_path: Path):
        """
        Initialize converter.

        Args:
            p_file_path: Path to Auctionator_Price_Database.lua file
        """
        super().__init__(p_file_path, 'AUCTIONATOR_PRICE_DATABASE')
