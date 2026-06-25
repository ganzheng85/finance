import pandas as pd
from datetime import datetime
from collections import defaultdict, deque
import sys

# Read the CSV file
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
else:
    csv_file = 'trades_20260611 - Sheet1.csv'

df = pd.read_csv(csv_file)

# Clean up column names
df.columns = df.columns.str.strip()

# Normalize ticker symbols to uppercase (fix case sensitivity bug)
df['Stock / ETF Symbol'] = df['Stock / ETF Symbol'].str.strip().str.upper()

# Clean numeric columns
df['Quantity of Units'] = pd.to_numeric(df['Quantity of Units'].astype(str).str.replace(',', ''), errors='coerce')
df['Amount per unit'] = pd.to_numeric(df['Amount per unit'].astype(str).str.replace(',', ''), errors='coerce')
df['Total Amount (before trading fees)'] = pd.to_numeric(df['Total Amount (before trading fees)'].astype(str).str.replace(',', ''), errors='coerce')

# Parse dates
df['Date'] = pd.to_datetime(df['Date (MM-DD-YYYY)'], format='%m-%d-%Y', errors='coerce')

# Filter out CASH$ and Dividend transactions
trades_df = df[(df['Transaction Type'].isin(['Buy', 'Sell'])) & (df['Stock / ETF Symbol'] != 'CASH$')].copy()

# Sort by date to ensure chronological order (stable sort preserves original CSV order for same-day trades)
trades_df = trades_df.sort_values('Date', kind='stable').reset_index(drop=True)

print("Calculating Realized Profit/Loss using FIFO method...\n")

# Track buy positions for each ticker (FIFO - First In First Out)
buy_queue = defaultdict(deque)  # ticker -> deque of (date, price, quantity)
realized_trades = []  # List of realized gains/losses
total_realized_pnl = 0

# Process each transaction chronologically
for idx, row in trades_df.iterrows():
    ticker = row['Stock / ETF Symbol']
    transaction_type = row['Transaction Type']
    price = row['Amount per unit']
    quantity = row['Quantity of Units']
    date = row['Date']

    if transaction_type == 'Buy':
        # Add to buy queue
        buy_queue[ticker].append({
            'date': date,
            'price': price,
            'quantity': quantity
        })

    elif transaction_type == 'Sell':
        # Match with oldest buys (FIFO)
        remaining_sell_qty = quantity
        sell_price = price

        while remaining_sell_qty > 0 and buy_queue[ticker]:
            oldest_buy = buy_queue[ticker][0]

            # Determine how much to match
            match_qty = min(remaining_sell_qty, oldest_buy['quantity'])

            # Calculate realized P&L for this match
            buy_price = oldest_buy['price']
            realized_pnl = (sell_price - buy_price) * match_qty
            total_realized_pnl += realized_pnl

            # Record the realized trade
            realized_trades.append({
                'ticker': ticker,
                'buy_date': oldest_buy['date'],
                'sell_date': date,
                'quantity': match_qty,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'realized_pnl': realized_pnl,
                'pnl_pct': ((sell_price - buy_price) / buy_price) * 100
            })

            # Update quantities
            remaining_sell_qty -= match_qty
            oldest_buy['quantity'] -= match_qty

            # Remove from queue if fully sold
            if oldest_buy['quantity'] <= 0:
                buy_queue[ticker].popleft()

# Analyze realized trades
print("="*100)
print("REALIZED PROFIT/LOSS ANALYSIS (Completed Trades)")
print("="*100)

if not realized_trades:
    print("\nNo realized trades found (no matching buy-sell pairs)")
