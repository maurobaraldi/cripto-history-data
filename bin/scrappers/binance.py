#!/usr/bin/env python3

from datetime import datetime, timedelta
from io import BytesIO
from re import findall
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zipfile import ZipFile

klinesBaseURL = "https://data.binance.vision/data/spot/daily/klines"
check_date = datetime.strptime('2021/03/01', '%Y/%m/%d').date()

#while check_date != datetime.now().date():
#    day, month, year = check_date.day, check_date.month, check_date.year
#    base_url = f'{klinesBaseURL}/LTCBRL/8h/LTCBRL-8h-{year}-{month:02}-{day:02}.zip'
#    request = Request(base_url, headers={'User-agent': 'Mozilla/5.0'})
#    print(f'working on file LTCBRL-8h-{year}-{month:02}-{day:02}.zip')
#    with urlopen(request) as r:
#        with ZipFile(BytesIO(r.read())) as zipf:
#            with open('LTCBRL-8h.txt', 'a') as result:
#                result.write(zipf.open(zipf.filelist[0]).read().decode('utf-8'))
#                check_date = timedelta(days=1) + check_date 


def download_and_extract(asset: str, interval: str, day: int, month: int, year: int):
    request = Request(
        f'{klinesBaseURL}/{asset}/{interval}/{asset}-{interval}-{year}-{month:02}-{day:02}.zip',
        headers={'User-agent': 'Mozilla/5.0'}
    )
    #print(f'Downloading data for {asset}-{interval} from {day}/{month}/{year}')
    try:
        with urlopen(request) as r:
            with ZipFile(BytesIO(r.read())) as zipf:
                with open(f'./data/binance/{asset}-{interval}.csv', 'a') as result:
                    result.write(zipf.open(zipf.filelist[0]).read().decode('utf-8'))
    except HTTPError:
        print(f'Error downloading {klinesBaseURL}/{asset}/{interval}/{asset}-{interval}-{year}-{month:02}-{day:02}.zip file.')

#download_and_extract('LTCBRL', '12h', 16, 12, 2022)

class BinanceDailyKlines:
    def __init__(self, *args, **kwargs):
        self.pairs_url = 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/'
        self._pairs = []
        self._intervals = []
        self._items = []
    
    def request(self, url):
        request = Request(url, headers={'User-agent': 'Mozilla/5.0'})
        #print(request.full_url) # debug
        with urlopen(request) as r:
            return r.readlines()

    def _download(self, item):
        url = f'https://data.binance.vision/data/spot/daily/klines/{self.pair}/{self.interval}/'
        headers = {
            'authority': 'data.binance.vision',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': url,
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        request = Request(url + item, headers=headers)
        with urlopen(request) as r:
            with ZipFile(BytesIO(r.read())) as zipf:
                rows = zipf.open(zipf.filelist[0]).read().decode('utf-8').strip().split('\n')
                # write to file
                #with open(f'{item}.csv', 'a') as result:
                #    result.write(zipf.open(zipf.filelist[0]).read().decode('utf-8'))
        keys = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'NumberOfTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'Ignore']
        return [dict(zip(keys, row.split(','))) for row in rows]

    @property
    def pairs(self):
        '''Download and parse all the pairs from klines'''
        if self._pairs == []:
            print('Loading pairs list...')
            request = self.request(self.pairs_url)[1].decode('utf8')
            self._pairs = findall(r'([A-Z0-9]{2,})', request) # there is a bug here: print self._pairs and you will see!! ¯\_(ツ)_/¯
            print('Done.')
        return self._pairs

    @property
    def pair(self):
        
        return self._pair

    @pair.setter
    def pair(self, name):
        if name in self.pairs:
            self._pair = name
        else:
            print('pair not available in pairs list.') # Convert it to and Exception
            self._pair = None

    @pair.deleter
    def pair(self, name):
        del self._pair
    
    @property
    def intervals(self):
        if not self.pair:
            print('Pair not defined.') # Convert it to and Exception
            return []
        
        if not self._intervals:
            url = f'{self.pairs_url}{self.pair}/'
            request = self.request(url)[1].decode('utf8')
            self._intervals = findall(r'(1[dhms]|15m|5m|3m|30m|[2468]h|12h)', request)
        return self._intervals

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval):
        if interval in self.intervals:
            self._interval = interval
        else:
            print('interval not available in intervals list.') # Convert it to and Exception
            self._interval = None

    @interval.deleter
    def interval(self, interval):
        del self._interval
    
    @property
    def items(self):
        if self.pair is None:
            print('Pair not set or invalid.') # Convert it to and Exception
            return False

        if self.interval is None:
            print('Interval not set or invalid.') # Convert it to and Exception
            return False

        url = f'{self.pairs_url}{self.pair}/{self.interval}/'
        
        request = self.request(url)[1].decode('utf8')
        patterns = f'({self.pair}-{self.interval}' + '-[1-3][0-9]{3}-[0-9]{2}-[0-9]{2}.zip)<' # improve this
        self._items = findall(patterns, request)
        return self._items


#binance = BinanceDailyKlines()
#binance.pair = 'CHZTRY'
#binance.interval = '4h'