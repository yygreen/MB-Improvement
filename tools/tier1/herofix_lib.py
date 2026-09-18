#!/usr/bin/env python3
"""Shared helpers for the hero fix generators.

The specificity gate here exists because of a bug it would have caught. The
first /services payload promoted the headline to `<h1 class="hero-headline">`
and converged `.mm-embed .hero-headline` to the canonical fluid spec - and would
have changed nothing on screen, because the page also carries

    .mm-embed .hero h1 { font-size: 40px; line-height: 1.18; font-weight: 700; }

which is (0,2,1) against the canonical rule's (0,2,0) and therefore wins the
moment the headline becomes an h1. The rule was invisible before the swap: the
old h1 was the eyebrow, and `.hero h1.hero-eyebrow` (0,3,1) outranked it there.

Promoting an element into a new tag silently changes which rules apply to it, so
every generator that does this asserts afterwards that the rule it intends to win
actually wins.
"""
import re
import sys
import urllib.request

UA = {"User-Agent": "mb-herofix/1"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def extract_embed(html, cls):
    """Inner HTML of the div carrying `cls`, found by brace-matching divs."""
    start = html.index(f'<div class="{cls} w-embed"')
    i = html.index(">", start) + 1
    depth = 1
    for m in re.finditer(r"</?div\b", html[i:]):
        depth += -1 if html[i + m.start():i + m.start() + 5] == "</div" else 1
        if depth == 0:
            return html[i:i + m.start()]
    sys.exit(f"unbalanced divs inside .{cls}")


def specificity(selector):
    """(ids, classes, elements) for a simple selector.

    An approximation, and deliberately so: these sheets are hand-written, flat
    and scoped under .mm-embed, with no :is()/:where()/:not() whose arguments
    would change the count. It is exact for everything in them.
    """
    s = re.sub(r"::[a-z-]+", " ", selector)          # pseudo-elements -> elements
    pseudo_el = len(re.findall(r"::[a-z-]+", selector))
    ids = len(re.findall(r"#[\w-]+", s))
    classes = len(re.findall(r"[.:\[][\w-]+", s))    # .class, :hover, [attr]
    elements = len(re.findall(r"(?:^|[\s>+~])([a-z][\w-]*)", s))
    return (ids, classes, elements + pseudo_el)


def css_of(embed):
    """The CSS of an embed payload: the style block, comments stripped."""
    css = embed[embed.index(">", embed.index("<style")) + 1:embed.index("</style>")]
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def selectors_matching(css, tag, classes, ancestor_classes):
    """Selectors in `css` that could match <tag class=...> under the given ancestors.

    Conservative in the safe direction: combinators are relaxed to descendant,
    so the result can over-report (a rule that would not really match) but never
    under-report. A gate that misses a match is useless; one that flags an extra
    is merely annoying, and the caller sees which selector it was.
    """
    out, unparsed = [], []
    for m in re.finditer(r"(?:^|[{}])\s*([^{}@/][^{}]*?)\s*\{", css, re.M):
        for sel in m.group(1).split(","):
            sel = sel.strip()
            if not sel or sel.startswith("@"):
                continue
            if "\n" in sel or "<" in sel:
                unparsed.append(sel)
                continue
            parts = [p for p in re.sub(r"\s*[>+~]\s*", " ", sel).split() if p]
            key = re.sub(r"::[a-z-]+$", "", parts[-1])
            key_tag = re.match(r"^([a-z][\w-]*)", key)
            key_classes = set(re.findall(r"\.([\w-]+)", key))
            if key_tag and key_tag.group(1) != tag:
                continue
            if not key_classes <= set(classes):
                continue
            # every ancestor part must be satisfiable by the ancestor classes
            ok = True
            for p in parts[:-1]:
                pc = set(re.findall(r"\.([\w-]+)", p))
                if re.match(r"^[a-z]", p) or not pc <= set(ancestor_classes):
                    ok = False
                    break
            if ok:
                out.append(sel)
    return out, unparsed


def assert_rule_wins(embed, winner, tag, classes, ancestor_classes):
    """Fail unless `winner` is the last-declared highest-specificity match.

    Ties go to whichever is declared later, so this checks source order too.
    """
    css = css_of(embed)
    matches, unparsed = selectors_matching(css, tag, classes, ancestor_classes)
    assert winner in matches, f"{winner!r} does not itself match the element"
    assert not unparsed, f"selectors this gate cannot reason about: {unparsed}"
    win_spec = specificity(winner)
    win_pos = css.rindex(winner)
    for sel in matches:
        if sel == winner:
            continue
        spec = specificity(sel)
        if spec > win_spec or (spec == win_spec and css.rindex(sel) > win_pos):
            sys.exit(
                f"specificity gate failed: {sel!r} {spec} beats {winner!r} "
                f"{win_spec} for <{tag} class=\"{' '.join(classes)}\">.\n"
                "The promoted element would keep rendering the old style. "
                "Remove or converge that rule too.")
