#!/usr/bin/env python3
"""Verify staged Tier 1 pages against their banked embed files.

For each slug passed on argv (or the default set):
- fetch https://mastermindbehavior.webflow.io/<slug>
- h1 count == 1 and h1 text matches the banked embed's h1
- <title> matches the expected title tag
- meta description matches expected
- embed body renders byte-identically inside div.w-embed (compare the
  section markup after the </style> of the banked file against the page)
- every relative href in the embed resolves 200 on staging (Tier 1 sibling
  targets may be 404 until built: reported as PENDING only if not yet staged)
- em dashes on the page only inside <td>
- JSON-LD schema block present with expected @type Service and page url
"""
import html as html_mod
import json, re, sys, urllib.request

BASE = "https://mastermindbehavior.webflow.io"
EXPECT = {
    "early-intervention-new-jersey": (
        "Early Intervention in New Jersey",
        "Early Intervention in New Jersey | In-Home ABA | Mastermind Behavior",
        "In-home early intervention ABA for young children across New Jersey. How NJEIS works, what changes at age three, and how coverage keeps going.",
    ),
    "parent-training-new-jersey": (
        "Parent Training in New Jersey",
        "Parent Training in New Jersey | In-Home ABA | Mastermind Behavior",
        "In-home ABA parent training for New Jersey families. Hands-on coaching in your own routines, typically covered as part of ABA therapy.",
    ),
    "behavior-support-new-jersey": (
        "Behavior Support in New Jersey",
        "Behavior Support in New Jersey | In-Home ABA | Mastermind Behavior",
        "In-home behavior support across New Jersey. An FBA-based plan built where behaviors happen, from BCBAs licensed in New Jersey.",
    ),
    "transition-planning-georgia": (
        "Transition Planning in Georgia",
        "Transition Planning in Georgia | In-Home ABA | Mastermind Behavior",
        "Georgia's autism supports wind down in the early twenties. Learn how in-home ABA builds adult-life skills through the transition years.",
    ),
    "early-intervention-georgia": (
        "Early Intervention in Georgia",
        "Early Intervention in Georgia | In-Home ABA | Mastermind Behavior",
        "In-home early intervention ABA across Georgia. How Babies Can't Wait works, what changes at age three, and how coverage keeps going.",
    ),
    "parent-training-georgia": (
        "Parent Training in Georgia",
        "Parent Training in Georgia | In-Home ABA | Mastermind Behavior",
        "In-home ABA parent training for Georgia families. Hands-on coaching in your own routines, typically covered as part of ABA therapy.",
    ),
    "behavior-support-georgia": (
        "Behavior Support in Georgia",
        "Behavior Support in Georgia | In-Home ABA | Mastermind Behavior",
        "In-home behavior support across Georgia. An FBA-based plan built where behaviors happen, from state-licensed BCBAs.",
    ),
    "transition-planning-north-carolina": (
        "Transition Planning in North Carolina",
        "Transition Planning in North Carolina | In-Home ABA | Mastermind Behavior",
        "Transition planning with in-home ABA across North Carolina, where Medicaid ABA coverage can continue past 21. Start the skills work early.",
    ),
    "early-intervention-north-carolina": (
        "Early Intervention in North Carolina",
        "Early Intervention in North Carolina | In-Home ABA | Mastermind Behavior",
        "In-home early intervention ABA across North Carolina. How the Infant-Toddler Program works and what changes at age three.",
    ),
    "parent-training-north-carolina": (
        "Parent Training in North Carolina",
        "Parent Training in North Carolina | In-Home ABA | Mastermind Behavior",
        "In-home ABA parent training for North Carolina families. Hands-on coaching in your own routines, typically covered as part of ABA therapy.",
    ),
    "behavior-support-north-carolina": (
        "Behavior Support in North Carolina",
        "Behavior Support in North Carolina | In-Home ABA | Mastermind Behavior",
        "In-home behavior support across North Carolina. An FBA-based plan built where behaviors happen, from state-licensed BCBAs.",
    ),
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mb-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "replace")


def head_ok(path, cache={}):
    if path not in cache:
        try:
            cache[path] = get(BASE + path)[0]
        except Exception as e:
            cache[path] = getattr(e, "code", 0)
    return cache[path]


fails = []
slugs = sys.argv[1:] or list(EXPECT)
for slug in slugs:
    h1x, titlex, metax = EXPECT[slug]
    status, page = get(f"{BASE}/{slug}")
    banked = open(f"content/tier1/build/{slug}.embed.html").read()
    body = banked[banked.index("</style>") + len("</style>") :].strip()
    tag = f"{slug}"

    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    if len(h1s) != 1 or h1s[0].strip() != h1x:
        fails.append(f"{tag}: h1 {h1s!r}")
    t = re.search(r"<title>(.*?)</title>", page, re.S)
    if not t or t.group(1).strip() != titlex:
        fails.append(f"{tag}: title {t and t.group(1)!r}")
    m = re.search(r'<meta content="([^"]*)" name="description"', page) or re.search(
        r'<meta name="description" content="([^"]*)"', page
    )
    if not m or html_mod.unescape(m.group(1)) != metax:
        fails.append(f"{tag}: meta description mismatch")
    if body.split("</div>")[0].split("\n")[0].strip() not in page:
        fails.append(f"{tag}: first embed line not found in page")
    # byte-check the whole embed body: every non-empty line must appear verbatim
    missing = [ln for ln in body.splitlines() if ln.strip() and ln.strip() not in page]
    if missing:
        fails.append(f"{tag}: {len(missing)} embed lines missing, first: {missing[0].strip()[:60]}")
    stripped = re.sub(r"<script.*?</script>", "", page, flags=re.S)
    stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.S)
    in_td = sum(c.count("—") for c in re.findall(r"<td>(.*?)</td>", stripped, re.S))
    total = stripped.count("—")
    if total != in_td:
        fails.append(f"{tag}: {total - in_td} em dashes outside table cells")
    hrefs = sorted(set(re.findall(r'href="(/[^"]*)"', body)))
    for h in hrefs:
        c = head_ok(h)
        if c != 200:
            fails.append(f"{tag}: link {h} -> {c}")
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
    ok = any(
        j.get("@type") == "Service" and j.get("url", "").endswith(slug)
        for j in (json.loads(x) for x in ld)
    )
    if not ok:
        fails.append(f"{tag}: Service JSON-LD missing")
    print(f"{slug}: fetched {status}, {len(hrefs)} links checked, {len(ld)} ld+json blocks")

if fails:
    print("\nFAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("all staged pages verified")
