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
    .mm-cta-close__lede {
      font-size: 18px; line-height: 1.7; color: var(--soft, #5a5a5a);
      max-width: 60ch; margin: 0 auto;
    }
    .mm-acc { border-top: 1px solid var(--rule, #e6e2da); }
    .mm-acc__item { border-bottom: 1px solid var(--rule, #e6e2da); }
    .mm-acc__q {
      list-style: none; cursor: pointer;
      display: flex; align-items: flex-start; justify-content: space-between; gap: 20px;
      padding: 20px 0; font-family: var(--font-body); font-weight: 600;
      font-size: 18px; line-height: 1.35; color: var(--navy, #1a2744);
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
    .mm-acc__a { padding: 0 0 22px 0; line-height: 1.7; color: var(--text, #2c2c2c); }
    /* size the P itself: a global Webflow rule sets p to 1.125rem, which beats
       anything inherited from the container - see the note in the base sheet */
    .mm-acc__a p { font-size: 18px; margin: 0 0 1.1em 0; }
    .mm-acc__a p:last-child { margin-bottom: 0; }
  </style>
"""


# A byline under the closing headline. Written per service, with the state name
# inserted, so twelve pages do not all close on the same sentence. Each one
# lowers the barrier to the click rather than promising a result: the copy gates
# forbid outcome guarantees, and these are deliberately about what the
# conversation is, not what it will achieve.
CTA_LEDE = {
    "early-intervention":
        "Tell us what you are seeing at home and we will walk you through what "
        "starts when in {state}. There is no onboarding waitlist, and assessment "
        "takes about four weeks.",
    "parent-training":
        "Bring the routine that is hardest right now. We will talk through what "
        "coaching in your own home would look like for your family in {state}.",
    # behavior-support deliberately does NOT name the state. Every phrasing that
    # bolted it on read as filler ("anywhere in {state}"), and the sentence is
    # stronger ending on the plan than on geography.
    "behavior-support":
        "Describe what is happening at home and we will talk through how an "
        "assessment works and what a plan built around your routines would involve.",
    "transition-planning":
        "Tell us where your child sits in the {state} timeline and we will talk "
        "through what is worth starting now and what can wait.",
}

def cta_byline(part2, slug):
    """Add a paragraph under the closing CTA headline, above the buttons."""
    service = next(k for k in CTA_LEDE if slug.startswith(k))
    state = slug[len(service) + 1:].replace("-", " ").title()
    lede = CTA_LEDE[service].format(state=state)
    for w in FORBIDDEN:
        assert w not in lede, f"{slug}: forbidden token {w!r} in the CTA byline"
    assert "guarantee" not in lede.lower()

    m = re.search(r'(<section class="mm-section mm-cta-close">.*?</h2>\n)(\s*)'
                  r'(<div class="mm-cta-row">)', part2, re.S)
    assert m, f"{slug}: closing CTA shape not as expected"
    out = (part2[:m.end(1)]
           + f'      <p class="mm-cta-close__lede">{lede}</p>\n'
           + m.group(2) + part2[m.start(3):])

    # count the ELEMENT, not the class name - the name also appears in the sheet
    tag = '<p class="mm-cta-close__lede">'
    assert out.count(tag) == 1, f"{slug}: byline not added exactly once"
    assert out.index(tag) < out.index('<div class="mm-cta-row">'), \
        f"{slug}: byline must sit above the buttons"
    assert out.count("<h2") == part2.count("<h2"), f"{slug}: heading count changed"
    return out


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
      text-align: center; padding: 20px; font-size: 15px; font-weight: 500; color: #8a8a8a;
      background: linear-gradient(135deg, var(--teal-pale, #e8f6f6) 0%, #f0ebe3 100%);
    }
    @media (max-width: 900px) {
      .mm-hero__grid { grid-template-columns: 1fr; gap: 40px; }
    }
"""

def trim_hero(part1, slug):
    """Shorten the hero to hook + positioning line; relocate the middle paragraph.

    Every page's hero runs three paragraphs: an emotional hook, a substantive
    paragraph carrying the only link to the matching service page, and a one-line
    positioning sentence. Three is too much copy beside an image, but the middle
    one is not disposable - deleting it would drop that internal link entirely, so
    it moves to the top of the first body section instead.
    """
    m = re.search(r'(<div class="mm-hero__intro">)(.*?)(</div>)', part1, re.S)
    assert m, f"{slug}: hero intro not found"
    paras = re.findall(r'<p>.*?</p>', m.group(2), re.S)
    assert len(paras) == 3, f"{slug}: expected 3 hero paragraphs, got {len(paras)}"
    keep, move = [paras[0], paras[2]], paras[1]
    assert "<a href=" in move, f"{slug}: middle paragraph has no link, re-check the choice"

    ind = "\n            "
    intro = m.group(1) + ind + ind.join(keep) + "\n          " + m.group(3)
    out = part1[:m.start()] + intro + part1[m.end():]

    body = re.search(r'<section class="mm-section mm-section--warm">\s*'
                     r'<div class="mm-section__inner">\s*<h2 class="mm-h2">.*?</h2>\s*'
                     r'<div class="mm-rt">\s*', out, re.S)
    assert body, f"{slug}: first body section not found"
    out = out[:body.end()] + move + "\n        " + out[body.end():]

    assert out.count(move) == 1, f"{slug}: relocated paragraph duplicated"
    left = re.search(r'<div class="mm-hero__intro">(.*?)</div>', out, re.S).group(1)
    assert len(re.findall(r'<p>.*?</p>', left, re.S)) == 2, f"{slug}: hero not left with two"
    return out


ALIGN_CSS = """    .mm-section__inner { max-width: 1200px; margin: 0 auto; }
"""


def align_widths(part1, slug):
    """Match every section's container to the hero's, in width as well as position.

    Before this the hero ran 1200 wide and body sections 900, centred - so the
    hero's text started ~160px left of every heading below it. A first attempt
    fixed the left edge but capped prose at 62ch, which aligned the columns
    without widening them and left the copy sitting in the left two-thirds of an
    empty container. There is now no measure cap: copy fills the 1200 container,
    matching the hero. Line length is long by typographic convention, which is the
    accepted trade for the sections reading as one width.
    """
    old = "    .mm-section__inner { max-width: 900px; margin: 0 auto; }\n"
    assert part1.count(old) == 1, f"{slug}: section inner rule not as expected"
    out = part1.replace(old, ALIGN_CSS, 1)
    # the hero intro carries its own 62ch cap in the source embeds; drop it so the
    # hero copy fills its column rather than stopping short inside it
    hero_cap = " max-width: 62ch;"
    assert out.count(hero_cap) == 1, f"{slug}: expected one hero measure cap"
    out = out.replace(hero_cap, "", 1)
    assert ".mm-section__inner { max-width: 1200px" in out
    assert "max-width: 62ch" not in out, f"{slug}: a measure cap survived"
    return out


PLACEHOLDER = """        <div class="mm-hero__media">
          <div class="mm-hero__placeholder">Hero image placeholder</div>
        </div>"""

# slug -> (Webflow asset url, alt text). A slug with no entry keeps the
# placeholder, so pages can take real images one state at a time. The urls must
# be Webflow-hosted: an image loaded from anywhere else is a third-party request
# on a healthcare page and outlives nobody's control but the host's.
HERO_IMG = {
    "early-intervention-north-carolina": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e39f714680f3b5abd614_early-intervention-north-carolina-hero.webp",
        "Mother sitting on the kitchen floor as her toddler stacks colorful nesting cups"),
    "parent-training-north-carolina": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e3a0156a4015be093e13_parent-training-north-carolina-hero.webp",
        "Mother helps her daughter zip her jacket in the hallway while a Behavior Technician looks on"),
    "behavior-support-north-carolina": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e3a087d56fcc1023613c_behavior-support-north-carolina-hero.webp",
        "Behavior Technician offers a boy two picture cards to choose between in his living room"),
    "transition-planning-north-carolina": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e3a0736b942eb8a7bb57_transition-planning-north-carolina-hero.webp",
        "Young adult loads the dishwasher while a parent reads at the kitchen table"),
    "parent-training-georgia": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78eedf6cbd4007454bb684_parent-training-georgia-hero.webp",
        "Father reads to his son on the porch at dusk while a Behavior Technician sits nearby"),
    "transition-planning-georgia": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78eedfc4ed60382a36306e_transition-planning-georgia-hero.webp",
        "Young adult loads the dishwasher while a parent reads at the kitchen table"),
    "early-intervention-georgia": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78ecd60e6cceed2985ac3b_early-intervention-georgia-hero.webp",
        "Mother reads an animal picture book with her toddler on the living room rug"),
    "behavior-support-georgia": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78ecd6bd634cf4b1f16b08_behavior-support-georgia-hero.webp",
        "Behavior Technician works with a boy at the kitchen table with picture cards on the fridge"),
    "early-intervention-new-jersey": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e6e6ada099bf0ebef310_early-intervention-new-jersey-hero.webp",
        "Mother smiles as her toddler works a wooden shape box at the kitchen table"),
    "parent-training-new-jersey": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e6e61af92c90aa0cfab6_parent-training-new-jersey-hero.webp",
        "Boy hands groceries to his mother while a Behavior Technician watches from the hallway"),
    "behavior-support-new-jersey": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e6e658560a803d64112e_behavior-support-new-jersey-hero.webp",
        "Behavior Technician kneels by the front door showing a boy two picture cards"),
    "transition-planning-new-jersey": (
        "https://cdn.prod.website-files.com/6627fd62e242d50407cfe12d/6a78e6e60955b2e9f1a6acec_transition-planning-new-jersey-hero.webp",
        "Teenager makes his own lunch at the counter while a parent reads nearby"),
}


