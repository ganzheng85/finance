"""
ERCOT Market Data Fetcher
Fetches real-time and historical ERCOT market data for daily analysis.

Usage:
    python fetch_ercot_data.py --date 2026-06-04
    python fetch_ercot_data.py --date today
    python fetch_ercot_data.py --date 2026-06-04 --output data/ --format json

Requirements:
    pip install gridstatus pandas requests pytz python-dateutil
"""

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CENTRAL_TZ = ZoneInfo("America/Chicago")
ERCOT_API_BASE = "https://api.ercot.com/api/public-reports"

# ERCOT public report endpoint codes
ERCOT_REPORTS = {
    "rt_prices":        "NP6-785-CD",   # Real-Time Settlement Point Prices (15-min)
    "da_prices":        "NP6-905-CD",   # Day-Ahead Market Settlement Point Prices
    "system_conditions":"NP3-911-ER",   # Real-Time System Conditions (load, reserves)
    "outages":          "NP4-732-CD",   # Hourly Resource Outage Capacity
    "generation_mix":   "NP4-160-CD",   # Generation by Fuel Type
    "shadow_prices":    "NP6-86-CD",    # Shadow Prices of Binding Constraints
    "wind_actual":      "NP4-742-CD",   # Wind Power Production Actual
    "solar_actual":     "NP4-745-CD",   # Solar Power Production Actual
    "bess_dispatch":    "NP4-188-CD",   # Battery Storage Dispatch
}

# Hub and zone settlement points of interest
HUBS = ["HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HOUSTON", "HB_HUBAVG"]
LOAD_ZONES = ["LZ_NORTH", "LZ_SOUTH", "LZ_WEST", "LZ_HOUSTON"]

# Installed capacity reference (approximate, update as needed)
ERCOT_INSTALLED_CAPACITY_MW = {
    "wind": 40_000,
    "solar": 25_000,
    "battery": 5_000,
}


# ---------------------------------------------------------------------------
# Date utilities
# ---------------------------------------------------------------------------

def resolve_date(date_str: str) -> date:
    """Parse date string; 'today' returns today in Central Time."""
    if date_str.lower() == "today":
        return datetime.now(tz=CENTRAL_TZ).date()
    return date.fromisoformat(date_str)


def date_range_params(target_date: date) -> dict:
    """Return API query params for a full UTC day covering Central Time date."""
    # ERCOT timestamps are in CT; cover full calendar day
    return {
        "deliveredDateFrom": target_date.isoformat(),
        "deliveredDateTo": target_date.isoformat(),
    }


# ---------------------------------------------------------------------------
# ERCOT Public API client
# ---------------------------------------------------------------------------

def ercot_api_get(report_code: str, params: dict, max_retries: int = 3) -> list[dict]:
    """
    Fetch data from ERCOT Public API for a given report code.
    Returns list of record dicts, or empty list on failure.
    """
    url = f"{ERCOT_API_BASE}/{report_code}"
    headers = {"Accept": "application/json"}

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # ERCOT API wraps records in different shapes — handle both
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # Common shapes: {"data": [...]} or {"_embedded": {"_doc": [...]}}
                for key in ("data", "records", "_doc"):
                    if key in data:
                        return data[key]
                embedded = data.get("_embedded", {})
                for key in embedded:
                    if isinstance(embedded[key], list):
                        return embedded[key]
            return []
        except requests.exceptions.HTTPError as e:
            print(f"  HTTP error on attempt {attempt}/{max_retries}: {e}", file=sys.stderr)
            if attempt < max_retries:
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            print(f"  Request error on attempt {attempt}/{max_retries}: {e}", file=sys.stderr)
            if attempt < max_retries:
                time.sleep(2 ** attempt)

    print(f"  Failed to fetch {report_code} after {max_retries} attempts.", file=sys.stderr)
    return []


# ---------------------------------------------------------------------------
# GridStatus fallback (optional)
# ---------------------------------------------------------------------------

