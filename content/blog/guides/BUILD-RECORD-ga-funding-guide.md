# Georgia funding guide: build record

**Shipped 12 August 2026.** Live at
`https://www.mastermindbehavior.com/post/aba-therapy-funding-georgia`

Third and last of the three state funding guides. New URL, per
`OVERLAP-DECISION-georgia.md`.

## What shipped

| | |
|---|---|
| Collection item | `6a7c8d78e54812e5af77f596` (Blog Posts `6627fd62e242d50407cfe157`) |
| Body | 21,612 chars, ~3,140 words |
| Dataset | `data/funding/georgia.json`, 37 facts, gate green |
| Quotes gated against dataset | 36 |
| Internal links | 11, of which 8 sit above the closing section |
| Figures | 1 (`ga-who-pays-when.webp`, asset `6a7c8beca821f36d7ab16b85`) |
| Title | Who Pays for ABA Therapy in Georgia? |
| Byline | Mastermind Behavior Clinical Team `6a2e763ca589b9cdd033a53b` |

## Verification

Live page fetched after publish and compared against the generated source:

- tag-stripped text identical, 19,293 chars both sides
- href list identical, 11 links, same order
- h2 list identical
- figure renders from the CMS-space URL, alt non-empty, width 600
- no em dash, no `RBT`, no clinic or center language
- phone tokens are the four state and non-profit lines only: 678-248-7449,
  800.229.2038, 404.656.2070, 800.656.2298

## What this page says that no competing page says

**SB 118 moved the medical necessity determination to the covering
entity.** The statute now reads that coverage is required "when it is
determined by the covering entity that the treatment is medically
necessary health care according to established criteria", with the
physician or psychologist required to demonstrate ongoing necessity at
least annually. Every summary we found treats the clinician's
recommendation as decisive. It is not, and the practical consequences are
real: write treatment plans to the insurer's published criteria, ask for
those criteria in writing, and diary the annual redetermination.

**Katie Beckett is an eligibility route, not a service package.** It
"permits the state to ignore family income for certain children who are
disabled", which is the single most useful fact on the page for a family
over the Medicaid income line, and it is the fact least likely to have
been mentioned to them.

**Babies Can't Wait providers cannot balance bill.** Where insurance pays
any portion, providers "cannot bill families for co-pays, deductibles,
travel or any other fees", and where Medicaid pays any portion "the
provider must consider that as payment in full".

## Flagged, not softened

The independent review filing deadline is **unresolved from primary
sources**. Chapter 120-2-111 as published requires the internal grievance
to be exhausted and says where to send the request, but the chapter text
we checked states no filing deadline. The page says so in our own voice
and tells families to treat the date on their denial letter as
controlling and confirm with OCI. No number was invented.

Same treatment for Katie Beckett processing times, and for which Georgia
Families care management organizations administer the benefit: both
unsourced, both said to be unsourced.

## Generator changes this build

- **Quote-pairing bug fixed.** The gate extracted quotes with a
  `"([^"]{12,})"` regex, which silently skips a short quoted word such as
  `"six"` and then pairs its closing mark with the next quote's opening
  one. That mispairs every quote after it and invents spans that were
  never quoted. Marks are now paired in document order first and filtered
  by length second, with an error on an odd number of marks. New Jersey
  and North Carolina were rebuilt under the fixed gate; NC's md5 is
  unchanged from what is live.
- Georgia's `REQUIRED_BY_STATE` entry went from 3 facts to 13.
- Georgia service pages, `/financial-aid-resources`, and both sibling
  guides added to the link allowlist.
- Four Georgia agency phone numbers added to the phone allowlist.

## Figure

`tools/blog/build-ga-figures.py`. Bands computed from the dataset ages,
each edge re-derived from the published percentage and asserted. Six
labelled claims checked against the dataset field they came from. The
marker sits on the point of the figure: Ava's Law and Georgia Medicaid
both end at 21 while the school district continues, and the script
asserts that relationship rather than trusting the numbers as typed.

The marker label lives in a reserved 62px lane above the plot, so it
cannot land on a band, and its horizontal extent is computed and gated
against the canvas edges. Rendered at 900px and measured in the browser:
**0 collisions** with bars, row labels or axis ticks.

## Known gaps

- The hero is the New Jersey guide's photograph. State-neutral (a parent
  at a kitchen table with paperwork) but shared between two posts, and
  Webflow content-addresses by MD5 so the file keeps its New Jersey name.
  A Georgia-specific hero would fix both.
- The two legacy Georgia posts still carry competing coverage sections.
  See `OVERLAP-DECISION-georgia.md` for the two required edits.
- The New Jersey guide does not yet link to either sibling guide.
