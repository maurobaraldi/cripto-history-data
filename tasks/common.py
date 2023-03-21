#import pip
#pip.main(['install', 'psycopg2-binary==2.9.5'])

import logging
import os
from datetime import datetime, timedelta
from io import BytesIO
from json import loads
from sqlite3 import connect
from urllib.request import Request, urlopen
from urllib.error import URLError
from zipfile import ZipFile, is_zipfile
from gzip import GzipFile

import pandas as pd
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def request(url, headers = {}, *args, **kwargs):
    '''Request a GET to given url endpoint.'''
    request = Request(url, headers={'User-agent': 'Mozilla/5.0'} | headers)

    try:
        with urlopen(request) as r:
            return r.read()
    except URLError as err:
        logging.info(f'Failed to GET {url}. Error: {err}')
        print(f'Failed to GET {url}. Error: {err}')
        return False


def decompress(data, *args, **kwargs):
    '''Decompress data and return as a string.'''
    with ZipFile(BytesIO(data)) as zipf:
        return zipf.open(zipf.filelist[0]).read().decode('utf-8')


def decompress_gz(data, *args, **kwargs):
    '''Decompress data (GZip) and return as a string.'''
    with GzipFile(fileobj=BytesIO(data)) as zipf:
        return zipf.read()


def initdb(*args, **kwargs):
    '''Create database and table if they doesn't exists.'''

    conn = psycopg2.connect(
        host="192.168.1.251",
        user="postgres",
        password="secret",
        port=5432
    )

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        cursor.execute('CREATE DATABASE ohlcv;')
    except psycopg2.errors.DuplicateDatabase:
        logging.info('Database already exists.')
    finally:
        cursor.execute('CREATE TABLE IF NOT EXISTS ohlcv (id serial primary key, open money, high money, low money, close money, volume money, pair varchar (30), interval varchar (30), datetime varchar, exchange varchar (100));')
        conn.commit()
        cursor.close()
        conn.close()
        logging.info('Database initialization finished successfully.')


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def  get_pie(pair, interval, exchange, events=100, *arg, **kwargs):
    '''
    Connect to database (Postgres) and return a list of results according query.
    
    PIE = Pair, Interval, Exchange.
    '''

    con = connect("/var/code/ohlcv.sqlite")
    con.row_factory = dict_factory
    cur = con.cursor()
    strSQL = f"SELECT * FROM ohlcv WHERE pair LIKE '{pair}' AND interval LIKE '{interval}' AND exchange LIKE '{exchange}' ORDER BY date DESC LIMIT 100"
    print(strSQL)
    cur.execute(strSQL)
    res = [dict(row) for row in cur.fetchall()]
    cur.close()
    con.close()
    return res


def load_df(pair, interval, exchange, events, *args, **kwargs) -> pd.DataFrame:
       records = get_pie(pair, interval, exchange, events)
       return pd.DataFrame.from_records(records)


def check_var_images() -> None:
    try:
        return os.makedirs('/tmp/images')
    except FileExistsError:
        pass


def load_config(exchange):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'./{exchange}.json')
    with open(filename) as _:
        return loads(_.read())

def check_last_entry(pair, interval, exchange):
    '''
    Return the last registry (pair + interval + exchange) in DB.

    Return days to scrapping until yesterday, 0 if up to date.
    '''
    con = connect("/var/code/ohlcv.sqlite")
    cur = con.cursor()
    record = cur.execute(f'SELECT date FROM ohlcv WHERE pair LIKE "{pair}" AND interval LIKE "{interval}" AND exchange LIKE "{exchange}" ORDER BY date DESC LIMIT 1;').fetchone()
    con.commit()
    cur.close()
    con.close()

    if not record:
        print(f'Pair/Interval {pair}/{interval} not found.')
        return 0

    offset = datetime.fromtimestamp(float(record[0])).date()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    return (yesterday - offset).days