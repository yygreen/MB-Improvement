# Colour drift: corrected embeds

Each `embedN.orig.html` is the live embed code as rendered on staging; each
`embedN.fixed.html` is byte-identical to it except for the colour substitutions
listed below. Lengths match exactly, so applying one is a paste, not a merge.

Substitutions, and why each is drift rather than a deliberate choice:

| from | to | dominant name | note |
|---|---|---|---|
| `#c64d42` | `#b34a40` | `--cta-hover` | third button-hover red for the same button role |
| `#c45045` | `#b34a40` | `--cta-hover` | fourth button-hover red for the same button role |
| `#f8f6f1` | `#f9f6f1` | `--warm` | one unit off in the red channel; invisible, pure copy-paste drift |
| `#fdebe2` | `#fef0eb` | `--accent-light` | single-use near-miss |
| `#eef0f4` | `#e8f6f6` | `--teal-light` | single-use near-miss |

Deliberately NOT changed:

- `#e6e2da` — appears 10 times and *only* ever as `--rule`. A consistently used
  warm hairline that pairs with the warm backgrounds. It is an unnamed member of
  the palette, not drift; flattening it to `--border #e5e5e5` would make hairlines
  neutral against warm fills.
- `#ff8c5a` — `.placeholder-note` on six service pages. A visible change against
  `--accent #e8734a`, so it needs a decision rather than a sweep.
- `#002833` / `#34abc7` — these are fallbacks inside
  `var(--base-color-brand--blue-dark, #002833)`. Those embeds read Webflow's own
  Designer brand variables; overriding them from a stylesheet would fight the
  Designer rather than unify with it.

| embed | bytes | what | page(s) | substitutions | applied |
|---|---|---|---|---|---|
| `embed0` | 21607 | Service Page Styles component (+ hero convergence, see note) | behavior-support, early-intervention, in-home-aba-therapy, parent-training, skill-development, transition-planning | `#f8f6f1`x1 | yes |
| `embed1` | 6996 | hero band | aba-therapy-in-georgia | `#c64d42`x2 | yes |
| `embed3` | 5143 | bottom CTA band | aba-therapy-in-georgia | `#c64d42`x2 | yes |
| `embed4` | 6799 | hero band | aba-therapy-in-new-jersey | `#c64d42`x2 | yes |
| `embed6` | 6774 | hero band | aba-therapy-in-north-carolina | `#c64d42`x2 | yes |
| `embed9` | 6847 | hero band | financial-aid-resources | `#c64d42`x2 | yes |
| `embed10` | 21719 | body embed | financial-aid-resources | `#c64d42`x2, `#fdebe2`x1 | yes |
| `embed11` | 19479 | body embed | financial-aid-resources | `#c64d42`x2 | yes |
| `embed12` | 4595 | bottom CTA band | financial-aid-resources | `#c64d42`x2 | yes |
| `embed13` | 6525 | hero band | insurance-terminology | `#c64d42`x2 | yes |
| `embed15` | 4613 | bottom CTA band | insurance-terminology | `#c64d42`x2 | yes |
| `embed16` | 21927 | page embed | services | `#c45045`x4, `#eef0f4`x1 | yes |

## Note on `embed0` — the length invariant no longer applies to it

Every other embed here is a hex-for-hex colour substitution, so `.orig` and
`.fixed` are the same length and `fix.py` asserts it. `embed0` is now the one
exception: on 2026-08-04 it also took the hero convergence, which is a deliberate
value change rather than a colour swap.

What changed beyond colour, all of it aligning the service hero with the state
pages' `.mm-hero`:

- `.hero` vertical padding `80px 0 100px` -> `clamp(36px, 5vw, 64px) 0 clamp(28px, 4vw, 48px)`
- `.hero-grid` `1fr 1fr` / `gap: 64px` -> `minmax(0, 1.05fr) minmax(0, 1fr)` / `gap: clamp(32px, 5vw, 64px)`
- `.hero-headline` `48px / 800 / 1.15 / -0.5px` -> `clamp(32px, 5vw, 52px) / 600 / 1.08 / -0.015em`
- the eyebrow rule is **de-qualified**: `.hero h1.hero-eyebrow` -> `.hero .hero-eyebrow`,
  with `letter-spacing` `1.5px` -> `0.08em` and `margin-bottom` `20px` -> `28px`
- the fixed `font-size: 36px` mobile override is gone; `clamp()` governs
- the hero grid now collapses at 900px, matching the state family, not 768px

Two things a future reader will trip over:

1. **Do not re-add `h1.` to the eyebrow selector.** The eyebrow is a `div`; the h1
   is the headline. Re-qualifying it silently unstyles the eyebrow on all six pages.
2. **The five page embeds still carry their own `.hero-eyebrow` rule** at
   `1.5px` / `20px`. Those are now outranked by the component's `.hero .hero-eyebrow`
   (0,3,0 beats 0,2,0) and are kept only as a fallback. They are not what renders —
   `hero-lint.py` and the cascade check confirm `0.08em` / `28px` wins on all six.

## The state heroes applied their padding twice

`.mm-hero` sat on both the wrapper `<div class="mm-embed mm-hero">` and the inner
`<section class="mm-hero">`, so the rule's padding landed twice on all five
state-family heroes. That is double the top padding at every width, and below
~1296px a different left edge and inner width from the service family — at 1024px,
96px vs 48px and an 832px vs 928px content box. Wide viewports hid the horizontal
half of it, because the 1200px `max-width` cap absorbs the extra padding once there
is room to spare.

Fixed by dropping `mm-hero` from the wrapper on `embed1`, `embed4`, `embed6`,
`embed9` and `embed13`, leaving `<div class="mm-embed">` around
`<section class="mm-hero">` — which is exactly how the service family is built.
Those five `.fixed.html` files are therefore 8 bytes shorter than their `.orig`,
the second deliberate departure from the length invariant after `embed0`.

`hero-lint.py` now counts hero padding applications per page and fails above one,
so this cannot come back silently.
