
"""Obsidian markdown generator for AHScanner auctions."""

from pathlib import Path
from typing import Dict, List

from datetime import datetime

from item_database import ItemDatabase
from auction_database import AuctionDatabase


class AHScannerObsidianGenerator:
    """Generate Obsidian markdown files from AHScanner auction files."""

    def __init__(self, p_items_db: ItemDatabase, p_auction_database: AuctionDatabase, p_output_dir: Path):
        """Initialize generator."""
        self.m_items_db = p_items_db
        self.m_auction_database = p_auction_database
        self.m_output_dir = p_output_dir
        self.m_output_dir.mkdir(parents=True, exist_ok=True)
        self.m_templates_dir = Path(__file__).parent.parent / 'templates'
        self.m_auction_chart_template = self._load_template('auction_chart.md')
        self.m_chart_avgs_template = self._load_template('chart_avgs.md')
        self.m_chart_mmmm_template = self._load_template('chart_mmmm.md')
        self.m_chart_pxxx_template = self._load_template('chart_pXxx.md')
        self.m_graph_mustache_template = self._load_template('graph_mustache.md')
        self.m_step_count = 1000

    def generate(self) -> int:
        """Generate all Obsidian markdown files for auctions."""
        l_generated_count = 0
        l_index_items = []

        l_auctions_data = self.m_auction_database.m_auctions_by_realm
        for c_realm, c_timestamps in l_auctions_data.items():
            for c_timestamp, c_auctions in c_timestamps.items():
                l_markdown = self._generate_auction_markdown(c_auctions, c_realm, c_timestamp)
                if not l_markdown:
                    continue

                l_output_file = self.m_output_dir / f"auctions_{c_timestamp}.md"
                with open(l_output_file, 'w', encoding='utf-8') as l_file:
                    l_file.write(l_markdown)
                l_index_items.append(f"- [[auctions_{c_timestamp}|auctions/auctions_{c_timestamp}]]")
                l_generated_count += 1

        l_all_items = self.m_items_db.get_all_by_id()
        for c_item_id, c_item_name in sorted(l_all_items.items()):
            l_item_filename = f"{c_item_name} - {c_item_id}.md"
            l_item_file = self.m_output_dir / f'stats_{l_item_filename}'
            l_markdown = self._generate_stats_chart(c_item_id)
            if l_markdown:
                with open(l_item_file, 'w', encoding='utf-8') as l_file:
                    l_file.write(l_markdown)
                l_index_items.append(f"- [[stats_{l_item_filename}|stats/stats_{l_item_filename}]]")
                l_generated_count += 1

        if l_index_items:
            self._generate_index(l_index_items)
            l_generated_count += 1

        return l_generated_count


    def _generate_stats_chart(self, p_item_id):
        """Generate stats charts."""
        l_markdown = ""
        for c_realm, c_timestamps in self.m_auction_database.m_auctions_by_realm.items():
            l_dates = []
            l_harmonic_means = []
            l_medians = []
            l_medians_groupe = []
            l_medians_low = []
            l_means = []
            l_mins = []
            l_maxs = []
            l_p_stdevs = []
            l_stdevs = []
            l_p_variances = []
            l_variances = []
            l_mustaches = []
            for c_timestamp, c_items in c_timestamps.items():
                l_timestamp_obj = datetime.strptime(c_timestamp, '%Y_%m_%dT%H_%M_%S')
                l_date_str = l_timestamp_obj.strftime('%Y-%m-%d %H:%M')

                l_item = c_items.get(p_item_id)
                if not l_item:
                    continue
                l_buyout_filtered = l_item['buyout']['filtered']
                l_harmonic_mean = l_buyout_filtered['harmonic_mean']
                l_median = l_buyout_filtered['median']
                l_median_groupe = l_buyout_filtered['median_grouped']
                l_median_low = l_buyout_filtered['median_low']
                l_mean = l_buyout_filtered['mean']
                l_min = l_buyout_filtered['min']
                l_max = l_buyout_filtered['max']
                l_p_stdev = l_buyout_filtered['pstdev']
                l_stdev = l_buyout_filtered['stdev']
                l_p_variance = l_buyout_filtered['pvariance']
                l_variance = l_buyout_filtered['variance']
                l_mustache = l_buyout_filtered['quartiles']
                l_dates.append(l_date_str)
                l_harmonic_means.append(l_harmonic_mean)
                l_medians.append(l_median)
                l_medians_groupe.append(l_median_groupe)
                l_medians_low.append(l_median_low)
                l_means.append(l_mean)
                l_mins.append(l_min)
                l_maxs.append(l_max)
                l_p_stdevs.append(l_p_stdev)
                l_stdevs.append(l_stdev)
                l_p_variances.append(l_p_variance)
                l_variances.append(l_variance)
                l_mustaches.append(l_mustache)
            if not l_dates:
                return ""
            l_stats_chart_content = self._generate_stats_chart_content(l_dates, l_harmonic_means, l_medians, l_medians_groupe, l_medians_low, l_means, l_mins, l_maxs)
            l_mmmm_chart_content = self._generate_mmmm_chart_content(l_dates, l_mins, l_means, l_medians, l_maxs)
            l_devs_chart_content = self._generate_pxxx_chart_content(l_dates, l_p_stdevs, l_stdevs)
            l_variances_chart_content = self._generate_pxxx_chart_content(l_dates, l_p_variances, l_variances)
            l_mustaches_graph_content = self._generate_mustaches_graph_content(l_dates, l_mustaches, l_mins, l_maxs)
            l_markdown = f"\n## {c_realm}\n\n" + \
                f"### Mustaches\n" + \
                f"\n" + \
                f"{l_mustaches_graph_content}\n" + \
                f"\n" \
                f"### Min-Mean-Median-Max\n" + \
                f"```chart\n" + \
                f"{l_mmmm_chart_content}\n" + \
                f"```\n" \
                f"### Stats\n" + \
                f"```chart\n" + \
                f"{l_stats_chart_content}\n" + \
                f"```\n" \
                f"### stdDev\n" + \
                f"```chart\n" + \
                f"{l_devs_chart_content}\n" + \
                f"```\n" \
                f"### Variance\n" + \
                f"```chart\n" + \
                f"{l_variances_chart_content}\n" + \
                f"```\n"
            return l_markdown
        return ""

    def _generate_auction_markdown(self, p_auctions, p_realm, p_timestamp):
        """Generate markdown content for a single auction file."""
        if not p_auctions:
            return ""
        l_markdown = "\n"
        print("---", p_realm, p_timestamp)
        for c_item_id, c_item_data in sorted(p_auctions.items()):
            l_item_name = self.m_items_db.get_by_id(c_item_id)
            if not l_item_name:
                continue
            l_markdown += f"## {l_item_name} ({c_item_id})\n\n"
            l_min_bid_data = c_item_data["minBid"]["counts_by_prices"]
            l_buyout_data = c_item_data["buyout"]["counts_by_prices"]
            if l_min_bid_data:
                l_markdown += "### Min Bid\n"
                l_markdown += "\n"
                l_markdown += self._generate_price_chart(l_min_bid_data)
                l_markdown += "\n\n"
            if l_buyout_data:
                l_markdown += "### Buyout\n"
                l_markdown += "\n"
                l_markdown += self._generate_price_chart(l_buyout_data)
                l_markdown += "\n\n"

        return l_markdown

    def _generate_price_chart(self, p_price_data: Dict) -> str:
        """
        Generate chart content for price vs item count.
        https://github.com/DylanHojnoski/obsidian-graphs
        """
        l_prices = []
        l_cumulative_item_counts = []
        l_cumul = 0
        for c_price, c_price_info in sorted(p_price_data.items(), key=lambda x: int(x[0])):
            l_item_count = c_price_info.get('item_count', 0)
            l_prices.append(c_price)
            l_cumul += l_item_count
            l_cumulative_item_counts.append(l_cumul)

        if not l_prices:
            return ""
        l_prices.sort()
        l_prices_to_count = dict(zip(l_prices, l_cumulative_item_counts))

        l_max_count = l_cumul
        if l_max_count < 10:
            l_max_count = 10
        elif l_max_count < 100:
            l_max_count = (2 + int(l_max_count / 10)) * 10
        else:
            l_max_count = (2 + int(l_max_count / 100)) * 100
        l_elements = []
        l_last_price = 0
        l_last_cumulative_item_count = 0
        for c_price, c_cumulative_item_count in l_prices_to_count.items():
            l_elements.append(f"{{type: segment, def: [[{l_last_price}, {l_last_cumulative_item_count}], [{c_price}, {l_last_cumulative_item_count}]]}}")
            l_elements.append(f"{{type: segment, def: [[{c_price}, {l_last_cumulative_item_count}], [{c_price}, {c_cumulative_item_count}]]}}")
            l_last_price = c_price
            l_last_cumulative_item_count = c_cumulative_item_count

        l_xmax = l_prices[-1] * 1.05
        l_ymax = l_max_count * 1.05
        return self.m_auction_chart_template.format(
            elements=',\n  '.join(l_elements),
            xmin=- l_xmax / 12,
            ymin=- l_ymax / 5,
            xmax=l_xmax,
            ymax=l_ymax,
        )

    def _load_template(self, p_filename: str) -> str:
        """Load template from file."""
        l_template_path = self.m_templates_dir / p_filename
        with open(l_template_path, 'r', encoding='utf-8') as l_file:
            return l_file.read()

    def _generate_index(self, p_index_items: List[str]) -> None:
        """Generate Auction Index.md file."""
        l_index_file = self.m_output_dir / 'Auction Index.md'
        l_index_content = "# Auction Index\n\n" + '\n'.join(sorted(p_index_items)) + '\n'

        with open(l_index_file, 'w', encoding='utf-8') as l_file:
            l_file.write(l_index_content)

    def _generate_stats_chart_content(self, p_dates, p_harmonic_means, p_medians, p_medians_groupe, p_medians_low, p_means, p_mins, p_maxs):
        """Generate chart content from dates and stats."""
        l_chart_labels = '","'.join(p_dates)
        l_means_str = ','.join('null' if p is None else str(p) for p in p_means)
        l_harmonics_str = ','.join('null' if p is None else str(p) for p in p_harmonic_means)
        l_medians_str = ','.join('null' if p is None else str(p) for p in p_medians)
        l_medians_groupe_str = ','.join('null' if p is None else str(p) for p in p_medians_groupe)
        l_medians_low_str = ','.join('null' if p is None else str(p) for p in p_medians_low)
        l_means_str = ','.join('null' if p is None else str(p) for p in p_means)

        return self.m_chart_avgs_template.format(
            labels=l_chart_labels,
            harmonics=l_harmonics_str,
            medians=l_medians_str,
            medians_groupe=l_medians_groupe_str,
            medians_low=l_medians_low_str,
            means=l_means_str,
        )

    def _generate_mmmm_chart_content(self, p_dates, p_mins, p_means, p_medians, p_maxs):
        """Generate chart content from dates and min-mean-median-max."""
        l_chart_labels = '","'.join(p_dates)
        l_mins_str = ','.join('null' if p is None else str(p) for p in p_mins)
        l_means_str = ','.join('null' if p is None else str(p) for p in p_means)
        l_medians_str = ','.join('null' if p is None else str(p) for p in p_medians)
        l_maxs_str = ','.join('null' if p is None else str(p) for p in p_maxs)

        return self.m_chart_mmmm_template.format(
            labels=l_chart_labels,
            mins=l_mins_str,
            means=l_means_str,
            medians=l_medians_str,
            maxs=l_maxs_str,
        )

    def _generate_pxxx_chart_content(self, p_dates, p_p_vals, p_vals):
        """Generate chart content from dates and p-values or values."""
        l_chart_labels = '","'.join(p_dates)
        l_p_vals_str = ','.join('null' if p is None else str(p) for p in p_p_vals)
        l_vals_str = ','.join('null' if p is None else str(p) for p in p_vals)

        return self.m_chart_pxxx_template.format(
            labels=l_chart_labels,
            p_vals=l_p_vals_str,
            vals=l_vals_str,
        )

    def _generate_mustaches_graph_content(self, p_dates, p_mustaches, p_mins, p_maxs):
        """Generate graph content from dates and mustaches, mins and maxs."""
        l_elements = []
        l_x_min_ts = datetime.strptime(p_dates[0], '%Y-%m-%d %H:%M').timestamp() * 0.99999
        l_x_max_ts = datetime.strptime(p_dates[-1], '%Y-%m-%d %H:%M').timestamp() * 1.00001
        for c_index, c_date in enumerate(p_dates):
            l_x = datetime.strptime(c_date, '%Y-%m-%d %H:%M').timestamp() - l_x_min_ts
            l_elements += self._draw_one_mustache(l_x, 10000, p_mustaches[c_index], p_mins[c_index], p_maxs[c_index])
        l_elements_str = ','.join(l_elements)
        l_xmax = (l_x_max_ts - l_x_min_ts)
        l_ymax = max(p_mins + p_maxs) * 1.05
        return self.m_graph_mustache_template.format(
            elements=l_elements_str,
            xmin=- l_xmax / 12,
            ymin=- l_ymax / 5,
            xmax=l_xmax,
            ymax=l_ymax,
        )

    def _draw_one_mustache(self, p_x, p_delta, p_mustache, p_min, p_max):
        """
        Draw one mustache.
        https://github.com/DylanHojnoski/obsidian-graphs
        """
        l_elements = []
        l_left = p_x - p_delta / 2
        l_right = p_x + p_delta / 2
        l_elements.append(f"{{type: segment, def: [[{l_left}, {p_min}], [{l_right}, {p_min}]]}}")                  # bottom line
        l_elements.append(f"{{type: segment, def: [[{l_left}, {p_max}], [{l_right}, {p_max}]]}}")                  # top line
        l_elements.append(f"{{type: segment, def: [[{l_left}, {p_mustache[0]}], [{l_right}, {p_mustache[0]}]]}}")  # q1 line
        l_elements.append(f"{{type: segment, def: [[{l_left}, {p_mustache[1]}], [{l_right}, {p_mustache[1]}]]}}")  # q2 line
        l_elements.append(f"{{type: segment, def: [[{l_left}, {p_mustache[2]}], [{l_right}, {p_mustache[2]}]]}}")  # q3 line
        l_elements.append(f"{{type: segment, def: [[{l_left}, {p_mustache[0]}], [{l_left}, {p_mustache[2]}]]}}")   # q1-q3 left vertical line
        l_elements.append(f"{{type: segment, def: [[{l_right}, {p_mustache[0]}], [{l_right}, {p_mustache[2]}]]}}") # q1-q3 right vertical line
        l_elements.append(f"{{type: segment, def: [[{p_x}, {p_min}], [{p_x}, {p_mustache[0]}]]}}")                 # bottom vertical line
        l_elements.append(f"{{type: segment, def: [[{p_x}, {p_max}], [{p_x}, {p_mustache[2]}]]}}")                 # top vertical line
        return l_elements
