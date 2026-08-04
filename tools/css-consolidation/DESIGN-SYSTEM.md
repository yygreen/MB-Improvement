# MasterMindBehavior — dominant stylesheet

Handoff reference for the design system as it stands on staging. Every value here
was read from the live published CSS, not from memory or from a source file that
might have drifted.

Site `6627fd62e242d50407cfe12d`. **Staging only** — publish with
`publishToWebflowSubdomain: true, customDomains: []`. Production still carries the
pre-convergence CSS; publishing to the custom domains is an open client decision
and would also ship four pages of someone else's unpublished Designer work.

---

## 1. Where the CSS actually lives — read this first

There is no global stylesheet you can edit. The design system is **CSS text inside
Webflow HtmlEmbed blocks**, and that shapes everything about how you change it.

- Six service pages share one component, **Service Page Styles**
  (`b3b13b91-f7d3-431f-4f5c-148220cae266`). Edit it once, six pages change.
- Five state-family pages each carry their own copy of a near-identical hero
  stylesheet. There is no shared component for them.
- `set_settings` has **no partial update**. Changing one declaration means
  resending the whole embed as a literal string.
- These class names are **not Webflow Designer styles**. A previous attempt to
  rebuild a hero as native elements failed with "One or more styles not found" for
  every class — they exist only as CSS text. Porting the ~115 classes into Designer
  styles is a separate project, scoped in the audit.

---

## 2. Palette — the dominant tokens

One button-hover red site-wide. Verified across all 586 pages in the staging sitemap.

| token | value | role |
|---|---|---|
| `--navy` | `#1a2744` | headings, dark sections |
| `--navy-light` | `#2a3a5c` | |
| `--teal` | `#3ba5a8` | accent, eyebrows, icons, links |
| `--teal-light` | `#e8f6f6` | icon backgrounds, pale fills |
| `--teal-dark` | `#2d8a8d` | gradient end |
| `--warm` | `#f9f6f1` | warm section background |
| `--warm-dark` | `#f0ebe3` | image placeholder |
| `--white` | `#ffffff` | |
| `--text` | `#2c2c2c` | body |
| `--text-light` / `--soft` | `#5a5a5a` | secondary body |
| `--text-muted` / `--mute` | `#8a8a8a` | captions, disclaimers |
| `--accent` | `#e8734a` | secondary accent |
| `--accent-light` | `#fef0eb` | accent fills, callouts |
| `--border` | `#e5e5e5` | neutral hairline |
| `--rule` | `#e6e2da` | **warm** hairline — see §6 |
| **`--cta`** | **`#db5b4f`** | **button fill** |
| **`--cta-hover`** | **`#b34a40`** | **the single hover red** |

Radii `--radius: 12px`, `--radius-lg: 20px`. Layout `--max-width: 1200px`,
`--section-pad: 100px`. Shadows `--shadow-sm/md/lg` as declared in the component.

> **Gotcha.** The service family hardcodes `#db5b4f` and `#b34a40` in its button
> rules rather than using `var(--cta)`. The state family tokenises them. If you
> sweep colours, grep for the literals as well as the token.

---

## 3. Buttons — NOT converged, two systems

The heroes were converged; **the buttons were not**. Only the colours match. Treat
this as known outstanding work, not as a design decision.

| | service `.btn-primary` | state `.mm-btn--primary` |
|---|---|---|
| background | `#db5b4f` | `var(--cta)` |
| hover background | `#b34a40` | `#b34a40` ✅ same |
| padding | `16px 32px` | `16px 28px` |
| border-radius | `50px` | `999px` |
| font-size | `16px` | `15px` |
| font-weight | `600` | `600` ✅ same |
| border | `none` | `2px solid transparent` → `var(--cta)` |
| box-shadow | `0 4px 16px rgba(219,91,79,0.3)` | none |
| hover transform | `translateY(-2px)` | `translateY(-1px)` |
| transition | `0.25s` | `0.15s / 0.2s ease` |

Secondary buttons diverge the same way: service `.btn-secondary` is white with a
`1px` CTA border; state `.mm-btn--secondary` is transparent with a `2px` CTA border
and fills with `var(--cta)` on hover.

The service rules are almost entirely `!important`, because two duplicate
stylesheets used to fight each other. Do not strip those without re-testing — an
earlier attempt turned `.hero-cta` transparent.

