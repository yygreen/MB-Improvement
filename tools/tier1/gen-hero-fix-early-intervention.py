#!/usr/bin/env python3
"""Generate the fixed hero embed payload for /early-intervention.

WHY: hero-type-lint reports /early-intervention as the only stray inside the
reference family - h1 renders 48px/800 where the reference renders 52px/600.
Cause (see content/tier1/build/BUILD-RECORD-HERO-DRIFT.md): its headline is a
BARE <h1>, so the canonical fluid rule

    .mm-embed .hero-headline { font-size: clamp(32px, 5vw, 52px);
      line-height: 1.08; font-weight: 600; ... }

never matches, and a legacy page override on `.mm-embed .hero h1` wins instead.

Two edits, no visual redesign:
  1. <h1> -> <h1 class="hero-headline">
  2. delete both `.mm-embed .hero h1` rules (they go dead once the class is
     present, and leaving them risks the bare-h1 selector winning again later)
  3. rewrite the block comment, which documents the OLD structure and still
     claims "the headline is 800 to match the reference page" - true before the
     hero convergence, false now and the reason nobody caught this.

The input is scraped from the LIVE page rather than retyped: the embed's code
renders verbatim, so the rendered page is a faithful copy of the payload. The
program rule is never to hand-retype a payload - generate it, gate it with
assertions, then verify byte-identity against the rendered page afterwards.

    python3 tools/tier1/gen-hero-fix-early-intervention.py

Writes content/tier1/build/herofix/early-intervention.embed.{orig,fixed}.html
Apply the .fixed file as the `code` setting of embed "code-embed-6" on the
/early-intervention page, publish to STAGING ONLY, then re-run
`hero-type-lint.py` and expect the service family to come back clean.
"""
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "content/tier1/build/herofix"
PAGE = "https://www.mastermindbehavior.com/early-intervention"
EMBED_CLASS = "code-embed-6"

OLD_COMMENT_MARK = "The headline is 800 to match the reference page"
NEW_COMMENT = """/* Page-specific overrides for /early-intervention.
   Shared rules live in the "Service Page Styles" component - do not duplicate
   them here, an override loads later and silently wins.
   The hero headline deliberately carries NO rule here. It uses the canonical
   .hero-headline rule from the shared component (fluid clamp, weight 600) so it
   cannot drift from the reference page again. The pair of bare-h1 rules that
   used to sit here forced 48px at weight 800 and were the drift; they are gone
   on purpose, do not reinstate them.
   The eyebrow is a div on this page where the other five use an h1, so it still
   needs its own rules below.
   (Angle brackets are deliberately avoided in this comment - a literal tag
   inside a style block is valid CSS but trips naive markup parsers.) */"""

H1_RULE = re.compile(
    r"\n?[ \t]*\.mm-embed \.hero h1 \{[^}]*\}"          # the base rule
    r"|\n?@media \(max-width: 768px\) \{\n"             # and its mobile wrapper,
    r"[ \t]*\.mm-embed \.hero h1 \{[^}]*\}\n\}"         # whose only rule it is
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mb-herofix/1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def extract_embed(html, cls):
    """Return the inner HTML of the div carrying `cls`, by brace-matching divs."""
    start = html.index(f'<div class="{cls} w-embed"')
    i = html.index(">", start) + 1
    depth = 1
    for m in re.finditer(r"</?div\b", html[i:]):
        depth += -1 if html[i + m.start():i + m.start() + 5] == "</div" else 1
        if depth == 0:
            return html[i:i + m.start()]
    sys.exit(f"unbalanced divs inside .{cls}")


def main():
    html = fetch(PAGE)
    orig = extract_embed(html, EMBED_CLASS)

    # --- gates on the INPUT: fail loudly if the live page is not what we expect
    assert orig.count("<h1") == 1, "expected exactly one h1 in the hero embed"
    assert "<h1>" in orig, "h1 already carries a class - has the fix landed?"
    assert 'class="mm-embed"' in orig, "embed lost its .mm-embed scope wrapper"
    assert orig.count(".mm-embed .hero h1") == 2, "expected exactly 2 stray rules"
    assert OLD_COMMENT_MARK in orig, "stale comment not found - embed changed"

    fixed = orig.replace("<h1>", '<h1 class="hero-headline">', 1)
    fixed = H1_RULE.sub("", fixed)
    # splice the comment in place - keep the <style> tag that precedes it
    start, end = fixed.index("/*"), fixed.index("*/") + 2
    fixed = fixed[:start] + NEW_COMMENT + fixed[end:]

    # --- gates on the OUTPUT. Check the CSS with comments stripped: the block
    # comment legitimately discusses the rules being removed, and gating on the
    # raw text would make an accurate comment look like a failed removal.
    live_css = re.sub(r"/\*.*?\*/", "", fixed, flags=re.S)
    assert fixed.count('<h1 class="hero-headline">') == 1, "h1 not promoted"
    assert ".mm-embed .hero h1" not in live_css, "stray rules survived"
    assert "font-weight: 800" not in live_css, "800 weight still present"
    assert OLD_COMMENT_MARK not in fixed, "stale comment survived"
    assert fixed.count("<style>") == orig.count("<style>") == 1
    assert fixed.count("</style>") == 1 and fixed.count("</section>") == 1
    assert "@media" in fixed, "removal ate the surviving media queries"
    # every non-hero rule must survive untouched
    def rules(css):
        return {r.strip() for r in re.findall(r"\.mm-embed [^{]+\{[^}]*\}", css)}
    lost = rules(orig) - rules(fixed)
    assert all(".hero h1" in r for r in lost), f"unexpected rules removed: {lost}"
    # the markup must be identical apart from the one h1 class
    assert (fixed[fixed.index("</style>"):]
            == orig[orig.index("</style>"):].replace(
                "<h1>", '<h1 class="hero-headline">', 1)), "markup changed elsewhere"

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "early-intervention.embed.orig.html").write_text(orig)
    (OUT / "early-intervention.embed.fixed.html").write_text(fixed)
    print(f"orig  {len(orig):6,} bytes  ({len(rules(orig))} scoped rules)")
    print(f"fixed {len(fixed):6,} bytes  ({len(rules(fixed))} scoped rules)")
    print(f"removed: {len(lost)} rule(s), all .hero h1")
    print(f"\nwritten to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
