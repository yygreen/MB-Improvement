# Build record: Georgia and North Carolina Tier 1 sets (2026-08-05)

Eight pages built on staging, completing the full 12-page Tier 1 complex
(4 services x 3 states), per "continue with the same for the two other states".
Copy drafted fresh this session by Claude; generated and gated by
`tools/tier1/gen-ga-nc-pages.py`; verified by `tools/tier1/verify-staged.py`.

| Page | Page id | Embed element | Words |
| --- | --- | --- | --- |
| /transition-planning-georgia | 6a72fee1d368a296f7587efe | 2aac12c3-4fec-0504-226b-cb138c2e8768 | 965 |
| /early-intervention-georgia | 6a72fee2ba2fea86c0d4a1cd | 282411ab-5c5a-6de5-9ab6-cd933da5360f | 1,022 |
| /parent-training-georgia | 6a72fee2a29eccb8824eaaef | d14235a7-54b6-5155-cd18-cb41939b3124 | 916 |
| /behavior-support-georgia | 6a72fee3a29eccb8824eab12 | 0e20044b-4732-481d-753a-79a72952e338 | 1,009 |
| /transition-planning-north-carolina | 6a72fee30453f9539a20c632 | f8a4cced-0c37-85c9-a516-dc656ed7992f | 930 |
| /early-intervention-north-carolina | 6a72fee3d368a296f7587fef | c9dcbacb-489d-d47e-890f-a7c49fcdb7b2 | 959 |
| /parent-training-north-carolina | 6a72fee457ccb52693e1c03e | a0ee0a99-377c-6ec2-b03a-a8a5deebc670 | 878 |
| /behavior-support-north-carolina | 6a72fee44850fefbf2dfe597 | a0fd5fcb-9af1-6a33-ec12-960695429439 | 997 |

All at https://mastermindbehavior.webflow.io/<slug>; staging subdomain only.

## Verified at build (all eight, plus NJ re-verified in the same run)

- Style block byte-identical to the pilot embed (programmatic extraction)
- Single h1, exact title tags and meta descriptions (rendered entity-encoding
  unescaped before compare); every embed line renders verbatim on staging
- All internal links 200, including within-state sibling cross-links and the
  corrected NC city slugs (greensboro-nc, fayetteville-nc; both bare slugs
  301 to the Georgia hub - trap recorded below)
- Em dashes only in verbatim coverage-table rows
- Service JSON-LD via the bulk endpoint; 0 invalid properties against the
  schema.org vocabulary; sitemap shows 0 of the 12 Tier 1 slugs
- link-audit.sh staging: RESULT pass, 0 Tier 1 targets pending (was 11 this
  morning)
- Word counts 878-1,022 (PT-NC at 878 sits just under the 900 soft floor)

## Sources and citation status

- Coverage rows: extracted programmatically (curl, byte-verbatim) from the
  live client-approved GA and NC hubs into tools/tier1/{state}-hub-rows.txt;
  each page uses a service-relevant 4-row subset, never the full table
- Office lines: GA = Macon, 4658 Presidential Pkwy (from live contact-page
  JSON-LD: 4658 Presidential Pkwy #1365, Macon GA 31206); NC has NO office,
  so NC pages carry a statewide-reach line instead
- VERIFIED dph.georgia.gov/babies-cant-wait: birth to three, Department of
  Public Health, Part C, referral channels, transition-at-3 materials exist
- VERIFIED ncdhhs.gov (About NC ITP): under three, Early Intervention Section
  of the Division of Child and Family Well-Being, Part C, sixteen CDSAs,
  referral channels
- VERIFIED dbhdd.georgia.gov: NOW and COMP are I/DD waivers with DBHDD
  running day-to-day operation; regional field offices exist
- NOT RE-VERIFIED, for Taylor:
  1. "waits are commonly measured in years" (GA NOW/COMP) and "waits are
     long" (NC Innovations) - widely documented, no single official page
     cited; hedged, but review the phrasing
  2. School transition timing on GA/NC pages is stated ONLY at the federal
     IDEA level (by 16, student invited); no state-specific earlier
     requirement is claimed for either state
  3. "parent training is typically billed as part of ABA therapy" -
     practice-level claim, hedged, same as the NJ pages
  4. NC transition FAQ says continued ABA past 21 "can be possible depending
     on your coverage" - the coverage fact is the hub's verbatim row, but
     whether Mastermind itself serves adults past 21 is NOT claimed; company
     age copy stays "through age 21". Taylor should confirm this framing.

## Cannibalization checks

Semrush resource_organic on mastermindbehavior.com filtered by "early
intervention" / "parent training" / "behavior support" (2026-08-05, domain-
wide, state-agnostic): only national blog posts rank; nothing targets any
service+state combination for any of the three states. phrase_organic for
service+state phrases returns NOTHING FOUND (below data threshold). GSC
cross-check NOT run (tool unavailable this session) - flag carried.

## Traps recorded

- /areas-we-serve/greensboro and /areas-we-serve/greenville are GEORGIA
  redirects to the GA hub; the NC cities live at greensboro-nc and
  greenville-urfem (the latter avoided; Jacksonville used instead)
- /areas-we-serve/fayetteville is the GEORGIA Fayetteville; NC is
  fayetteville-nc
- GA hub table rows contain spaces between tags (<tr> <td>); NC rows do not;
  both kept byte-verbatim as extracted

## Open before production (whole 12-page complex)

1. Taylor clinical review of all 11 fresh-draft pages (pilot has its own
   review flags in BUILD-RECORD.md); the 8 GA/NC pages are entirely fresh
2. None of the 12 pages is draft or noindexed (API cannot set robots).
   Protections: sitemap-excluded, no inbound links from published nav.
   Before ANY production publish: add noindex via Designer page settings or
   flip to draft. They all ride a production publish otherwise. The staged
   old-path link fixes ride that same publish.
3. OG images needed for all 12
4. FAQPage schema deferred on all 12 until FAQ text is final after sign-off
5. Pilot page still does not link its NJ siblings (copy under review); the
   GA/NC transition pages DO link their siblings from birth
6. Sister-state footer links (e.g. NJ transition -> GA/NC transition) still
   omitted everywhere; a decision for after review, since adding them means
   editing reviewed copy
7. "BACKFILL 992" state-key typed confirmation still pending (separate task)
