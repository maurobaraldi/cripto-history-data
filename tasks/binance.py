#!/usr/bin/env python3
import logging
import sqlite3
import re

from datetime import (
    datetime,
    timedelta
)
from urllib.request import (
    Request,
    urlopen
)

from common import (
    check_last_entry,
    decompress,
    load_config,
    request
)

logging.basicConfig(format='%(asctime)s - BINANCE - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

KLINES_BASE_URL = 'https://data.binance.vision/data/spot/daily/klines'
PAIRS = ['BTCUSDT','ADAUSDT', 'ADABTC', 'ADAETH', 'COTIBTC', 'COTIUSDT', 'LINKBRL', 'LINKBTC', 'LINKUSDT']
INTERVAL = ['1m', '3m', '5m', '15m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'] # '1s' == 1 second == more than gigabytes of data. -__-

config = lambda: load_config('binance')

def download(pair, interval, day, *args, **kwargs):
    '''Download compressed file of pair from Binance vault.'''
    return request(f'{KLINES_BASE_URL}/{pair}/{interval}/{pair}-{interval}-{day}.zip')


def extract(data, *args, **kwargs):
    '''Extract file from compressed data.'''
    if not data:
        return False
    return decompress(data)


def transform(data, pair, inteval, *args, **kwargs):
    '''Return a list of dicts with OHLCV + date and pair'''
    if not data:
        return False

    lines = [d.split(',') for d in data.strip().split('\n')]
    result = []

    for l in lines:
        result.append({
            'open': l[1],
            'high': l[4],
            'low': l[3],
            'close': l[2],
            'volume': l[5],
            'pair': pair,
            'interval': inteval,
            #'date': datetime.fromtimestamp(int(l[0])/1000)
            'date': int(l[0])/1000,
            'exchange': 'binance',
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


def etl(pair, interval, day, *args, **kwargs):
    '''Execute the sequence download, extract, transform, load.'''

    logging.info(f'Downloading {pair} from interval {interval} for day {day}.')
    print(f'Downloading {pair} from interval {interval} for day {day}.')
    d = download(pair, interval, day)

    logging.info('Extracting data.')
    e = extract(d)

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
        days = check_last_entry(asset.get('pair'), asset.get('interval'), 'binance')
        #days = 30
        while days > 0:
            day = datetime.now() - timedelta(days)
            strdate = datetime.strftime(day, "%Y-%m-%d")
            etl(asset.get('pair'), asset.get('interval'), strdate)
            days -= 1
