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

---

## Executed 2026-08-13 (staged, not published)

All three edits went through the REST path with per-replacement assertions
and a re-read diff. Every write verified byte-identical to the locally
computed body, so the embedded insurance widget passed through untouched.

**`/post/medicaid-and-aba-coverage-in-nj`** (+204 chars)
April 2020 corrected to 1 January 2019 in both places, with the SPA named
and its 18 September 2020 approval date given. Reference [1] repointed from
a landing page that stated no date to the CMS-approved SPA PDF, across all
five occurrences. Legacy `/areas-we-serve/` link fixed.

The assertion earned its place here: the nj.gov URL occurs five times, not
the four I specified, because the reference line carries it twice. The dry
run refused to write until the count was right.

**`/post/how-georgia-laws-support-autism-services`** (-361 chars)
Competitor table deleted. Replaced with a section that points at the
Georgia funding guide instead of naming providers. Also removed a broken
heading, `<h2>Age GroupNumber Screened18-24 Months3,500+</h2>`, where a
table had collapsed into an H2.

**`/post/aba-therapy-services-in-georgia-overview`** (-2,023 chars)
The coverage section did not merely overlap the guide, it contradicted the
statute: it told families insurers "may impose restrictions on the number
of therapy sessions allowed per week or year" when Ava's Law states a
policy "shall not include any limits on the number of visits". Replaced
with the sourced position plus a pointer to the guide. Legacy link fixed.

## Two corrections to this audit

- The **"guarantee"** on the Georgia laws page refers to what the law
  guarantees, not to an outcome we promise. Correct usage, left alone.
- The **screening figure is sourced**, to Georgia DPH. Calling it invented
  was wrong. The actual defect was the collapsed table, now removed.

## Still open on these pages

**The clinic language on the Georgia overview.** Eighteen references,
including a "Clinic-Based Therapy" section describing dedicated therapy
rooms and sensory spaces as though we offer them. This is a rewrite rather
than a find-and-replace: the section sits under "ABA Therapy Settings in
Georgia" and legitimately describes what exists in the state, so it needs
reframing to make clear it is describing the landscape, not our services.
Doing that badly would be worse than leaving it.

**RBT on the same page, three uses.** All three name the BACB credential:
a certification-tier table row, "RBT certification", and "RBT Ethics Code".
The house rule targets RBT as our term for our own staff; renaming an
actual credential would introduce a factual error. Left as is, flagged for
a decision rather than silently changed.

**Unsourced hourly rates** ($100 to $200 per session) remain in the
settings sections. They should point at the cost page instead.

## Second competitor mention removed (2026-08-13, published)

The table removal was not the whole job. The page's **opening paragraph**
also named both organisations: "Families affected by autism benefit from
several top autism centers, such as Above & Beyond Therapy and the Emory
Autism Center." Found only when checking the published site, because the
first pass searched for the table and did not sweep the page for the names.

Rewritten to categories rather than names, and pointed at the coverage
question. Verified live: both names absent, and an independent diff against
the pre-change live text shows 12,986 of 13,420 characters untouched.

**One undeclared change.** That diff also caught an em dash normalised to a
comma in the Family Support Services paragraph, which I did not intend to
touch. The result is correct (an em dash fails our own copy gate) but it
was not a declared edit. This is the drift that hand-retyping causes, and
it is the argument for doing large-body edits over REST with per-string
assertions rather than re-emitting a whole field.

**Lesson worth keeping:** when removing a named entity from a page, grep
the whole body for the name, not just the structure it appeared in.
