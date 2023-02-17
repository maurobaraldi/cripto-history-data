#!/usr/bin/env python3

import logging
from io import BytesIO
from urllib.request import Request, urlopen
from urllib.error import URLError
from zipfile import ZipFile

import psycopg2
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
        return False

def decompress(data):
    '''Decompress data and return as a string.'''
    with ZipFile(BytesIO(data)) as zipf:
        return zipf.open(zipf.filelist[0]).read().decode('utf-8')

def initdb():
    '''Create database and table if they doesn't exists.'''

    conn = psycopg2.connect(
        host="127.0.0.1",
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
        cursor.execute('CREATE TABLE IF NOT EXISTS ohlcv (id serial primary key, open money, high money, low money, close money, volume money, pair varchar (30), interval varchar (30), datetime varchar);')
        conn.commit()
        cursor.close()
        conn.close()
        logging.info('Database initialization finished successfully.')



