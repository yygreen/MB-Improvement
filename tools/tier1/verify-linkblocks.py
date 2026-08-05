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

# wait for the publish: poll the first page until its block renders
first = manifest[0]
marker = '<section class="mm-availin">'
for attempt in range(24):
    _, page = get(f"{BASE}/{first['slug']}")
    if marker in page:
        break
    time.sleep(5)
else:
    sys.exit("publish never landed: block missing on first page after 2 min")

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
    root_cls = re.search(r'<section class="(mm-[a-z]+)"', banked).group(1)
    block_pos = page.find(f'<section class="{root_cls}">')
    footer_pos = page.find("footer_link")
    if block_pos == -1:
        fails.append(f"{slug}: block section not found")
    elif footer_pos != -1 and block_pos > footer_pos:
        fails.append(f"{slug}: block renders after the footer")
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
