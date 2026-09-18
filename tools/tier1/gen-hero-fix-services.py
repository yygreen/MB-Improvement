#!/usr/bin/env python3
"""Generate the fixed hero embed payload for /services.

WHY: /services is the last page still carrying the pre-convergence hero defect
that the commit "Promote the real headline to h1 on five service pages" fixed
everywhere else. Live markup:

    <h1 class="hero-eyebrow">Mastermind Behavior Services</h1>      13px teal
    <p  class="hero-headline">Helping Your Child Build Real Skills...</p>  40px

so the page's only h1 is the 13px kicker and the real headline is a paragraph.

THE TRAP THAT SHAPES THIS SCRIPT
--------------------------------
/services does NOT load the shared "Service Page Styles" component. Every other
service page does; /services carries its own standalone copy of an older sheet.
Verified per run by the gates below.

That inverts the obvious fix. On /early-intervention the repair is to DELETE the
page's local hero rules so the shared canonical rule takes over. Doing the same
here would leave `.hero-headline` with no rule at all and drop the headline onto
Webflow's default h1 styling. So this script CONVERGES VALUES instead: it keeps
/services' own selectors and replaces their declaration bodies with the canonical
ones, read at run time from a page that does load the shared sheet. Nothing is
retyped, so the two can't drift apart through a transcription slip.

The edits:

 1. MARKUP - swap the semantics. Eyebrow becomes a div, headline becomes the h1.
    Safe because /services styles `.hero-eyebrow` element-agnostically, so the
    eyebrow keeps its styling once it stops being an h1.

 2. CSS - headline declarations -> canonical (fluid clamp, 1.08, weight 600).
    The live rule pins 40px / 1.18 / 700 with `!important` on every property,
    which is what actually holds the headline off the canonical spec; without
    this, edit 1 alone changes nothing visible. The `!important` is dropped: it
    reads as defensive hardening against the Webflow host stylesheet, but it was
    hardening a PARAGRAPH, and `.mm-embed .hero-headline` (0,2,0) already beats
    any bare `h1` host rule. All five sibling pages render the canonical rule
    with no `!important` at all.

 3. CSS - drop the `font-size: 34px !important` mobile override. clamp() governs
    below 768px; the shared sheet's own comment says not to reinstate it.

 4. CSS - eyebrow declarations -> canonical. This is the eyebrow drift: /services
    sits at letter-spacing 1.5px / margin-bottom 20px against the reference's
    0.08em / 28px, so its gap to the headline is 8px short.

 5. CSS - add `padding: 0` to `.mm-embed .hero .container`. This is the 32px
    width drift. The shared sheet carries exactly this reset (cancelling the
    `.container { padding: 0 32px }` gutter inside the hero so content starts at
    x=120) and comments "do not tidy that away" - but /services never got it,
    because it never got the shared sheet. Its hero content starts at x=152.

    python3 tools/tier1/gen-hero-fix-services.py

Writes content/tier1/build/herofix/services.embed.{orig,fixed}.html
Apply the .fixed file as the `code` setting of embed "code-embed-3" on /services,
publish to STAGING ONLY, then re-run hero-type-lint.py and screenshot: this one
changes the rendered headline size (40px -> fluid, up to 52px) and so needs an
explicit look before it goes anywhere near production.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from herofix_lib import assert_rule_wins, extract_embed, fetch  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "content/tier1/build/herofix"
PAGE = "https://www.mastermindbehavior.com/services"
EMBED_CLASS = "code-embed-3"
# a page that DOES load the shared sheet, used as the canonical donor
DONOR = "https://www.mastermindbehavior.com/parent-training"
SHARED_MARK = ".mm-embed .hero-headline { font-family: var(--font-display); font-size: clamp("

EYEBROW = "Mastermind Behavior Services"
CONTAINER_OLD = ".mm-embed .hero .container { position: relative; max-width: var(--max-width); }"
CONTAINER_NEW = ".mm-embed .hero .container { position: relative; max-width: var(--max-width); padding: 0; }"

# selector -> the donor selector whose declarations are canonical for it
CONVERGE = {
    ".mm-embed .hero-headline": ".mm-embed .hero-headline",
    ".mm-embed .hero-eyebrow": ".mm-embed .hero .hero-eyebrow",
}
# the mobile headline override, inside a max-width media query
MOBILE_HEADLINE = re.compile(r"\n?[ \t]*\.mm-embed \.hero-headline \{ font-size: 34px[^}]*\}")
# The pair of bare-h1 rules. Invisible today (the h1 is the eyebrow, and
# `.hero h1.hero-eyebrow` outranks them there) but they become the winning rule
# the instant the headline is promoted to an h1: (0,2,1) beats the canonical
# `.mm-embed .hero-headline` (0,2,0). Without removing them the whole fix is a
# no-op on screen. Caught by assert_rule_wins, not by eye.
BARE_H1 = re.compile(r"\n?[ \t]*\.mm-embed \.hero h1 \{[^}]*\}")


def rule_body(css, selector):
    """The declaration body of `selector`, matched exactly (not as a prefix)."""
    m = re.search(re.escape(selector) + r" \{([^}]*)\}", css)
    assert m, f"selector not found: {selector}"
    return m.group(1)


def main():
    html = fetch(PAGE)
    orig = extract_embed(html, EMBED_CLASS)
    donor = fetch(DONOR)

    # --- gates on the DONOR: it must really be the shared canonical sheet
    assert SHARED_MARK in donor, "donor page no longer carries the shared sheet"

    # --- gates on the INPUT
    assert orig.count("<h1") == 1, "expected exactly one h1 in the hero embed"
    assert f'<h1 class="hero-eyebrow">{EYEBROW}</h1>' in orig, "eyebrow h1 not found"
    assert orig.count('<p class="hero-headline">') == 1, "headline paragraph not found"
    assert 'class="mm-embed"' in orig, "embed lost its .mm-embed scope wrapper"
    assert orig.count(CONTAINER_OLD) == 1, "hero container rule not as expected"
    assert ".mm-embed .hero-eyebrow {" in orig, "no element-agnostic eyebrow rule"
    assert len(MOBILE_HEADLINE.findall(orig)) == 1, "mobile headline override not found"
    assert len(BARE_H1.findall(orig)) == 2, "expected 2 bare-h1 rules"
    # THE point of this script: /services must still be the odd page out. If it
    # ever starts loading the shared sheet, deleting rules becomes correct and
    # this value-convergence approach is the wrong tool.
    assert SHARED_MARK not in html, \
        "/services now loads the shared sheet - re-think this fix, do not force it"
    # each converged class must appear exactly once in the markup, so replacing
    # a declaration body cannot silently restyle something else on the page
    for cls in ("hero-eyebrow", "hero-headline"):
        assert orig.count(f'class="{cls}"') == 1, f"{cls} used more than once"

    headline = re.search(r'<p class="hero-headline">(.*?)</p>', orig, re.S).group(1)
    assert "<" not in headline, "headline contains markup - swap needs review"

    # 1. markup swap
    fixed = orig.replace(f'<h1 class="hero-eyebrow">{EYEBROW}</h1>',
                         f'<div class="hero-eyebrow">{EYEBROW}</div>', 1)
    fixed = fixed.replace(f'<p class="hero-headline">{headline}</p>',
                          f'<h1 class="hero-headline">{headline}</h1>', 1)
    # 2+4. converge declaration bodies onto the canonical ones
    for local, canon in CONVERGE.items():
        want = rule_body(donor, canon)
        have = rule_body(fixed, local)
        assert "!important" not in want, f"canonical {canon} unexpectedly has !important"
        fixed = fixed.replace(f"{local} {{{have}}}", f"{local} {{{want}}}", 1)
    # 3. mobile override, and the bare-h1 pair that would otherwise win
    fixed = MOBILE_HEADLINE.sub("", fixed)
    fixed = BARE_H1.sub("", fixed)
    # 5. container gutter reset
    fixed = fixed.replace(CONTAINER_OLD, CONTAINER_NEW, 1)

    # --- gates on the OUTPUT
    assert fixed.count("<h1") == 1, "must still have exactly one h1"
    assert f'<h1 class="hero-headline">{headline}</h1>' in fixed, "headline not promoted"
    assert f'<div class="hero-eyebrow">{EYEBROW}</div>' in fixed, "eyebrow not demoted"
    assert not MOBILE_HEADLINE.findall(fixed), "mobile override survived"
    assert fixed.count(CONTAINER_NEW) == 1, "container padding reset not applied"
    for local, canon in CONVERGE.items():
        assert rule_body(fixed, local) == rule_body(donor, canon), f"{local} not converged"
    assert "font-size: clamp(32px, 5vw, 52px)" in fixed, "headline is not fluid"
    # scoped to font-size: .pillar-cta legitimately has `padding: 18px 40px !important`
    assert "font-size: 40px !important" not in fixed, "old pinned size survived"
    assert fixed.count("<style>") == orig.count("<style>") == 1
    assert fixed.count("</style>") == 1
    assert fixed.count("<section") == orig.count("<section"), "sections changed"
    assert fixed.count("{") == fixed.count("}"), "unbalanced braces in the CSS"

    assert not BARE_H1.findall(fixed), "bare-h1 rules survived"

    def selectors(css):
        return {m.group(1).strip() for m in re.finditer(r"(\.mm-embed [^{]+)\{", css)}
    lost = selectors(orig) - selectors(fixed)
    # the bare-h1 selector is meant to go; nothing else may
    assert lost <= {".mm-embed .hero h1"}, f"selectors disappeared: {lost}"

    # THE gate: after promoting the paragraph to an h1, the canonical rule must
    # actually be the one that wins on the new element. Everything above can be
    # correct and the page still render unchanged if some other selector outranks
    # it - which is exactly what the bare-h1 pair did.
    assert_rule_wins(fixed, ".mm-embed .hero-headline", tag="h1",
                     classes=["hero-headline"],
                     ancestor_classes=["mm-embed", "hero", "container",
                                       "hero-grid", "hero-copy"])

    # copy that is not part of the swap must be untouched, character for character
    strip = lambda s: re.sub(r"<[^>]+>", "", s[s.index("</style>"):])
    assert strip(fixed) == strip(orig), "visible copy changed - not a pure swap"

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "services.embed.orig.html").write_text(orig)
    (OUT / "services.embed.fixed.html").write_text(fixed)
    print(f"orig  {len(orig):7,} bytes")
    print(f"fixed {len(fixed):7,} bytes")
    print(f"headline promoted to h1: {headline[:58]}...")
    print("converged: " + ", ".join(CONVERGE))
    print(f"\nwritten to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
