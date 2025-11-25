"""ScanData decoder for TradeSkillMaster AuctionDB."""

# CODE DIRECT FROM https://github.com/Sapphic-Software/TradeSkillMaster/blob/main/TSM/Util/ScanDataDecoder.lua
# MIT License
# Copyright (c) 2010-2025 Sapphic Software
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

from typing import Dict, List, Any, Optional


class ScanDataDecoder:
    """Decode TradeSkillMaster AuctionDB scanData."""

    def __init__(self):
        """Initialize decoder."""
        self.m_alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_="
        self.m_base = len(self.m_alpha)
        self.m_lookup = {c_char: c_i for c_i, c_char in enumerate(self.m_alpha, 1)}

    def decode(self, p_value: str) -> Optional[int]:
        """Decode a base64-like encoded value."""
        if not p_value or '~' in p_value:
            return None
        l_result = 0
        l_length = len(p_value)
        for c_j in range(l_length - 1, -1, -1):
            c_char_index = l_length - 1 - c_j
            if c_char_index >= l_length:
                break
            c_char = p_value[c_char_index]
            if c_char not in self.m_lookup:
                return None
            l_result += (self.m_lookup[c_char] - 1) * (self.m_base ** c_j)
        return l_result

    def decode_scans(self, p_rope: str) -> Dict[int, Any]:
        """Decode scan history."""
        if p_rope == "A" or not p_rope:
            return {}
        l_scans = {}
        l_days = p_rope.split('!')
        for c_day_data in l_days:
            if ':' not in c_day_data:
                continue
            l_parts = c_day_data.split(':')
            if len(l_parts) != 2:
                continue
            l_day_encoded = l_parts[0]
            l_market_value_data = l_parts[1]
            l_day = self.decode(l_day_encoded)
            if l_day is None:
                continue
            l_scans[l_day] = {}
            if '@' in l_market_value_data:
                l_avg_count = l_market_value_data.split('@')
                if len(l_avg_count) == 2:
                    l_avg = self.decode(l_avg_count[0])
                    l_count = self.decode(l_avg_count[1])
                    if l_avg is not None and l_count is not None:
                        l_scans[l_day]['avg'] = l_avg
                        l_scans[l_day]['count'] = l_count
            else:
                l_values = l_market_value_data.split(';')
                l_decoded_values = []
                for c_value in l_values:
                    l_decoded = self.decode(c_value)
                    if l_decoded is not None:
                        l_decoded_values.append(l_decoded)
                if l_decoded_values:
                    l_scans[l_day] = l_decoded_values
        return l_scans

    def decode_scandata(self, p_scan_data: str) -> List[Dict[str, Any]]:
        """Decode a complete scanData string."""
        if not p_scan_data:
            return []
        l_items = []
        l_parts = p_scan_data.split('?')
        for c_part in l_parts:
            if not c_part.strip():
                continue
            c_parts = c_part.split(',')
            if len(c_parts) < 7:
                continue
            l_item_id_encoded = c_parts[0]
            l_v2 = c_parts[2]  # marketValue
            l_v3 = c_parts[3]  # lastScan
            l_v5 = c_parts[5]  # minBuyout
            l_v6 = c_parts[6]  # encodeScans(scans)
            l_v7 = c_parts[7] if len(c_parts) > 7 else None  # quantity
            l_item_id = self.decode(l_item_id_encoded)
            l_market_value = self.decode(l_v2)
            l_last_scan = self.decode(l_v3)
            l_min_buyout = self.decode(l_v5)
            l_scans = self.decode_scans(l_v6)
            l_quantity = self.decode(l_v7) if l_v7 else None
            if l_item_id is not None:
                l_items.append({
                    'itemID': str(l_item_id),
                    'marketValue': l_market_value,
                    'lastScan': l_last_scan,
                    'minBuyout': l_min_buyout,
                    'scans': l_scans,
                    'quantity': l_quantity
                })
        return l_items


