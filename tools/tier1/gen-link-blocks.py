#!/usr/bin/env python3
"""Generate the 9 nav-pathway link-block embeds (ship plan step 2).

Six "Available in:" state strips for the generic service pages and three
four-link services blocks for the state hubs. Visual language lifted from
the client-approved town-services-block mockup (same tokens: navy #1a2744,
teal #3ba5a8, warm #f9f6f1, rule #e6e2da, Manrope); the hub block reuses the
approved fixed byline sentence with only the state name varying.

Decision made this session, flagged for user review via screenshots:
/in-home-aba-therapy and /skill-development have no per-state Tier 1 pages,
so their strips link to the three state hubs (/aba-therapy-in-<state>).

Gates: no em dashes, no RBT, no clinic/center/guarantee language, href
whitelist against the known Tier 1 slugs and hubs, single <style> block,
every block is one <section> root.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "content/tier1/build/linkblocks"
OUT.mkdir(exist_ok=True)

STATES = [("new-jersey", "New Jersey"), ("georgia", "Georgia"),
          ("north-carolina", "North Carolina")]
SERVICES = [("early-intervention", "Early Intervention"),
            ("parent-training", "Parent Training"),
            ("behavior-support", "Behavior Support"),
            ("transition-planning", "Transition Planning")]

VALID_HREFS = {f"/{s}-{k}" for s, _ in SERVICES for k, _ in STATES} | {
    f"/aba-therapy-in-{k}" for k, _ in STATES
}

STRIP_CSS = """  .mm-availin { background: #f9f6f1; border-top: 1px solid #e6e2da; padding: 28px clamp(20px, 5vw, 48px); font-family: 'Manrope', system-ui, sans-serif; }
  .mm-availin__inner { max-width: 900px; margin: 0 auto; display: flex; align-items: center; flex-wrap: wrap; gap: 12px 18px; }
  .mm-availin__label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #8a8578; }
  .mm-availin nav { display: flex; flex-wrap: wrap; gap: 10px; }
  .mm-availin a { display: inline-flex; align-items: center; gap: 8px; background: #fff; border: 1px solid #e6e2da; border-radius: 10px; padding: 10px 14px; text-decoration: none; font-size: 14px; font-weight: 600; color: #1a2744; transition: border-color .15s ease, transform .15s ease, box-shadow .15s ease; }
  .mm-availin a::after { content: '\\2192'; color: #3ba5a8; font-weight: 700; }
  .mm-availin a:hover { border-color: #3ba5a8; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(26,39,68,0.07); }"""

SVC_CSS = """  .mm-svc { background: #f9f6f1; border-top: 1px solid #e6e2da; padding: clamp(36px, 5vw, 56px) clamp(20px, 5vw, 48px); font-family: 'Manrope', system-ui, sans-serif; }
  .mm-svc__inner { max-width: 900px; margin: 0 auto; }
  .mm-svc h2 { font-weight: 600; font-size: clamp(22px, 3vw, 30px); line-height: 1.15; letter-spacing: -0.01em; color: #1a2744; margin: 0 0 10px; }
  .mm-svc .mm-svc__lede { font-size: 16px; line-height: 1.6; color: #5a5a5a; margin: 0 0 22px; max-width: 62ch; }
  .mm-svc nav { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }
  .mm-svc a { display: flex; align-items: center; justify-content: space-between; gap: 10px; background: #fff; border: 1px solid #e6e2da; border-radius: 12px; padding: 16px 18px; text-decoration: none; font-size: 15px; font-weight: 600; color: #1a2744; transition: border-color .15s ease, transform .15s ease, box-shadow .15s ease; }
  .mm-svc a::after { content: '\\2192'; color: #3ba5a8; font-weight: 700; }
  .mm-svc a:hover { border-color: #3ba5a8; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(26,39,68,0.07); }"""


def strip(aria, links):
    a = "\n".join(f'      <a href="{h}">{t}</a>' for h, t in links)
    return (
        f"<style>\n{STRIP_CSS}\n</style>\n"
        '<section class="mm-availin">\n'
        '  <div class="mm-availin__inner">\n'
        '    <span class="mm-availin__label">Available in:</span>\n'
        f'    <nav aria-label="{aria}">\n{a}\n    </nav>\n'
        "  </div>\n</section>\n"
    )


def svc_block(state_name, state_key):
    a = "\n".join(
        f'        <a href="/{s}-{state_key}">{label}</a>' for s, label in SERVICES
    )
    return (
        f"<style>\n{SVC_CSS}\n</style>\n"
        '<section class="mm-svc">\n'
        '  <div class="mm-svc__inner">\n'
        f"    <h2>ABA services in {state_name}</h2>\n"
        f'    <p class="mm-svc__lede">All four are delivered in your home by a BCBA-led team, anywhere we serve in {state_name}.</p>\n'
        '    <nav aria-label="ABA services">\n'
        f"{a}\n"
        "    </nav>\n  </div>\n</section>\n"
    )


BLOCKS = {}
for s, label in SERVICES:
    BLOCKS[s] = strip(
        f"{label} by state", [(f"/{s}-{k}", n) for k, n in STATES]
    )
for slug in ("in-home-aba-therapy", "skill-development"):
    BLOCKS[slug] = strip(
        "In-home ABA by state", [(f"/aba-therapy-in-{k}", n) for k, n in STATES]
    )
for k, n in STATES:
    BLOCKS[f"aba-therapy-in-{k}"] = svc_block(n, k)

FORBIDDEN = ["—", "RBT", "rbt", "clinic", "center", "guarantee", "–"]
for slug, html in BLOCKS.items():
    body = html[html.index("</style>") :]
    for w in FORBIDDEN:
        assert w not in body, f"{slug}: forbidden token {w!r}"
    assert html.count("<style>") == 1 and html.count("<section") == 1, slug
    hrefs = re.findall(r'href="([^"]+)"', html)
    assert hrefs and all(h in VALID_HREFS for h in hrefs), f"{slug}: bad href {hrefs}"
    exp = 4 if slug.startswith("aba-therapy-in-") else 3
    assert len(hrefs) == exp, f"{slug}: {len(hrefs)} links, expected {exp}"
    (OUT / f"{slug}.embed.html").write_text(html)
    print(f"{slug}: {len(html)} bytes, {len(hrefs)} links, gates pass")

print(f"\n{len(BLOCKS)} blocks written to {OUT.relative_to(ROOT)}/")
