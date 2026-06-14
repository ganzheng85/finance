import pandas as pd
import yfinance as yf
from datetime import datetime
from collections import defaultdict, deque
import sys

# Read the CSV file
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
else:
    csv_file = 'trades_20260611 - Sheet1.csv'

df = pd.read_csv(csv_file)

# Clean up column names (remove spaces)
df.columns = df.columns.str.strip()

# Clean numeric columns (remove commas and convert to float)
df['Quantity of Units'] = pd.to_numeric(df['Quantity of Units'].astype(str).str.replace(',', ''), errors='coerce')
df['Amount per unit'] = pd.to_numeric(df['Amount per unit'].astype(str).str.replace(',', ''), errors='coerce')
df['Total Amount (before trading fees)'] = pd.to_numeric(df['Total Amount (before trading fees)'].astype(str).str.replace(',', ''), errors='coerce')

# Parse dates
df['Date'] = pd.to_datetime(df['Date (MM-DD-YYYY)'], format='%m-%d-%Y', errors='coerce')

# Show transaction type breakdown
print("Transaction Type Breakdown:")
transaction_counts = df['Transaction Type'].value_counts()
for trans_type, count in transaction_counts.items():
    print(f"  {trans_type}: {count}")
print()

# Filter out CASH$ and Dividend transactions for ticker analysis
trades_df = df[(df['Transaction Type'].isin(['Buy', 'Sell'])) & (df['Stock / ETF Symbol'] != 'CASH$')].copy()

print(f"After filtering (excluding Dividends and CASH$ transactions):")
print(f"  Total trades to analyze: {len(trades_df)}")
print(f"  Buy trades: {len(trades_df[trades_df['Transaction Type'] == 'Buy'])}")
print(f"  Sell trades: {len(trades_df[trades_df['Transaction Type'] == 'Sell'])}")
print()

# Get unique tickers
tickers = trades_df['Stock / ETF Symbol'].unique()
print(f"Found {len(tickers)} unique tickers: {sorted(tickers)}\n")

# Fetch current prices from Yahoo Finance
print("Fetching current prices from Yahoo Finance...")
current_prices = {}
failed_tickers = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d')
        if not hist.empty:
            current_prices[ticker] = hist['Close'].iloc[-1]
            print(f"  {ticker}: ${current_prices[ticker]:.2f}")
        else:
            print(f"  {ticker}: No data available")
            failed_tickers.append(ticker)
    except Exception as e:
        print(f"  {ticker}: Error - {str(e)}")
        failed_tickers.append(ticker)

print(f"\nSuccessfully fetched prices for {len(current_prices)}/{len(tickers)} tickers")
if failed_tickers:
    print(f"Failed tickers: {failed_tickers}\n")

# Analyze trades
print("\n" + "="*80)
print("TRADE ANALYSIS")
print("="*80)

buy_trades = []
sell_trades = []

for idx, row in trades_df.iterrows():
    ticker = row['Stock / ETF Symbol']
    transaction_type = row['Transaction Type']
    price = row['Amount per unit']
    quantity = row['Quantity of Units']
    date = row['Date']

    if ticker not in current_prices:
        continue

    current_price = current_prices[ticker]

    if transaction_type == 'Buy':
        # For buys, good if current price > buy price (unrealized gain)
        pct_change = ((current_price - price) / price) * 100
        is_good = pct_change > 0
        buy_trades.append({
            'ticker': ticker,
            'date': date,
            'buy_price': price,
            'current_price': current_price,
            'quantity': quantity,
            'pct_change': pct_change,
            'is_good': is_good
        })

    elif transaction_type == 'Sell':
        # For sells, good if current price < sell price (sold high)
        pct_change = ((price - current_price) / current_price) * 100
        is_good = pct_change > 0
        sell_trades.append({
            'ticker': ticker,
            'date': date,
            'sell_price': price,
            'current_price': current_price,
            'quantity': quantity,
            'pct_change': pct_change,
            'is_good': is_good
        })

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

total_buy_trades = len(buy_trades)
good_buy_trades = sum(1 for t in buy_trades if t['is_good'])
bad_buy_trades = total_buy_trades - good_buy_trades

total_sell_trades = len(sell_trades)
good_sell_trades = sum(1 for t in sell_trades if t['is_good'])
bad_sell_trades = total_sell_trades - good_sell_trades

print(f"\nBUY TRADES (currently held positions):")
print(f"  Total: {total_buy_trades}")
print(f"  Good (in profit): {good_buy_trades} ({good_buy_trades/total_buy_trades*100:.1f}%)")
print(f"  Bad (in loss): {bad_buy_trades} ({bad_buy_trades/total_buy_trades*100:.1f}%)")

print(f"\nSELL TRADES (sold positions):")
print(f"  Total: {total_sell_trades}")
print(f"  Good (sold higher than current): {good_sell_trades} ({good_sell_trades/total_sell_trades*100:.1f}%)")
print(f"  Bad (sold lower than current): {bad_sell_trades} ({bad_sell_trades/total_sell_trades*100:.1f}%)")

print(f"\nOVERALL:")
total_trades = total_buy_trades + total_sell_trades
good_trades = good_buy_trades + good_sell_trades
bad_trades = bad_buy_trades + bad_sell_trades
print(f"  Total trades analyzed: {total_trades}")
print(f"  Good trades: {good_trades} ({good_trades/total_trades*100:.1f}%)")
print(f"  Bad trades: {bad_trades} ({bad_trades/total_trades*100:.1f}%)")

