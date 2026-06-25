import pandas as pd
from collections import defaultdict, deque

# Read the CSV file
csv_file = 'trades_analysis_skill/data/gan_portfolio_for_analysis - Sheet1 (1).csv'
df = pd.read_csv(csv_file)

# Clean up column names (remove spaces)
df.columns = df.columns.str.strip()

# Normalize ticker symbols to uppercase (fix case sensitivity bug)
df['Stock / ETF Symbol'] = df['Stock / ETF Symbol'].str.strip().str.upper()

# Clean numeric columns (remove commas and convert to float)
df['Quantity of Units'] = pd.to_numeric(df['Quantity of Units'].astype(str).str.replace(',', ''), errors='coerce')
df['Amount per unit'] = pd.to_numeric(df['Amount per unit'].astype(str).str.replace(',', ''), errors='coerce')
df['Total Amount (before trading fees)'] = pd.to_numeric(df['Total Amount (before trading fees)'].astype(str).str.replace(',', ''), errors='coerce')

# Parse dates
df['Date'] = pd.to_datetime(df['Date (MM-DD-YYYY)'], format='%m-%d-%Y', errors='coerce')

# Filter out CASH$ and Dividend transactions for ticker analysis
trades_df = df[(df['Transaction Type'].isin(['Buy', 'Sell'])) & (df['Stock / ETF Symbol'] != 'CASH$')].copy()

print(f"Total trades after filtering: {len(trades_df)}")

# Sort trades chronologically for FIFO
trades_df_sorted = trades_df.sort_values('Date').reset_index(drop=True)

# Track buy lots using FIFO queues
buy_queues = defaultdict(deque)

for idx, row in trades_df_sorted.iterrows():
    ticker = row['Stock / ETF Symbol']
    transaction_type = row['Transaction Type']
    price = row['Amount per unit']
    quantity = row['Quantity of Units']
    date = row['Date']

    if ticker == 'VIXY':
        print(f"{date.date()} {transaction_type:4s} {quantity:6.0f} @ ${price:.2f}")

    if transaction_type == 'Buy':
        # Add to buy queue
        buy_queues[ticker].append({'price': price, 'quantity': quantity})
        if ticker == 'VIXY':
            print(f"  -> Queue size: {sum(lot['quantity'] for lot in buy_queues[ticker])}")
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

        if ticker == 'VIXY':
            print(f"  -> Queue size: {sum(lot['quantity'] for lot in buy_queues[ticker])}")

print(f"\n{'='*60}")
print(f"VIXY final position: {sum(lot['quantity'] for lot in buy_queues['VIXY'])}")
if buy_queues['VIXY']:
    print(f"VIXY queue contents:")
    for lot in buy_queues['VIXY']:
        print(f"  {lot['quantity']} shares @ ${lot['price']:.2f}")
else:
    print("VIXY queue is EMPTY (0 shares)")
