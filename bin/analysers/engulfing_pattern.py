#!/usr/bin/env python3

#
# Inspired in https://www.youtube.com/watch?v=33qz3LIdwKo
# Thank you Code Trading Cafe
#

from datetime import datetime

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
try:
    from plotly import graph_objects as go
    from plotly import io as pio
except ImportError:
    import pip
    pip.main(['install', 'plotly'])

# Shows blank figure in Jupyter notebooks.
pio.renderers.default = "iframe"

def load_data_frame(path: str) -> DataFrame:
    return pd.read_csv(path)

def reverse_signal_finder(dataframe: DataFrame, diffmin: float, diffpips: int) -> DataFrame:
    '''
    Analyse dataframe, add a colum with the following trend.
    
    dataframe: Dataframe to be analysed 
    diffmin: Body difference minimal in pips.
    Ex: 0.003 = 30 pips
    diffpips: Difference in pips for calculation when it is very small.
    Ex.: +5e-5 -> 1 +5e-5 = 1.00005
    
    Trends: 1 - bearrish, 2 - bullish or 0 - none)
    '''
    length = len(dataframe)
    high = list(dataframe['high'])
    low = list(dataframe['low'])
    close = list(dataframe['close'])
    open = list(dataframe['open'])
    signal = [0] * length
    bodydiff = [0] * length

    for row in range(1, length):
        bodydiff[row] = abs(open[row] - close[row])
        #bodydiffmin = 0.003
        bodydiffmin = diffmin
        if (
            bodydiff[row] > bodydiffmin and
            bodydiff[row - 1] > bodydiffmin and
            open[row - 1] < close[row - 1] and
            open[row] > close[row] and
            ###open[row] >=close[row - 1] and close[row] < open[row - 1]):
            (open[row] - close[row - 1]) >= +diffpips and 
            close[row] < open[row - 1]
        ):
            signal[row] = 1
        elif (
            bodydiff[row] > bodydiffmin and
            bodydiff[row - 1] > bodydiffmin and
            open[row - 1] > close[row - 1] and
            open[row] < close[row] and
            ##open[row] <= close[row - 1] and close[row] > open[row - 1]):
            (open[row]-close[row - 1]) <= -diffpips and
            close[row] > open[row - 1]
        ):
            signal[row] = 2
        else:
            signal[row] = 0
    return signal

def price_target_analyser(dataframe: DataFrame, barsfront: int) -> DataFrame:
    '''
    Analyse the trends category and return a column to add in dataframe.

    dataframe: Dataframe to be analysed.
    barsfront: How many bars will be analysed (days/hours/minutes). 
    
    Trends:
    0 - no clear trend
    1 - downtrend
    2 - updtrend
    3 - no trend
    '''
    length = len(dataframe)
    high = list(dataframe['high'])
    low = list(dataframe['low'])
    close = list(dataframe['close'])
    open = list(dataframe['open'])
    trendcat = [None] * length
    
    piplim = 300e-5

    for line in range (0, length - 1 - barsfront):
        for i in range(1, barsfront + 1):
            if (
                    (high[line + i] - max(close[line], open[line])) > piplim
                ) and (
                    (min(close[line], open[line]) - low[line+i]) > piplim
                ):
                    trendcat[line] = 3 # no trend
            elif (min(close[line], open[line]) - low[line + i]) > piplim:
                trendcat[line] = 1 #-1 downtrend
                break
            elif (high[line + i] - max(close[line], open[line])) > piplim:
                trendcat[line] = 2 # uptrend
                break
            else:
                trendcat[line] = 0 # no clear trend  
    return trendcat

def calculate_precision(dataframe: DataFrame, trend: int):
    '''
    Calculate the precision of trend, signal and result toghether

    dataframe: Dataframe to be analysed.
    trend: Which trend evaluate (1 - bearish, 2 - bullish)
    '''
    trendId=2
    result = dataframe[dataframe['result'] == trend].result.count() / dataframe[dataframe['signal1'] == trend].signal1.count()
    false_results = dataframe[(dataframe['trend'] != trendId) & (dataframe['signal1'] == trendId)] # false positives
    return {'precision': f'{100*result}%', 'false_positive': false_results}

def plot_interval(dataframe: DataFrame, start: int, end: int) -> None:
    '''
    Plot candlestick chart given, dataframe, start and end intervals.
    '''
    df = dataframe[start: end]
    fig = go.Figure(
        data=[
            go.Candlestick(
                x = df.index,
                open = df['open'],
                high = df['high'],
                low = df['low'],
                close = df['close']
            )
        ]
    )
    fig.show()

def get_moments(dataframe: DataFrame, behaviour: int) -> None:
    '''
    Return a list of ids in dataframe to choice and plot.
    behaviour 1 - bullish, 2 - bearish
    '''

    b = {1: 'bullish', 2: 'bearish'}

    ids = list(dataframe[dataframe['result'] == behaviour].index)
    print(f'Dataframes that behave as {b[behaviour]}: {ids}')
    momment = int(input('Choice a momment:'))
    plot_interval(dataframe, momment - 15, momment + 15)

# Add a signal column with the signal analysed (bear, bull or none)
data = load_data_frame('../../data/binance/LTCBRL-4h.csv')
data['signal1'] = reverse_signal_finder(data, 0.003, 5e-5)
#data[data['signal1'] == 1].count() # debug

# Add a trend column with the result of price target analyser
data['trend'] = price_target_analyser(data, 4)
#data.head(30) # debug

# Add a results column with values 1 if trend and signal are bearish and 2 if bullish.
conditions = [(data['trend'] == 1) & (data['signal1'] == 1),(data['trend'] == 2) & (data['signal1'] == 2)]
values = [1, 2]
data['result'] = np.select(conditions, values)

print(f'Bearish precision: {calculate_precision(data, 1)["precision"]}')
print(f'Bullish precision: {calculate_precision(data, 2)["precision"]}')