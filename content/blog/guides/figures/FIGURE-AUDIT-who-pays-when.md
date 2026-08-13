# Figure audit: "Who pays, and until when" (2026-08-13)

Triggered by a direct question about the Georgia chart. The answer turned out
to be "every band is factually right, but one of them was right by luck."

## What was wrong

Four of the five band endpoints were derived from an asserted dataset string.
One was not.

| Band | Ends | Was asserted against |
| --- | --- | --- |
| Babies Can't Wait | 3 | "birth to three years of age" |
| Ava's Law | 21 | "20 years of age or under" |
| Georgia Medicaid | 21 | "under the age of 21" |
| Katie Beckett | 19 | "18 or under" |
| **School district, IEP** | **22** | **nothing** |

`data/funding/georgia.json` had a `school_services` block carrying only the
*start* of the obligation (the third birthday). There was no age-out fact in
it at all. The 22 was typed straight into the geometry, and the only
assertion covering it was:

    assert BANDS[1][3] > CLIFF

which 21.1, or 40, would also have passed.

Two further problems followed from the same place:

- **The chart said school continues and never said until when.** The last
  tick was 21 and the band ran past the marker to an unlabelled edge. The
  entire point of the figure is the contrast at 21, and the one band that
  survives it had an unreadable endpoint. Katie Beckett's 19 had no tick
  either; the nearest was 18, which is the inclusive age, not the edge.
- **The diploma exit was missing**, and that is the one that matters to a
  parent planning around the cliff.

## What the sources actually say

**Georgia SBOE Rule 160-4-7-.02(1)(a):** "A free appropriate public education
(FAPE) must be available to all children residing in the State between the
ages of 3 and 21, inclusive."

**Rule 160-4-7-.02(1)(b)** confirms the far edge: it sets out what an LEA must
do for a student "receiving services upon reaching age 22", and requires the
LEA to notify a student who remains after the 22nd birthday that "although
services will continue, no individual entitlement to FAPE or other rights
under IDEA are afforded the adult student."

So 22 was correct.

**34 CFR 300.102(a)(3)(i):** the FAPE obligation does not apply to "Children
with disabilities who have graduated from high school with a regular high
school diploma." **300.102(a)(3)(iv)** defines that narrowly as "the standard
high school diploma awarded to the preponderance of students in the State
that is fully aligned with State standards, or a higher diploma", and
excludes a GED, a certificate of completion, a certificate of attendance or
a similar lesser credential.

The diploma exit was pinned to the federal rule rather than to Georgia's
Chapter 160-4-7 on purpose. Two attempts to read the Georgia subsection back
returned the graduation provision tangled up with 160-4-7-.02(2)(a), which is
a **LIMITATION for incarcerated students aged 18 to 21**. Citing that as the
general diploma rule would have been a worse error than the one being fixed,
so the citation went to the federal regulation, which is unambiguous and is
the controlling floor.

## What changed

**Dataset**, two new gated facts (37 facts to 39, all six datasets still PASS):
`school_services.age_out` and `school_services.diploma_exit`.

**Generator.** Every right edge is now derived from dataset prose rather than
typed. `edge()` regexes the age out of the sourced value and applies the
offset that turns an inclusive age into an exclusive edge, so "20 years of
age or under" becomes 21. A dataset correction now moves the figure or breaks
the build, instead of the chart quietly disagreeing with the guide printed
beside it.

New gate: every band edge must be readable, either a tick or the marked cliff
year. Ticks changed from `0,3,5,10,15,18,21` to `0,3,5,10,15,19,22`. 21 could
not stay a tick because at 900px the plot gives about 22px per year against a
25px label, so 21 and 22 would collide; the cliff year moved into the marker
label instead, which now reads "Insurance and Medicaid both stop at 21".

New caveat line under the chart, with both numbers interpolated from the
bands so they cannot drift:

> **Two of these end sooner than the bar suggests.** The Katie Beckett route
> ends at 19, before the line. School services end when a student graduates
> with a regular high school diploma, which for many is well before 22. A
> GED, a certificate of completion or a certificate of attendance does not
> end them.

## Verification

Geometry re-derived independently from the emitted HTML, parsing the rendered
percentages back into years rather than trusting the generator's own
assertions. All five bands match. All four distinct edges (3, 19, 21, 22)
are readable.

Negative tests, both fire:

- corrupt the dataset to "ages of 3 and 25, inclusive" and the build fails on
  the changed quote *and* on the unreadable edge at 26
- delete the age range from the value and the build fails because the edge
  cannot be derived at all

## Not fixed: New Jersey and North Carolina carry the same defect

`build-nj-figures.py` and `build-nc-figures.py` both hardcode the school band
at `22.0`, and neither `data/funding/new-jersey.json` nor
`data/funding/north-carolina.json` has a `school_services` age-out field to
check it against. Both stop their ticks at 21, so the school endpoint is
unreadable there too, and neither carries the diploma caveat.

Their bands are drawn with `open_ended=True`, which only rounds the right cap
differently. That is a visual hint that the band continues, not a labelled
endpoint, so it is milder than Georgia's hard stop at an unmarked 22. It is
still the same class of defect on two live pages.

Fixing them needs each state's IDEA age-out verified from its own primary
source rather than assumed from Georgia's, since states may limit FAPE for
ages 18 to 21 where it conflicts with state law. Not guessed here.

## The lesson

The gate that existed checked a *relationship* between two numbers (school
outlasts the cliff) rather than the *provenance* of either. A relationship
gate passes for an entire family of wrong values. Assert where a number came
from, not just how it compares to another one.
