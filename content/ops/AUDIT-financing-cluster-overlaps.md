# Audit: four unresolved financing-cluster pages (2026-08-13)

Checked against the gated datasets and the copy gates. One of these is not
an overlap problem, it is a duplicate page.

## 1. `/post/insurance-for-aba-therapy-new-jersey` — DUPLICATE, kill it

**This is a byte-identical copy of `/post/medicaid-and-aba-coverage-in-nj`.**

- Both bodies: 11,471 characters. Similarity ratio 1.000.
- Same `<title>`: "Understanding Medicaid and ABA Coverage in NJ".
- Same opening sentence, same headings, same everything.
- **No canonical tag on either.** Neither carries a robots directive, so
  both are fully indexable.
- The duplicate is absent from the sitemap, so it is half-orphaned already,
  but absence from a sitemap does not stop indexing or deduplication.

Two identical indexable URLs compete with each other and with the New
Jersey funding guide. Google picks one and it may not be the one we want.

**Action: 301 `/post/insurance-for-aba-therapy-new-jersey` to
`/post/medicaid-and-aba-coverage-in-nj`.** No content to salvage, because
there is no content that is not already on the other URL.

It also carries the April 2020 error twice more, which the redirect
disposes of at no extra cost.

## 2. `/post/aba-therapy-services-in-georgia-overview` — trim, and clean

3,327 words. The worst copy-gate offender on the property.

- **18 clinic or center references**, including a section heading
  "Clinic-Based Therapy". We do not run a clinic. This contradicts the
  in-home positioning on every page that links to it.
- **3 uses of `RBT`**, against the house rule (Behavior Technician).
- All three unverified boilerplate claims.
- Unsourced hourly rates: $100, $150, $200.
- Legacy link to `/areas-we-serve/aba-therapy-in-georgia`, which 301s.

It does correctly state $35,000 and age 20, which match the dataset.

**Action:** cut "Insurance Coverage Details" and "Limitations and
Pre-Authorization" to a short paragraph pointing at the Georgia funding
guide; delete the clinic framing; drop the unsourced rates or point them
at the cost page; fix the legacy link.

## 3. `/post/how-georgia-laws-support-autism-services` — cut the competitor table

2,647 words.

**It recommends two competitors by name.** The "Top Autism Centers"
section is a table listing:

> Above & Beyond Therapy, Atlanta, ABA therapy, family support
> Emory Autism Center, Atlanta, Research, diagnostic services, therapies

Above & Beyond Therapy is a direct ABA competitor in our own Georgia
market, and the page calls these "top-rated" and "leading facilities". We
are sending Georgia families to a competitor from our own site. This
breaks the no-competitor-names gate outright.

Also present:
- 7 clinic or center references
- the word "guarantee"
- a screening table with no source: "Age Group / Number Screened /
  18-24 Months / 3,500+". Unverifiable and reads as invented. Cut it or
  source it.

**Action:** delete the "Top Autism Centers" table entirely. Point
"Georgia's Autism Insurance Laws" and "Mandatory Coverage Reporting" at
the Georgia funding guide rather than restating the law.

## 4. `/post/ssi-benefits-for-autistic-child` — keep, it is the healthiest of the four

3,041 words. No clinic language, no competitors, no RBT.

This is a genuinely distinct topic. SSI is a federal income benefit, not
ABA funding, and the page covers the age-18 redetermination, ABLE
accounts, HCBS waivers and special needs trusts. `/financial-aid-resources`
has an SSI *section*; this has an SSI *page*. That is a section-versus-page
relationship, not a duplicate.

**Action:** keep it, and have `/financial-aid-resources` link to it rather
than compete. One thing to verify: the page states $994, which is
consistent with a 2026 federal benefit rate after COLA, but it should be
cited to ssa.gov rather than asserted.

## The pattern across all four

All four carry the same three unverified boilerplate claims (90%+
retention, no onboarding waitlist, six weeks). That is four more pages on
a pile that already spans the Tier 1 pages and 133 legacy posts, and it is
still waiting on a decision from Adina or Raizy.

## Execution note

Items 2 and 3 are body rewrites on CMS posts. Both bodies are large and at
least one embeds the insurance widget, so they should go through the REST
path with per-replacement assertions rather than being re-emitted by hand.
Item 1 is a redirect, which is UI-only. Item 4 needs no change beyond a
link from a static page.
