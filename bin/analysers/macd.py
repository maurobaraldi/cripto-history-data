#import pip
#pip.main(['install', 'plotly', 'pandas-ta', 'matplotlib'])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as sql
import plotly.graph_objects as go

from plotly import io as pio

# Shows blank figure in Jupyter notebooks.
pio.renderers.default = "iframe"

# Using SQLite DB file in the example.
conn = sql.connect('binance.sqlite')
df = pd.read_sql_query('SELECT * FROM quotes WHERE pair LIKE "ADAUSDT" AND interval LIKE "15m" LIMIT 100', conn)

# # Calculate MACD values using the pandas_ta library
# df.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)

# Get the 12-day EMA of the closing price
k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()

# Get the 26-day EMA of the closing price
d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()

# Subtract the 26-day EMA from the 12-Day EMA to get the MACD
macd = k - d

# Get the 9-Day EMA of the MACD for the Trigger line
macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()

# Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
macd_h = macd - macd_s

# Add all of our new values for the MACD to the dataframe
df['macd'] = df.index.map(macd)
df['macd_h'] = df.index.map(macd_h)
df['macd_s'] = df.index.map(macd_s)

plt.figure(figsize=(25, 10))
plt.plot(macd,label='ADA USDT MACD')
plt.plot(macd_s,label='Signal Line')
plt.xticks(rotation=45)
plt.bar(macd_h.index,macd_h ,label='ADA USDT MACD History')
plt.xlabel('15 min slots')
plt.ylabel('Indicator Value')
plt.legend(loc='upper right')
plt.show()
plt.savefig('./data/analyses/analysis.png')