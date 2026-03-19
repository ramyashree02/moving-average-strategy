import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Step 1: Download stock data
print("Downloading stock data...")
stock = "GOOGL"  # Apple stock (you can change this to any stock ticker)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)  # 1 year of data

data = yf.download(stock, start=start_date, end=end_date, progress=False)

# Step 2: Calculate moving averages
print("Calculating moving averages...")
data['MA_20'] = data['Close'].rolling(window=20).mean()  # Fast moving average (20 days)
data['MA_50'] = data['Close'].rolling(window=50).mean()  # Slow moving average (50 days)

# Step 3: Generate trading signals
print("Generating trading signals...")
data['Signal'] = 0  # 0 = no signal
data['Signal'][20:] = 1  # Default to holding (start after 20 days)

# Buy signal: when fast MA crosses above slow MA
data['Position'] = 0
for i in range(50, len(data)):
    if data['MA_20'].iloc[i] > data['MA_50'].iloc[i] and data['MA_20'].iloc[i-1] <= data['MA_50'].iloc[i-1]:
        data['Position'].iloc[i] = 1  # BUY
    elif data['MA_20'].iloc[i] < data['MA_50'].iloc[i] and data['MA_20'].iloc[i-1] >= data['MA_50'].iloc[i-1]:
        data['Position'].iloc[i] = -1  # SELL
    else:
        data['Position'].iloc[i] = data['Position'].iloc[i-1]  # HOLD

# Step 4: Calculate returns
print("Calculating returns...")
data['Daily_Return'] = data['Close'].pct_change()  # Daily % change
data['Strategy_Return'] = data['Position'].shift(1) * data['Daily_Return']  # Our strategy's return

# Step 5: Calculate performance metrics
total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
strategy_return = (data['Strategy_Return'].sum()) * 100
buy_hold_return = total_return

# Count trades
trades = (data['Position'].diff() != 0).sum()

print("\n" + "="*50)
print(f"STOCK: {stock}")
print("="*50)
print(f"Start Date: {start_date.date()}")
print(f"End Date: {end_date.date()}")
print(f"Strategy Return: {strategy_return:.2f}%")
print(f"Strategy Return: {strategy_return:.2f}%")
print(f"Number of Trades: {int(trades)}")
print("="*50)

# Step 6: Create visualization
print("\nCreating chart...")
plt.figure(figsize=(14, 7))
plt.plot(data.index, data['Close'], label='Stock Price', linewidth=2, color='black')
plt.plot(data.index, data['MA_20'], label='20-Day MA (Fast)', linewidth=1.5, color='blue')
plt.plot(data.index, data['MA_50'], label='50-Day MA (Slow)', linewidth=1.5, color='red')

# Mark buy and sell points
buy_points = data[data['Position'].diff() == 1]
sell_points = data[data['Position'].diff() == -1]
plt.scatter(buy_points.index, buy_points['Close'], color='green', marker='^', s=100, label='BUY Signal')
plt.scatter(sell_points.index, sell_points['Close'], color='red', marker='v', s=100, label='SELL Signal')

plt.title(f'{stock} - Moving Average Crossover Strategy', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Price ($)', fontsize=12)
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('trading_strategy_chart.png')
print("Chart saved as 'trading_strategy_chart.png'")
plt.show()
