"""
Fetch ERCOT data using GridStatus library
"""
import gridstatus
from datetime import datetime, timedelta
import pandas as pd
import json
import sys

def fetch_ercot_data(date_str="today"):
    """Fetch ERCOT data for the specified date"""

    print(f"Fetching ERCOT data using GridStatus for {date_str}...")

    iso = gridstatus.Ercot()

    data = {
        "date": date_str,
        "fetched_at": datetime.now().isoformat(),
        "raw": {},
        "analyses": {}
    }

    try:
        # Fetch real-time prices
        print("  Fetching real-time LMP prices...")
        rt_prices = iso.get_lmp(date=date_str, market="REAL_TIME_15_MIN")
        if rt_prices is not None and not rt_prices.empty:
            data["raw"]["rt_prices"] = rt_prices.to_dict(orient="records")
            print(f"    ✓ Got {len(rt_prices)} RT price records")
        else:
            print("    ✗ No RT price data")
    except Exception as e:
        print(f"    ✗ Error fetching RT prices: {e}")

    try:
        # Fetch day-ahead prices
        print("  Fetching day-ahead prices...")
        da_prices = iso.get_lmp(date=date_str, market="DAY_AHEAD_HOURLY")
        if da_prices is not None and not da_prices.empty:
            data["raw"]["da_prices"] = da_prices.to_dict(orient="records")
            print(f"    ✓ Got {len(da_prices)} DA price records")
        else:
            print("    ✗ No DA price data")
    except Exception as e:
        print(f"    ✗ Error fetching DA prices: {e}")

    try:
        # Fetch fuel mix
        print("  Fetching fuel mix...")
        fuel_mix = iso.get_fuel_mix(date=date_str)
        if fuel_mix is not None and not fuel_mix.empty:
            data["raw"]["fuel_mix"] = fuel_mix.to_dict(orient="records")
            print(f"    ✓ Got {len(fuel_mix)} fuel mix records")
        else:
            print("    ✗ No fuel mix data")
    except Exception as e:
        print(f"    ✗ Error fetching fuel mix: {e}")

    try:
        # Fetch load
        print("  Fetching load data...")
        load = iso.get_load(date=date_str)
        if load is not None and not load.empty:
            data["raw"]["load"] = load.to_dict(orient="records")
            print(f"    ✓ Got {len(load)} load records")
        else:
            print("    ✗ No load data")
    except Exception as e:
        print(f"    ✗ Error fetching load: {e}")

    try:
        # Fetch storage
        print("  Fetching storage data...")
        storage = iso.get_storage(date=date_str)
        if storage is not None and not storage.empty:
            data["raw"]["storage"] = storage.to_dict(orient="records")
            print(f"    ✓ Got {len(storage)} storage records")
        else:
            print("    ✗ No storage data")
    except Exception as e:
        print(f"    ✗ Error fetching storage: {e}")

    # Save raw data
    output_file = f"data/ercot_gridstatus_{date_str}.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✓ Data saved to {output_file}")

    return data

if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else "today"
    fetch_ercot_data(date_str)
