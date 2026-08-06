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

The repo copy `tools/css-consolidation/service-pages.shared.css` was STALE - it
still carried the pre-convergence `48px / 1.15 / 800`. Re-synced from live with
the new `tools/tier1/sync-shared-from-live.py` (46 lines changed; the mirror had
missed the whole 2026-08-04 convergence). Run that script after any Designer edit
to the shared component.

That re-sync exposed a second, worse problem - see "The rebase would revert it".

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

PAYLOAD GENERATED: `tools/tier1/gen-hero-fix-early-intervention.py` scrapes the
live embed (its code renders verbatim, so the page is a faithful copy of the
payload - nothing is retyped), applies exactly those two edits plus a rewrite of
the block comment, and gates both input and output: one h1, scope wrapper intact,
exactly two rules removed and all of them `.hero h1`, and the markup byte-identical
apart from the single added class. Output at
`content/tier1/build/herofix/early-intervention.embed.{orig,fixed}.html`
(5,054 -> 4,960 bytes, 17 -> 15 scoped rules).

The comment rewrite matters as much as the CSS: the old one asserted "the headline
is 800 to match the reference page", which is why the rule survived the
convergence. The replacement states that the headline deliberately carries no
local rule and that the removed pair must not be reinstated.

### 2. /services - h1 and eyebrow are semantically inverted

    <h1 class="hero-eyebrow">Mastermind Behavior Services</h1>   13px teal
    <p  class="hero-headline">Helping Your Child Build Real Skills...</p>  40px

The page's h1 is the 13px kicker; the real headline is a paragraph. This is the
same defect the earlier commit "Promote the real headline to h1 on five service
pages" fixed - /services was missed by that pass.

**/services does not load the shared "Service Page Styles" component at all.**
Every other service page does; /services carries its own standalone copy of an
older sheet. This was found while generating the payload and it inverts the fix:
on /early-intervention the repair is to DELETE the local hero rules so the shared
canonical rule takes over, but doing that here would leave `.hero-headline` with
no rule at all and drop the headline onto Webflow's default h1 styling. The fix
therefore CONVERGES VALUES - keeps /services' own selectors, replaces their
declaration bodies with the canonical ones read from a page that does load the
shared sheet.

It also explains the 32px. The mechanism is not "container adds padding" - the
shared `.container { padding: 0 32px }` gutter applies everywhere. It is that the
shared sheet ALSO carries `.mm-embed .hero .container { padding: 0 }` to cancel
that gutter inside the hero (its comment says "do not tidy that away"), and
/services never received it, because it never received the sheet. Hence x=152
against everyone else's x=120.

Third contributor: `.mm-embed .hero-headline` is pinned locally at 40px / 1.18 /
700 with `!important` on every property. Without removing that, the markup swap
alone changes nothing visible. The `!important` reads as defensive hardening
against the Webflow host stylesheet - a real pattern on this site - but it was
hardening a PARAGRAPH; `.mm-embed .hero-headline` (0,2,0) already beats a bare
`h1` host rule, and all five sibling pages prove it by rendering the canonical
rule with no `!important` at all.

Fourth contributor, and the one that nearly shipped a no-op: the page ALSO has

    .mm-embed .hero h1 { font-size: 40px; line-height: 1.18; font-weight: 700; }
    @media (max-width: 768px) { .mm-embed .hero h1 { font-size: 34px; } }

That pair is invisible today - the h1 is the eyebrow, and `.hero h1.hero-eyebrow`
(0,3,1) outranks it there - but it becomes the winning rule the instant the
headline is promoted to an h1, because (0,2,1) beats the canonical
`.mm-embed .hero-headline` (0,2,0). The first version of this payload converged
the headline correctly and would have rendered exactly the same 40px/700 page.
Found by the specificity gate described below, not by reading the diff.

FIX (six edits): promote `<p class="hero-headline">` to `<h1>`, demote
`<h1 class="hero-eyebrow">` to `<div>`, converge the headline declarations to the
canonical fluid clamp, converge the eyebrow declarations (letter-spacing 1.5px ->
0.08em, margin-bottom 20px -> 28px, which is the eyebrow gap drift), drop the
`font-size: 34px !important` mobile override, delete the bare-h1 pair, and add
`padding: 0` to `.mm-embed .hero .container`.