def fetch_via_gridstatus(target_date: date) -> dict:
    """
    Fallback: fetch fuel mix and prices via the gridstatus library.
    Returns partial dataset (prices + fuel_mix).
    """
    try:
        import gridstatus  # noqa: PLC0415
    except ImportError:
        print("  gridstatus not installed. Skipping fallback.", file=sys.stderr)
        return {}

    iso = gridstatus.Ercot()
    result = {}

    try:
        fuel_mix = iso.get_fuel_mix(date=str(target_date))
        if fuel_mix is not None and not fuel_mix.empty:
            result["fuel_mix"] = fuel_mix.to_dict(orient="records")
            print("  [gridstatus] Fuel mix: OK")
    except Exception as e:  # noqa: BLE001
        print(f"  [gridstatus] Fuel mix failed: {e}", file=sys.stderr)

    try:
        rt_prices = iso.get_lmp(date=str(target_date), market="REAL_TIME_15_MIN")
        if rt_prices is not None and not rt_prices.empty:
            result["rt_prices_gs"] = rt_prices.to_dict(orient="records")
            print("  [gridstatus] RT prices: OK")
    except Exception as e:  # noqa: BLE001
        print(f"  [gridstatus] RT prices failed: {e}", file=sys.stderr)

    try:
        da_prices = iso.get_lmp(date=str(target_date), market="DAY_AHEAD_HOURLY")
        if da_prices is not None and not da_prices.empty:
            result["da_prices_gs"] = da_prices.to_dict(orient="records")
            print("  [gridstatus] DA prices: OK")
    except Exception as e:  # noqa: BLE001
        print(f"  [gridstatus] DA prices failed: {e}", file=sys.stderr)

    return result


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def analyze_rt_prices(records: list[dict]) -> dict:
    """
    Compute price spike and volatility metrics from RT settlement point prices.
    Expects records with fields: settlementPoint, settlementPointPrice, deliveryDate, deliveryHour, deliveryInterval
    """
    if not records:
        return {"error": "No RT price data available"}

    df = pd.DataFrame(records)

    # Normalise column names to lower case
    df.columns = [c.lower() for c in df.columns]

    price_col = next((c for c in df.columns if "price" in c.lower()), None)
    point_col = next((c for c in df.columns if "settlementpoint" in c.lower() or "point" in c.lower()), None)
    hour_col  = next((c for c in df.columns if "hour" in c.lower()), None)

    if price_col is None or point_col is None:
        return {"error": f"Unexpected columns: {list(df.columns)}"}

    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[price_col])

    hub_df = df[df[point_col].isin(HUBS)]

    metrics: dict = {}

    if hub_df.empty:
        # Try all points if hub filter returns nothing
        hub_df = df

    # Per-hub summary
    hub_summary = {}
    for hub, grp in hub_df.groupby(point_col):
        prices = grp[price_col]
        hub_summary[str(hub)] = {
            "mean":  round(float(prices.mean()), 2),
            "std":   round(float(prices.std()), 2),
            "min":   round(float(prices.min()), 2),
            "max":   round(float(prices.max()), 2),
            "spread": round(float(prices.max() - prices.min()), 2),
            "cv_pct": round(float(prices.std() / prices.mean() * 100), 1) if prices.mean() != 0 else None,
            "pct_above_100":  round(float((prices > 100).mean() * 100), 1),
            "pct_above_500":  round(float((prices > 500).mean() * 100), 1),
            "pct_above_2000": round(float((prices > 2000).mean() * 100), 1),
            "pct_negative":   round(float((prices < 0).mean() * 100), 1),
            "intervals_total": len(prices),
        }

    metrics["hub_summary"] = hub_summary

    # Spike events (>$500/MWh)
    spikes = hub_df[hub_df[price_col] > 500].copy()
    if not spikes.empty:
        spike_records = spikes[[point_col, price_col] + ([hour_col] if hour_col else [])].copy()
        spike_records = spike_records.sort_values(price_col, ascending=False).head(20)
        metrics["spike_events"] = spike_records.to_dict(orient="records")
    else:
        metrics["spike_events"] = []

    # Negative price events
    negatives = hub_df[hub_df[price_col] < 0].copy()
    if not negatives.empty:
        neg_records = negatives[[point_col, price_col] + ([hour_col] if hour_col else [])].copy()
        neg_records = neg_records.sort_values(price_col).head(20)
        metrics["negative_price_events"] = neg_records.to_dict(orient="records")
    else:
        metrics["negative_price_events"] = []

    # Overall volatility classification
    all_hub_prices = hub_df[price_col]
    overall_std = float(all_hub_prices.std())
    overall_spread = float(all_hub_prices.max() - all_hub_prices.min())

    if overall_std < 20:
        volatility_level = "LOW"
    elif overall_std < 100:
        volatility_level = "MODERATE"
    elif overall_std < 500:
        volatility_level = "HIGH"
    else:
        volatility_level = "EXTREME"

    metrics["volatility_classification"] = volatility_level
    metrics["overall_std"] = round(overall_std, 2)
    metrics["overall_spread"] = round(overall_spread, 2)

    # Spike classification
    max_price = float(hub_df[price_col].max())
    if max_price < 100:
        spike_level = "NONE"
    elif max_price < 500:
        spike_level = "MINOR"
    elif max_price < 2000:
        spike_level = "SIGNIFICANT"
    else:
        spike_level = "EXTREME"

    metrics["spike_classification"] = spike_level
    metrics["max_rt_price"] = round(max_price, 2)

    return metrics


