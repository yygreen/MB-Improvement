#!/usr/bin/env python3
"""Generate the per-state town grid embeds for the 12 Tier 1 state pages.

Why this is static rather than a CMS Collection List
----------------------------------------------------
The hubs use a real Collection List (DynamoWrapper -> DynamoList -> DynamoItem)
whose card link uses link mode "collectionPage" to reach the current item's
page. That mode CANNOT be reproduced through the Data API: setting
`link = {mode: "collectionPage"}` publishes as href="#", and adding
`to.pageSlug` publishes the slug literally. get_bindable_sources reports NO
source bindable to a `link` value on the collection item, so there is no API
path to "link to current item". Wiring it needs one Designer click per card.

So the grid here is generated from the LIVE hub pages (the client-approved
source of truth) and rendered as static markup with real hrefs. Visually it
matches the hub grid; it just does not auto-pick-up new towns. If a town is
added later, re-run this and re-apply.

Live town counts (2026-08-05, scraped from the hubs): NJ 115, GA 78, NC 20.
NOTE the CMS reports 992 items total (NJ 517 / GA 455 / NC 20) but the great
majority are ARCHIVED and unpublished - see the build record.

    python3 tools/tier1/gen-town-grids.py

Reads tools/tier1/towns.json, writes content/tier1/build/towngrids/<slug>.embed.html
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "content/tier1/build/towngrids"
OUT.mkdir(parents=True, exist_ok=True)
TOWNS = json.loads((ROOT / "tools/tier1/towns.json").read_text())

STATES = [("new-jersey", "New Jersey"), ("georgia", "Georgia"),
          ("north-carolina", "North Carolina")]
SERVICES = [("early-intervention", "Early Intervention", "early intervention"),
            ("parent-training", "Parent Training", "parent training"),
            ("behavior-support", "Behavior Support", "behavior support"),
            ("transition-planning", "Transition Planning", "transition planning")]

CSS = """  .mm-towns { background: #1a2744; padding: clamp(48px, 6vw, 80px) clamp(20px, 5vw, 48px); font-family: 'Manrope', system-ui, sans-serif; }
  .mm-towns__inner { max-width: 1200px; margin: 0 auto; }
  .mm-towns__head { text-align: center; margin: 0 0 40px; }
  .mm-towns__label { font-size: 12px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #8fa0bd; margin: 0 0 14px; }
  .mm-towns h2 { font-weight: 700; font-size: clamp(26px, 3.4vw, 38px); line-height: 1.15; letter-spacing: -0.015em; color: #fff; margin: 0 0 14px; }
  .mm-towns__lede { font-size: 16px; line-height: 1.65; color: #b9c3d6; margin: 0 auto; max-width: 62ch; }
  .mm-towns__lede a { color: #5fc6c9; font-weight: 600; text-decoration: none; }
  .mm-towns__lede a:hover { text-decoration: underline; }
  .mm-towns nav { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 10px 18px; }
  .mm-towns nav a { display: block; padding: 9px 12px; border-radius: 8px; font-size: 15px; font-weight: 600; line-height: 1.35; color: #fff; text-decoration: none; transition: background .15s ease, color .15s ease; }
  .mm-towns nav a:hover { background: #232f4e; color: #5fc6c9; }
  @media (max-width: 479px) { .mm-towns nav { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); } }"""


def grid(state_key, state_name):
    # the CMS holds duplicate town names in places (e.g. two Georgia "Perry"
    # items, slugs perry and perry-043a7). The hub renders both; showing the
    # same town twice reads as a bug, so keep the first of each NAME.
    seen, towns = set(), []
    for t in TOWNS[state_key]:
        if t["name"] in seen:
            continue
        seen.add(t["name"]); towns.append(t)
    links = "\n".join(
        f'        <a href="/areas-we-serve/{t["slug"]}">{html.escape(t["name"])}</a>'
        for t in towns
    )
    return (
        '<div class="mm-embed">\n'
        f"<style>\n{CSS}\n</style>\n"
        '<section class="mm-towns">\n'
        '  <div class="mm-towns__inner">\n'
        '    <div class="mm-towns__head">\n'
        '      <div class="mm-towns__label">Where we serve</div>\n'
        f"      <h2>Towns We Serve Across {state_name}</h2>\n"
        f'      <p class="mm-towns__lede">We bring in-home ABA to {len(towns)} '
        f'{state_name} communities. Find your town below, or see our '
        f'<a href="/aba-therapy-in-{state_key}">{state_name} page</a>.</p>\n'
        "    </div>\n"
        f'    <nav aria-label="{state_name} towns we serve">\n{links}\n    </nav>\n'
        "  </div>\n</section>\n</div>\n"
    )


FORBIDDEN = ["—", "–", "RBT", "clinic", "guarantee"]
manifest = []
for k, n in STATES:
        page = k
        markup = grid(k, n)
        body = markup[markup.index("</style>"):]
        for w in FORBIDDEN:
            assert w not in body, f"{page}: forbidden token {w!r}"
        hrefs = [h for h in markup.split('href="')[1:]]
        assert markup.count("<h2>") == 1, page
        assert markup.count("<section") == 1, page
        n_town = markup.count('href="/areas-we-serve/')
        (OUT / f"{page}.embed.html").write_text(markup)
        manifest.append((page, n_town, len(markup)))
        print(f"{page:38} {n_town:3} towns  {len(markup):6,} bytes")

print(f"\n{len(manifest)} grids written to {OUT.relative_to(ROOT)}/")