def hero_media(slug):
    """The hero's right-hand column: a real image if we have one, else the box."""
    if slug not in HERO_IMG:
        return PLACEHOLDER
    src, alt = HERO_IMG[slug]
    assert src.startswith("https://cdn.prod.website-files.com/"), \
        f"{slug}: hero image must be a Webflow-hosted asset, got {src!r}"
    assert '"' not in src and '"' not in alt, f"{slug}: quote would break the attribute"
    # alt text is client-facing copy and clears the same gates as the rest
    assert 3 <= len(alt.split()) <= 20, f"{slug}: alt text length {len(alt.split())} words"
    for w in FORBIDDEN:
        assert w not in alt, f"{slug}: forbidden token {w!r} in alt text"
    # the 4/3 box is fixed by HERO_CSS; stating it stops the layout shifting while
    # the image loads. eager because the hero is above the fold on every page.
    return ('        <div class="mm-hero__media">\n'
            f'          <img src="{src}" alt="{alt}" width="1200" height="900"'
            ' loading="eager" decoding="async">\n'
            '        </div>')


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
            f"{hero_media(slug)}\n"
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
    assert out.count('class="mm-hero__media"') == 1
    # exactly one of the two, never both and never neither
    assert (out.count('class="mm-hero__placeholder"')
            + out.count("<img src=")) == 1, f"{slug}: hero media column is wrong"
    if slug in HERO_IMG:
        assert f'src="{HERO_IMG[slug][0]}"' in out, f"{slug}: hero image not applied"
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



