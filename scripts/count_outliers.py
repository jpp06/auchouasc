
# NOT REVIEWED, FULL CURSOR

"""Count outliers for each timestamp in auctions.yaml."""

import sys
from pathlib import Path

import yaml


def count_outliers(p_auctions_file: Path) -> None:
    """Count outliers below Q1 - 1.5*IQR and above Q3 + 1.5*IQR."""
    with open(p_auctions_file, 'r', encoding='utf-8') as l_file:
        l_data = yaml.safe_load(l_file) or {}

    if not l_data:
        print("***", "No data found in auctions.yaml", file=sys.stderr)
        sys.exit(1)

    for c_realm, c_timestamps in l_data.items():
        print(f"\n=== {c_realm} ===")
        for c_timestamp, c_items in c_timestamps.items():
            l_total_lower_outliers = 0
            l_total_upper_outliers = 0
            l_total_items = 0
            l_items_with_outliers = []

            for c_item_id, c_item_data in c_items.items():
                l_buyout_data = c_item_data.get('buyout', {})
                l_quartiles = l_buyout_data.get('quartiles', [])

                if len(l_quartiles) < 3:
                    continue

                l_q1 = l_quartiles[0]
                l_q3 = l_quartiles[2]
                l_iqr = l_q3 - l_q1
                l_lower_fence = l_q1 - 1.5 * l_iqr
                l_upper_fence = l_q3 + 1.5 * l_iqr

                l_counts_by_prices = l_buyout_data.get('counts_by_prices', {})
                l_lower_count = 0
                l_upper_count = 0
                l_item_total = 0

                for c_price_str, c_price_data in l_counts_by_prices.items():
                    c_price = int(c_price_str)
                    l_item_count = c_price_data.get('item_count', 0)
                    l_item_total += l_item_count

                    if c_price < l_lower_fence:
                        l_lower_count += l_item_count
                    elif c_price > l_upper_fence:
                        l_upper_count += l_item_count

                l_total_items += l_item_total

                if l_lower_count > 0 or l_upper_count > 0:
                    l_items_with_outliers.append({
                        'id': c_item_id,
                        'lower': l_lower_count,
                        'upper': l_upper_count
                    })
                    l_total_lower_outliers += l_lower_count
                    l_total_upper_outliers += l_upper_count

            l_total_outliers = l_total_lower_outliers + l_total_upper_outliers
            l_outlier_percentage = (l_total_outliers / l_total_items * 100) if l_total_items > 0 else 0.0

            print(f"\n{c_timestamp}:")
            print(f"  Total items: {l_total_items}")
            print(f"  Lower outliers (< Q1 - 1.5*IQR): {l_total_lower_outliers}")
            print(f"  Upper outliers (> Q3 + 1.5*IQR): {l_total_upper_outliers}")
            print(f"  Total outliers: {l_total_outliers} ({l_outlier_percentage:.2f}%)")
            print(f"  Items with outliers: {len(l_items_with_outliers)}")

            if l_items_with_outliers:
                print("  Top items with outliers:")
                l_sorted_items = sorted(
                    l_items_with_outliers,
                    key=lambda x: x['lower'] + x['upper'],
                    reverse=True
                )
                for c_item in l_sorted_items[:10]:
                    print(f"    Item {c_item['id']}: "
                          f"lower={c_item['lower']}, "
                          f"upper={c_item['upper']}")


if __name__ == '__main__':
    l_script_dir = Path(__file__).parent
    l_project_root = l_script_dir.parent
    l_auctions_file = l_project_root / 'datas' / 'auctions.yaml'

    if not l_auctions_file.exists():
        print("***", f"File not found: {l_auctions_file}", file=sys.stderr)
        sys.exit(1)

    count_outliers(l_auctions_file)

