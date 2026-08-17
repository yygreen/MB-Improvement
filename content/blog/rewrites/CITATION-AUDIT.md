# Citation audit: three blog rewrites

Every source in the three drafts was checked against the primary record.
Verdicts below are what the paper actually says, not what the draft says it says.

## Verified exactly as written

| Claim in draft | Source | Verdict |
|---|---|---|
| 1,256,407 children; OR 0.99 (0.92-1.06); MMR 0.84; thimerosal 1.00; mercury 1.00 | Taylor et al., Vaccine 2014, PMID 24814559 | CONFIRMED, every figure |
| 2,001,631 children, 22,156 autistic, ~80% heritability, maternal effects 0.4-1.6% | Bai et al., JAMA Psychiatry 2019, PMID 31314057 | CONFIRMED, every figure (heritability CI 73.2-85.5%) |
| Cochrane: one study only, methodological limits, "risks ... outweigh proven benefits", hypocalcaemia / renal impairment / death | James et al., Cochrane 2015, PMID 26114777 | CONFIRMED, including the risk-benefit wording |
| DAN registry discontinued 2011 | Autism Research Institute | CONFIRMED (January 2011) |
| Five-year-old died during chelation, 2005 | Abubakar Tariq Nadama, Aug 2005, Portersville PA | CONFIRMED |
| Eye contact declines 2-6 months in infants later diagnosed | Jones & Klin, Nature 2013, 504(7480):427-31 | CONFIRMED. Note the paper's point is that eye-looking STARTS at normative levels then declines, which the draft states correctly |
| Majority of Amish accept some or all vaccines | 2011 Ohio settlement study | CONFIRMED: 85% accepted some, 68% all children had at least one |
| Autism genes discovered in Amish/Mennonite families | Strauss et al., NEJM 2006 (CNTNAP2) | CONFIRMED |

## Wrong, or overstated, and must be fixed

### 1. Fraguas 2019 is selectively quoted  (`what-is-defeat-autism-now`)

Draft: "concluded the evidence 'does not support' nutritional interventions as an
autism treatment."

Actual conclusion: "does not support NONSPECIFIC dietary interventions as treatment
of ASD BUT SUGGESTS A POTENTIAL ROLE FOR SOME SPECIFIC DIETARY INTERVENTIONS in the
management of some symptoms." Omega-3 and vitamin supplementation showed modest
benefit, mean effect size 0.31.

Dropping "nonspecific" and the second clause reverses the paper's nuance. On a page
whose whole argument is "follow the evidence", misquoting the evidence is the one
mistake that cannot ship.

### 2. "every randomized trial" overstates Keller 2021  (`what-is-defeat-autism-now`)

It is a systematic review and meta-analysis of SIX RCTs. Findings hold (no effect on
core symptoms, SMD -0.31, CI -0.89 to 0.27), and the GI caveat is correctly hedged as
"possible" (RR 2.33, CI 0.69-7.90, crosses 1). Just name the number.

### 3. The Amish prevalence claim is false as written  (`do-amish-kids-get-autism`)

Draft: "Screening research in Amish communities in PENNSYLVANIA AND OHIO identified
autistic children at rates IN THE SAME RANGE AS OTHER POPULATIONS once CULTURALLY
ADAPTED screening was used."

The actual study (1,899 children, IMFAR 2010) found:
  - rate 1 in 271, against 1 in 91 in the general US population at the time.
    That is roughly a third, not "the same range".
  - communities were Holmes County OHIO and Elkhart-Lagrange INDIANA, not Pennsylvania.
  - the instruments (SCQ, DSM-IV-TR checklist) were NOT culturally adapted. That is
    precisely why researchers call it an undercount, which the draft's very next
    bullet says.

Three errors in one sentence, and the paragraph contradicts itself. The conclusion
still holds (autism exists among the Amish; nothing shows they are protected), but a
debunk article that misstates its own evidence hands the myth back its credibility.

### 4. The DAN draft misdescribes what it replaces

Its front matter says it replaces "neutral/positive framing of chelation". The live
page already says chelation "lacks scientific backing for autism and can pose serious
risks, including death in documented cases" and "is not recommended by mainstream
medicine". The rewrite is still stronger, but the stated premise is not accurate.

### 5. Character counts in the front matter are wrong

| file | field | claimed | actual |
|---|---|---|---|
| amish | SEO title | 49 | 47 |
| amish | meta description | 147 | 158 |
| neglect | meta description | 150 | 156 |
| DAN | SEO title | 58 | 55 |

### 6. Em dashes breach the copy gate

17 (amish), 25 (neglect), 23 (DAN). Removed in the corrected drafts.

## What the live pages actually say

`does-emotional-neglect-cause-autism` states THREE SEPARATE TIMES that "children who
experience emotional neglect are 2.5 times more likely to develop autism". No source
is given beyond a footnote marker. This is the refrigerator-mother myth restated as a
statistic, published on a BCBA-owned provider's site, currently ranking at position
7.0. Replacing it is a correction, not an optimisation.

`what-is-defeat-autism-now` is mixed: it warns clearly about chelation but presents
the protocol's goals and "detox methods" in neutral feature tables.

