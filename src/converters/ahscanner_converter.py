#!/usr/bin/env python3
"""Convert AHScanner to YAML."""

from pathlib import Path
from typing import Any, List, Dict
from copy import deepcopy
import statistics

from .lua_to_yaml import LuaToYamlConverter


class AHScannerConverter(LuaToYamlConverter):
    """Convert AHScanner Lua to YAML."""

    def __init__(self, p_file_path: Path):
        """
        Initialize converter.

        Args:
            p_file_path: Path to AHScanner.lua file
        """
        super().__init__(p_file_path, 'AHScannerDB')

    def load(self) -> None:
        super().load()
        l_scans = self.m_python_data.get('scans', {})
        self.m_python_data = self._aggregate_scans()

    def _aggregate_scans(self) -> Dict:
        l_result = {}
        for c_realm, c_items_by_name in self.m_python_data.items():
            if c_realm in ["settings", "scans"]:
                continue
            l_item_name_to_auctions = {}
            for c_item_name, c_items in c_items_by_name.items():
                if c_item_name not in l_item_name_to_auctions:
                    l_item_name_to_auctions[c_item_name] = {}
                for c_item in c_items["items"].values():
                    l_type = self._get_type_and_prepare_data(c_item_name, c_item, l_item_name_to_auctions)
                    self._add_auction_to_data(c_item_name, c_item, l_type, l_item_name_to_auctions)
            l_result[c_realm] = self._get_counted_data(l_item_name_to_auctions)
        return l_result

    def _get_type_and_prepare_data(self, p_item_name, p_item, p_item_name_to_auctions):
        l_type = "buyout"
        l_price_unit = p_item["buyoutUnit"]
        l_min_bid_unit = p_item["minBidUnit"]
        if l_price_unit == 0:
            l_type = "minBid"
            l_price_unit = l_min_bid_unit
        if "buyout" not in p_item_name_to_auctions[p_item_name]:
            p_item_name_to_auctions[p_item_name]["buyout"] = {}
        if "minBid" not in p_item_name_to_auctions[p_item_name]:
            p_item_name_to_auctions[p_item_name]["minBid"] = {}
        if l_min_bid_unit not in p_item_name_to_auctions[p_item_name]["minBid"]:
            p_item_name_to_auctions[p_item_name]["minBid"][l_min_bid_unit] = {}
            p_item_name_to_auctions[p_item_name]["minBid"][l_min_bid_unit]["auctions"] = []
        if l_type == "buyout" and l_price_unit not in p_item_name_to_auctions[p_item_name]["buyout"]:
            p_item_name_to_auctions[p_item_name]["buyout"][l_price_unit] = {}
            p_item_name_to_auctions[p_item_name]["buyout"][l_price_unit]["auctions"] = []
        return l_type

    def _add_auction_to_data(self, p_item_name, p_item, p_type, p_item_name_to_auctions):
        l_data = {
            "minBid": p_item.get('minBid', 0),
            "minBidUnit": p_item.get('minBidUnit', 0),
            "buyout": p_item.get('buyout', 0),
            "buyoutUnit": p_item.get('buyoutUnit', 0),
            "count": p_item.get('count', 0),
            "quality": p_item.get('quality', 0),
            "level": p_item.get('level', 0),
            "minIncrement": p_item.get('minIncrement', 0),
            "highBidder": p_item.get('highBidder', ''),
            "seller": p_item.get('seller', ''),
            "type": p_type,
        }
        l_min_bid_unit = p_item["minBidUnit"]
        p_item_name_to_auctions[p_item_name]["minBid"][l_min_bid_unit]["auctions"].append(l_data)
        if p_type == "buyout":
            l_buyout_unit = p_item["buyoutUnit"]
            p_item_name_to_auctions[p_item_name]["buyout"][l_buyout_unit]["auctions"].append(deepcopy(l_data))

    def _get_counted_data(self, p_item_name_to_auctions):
        l_counted_data = {}
        for c_item_name, c_item_data in p_item_name_to_auctions.items():
            l_counted_data[c_item_name] = {}
            for c_type, c_prices in c_item_data.items():
                l_prices = []
                l_counts_by_prices = {}
                for c_price, c_auctions in c_prices.items():
                    l_item_count = 0
                    l_auctions = c_auctions.get('auctions', [])
                    for c_auction in l_auctions:
                        l_item_count += c_auction.get('count', 0)
                    if l_item_count > 0:
                        l_counts_by_prices[c_price] = {}
                        l_counts_by_prices[c_price]["item_count"] = l_item_count
                        l_counts_by_prices[c_price]["auctions_count"] = len(l_auctions)
                        l_prices += [c_price] * l_item_count
                l_counted_data[c_item_name][c_type] = {}
                l_counted_data[c_item_name][c_type]["counts_by_prices"] = dict(l_counts_by_prices)
                l_prices.sort()
                l_counted_data[c_item_name][c_type]["count"] = len(l_prices)
                l_counted_data[c_item_name][c_type]["min"] = l_prices[0]
                l_counted_data[c_item_name][c_type]["max"] = l_prices[-1]
                l_counted_data[c_item_name][c_type]["mean"] = statistics.mean(l_prices)
                l_counted_data[c_item_name][c_type]["median"] = statistics.median(l_prices)
                l_counted_data[c_item_name][c_type]["harmonic_mean"] = statistics.harmonic_mean(l_prices)
                l_counted_data[c_item_name][c_type]["median_grouped"] = statistics.median_grouped(l_prices)
                l_counted_data[c_item_name][c_type]["median_high"] = statistics.median_high(l_prices)
                l_counted_data[c_item_name][c_type]["median_low"] = statistics.median_low(l_prices)
                l_counted_data[c_item_name][c_type]["mode"] = statistics.mode(l_prices)
                l_counted_data[c_item_name][c_type]["pstdev"] = statistics.pstdev(l_prices)
                l_counted_data[c_item_name][c_type]["stdev"] = statistics.stdev(l_prices)
                l_counted_data[c_item_name][c_type]["pvariance"] = statistics.pvariance(l_prices)
                l_counted_data[c_item_name][c_type]["variance"] = statistics.variance(l_prices)
                l_counted_data[c_item_name][c_type]["deciles"] = statistics.quantiles(l_prices, n=10)
                l_counted_data[c_item_name][c_type]["quartiles"] = statistics.quantiles(l_prices, n=4)
        return l_counted_data
