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


# The FAQ becomes a native <details>/<summary> accordion: no JavaScript, keyboard
# accessible for free, and the answer text stays in the DOM so it is still indexed.
#
# These rules live in PART 2, not in the base sheet in part 1. The base sheet stays
# where it was; this is the only markup that uses these rules, and keeping them here
# means pages already split do not need their part 1 rewritten to gain the accordion.
ACC_CSS = """  <style>
    /* the FAQ is white and the closing CTA beige - stated, not inherited */
    .mm-faq { background: #fff; }
    .mm-cta-close { background: var(--warm, #f9f6f1); }
    .mm-acc { border-top: 1px solid var(--rule, #e6e2da); }
    .mm-acc__item { border-bottom: 1px solid var(--rule, #e6e2da); }
    .mm-acc__q {
      list-style: none; cursor: pointer;
      display: flex; align-items: flex-start; justify-content: space-between; gap: 20px;
      padding: 20px 0; font-family: var(--font-body); font-weight: 600;
      font-size: 19px; line-height: 1.35; color: var(--navy, #1a2744);
      transition: color 0.15s ease;
    }
    .mm-acc__q::-webkit-details-marker { display: none; }
    .mm-acc__q:hover { color: var(--teal, #3ba5a8); }
    .mm-acc__q::after {
      content: ''; flex: 0 0 auto; width: 10px; height: 10px; margin-top: 6px;
      border-right: 2px solid var(--teal, #3ba5a8); border-bottom: 2px solid var(--teal, #3ba5a8);
      transform: rotate(45deg); transition: transform 0.2s ease;
    }
    .mm-acc__item[open] .mm-acc__q::after { transform: rotate(-135deg); margin-top: 10px; }
    .mm-acc__a { padding: 0 0 22px 0; font-size: 17px; line-height: 1.7; color: var(--text, #2c2c2c); }
    .mm-acc__a p { margin: 0 0 1.1em 0; }
    .mm-acc__a p:last-child { margin-bottom: 0; }
    @media (max-width: 600px) { .mm-acc__q { font-size: 17px; } }
  </style>
"""


def accordion(faq_section, slug):
    """Rewrite the FAQ section's h3/p pairs as a details/summary accordion."""
    # non-greedy: a greedy match runs to the LAST </div> in the section and drags
    # the section's own closing tags into the final answer.
    m = re.search(r'<div class="mm-rt">(.*?)</div>', faq_section, re.S)
    assert m, f"{slug}: FAQ body not found"
    body = m.group(1)
    # the non-greedy match is only correct while the FAQ body has no nested divs
    assert "<div" not in body, f"{slug}: FAQ body has nested divs, revisit the match"
    # each question is an h3; its answer is every paragraph up to the next h3
    pairs = re.findall(r'<h3 class="mm-h3">(.*?)</h3>\s*(.*?)(?=<h3 class="mm-h3">|\Z)',
                       body, re.S)
    assert pairs, f"{slug}: no question/answer pairs found"
    assert len(pairs) == body.count("<h3"), f"{slug}: lost a question"
    items = []
    for q, a in pairs:
        a = a.strip()
        assert a.startswith("<p>") and a.endswith("</p>"), f"{slug}: odd answer markup"
        items.append(
            '        <details class="mm-acc__item">\n'
            f'          <summary class="mm-acc__q">{q}</summary>\n'
            f'          <div class="mm-acc__a">{a}</div>\n'
            "        </details>"
        )
    acc = '      <div class="mm-acc">\n' + "\n".join(items) + "\n      </div>"
    out = faq_section[:m.start()].rstrip() + "\n" + acc + faq_section[m.end():]
    # gates: every question and every answer survives, in order
    for q, a in pairs:
        assert f'<summary class="mm-acc__q">{q}</summary>' in out, f"{slug}: lost {q!r}"
        assert a.strip() in out, f"{slug}: lost an answer"
    assert out.count("<details") == out.count("</details>") == len(pairs)
    assert out.count("<summary") == len(pairs)
    assert "<h3" not in out, f"{slug}: an h3 survived the rewrite"
    return out


# Hero layout copied from /in-home-aba-therapy: text left, image right, 1.05fr to
# 1fr, collapsing to one column at 900px. Measured off that page rather than
# guessed. The image is a placeholder until real art is chosen.
HERO_CSS = """    .mm-hero__grid {
      display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
      gap: clamp(32px, 5vw, 64px); align-items: center;
    }
    .mm-hero__text { min-width: 0; }
    .mm-hero__media {
      position: relative; border-radius: 20px; overflow: hidden;
      aspect-ratio: 4/3; background: #f0ebe3;
    }
    .mm-hero__media img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .mm-hero__placeholder {
      width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
      text-align: center; padding: 20px; font-size: 14px; font-weight: 500; color: #8a8a8a;
      background: linear-gradient(135deg, var(--teal-pale, #e8f6f6) 0%, #f0ebe3 100%);
    }
    @media (max-width: 900px) {
      .mm-hero__grid { grid-template-columns: 1fr; gap: 40px; }
    }
"""

PLACEHOLDER = """        <div class="mm-hero__media">
          <div class="mm-hero__placeholder">Hero image placeholder</div>
        </div>"""


