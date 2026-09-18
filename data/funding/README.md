# State funding dataset

One dataset, four properties. The NJ/GA/NC funding and legislation guides, the
ABA cost calculator, the insurance mandate lookup widget, and the appeals
section of the appeals-toolkit satellite are all renders of the files in this
directory. Nothing downstream should hold its own copy of a coverage fact.

## Why it is built this way

These are not blog facts. A wrong citation on a health article is
embarrassing; a wrong dollar cap or appeal deadline costs a family money or
loses them a case. Two rules follow from that.

**Every fact carries its own source and its own date.** Not a page-level
bibliography, a per-field one. The unit is:

```json
{
  "value": "...",
  "source_url": "https://...",
  "source_type": "statute | regulation | medicaid_manual | doi_bulletin | agency_page | federal | waiver_document",
  "source_title": "...",
  "verified_on": "YYYY-MM-DD",
  "note": "optional, e.g. what the statute does NOT say"
}
```

**Facts expire.** Caps get amended, managed-care organizations change, waiver
waitlists move. `tools/funding/validate-funding.py` fails the build when any
fact is older than the max age (default 180 days) and warns from 75% of that.
Re-verification is a scheduled chore, not a one-time task.

## The field that matters most

`self_funded_exemption` is marked SAFETY-CRITICAL in the validator and the
build fails if it is empty. State autism mandates do not reach self-funded
ERISA plans, which cover a large share of employees at larger employers. A
lookup widget that tells such a family "your plan is required to cover ABA"
is worse than no widget. Every downstream property must branch on this before
it answers a coverage question.

## Source rules

Primary sources only: state legislature, state insurance department, state
Medicaid agency, state early-intervention program, federal (CMS, DOL/EBSA,
eCFR), and BACB for credentialing facts. The validator rejects any host that
is not `.gov`, `.us`, `.mil`, or an explicit allowlisted exception. Law
aggregators and advocacy sites are research leads, never sources.

Reachability was tested 2026-08-11: all NJ, GA, NC and federal sources above
respond. njfamilycare.org needs a browser user agent (403 to a bare curl), so
fetch it with Playwright or a UA header.

## Status

Skeletons only. Every `value` is `UNVERIFIED` and the validator fails by
design until a state has had a real evidence pass. Do not fill a value without
also filling its source and date, and do not fill either from memory.

Order of work: New Jersey, then Georgia, then North Carolina.
