# calhacks-dashboard

Cal Hacks 13.0 by the numbers: every project, winner and prize track parsed
from the hackathon's real Devpost pages and rendered into a static dashboard.

I was at Cal Hacks 13.0 and wanted to see the whole thing at once - how many
projects people actually shipped, which tracks had the most winners, what the
prizes were. Devpost shows it one gallery page at a time, so I snapshotted
the pages and parsed them properly.

## the numbers

- **1,918** participants
- **651** projects submitted
- **90** winning projects, cross-checked between the "Winner" badges on the
  gallery cards and the winners JSON-LD list - the two sources agree exactly
- **52** prize tracks, **$204,408+** in prizes

Every figure comes out of the snapshots. Nothing estimated, nothing filled in.

## what's here

- `data/calhacks13/raw/` - trimmed HTML snapshots of the Devpost home page,
  rules, dates, updates and all 28 gallery pages, fetched 2026-11-20
- `data/calhacks13/MANIFEST.json` - which snapshot came from which URL, plus
  honest coverage notes (individual project pages were not snapshotted, so
  tech tags are not in the dataset)
- `calhacksdash/devpost.py` - the parser (stdlib only, regex over the markup)
- `calhacksdash/build.py` - snapshots → `data/calhacks13/dataset.json`,
  with the winner cross-check
- `calhacksdash/dashboard.py` - dataset → `dashboard.html`, a static page
  with the headline numbers, all prize tracks, all winners and all projects

## run it

```bash
python3 calhacksdash/build.py       # rebuild dataset.json from the snapshots
python3 calhacksdash/dashboard.py   # render dashboard.html
python3 -m unittest discover        # 17 tests against the real snapshots
```

stdlib only, nothing to install.

## honesty notes

- The dataset is what Devpost showed on 2026-11-20. If Cal Hacks edits pages
  later, the snapshots stay the record of what they said that day.
- Taglines, names and prize values are verbatim from the pages, including
  the occasional typo.
- Winner status is cross-checked, not assumed: see
  `winner_crosscheck` in the dataset (currently zero mismatches).
