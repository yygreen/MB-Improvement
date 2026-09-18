# Fix spec: wrong effective date on the NJ Medicaid post

**Status: specified, not executed.** Needs the REST path, not the MCP path.
See "Why this cannot go through the CMS tool" below.

**Item:** `67591b97ca6a22e4fa4b05ff`
**URL:** `/post/medicaid-and-aba-coverage-in-nj`
**Collection:** Blog Posts `6627fd62e242d50407cfe157`
**Field:** `post-body`

## The error

The post states, twice, that NJ Medicaid has covered ABA "since April 2020"
and "effective April 2020", each citing reference [1], which points at a
generic NJ FamilyCare landing page that does not state a date at all.

April 2020 is neither of the two real dates.

## What the primary source says

From `data/funding/new-jersey.json`, `medicaid.aba_coverage_basis`, sourced
to the CMS-approved State Plan Amendment:

> SPA NJ-19-0003 was approved September 18, 2020 with an effective date of
> January 1, 2019.

Source: `https://www.medicaid.gov/medicaid/spa/downloads/NJ-19-0003.pdf`

So the benefit has existed since **1 January 2019**, roughly fifteen months
earlier than the page claims. A family reading this could reasonably
conclude they were not eligible for a period when they were, which matters
for retroactive eligibility.

## The three replacements

Each is an exact string, expected to occur exactly once. Assert the count
before writing, and re-read the field afterwards to confirm.

**1.** Replace:

    has covered Applied Behavior Analysis (ABA) therapy for children under 21 with an autism diagnosis since April 2020

with:

    has covered Applied Behavior Analysis (ABA) therapy for children under 21 with an autism diagnosis since 1 January 2019, the effective date of State Plan Amendment NJ-19-0003, which CMS approved on 18 September 2020

**2.** Replace:

    in children under 21, effective April 2020

with:

    in children under 21, effective 1 January 2019 under State Plan Amendment NJ-19-0003

**3.** Repoint reference [1]. Replace:

    [1] New Jersey Department of Human Services, Division of Medical Assistance and Health Services. "NJ FamilyCare."

with:

    [1] CMS-approved New Jersey Medicaid State Plan Amendment NJ-19-0003, EPSDT Autism Benefit, approved 18 September 2020 with an effective date of 1 January 2019.

and change the two `href` values on the inline [1] links from
`https://www.nj.gov/humanservices/dmahs/clients/medicaid/` to
`https://www.medicaid.gov/medicaid/spa/downloads/NJ-19-0003.pdf`.

## Why this cannot go through the CMS tool

The body embeds the full insurance check widget: roughly 20KB of inline CSS
and JavaScript inside a `data-rt-embed-type` block. `update_collection_items`
replaces the whole field, so pushing a change through the MCP tool means
re-emitting that embed by hand.

That is the exact failure mode the house rule forbids. A single mistyped
character in 20KB of minified-ish CSS silently breaks a live, working
widget, and the damage would not be obvious from the diff.

The safe route is the one used for the phone sweep: fetch the field over
REST, do the three replacements in code with an assertion that each matches
exactly once, PATCH, then re-read and diff to confirm nothing outside the
replaced spans changed.

## While in there

The same body carries the three unverified boilerplate claims:

> With a 90%+ staff retention rate and no onboarding waitlist, most
> families begin direct services within six weeks of their initial
> assessment

These are still awaiting a decision from Adina or Raizy: confirm with a
source and a date, give hedged wording, or pull. Do not silently soften.

## Also worth noting

The post links to `/areas-we-serve/aba-therapy-in-new-jersey`, which is the
legacy path that 301s. Repoint to `/aba-therapy-in-new-jersey` in the same
pass.
