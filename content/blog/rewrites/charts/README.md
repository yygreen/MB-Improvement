# Branded evidence charts for does-emotional-neglect-cause-autism (2026-08-10)

Three house-style charts, palette validated (dataviz six checks, teal #009499
+ coral #c14a3f on white), rendered at 2x from heritability-charts.html:

1. autism-heritability-vs-environment-inline.webp - genetics 64-91% vs shared
   family environment 7-35% plus a third "Unique to one twin" row ~2-9%
   (Tick et al. 2016, JCPP, PMID 26709141)
2. twin-concordance-autism-inline.webp - identical 0.98 vs fraternal 0.53
   twin correlations (Tick et al. 2016)
3. autism-risk-genetic-relatedness-inline.webp - relative risk by relatedness,
   identical twin 153x to cousin 2.0x (Sandin et al. 2014, JAMA, PMID 24794370;
   an earlier revision of this file misattributed PMID 24196715, which is
   Jones & Klin 2013, Nature)

Amendments after review (this revision): fig1 gained the third row (gray
#9a9484) with legend key and a caption note that the three parts sum to 100%
within each model; fig2's fraternal small-text now reads "share about half of
the genes that vary, same home".

## Shipped 2026-08-10

Uploaded to the MasterMind Webflow site (6627fd62e242d50407cfe12d) after the
MCP connector was re-authorized; CDN byte-verified against these local files:

| file | md5 | asset id |
|---|---|---|
| autism-heritability-vs-environment-inline.webp | 78c83f4124cb411328e8763e473b4992 | 6a7a312d36c8b65f5fb5e728 |
| twin-concordance-autism-inline.webp | ba6526c041dcdc105cfebaf9042b0bb7 | 6a7a312de18736ddd008b5ff |
| autism-risk-genetic-relatedness-inline.webp | fe2e315c9fa90cc98aba285bf118a066 | 6a7a312dc165f7321b287b92 |

Wired into the live article (Blog Posts item 66e7ec0089e32577d87461a5, slug
does-emotional-neglect-cause-autism) as full-width rich-text figures with
descriptive alt text; on save Webflow re-ingested the images under the CMS
asset space (cfe155/6a7a3238... URLs), which is expected. See
../BUILD-RECORD-neglect-ship.md for the full ship record.

## Figure 4 added 2026-08-11

eye-contact-decline-infancy-inline.webp (md5 f67f0e63dc865fd2d4a9f742201a9585,
asset 6a7ade55a3b1758ceee45cc6): monthly rate of change in eye fixation across
months 2 to 6, +3.6%/month [95% CI 1.3 to 5.9] in infants not later diagnosed
vs -4.8%/month [95% CI -7.9 to -1.7] in infants later diagnosed. Diverging bars
from a zero baseline with 95% CI whiskers. Data: Jones & Klin 2013, Nature
(PMID 24196715), values read from the PMC full text (PMC4035120), not from the
abstract, which carries no numbers.

Chosen over three alternatives the client proposed from the source papers:
- Bai 2019 Figure 1 (pedigree / variance-component derivation): a methods
  diagram, not a result. Its useful content (maternal effect 0.4-1.6%, "no
  support for contribution from maternal effects") is already in the body text.
- CAST group-heritability-by-cutoff bars: a methodological robustness check,
  and NOT from our reference 2 as assumed. It is Colvert, Tick et al. 2015,
  JAMA Psychiatry (PMID 25738232), a UK twin study of 6,423 CAST pairs at mean
  age 7.9 - a different paper that shares an author with Tick 2016.
- Sibling-recurrence cumulative-probability curve (~13.5% by age 21 vs ~1%):
  source could NOT be confirmed as Sandin 2014; the values match neither
  Sandin's relative-risk framing, Risch 2014 (10.1% vs 0.52%), nor Gronborg
  2013. Not buildable under the no-unverified-data rule, and off-thesis: it
  answers "what is the risk for my next child", not "did I cause this".

Geometry gate: every bar edge and whisker end in fig4 is computed from the four
published statistics via a single linear scale (-10..+10 -> 0..100%); the gate
recomputes each position and fails on any mismatch. No trajectory or curve was
drawn, because the per-month fixation values are not in the accessible text.

## Vitamin D graphics added 2026-08-11

Built from vitamin-d-charts.html for /post/vitamin-d-and-autism. Two original
designs (no paper's own figure used as a template):

| file | md5 | asset id |
|---|---|---|
| vitamin-d-dose-vs-upper-limit-inline.webp | b3c7d025acdf161cfb503f414e0c1381 | 6a7ae6db51df9d5b47e85ae3 |
| vitamin-d-observation-vs-trial-inline.webp | 5747e59ebe91dbab6992a6a4ac2fa704 | 6a7ae6db7980f37222c7c95a |

Sources: NIH Office of Dietary Supplements (RDA/UL, fetched and parsed);
Bandini et al. 2026 EJCAP (RR 0.91, 0.87-0.96); Sandboge et al. 2026 JCPP
(-0.002, -0.20 to 0.20, from PMC13265620). See ../BUILD-RECORD-vitamind-ship.md.

### Mobile rebuild, same day

Measured on a 390px phone viewport: the article's content column is 358px, so
the original 1400px-wide charts rendered at 25.6% of their design size, putting
axis labels and credits at roughly 4px. Unreadable.

Rebuilt on a 900px canvas with the type scaled for that column (39.8% scale):
axis ticks 27px -> 10.7px effective, credit 26px -> 10.3px, row labels
34px -> 13.5px, titles 46px -> 18.3px. Structural changes: the left-hand label
column in the dose chart became a full-width label above each track, the
per-bar annotations moved into a readable sentence under each track, the
legend stacks vertically, and the panel results in the second chart are stated
as plain conclusions with the numbers in parentheses. Axis ticks got
white-space:nowrap after the last one wrapped and collided with the credit.

Geometry is byte-identical in intent: the gate recomputes every position from
the same published values and passed unchanged. Replacement assets:

| file | md5 | asset id |
|---|---|---|
| vitamin-d-dose-vs-upper-limit-m.webp | dede2473c202b1f45483ff35ea780d0d | 6a7aec07403eb5e5f03e17b6 |
| vitamin-d-observation-vs-trial-m.webp | 46f2e1dd1dc500a611fda5710d901d15 | 6a7aec07d5516e2a8c1756fe |

Live re-verified on a phone viewport: both at 358px, no horizontal page
overflow, screenshots legible.

NOTE for the four charts on /post/does-emotional-neglect-cause-autism: they are
still on the 1400px canvas and have the same mobile legibility problem. They
need the same treatment.

### Label fix + figure sizing (same day, after client review)

Two corrections:

1. In the observation panel, the "no difference" label had been right-aligned
   against the reference line, which put it on top of the confidence
   interval's right cap (label ran ~48.9-66.7%, whisker ends at 53.3%). Moved
   to the right of the reference line, matching the trial panel; now clear by
   13.4% of the axis. New asset: vitamin-d-observation-vs-trial-m2.webp
   (md5 12cc1a637d9ee29730d67abd0e0988eb, asset 6a7aed8f503626513621e67c).
   The dose chart was unchanged and its md5 is identical, so it was not
   re-uploaded.

2. Figures were set to w-richtext-align-fullwidth, which stretched them across
   the whole 821px text column on desktop. Changed to
   w-richtext-align-center with style="max-width:600px" on the figure and
   width="600" on the img. Verified live: 600px on desktop (col 821px, so
   clearly not full width) and 358px on mobile where the container caps it.
   Axis labels render 18.0px on desktop and 10.7px on a phone; zero horizontal
   page overflow at both sizes.
