#!/usr/bin/env python3
import logging
import json
import sqlite3

from common import (
    load_config,
    request
)

logging.basicConfig(format='%(asctime)s - BINANCE - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

GEMINI_BASE_URL = 'https://api.gemini.com'
#PAIRS = ['BTCUSDT','ADAUSDT', 'ADABTC', 'ADAETH', 'COTIBTC', 'COTIUSDT', 'LINKBRL', 'LINKBTC', 'LINKUSDT']
#INTERVAL = ['1m', '3m', '5m', '15m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'] # '1s' == 1 second == more than gigabytes of data. -__-

config = lambda: load_config('gemini')

def extract(pair, interval, *args, **kwargs):
    '''Download json data of pair from Gemini API.'''
    return json.loads(request(f'{GEMINI_BASE_URL}/v2/candles/{pair}/{interval}'))


def transform(data, pair, inteval, *args, **kwargs):
    '''Return a list of dicts with OHLCV + date and pair'''
    if not data:
        return False
    
    result = []

    for line in data:
        result.append({
            "open": line[1],
            "high": line[2],
            "low": line[3],
            "close": line[4],
            "volume": line[5],
            "pair": pair,
            "interval": inteval,
            "date": line[0],
            "exchange": 'gemini',
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
    print(f'  {len(list(lines))} rows inserted successfully.')


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
        etl(asset.get('pair'), asset.get('interval'))
