# ABA cost calculator and the consolidated cost page

**Page live 13 August 2026** at
`https://www.mastermindbehavior.com/post/cost-of-aba-therapy-for-autism`

**Calculator staged, not yet live.** See "The one step left" below.

## What shipped

| | |
|---|---|
| Collection item | `6695038d9bdd2d4ef3d3bbc4` |
| Body | 11,160 chars, ~1,620 words |
| Quotes gated against datasets | 12 |
| Internal links | 11, of which 6 above the closing section |
| Widget script | `mb_cost_calculator` v1.0.0, asset `6a7d8935e4620c5857e85cac` |
| Datasets | 3 funding + 3 cost files, all gate green |

## The design rule

The calculator never invents a price. Commercial insurers negotiate rates
per provider and publish nothing, so there is no primary source for what a
private plan pays. The widget asks the family for the figure on their own
quote or explanation of benefits, and applies the sourced rules to it.

That is the whole differentiator. Every competing page answers this query
with a national average nobody can source. We answer it with the family's
own number plus the rules that decide what their plan can do with it.

## What is sourced and what is flagged

**Georgia**: current ASD fee schedule, full matrix by practitioner level
and service location. Code 97153 by a U5 practitioner in the home is
$18.69 per 15 minute unit, so $74.76 an hour. 120 rate rows parsed from
the state PDF.

**North Carolina**: the citable sheet lists 97153 at $18.09 per unit but
carries a 2019 effective date, and NC moved these schedules to a portal in
November 2022. Recorded as a base with the currency caveat attached, not
as the live rate.

**New Jersey**: no reachable published rate. The Division of Medical
Assistance and Health Services is the authority and its site publishes
provider resources and service manuals but no adaptive behavior fee
schedule. Flagged, not estimated. The widget refuses to print a New Jersey
Medicaid rate and says why.

The validator caught this honestly: the first New Jersey draft cited
`njmmis.com`, which is a `.com` and therefore not a primary source under
our own rule. It failed the gate and was repointed at the verified
`nj.gov` authority.

## Gates added

- **`check_rate`**: a machine-readable `rate_per_unit` must appear in the
  prose it is paired with and must name its CPT code. Stops the widget and
  the page drifting apart.
- **`check_cap`**: same for `cap_usd`, plus a mandatory `cap_status`.
  Every state's cap has a catch, and a widget that shows the ceiling
  without the catch is worse than one that shows nothing.
- **Generator quote extractor fixed again**: it matched only values
  immediately followed by `source_url`. The cost facts put `rate_per_unit`
  in between, so a quoted rate would have passed unchecked.
- **Widget build gate**: rejects any currency literal in the emitted JS
  that is not a known cap. This caught Georgia's superseded `$30,000`
  riding along in an unused field.

## Verified in a browser

Chromium at 390px, served from a local path matching the production URL:

- arithmetic correct: 30 hours at $120 renders $187,200, and the gap over
  the North Carolina cap renders $147,200
- New Jersey on Medicaid refuses to print a rate
- rate precision preserved: $74.76 an hour, not a rounded $75
- no console errors

## The one step left

Registered site scripts only reach the live site on a **full site
publish**. The page is live and correct now, showing a graceful fallback
paragraph in place of the calculator, but the script will not execute
until the site is published.

A full site publish pushes any other staged Designer changes live too, so
it is not something to do unilaterally. Confirm nothing else is staged,
then publish.

## Consolidation status

The page is written to absorb three others. The redirects are **not** in
place, and until they are, nothing should be unpublished:

```
/post/how-much-is-aba-therapy-with-insurance  ->  /post/cost-of-aba-therapy-for-autism
/post/average-cost-of-autism-treatment        ->  /post/cost-of-aba-therapy-for-autism
/post/autism-treatment-expenses               ->  /post/cost-of-aba-therapy-for-autism
```

Webflow 301s are UI-only (Site Settings, Publishing). There is no
redirects endpoint in the Data API surface available here.

`/post/how-much-autism-evaluation-cost` is deliberately **excluded**: the
cost of diagnosis is a separate intent from the cost of therapy.

## Incidental fix

The old body carried an unsourced "$120 per hour" figure and the three
unverified boilerplate claims (90%+ retention, no onboarding waitlist, six
weeks). Replacing it removed all four from this page. They remain on the
other pages flagged in the outstanding backlog.