PAYLOAD GENERATED: `tools/tier1/gen-hero-fix-services.py`, same scrape-and-gate
approach, with `/parent-training` as the canonical donor so the converged values
are read rather than retyped. It gates that the donor still carries the shared
sheet, that /services still does NOT (if that ever changes, deletion becomes the
right fix and this tool is the wrong one), and that each converged class appears
exactly once in the markup so replacing a declaration body cannot restyle
anything else. Output at
`content/tier1/build/herofix/services.embed.{orig,fixed}.html`
(21,927 -> 21,882 bytes; diff is exactly the five edits, nothing else).

NEEDS A LOOK BEFORE PRODUCTION: unlike fix 1 this changes the rendered headline
size, 40px -> fluid up to 52px. Stage and screenshot.

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

## The rebase would revert it

Re-syncing the mirror surfaced a live regression risk that has nothing to do with
Webflow access. `tools/css-consolidation/rebase-shared.mjs` rebases the shared
sheet onto `in-home-aba-therapy.merged.css`, and that reference is a SNAPSHOT
taken before the convergence: it still holds 48px / 1.15 / 800, `h1.hero-eyebrow`,
and the 768px `font-size: 36px` override. Running `node rebase-shared.mjs --apply`
today would have put every one of them back.

The script's own EXCEPTIONS map exists to stop exactly this ("a fix that a tool
quietly undoes is worse than no fix"), but the convergence cannot be expressed in
it: EXCEPTIONS overrides properties on selectors the walk already visits, while
the convergence RENAMES a selector (`.hero h1.hero-eyebrow` -> `.hero
.hero-eyebrow`), ADDS rules the reference has no opinion on (`.hero .container {
padding: 0 }`, a 900px breakpoint) and DELETES one.

So the script now refuses to run when the mirror is converged and the reference
is not, exiting 2 with an explanation rather than corrupting the mirror. Verified:
it fires today. The real repair is to re-snapshot the reference from live; the
guard is there so nobody rebases before that happens.

## The specificity gate

`tools/tier1/herofix_lib.py` - `assert_rule_wins()`. After a generator promotes
an element into a new tag, it asserts that the rule it INTENDS to win actually
wins: it collects every selector in the cascade that could match the new element,
computes specificity, and fails if any outranks the intended one (or ties it and
is declared later).

This exists because promoting an element changes which rules apply to it, and the
newly-applicable rule can be one that was dormant and therefore invisible in
review. Both payloads pass it now; both were negative-tested by reinstating the
removed rules and confirming the gate rejects them:

    specificity gate failed: '.mm-embed .hero h1' (0, 2, 1) beats
    '.mm-embed .hero-headline' (0, 2, 0) for <h1 class="hero-headline">.

For /early-intervention the check runs against the real cascade - shared sheet
first, then the page embed - because the winning rule lives in the shared sheet
and the losing rules in the page. For /services it runs on the embed alone, since
that page loads no shared sheet.

The selector matcher relaxes `>`/`+`/`~` to descendant, so it can over-report a
match but never miss one; a gate that misses is useless, one that over-reports is
merely noisy and names the selector.

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

Done and in the repo, needing no Webflow access:
  - both fix payloads generated and gated (see the two sections above)
  - the mirror re-synced from live
  - the rebase guard, so the convergence cannot be silently reverted

STILL BLOCKED on applying fixes 1 and 2 to the site: the Webflow MCP connection
re-authorised mid-session to a different workspace and still lists only "Chesed
24/7" and "Kosher Mezuzah". Site 6627fd62e242d50407cfe12d returns 404 "The site
cannot be found" for every call. Nothing has been written to Webflow.

When access is restored, the apply is mechanical:
  1. set the `code` setting of embed `code-embed-6` on /early-intervention to
     `content/tier1/build/herofix/early-intervention.embed.fixed.html`
  2. set the `code` setting of embed `code-embed-3` on /services to
     `content/tier1/build/herofix/services.embed.fixed.html`
  3. publish to STAGING ONLY (`publishToWebflowSubdomain: true, customDomains: []`)
  4. re-run both generators against staging - each re-reads the live page, so a
     clean second run is the byte-identity check that the payload landed intact
  5. `PLAYWRIGHT_DIR=<dir> python3 tools/tier1/hero-type-lint.py` - expect 0
     findings in the gated families, and /services to drop from 5 differences to
     roughly 1 (its hero is centre-aligned by design, so it will not reach 0)
  6. screenshot /services: it is the one with a visible size change
