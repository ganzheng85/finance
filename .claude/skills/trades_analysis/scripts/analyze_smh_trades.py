import pandas as pd
from datetime import datetime
from collections import deque
import sys

# Read the TSV file
tsv_file = '/c/Users/ZJGan/Projects/finance/.claude/skills/trades_analysis/data/smh_trades_2026-07-22.tsv'
df = pd.read_csv(tsv_file, sep='\t')

# Parse dates (MM-DD-YYYY format)
df['date'] = pd.to_datetime(df['date'], format='%m-%d-%Y')

# Current market price
current_price = 561.19

# Sort by date to ensure FIFO
df = df.sort_values('date').reset_index(drop=True)

print("="*80)
print("SMH TRADING ANALYSIS - FIFO METHODOLOGY")
print("="*80)
print(f"\nAnalysis Date: July 22, 2026")
print(f"Current Market Price: ${current_price:.2f}")
print(f"Analysis Period: {df['date'].min().strftime('%B %d, %Y')} to {df['date'].max().strftime('%B %d, %Y')}")
print(f"Total Transactions: {len(df)}")
print(f"  Buys: {len(df[df['action'] == 'Buy'])}")
print(f"  Sells: {len(df[df['action'] == 'Sell'])}")

# FIFO tracking
buy_queue = deque()
realized_trades = []
total_invested = 0
total_shares_bought = 0
total_shares_sold = 0

# Process each transaction
for idx, row in df.iterrows():
    if row['action'] == 'Buy':
        buy_queue.append({
            'date': row['date'],
            'quantity': row['quantity'],
            'price': row['price'],
            'original_quantity': row['quantity']
        })
        total_invested += row['value']
        total_shares_bought += row['quantity']

    elif row['action'] == 'Sell':
        remaining_sell_qty = row['quantity']
        sell_price = row['price']
        sell_date = row['date']
        total_shares_sold += row['quantity']

        # Match with FIFO buys
        while remaining_sell_qty > 0 and buy_queue:
            oldest_buy = buy_queue[0]
            match_qty = min(remaining_sell_qty, oldest_buy['quantity'])

            # Calculate realized P&L
            buy_cost = match_qty * oldest_buy['price']
            sell_proceeds = match_qty * sell_price
            realized_pnl = sell_proceeds - buy_cost

            realized_trades.append({
                'buy_date': oldest_buy['date'],
                'sell_date': sell_date,
                'quantity': match_qty,
                'buy_price': oldest_buy['price'],
                'sell_price': sell_price,
                'realized_pnl': realized_pnl,
                'return_pct': (realized_pnl / buy_cost) * 100
            })

            # Update quantities
            oldest_buy['quantity'] -= match_qty
            remaining_sell_qty -= match_qty

            if oldest_buy['quantity'] <= 0:
                buy_queue.popleft()

# Current holdings (remaining in queue)
current_holdings = []
total_current_shares = 0
total_cost_basis = 0

for lot in buy_queue:
    total_current_shares += lot['quantity']
    cost = lot['quantity'] * lot['price']
    total_cost_basis += cost
    current_holdings.append({
        'buy_date': lot['date'],
        'quantity': lot['quantity'],
        'price': lot['price'],
        'cost_basis': cost,
        'current_value': lot['quantity'] * current_price,
        'unrealized_pnl': (lot['quantity'] * current_price) - cost,
        'return_pct': ((current_price - lot['price']) / lot['price']) * 100
    })

# Calculate metrics
avg_cost_basis = total_cost_basis / total_current_shares if total_current_shares > 0 else 0
current_value = total_current_shares * current_price
total_unrealized_pnl = current_value - total_cost_basis

# Realized P&L
total_realized_pnl = sum(t['realized_pnl'] for t in realized_trades)
winning_trades = [t for t in realized_trades if t['realized_pnl'] > 0]
losing_trades = [t for t in realized_trades if t['realized_pnl'] < 0]

print("\n" + "="*80)
print("1. CURRENT POSITION (FIFO)")
print("="*80)

