# Site-wide phone number correction (2026-08-11)

Replaced a stale phone number, 732.507.9883, with the correct line,
732.813.7333, across the whole Blog Posts collection.

    CMS items scanned                350
    items carrying the stale number  152
    field affected                   post-body, in every case
    occurrences                      one per item
    live pages affected              149 (three of the 152 were unpublished)
    after the sweep                  0 in the CMS, 0 across all 607 live URLs

## How the number got there, and where it did not

Not from us. This repository's first commit is 30 July 2026; the sample
item checked was last edited 13 July 2026 and already carried it. A
`git log -S` on the string matches only four commits, and in each the
string appears solely as prose in a build record describing its removal
from a live page. It never existed as content in this repo.

The site chrome was always correct. The nav and the mobile call button
carry 732.813.7333. The stale number was baked into the closing
paragraph of individual article bodies, written at the time each post was
drafted, which is why nothing in the template could fix it.

That is also why the earlier sweeps looked so much smaller. The four
rewrites in August found and stripped it on the pages they were already
touching. Nobody scanned the rest of the collection until now.

## Scope was misjudged twice before it was measured

First reported as four pages, then six, because both counts came from
pages already under edit. The real figure only appeared after scanning
all 607 sitemap URLs. Worth remembering: a defect found while working on
a page says nothing about how many other pages have it.

## What the sweep did

Direct Webflow Data API v2, client token supplied for the session only,
never written to this repo and destroyed afterwards. For each item:
read the field, replace the number, gate, write, publish.

The gate rejects a write unless, after masking every phone-like token on
both sides, the remaining text is byte identical; the old number is gone;
and the count of correct numbers equals the old count plus any that were
already present.

## Two bugs the gates caught

**Transport errors were not retried.** The first pass retried HTTP status
codes but not connection resets, and died after roughly 111 items,
having patched them without publishing. The follow-up pass republished
every affected item rather than only the ones it had touched itself, so
the partial run did not leave anything stranded.

**The reverse-check false-positived on seven pages.** The original gate
verified a write by reversing the replacement and comparing. On the seven
pages that already contained the correct number alongside the stale one,
reversing turned those correct numbers into stale ones, so the comparison
failed and the write was refused. The gate was rewritten to mask phone
tokens on both sides instead of reversing. The seven were then written
one at a time with a read-back check confirming each before moving on.

The seven were the entire financing cluster plus autism-treatment-expenses,
that is, the highest commercial intent pages on the site. A looser gate
would have written them silently and a stricter reading of the failure
would have skipped them. Both would have been wrong.

## Still open, and not a copy problem

133 of the affected posts carry the same closing boilerplate:

- "90%+ staff retention rate"
- "no onboarding waitlist"
- "most families begin direct services within six weeks of their initial
  assessment"

The first two are factual claims about the business. The third reads as a
timeline promise. The same phrasing was reused in the twelve Tier 1
service pages built in this program, so it is live on our own new pages
as well as on the legacy posts. If any of it has drifted it needs a
decision from the client, and the correction should run as one scripted
pass rather than two sweeps.
