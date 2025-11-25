#!/usr/bin/env python3
"""Convert TradeSkillMaster Accounting to YAML."""

from pathlib import Path

from .lua_to_yaml import LuaToYamlConverter


class AccountingConverter(LuaToYamlConverter):
    """Convert TradeSkillMaster Accounting Lua to YAML."""

    def __init__(self, p_file_path: Path):
        """
        Initialize converter.

        Args:
            p_file_path: Path to TradeSkillMaster_Accounting.lua file
        """
        super().__init__(p_file_path, 'AscensionTSM_AccountingDB')
