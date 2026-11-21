"""Parser tests against the committed Devpost snapshots.

The expected numbers are the real contents of the snapshots (Cal Hacks 13.0,
fetched 2026-11-20): if Devpost markup or our trimming ever makes the parser
drift, these counts move.
"""

import glob
import os
import unittest

from calhacksdash.devpost import (parse_gallery_page, parse_home,
                                  parse_winners_jsonld)

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "data", "calhacks13", "raw")


def read(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as fh:
        return fh.read()


def all_projects():
    projects = []
    for path in sorted(glob.glob(os.path.join(RAW, "gallery_p*.html"))):
        with open(path, encoding="utf-8") as fh:
            projects.extend(parse_gallery_page(fh.read()))
    return projects


class TestGallery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = all_projects()

    def test_total_projects(self):
        self.assertEqual(len(self.projects), 651)

    def test_winner_badge_count(self):
        self.assertEqual(sum(1 for p in self.projects if p.winner), 90)

    def test_every_project_complete(self):
        for p in self.projects:
            self.assertTrue(p.software_id.isdigit(), p)
            self.assertTrue(p.name, f"empty name for {p.software_id}")
            self.assertTrue(p.url and p.url.startswith("https://devpost.com/software/"), p.name)
            self.assertTrue(p.tagline, f"empty tagline for {p.name}")

    def test_winners_have_awards(self):
        for p in self.projects:
            if p.winner:
                self.assertTrue(p.awards, f"winner without award text: {p.name}")

    def test_unique_ids(self):
        ids = [p.software_id for p in self.projects]
        self.assertEqual(len(ids), len(set(ids)))

    def test_first_card_known_values(self):
        # first card of page 1 as fetched: the overall winner
        first = self.projects[0]
        self.assertEqual(first.name, "Sophi - The Physical Augmentation Walker")
        self.assertTrue(first.winner)
        self.assertTrue(any("First Overall" in a for a in first.awards))
        self.assertEqual(len(first.team), 4)


class TestWinnersJsonLd(unittest.TestCase):
    def test_winners_list(self):
        winners = parse_winners_jsonld(read("gallery_p1.html"))
        self.assertEqual(len(winners), 90)
        for w in winners:
            self.assertTrue(w["name"])
            self.assertTrue(w["awards"])

    def test_card_badges_match_jsonld(self):
        # two independent sources on the same pages must agree
        badge_urls = {p.url for p in all_projects() if p.winner}
        ld_urls = {w["url"] for w in parse_winners_jsonld(read("gallery_p1.html"))}
        self.assertEqual(badge_urls, ld_urls)


class TestHome(unittest.TestCase):
    def test_headline_numbers(self):
        home = parse_home(read("home.html"))
        self.assertEqual(home["participants"], 1918)
        self.assertEqual(home["prize_pool_text"], "$204,408+ in prizes")

    def test_prize_tracks(self):
        home = parse_home(read("home.html"))
        self.assertEqual(len(home["prizes"]), 52)
        first = home["prizes"][0]
        self.assertEqual(first["title"], "Cal Hacks First Overall")
        self.assertEqual(first["winners"], "1 winner")
        for prize in home["prizes"]:
            self.assertTrue(prize["title"])
            self.assertTrue(prize["winners"])


if __name__ == "__main__":
    unittest.main()
