#!/usr/bIn/env python3
import gzip

from tasks.common import (
    decompress_gz,
    request
)

'''
curl 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id=12573&range=3M' \
-X 'GET' \
-H 'Accept: application/json, text/plain, */*' \
-H 'Origin: https://coinmarketcap.com' \
-H 'Referer: https://coinmarketcap.com/' \
-H 'Cache-Control: no-cache' \
-H 'Host: api.coinmarketcap.com' \
-H 'Accept-Language: en-GB,en;q=0.9' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Connection: keep-alive' \
-H 'x-request-id: d68fea1d63f34875881860fe5ada1155' \
-H 'platform: web' --output cpool.json
'''


def download(id):
    '''Download compressed file of pair from Binance vault.'''
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://coinmarketcap.com',
        'Referer': 'https://coinmarketcap.com/',
        'Cache-Control': 'no-cache',
        'Host': 'api.coinmarketcap.com',
        'Accept-Language': 'en-GB,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'x-request-id': 'd68fea1d63f34875881860fe5ada1155',
        'platform': 'web'
    }
    return request(f'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id={id}&range=3M', headers=headers)

def extract(data):
    '''Extract file from compressed data.'''
    if not data:
        return False

    return decompress_gz(data)

def transform(data):
    '''Return a list of dicts with OHLCV + date and pair'''
    pass



curl 'https://pro-api.coingecko.com/api/v3/coins/clearpool/market_chart/range?vs_currency=btc&from=1668800000&to=1676752974&x_cg_pro_api_key=CG-RNzPJmPbJXtnJGtx8Y38Zd4g' \
-X 'GET' \
-H 'Accept: */*' \
-H 'Content-Type: application/json' \
-H 'Origin: https://blockworks.co' \
-H 'Host: pro-api.coingecko.com' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15' \
-H 'Accept-Language: en-GB,en;q=0.9' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Connection: keep-alive' \
-H 'X-Research-Session-Token: undefined'


curl 'https://pro-api.coingecko.com/api/v3/coins/clearpool/ohlc?vs_currency=btc&days=180&x_cg_pro_api_key=CG-RNzPJmPbJXtnJGtx8Y38Zd4g'