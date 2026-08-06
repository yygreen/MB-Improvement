# Hero drift audit and fix spec (2026-08-05)

Raised by the user: "/aba-therapy-in-new-jersey, /bcba-team, /services etc still
drift away in width, eyebrow position etc. orientate yourself on
/aba-therapy-in-new-jersey", then "also with the h1 boldness? checked?".

Measured with `tools/tier1/hero-type-lint.py` (new; renders each page in
Chromium at 1440px and diffs computed hero type against the reference).

## The reference: /aba-therapy-in-new-jersey

    section.mm-hero            padding-left 48px
      div.mm-hero__inner       max-width 1200  -> content starts at x=120
        div.mm-hero__text      582px text column
          span.mm-eyebrow      13px UPPERCASE, letter-spacing 1.04px, 28px above h1
          h1                   52px / 56 / weight 600 / #1a2744

The canonical rule is in the "Service Page Styles" component and is fluid:

    .mm-embed .hero-headline { font-family: var(--font-display);
      font-size: clamp(32px, 5vw, 52px); line-height: 1.08; font-weight: 600;
      color: var(--navy); margin-bottom: 28px; letter-spacing: -0.015em; }

NOTE the repo copy `tools/css-consolidation/service-pages.shared.css` is STALE:
it still carries the pre-convergence `48px / 1.15 / 800`. Live Webflow is the
source of truth here; re-sync that file.

## Findings

Gated families (should match the reference exactly):

| page | status |
| --- | --- |
| aba-therapy-in-{new-jersey,georgia,north-carolina} | ok |
| in-home-aba-therapy, parent-training, behavior-support, skill-development, transition-planning | ok |
| insurance-terminology, financial-aid-resources | ok |
| **early-intervention** | **FAIL: h1 48px (want 52), weight 800 (want 600)** |

Other hero systems, informational until a convergence decision is taken:
bcba-team 1 diff, services 5, about-us 9, areas-we-serve 9, contact 6.

### 1. /early-intervention - the only stray inside the reference family

Cause: its headline is a BARE `<h1>` with no class. Its five siblings use
`<h1 class="hero-headline">`, so the canonical fluid rule never matches on this
page and it falls through to a legacy page override:

    .mm-embed .hero h1 { font-family: var(--font-display); font-size: 48px;
      line-height: 1.15; font-weight: 800; color: var(--navy);
      margin-bottom: 24px; letter-spacing: -0.5px; }
    @media (max-width: 768px) { .mm-embed .hero h1 { font-size: 36px; } }

banked at `tools/css-consolidation/override.early-intervention.css` lines 3-6.

That override carries a comment claiming "The headline is 800 to match the
reference page, not the 700 this clone froze." That was true BEFORE the hero
convergence; the reference is now 600. The comment is stale and the rule is now
the thing causing the drift.

FIX (two edits, no visual redesign):
  1. hero embed markup: `<h1>` -> `<h1 class="hero-headline">`
  2. page override CSS: delete both `.mm-embed .hero h1` rules (lines 3-6);
     they become dead once the class is present, and leaving them risks the
     bare-h1 selector winning again later.
Result: the page inherits the canonical fluid spec and cannot drift back.

### 2. /services - h1 and eyebrow are semantically inverted

    <h1 class="hero-eyebrow">Mastermind Behavior Services</h1>   13px teal
    <p  class="hero-headline">Helping Your Child Build Real Skills...</p>  40px

The page's h1 is the 13px kicker; the real headline is a paragraph. This is the
same defect the earlier commit "Promote the real headline to h1 on five service
pages" fixed - /services was missed by that pass.

Also: its `div.container` adds `padding-left: 32px` ON TOP of the 1200px
centering, so all hero content starts at x=152 instead of x=120. That is the
32px width/position drift visible against every other page.

FIX: move the h1 onto the headline (`<h1 class="hero-headline">`), demote the
eyebrow to `<div class="hero-eyebrow">`, and drop the extra container padding.

### 3. bcba-team / about-us / areas-we-serve / contact - a separate decision

- bcba-team: native Designer elements (NOT an embed), third naming scheme
  (`mm-hero-inner`, `mm-hero-h1` - dashes, not the reference's BEM `mm-hero__`).
  No text column, so the h1 runs 760px instead of 582. Eyebrow sits at x=158,
  38px right of its own h1 at x=120 - the eyebrow misalignment reported.
- about-us + areas-we-serve: h1 56/67 weight 700 in PURE BLACK #000 (not the
  brand navy #1a2744), starting at x=80, container 624.
- contact: h1 64/70 weight 700, black, x=128, no eyebrow.

Converging these means rebuilding four client-approved heroes, and bcba-team
needs Designer style edits rather than an embed rewrite. Not attempted; awaiting
a decision.

## Tooling added

`tools/tier1/hero-type-lint.py` - renders and diffs computed hero type
(size, line-height, weight, colour, h1 left edge; eyebrow size, transform,
left edge, gap) against the reference. The existing
`tools/css-consolidation/drift/hero-lint.py` greps source and therefore CANNOT
see any of this - a page can have perfect markup and still render 800 weight.
The two are complementary; run both.

    PLAYWRIGHT_DIR=<dir with playwright installed> \
      python3 tools/tier1/hero-type-lint.py --prod

Exit 1 on any finding in the gated families; other systems print as info.

## Status

BLOCKED on applying fixes 1 and 2: mid-session the Webflow MCP connection
re-authorised to a different workspace and now lists only "Chesed 24/7" and
"Kosher Mezuzah". Site 6627fd62e242d50407cfe12d returns 404 "The site cannot be
found" for every call. Nothing was written. Re-point the Webflow connection at
the Mastermind workspace and the two fixes are a handful of calls.
