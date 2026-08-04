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
| `embed0` | 21033 | Service Page Styles component | behavior-support, early-intervention, in-home-aba-therapy, parent-training, skill-development, transition-planning | `#f8f6f1`x1 | no |
| `embed1` | 7004 | hero band | aba-therapy-in-georgia | `#c64d42`x2 | yes |
| `embed3` | 5143 | bottom CTA band | aba-therapy-in-georgia | `#c64d42`x2 | yes |
| `embed4` | 6807 | hero band | aba-therapy-in-new-jersey | `#c64d42`x2 | no |
| `embed6` | 6782 | hero band | aba-therapy-in-north-carolina | `#c64d42`x2 | no |
| `embed9` | 6855 | hero band | financial-aid-resources | `#c64d42`x2 | no |
| `embed10` | 21719 | body embed | financial-aid-resources | `#c64d42`x2, `#fdebe2`x1 | no |
| `embed11` | 19479 | body embed | financial-aid-resources | `#c64d42`x2 | no |
| `embed12` | 4595 | bottom CTA band | financial-aid-resources | `#c64d42`x2 | no |
| `embed13` | 6533 | hero band | insurance-terminology | `#c64d42`x2 | no |
| `embed15` | 4613 | bottom CTA band | insurance-terminology | `#c64d42`x2 | no |
| `embed16` | 21927 | page embed | services | `#c45045`x4, `#eef0f4`x1 | no |
