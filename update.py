#!/usr/bin/env python3

from pathlib import Path

from git import Repo
import pdb; pdb.set_trace()

repo = Repo('./')
diff = repo.index.diff(None, name_only=True)

if len(diff) == 0:
    exit()

for f in diff:
    if Path(f).suffix == '.csv':
        repo.index.add(f)
        repo.index.commit(f'Update {Path(f).name} Binance')

repo.remotes.origin.push()