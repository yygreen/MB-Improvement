"""Prove each new hero-image gate actually fires. A gate that cannot fail is decoration."""
import sys, importlib
sys.path.insert(0, "tools/tier1")
g = importlib.import_module("gen-embed-split".replace("-", "_")) if False else None
import importlib.util
spec = importlib.util.spec_from_file_location("gen", "tools/tier1/gen-embed-split.py")
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)

SLUG = "early-intervention-north-carolina"
GOOD = ("https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/aaa_ei-nc.jpg",
        "Behavior Technician and toddler stacking nesting cups on a living room rug")

CASES = [
    ("off-host url", ("https://example.com/x.jpg", GOOD[1]), "Webflow-hosted"),
    ("quote in alt", (GOOD[0], 'a "quoted" phrase in the alt text here'), "quote"),
    ("alt too short", (GOOD[0], "Boy playing"), "alt text length"),
    ("alt too long", (GOOD[0], " ".join(["word"] * 21)), "alt text length"),
    ("forbidden token", (GOOD[0], "Behavior Technician and child in our clinic playroom"), "forbidden token"),
]
fails = []
for name, entry, want in CASES:
    gen.HERO_IMG = {SLUG: entry}
    try:
        gen.hero_media(SLUG)
    except AssertionError as e:
        if want in str(e):
            print(f"  PASS  {name:18} -> {e}")
        else:
            fails.append(f"{name}: wrong message {e}")
        continue
    fails.append(f"{name}: NO ASSERTION FIRED")

# and the happy path must produce an img with no placeholder, through the full split
gen.HERO_IMG = {SLUG: GOOD}
markup = open(f"content/tier1/build/{SLUG}.embed.html").read().strip()
p1, p2 = gen.split(markup, SLUG)
for cond, msg in [
    (f'src="{GOOD[0]}"' in p1, "img src missing"),
    (f'alt="{GOOD[1]}"' in p1, "alt missing"),
    ("mm-hero__placeholder\"" not in p1, "placeholder survived"),
    ("Hero image placeholder" not in gen.visible(p1), "placeholder text survived"),
    ('width="1200" height="900"' in p1, "intrinsic size missing"),
]:
    if not cond:
        fails.append(f"happy path: {msg}")
print("  PASS  happy path      -> img emitted, placeholder gone, copy gate held" if not any(
    f.startswith("happy") for f in fails) else "")

# and a mismatched map must be caught by the positive gate in restyle_hero
gen.HERO_IMG = {SLUG: GOOD}
orig = gen.hero_media
gen.hero_media = lambda s: gen.PLACEHOLDER   # simulate the map silently not applying
try:
    gen.split(markup, SLUG)
    fails.append("silent no-op: NO ASSERTION FIRED")
except AssertionError as e:
    print(f"  PASS  silent no-op      -> {e}")
gen.hero_media = orig

print("\nFAILURES:" if fails else "\nall gates fire")
for f in fails: print("  " + f)
sys.exit(1 if fails else 0)
