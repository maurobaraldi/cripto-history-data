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
    break
    print(asset)
    since = datetime.strptime(binance.get(asset).get('since'), '%Y/%m/%d').date()
    intervals = binance.get(asset).get('intervals')
    #print(intervals)
    for interval in intervals:
        print(f'  {interval}')
        while since != datetime.now().date():
            day, month, year = since.day, since.month, since.year
            download_and_extract(asset, interval, day, month, year)
            since = timedelta(days=1) + since
        since = datetime.strptime(binance.get(asset).get('since'), '%Y/%m/%d').date()

# Update Binance - Finish

for f in diff.split('\n'):
    break
    if Path(f).suffix == '.csv':
        repo.index.add(f)
        print(f'Update {Path(f).name} from {Path(f).parent.name}')
        repo.index.commit(f'Update {Path(f).name} from {Path(f).parent.name.upper()}')

# flow to check the files to commit
from datetime import datetime
from subprocess import Popen, PIPE, DEVNULL

#with Popen(['/usr/bin/git', 'status', '-s'], stdout=PIPE) as proc:
#    files = [i.strip() for i in proc.stdout.read().decode('utf8').split('\n') if i.endswith('csv')]

Popen(['/usr/bin/git', 'add', '*.csv'], stdout=DEVNULL)
#Popen(['/usr/bin/git', 'status', '-s'], stdout=PIPE)
Popen(['/usr/bin/git', 'commit', '-m', f'Update data {str(datetime.now().date())}'], stdout=DEVNULL)
Popen(['/usr/bin/git'], 'push', stdout=DEVNULL)
#repo.remotes.origin.push()
