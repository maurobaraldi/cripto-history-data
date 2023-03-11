#!/usr/bin/env python3

# TESTES - BACKUP DO threaded_scraping.py
import sqlite3

from csv import DictReader
from datetime import datetime, timedelta
from glob import glob
from io import BytesIO
from pathlib import PurePath
from queue import Queue
from sys import exit as _exit
from time import sleep
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import URLError
from zipfile import ZipFile

klinesBaseURL = "https://data.binance.vision/data/spot/daily/klines"
concurrent = 6 # available (safe amount) of threads
days = 120
base = datetime.today() - timedelta(days=1)
days = [base - timedelta(days=x) for x in range(days)]
pairs = ['BTCUSDT','ADAUSDT', 'ADABTC', 'ADAETH', 'COTIBTC', 'COTIUSDT', 'LINKBRL', 'LINKBTC', 'LINKUSDT']
intervals = ['1m', '3m', '5m', '15m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'] # '1s' == 1 second == more than gigabytes of data. -__-

pairs = ['XRPUSDT',]
intervals = ['1d',]


def download_extract(pair, interval, day):
    sleep(0.5)
    url = f'{klinesBaseURL}/{pair}/{interval}/{pair}-{interval}-{day.year}-{day.month:02}-{day.day:02}.zip'
    request = Request(url, headers={'User-agent': 'Mozilla/5.0'})
    try:
        print(f'Downloading {pair}-{interval}-{day.day}-{day.month}-{day.year} file.')
        with urlopen(request) as r:
            with ZipFile(BytesIO(r.read())) as zipf:
                with open(f'./data/binance/{pair}-{interval}.csv', 'a') as result:
                    result.write(zipf.open(zipf.filelist[0]).read().decode('utf-8'))
                    #print(f'Download and extract ./data/binance/{pair}-{interval}.csv done successfully.')
    except URLError:
        print(f'Error downloading {url}')

def doWork():
    while True:
        params = q.get()
        download_extract(**params)
        q.task_done()

q = Queue(concurrent * 2)

for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()

try:
    for pair in pairs:
        for interval in intervals:
            for day in days:
                # debug
                # print(f'{klinesBaseURL}/{pair}/{interval}/{pair}-{interval}-{day.year}-{day.month:02}-{day.day:02}.zip')
                q.put({'pair': pair, 'interval': interval, 'day': day})
    q.join()
except KeyboardInterrupt:
    _exit(1)

def insert():
    fieldnames = ["open_time", "open", "close", "low", "high", "volume", "close_time", "quote_asset_volume", "trades", "take_buy_base_asset_volume", "take_buy_quote_asset_volume", "ignore", "pair", "interval"]
    csv_files = glob('./data/binance/*.csv')
    insert_rows = []
    for csvf in csv_files:
        path = PurePath(csvf)
        pair, interval = path.stem.split('-')
        with open(path) as fin:
            print(f'Working with file {path}')
            dr = DictReader(fin, fieldnames=fieldnames)
            for row in dr:
                insert_rows.append({
                    'pair': pair,
                    'open_time': datetime.fromtimestamp(int(row['open_time'])/1000),
                    'open': row['open'],
                    'close': row['close'],
                    'low': row['low'],
                    'high': row['high'],
                    'volume': row['volume'],
                    'close_time': datetime.fromtimestamp(int(row['close_time'])/1000),
                    'quote_asset_volume': row['quote_asset_volume'],
                    'trades': row['trades'],
                    'take_buy_base_asset_volume': row['take_buy_base_asset_volume'],
                    'take_buy_quote_asset_volume': row['take_buy_quote_asset_volume'],
                    'interval': interval,
                    'ignore': row['ignore']
                })

    print(f'Inserting {len(insert_rows)} rows.\nStarting...')

    con = sqlite3.connect("./binance.sqlite")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS quotes ("id" INTEGER NOT NULL UNIQUE, "pair" TEXT NOT NULL, "open_time" TEXT NOT NULL, "open" REAL NOT NULL, "close" REAL NOT NULL, "low" REAL NOT NULL, "high" REAL NOT NULL, "volume" REAL NOT NULL, "close_time" TEXT NOT NULL, "quote_asset_volume" REAL, "trades" INTEGER, "take_buy_base_asset_volume " REAL, "take_buy_quote_asset_volume" INTEGER, "interval" TEXT, "ignore" INTEGER, PRIMARY KEY("id" AUTOINCREMENT), UNIQUE("interval","pair","open_time"));')
    cur.executemany('INSERT OR IGNORE INTO quotes VALUES (NULL, :pair, :open_time, :open, :close, :low, :high, :volume, :close_time, :quote_asset_volume, :trades, :take_buy_base_asset_volume, :take_buy_quote_asset_volume, :interval, :ignore);', insert_rows)
    con.commit()
    cur.close()
    con.close()
    print('Inserting data finished successfully.')

print(insert())