def restyle_hero(part1, slug):
    """Wrap the hero's contents in a two-column grid with a placeholder image."""
    m = re.search(r'(<section class="mm-hero">\s*<div class="mm-hero__inner">)(.*?)'
                  r'(\s*</div>\s*</section>)', part1, re.S)
    assert m, f"{slug}: hero not found"
    inner = m.group(2)
    assert '<div class="mm-hero__grid">' not in inner, f"{slug}: hero already gridded"
    assert inner.count("<h1>") == 1, f"{slug}: hero should hold exactly one h1"
    # re-indent the existing hero content one level deeper, inside the text column
    # the hero content sat 6 spaces deep; inside the grid + text column it is 10
    text = "\n".join(("    " + ln if ln.strip() else ln) for ln in inner.strip("\n").split("\n"))
    grid = ('\n      <div class="mm-hero__grid">\n'
            '        <div class="mm-hero__text">\n'
            f"{text}\n"
            "        </div>\n"
            f"{PLACEHOLDER}\n"
            "      </div>")
    # the captured tail begins with the whitespace that preceded </div></section>
    out_tail = part1[m.end(2):].lstrip("\n ")
    part1 = part1[:m.start(2)] + grid + "\n    " + out_tail
    out = part1

    # widen the hero column: a two-column hero needs the reference page's 1200,
    # not the 900 that suits single-column prose. Body sections stay at 900.
    old = ".mm-hero__inner { max-width: 900px; margin: 0 auto; }"
    assert out.count(old) == 1, f"{slug}: hero inner rule not as expected"
    out = out.replace(old, ".mm-hero__inner { max-width: 1200px; margin: 0 auto; }", 1)
    # add the grid rules right after it
    anchor = ".mm-hero__inner { max-width: 1200px; margin: 0 auto; }\n"
    out = out.replace(anchor, anchor + HERO_CSS, 1)

    assert out.count('<div class="mm-hero__grid">') == 1
    assert out.count('class="mm-hero__placeholder"') == 1
    assert out.count("<h1>") == 1, f"{slug}: h1 lost in the hero rewrite"
    return out


def drop_inline_towns(part1, slug):
    """Remove the 'Where we serve' section whose prose lists towns inline.

    The navy Town Grid component now sits directly below this embed and lists
    every town as a real link, so the paragraph of inline town links is a
    duplicate of it in weaker form.
    """
    m = re.search(r'\n  <section class="mm-section">\s*<div class="mm-section__inner">\s*'
                  r'<h2 class="mm-h2">Where we serve</h2>.*?</section>', part1, re.S)
    assert m, f"{slug}: 'Where we serve' section not found"
    body = m.group(0)
    assert "/areas-we-serve/" in body, f"{slug}: matched section has no town links"
    assert body.count("<section") == 1, f"{slug}: match swallowed another section"
    out = part1[:m.start()] + part1[m.end():]
    assert "/areas-we-serve/" not in out, f"{slug}: inline town links remain"
    assert "Where we serve" not in out, f"{slug}: heading remains"
    return out


def sections(markup):
    return re.findall(r'<section class="([^"]*)"', markup)


def visible(markup):
    """Text with tags and any style blocks stripped, whitespace collapsed."""
    body = re.sub(r"<style>.*?</style>", " ", markup, flags=re.S)
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
    part1 = drop_inline_towns(part1, slug)
    part1 = restyle_hero(part1, slug)

    # split the tail into the FAQ section and everything after it (the closing CTA),
    # rewrite the FAQ as an accordion, and prepend the accordion-only stylesheet
    cta_at = tail.index('  <section class="mm-section mm-cta-close">')
    faq, rest = tail[:cta_at], tail[cta_at:]
    faq = faq.replace('<section class="mm-section mm-section--warm mm-faq">',
                      '<section class="mm-section mm-faq">', 1)
    part2 = OPEN + "\n" + ACC_CSS + accordion(faq.rstrip(), slug) + "\n" + rest.lstrip("\n")

    # --- gates
    assert len(sections(part1)) == len(sections(markup)) - 3, \
        f"{slug}: expected part 1 to lose the inline-towns section to part 2's two"
    assert len(sections(part2)) == 2, f"{slug}: part 2 should be FAQ + CTA only"
    assert "mm-faq" in sections(part2)[0] and "mm-cta-close" in sections(part2)[1]
    assert "mm-section--warm" not in sections(part2)[0], f"{slug}: FAQ still beige"
    assert "Where we serve" not in part1 and "Where we serve" not in part2
    assert "<style>" in part1, f"{slug}: base stylesheet must stay in part 1"
    # part 2 carries ONLY the accordion rules - never a copy of the base sheet
    assert part2.count("<style>") == 1, f"{slug}: part 2 should have one style block"
    assert ".mm-section {" not in part2 and ".mm-hero" not in part2, \
        f"{slug}: part 2 must not duplicate the base sheet"
    assert part1.count(OPEN) == part2.count(OPEN) == 1
    for p, name in ((part1, "part1"), (part2, "part2")):
        assert p.count("<div") == p.count("</div>"), f"{slug}: {name} unbalanced divs"
        assert p.count("<section") == p.count("</section>"), f"{slug}: {name} sections"
    # no copy may change, appear or vanish
    expect = visible(drop_inline_towns(markup, slug)) + " Hero image placeholder"
    got = visible(part1) + " " + visible(part2)
    assert sorted(got.split()) == sorted(expect.split()), f"{slug}: visible copy changed"
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
