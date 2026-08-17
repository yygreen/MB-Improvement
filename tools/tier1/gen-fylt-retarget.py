#!/usr/bin/env python3
"""Retarget the 'Find Your Local Team' card links on the four service pages
with Tier 1 state variants: /aba-therapy-in-<state> -> /<service>-<state>,
and the card link text 'ABA therapy in <State>' -> '<Service> in <State>'.

Source of truth: tools/css-consolidation/linkfix/<slug>.body.fixed.html,
the banked byte-exact copy of each page's content embed as it sits in
Webflow. Step 1 asserts that copy still matches the rendered staging page
line-for-line; step 2 applies exactly six substring replacements; step 3
writes the new embed to content/tier1/build/linkblocks/fylt/ and updates
the linkfix bank so it keeps tracking what is actually in Webflow.
"""
import pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
LINKFIX = ROOT / "tools/css-consolidation/linkfix"
OUT = ROOT / "content/tier1/build/linkblocks/fylt"
OUT.mkdir(exist_ok=True)
BASE = "https://mastermindbehavior.webflow.io"

SERVICES = {
    "early-intervention": "Early Intervention",
    "parent-training": "Parent Training",
    "behavior-support": "Behavior Support",
    "transition-planning": "Transition Planning",
}
STATES = [("new-jersey", "New Jersey"), ("georgia", "Georgia"),
          ("north-carolina", "North Carolina")]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mb-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


for slug, label in SERVICES.items():
    src = (LINKFIX / f"{slug}.body.fixed.html").read_text()
    page = get(f"{BASE}/{slug}")
    missing = [ln for ln in src.splitlines() if ln.strip() and ln.strip() not in page]
    assert not missing, f"{slug}: linkfix bank no longer matches staging, first miss: {missing[0].strip()[:70]}"

    new = src
    for key, name in STATES:
        old_href = f'href="/aba-therapy-in-{key}" class="area-card"'
        new_href = f'href="/{slug}-{key}" class="area-card"'
        assert new.count(old_href) == 1, f"{slug}: {old_href} x{new.count(old_href)}"
        new = new.replace(old_href, new_href)
        old_txt = f'<span class="area-link">ABA therapy in {name} →</span>'
        new_txt = f'<span class="area-link">{label} in {name} →</span>'
        assert new.count(old_txt) == 1, f"{slug}: link text for {name} x{new.count(old_txt)}"
        new = new.replace(old_txt, new_txt)

    # exactly six lines differ, nothing else
    diff = [
        (a, b) for a, b in zip(src.splitlines(), new.splitlines()) if a != b
    ]
    assert len(diff) == 6 and len(src.splitlines()) == len(new.splitlines()), \
        f"{slug}: {len(diff)} changed lines, expected 6"
    assert "—" not in new.replace("—", "—", 0) or new.count("—") == src.count("—"), slug

    (OUT / f"{slug}.embed.html").write_text(new)
    (LINKFIX / f"{slug}.body.fixed.html").write_text(new)
    print(f"{slug}: 6 replacements applied, {len(new)} bytes, bank matches staging")

print("\nall four generated; linkfix bank updated to the new target state")