print(f"\nShares Owned: {total_current_shares:.2f}")
print(f"Average Cost Basis: ${avg_cost_basis:.2f}")
print(f"Total Cost Basis: ${total_cost_basis:,.2f}")
print(f"Current Market Price: ${current_price:.2f}")
print(f"Current Market Value: ${current_value:,.2f}")
print(f"Unrealized P&L: ${total_unrealized_pnl:,.2f} ({(total_unrealized_pnl/total_cost_basis*100):.2f}%)")

print("\nRemaining Lots (FIFO Order):")
print(f"{'Buy Date':<12} {'Shares':>10} {'Cost Basis':>12} {'Current':>12} {'Unrealized P&L':>18} {'Return':>10}")
print("-"*80)
for lot in current_holdings:
    print(f"{lot['buy_date'].strftime('%Y-%m-%d'):<12} {lot['quantity']:>10.2f} ${lot['price']:>11.2f} ${current_price:>11.2f} ${lot['unrealized_pnl']:>17,.2f} {lot['return_pct']:>9.2f}%")

print("\n" + "="*80)
print("2. REALIZED P&L (CLOSED TRADES)")
print("="*80)

print(f"\nTotal Realized Trades: {len(realized_trades)}")
print(f"Winning Trades: {len(winning_trades)} ({len(winning_trades)/len(realized_trades)*100:.1f}%)")
print(f"Losing Trades: {len(losing_trades)} ({len(losing_trades)/len(realized_trades)*100:.1f}%)")
print(f"Total Realized P&L: ${total_realized_pnl:,.2f}")
print(f"Total Realized Gains: ${sum(t['realized_pnl'] for t in winning_trades):,.2f}")
print(f"Total Realized Losses: ${sum(t['realized_pnl'] for t in losing_trades):,.2f}")

if winning_trades:
    print(f"Average Winner: ${sum(t['realized_pnl'] for t in winning_trades)/len(winning_trades):,.2f}")
if losing_trades:
    print(f"Average Loser: ${sum(t['realized_pnl'] for t in losing_trades)/len(losing_trades):,.2f}")

print("\nTop 5 Best Trades:")
best_trades = sorted(realized_trades, key=lambda x: x['realized_pnl'], reverse=True)[:5]
for i, trade in enumerate(best_trades, 1):
    print(f"{i}. {trade['buy_date'].strftime('%m/%d')} -> {trade['sell_date'].strftime('%m/%d')}: {trade['quantity']:.0f} shares @ ${trade['buy_price']:.2f} -> ${trade['sell_price']:.2f} = ${trade['realized_pnl']:,.2f} ({trade['return_pct']:+.2f}%)")

print("\nTop 5 Worst Trades:")
worst_trades = sorted(realized_trades, key=lambda x: x['realized_pnl'])[:5]
for i, trade in enumerate(worst_trades, 1):
    print(f"{i}. {trade['buy_date'].strftime('%m/%d')} -> {trade['sell_date'].strftime('%m/%d')}: {trade['quantity']:.0f} shares @ ${trade['buy_price']:.2f} -> ${trade['sell_price']:.2f} = ${trade['realized_pnl']:,.2f} ({trade['return_pct']:+.2f}%)")

# Monthly breakdown
realized_df = pd.DataFrame(realized_trades)
if not realized_df.empty:
    realized_df['month'] = realized_df['sell_date'].dt.to_period('M')
    monthly_pnl = realized_df.groupby('month')['realized_pnl'].sum()
    print("\nRealized P&L by Month:")
    for month, pnl in monthly_pnl.items():
        print(f"  {month}: ${pnl:,.2f}")

print("\n" + "="*80)
print("3. UNREALIZED P&L (CURRENT HOLDINGS)")
print("="*80)

print(f"\nTotal Unrealized P&L: ${total_unrealized_pnl:,.2f} ({(total_unrealized_pnl/total_cost_basis*100):+.2f}%)")
print("\nBest Performing Lots:")
best_lots = sorted(current_holdings, key=lambda x: x['return_pct'], reverse=True)[:5]
for i, lot in enumerate(best_lots, 1):
    print(f"{i}. {lot['buy_date'].strftime('%Y-%m-%d')}: {lot['quantity']:.2f} shares @ ${lot['price']:.2f} = ${lot['unrealized_pnl']:,.2f} ({lot['return_pct']:+.2f}%)")

