#!/usr/bin/env python3
import logging

from datetime import (
    datetime,
    timedelta
)
from urllib.request import (
    Request,
    urlopen
)

import psycopg2

from tasks.common import (
    decompress,
    initdb,
    request
)

from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@192.168.1.97//')
logging.basicConfig(format='%(asctime)s - BINANCE - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

KLINES_BASE_URL = 'https://data.binance.vision/data/spot/daily/klines'
PAIRS = ['BTCUSDT','ADAUSDT', 'ADABTC', 'ADAETH', 'COTIBTC', 'COTIUSDT', 'LINKBRL', 'LINKBTC', 'LINKUSDT']
INTERVAL = ['1m', '3m', '5m', '15m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'] # '1s' == 1 second == more than gigabytes of data. -__-


def download(pair, interval, day):
    '''Download compressed file of pair from Binance vault.'''
    return request(f'{KLINES_BASE_URL}/{pair}/{interval}/{pair}-{interval}-{day.year}-{day.month:02}-{day.day:02}.zip')

def extract(data):
    '''Extract file from compressed data.'''
    if not data:
        return False

    return decompress(data)

def transform(data, pair, inteval):
    '''Return a list of dicts with OHLCV + date and pair'''
    lines = [d.split(',') for d in data.strip().split('\n')]

    for l in lines:
        yield {
            'open': l[1],
            'high': l[4],
            'low': l[3],
            'close': l[2],
            'volume': l[5],
            'pair': pair,
            'interval': inteval,
            #'date': datetime.fromtimestamp(int(l[0])/1000)
            'date': int(l[0])/1000,
        }

def load(lines):
    '''Load data to database.'''

    data = [(l['open'], l['high'], l['low'], l['close'], l['volume'], l['pair'], l['interval'], l['date']) for l in lines]

    initdb()

    conn = psycopg2.connect(host="127.0.0.1", user="postgres", password="secret", port=5432)
    cursor = conn.cursor()
    args_str = b','.join(cursor.mogrify("%s", (x, )) for x in data)
    cursor.execute(f"INSERT INTO ohlcv (open, high, low, close, volume, pair, interval, datetime) VALUES " + args_str.decode('utf8'))
    conn.commit()
    cursor.close()
    conn.close()

#@app.task
def etl(pair, interval, day):
    '''Execute the sequence download, extract, transform, load.'''

    logging.info('Downloading {pair} from interval {interval} for day {day}.')
    print('Downloading {pair} from interval {interval} for day {day}.')
    d = download(pair, interval, day)

    logging.info('Extracting data.')
    print('Extracting data.')
    e = extract(d)

    logging.info('Transforming data.')
    print('Transforming data.')
    t = transform(e, pair, interval)

    logging.info('Load data to DB.')
    print('Load data to DB.')
    load(t)


#    yesterday = datetime.today() - timedelta(days=1)
#    days = [yesterday - timedelta(days=x) for x in range(days)]
# docker run -d --rm --name posttest postgres:alpine -e POSTGRES_PASSWORD=fred -p 5432:5432

