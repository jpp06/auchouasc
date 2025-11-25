#!/usr/bin/env python3
"""Convert TradeSkillMaster Shopping to YAML."""

from pathlib import Path

from .lua_to_yaml import LuaToYamlConverter


class ShoppingConverter(LuaToYamlConverter):
    """Convert TradeSkillMaster Shopping Lua to YAML."""

    def __init__(self, p_file_path: Path):
        """
        Initialize converter.

        Args:
            p_file_path: Path to TradeSkillMaster_Shopping.lua file
        """
        super().__init__(p_file_path, 'AscensionTSM_ShoppingDB')

