#!/usr/bin/env python3

from datetime import datetime, timedelta
from io import BytesIO
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
    print(f'Downloading data for {asset}-{interval} from {day}/{month}/{year}')
    try:
        with urlopen(request) as r:
            with ZipFile(BytesIO(r.read())) as zipf:
                with open(f'./data/binance/{asset}-{interval}.csv', 'a') as result:
                    result.write(zipf.open(zipf.filelist[0]).read().decode('utf-8'))
    except HTTPError:
        print(f'Error downloading {klinesBaseURL}/{asset}/{interval}/{asset}-{interval}-{year}-{month:02}-{day:02}.zip file.')

#download_and_extract('LTCBRL', '12h', 16, 12, 2022)