else:
    # Summary statistics
    winning_trades = [t for t in realized_trades if t['realized_pnl'] > 0]
    losing_trades = [t for t in realized_trades if t['realized_pnl'] < 0]
    breakeven_trades = [t for t in realized_trades if t['realized_pnl'] == 0]

    total_winning_pnl = sum(t['realized_pnl'] for t in winning_trades)
    total_losing_pnl = sum(t['realized_pnl'] for t in losing_trades)

    print(f"\nSUMMARY:")
    print(f"  Total Realized Trades: {len(realized_trades)}")
    print(f"  Winning Trades: {len(winning_trades)} ({len(winning_trades)/len(realized_trades)*100:.1f}%)")
    print(f"  Losing Trades: {len(losing_trades)} ({len(losing_trades)/len(realized_trades)*100:.1f}%)")
    print(f"  Breakeven Trades: {len(breakeven_trades)}")
    print()
    print(f"  Total Realized P&L: ${total_realized_pnl:,.2f}")
    print(f"  Total Realized Gains: ${total_winning_pnl:,.2f}")
    print(f"  Total Realized Losses: ${total_losing_pnl:,.2f}")
    print(f"  Win Rate: {len(winning_trades)/len(realized_trades)*100:.1f}%")

    # Calculate average win/loss
    avg_win = total_winning_pnl / len(winning_trades) if winning_trades else 0
    avg_loss = total_losing_pnl / len(losing_trades) if losing_trades else 0

    print(f"\n  Average Winning Trade: ${avg_win:,.2f}")
    print(f"  Average Losing Trade: ${avg_loss:,.2f}")
    if avg_loss != 0:
        print(f"  Win/Loss Ratio: {abs(avg_win/avg_loss):.2f}")

    # Top 10 best realized trades
    print("\n" + "="*100)
    print("TOP 10 BEST REALIZED TRADES (by P&L)")
    print("="*100)
    best_realized = sorted(realized_trades, key=lambda x: x['realized_pnl'], reverse=True)[:10]
    print(f"\n{'Rank':<6} {'Ticker':<8} {'Buy Date':<12} {'Sell Date':<12} {'Qty':<8} {'Buy $':<10} {'Sell $':<10} {'P&L':<15} {'%':<10}")
    print("-"*100)
    for i, trade in enumerate(best_realized, 1):
        print(f"{i:<6} {trade['ticker']:<8} {trade['buy_date'].strftime('%Y-%m-%d'):<12} {trade['sell_date'].strftime('%Y-%m-%d'):<12} "
              f"{trade['quantity']:<8.0f} ${trade['buy_price']:<9.2f} ${trade['sell_price']:<9.2f} "
              f"${trade['realized_pnl']:>13,.2f} {trade['pnl_pct']:>9.2f}%")

    # Top 10 worst realized trades
    print("\n" + "="*100)
    print("TOP 10 WORST REALIZED TRADES (by P&L)")
    print("="*100)
    worst_realized = sorted(realized_trades, key=lambda x: x['realized_pnl'])[:10]
    print(f"\n{'Rank':<6} {'Ticker':<8} {'Buy Date':<12} {'Sell Date':<12} {'Qty':<8} {'Buy $':<10} {'Sell $':<10} {'P&L':<15} {'%':<10}")
    print("-"*100)
    for i, trade in enumerate(worst_realized, 1):
        print(f"{i:<6} {trade['ticker']:<8} {trade['buy_date'].strftime('%Y-%m-%d'):<12} {trade['sell_date'].strftime('%Y-%m-%d'):<12} "
              f"{trade['quantity']:<8.0f} ${trade['buy_price']:<9.2f} ${trade['sell_price']:<9.2f} "
              f"${trade['realized_pnl']:>13,.2f} {trade['pnl_pct']:>9.2f}%")

    # Realized P&L by ticker
    print("\n" + "="*100)
    print("REALIZED P&L BY TICKER")
    print("="*100)

    ticker_pnl = defaultdict(lambda: {'pnl': 0, 'trades': 0, 'wins': 0, 'losses': 0})
    for trade in realized_trades:
        ticker = trade['ticker']
        ticker_pnl[ticker]['pnl'] += trade['realized_pnl']
        ticker_pnl[ticker]['trades'] += 1
        if trade['realized_pnl'] > 0:
            ticker_pnl[ticker]['wins'] += 1
        elif trade['realized_pnl'] < 0:
            ticker_pnl[ticker]['losses'] += 1

    # Sort by total P&L
    ticker_summary = sorted(ticker_pnl.items(), key=lambda x: x[1]['pnl'], reverse=True)

    print(f"\n{'Ticker':<10} {'Trades':<10} {'Wins':<8} {'Losses':<8} {'Win Rate':<12} {'Total P&L':<15}")
    print("-"*100)
    for ticker, stats in ticker_summary:
        win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
        print(f"{ticker:<10} {stats['trades']:<10} {stats['wins']:<8} {stats['losses']:<8} "
              f"{win_rate:<11.1f}% ${stats['pnl']:>13,.2f}")

    # Monthly P&L
    print("\n" + "="*100)
    print("REALIZED P&L BY MONTH")
    print("="*100)

    monthly_pnl = defaultdict(lambda: {'pnl': 0, 'trades': 0})
    for trade in realized_trades:
        month_key = trade['sell_date'].strftime('%Y-%m')
        monthly_pnl[month_key]['pnl'] += trade['realized_pnl']
        monthly_pnl[month_key]['trades'] += 1

    print(f"\n{'Month':<12} {'Trades':<10} {'Realized P&L':<15}")
    print("-"*100)
    for month in sorted(monthly_pnl.keys()):
        stats = monthly_pnl[month]
        print(f"{month:<12} {stats['trades']:<10} ${stats['pnl']:>13,.2f}")

    print("\n" + "="*100)
    print(f"TOTAL REALIZED P&L: ${total_realized_pnl:,.2f}")
    print("="*100)
