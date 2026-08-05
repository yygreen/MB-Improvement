# Build record: NJ Tier 1 set completion (2026-08-05)

Three pages built to complete the four-service New Jersey complex on staging,
per "build the other service pages for new jersey on staging so we can gauge
the whole complex". Copy drafted fresh this session by Claude (no July 28
pipeline draft exists for these three) and generated + gated by
`tools/tier1/gen-nj-pages.py`; verified by `tools/tier1/verify-staged.py`.

| Page | Page id | Embed element | Words |
| --- | --- | --- | --- |
| /early-intervention-new-jersey | 6a72fb3e8eed26eb797db45b | afefb25b-9139-e864-3baf-eed252384b67 | 1,063 |
| /parent-training-new-jersey | 6a72fb3e8eed26eb797db4fb | 19ff5aa5-499d-c17c-de8f-893125d645ba | 969 |
| /behavior-support-new-jersey | 6a72fb3f8eed26eb797db545 | 0a254646-b809-b377-115e-c27cb814c45a | 1,043 |

Review URLs (staging subdomain only; production untouched):

- https://mastermindbehavior.webflow.io/early-intervention-new-jersey
- https://mastermindbehavior.webflow.io/parent-training-new-jersey
- https://mastermindbehavior.webflow.io/behavior-support-new-jersey

## Verified at build (all three)

- Style block byte-identical to the pilot embed (extracted programmatically)
- Single h1, exact title tag and meta description (142 / 134 / 126 chars)
- Every embed line renders verbatim on staging; all internal links 200,
  including the four-way NJ sibling cross-links
- Em dashes only in verbatim coverage-table rows (one site-wide marketing
  HTML comment also carries one; not page copy)
- Service JSON-LD via bulk_update_pages_schema_markup; 0 invalid properties
  against the schema.org vocabulary
- Excluded from sitemap; BT terminology; no RBT / clinic / guarantees /
  competitors; phone 732.813.7333 only
- link-audit.sh staging: pass, Tier 1 pending count 11 -> 8

## Sources and citation status

- Coverage tables: verbatim rows from the live client-approved NJ hub
  (fetched 2026-08-05); subsets differ per page to avoid the near-duplicate
  block pattern (EI: mandate/coverage/FamilyCare/pathways; PT adds Plans
  covered; BS: mandate/dollar-cap/FamilyCare/licensure)
- Service facts (play-based, NET, BST, FBA/BIP, FCT, before-age-five gains
  claim) restated from the live client-approved generic service pages
- VERIFIED nj.gov/health/fhs/eis: NJEIS serves children under 3, run by the
  Department of Health under IDEA Part C; a System of Payment and Family
  Cost Participation exists (claim phrased no stronger than the page title)
- NOT RE-VERIFIED, for Taylor: age-3 handoff details are stated at the
  federal Part C/Part B structural level only (nj.gov subpages have moved);
  "parent training is typically billed as part of ABA therapy" is a
  practice-level claim, hedged, not a statute citation; PBIS-consideration
  sentence is federal IDEA, hedged with "in practice that often means"

## Cannibalization checks (per page, 2026-08-05)

Semrush resource_organic on mastermindbehavior.com filtered by service term:
only national blog posts rank (e.g. /post/effective-parent-training-...);
no page targets "{service} new jersey". GSC cross-check NOT run (tool
unavailable this session) - flag carried, same caveat as the pilot check.

## Open before production (in addition to the pilot's items)

1. Taylor clinical review of all three; fresh drafts, so full review, not a
   trim pass. Note especially: "Children who begin before age five
   consistently show the greatest gains" (reused from the live approved
   /early-intervention page, but it is an outcome-flavored claim), and both
   NOT-RE-VERIFIED items above.
2. Pages are NOT draft and NOT noindexed (API cannot set robots). Same
   protections as the pilot: sitemap-excluded, no inbound links from
   published nav. Before any production publish: noindex via Designer page
   settings or flip to draft. They ride a production publish otherwise.
3. OG images needed (none set).
4. FAQPage schema deferred until FAQ text is final after sign-off.
5. The pilot page does not yet link its three siblings (its copy is under
   review); add the one-sentence cross-service block after Taylor's pass.
6. GA/NC footer sibling links still omitted on all four NJ pages until those
   states ship.