**If you converge these**, the state spec is the better base (tokenised, uses
`border-color` so the outline variant is symmetric), and the decision that already
went the state family's way on the hero would apply consistently.

---

## 4. Hero — converged 2026-08-04, both families identical

| property | value |
|---|---|
| section padding | `clamp(36px, 5vw, 64px) clamp(20px, 5vw, 48px) clamp(28px, 4vw, 48px)` |
| inner box | `max-width: 1200px; margin: 0 auto` — **no inner padding** |
| grid | `minmax(0, 1.05fr) minmax(0, 1fr)` |
| gap | `clamp(32px, 5vw, 64px)` |
| collapses to 1 column | `900px` |
| h1 | `clamp(32px, 5vw, 52px)` / weight `600` / lh `1.08` / ls `-0.015em` / mb `28px` |
| eyebrow | `13px` / weight `600` / uppercase / ls `0.08em` / mb `28px`, teal |
| eyebrow `::before` | a short teal rule (`24–28px × 1–2px`) |

**Three traps, all of which have already bitten once:**

1. The hero's horizontal padding belongs on the **section**, not inside the 1200px
   box. Putting it inside makes the text start 32px right and the columns 64px
   narrower. `.hero .container` is deliberately reset to `padding: 0`.
2. The eyebrow selector must **not** be element-qualified. The eyebrow is a `div`;
   the `h1` is the headline. Re-adding `h1.hero-eyebrow` silently unstyles it.
3. `.mm-hero` must appear on the **section only**, never also on the wrapper `div`.
   It was on both across five pages, doubling the padding.

Do not restore a fixed `font-size: 36px` under 768px — `clamp()` governs.

---

## 5. Headings

`h1` is the hero headline (see above). `h2` is `40px` / weight `800` / lh `1.2` /
ls `-0.3px`, dropping to `32px` at 768px. Section labels above an `h2` are `13px`
uppercase teal with `1.5px` letter-spacing — note this is **px**, unlike the hero
eyebrow's `0.08em`; they are separate elements and were never unified.

**The `h1` must be the headline, not the eyebrow.** Five service pages had it
backwards — the `h1` was the small uppercase label and the real headline was a `<p>`.
`hero-lint.py` now fails on this.

---

## 6. Deliberately NOT on the dominant palette

Do not "fix" these. Each is a decision, and the reasoning is in `drift/README.md`.

- **`#e6e2da`** (`--rule`) — 12 uses, always a hairline. A *warm* rule that pairs
  with the warm backgrounds. Flattening it to `--border #e5e5e5` would put neutral
  hairlines on warm fills.
- **`#002833` / `#34abc7`** — fallbacks inside `var(--base-color-brand--blue-dark, …)`.
  These embeds read Webflow's own Designer brand variables; overriding them from a
  stylesheet fights the Designer.
- **`#f7f6f5` / `#fbf9f9`** — `--surface-alt` and `--warm-alt`, deliberate additions
  on the two resource hubs.
- **`#ff8c5a`** on `.placeholder-note` — six service pages. **Dead CSS**: the class
  is declared but used by zero elements across all 576 in-scope pages. Either delete
  the rule or leave it; it is not a visible change either way.

---

## 7. Verify before you claim anything works

```bash
bash    tools/css-consolidation/drift/verify.sh        # colour + byte identity, ~90s
bash    tools/css-consolidation/drift/verify.sh quick  # skip the site sweep, ~15s
python3 tools/css-consolidation/drift/hero-lint.py     # structure, ~15s
python3 tools/css-consolidation/drift/snapshot.py --verify
```

All four are green as of this writing. `snapshot.py` (no flag) re-banks 80 embeds
across 9 pages — that is the rollback material, and the restore target is
`.fixed.html`, **not** `.orig.html` (which predates the colour fix).

### Lessons that cost real time here

- **Comparing declared values does not prove pages render alike.** A cascade check
  and a geometry calculation both passed while the box model still differed, twice.
  Count rule *applications*, not just values.
- **Verify a hand-reproduced payload before sending it.** Because the code is a
  literal tool parameter, large embeds get retyped. Write the candidate to a file,
  diff it against the source, *then* spend the write. Two transcription slips were
  caught this way and one only after publishing.
- **Poll for a marker before trusting a post-publish diff**, or you compare cached
  content with itself and see no change.
- **The byte-length invariant only holds for hex-for-hex edits.** `fix.py` asserts
  it. `embed0` and the five state heroes are documented exceptions.
