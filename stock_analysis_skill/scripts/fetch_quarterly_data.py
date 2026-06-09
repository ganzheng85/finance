#!/usr/bin/env python3
"""
Fetch quarterly financial data from yfinance for any stock

Usage:
    python fetch_quarterly_data.py META
    python fetch_quarterly_data.py MSFT
    python fetch_quarterly_data.py AAPL --quarters 8
    python fetch_quarterly_data.py NVDA --export
"""

import yfinance as yf
import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description='Fetch quarterly financial data for a stock ticker'
    )
    parser.add_argument('ticker', type=str, help='Stock ticker symbol (e.g., META, MSFT, AAPL)')
    parser.add_argument('--quarters', type=int, default=13, help='Number of quarters to display (default: 13)')
    parser.add_argument('--export', action='store_true', help='Export to CSV files')

    args = parser.parse_args()

    ticker_symbol = args.ticker.upper()
    num_quarters = args.quarters

    print(f"Fetching quarterly data for {ticker_symbol}...")

    try:
        # Fetch data
        ticker = yf.Ticker(ticker_symbol)

        # Get quarterly financials
        quarterly_income = ticker.quarterly_income_stmt
        quarterly_balance = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cashflow

        # Get stock info for additional metrics
        info = ticker.info

        print("="*80)
        print(f"{ticker_symbol} QUARTERLY FINANCIAL DATA (Most Recent {num_quarters} Quarters)")
        print("="*80)

        print("\n" + "="*80)
        print("INCOME STATEMENT (Quarterly)")
        print("="*80)
        if quarterly_income is not None and not quarterly_income.empty:
            print(quarterly_income.head(num_quarters).to_string())
        else:
            print("No quarterly income statement data available")

        print("\n" + "="*80)
        print("BALANCE SHEET (Quarterly)")
        print("="*80)
        if quarterly_balance is not None and not quarterly_balance.empty:
            print(quarterly_balance.head(num_quarters).to_string())
        else:
            print("No quarterly balance sheet data available")

        print("\n" + "="*80)
        print("CASH FLOW (Quarterly)")
        print("="*80)
        if quarterly_cashflow is not None and not quarterly_cashflow.empty:
            print(quarterly_cashflow.head(num_quarters).to_string())
        else:
            print("No quarterly cash flow data available")

        print("\n" + "="*80)
        print("KEY METRICS")
        print("="*80)
        print(f"Current Price: ${info.get('currentPrice', 'N/A')}")
        print(f"Market Cap: ${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else "Market Cap: N/A")
        print(f"Trailing P/E: {info.get('trailingPE', 'N/A')}")
        print(f"Forward P/E: {info.get('forwardPE', 'N/A')}")
        print(f"Trailing EPS: ${info.get('trailingEps', 'N/A')}")
        print(f"Forward EPS: ${info.get('forwardEps', 'N/A')}")

        # Export to CSV if requested
        if args.export:
            # Create data directory structure: data/{TICKER}/
            script_dir = Path(__file__).parent
            data_dir = script_dir.parent / "data" / ticker_symbol
            data_dir.mkdir(parents=True, exist_ok=True)

            if quarterly_income is not None and not quarterly_income.empty:
                filename = data_dir / f"{ticker_symbol.lower()}_quarterly_income.csv"
                quarterly_income.to_csv(filename)
                print(f"\nExported income statement to {filename}")

            if quarterly_balance is not None and not quarterly_balance.empty:
                filename = data_dir / f"{ticker_symbol.lower()}_quarterly_balance.csv"
                quarterly_balance.to_csv(filename)
                print(f"Exported balance sheet to {filename}")

            if quarterly_cashflow is not None and not quarterly_cashflow.empty:
                filename = data_dir / f"{ticker_symbol.lower()}_quarterly_cashflow.csv"
                quarterly_cashflow.to_csv(filename)
                print(f"Exported cash flow to {filename}")

        return 0

    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
