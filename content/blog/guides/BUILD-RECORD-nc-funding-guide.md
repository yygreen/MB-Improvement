# North Carolina funding guide: build record

**Shipped 12 August 2026.** Live at
`https://www.mastermindbehavior.com/post/is-aba-therapy-covered-by-insurance-north-carolina`

Rewritten in place per `OVERLAP-DECISION-north-carolina.md`. URL kept, no
redirect, no second page created.

## What shipped

| | |
|---|---|
| Collection item | `673ae71b8f7e62aaf54d28e6` (Blog Posts `6627fd62e242d50407cfe157`) |
| Body | 18,778 chars, md5 `99d06debdb97509df1a861c6b1ee9b0c` |
| Dataset | `data/funding/north-carolina.json`, 37 facts, gate green |
| Quotes gated against dataset | 42 |
| Internal links | 9, of which 6 sit above the closing section |
| Figures | 1 (`nc-funding-who-pays-when.webp`) |
| Title | Is ABA Therapy Covered by Insurance in North Carolina? |
| Byline | Mastermind Behavior Clinical Team `6a2e763ca589b9cdd033a53b` |

Figure asset `6a7c889e9e9624011425c787`, normalized by Webflow into CMS
space as `6627fd62e242d50407cfe155/6a7c89fb954d912788e40629_...`.
`figures.json` now carries the normalized URL so a rebuild does not create
a duplicate asset.

## Verification

Live page fetched after publish and compared against the generated source:

- tag-stripped text identical, 16,759 chars both sides
- href list identical, 9 links, same order
- figure renders, alt non-empty, width 600
- no em dash, no `RBT`, no clinic or center language
- only phone token in the body is the Smart NC line `855.408.1212`

## The seven must-fix items from the overlap decision

1. **Regulator named wrong.** Fixed. The appeal section names the
   Department of Insurance and states explicitly that this is not the
   Department of Health and Human Services.
2. **No appeal deadline.** Fixed. 120 days, Smart NC by name, the
   expedited route, and that it is free.
3. **Order requirement missing.** Fixed, and given its own subsection.
4. **$40,000 treated as live.** Fixed. The page now leads that section
   with the fact that the figure has been indexed since 2017, and tells
   families to ask their insurer in writing rather than printing a number
   we cannot source.
5. **Unverified over-21 claim.** Verified against the NC Medicaid bulletin
   on CMS approval effective 1 July 2021, and kept.
6. **Legacy link** to `/areas-we-serve/aba-therapy-in-north-carolina`.
   Removed; the page now links `/aba-therapy-in-north-carolina`.
7. **Stray NJ Medicaid cross-reference.** Repointed at the New Jersey
   funding guide, which now exists.

## What this page says that no competing page says

The $40,000 cap is a 2015 base, not the live ceiling. N.C.G.S. 58-3-192
indexes it to CPI for the South Region from 2017, measured against March
2015 and rounded to the nearest thousand. Every other page we checked
quotes $40,000 flat. We could not find the current indexed figure on a
primary source, so the page flags that gap rather than inventing a number.

Second: North Carolina Medicaid does not stop at 21. CMS approved RB-BHT
for beneficiaries over 21 effective 1 July 2021. Most state autism
benefits end at 21, so this is the difference between a plan and a cliff
for transition-age young adults.

## Known gaps

- The State Health Plan section deliberately declines to characterize the
  benefit, because we have not verified its terms against a primary
  source. Verify or leave as is; do not guess.
- The New Jersey guide does not yet link back to this page. Reciprocal
  link outstanding.
- The main image is the legacy hero. New Jersey got a custom photographic
  hero; this page has not.
