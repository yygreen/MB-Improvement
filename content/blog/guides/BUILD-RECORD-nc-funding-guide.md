# Build record: North Carolina funding guide (2026-08-11)

Written to replace the body at
`/post/is-aba-therapy-covered-by-insurance-north-carolina`. Absorb, not
redirect; reasoning in `OVERLAP-DECISION-north-carolina.md`.

**Not yet shipped.** Everything below is built, gated and waiting on the
Webflow connection, which began returning "the site cannot be found" on
every endpoint partway through this session.

    guide copy      18,252 chars, all gates green except the figure URL
    quotes verified 42, every one matched verbatim against the dataset
    figure          built, 900px canvas, 0 label collisions, no overflow
    figure asset    NOT uploaded, Webflow returned 404 on create_asset
    dataset         37 facts green, plus one fact added this session

## What the guide fixes in the page it replaces

1. The old body named NCDHHS as overseeing compliance and told families
   near the cap to go there. The mandate is in Chapter 58 and appeals run
   through Smart NC inside the Department of Insurance.
2. The old appeals section had no deadline in it. The guide leads with
   120 days, names Smart NC, gives the three-day expedited route, says it
   is free, and lists who it does not cover.
3. The statute's requirement that treatment be "ordered by a licensed
   physician or licensed psychologist" was missing entirely. It is now the
   first thing under what the law requires, because it is the step a
   family has to take before anything else happens.
4. $40,000 was presented as the live figure. The guide explains the CPI
   indexing clause, says the current ceiling is higher, and tells families
   to ask for the indexed maximum in writing rather than printing a number
   nobody can source.

## What it keeps

The three-bucket framing, the note that most first-year programs sit
inside the annual maximum, and the local knowledge that North Carolina
licenses behavior analysts, which narrows insurer panels and makes single
case agreements more available than families expect. That last one is
first-party and no dataset could have produced it.

## One claim verified rather than cut

The old page said NCDHHS expanded behavioral health to RB-BHT for people
over 21 in July 2021. It checks out: CMS approved it effective 1 July
2021 and Policy 8F was updated. Added to the dataset with its source, and
it is now a highlight of the guide, because most state Medicaid autism
benefits stop at 21 and North Carolina's does not.

## Section deliberately left thin

The State Health Plan. The old page characterized its coverage; we have
not verified its current terms against a primary source, so the guide
says so and tells families to ask their plan in writing. A short honest
section beats a confident wrong one.

## Three generator defects this build exposed

Running a second state through the pipeline found all three:

1. **The required-facts list was hardcoded to New Jersey.** A North
   Carolina guide was being checked for `$36,000` and `February 9, 2010`.
   Now keyed by `state_key`, with its own list per state.
2. **The quote extractor skipped short quotes and mispaired everything
   after them.** The minimum was 25 characters, so `"within three days"`
   was skipped and the scanner paired its closing quote with the next
   opening one, inventing a phantom quote that then failed verification.
   Threshold lowered to 12, which catches the short quotes and restores
   correct pairing.
3. **The figure gate required every declared figure to be placed**, which
   breaks as soon as `figures.json` serves more than one guide. Now
   requires only that this guide places at least one.

The New Jersey guide was rebuilt under all three and still passes.

## To finish

Upload `figures/nc-who-pays-when.webp`, set its CDN URL in
`figures/figures.json`, regenerate, then replace the body at the existing
URL and publish. Nothing else outstanding.
