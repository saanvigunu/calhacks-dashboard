"""Render data/calhacks13/dataset.json into a static dashboard.html.

One file, no JavaScript, no framework: the numbers are the point. Every
figure on the page comes out of the dataset, which comes out of the
snapshots - the footer says where and when.
"""

import html
import json
import os

DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       os.pardir, "data", "calhacks13", "dataset.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   os.pardir, "dashboard.html")

CSS = """
body { font-family: Georgia, serif; max-width: 860px; margin: 3rem auto; padding: 0 1rem; color: #1a1a1a; }
h1 { font-size: 1.6rem; margin-bottom: 0.2rem; }
.sub { color: #666; margin-top: 0; }
.stats { display: flex; flex-wrap: wrap; gap: 2rem; margin: 2rem 0; }
.stat .n { font-family: ui-monospace, monospace; font-size: 1.8rem; }
.stat .l { color: #666; font-size: 0.9rem; }
h2 { font-size: 1.1rem; border-bottom: 1px solid #ddd; padding-bottom: 0.3rem; margin-top: 2.5rem; }
table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
td, th { text-align: left; padding: 0.3rem 0.6rem 0.3rem 0; vertical-align: top; }
th { color: #666; font-weight: normal; border-bottom: 1px solid #ddd; }
td.award { font-family: ui-monospace, monospace; font-size: 0.82rem; }
tr.winner td:first-child::before { content: "★ "; color: #b8860b; }
a { color: #1a1a1a; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #666; font-size: 0.85rem; }
"""


def esc(text):
    return html.escape(text or "", quote=True)


def render(dataset):
    winners = [p for p in dataset["projects"] if p["winner"]]
    e = []
    e.append(f"<h1>{esc(dataset['hackathon'])} by the numbers</h1>")
    e.append('<p class="sub">every figure parsed from the hackathon\'s public Devpost pages</p>')

    stats = [
        (f"{dataset['participants']:,}", "participants"),
        (f"{len(dataset['projects']):,}", "projects submitted"),
        (str(len(winners)), "winning projects"),
        (str(len(dataset["prizes"])), "prize tracks"),
        (esc(dataset["prize_pool_text"] or ""), "prize pool"),
    ]
    e.append('<div class="stats">' + "".join(
        f'<div class="stat"><div class="n">{n}</div><div class="l">{esc(l)}</div></div>'
        for n, l in stats) + "</div>")

    e.append("<h2>prize tracks</h2>")
    e.append("<table><tr><th>track</th><th>value</th><th>winners</th></tr>")
    for prize in dataset["prizes"]:
        e.append("<tr>"
                 f"<td>{esc(prize['title'])}</td>"
                 f"<td>{esc(prize['value'] or '')}</td>"
                 f"<td>{esc(prize['winners'] or '')}</td>"
                 "</tr>")
    e.append("</table>")

    e.append("<h2>winners</h2>")
    e.append("<table><tr><th>project</th><th>award</th></tr>")
    for p in winners:
        awards = "; ".join(a.replace(" — Cal Hacks 13.0", "") for a in p["awards"])
        e.append(f'<tr><td><a href="{esc(p["url"])}">{esc(p["name"])}</a></td>'
                 f'<td class="award">{esc(awards)}</td></tr>')
    e.append("</table>")

    e.append(f"<h2>all {len(dataset['projects'])} projects</h2>")
    e.append("<table><tr><th>project</th><th>tagline</th></tr>")
    for p in dataset["projects"]:
        cls = ' class="winner"' if p["winner"] else ""
        e.append(f'<tr{cls}><td><a href="{esc(p["url"])}">{esc(p["name"])}</a></td>'
                 f"<td>{esc(p['tagline'])}</td></tr>")
    e.append("</table>")

    e.append(f"""<footer>
source: <a href="https://{esc(dataset['source'])}">{esc(dataset['source'])}</a>
(Cal Hacks 13.0's official Devpost), snapshotted {esc(dataset['fetched_at'])}.
Numbers are what the pages showed on that date. Raw snapshots and the parser
live in the <a href="https://github.com/saanvigunu/calhacks-dashboard">calhacks-dashboard repo</a>.
Winner status is cross-checked between two independent sources on the pages
(project badges and the winners JSON-LD list): they agree exactly.
</footer>""")

    return ("<!doctype html>\n<html><head><meta charset=\"utf-8\">"
            f"<title>{esc(dataset['hackathon'])} by the numbers</title>"
            f"<style>{CSS}</style></head><body>"
            + "\n".join(e) + "</body></html>\n")


def main():
    with open(DATASET, encoding="utf-8") as fh:
        dataset = json.load(fh)
    page = render(dataset)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"dashboard.html: {len(page)} bytes, "
          f"{sum(1 for p in dataset['projects'] if p['winner'])} winners marked")


if __name__ == "__main__":
    main()