`do-amish-kids-get-autism` is directionally correct already. It buries the answer, but
it is not wrong, and it is the site's fourth-biggest page by clicks.

---

# Second pass: the five "unsupported" articles

All five checked against the primary literature. Traffic is 28-day GSC.

| page | traffic | verdict |
|---|---|---|
| `camel-milk-for-autism` | none in top 100 | REWRITE (safety) |
| `vitamin-d-and-autism` | none in top 100 | REWRITE (safety, dosing) |
| `autism-and-gluten-free-casein-free-gfcf-diet` | none in top 100 | REWRITE |
| `dairy-and-autism` | 30 clicks, pos 8.4 | REORGANISE |
| `can-emfs-cause-autism` | 23 clicks, pos 7.2 | REORGANISE |

None of the five earns meaningful traffic, so all five can be changed without risk.

## camel-milk-for-autism

Live page: "now being supported by a small body of scientific evidence"; an Egyptian
study where "about 58% of participants showed improvement"; a single anecdote of a
child with "overnight improvement" after "one half cup of RAW camel milk daily";
and an extension of the claims to Parkinson's and Alzheimer's.

What the evidence says. Kandeel et al., Open Veterinary Journal 2024, pooled ALL FIVE
randomised trials, 299 children:

    CARS score, camel milk vs control:  MD -0.75, 95% CI -1.97 to 0.47, p = 0.23
    raw milk subgroup:                  p = 0.18
    boiled milk subgroup:               p = 0.49

No significant difference on any analysis. Four of the five trials carried "some
concern" for risk of bias. A separate 2022 camel-milk meta-analysis has been RETRACTED,
which matters because confident online summaries often rest on it.

SAFETY, and the live page has none of this. The advocacy specifically recommends RAW
milk. CDC advises against drinking raw camel milk (MERS-CoV). Brucellosis is the better
documented risk: commercially sold camel milk carrying Brucella melitensis has caused
traced outbreaks, and daily raw consumption is associated with seropositivity.

## vitamin-d-and-autism

The most urgent of the five, because it publishes doses.

Live page: "vitamin D supplementation during pregnancy (5000 IU/day) and during infancy
and early childhood (1000 IU/day) significantly reduced the expected incidence of autism
in mothers who already had one autistic child from 20% to 5%."

    The tolerable upper intake level for adults, INCLUDING PREGNANCY, is 4,000 IU/day.
    The page published 5,000. For infants under six months the UL is 1,000 IU/day, so
    the infant figure sat at the ceiling.

The source is Stubbs et al. 2016: 19 women, open label, NO CONTROL GROUP, no blinding,
published in Medical Hypotheses. The 20% comparator is a historical literature figure,
not a concurrent control. One diagnosis in 19 children; a single case either way moves
the headline by more than five points.

Also presented as evidence: "two open-label trials ... improved core symptoms in about
75%". Open label means no placebo and no blinding.

NOTE this one is not a pure debunk. The observational association is real: a
meta-analysis of case-control studies does find lower vitamin D in autistic children.
The rewrite separates three questions the live page merges: is the level lower (yes),
does that mean low vitamin D causes autism (unproven), does supplementing treat or
prevent autism (not supported).

## autism-and-gluten-free-casein-free-gfcf-diet

Live page: "Research supports these claims to some extent, suggesting that avoiding
gluten and casein might reduce intestinal permeability, commonly known as 'leaky gut'",
and "a meta-analysis of randomized controlled trials has indicated some potential
benefits".

Keller et al., Nutrients 2021, six RCTs: no effect on clinician-reported core symptoms,
SMD -0.31 (95% CI -0.89 to 0.27), plus possible GI adverse effects (RR 2.33, CI 0.69 to
7.90, so uncertain rather than established), weight loss and night waking.

## dairy-and-autism

The mildest of the five and correctly hedged throughout, so it is reorganised rather
than replaced. Two problems: it blurs a real medical question (allergy or intolerance,
worth diagnosing) with a discredited one (casein elimination as autism treatment), and
its sources are unnamed, e.g. "a study published in the Journal of Autism and
Developmental Disorders" with no author or year. Diet-as-treatment now lives on the
GFCF page and this one links to it.

## can-emfs-cause-autism

The strongest of the five. It already concludes research "has not provided consistent
support for this hypothesis". Its conclusion is not changed. Three structural fixes:

  - the answer arrived about 500 words in; it now leads
  - "varying results" and "ongoing debates in the scientific community" implied a live
    controversy. There is no body of epidemiological evidence on EMFs and autism to be
    mixed about. "Essentially no research finding a link" and "the research is mixed"
    sound similar and mean different things
  - the title asked a question the SERP never answered

## Cross-cutting

All five carry the byline "Mastermind Behavior Clinical Team". The copy gate forbids
attributing posts to named BCBAs, and no BCBA is named, so the letter of the rule holds.
The spirit does not: a clinical byline on pages recommending raw camel milk and
supra-upper-limit vitamin D doses lends clinical authority to claims the clinical team
would not make. Worth a decision separately from these rewrites.
