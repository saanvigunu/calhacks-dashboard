"""Parse Devpost hackathon pages (Cal Hacks 13.0) into plain records.

Everything here reads the committed snapshots under data/calhacks13/raw/ and
keeps the site's own values verbatim. Nothing is estimated: a field the page
does not publish stays None.
"""

import json
import re
from dataclasses import dataclass, field
from html import unescape


@dataclass
class Project:
    software_id: str        # Devpost's numeric id, from the card's div id
    name: str
    tagline: str
    url: str
    winner: bool
    awards: list            # verbatim award strings, e.g. "Winner, Cal Hacks First Overall — Cal Hacks 13.0"
    team: list              # devpost profile handles, verbatim from data-url


def _clean(text):
    return unescape(re.sub(r"\s+", " ", text or "")).strip()


def parse_gallery_page(html_text):
    """Parse one project-gallery page into Project records.

    Cards are div.gallery-item blocks. Winner cards carry an
    <aside class="entry-badge">Winner</aside> and, in the snapshots, a
    per-project JSON-LD block naming the exact award(s). Team members are
    profile spans whose data-url is the member's Devpost profile.
    """
    projects = []
    for block in re.split(r'<div class="[^"]*gallery-item[^"]*"[^>]*data-software-id="', html_text)[1:]:
        software_id, _, rest = block.partition('"')
        m = re.search(r'link-to-software" href="([^"]+)"', rest)
        url = m.group(1) if m else None
        m = re.search(r"<h5>\s*(.*?)\s*</h5>", rest, re.S)
        name = _clean(m.group(1)) if m else ""
        m = re.search(r'<p class="small tagline">\s*(.*?)\s*</p>', rest, re.S)
        tagline = _clean(m.group(1)) if m else ""
        winner = bool(re.search(r'<aside class="entry-badge">\s*Winner', rest))
        awards = []
        for jm in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', rest, re.S):
            try:
                data = json.loads(jm.group(1))
            except json.JSONDecodeError:
                continue
            awards.extend(data.get("award") or [])
        team = re.findall(r'data-url="https://devpost\.com/([^"/]+)"', rest)
        projects.append(Project(software_id=software_id, name=name, tagline=tagline,
                                url=url, winner=winner, awards=awards, team=team))
    return projects


def parse_winners_jsonld(html_text):
    """Read the challenge-winners-json-ld ItemList from gallery page 1.

    Returns one record per winner: name, url, awards (verbatim list).
    """
    m = re.search(r'id="challenge-winners-json-ld">\s*(\{.*?\})\s*</script>', html_text, re.S)
    if not m:
        return []
    data = json.loads(m.group(1))
    return [{"name": item.get("name"), "url": item.get("url"),
             "awards": item.get("award") or []}
            for item in data.get("itemListElement", [])]


def parse_home(html_text):
    """Pull the headline numbers and prize list off the hackathon home page."""
    out = {"participants": None, "prize_pool_text": None, "prizes": []}
    m = re.search(r"Participants \(([\d,]+)\)", html_text)
    if m:
        out["participants"] = int(m.group(1).replace(",", ""))
    m = re.search(r'data-currency-value>([\d,]+)</span></span>\+ in prizes', html_text)
    if m:
        out["prize_pool_text"] = "$" + m.group(1) + "+ in prizes"
    # one div.prize per track: title, optional cash value, "N winner(s)", description
    for block in re.split(r'<div class="[^"]*prize" id="prize_\d+">', html_text)[1:]:
        prize = {"title": None, "value": None, "winners": None, "description": None}
        m = re.search(r'<div class="prize-title">.*?<div>\s*(.*?)\s*</div>', block, re.S)
        if m:
            prize["title"] = _clean(m.group(1))
        m = re.search(r'<div class="prize-value">(.*?)</div>', block, re.S)
        if m:
            prize["value"] = _clean(re.sub(r"<[^>]+>", "", m.group(1)))
        m = re.search(r'<div class="prize-winners">\s*(.*?)\s*</div>', block, re.S)
        if m:
            prize["winners"] = _clean(m.group(1))
        m = re.search(r"<p>(.*?)</p>", block, re.S)
        if m:
            prize["description"] = _clean(m.group(1))
        if prize["title"]:
            out["prizes"].append(prize)
    return out