print("\nWorst Performing Lots:")
worst_lots = sorted(current_holdings, key=lambda x: x['return_pct'])[:5]
for i, lot in enumerate(worst_lots, 1):
    print(f"{i}. {lot['buy_date'].strftime('%Y-%m-%d')}: {lot['quantity']:.2f} shares @ ${lot['price']:.2f} = ${lot['unrealized_pnl']:,.2f} ({lot['return_pct']:+.2f}%)")

print("\n" + "="*80)
print("4. TOTAL P&L (REALIZED + UNREALIZED)")
print("="*80)

total_pnl = total_realized_pnl + total_unrealized_pnl
print(f"\nTotal Invested: ${total_invested:,.2f}")
print(f"Realized P&L: ${total_realized_pnl:,.2f}")
print(f"Unrealized P&L: ${total_unrealized_pnl:,.2f}")
print(f"TOTAL P&L: ${total_pnl:,.2f}")
print(f"Total Return: {(total_pnl/total_invested)*100:.2f}%")

print("\n" + "="*80)
print("5. TRADING PATTERN ANALYSIS")
print("="*80)

# Buy analysis by price ranges
buy_df = df[df['action'] == 'Buy'].copy()

price_ranges = [
    ('$545-570 (DIP)', 545, 570),
    ('$571-590 (LOW)', 571, 590),
    ('$591-610 (MID)', 591, 610),
    ('$611-630 (HIGH)', 611, 630),
    ('$631-665 (TOP)', 631, 665)
]

print("\nBuy Distribution by Price Range:")
print(f"{'Price Range':<20} {'Shares':>10} {'Total Cost':>15} {'% of Total':>12}")
print("-"*60)

for range_name, low, high in price_ranges:
    range_buys = buy_df[(buy_df['price'] >= low) & (buy_df['price'] <= high)]
    total_shares = range_buys['quantity'].sum()
    total_cost = range_buys['value'].sum()
    pct_of_total = (total_cost / total_invested) * 100
    print(f"{range_name:<20} {total_shares:>10.2f} ${total_cost:>14,.2f} {pct_of_total:>11.2f}%")

# Sell analysis
sell_df = df[df['action'] == 'Sell'].copy()
print("\nSell Analysis:")
print(f"{'Sell Date':<12} {'Shares':>10} {'Sell Price':>12} {'Context':>30}")
print("-"*70)
for idx, row in sell_df.iterrows():
    context = ""
    if row['price'] < 575:
        context = "PANIC SELL (near low)"
    elif row['price'] > 625:
        context = "WINNER (sold high)"
    else:
        context = "Mid-range sell"
    print(f"{row['date'].strftime('%Y-%m-%d'):<12} {row['quantity']:>10.2f} ${row['price']:>11.2f} {context:>30}")

print("\n" + "="*80)
print("6. DAY TRADING ANALYSIS (June 5, 2026)")
print("="*80)

june5_trades = df[df['date'] == '2026-06-05']
print(f"\nTransactions on June 5:")
june5_buys = june5_trades[june5_trades['action'] == 'Buy']
june5_sells = june5_trades[june5_trades['action'] == 'Sell']

print(f"\nBuys: {len(june5_buys)}")
for idx, row in june5_buys.iterrows():
    print(f"  {row['quantity']:.2f} shares @ ${row['price']:.2f} = ${row['value']:,.2f}")
print(f"Total bought: {june5_buys['quantity'].sum():.2f} shares for ${june5_buys['value'].sum():,.2f}")

print(f"\nSells: {len(june5_sells)}")
for idx, row in june5_sells.iterrows():
    print(f"  {row['quantity']:.2f} shares @ ${row['price']:.2f} = ${row['value']:,.2f}")
print(f"Total sold: {june5_sells['quantity'].sum():.2f} shares for ${june5_sells['value'].sum():,.2f}")

