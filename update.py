#!/usr/bin/env python3

from pathlib import Path

from git import Repo

repo = Repo('./')
diff = repo.git.diff(None, name_only=True)

import pdb; pdb.set_trace()
if len(diff) == 0:
    exit()

for f in diff.split('\n'):
    if Path(f).suffix == '.csv':
        repo.index.add(f)
        repo.index.commit(f'Update {Path(f).name} Binance')

repo.remotes.origin.push()