def analyze_fuel_mix(records: list[dict]) -> dict:
    """
    Compute renewable contribution and battery storage metrics from generation mix data.
    """
    if not records:
        return {"error": "No fuel mix data available"}

    df = pd.DataFrame(records)
    df.columns = [c.lower() for c in df.columns]

    # Find fuel type and generation columns
    fuel_col = next((c for c in df.columns if "fuel" in c.lower() or "type" in c.lower()), None)
    gen_col  = next((c for c in df.columns if "gen" in c.lower() or "mw" in c.lower() or "output" in c.lower()), None)

    if fuel_col is None or gen_col is None:
        return {"error": f"Cannot identify columns. Available: {list(df.columns)}"}

    df[gen_col] = pd.to_numeric(df[gen_col], errors="coerce")
    df = df.dropna(subset=[gen_col])

    # Normalise fuel type names
    df[fuel_col] = df[fuel_col].str.lower().str.strip()

    # Map to canonical fuel categories
    fuel_map = {
        "wind": ["wind"],
        "solar": ["solar", "pvgr"],
        "gas":   ["gas", "natural gas", "ng", "gas-cc", "gas-ct", "gas cc", "gas ct"],
        "nuclear": ["nuclear", "nuc"],
        "coal":  ["coal", "lignite"],
        "hydro": ["hydro", "water", "hyd"],
        "battery": ["battery", "bess", "storage", "bat"],
        "other": ["other", "biomass", "bio", "fuel oil", "oil"],
    }

    def map_fuel(fuel_str: str) -> str:
        for canonical, aliases in fuel_map.items():
            if any(a in fuel_str for a in aliases):
                return canonical
        return "other"

    df["fuel_canonical"] = df[fuel_col].apply(map_fuel)

    # Aggregate by fuel type
    by_fuel = df.groupby("fuel_canonical")[gen_col].agg(["mean", "max", "min", "sum"]).round(1)
    total_mean = float(by_fuel["mean"].sum())

    fuel_summary = {}
    for fuel, row in by_fuel.iterrows():
        share = round(float(row["mean"]) / total_mean * 100, 1) if total_mean > 0 else 0
        fuel_summary[str(fuel)] = {
            "avg_mw":  float(row["mean"]),
            "peak_mw": float(row["max"]),
            "min_mw":  float(row["min"]),
            "total_mwh": float(row["sum"]),
            "daily_share_pct": share,
        }

    wind_mw   = fuel_summary.get("wind",    {}).get("avg_mw", 0)
    solar_mw  = fuel_summary.get("solar",   {}).get("avg_mw", 0)
    battery_mw = fuel_summary.get("battery", {}).get("avg_mw", 0)
    renew_share = round((wind_mw + solar_mw) / total_mean * 100, 1) if total_mean > 0 else 0

    # Renewable classification
    if renew_share < 30:
        renew_level = "LOW"
    elif renew_share < 50:
        renew_level = "MODERATE"
    elif renew_share < 70:
        renew_level = "HIGH"
    else:
        renew_level = "RECORD"

    # Wind capacity factor
    wind_cap = ERCOT_INSTALLED_CAPACITY_MW["wind"]
    solar_cap = ERCOT_INSTALLED_CAPACITY_MW["solar"]
    wind_cf   = round(wind_mw / wind_cap * 100, 1) if wind_cap > 0 else None
    solar_cf  = round(solar_mw / solar_cap * 100, 1) if solar_cap > 0 else None

    return {
        "fuel_summary": fuel_summary,
        "total_avg_mw": round(total_mean, 1),
        "renewable_share_pct": renew_share,
        "renewable_classification": renew_level,
        "wind_capacity_factor_pct": wind_cf,
        "solar_capacity_factor_pct": solar_cf,
        "battery_avg_mw": round(battery_mw, 1),
    }


