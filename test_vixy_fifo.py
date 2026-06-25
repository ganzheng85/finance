import pandas as pd
from collections import deque

# Read CSV
df = pd.read_csv('trades_analysis_skill/data/gan_portfolio_for_analysis - Sheet1 (1).csv')

# Clean and normalize
df.columns = df.columns.str.strip()
df['Stock / ETF Symbol'] = df['Stock / ETF Symbol'].str.strip().str.upper()
df['Quantity of Units'] = pd.to_numeric(df['Quantity of Units'].astype(str).str.replace(',', ''), errors='coerce')
df['Amount per unit'] = pd.to_numeric(df['Amount per unit'].astype(str).str.replace(',', ''), errors='coerce')
df['Date'] = pd.to_datetime(df['Date (MM-DD-YYYY)'], format='%m-%d-%Y', errors='coerce')

# Filter for VIXY only
vixy = df[(df['Stock / ETF Symbol'] == 'VIXY') & (df['Transaction Type'].isin(['Buy', 'Sell']))].copy()
vixy = vixy.sort_values('Date').reset_index(drop=True)

print(f"Total VIXY transactions: {len(vixy)}")
print(f"\nVIXY transactions:")
print(vixy[['Date', 'Transaction Type', 'Quantity of Units', 'Amount per unit']].to_string())

# Run FIFO
buy_queue = deque()
total_bought = 0
total_sold = 0

for idx, row in vixy.iterrows():
    qty = row['Quantity of Units']
    price = row['Amount per unit']
    trans_type = row['Transaction Type']
    date = row['Date']

    if trans_type == 'Buy':
        buy_queue.append({'price': price, 'quantity': qty})
        total_bought += qty
        print(f"\n{date.date()} BUY {qty} @ ${price:.2f} -> Queue size: {sum(lot['quantity'] for lot in buy_queue)}")
    elif trans_type == 'Sell':
        total_sold += qty
        remaining_sell = qty
        print(f"\n{date.date()} SELL {qty} @ ${price:.2f}")
        while remaining_sell > 0 and buy_queue:
            oldest = buy_queue[0]
            match_qty = min(remaining_sell, oldest['quantity'])
            oldest['quantity'] -= match_qty
            remaining_sell -= match_qty
            print(f"  Matched {match_qty} from lot @ ${oldest['price']:.2f}, lot remaining: {oldest['quantity']}")
            if oldest['quantity'] <= 0:
                buy_queue.popleft()
                print(f"  Lot depleted, removed from queue")
        print(f"  -> Queue size: {sum(lot['quantity'] for lot in buy_queue)}")

print(f"\n{'='*60}")
print(f"FINAL VIXY POSITION:")
print(f"Total bought: {total_bought}")
print(f"Total sold: {total_sold}")
print(f"Remaining in queue: {sum(lot['quantity'] for lot in buy_queue)}")
print(f"Queue contents: {list(buy_queue)}")
