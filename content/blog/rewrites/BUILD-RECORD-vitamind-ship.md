# Ship record: vitamin-d-and-autism rewrite + 2 custom graphics (2026-08-11)

The most urgent of the seven. Live item 665f06a6fe948fefa9ab4258, slug kept.

## What the live page actually carried (worse than the draft recorded)

The draft flagged 5,000 IU/day in pregnancy and 1,000 IU/day in infancy. On
inspection the live page also published, in a table headed "Recommended
Vitamin D Dosages":
- a weight-based TREATMENT dose of 300 IU/kg/day for an autistic child
  (a 20 kg six-year-old = 6,000 IU/day, twice the 3,000 IU ceiling for ages 4-8)
- 150 IU/kg/day for infants and young children
- advice to re-check 25(OH)D every 3 months
- "high-dose vitamin D improved core symptoms in about 75% of autistic children"

All of it is gone. The rewrite carries no dose as advice; the only IU figures
that remain are the recommended amounts, the ceilings, the trial doses, and
the old page's own figures shown in order to retire them.

## Evidence base (7 PubMed records + NIH ODS, all verified today)

New since the draft was written, and decisive:
- Aagaard 2024 AJCN (38072183): high-dose vitamin D3 randomized in pregnancy,
  children assessed at 10. "High-dose vitamin D3 supplementation was not
  associated with risk of autism or ADHD." Higher PRE-trial maternal 25(OH)D
  was associated with lower risk - the same paper holds both the correlation
  and the null experiment, which is the article's whole lesson.
- Sandboge 2026 JCPP (41486975), VIDI trial: 366 children, 1,200 vs 400 IU
  daily from 2 weeks to 2 years, ASSQ at 6-8 years. Adjusted mean difference
  -0.002 (95% CI -0.20 to 0.20). Value taken from the PMC full text
  (PMC13265620); the abstract carries no number.
- Bandini 2026 EJCAP (42234108): 15 observational studies, RR 0.91 (0.87-0.96).
- Li 2022 Nutr Neurosci (32893747): 5 RCTs / 349 children; hyperactivity
  improved (MD -3.20), core symptoms did not.
- Song 2020 (32329301): a POSITIVE meta-analysis, included deliberately and
  weighed lower (3 studies, 203 children) with the reasoning stated. Omitting
  the disagreeing study is the habit that produced the page being replaced.
- Stubbs 2016 Medical Hypotheses (26880644): the origin of every dose on the
  old page. 19 women, open label, no control, no blinding; quoted from the
  authors' own limitations rather than attacked.
- Bai 2019 (31314057) for causal context; NIH ODS for RDA/UL values, fetched
  and parsed rather than recalled (pregnancy RDA 600 IU, UL 4,000 IU; infant
  0-6 mo AI 400 IU, UL 1,000 IU; ages 4-8 UL 3,000 IU).

Aagaard has no PMC copy, so its randomized arm has no published CI available;
no numeric estimate for it appears in either graphic. Only figures that could
be cited exactly were drawn.

## The two custom graphics

Original designs, not redrawings of any paper's figure.

1. vitamin-d-dose-vs-upper-limit-inline.webp (md5
   b3c7d025acdf161cfb503f414e0c1381, asset 6a7ae6db51df9d5b47e85ae3) - two
   rows, pregnancy and infants under 6 months, each showing the recommended
   amount, the band below the ceiling, the ceiling itself, and where the old
   article's dose sat. The pregnancy dose renders beyond the ceiling line; the
   infant dose renders exactly on it.
2. vitamin-d-observation-vs-trial-inline.webp (md5
   5747e59ebe91dbab6992a6a4ac2fa704, asset 6a7ae6db7980f37222c7c95a) - two
   stacked panels: the observational pooled RR 0.91 (0.87-0.96) whose interval
   clears 1.0, above the randomized -0.002 (-0.20 to 0.20) whose interval
   straddles 0. Different measures on deliberately separate axes, stated in
   the caption, because the comparison being drawn is between conclusions and
   not between effect sizes.

Geometry gate recomputes every bar edge, whisker end, tick and reference line
from the published values through a single linear scale per axis and fails on
mismatch; it also asserts the observational interval clears the null line and
the trial interval crosses it, and that no unverified value (e.g. Aagaard's
absent CI) appears. Both charts byte-verified on the CDN after upload.

Deviation from the draft, deliberate: the draft said "no dose should appear on
this page at all". Graphic 1 does show doses, because a ceiling a parent can
check their own bottle against is protective, whereas the draft's rule was
aimed at doses presented as recommendations. Nothing in the article or the
graphics tells a reader what to take.

## Verification

Copy gates before write: no em/en dashes, no UK spellings, no phone numbers,
no imperative dosing phrasing, exactly 7 intended PubMed links and 3 internal
links, 8 references with DOIs, 2 figures with 3-20 word alt text, the
arithmetic in the weight-dose paragraph asserted (300 x 20 = 6,000 = 2 x 3,000),
counter-evidence present, balanced tags.

Live: 19/19 pass, including explicit checks that the 300 IU/kg and 150 IU/kg
doses, the dosage table, the 20%-to-5% framing and the 75% claim are all gone.

## Remaining

GFCF diet, dairy, EMF, Defeat Autism Now.