def analyze_outages(records: list[dict]) -> dict:
    """
    Summarise generator outage data.
    """
    if not records:
        return {"error": "No outage data available"}

    df = pd.DataFrame(records)
    df.columns = [c.lower() for c in df.columns]

    # Find relevant columns
    forced_col  = next((c for c in df.columns if "forced" in c.lower()), None)
    planned_col = next((c for c in df.columns if "planned" in c.lower() or "sched" in c.lower()), None)
    total_col   = next((c for c in df.columns if "total" in c.lower() and "out" in c.lower()), None)
    cap_col     = next((c for c in df.columns if "avail" in c.lower() or "cap" in c.lower()), None)

    summary = {"raw_columns": list(df.columns)}

    for col in [forced_col, planned_col, total_col, cap_col]:
        if col:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if forced_col:
        summary["max_forced_outages_mw"] = round(float(df[forced_col].max()), 0)
        summary["avg_forced_outages_mw"] = round(float(df[forced_col].mean()), 0)

    if planned_col:
        summary["avg_planned_outages_mw"] = round(float(df[planned_col].mean()), 0)

    if total_col:
        summary["max_total_outages_mw"] = round(float(df[total_col].max()), 0)

    if cap_col:
        summary["avg_available_capacity_mw"] = round(float(df[cap_col].mean()), 0)

    return summary


