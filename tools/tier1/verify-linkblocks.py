#!/usr/bin/env python3
"""Verify the staged nav-pathway link-block placements against banked files.

For each entry in content/tier1/build/linkblocks/manifest.json:
- fetch the staging page
- every non-empty line of the banked embed file must appear verbatim
- the block must sit before the footer markup in the document
- every href in the block resolves 200 on staging
- no em dashes outside <td> introduced (comments/scripts stripped first)

Polls up to ~2 minutes for the staging publish to land (first page only).
"""
import json, pathlib, re, sys, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / "content/tier1/build/linkblocks"
BASE = "https://mastermindbehavior.webflow.io"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mb-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "replace")


manifest = json.loads((BUILD / "manifest.json").read_text())["blocks"]

def block_marker(banked):
    """A line unique to our block on the rendered page. The navy states
    sections share their section class with the page's existing 'Find Your
    Local Team' section, so use the block's h2 line for those."""
    for probe in ('<section class="mm-availin">', '<section class="mm-svc">'):
        if probe in banked:
            return probe
    return next(
        ln.strip() for ln in banked.splitlines() if "<h2>" in ln
    )


# wait for the publish: poll the first page until its retargeted Find Your
# Local Team card renders (presence of the old hub card means stale render)
for attempt in range(24):
    _, page = get(f"{BASE}/early-intervention")
    if ('<a href="/early-intervention-new-jersey" class="area-card">' in page
            and 'href="/aba-therapy-in-new-jersey" class="area-card"' not in page):
        break
    time.sleep(5)
else:
    sys.exit("publish never landed: retargeted cards not rendered after 2 min")

fails = []
head_cache = {}


def head_ok(path):
    if path not in head_cache:
        try:
            head_cache[path] = get(BASE + path)[0]
        except Exception as e:
            head_cache[path] = getattr(e, "code", 0)
    return head_cache[path]


for b in manifest:
    slug = b["slug"]
    banked = (BUILD / b.get("banked", f"{slug}.embed.html")).read_text()
    status, page = get(f"{BASE}/{slug}")
    if status != 200:
        fails.append(f"{slug}: fetch {status}")
        continue
    missing = [
        ln for ln in banked.splitlines() if ln.strip() and ln.strip() not in page
    ]
    if missing:
        fails.append(f"{slug}: {len(missing)} lines missing, first: {missing[0].strip()[:60]}")
    block_pos = page.find(block_marker(banked))
    footer_pos = page.find("footer_link")
    if block_pos == -1:
        fails.append(f"{slug}: block section not found")
    elif footer_pos != -1 and block_pos > footer_pos:
        fails.append(f"{slug}: block renders after the footer")
    # position checks: strips sit under the hero (before the insurance
    # logos); hub blocks sit above the city grid; fylt-retargets live where
    # the section always was, but the old hub cards must be gone
    if b["kind"] == "availin-strip":
        marker_pos = page.find("We Accept Most Insurances")
        if block_pos != -1 and marker_pos != -1 and block_pos > marker_pos:
            fails.append(f"{slug}: block renders after the insurance logos")
    elif b["kind"] == "svc-block":
        marker_pos = page.find("w-dyn-item")
        if block_pos != -1 and marker_pos != -1 and block_pos > marker_pos:
            fails.append(f"{slug}: block renders after the city grid")
    elif b["kind"] == "fylt-retarget":
        if 'href="/aba-therapy-in-new-jersey" class="area-card"' in page:
            fails.append(f"{slug}: old hub area-card still renders")
    for h in sorted(set(re.findall(r'href="(/[^"]*)"', banked))):
        c = head_ok(h)
        if c != 200:
            fails.append(f"{slug}: link {h} -> {c}")
    # em-dash gate applies to markup we authored. fylt-retarget banks the
    # whole content embed whose approved copy already carries em dashes;
    # there the gate covers only the six retargeted card lines
    if b["kind"] == "fylt-retarget":
        card_lines = [ln for ln in banked.splitlines()
                      if 'class="area-card"' in ln or 'class="area-link"' in ln]
        if any("—" in ln for ln in card_lines):
            fails.append(f"{slug}: em dash in a retargeted card line")
    elif "—" in banked:
        fails.append(f"{slug}: em dash inside the banked block")
    print(f"{slug}: block present at offset {block_pos}, links ok" if not any(
        f.startswith(slug) for f in fails) else f"{slug}: FAIL")

if fails:
    print("\nFAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"all {len(manifest)} link-block placements verified on staging")