TYPE_SCALE = {
    # The paragraph scale was drifting because of one global Webflow rule:
    #     p { font-size: 1.125rem }   (18px)
    # It targets the ELEMENT, so it beats any size inherited from a container -
    # but loses to a size set on a p that carries a class. The result was
    # accidental: .mm-rt declared 17 and rendered 18, .mm-hero__intro declared a
    # 20px lead and rendered 18, while .mm-cta-close__lede (a classed p) actually
    # got its 17. Four paragraph sizes on screen, none of them chosen.
    #
    # Fixed by sizing the paragraphs themselves and collapsing the scale to two:
    #     18px  body - hero lead, prose, accordion, closing byline, town lede
    #     15px  dense - table cells, buttons, town links
    # plus one label size, 13px, for the eyebrow and the town grid label.
    ".mm-hero__intro { font-size: clamp(16px, 1.5vw, 20px); line-height: 1.65; color: var(--soft, #5a5a5a); margin: 0 0 36px 0; }":
        ".mm-hero__intro { line-height: 1.65; color: var(--soft, #5a5a5a); margin: 0 0 36px 0; }",
    ".mm-hero__intro p { margin: 0 0 1.1em 0; }":
        ".mm-hero__intro p { font-size: 18px; margin: 0 0 1.1em 0; }",
    ".mm-rt { font-size: 17px; line-height: 1.7; color: var(--text, #2c2c2c); }":
        ".mm-rt { line-height: 1.7; color: var(--text, #2c2c2c); }",
    ".mm-rt p { margin: 0 0 1.1em 0; }":
        ".mm-rt p { font-size: 18px; margin: 0 0 1.1em 0; }",
}

# dead once the FAQ became an accordion: no payload contains an h3 any more
DEAD_RULES = [
    "    .mm-h3 { font-family: var(--font-body); font-weight: 600; font-size: 20px; line-height: 1.3; color: var(--navy, #1a2744); margin: 1.8em 0 0.4em 0; }\n",
    "    .mm-faq .mm-h3 { margin-top: 1.4em; }\n",
]


def unify_type(part1, slug):
    """Collapse the paragraph scale to one body size and one dense size."""
    out = part1
    for old, new in TYPE_SCALE.items():
        assert out.count(old) == 1, f"{slug}: type rule not found verbatim: {old[:50]}"
        out = out.replace(old, new, 1)
    for dead in DEAD_RULES:
        assert out.count(dead) == 1, f"{slug}: dead rule not found verbatim"
        out = out.replace(dead, "", 1)
    assert "<h3" not in out, f"{slug}: an h3 exists, so .mm-h3 is not dead after all"
    assert "font-size: 17px" not in out and "font-size: 20px" not in out, \
        f"{slug}: an off-scale paragraph size survived"
    return out

