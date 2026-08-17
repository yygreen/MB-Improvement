# Settling the North Carolina overlap (2026-08-11)

**Decision: absorb. Rewrite `/post/is-aba-therapy-covered-by-insurance-north-carolina`
in place as the North Carolina funding guide. Keep the URL. No redirect.**

This is the opposite of the New Jersey decision, and deliberately so.

## Why New Jersey split and North Carolina does not

`/post/medicaid-and-aba-coverage-in-nj` answers a different question from
the NJ guide. It is an operational walkthrough of one system: get the
prescription, assemble the prior authorization packet, expect this many
hours. The guide is a map of four systems. Two pages, two intents, both
worth keeping.

`/post/is-aba-therapy-covered-by-insurance-north-carolina` is not that.
It is already the map, and its own opening says so:

> "Three different rules sit on top of each other, and which one applies
> depends on your plan. SB 676 governs many private plans. Medicaid covers
> it through age 20. The State Health Plan covers it for state employees
> and teachers."

That is the North Carolina guide's outline. It even leads with the
self-funded question the same way the NJ guide does: "The first question
to ask your plan: 'Is this a fully insured NC plan governed by SB 676, or
a self-funded plan?' The answer changes everything."

Writing a second page on that would be building the competitor by hand.

## Why in place rather than a new URL plus a redirect

The slug matches the query almost word for word, the page has age, and a
redirect always loses something. Rewriting in place keeps every signal and
removes the overlap in one move.

Accepted cost: the two guides will not share a naming pattern. New Jersey
is at `aba-therapy-funding-new-jersey`, North Carolina stays at
`is-aba-therapy-covered-by-insurance-north-carolina`. URL equity beats
tidiness.

## What the rewrite keeps

The existing post is better than its word count suggested and several
things in it should survive:

- The three-bucket framing, which is genuinely the right structure
- The plan-type comparison table
- The observation that NC licenses behavior analysts, which narrows the
  in-network panel, and the practical advice to ask about single case
  agreements. This is first-party knowledge the dataset cannot supply.
- The point that most denials are "not in this format" rather than "never"

## What the rewrite must fix

1. **The regulator is named wrong.** The post says "NCDHHS oversees
   compliance with the law" and, later, that families approaching the cap
   should turn to NCDHHS. The mandate sits in Chapter 58, the insurance
   chapter, and the appeal route runs through Smart NC inside the
   **Department of Insurance**. The post contradicts itself, having
   already said plans are "regulated by the NC Department of Insurance."
   A parent following the NCDHHS instruction calls the wrong agency.
2. **No appeal deadline anywhere.** The appeals section explains the flow
   but never says 120 days, never names Smart NC, never mentions the
   72-hour expedited route or that it is free. Deadlines are the part that
   loses cases.
3. **The order requirement is missing.** N.C.G.S. 58-3-192 requires
   treatment "ordered by a licensed physician or licensed psychologist."
   That is a step a family has to take and the page omits it.
4. **The $40,000 cap is treated as live.** The post does note it is
   CPI-adjusted and "has crept upward," which is better than most, but it
   still frames $40,000 as the number. Per the dataset flag, describe the
   mechanism and tell families to ask their insurer.
5. **Unverified claim to check before it survives the rewrite:** "In July
   2021, NCDHHS expanded its behavioral health offerings to include
   research-based behavioral health treatment for autism spectrum
   disorder for individuals age 21 and over." Not yet confirmed against a
   primary source. Verify or cut.
6. **Legacy link** to `/areas-we-serve/aba-therapy-in-north-carolina`,
   which 301s.
7. **Stray reference to the NJ Medicaid post** as a cross-state comparison.
   Repoint at the NJ funding guide once both exist.

## Sequencing

The dataset for North Carolina is already green at 37 facts. The rewrite
is copy work against `data/funding/north-carolina.json`, using the same
generator and gates as the New Jersey guide, plus the two figures rebuilt
with NC values.
