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
    items = binance.get(asset).get('items')
    for item in items:
        download_and_extract(asset, item, since.day, since.month, since.year)

# Update Binance - Finish

for f in diff.split('\n'):
    if Path(f).suffix == '.csv':
        repo.index.add(f)
        print(f'Update {Path(f).name} from {Path(f).parent.name}')
        repo.index.commit(f'Update {Path(f).name} from {Path(f).parent.name.upper()}')

repo.remotes.origin.push()