# Top 10 best and worst trades
print("\n" + "="*80)
print("TOP 10 BEST BUY TRADES (biggest unrealized gains)")
print("="*80)
best_buys = sorted(buy_trades, key=lambda x: x['pct_change'], reverse=True)[:10]
for i, trade in enumerate(best_buys, 1):
    print(f"{i:2d}. {trade['ticker']:6s} | Bought: ${trade['buy_price']:8.2f} | Now: ${trade['current_price']:8.2f} | Gain: {trade['pct_change']:+6.2f}%")

print("\n" + "="*80)
print("TOP 10 WORST BUY TRADES (biggest unrealized losses)")
print("="*80)
worst_buys = sorted(buy_trades, key=lambda x: x['pct_change'])[:10]
for i, trade in enumerate(worst_buys, 1):
    print(f"{i:2d}. {trade['ticker']:6s} | Bought: ${trade['buy_price']:8.2f} | Now: ${trade['current_price']:8.2f} | Loss: {trade['pct_change']:+6.2f}%")

print("\n" + "="*80)
print("TOP 10 BEST SELL TRADES (sold at good prices vs current)")
print("="*80)
best_sells = sorted(sell_trades, key=lambda x: x['pct_change'], reverse=True)[:10]
for i, trade in enumerate(best_sells, 1):
    print(f"{i:2d}. {trade['ticker']:6s} | Sold: ${trade['sell_price']:8.2f} | Now: ${trade['current_price']:8.2f} | Avoided: {trade['pct_change']:+6.2f}%")

print("\n" + "="*80)
print("TOP 10 WORST SELL TRADES (sold too early)")
print("="*80)
worst_sells = sorted(sell_trades, key=lambda x: x['pct_change'])[:10]
for i, trade in enumerate(worst_sells, 1):
    print(f"{i:2d}. {trade['ticker']:6s} | Sold: ${trade['sell_price']:8.2f} | Now: ${trade['current_price']:8.2f} | Missed: {trade['pct_change']:+6.2f}%")

# Net position analysis using FIFO (First In First Out) methodology
print("\n" + "="*80)
print("CURRENT PORTFOLIO POSITIONS (Net holdings - FIFO cost basis)")
print("="*80)

# Sort trades chronologically for FIFO
trades_df_sorted = trades_df.sort_values('Date').reset_index(drop=True)

# Track buy lots using FIFO queues
buy_queues = defaultdict(deque)

for idx, row in trades_df_sorted.iterrows():
    ticker = row['Stock / ETF Symbol']
    transaction_type = row['Transaction Type']
    price = row['Amount per unit']
    quantity = row['Quantity of Units']

    if transaction_type == 'Buy':
        # Add to buy queue
        buy_queues[ticker].append({'price': price, 'quantity': quantity})
    elif transaction_type == 'Sell':
        # Match with oldest buys (FIFO)
        remaining_sell_qty = quantity
        while remaining_sell_qty > 0 and buy_queues[ticker]:
            oldest_buy = buy_queues[ticker][0]
            match_qty = min(remaining_sell_qty, oldest_buy['quantity'])

            # Reduce the oldest buy lot
            oldest_buy['quantity'] -= match_qty
            remaining_sell_qty -= match_qty

            # Remove if fully sold
            if oldest_buy['quantity'] <= 0:
                buy_queues[ticker].popleft()

# Calculate current holdings from remaining buy lots
current_holdings = {}
for ticker, buy_queue in buy_queues.items():
    if len(buy_queue) > 0 and ticker in current_prices:
        total_quantity = sum(lot['quantity'] for lot in buy_queue)
        total_cost = sum(lot['quantity'] * lot['price'] for lot in buy_queue)
        current_holdings[ticker] = {
            'quantity': total_quantity,
            'total_cost': total_cost,
            'buy_lots': list(buy_queue)
        }

print(f"\nCurrent holdings: {len(current_holdings)} tickers\n")
holdings_list = []

for ticker, pos in current_holdings.items():
    avg_cost = pos['total_cost'] / pos['quantity'] if pos['quantity'] > 0 else 0
    current_price = current_prices[ticker]
    current_value = current_price * pos['quantity']
    cost_basis = avg_cost * pos['quantity']
    unrealized_pnl = current_value - cost_basis
    pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0

    holdings_list.append({
        'ticker': ticker,
        'quantity': pos['quantity'],
        'avg_cost': avg_cost,
        'current_price': current_price,
        'cost_basis': cost_basis,
        'current_value': current_value,
        'unrealized_pnl': unrealized_pnl,
        'pnl_pct': pnl_pct
    })

# Sort by unrealized P&L percentage
holdings_list.sort(key=lambda x: x['pnl_pct'], reverse=True)

total_cost_basis = sum(h['cost_basis'] for h in holdings_list)
total_current_value = sum(h['current_value'] for h in holdings_list)
total_unrealized_pnl = total_current_value - total_cost_basis
total_pnl_pct = (total_unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0

print(f"{'Ticker':<8} {'Qty':>8} {'Avg Cost':>12} {'Current':>12} {'Value':>15} {'P&L':>15} {'%':>10}")
print("-" * 90)
for h in holdings_list:
    print(f"{h['ticker']:<8} {h['quantity']:>8.0f} ${h['avg_cost']:>11.2f} ${h['current_price']:>11.2f} ${h['current_value']:>14,.2f} ${h['unrealized_pnl']:>14,.2f} {h['pnl_pct']:>9.2f}%")

print("-" * 90)
print(f"{'TOTAL':<8} {'':<8} {'':<12} {'':<12} ${total_current_value:>14,.2f} ${total_unrealized_pnl:>14,.2f} {total_pnl_pct:>9.2f}%")
print(f"\nPortfolio Summary:")
print(f"  Total Cost Basis: ${total_cost_basis:,.2f}")
print(f"  Current Value: ${total_current_value:,.2f}")
print(f"  Unrealized P&L: ${total_unrealized_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
