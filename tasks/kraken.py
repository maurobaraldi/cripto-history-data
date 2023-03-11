#!/usr/bin/env python3
import logging
import json
import sqlite3
import time

from common import (
    check_last_entry,
    decompress,
    load_config,
    request
)

# DOCS: https://docs.kraken.com/rest/#tag/Market-Data/operation/getTickerInformation
# Pairs: https://support.kraken.com/hc/en-us/articles/360000678446
# TODO: The current implementation gets only last 720 registries. Use the first registry time to get more 720 from behind.

logging.basicConfig(format='%(asctime)s - BINANCE - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

KRAKEN_BASE_URL = 'https://api.kraken.com/0/public/OHLC'

config = lambda: load_config('kraken')

URL = None

def extract(pair, interval, *args, **kwargs):
    '''Download json data of pair from Kraken API.'''
    INTERVALS = {'1h': 60, '4h': 240, '1d': 1440, '1w': 10080, '15d': 21600}
    global URL
    URL = f'{KRAKEN_BASE_URL}?pair={pair}&interval={INTERVALS[interval]}&since=0'

    return json.loads(request(f'{KRAKEN_BASE_URL}?pair={pair}&interval={INTERVALS[interval]}&since=0'))


def transform(data, pair, inteval, *args, **kwargs):
    '''Return a list of dicts with OHLCV + date and pair'''
    if not data:
        return False
    
    result = []
    try:
        data.pop(next(iter(data))) # remove "error" key
    except Exception as ex:
        print('Linha 39')
        import pdb; pdb.set_trace()

    try:
        _pair = next(iter(data.get('result')))   # get first key (pair). it has extra chars (¬_¬)
    except Exception as ex:
        print('Linha 42')
        import pdb; pdb.set_trace()

    for line in data.get('result').get(_pair):
        result.append({
            "open": line[1],
            "high": line[2],
            "low": line[3],
            "close": line[4],
            "volume": line[6],
            "pair": pair,
            "interval": inteval,
            "date": line[0],
            "exchange": 'kraken',
        })

    return result

def load(lines, *args, **kwargs):
    '''Load data to database.'''

    data = [(l['open'], l['high'], l['low'], l['close'], l['volume'], l['pair'], l['interval'], l['date'], l['exchange']) for l in lines]

    con = sqlite3.connect("/var/code/ohlcv.sqlite")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS "ohlcv" ("id" INTEGER NOT NULL UNIQUE, "open" REAL NOT NULL, "high" REAL NOT NULL, "low" REAL NOT NULL, "close" REAL NOT NULL, "volume" REAL NOT NULL, "pair" TEXT NOT NULL, "interval" TEXT NOT NULL, "date" TEXT NOT NULL, "exchange" TEXT NOT NULL, PRIMARY KEY("id" AUTOINCREMENT), UNIQUE(interval, pair , date ));')
    cur.executemany('INSERT OR IGNORE INTO ohlcv VALUES (NULL, :open, :high, :low, :close, :volume, :pair, :interval, :date, :exchange);', lines)
    con.commit()
    cur.close()
    con.close()
    pair, interval = lines[0]['pair'], lines[0]['interval']
    print(f'  {len(list(lines))} rows for pair {pair} - {interval} inserted successfully.')


def etl(pair, interval, *args, **kwargs):
    '''Execute the sequence download, extract, transform, load.'''

    logging.info(f'Extracting data {pair} for interval {interval}.')
    e = extract(pair, interval)

    logging.info('Transforming data.')
    t = transform(e, pair, interval)

    if t:
        logging.info('Load data to DB.')
        load(t)
    else:
        logging.info(f'Pair/Inteval {pair}/{interval} up to date.')
        print(f'Pair/Inteval {pair}/{interval} up to date.')

if __name__ == '__main__':
    assets = config().get('assets')

    for asset in assets:
        print(f"Workong on pair {asset.get('pair')} for interval {asset.get('interval')}")
        etl(asset.get('pair'), asset.get('interval'))