# Calculate P&L from June 5 day trading
june5_realized = [t for t in realized_trades if t['sell_date'] == pd.Timestamp('2026-06-05')]
june5_pnl = sum(t['realized_pnl'] for t in june5_realized)
print(f"\nJune 5 Day Trading P&L: ${june5_pnl:,.2f}")

print("\n" + "="*80)
print("7. POSITION SIZING ANALYSIS")
print("="*80)

# Check buying at extremes
high_price_buys = buy_df[buy_df['price'] >= 620]
low_price_buys = buy_df[buy_df['price'] <= 570]

print(f"\nBought at HIGH prices (>=$620):")
print(f"  Total shares: {high_price_buys['quantity'].sum():.2f}")
print(f"  Total cost: ${high_price_buys['value'].sum():,.2f}")
print(f"  % of total capital: {(high_price_buys['value'].sum()/total_invested)*100:.1f}%")

print(f"\nBought at LOW prices (<=$570):")
print(f"  Total shares: {low_price_buys['quantity'].sum():.2f}")
print(f"  Total cost: ${low_price_buys['value'].sum():,.2f}")
print(f"  % of total capital: {(low_price_buys['value'].sum()/total_invested)*100:.1f}%")

# July 17 dip analysis
july17_buy = buy_df[buy_df['date'] == '2026-07-17']
if not july17_buy.empty:
    print(f"\nJuly 17 DIP ($545.53 - BEST PRICE):")
    print(f"  Bought: {july17_buy['quantity'].sum():.2f} shares")
    print(f"  Cost: ${july17_buy['value'].sum():,.2f}")
    print(f"  % of total capital: {(july17_buy['value'].sum()/total_invested)*100:.1f}%")

# June 22 top analysis
june22_buy = buy_df[buy_df['date'] == '2026-06-22']
if not june22_buy.empty:
    print(f"\nJune 22 TOP ($665.19 - WORST PRICE):")
    print(f"  Bought: {june22_buy['quantity'].sum():.2f} shares")
    print(f"  Cost: ${june22_buy['value'].sum():,.2f}")
    print(f"  % of total capital: {(june22_buy['value'].sum()/total_invested)*100:.1f}%")

print("\n" + "="*80)
print("8. COUNTERFACTUAL ANALYSIS")
print("="*80)

# Buy and hold
total_shares_if_never_sold = total_shares_bought
buy_and_hold_value = total_shares_if_never_sold * current_price
buy_and_hold_profit = buy_and_hold_value - total_invested

print(f"\nBuy-and-Hold (Never Sold):")
print(f"  Shares owned: {total_shares_if_never_sold:.2f}")
print(f"  Total invested: ${total_invested:,.2f}")
print(f"  Current value: ${buy_and_hold_value:,.2f}")
print(f"  Profit: ${buy_and_hold_profit:,.2f} ({(buy_and_hold_profit/total_invested)*100:.2f}%)")

print(f"\nActual (With Trading):")
print(f"  Shares owned: {total_current_shares:.2f}")
print(f"  Total invested: ${total_invested:,.2f}")
print(f"  Current value: ${current_value:,.2f}")
print(f"  Total P&L (realized + unrealized): ${total_pnl:,.2f} ({(total_pnl/total_invested)*100:.2f}%)")

difference = buy_and_hold_profit - total_pnl
print(f"\nDifference:")
print(f"  Trading {'hurt' if difference > 0 else 'helped'} by ${abs(difference):,.2f}")

# Only buy at dips
dip_buys = buy_df[buy_df['price'] <= 570]
if not dip_buys.empty:
    print(f"\nCounterfactual: Only Buy at Dips (<=$570):")
    print(f"  Would have bought: {dip_buys['quantity'].sum():.2f} shares")
    print(f"  Cost: ${dip_buys['value'].sum():,.2f}")
    print(f"  Current value: ${dip_buys['quantity'].sum() * current_price:,.2f}")
    print(f"  Profit: ${(dip_buys['quantity'].sum() * current_price) - dip_buys['value'].sum():,.2f}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
