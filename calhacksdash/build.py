"""Build data/calhacks13/dataset.json from the raw Devpost snapshots.

Cross-checks rather than merges blindly: the per-card winner badges and the
JSON-LD winners list are two independent sources on the page, so the builder
compares them and reports any disagreement instead of picking one silently.
"""

import glob
import json
import os
import re
from dataclasses import asdict

from .devpost import parse_gallery_page, parse_home, parse_winners_jsonld

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   os.pardir, "data", "calhacks13", "raw")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   os.pardir, "data", "calhacks13", "dataset.json")


def build(raw_dir=RAW):
    projects = []
    for path in sorted(glob.glob(os.path.join(raw_dir, "gallery_p*.html")),
                       key=lambda p: int(re.search(r"\d+", os.path.basename(p)).group())):
        with open(path, encoding="utf-8") as fh:
            projects.extend(parse_gallery_page(fh.read()))

    with open(os.path.join(raw_dir, "gallery_p1.html"), encoding="utf-8") as fh:
        winners_ld = parse_winners_jsonld(fh.read())
    with open(os.path.join(raw_dir, "home.html"), encoding="utf-8") as fh:
        home = parse_home(fh.read())

    # cross-check: cards flagged Winner vs the JSON-LD winners list
    badge_urls = {p.url for p in projects if p.winner}
    ld_urls = {w["url"] for w in winners_ld}
    mismatches = {
        "badge_not_in_jsonld": sorted(badge_urls - ld_urls),
        "jsonld_not_on_cards": sorted(ld_urls - badge_urls),
    }

    # award strings from the JSON-LD list are the canonical source; cards
    # carry the same strings, so fill any project missing them by url.
    awards_by_url = {w["url"]: w["awards"] for w in winners_ld}
    for p in projects:
        if p.winner and not p.awards and p.url in awards_by_url:
            p.awards = awards_by_url[p.url]

    dataset = {
        "hackathon": "Cal Hacks 13.0",
        "source": "cal-hacks-13-0.devpost.com",
        "fetched_at": "2026-11-20",
        "participants": home["participants"],
        "prize_pool_text": home["prize_pool_text"],
        "prizes": home["prizes"],
        "projects": [asdict(p) for p in projects],
        "winner_crosscheck": mismatches,
    }
    return dataset


def main():
    dataset = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=2)
        fh.write("\n")
    n_winners = sum(1 for p in dataset["projects"] if p["winner"])
    print(f"dataset.json: {len(dataset['projects'])} projects, "
          f"{n_winners} winner-flagged, "
          f"{len(dataset['prizes'])} prize tracks, "
          f"crosscheck mismatches: {sum(len(v) for v in dataset['winner_crosscheck'].values())}")


if __name__ == "__main__":
    main()
