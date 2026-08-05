#!/usr/bin/env python3
"""Verify the 9 staged nav-pathway link blocks against their banked files.

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


# wait for the publish: poll the first page until its block renders in the
# expected position (present alone is not enough after a reposition/swap)
first = manifest[0]
first_marker = block_marker((BUILD / f"{first['slug']}.embed.html").read_text())
for attempt in range(24):
    _, page = get(f"{BASE}/{first['slug']}")
    bp = page.find(first_marker)
    mp = page.find("We Accept Most Insurances")
    if bp != -1 and (mp == -1 or bp < mp):
        break
    time.sleep(5)
else:
    sys.exit("publish never landed: block not in expected position after 2 min")

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
    banked = (BUILD / f"{slug}.embed.html").read_text()
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
    # position: service-page blocks sit under the hero (before the
    # insurance-logos section); hub blocks sit above the city grid
    if b["kind"] in ("availin-strip", "svc-states-section"):
        marker_pos = page.find("We Accept Most Insurances")
        marker = "insurance logos"
    else:
        marker_pos = page.find("w-dyn-item")
        marker = "city grid"
    if block_pos != -1 and marker_pos != -1 and block_pos > marker_pos:
        fails.append(f"{slug}: block renders after the {marker}")
    for h in sorted(set(re.findall(r'href="(/[^"]*)"', banked))):
        c = head_ok(h)
        if c != 200:
            fails.append(f"{slug}: link {h} -> {c}")
    # em-dash gate applies to the block we added, not to these pages'
    # pre-existing client-approved copy (hub metas already carry em dashes)
    if "—" in banked:
        fails.append(f"{slug}: em dash inside the banked block")
    print(f"{slug}: block present at offset {block_pos}, links ok" if not any(
        f.startswith(slug) for f in fails) else f"{slug}: FAIL")

if fails:
    print("\nFAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("all 9 link blocks verified on staging")