def analyze_congestion(records: list[dict]) -> dict:
    """
    Summarise shadow prices of binding transmission constraints.
    """
    if not records:
        return {"error": "No congestion data available"}

    df = pd.DataFrame(records)
    df.columns = [c.lower() for c in df.columns]

    shadow_col      = next((c for c in df.columns if "shadow" in c.lower() or "price" in c.lower()), None)
    constraint_col  = next((c for c in df.columns if "constraint" in c.lower() or "name" in c.lower()), None)

    if shadow_col is None:
        return {"error": f"Cannot find shadow price column. Available: {list(df.columns)}"}

    df[shadow_col] = pd.to_numeric(df[shadow_col], errors="coerce").abs()
    df = df.dropna(subset=[shadow_col])
    df_nonzero = df[df[shadow_col] > 0]

    if df_nonzero.empty:
        return {"congestion_classification": "NONE", "active_constraints": []}

    max_shadow = float(df_nonzero[shadow_col].max())

    if max_shadow < 5:
        congestion_level = "NONE"
    elif max_shadow < 25:
        congestion_level = "MINOR"
    elif max_shadow < 100:
        congestion_level = "MODERATE"
    else:
        congestion_level = "SEVERE"

    # Top constraints
    if constraint_col:
        top = (
            df_nonzero.groupby(constraint_col)[shadow_col]
            .agg(["max", "mean", "count"])
            .sort_values("max", ascending=False)
            .head(10)
            .reset_index()
        )
        top_list = top.to_dict(orient="records")
    else:
        top_list = []

    return {
        "congestion_classification": congestion_level,
        "max_shadow_price": round(max_shadow, 2),
        "avg_shadow_price_nonzero": round(float(df_nonzero[shadow_col].mean()), 2),
        "total_constrained_intervals": len(df_nonzero),
        "active_constraints": top_list,
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def fetch_all(target_date: date, use_gridstatus: bool = True) -> dict:
    """Fetch all available ERCOT data for the target date."""
    params = date_range_params(target_date)
    print(f"\nFetching ERCOT data for {target_date} ...")
    result: dict = {"date": target_date.isoformat(), "fetched_at_ct": datetime.now(tz=CENTRAL_TZ).isoformat()}
    raw: dict = {}

    for name, code in ERCOT_REPORTS.items():
        print(f"  [{name}] {code} ...", end=" ")
        records = ercot_api_get(code, params)
        if records:
            raw[name] = records
            print(f"OK ({len(records)} records)")
        else:
            print("NO DATA")

    # Fallback: try gridstatus for any missing critical datasets
    if use_gridstatus and ("rt_prices" not in raw or "generation_mix" not in raw):
        print("\n  Trying GridStatus fallback ...")
        gs_data = fetch_via_gridstatus(target_date)
        raw.update(gs_data)

    result["raw"] = raw

    # Run analyses
    print("\nRunning analyses ...")
    analyses: dict = {}

    rt_records = raw.get("rt_prices") or raw.get("rt_prices_gs", [])
    fuel_records = raw.get("generation_mix") or raw.get("fuel_mix", [])

    if rt_records:
        analyses["prices"] = analyze_rt_prices(rt_records)
    if fuel_records:
        analyses["renewables_and_storage"] = analyze_fuel_mix(fuel_records)
    if "outages" in raw:
        analyses["outages"] = analyze_outages(raw["outages"])
    if "shadow_prices" in raw:
        analyses["congestion"] = analyze_congestion(raw["shadow_prices"])

    result["analyses"] = analyses
    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_output(data: dict, output_dir: str, fmt: str = "json") -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    target_date = data.get("date", "unknown")

    if fmt == "json":
        file_path = out_path / f"ercot_{target_date}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\nSaved: {file_path}")

    elif fmt == "csv":
        analyses = data.get("analyses", {})
        for key, content in analyses.items():
            if isinstance(content, dict) and "error" not in content:
                file_path = out_path / f"ercot_{target_date}_{key}.csv"
                try:
                    pd.DataFrame([content]).to_csv(file_path, index=False)
                    print(f"Saved: {file_path}")
                except Exception as e:  # noqa: BLE001
                    print(f"  Could not save {key} as CSV: {e}", file=sys.stderr)
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def print_summary(data: dict) -> None:
    """Print a brief console summary of analysis results."""
    print("\n" + "=" * 60)
    print(f"ERCOT MARKET SUMMARY — {data.get('date', 'unknown')}")
    print("=" * 60)

    analyses = data.get("analyses", {})

    prices = analyses.get("prices", {})
    if prices and "error" not in prices:
        print(f"\nPrice Spikes:   {prices.get('spike_classification', 'N/A')} "
              f"(max ${prices.get('max_rt_price', 'N/A')}/MWh)")
        print(f"Volatility:     {prices.get('volatility_classification', 'N/A')} "
              f"(stddev ${prices.get('overall_std', 'N/A')}/MWh, "
              f"spread ${prices.get('overall_spread', 'N/A')}/MWh)")

    renew = analyses.get("renewables_and_storage", {})
    if renew and "error" not in renew:
        fs = renew.get("fuel_summary", {})
        wind_avg = fs.get("wind", {}).get("avg_mw", "N/A")
        solar_avg = fs.get("solar", {}).get("avg_mw", "N/A")
        print(f"\nRenewable Share: {renew.get('renewable_share_pct', 'N/A')}% "
              f"({renew.get('renewable_classification', 'N/A')})")
        print(f"  Wind:  {wind_avg} MW avg  "
              f"(CF: {renew.get('wind_capacity_factor_pct', 'N/A')}%)")
        print(f"  Solar: {solar_avg} MW avg  "
              f"(CF: {renew.get('solar_capacity_factor_pct', 'N/A')}%)")
        print(f"  Battery: {renew.get('battery_avg_mw', 'N/A')} MW avg dispatch")

    outages = analyses.get("outages", {})
    if outages and "error" not in outages:
        print(f"\nOutages: max forced {outages.get('max_forced_outages_mw', 'N/A')} MW")

    congestion = analyses.get("congestion", {})
    if congestion and "error" not in congestion:
        print(f"\nCongestion:     {congestion.get('congestion_classification', 'N/A')} "
              f"(max shadow ${congestion.get('max_shadow_price', 'N/A')}/MWh)")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and analyze ERCOT market data for a given date."
    )
    parser.add_argument(
        "--date", default="today",
        help="Date to fetch (YYYY-MM-DD or 'today'). Default: today in Central Time."
    )
    parser.add_argument(
        "--output", default="data",
        help="Output directory for saved data files. Default: data/"
    )
    parser.add_argument(
        "--format", choices=["json", "csv"], default="json",
        help="Output file format. Default: json"
    )
    parser.add_argument(
        "--no-gridstatus", action="store_true",
        help="Disable GridStatus fallback."
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="Print summary only, do not save output files."
    )
    args = parser.parse_args()

    target_date = resolve_date(args.date)
    use_gs = not args.no_gridstatus

    data = fetch_all(target_date, use_gridstatus=use_gs)
    print_summary(data)

    if not args.no_save:
        save_output(data, args.output, fmt=args.format)


if __name__ == "__main__":
    main()