# H1 and eyebrow, decided from Semrush data (2026-08-07).
#
# The state+service phrases these pages are named after have NO measurable
# search volume: "behavior support north carolina", "parent training north
# carolina" and "aba behavior support north carolina" all return no data, and
# "transition planning north carolina" is 0. So no H1 wording wins traffic here.
# The qualifier is added for CLARITY - "Behavior Support in North Carolina" reads
# like school PBIS or mental health - not for volume.
#
# Word order follows how people actually search: "aba parent training" (880)
# beats "parent training aba" (590), so the qualifier leads.
#
# Deliberately NOT "ABA Therapy in {state}". That is the hub's exact target
# ("aba therapy north carolina", 480/mo) and the hub does not yet rank top-12 for
# it. Putting the full string in four sub-page H1s would spend relevance on
# zero-volume phrases while diluting the one that matters.
H1_SERVICE = {
    "early-intervention": "ABA Early Intervention",
    "parent-training": "ABA Parent Training",
    "behavior-support": "ABA Behavior Support",
    "transition-planning": "ABA Transition Planning",
}

# The eyebrow used to read "In-Home ABA in {state}", which after the H1 change
# repeated both the category and the state directly above itself. It now carries
# only what the H1 does not: the delivery model. Eyebrow says how, H1 says what
# and where, no overlap.
EYEBROW = "In-Home Therapy"


def headline(part1, slug):
    """Prefix the H1 with the ABA qualifier and de-duplicate the eyebrow."""
    service = next(k for k in H1_SERVICE if slug.startswith(k))
    state = slug[len(service) + 1:].replace("-", " ").title()
    old_h1 = f"<h1>{service.replace('-', ' ').title()} in {state}</h1>"
    new_h1 = f"<h1>{H1_SERVICE[service]} in {state}</h1>"
    assert part1.count(old_h1) == 1, f"{slug}: h1 not found verbatim: {old_h1}"
    out = part1.replace(old_h1, new_h1, 1)

    old_eb = f'<span class="mm-eyebrow">In-Home ABA in {state}</span>'
    assert out.count(old_eb) == 1, f"{slug}: eyebrow not found verbatim"
    out = out.replace(old_eb, f'<span class="mm-eyebrow">{EYEBROW}</span>', 1)

    for w in FORBIDDEN:
        assert w not in new_h1 and w not in EYEBROW, f"{slug}: forbidden token"
    assert out.count("<h1") == 1, f"{slug}: h1 count changed"
    assert out.count('class="mm-eyebrow"') == 1, f"{slug}: eyebrow count changed"
    # the eyebrow must no longer repeat the H1's terms
    assert "ABA" not in EYEBROW and state not in EYEBROW
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
    part1 = trim_hero(part1, slug)
    part1 = align_widths(part1, slug)
    part1 = unify_type(part1, slug)
    part1 = headline(part1, slug)

    # split the tail into the FAQ section and everything after it (the closing CTA),
    # rewrite the FAQ as an accordion, and prepend the accordion-only stylesheet
    cta_at = tail.index('  <section class="mm-section mm-cta-close">')
    faq, rest = tail[:cta_at], tail[cta_at:]
    faq = faq.replace('<section class="mm-section mm-section--warm mm-faq">',
                      '<section class="mm-section mm-faq">', 1)
    part2 = OPEN + "\n" + ACC_CSS + accordion(faq.rstrip(), slug) + "\n" + rest.lstrip("\n")
    part2 = cta_byline(part2, slug)

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
    service = next(k for k in CTA_LEDE if slug.startswith(k))
    state = slug[len(service) + 1:].replace("-", " ").title()
    # The H1 and eyebrow are deliberately rewritten, so `expect` gets the same
    # substitution - applied to the untouched source, not to the pipeline output,
    # so every other word still has to survive the split unchanged.
    # a real hero image adds no visible text; the placeholder box adds its label
    inserted = "" if slug in HERO_IMG else " Hero image placeholder"
    expect = (visible(headline(drop_inline_towns(markup, slug), slug))
              + inserted + " " + CTA_LEDE[service].format(state=state))
    got = visible(part1) + " " + visible(part2)
    assert sorted(got.split()) == sorted(expect.split()), f"{slug}: visible copy changed"
    # and the rewrite itself is asserted positively, not just "nothing else moved"
    assert f"<h1>{H1_SERVICE[service]} in {state}</h1>" in part1, f"{slug}: h1 not applied"
    assert f'<span class="mm-eyebrow">{EYEBROW}</span>' in part1, f"{slug}: eyebrow not applied"
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
