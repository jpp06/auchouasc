
# NOT REVIEWED, FULL CURSOR

"""Migrate AHScanner.lua files to new structure (by realm and item name)."""

import sys
from pathlib import Path
from collections import defaultdict

# Add src to path
l_script_dir = Path(__file__).parent
l_project_root = l_script_dir.parent
sys.path.insert(0, str(l_project_root / 'src'))

from lupa import LuaRuntime


def load_lua_data(p_file_path: Path):
    """Load AHScannerDB from Lua file using lupa."""
    with open(p_file_path, 'r', encoding='utf-8') as l_file:
        l_content = l_file.read()

    l_lua = LuaRuntime(unpack_returned_tuples=True)
    l_lua.execute(l_content)
    l_globals = l_lua.globals()

    if 'AHScannerDB' not in l_globals:
        raise ValueError("AHScannerDB not found in Lua file")

    l_ahscanner_db = l_globals['AHScannerDB']
    return lua_to_python(l_ahscanner_db)


def lua_to_python(p_value):
    """Convert Lua object to Python object."""
    if p_value is None:
        return None
    if isinstance(p_value, (int, float, str, bool)):
        return p_value
    if hasattr(p_value, 'items'):
        l_result = {}
        for c_key, c_val in p_value.items():
            l_py_key = lua_to_python(c_key)
            l_py_val = lua_to_python(c_val)
            l_result[l_py_key] = l_py_val
        return l_result
    if hasattr(p_value, '__iter__') and not isinstance(p_value, str):
        return [lua_to_python(c_item) for c_item in p_value]
    return p_value


def write_new_structure(p_file_path: Path, p_realm: str, p_items_by_name: dict):
    """Write new structure to file."""
    l_lines = ['', 'AHScannerDB = {', f'\t["{p_realm}"] = {{']

    for c_item_name in sorted(p_items_by_name.keys()):
        l_lines.append(f'\t\t["{c_item_name}"] = {{')
        l_lines.append('\t\t\t["sales"] = {')
        for c_idx, c_item in enumerate(p_items_by_name[c_item_name], 1):
            l_lines.append('\t\t\t\t{')
            l_lines.append(f'\t\t\t\t\t["buyoutUnit"] = {c_item.get("buyoutUnit", 0)},')
            l_lines.append(f'\t\t\t\t\t["seller"] = "{c_item.get("seller", "Unknown")}",')
            l_lines.append(f'\t\t\t\t\t["bidAmount"] = {c_item.get("bidAmount", 0)},')
            l_lines.append(f'\t\t\t\t\t["count"] = {c_item.get("count", 0)},')
            l_lines.append(f'\t\t\t\t\t["buyout"] = {c_item.get("buyout", 0)},')
            l_lines.append(f'\t\t\t\t\t["name"] = "{c_item.get("name", "")}",')
            l_lines.append(f'\t\t\t\t\t["minBid"] = {c_item.get("minBid", 0)},')
            l_lines.append(f'\t\t\t\t\t["minIncrement"] = {c_item.get("minIncrement", 0)},')
            l_lines.append(f'\t\t\t\t\t["level"] = {c_item.get("level", 0)},')
            l_lines.append(f'\t\t\t\t\t["minBidUnit"] = {c_item.get("minBidUnit", 0)},')
            l_lines.append(f'\t\t\t\t\t["quality"] = {c_item.get("quality", 0)},')
            l_lines.append('\t\t\t\t}, -- [' + str(c_idx) + ']')
        l_lines.append('\t\t\t},')
        l_lines.append('\t\t},')

    l_lines.append('\t},')
    l_lines.append('}')

    with open(p_file_path, 'w', encoding='utf-8') as l_file:
        l_file.write('\n'.join(l_lines))


def migrate_file(p_file_path: Path) -> bool:
    """Migrate a single AHScanner.lua file."""
    print(f"--- Migrating {p_file_path.name}")

    try:
        l_data = load_lua_data(p_file_path)

        # Extract items from scans structure
        l_scans = l_data.get('scans', {})
        if not l_scans:
            print(f"*** No scans found in {p_file_path.name}")
            return False

        l_items = []
        l_realm = "Bronzebeard - Warcraft Reborn"

        # Handle both dict and list formats for scans
        if isinstance(l_scans, dict):
            l_scans_list = list(l_scans.values())
        else:
            l_scans_list = l_scans if isinstance(l_scans, list) else [l_scans]

        for c_scan in l_scans_list:
            l_scan_items = c_scan.get('items', {})
            if isinstance(l_scan_items, dict):
                l_scan_items = list(l_scan_items.values())
            elif not isinstance(l_scan_items, list):
                l_scan_items = [l_scan_items]

            for c_item in l_scan_items:
                if not isinstance(c_item, dict):
                    continue

                # Calculate units if not present
                l_count = c_item.get('count', 0)
                l_buyout = c_item.get('buyout', 0)
                l_min_bid = c_item.get('minBid', 0)

                if 'buyoutUnit' not in c_item and l_count > 0:
                    c_item['buyoutUnit'] = l_buyout // l_count
                if 'minBidUnit' not in c_item and l_count > 0:
                    c_item['minBidUnit'] = l_min_bid // l_count

                l_items.append(c_item)

        if not l_items:
            print(f"*** No items found in {p_file_path.name}")
            return False

        # Group items by name
        l_items_by_name = defaultdict(list)
        for c_item in l_items:
            l_item_name = c_item.get('name')
            if l_item_name:
                l_items_by_name[l_item_name].append(c_item)

        # Write new structure
        write_new_structure(p_file_path, l_realm, l_items_by_name)
        print(f"--- Migrated {len(l_items)} items for {len(l_items_by_name)} item types")
        return True

    except Exception as l_e:
        print(f"*** Error migrating {p_file_path.name}: {l_e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    l_script_dir = Path(__file__).parent
    l_project_root = l_script_dir.parent
    l_dailies_dir = l_project_root / 'dailies'
    l_reference_file = l_dailies_dir / '2025_11_17T14_18_16' / 'AHScanner.lua'

    if not l_dailies_dir.exists():
        print("***", f"Dailies directory not found: {l_dailies_dir}", file=sys.stderr)
        sys.exit(1)

    l_migrated = 0
    l_failed = 0

    for c_subdir in sorted(l_dailies_dir.iterdir()):
        if not c_subdir.is_dir():
            continue

        l_ahscanner_file = c_subdir / 'AHScanner.lua'
        if not l_ahscanner_file.exists():
            continue

        # Skip reference file
        if l_ahscanner_file == l_reference_file:
            print(f"--- Skipping reference file: {l_ahscanner_file.name}")
            continue

        if migrate_file(l_ahscanner_file):
            l_migrated += 1
        else:
            l_failed += 1

    print(f"\n=== Migration complete: {l_migrated} migrated, {l_failed} failed")


if __name__ == '__main__':
    main()
