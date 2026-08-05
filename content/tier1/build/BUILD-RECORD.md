# Build record: /transition-planning-new-jersey (pilot)

Built 2026-08-05 from `transition-planning-new-jersey.review.md`, body copy verbatim.
Page id `6a72f67cb41d49da7fdf2182`, embed element `d5a2f2f3-c0e1-96ec-a183-d6790073fe1d`.
Live for review on the staging subdomain only:
https://mastermindbehavior.webflow.io/transition-planning-new-jersey

## Verified at build

- Single h1, exact title tag and meta description (134 chars) from the page meta spec
- All 15 body links return 200 on staging; GA/NC sibling footer links omitted (pages absent)
- Coverage table verbatim incl. em dashes; zero em dashes in fresh copy
- Hedged IEP sentence in place; BT terminology; no RBT, no clinic implied, no
  guarantees, no competitors; phone 732.813.7333 only
- Service schema renders and validates against the schema.org vocabulary (0 invalid)
- FAQPage schema deliberately absent until the FAQ text is final after review
- Excluded from sitemap; zero internal links point at the page from anywhere

## Citation re-verification (build-time, per checklist)

- VERIFIED njfamilycare.dhs.state.nj.us: "Children under 19 ... up to 355% of the
  Federal Poverty Level"
- VERIFIED nj.gov/humanservices/ddd/individuals/transition: application "after
  turning 18 and at least six months before you turn 21"; "DDD services are
  available to people who are 21 or older"; Medicaid required
- NOT RE-VERIFIED (drafting-time verification stands, flag for reviewer):
  N.J.A.C. 6A:14-3.7(e)11 exact citation (official chapter PDF is image/glyph
  encoded; DOE transition URLs have moved; code mirrors block automated access),
  "DDD transition assistance from 16", "CSOC ends the day before the 21st birthday"

## Open before production

1. Taylor clinical review on the staging URL
2. Word count: 1,541 rendered vs 900-1,300 checklist target; expect trim in review
3. Page is NOT draft (so it is viewable) and NOT noindexed - the API does not expose
   per-page robots. Protections: no inbound links, excluded from sitemap. Before any
   production publish either add noindex in Designer page settings head code, or ask
   for the page to be flipped to draft. It rides a production publish otherwise.
4. OG image still needed; none set
5. FAQPage schema to generate from the final Section 6 text after sign-off
6. S6 closing line built as the closing CTA buttons rather than a literal sentence
