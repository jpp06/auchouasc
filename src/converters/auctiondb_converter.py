#!/usr/bin/env python3
"""Convert TradeSkillMaster AuctionDB to YAML."""

from pathlib import Path

from .lua_to_yaml import LuaToYamlConverter
from managers.scan_data_decoder import ScanDataDecoder


class AuctionDBConverter(LuaToYamlConverter):
    """Convert TradeSkillMaster AuctionDB Lua to YAML."""

    def __init__(self, p_file_path: Path):
        """Initialize converter."""
        super().__init__(p_file_path, 'AscensionTSM_AuctionDB')
        self.m_decoder = ScanDataDecoder()

    #def save_yaml(self, p_output_path=None):
    #    """Save data as YAML file with decoded scanData."""
    #    self._decode_scandata()
    #    super().save_yaml(p_output_path)

    #def _decode_scandata(self):
    #    """Decode scanData in all realms."""
    #    if not self.m_python_data or 'realm' not in self.m_python_data:
    #        return
    #    for c_realm_data in self.m_python_data['realm'].values():
    #        if 'scanData' in c_realm_data and c_realm_data['scanData']:
    #            l_scan_data = c_realm_data['scanData']
    #            l_decoded_items = self.m_decoder.decode_scandata(l_scan_data)
    #            c_realm_data['decodedScanData'] = l_decoded_items

