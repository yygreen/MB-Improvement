#!/usr/bin/env python3
"""Split each state page's single embed into two, so the town grid can sit between.

WHY: the 12 state pages currently render as

    nav -> [one embed: hero .. where-we-serve, FAQ, closing CTA] -> Town Grid -> footer

so the navy "Towns We Serve" block lands AFTER the FAQ and the closing CTA, which
puts a big navigational slab after the page has already asked for the call. The
wanted order is

    nav -> [embed 1: hero .. where-we-serve] -> Town Grid -> [embed 2: FAQ + CTA] -> footer

A Webflow component cannot be nested inside an HtmlEmbed, so the only way to put
the town grid mid-page is to cut the embed in two and place the component between
the halves.

THE STYLE BLOCK STAYS IN PART 1 ONLY
------------------------------------
Every `.mm-*` rule on these pages lives in one inline <style> at the top of the
embed (verified: it is the only style block on the rendered page carrying
`.mm-section`). CSS applies by selector, not by DOM position, and both halves
keep the `.mm-embed mm-t1` wrapper the rules are scoped to - so part 2 needs no
copy of the stylesheet. Duplicating it would add ~4.7 KB per page and create a
second source of truth that could drift.

    python3 tools/tier1/gen-embed-split.py

Reads content/tier1/build/<slug>.embed.html (verified byte-identical to what is
live before generating), writes
content/tier1/build/embedsplit/<slug>.part{1,2}.html
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "content/tier1/build"
OUT = SRC / "embedsplit"

STATES = ["new-jersey", "georgia", "north-carolina"]
SERVICES = ["early-intervention", "parent-training", "behavior-support",
            "transition-planning"]
SLUGS = [f"{s}-{st}" for st in STATES for s in SERVICES]

OPEN = '<div class="mm-embed mm-t1">'
# the cut: everything from the FAQ section onwards moves to part 2
CUT = '  <section class="mm-section mm-section--warm mm-faq">'

# these must never appear in fresh client-facing copy; the split introduces no
# new copy, but assert anyway so a bad edit here cannot slip through
FORBIDDEN = ["—", "–", "RBT", "clinic", "guarantee"]


def sections(markup):
    return re.findall(r'<section class="([^"]*)"', markup)


def visible(markup):
    """Text with tags and the style block stripped, whitespace collapsed."""
    body = markup[markup.index("</style>") + 8:] if "</style>" in markup else markup
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()


def split(markup, slug):
    assert markup.startswith(OPEN), f"{slug}: unexpected wrapper"
    assert markup.rstrip().endswith("</div>"), f"{slug}: unexpected tail"
    assert markup.count(CUT) == 1, f"{slug}: expected exactly one FAQ section"
    assert markup.count('<section class="mm-section mm-cta-close">') == 1, \
        f"{slug}: expected exactly one closing CTA"
    assert markup.count("<style>") == 1 and markup.count("</style>") == 1

    i = markup.index(CUT)
    head, tail = markup[:i], markup[i:]
    # `tail` still carries the wrapper's closing </div>; keep it for part 2 and
    # give part 1 its own.
    assert tail.rstrip().endswith("</div>"), f"{slug}: tail lost the wrapper close"

    part1 = head.rstrip() + "\n</div>\n"
    part2 = OPEN + "\n" + tail.lstrip("\n")

    # --- gates
    assert sections(part1) + sections(part2) == sections(markup), \
        f"{slug}: sections reordered or lost"
    assert len(sections(part2)) == 2, f"{slug}: part 2 should be FAQ + CTA only"
    assert "mm-faq" in sections(part2)[0] and "mm-cta-close" in sections(part2)[1]
    assert "<style>" in part1 and "<style>" not in part2, \
        f"{slug}: stylesheet must stay in part 1 only"
    assert part1.count(OPEN) == part2.count(OPEN) == 1
    for p, name in ((part1, "part1"), (part2, "part2")):
        assert p.count("<div") == p.count("</div>"), f"{slug}: {name} unbalanced divs"
        assert p.count("<section") == p.count("</section>"), f"{slug}: {name} sections"
    # no copy may change, appear or vanish
    assert visible(part1) + " " + visible(part2) == visible(markup), \
        f"{slug}: visible copy changed"
    for w in FORBIDDEN:
        assert w not in visible(part2), f"{slug}: forbidden token {w!r} in part 2"
    return part1, part2


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for slug in SLUGS:
        markup = (SRC / f"{slug}.embed.html").read_text().strip()
        p1, p2 = split(markup, slug)
        (OUT / f"{slug}.part1.html").write_text(p1)
        (OUT / f"{slug}.part2.html").write_text(p2)
        print(f"{slug:36} {len(markup):6,} -> {len(p1):6,} + {len(p2):5,}"
              f"  ({len(sections(p1))} + {len(sections(p2))} sections)")
        total += 1
    print(f"\n{total} page(s) split into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
