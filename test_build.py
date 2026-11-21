"""Dataset-builder and dashboard-render tests."""

import json
import os
import unittest

from calhacksdash.build import build
from calhacksdash.dashboard import render

DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "data", "calhacks13", "dataset.json")


class TestBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = build()

    def test_shape(self):
        d = self.dataset
        self.assertEqual(d["hackathon"], "Cal Hacks 13.0")
        self.assertEqual(len(d["projects"]), 651)
        self.assertEqual(len(d["prizes"]), 52)
        self.assertEqual(d["participants"], 1918)

    def test_crosscheck_is_clean(self):
        mm = self.dataset["winner_crosscheck"]
        self.assertEqual(mm["badge_not_in_jsonld"], [])
        self.assertEqual(mm["jsonld_not_on_cards"], [])

    def test_matches_committed_dataset(self):
        with open(DATASET, encoding="utf-8") as fh:
            committed = json.load(fh)
        self.assertEqual(self.dataset["projects"], committed["projects"])
        self.assertEqual(self.dataset["prizes"], committed["prizes"])


class TestRender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DATASET, encoding="utf-8") as fh:
            cls.page = render(json.load(fh))

    def test_headline_figures_present(self):
        for needle in ["1,918", "651", "90", "52", "$204,408+"]:
            self.assertIn(needle, self.page)

    def test_every_project_rendered(self):
        self.assertEqual(self.page.count("https://devpost.com/software/"),
                         # winners table + projects table both link each winner
                         651 + 90)

    def test_provenance_footer(self):
        self.assertIn("cal-hacks-13-0.devpost.com", self.page)
        self.assertIn("2026-11-20", self.page)

    def test_no_placeholder_text(self):
        self.assertNotIn("TODO", self.page)
        self.assertNotIn("lorem", self.page.lower())


if __name__ == "__main__":
    unittest.main()
