#!/usr/bin/env python3

from datetime import datetime, timedelta
from json import loads
from pathlib import Path

from git import Repo

from bin.scrappers.binance import download_and_extract

repo = Repo('./')
diff = repo.git.diff(None, name_only=True)

# Update Binance - Start
with open('./binance.json') as _:
    binance = loads(_.read())

for asset in binance:
    print(asset)
    since = datetime.strptime(binance.get(asset).get('since'), '%Y/%m/%d').date()
    intervals = binance.get(asset).get('intervals')
    print(intervals)
    for interval in intervals:
        print(interval)
        while since != datetime.now().date():
            day, month, year = since.day, since.month, since.year
            download_and_extract(asset, interval, day, month, year)
            since = timedelta(days=1) + since
        since = datetime.strptime(binance.get(asset).get('since'), '%Y/%m/%d').date()

# Update Binance - Finish

for f in diff.split('\n'):
    if Path(f).suffix == '.csv':
        repo.index.add(f)
        print(f'Update {Path(f).name} from {Path(f).parent.name}')
        repo.index.commit(f'Update {Path(f).name} from {Path(f).parent.name.upper()}')

#repo.remotes.origin.push()
