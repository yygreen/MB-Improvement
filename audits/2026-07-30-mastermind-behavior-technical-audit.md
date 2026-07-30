# Mastermind Behavior — Technical SEO Audit

**Date:** 2026-07-30
**Scope:** mastermindbehavior.com (Webflow site `6627fd62e242d50407cfe12d`)
**Mode:** The audit itself (Tasks 1–4) was read-only — no Webflow writes, no publishes,
no CMS changes, no freeform code edits. Remediation began afterwards and is recorded in
the Change log at the end of this document; that work does write to Webflow and has been
published to the production domains.

---

## Method & confidence note

This site was audited with raw HTTP fetches (`curl`) plus static analysis of every
JavaScript asset the pages load. Every JSON-LD claim below distinguishes a
**server-rendered `<script type="application/ld+json">` tag** from the **bare string
`application/ld+json` appearing inside JavaScript**, and both were counted separately
on every page.

**Headless rendering was attempted and is unavailable in this environment.** Chromium
is installed, but all HTTPS egress from the browser process fails with
`net::ERR_CONNECTION_RESET` — including to `example.com`, with and without the agent
proxy, with and without `--no-sandbox`, and running the binary directly outside the
tool sandbox. Only Chromium's own plain-HTTP requests reach the proxy. `curl` from the
same host works fine, so this is a browser-specific egress restriction, not a site
problem.

To keep the client-side-injection question rigorous without a renderer, I substituted a
stronger static test: **fetch and scan every script the page loads.** A page can only
inject JSON-LD at runtime if some script on it contains the code to do so. All seven
JS assets loaded across the site were downloaded and scanned:

| Asset | Bytes | `ld+json` | `BlogPosting` | `schema.org` |
|---|---|---|---|---|
| CallRail `swap.js` (company 477025173) | 42,913 | 0 | 0 | 0 |
| Finsweet `cmsload.js` | 18,482 | 0 | 0 | 0 |
| `mbinsurancewidgettracker-1.0.0.js` | 1,382 | 0 | 0 | 0 |
| Webflow runtime `webflow.af831f90…js` | 177,337 | 0 | 0 | 0 |
| Webflow chunk `webflow.schunk…js` | 41,429 | 0 | 0 | 0 |
| Plausible `script.js` | 2,855 | 0 | 0 | 0 |
| Leadtrap `platform/script` | 41,465 | 0 | 0 | 0 |

The only `document.createElement('script')` call found anywhere in the site's inline
code is the Leadtrap chat-widget loader — not schema.

**Important correction to the working premise:** the brief stated that the 205
Areas We Serve city pages "inject BreadcrumbList at runtime and look schema-less to a
static fetch." **That is no longer true.** City pages now serve a complete, fully
server-rendered `@graph` (verified on 15 sampled pages — see Task 4). There is
currently **no page type on this site that injects schema client-side.** Every schema
finding below is therefore a server-rendered fact, directly observable in the HTML
source, and the missing-renderer limitation does not affect any verdict.

---

## Task 1 — BlogPosting schema on blog posts

### Verdict: **GENUINELY ABSENT.** Not staged, not client-injected, not present anywhere.

13 posts fetched: 10 randomly sampled (deterministic MD5-ordered sample of the 337
`/post/*` sitemap URLs) plus the three highest-traffic posts. Top-traffic posts were
identified from Semrush organic data rather than guessed — `/post/what-is-the-average-iq`
alone carries **72.19% of the domain's entire organic traffic** (36,509 est. monthly
visits, 3,001 ranking keywords).

| Post | `<script ld+json>` tags | bare `ld+json` string | `BlogPosting` | `schema.org` |
|---|---|---|---|---|
| what-is-the-average-iq *(#1 traffic — 36,509)* | 0 | 0 | 0 | 0 |
| vocal-stimming-in-autism *(#2 — 2,845)* | 0 | 0 | 0 | 0 |
| do-amish-kids-get-autism *(#3 — 2,815)* | 0 | 0 | 0 | 0 |
| can-emfs-cause-autism | 0 | 0 | 0 | 0 |
| early-signs-of-autism-in-babies-and-kids | 0 | 0 | 0 | 0 |
| history-and-timeline-of-autism | 0 | 0 | 0 | 0 |
| how-access-school-based-aba-therapy-in-georgia | 0 | 0 | 0 | 0 |
| how-georgia-laws-support-autism-services | 0 | 0 | 0 | 0 |
| how-to-create-an-effective-behavior-intervention-plan-bip | 0 | 0 | 0 | 0 |
| how-to-use-aba-therapy-to-improve-peer-interactions | 0 | 0 | 0 | 0 |
| the-benefits-of-sensory-play-for-developing-emotional-awareness-in-autism | 0 | 0 | 0 | 0 |
| the-importance-of-consistency-in-behavior-therapy-for-children-with-autism | 0 | 0 | 0 | 0 |
| the-role-of-humor-in-building-connections-with-children | 0 | 0 | 0 | 0 |

**Evidence this is real absence, not a fetch artifact.** The same fetches return
complete, well-formed `<head>` metadata on all 13 posts — `<title>`, `meta description`,
`rel=canonical`, and 5 Open Graph tags each. Example:

```html
<title>What Is the Average IQ?</title>
<link href="https://www.mastermindbehavior.com/post/what-is-the-average-iq" rel="canonical"/>
```

So the fetch retrieved the full document; the schema simply is not in it.

**Server-rendered vs client-injected, stated separately as required:**
- Server-rendered: **absent** — 0 `<script type="application/ld+json">` tags on all 13.
- Client-injected: **absent, and impossible** — the string `application/ld+json` appears
  0 times in the HTML *and* 0 times across all 7 JS assets. There is no code path on a
  post page capable of creating a JSON-LD node.
- Staging (`mastermindbehavior.webflow.io`): also 0 on all three top-traffic posts, so
  this is not schema staged-but-unpublished either.

### RETRACTED — "every post displays today's date as its publish date"

**This finding was a false positive and has been withdrawn. There is no date bug.**
The original claim — that all 13 sampled posts render a byline of "Published: Thu Jul 30
2026" — came from matching the string `Thu Jul 30 2026` in the page source. That string
is **not a rendered byline.** It is Webflow's own boilerplate comment, the first line of
every page it serves:

```html
<!-- Last Published: Thu Jul 30 2026 12:54:51 GMT+0000 (Coordinated Universal Time) -->
```

It is an HTML comment (invisible to users, not a date signal to search engines), it
carries the *site's* last publish timestamp rather than any post's date, and it is
byte-identical on every URL on the domain. Verified on `/`, `/contact`, `/bcba-team`,
`/areas-we-serve/perry`, and two posts — all five return the same comment, same
timestamp. The original grep had no way to distinguish it from page content.

**The byline dates are correct and vary per post.** They are bound to Webflow's built-in
`Created On` item field, which is stable and does not reset on republish:

| Post | Rendered byline | CMS `createdOn` | Match |
|---|---|---|---|
| what-is-the-average-iq | November 28, 2024 | `2024-11-28T20:14:27Z` | ✅ |
| vocal-stimming-in-autism | June 2, 2024 | `2024-06-02T07:16:53Z` | ✅ |

The Blog Posts collection has no dedicated date field (confirmed against the full field
list), so `Created On` is what the template binds — correctly.

**Consequence for the BlogPosting work:** the concern raised here was unfounded.
`datePublished` can be wired to `Created On` safely. A dedicated editable date field is
still worth adding if editors ever need to backdate or correct a publication date, but
that is a convenience, not a prerequisite, and it does not block adding schema.

---

## Task 2 — /bcbas/* page metadata

All nine profile URLs fetched. **The prior audit's finding is confirmed and still true.**

> **Read this section in light of the noindex.** All nine of these pages serve
> `<meta name="robots" content="noindex,follow">` and are out of Google's index. This
> pass did not check the robots meta — that was a gap, corrected in the summary below.
> Every metadata gap catalogued here is real but carries no search impact while the
> noindex stands.

| Page | `<title>` | Meta description | Canonical | Person / ProfilePage JSON-LD |
|---|---|---|---|---|
| audrey-poggi | `MasterMindBehavior.com` | **absent** | `…/bcbas/audrey-poggi` ✅ | none |
| jennifer-chiochankitmun | `MasterMindBehavior.com` | **absent** | `…/bcbas/jennifer-chiochankitmun` ✅ | none |
| kafayat-thomas | `MasterMindBehavior.com` | **absent** | `…/bcbas/kafayat-thomas` ✅ | none |
| kelly-brzak | `MasterMindBehavior.com` | **absent** | `…/bcbas/kelly-brzak` ✅ | none |
| kristin-waugh | `MasterMindBehavior.com` | **absent** | `…/bcbas/kristin-waugh` ✅ | none |
| marissa-burd | `MasterMindBehavior.com` | **absent** | `…/bcbas/marissa-burd` ✅ | none |
| mastermind-behavior-clinical-team | `MasterMindBehavior.com` | **absent** | `…/bcbas/mastermind-behavior-clinical-team` ✅ | none |
| taylor-dzingle | `MasterMindBehavior.com` | **absent** | `…/bcbas/taylor-dzingle` ✅ | none |
| victoria-hornback | `MasterMindBehavior.com` | **absent** | `…/bcbas/victoria-hornback` ✅ | none |

- **Titles: all nine identical** — `MasterMindBehavior.com`. Confirmed still true. The
  collection page template has no title binding to the BCBA `name` field.
- **Meta descriptions: absent on all nine.** Not empty — the tag is not emitted at all.
  There are also **zero Open Graph and zero Twitter card tags** on these pages, so social
  shares have nothing to render either.
- **Canonicals: correct on all nine** — each is self-referential and well-formed. This is
  the one thing right on these pages.
- **Person / ProfilePage JSON-LD: absent on all nine**, server-rendered and
  client-injected alike (0 `<script>` tags, 0 bare-string occurrences).

Staging is identical (`mastermindbehavior.webflow.io/bcbas/audrey-poggi` →
`<title>MasterMindBehavior.com</title>`), so no fix is staged and awaiting publish.

### "Articles by this author" block

**The block renders on all nine pages. It is empty on eight of the nine.**

| Page | `w-dyn-item` count | Webflow empty state | Unique `/post/` links |
|---|---|---|---|
| mastermind-behavior-clinical-team | 13 (12/page, paginated) | no | 12 |
| audrey-poggi | 0 | **`w-dyn-empty`** | 0 |
| jennifer-chiochankitmun | 0 | **`w-dyn-empty`** | 0 |
| kafayat-thomas | 0 | **`w-dyn-empty`** | 0 |
| kelly-brzak | 0 | **`w-dyn-empty`** | 0 |
| kristin-waugh | 0 | **`w-dyn-empty`** | 0 |
| marissa-burd | 0 | **`w-dyn-empty`** | 0 |
| taylor-dzingle | 0 | **`w-dyn-empty`** | 0 |
| victoria-hornback | 0 | **`w-dyn-empty`** | 0 |

The eight empty pages render the heading followed by Webflow's literal empty state:

```html
<section class="author-articles">
  <h2 class="author-articles_heading">Articles by this author</h2>
  <div class="w-dyn-list">
    <div class="w-dyn-empty"><div>No items found.</div></div>
```

**Root cause, confirmed at the CMS level.** The Blog Posts collection
(`6627fd62e242d50407cfe157`) has an `author` reference field. Every post points at the
same item: `6a2e763ca589b9cdd033a53b` — which the BCBAs collection
(`6a2e6dbfd8c767bf9acb51ce`, 9 items) resolves to **"Mastermind Behavior Clinical Team"**.

This was verified exhaustively, not sampled. Walking the clinical-team author page's own
pagination to the last page returns **exactly 337 posts across 29 pages** — every live
post on the site. Since a Webflow collection list filters the whole collection by
reference, the eight `No items found` results are conclusive: **zero posts are attributed
to any of the eight individual BCBAs.**

A secondary `author-name` plain-text field also exists on the collection and is `null`
on all sampled posts.

> Method note: the Webflow MCP `list_collection_items` action **silently ignores the
> `offset` parameter** — calls with `offset: 100/200/300` all returned
> `"pagination":{"limit":100,"offset":0,...}` and the identical first 100 items. The API
> sample is therefore 100 of 340; the complete 337-post figure above comes from the
> rendered pagination walk, which is authoritative.

Collection total is **340** items vs **337** live `/post/` URLs — 3 posts are draft,
archived, or otherwise unpublished. All 100 sampled items have `noindex: false`.

---

## Task 3 — Sitemap hygiene

Source: `https://www.mastermindbehavior.com/sitemap.xml` (HTTP 200, 67,694 bytes).

| Metric | Value |
|---|---|
| Total `<url>` / `<loc>` entries | **579** |
| Entries carrying `lastmod` | **0 — no entry has one** |
| Entries carrying `changefreq` | 0 |
| Entries carrying `priority` | 0 |

Composition: 337 `/post/*`, 205 `/areas-we-serve/*`, 9 `/bcbas/*`, 28 root-level pages.

### lastmod
**No sitemap entry carries a `lastmod` value.** The sitemap is a bare `<urlset>` of
`<loc>` elements only. This is Webflow's default auto-generated output and is not
configurable without switching to a custom sitemap.

### Perry duplication
**Both entries are still listed:**
```
https://www.mastermindbehavior.com/areas-we-serve/perry
https://www.mastermindbehavior.com/areas-we-serve/perry-043a7
```

**The 301 still fires correctly:**
```
GET /areas-we-serve/perry-043a7
→ HTTP/2 301
   location: /areas-we-serve/perry
→ final: https://www.mastermindbehavior.com/areas-we-serve/perry (200, 1 redirect)
```

So the redirect is healthy, but the sitemap still advertises the redirecting URL. The
`perry-043a7` CMS item needs to be removed from the collection (or excluded) to drop it
from the sitemap — the redirect alone does not remove it.

### Non-200 sitemap entries
All 579 URLs were swept with HEAD requests.

| Result | Count |
|---|---|
| 200 | **578** |
| 301 | **1** |

**The only non-200 entry in the entire sitemap is `/areas-we-serve/perry-043a7` (301 → `/areas-we-serve/perry`).**

There are **no 404s, no 5xx, and no broken URLs**. Two URLs
(`/post/hyperfixation-in-autism` and `/areas-we-serve/dawson`) initially returned a curl
timeout during the parallel sweep; both returned clean 200s on retry and are healthy —
transient, not a site fault.

---

## Task 4 — Schema publish state

### Verdict: **every staged schema group is LIVE. Nothing is still staged-only.**

Live `www` and staging `webflow.io` were scanned with the identical parser. Results are
**byte-for-byte identical in schema terms across all 20 paths tested** — same tag counts,
same `@type` sets, same order. There is no staged-but-unpublished delta anywhere.

| Page group | URL | Live `www` | Staging `.webflow.io` | Types found |
|---|---|---|---|---|
| **Homepage** | `/` | ✅ **LIVE** | ✅ same | MedicalOrganization, PostalAddress, State×3, MedicalTherapy, ImageObject, WebSite, WebPage |
| **Contact** | `/contact` | ✅ **LIVE** | ✅ same | ContactPage, MedicalOrganization, MedicalBusiness×2, PostalAddress×2, State×2, OpeningHoursSpecification×4 |
| **Service 1** | `/early-intervention` | ✅ **LIVE** | ✅ same | Service, State×3, PeopleAudience, MedicalOrganization |
| **Service 2** | `/parent-training` | ✅ **LIVE** | ✅ same | Service, State×3, PeopleAudience, MedicalOrganization |
| **Service 3** | `/behavior-support` | ✅ **LIVE** | ✅ same | Service, State×3, PeopleAudience, MedicalOrganization |
| **Service 4** | `/skill-development` | ✅ **LIVE** | ✅ same | Service, State×3, PeopleAudience, MedicalOrganization |
| **Service 5** | `/transition-planning` | ✅ **LIVE** | ✅ same | Service, State×3, PeopleAudience, MedicalOrganization |
| **Service 6** | `/in-home-aba-therapy` | ✅ **LIVE** | ✅ same | Service, State×3, PeopleAudience, MedicalOrganization |
| **State hub — NJ** | `/aba-therapy-in-new-jersey` | ✅ **LIVE** | ✅ same | MedicalBusiness, PostalAddress, State, Country, MedicalTherapy, OpeningHoursSpecification×2, MedicalOrganization |
| **State hub — GA** | `/aba-therapy-in-georgia` | ✅ **LIVE** | ✅ same | MedicalBusiness, PostalAddress, State, Country, MedicalTherapy, OpeningHoursSpecification×2, MedicalOrganization |
| **State hub — NC** | `/aba-therapy-in-north-carolina` | ✅ **LIVE** | ✅ same | MedicalOrganization, State, Country, MedicalTherapy, MedicalOrganization |
| **Areas We Serve city template** | `/areas-we-serve/{city}` | ✅ **LIVE** | ✅ same | Service, City, State, PeopleAudience, BreadcrumbList, ListItem×3, MedicalOrganization |

All six service pages are confirmed live. The NC hub correctly uses `MedicalOrganization`
with no address (no NC office, no GBP) — as expected, not an inconsistency.

### City template coverage
The city template schema is **fully server-rendered**, not client-injected. A
15-page deterministic random sample of the 205 city pages returned an identical result on
**15 of 15**: exactly 1 `<script type="application/ld+json">` tag containing the full
`Service` + `BreadcrumbList` + `MedicalOrganization` `@graph`. Verbatim head of the Perry
payload:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Service",
      "@id": "https://www.mastermindbehavior.com/areas-we-serve/perry#service",
      "name": "In-Home ABA Therapy in Perry, Georgia",
      "serviceType": "In-Home ABA Therapy",
      "provider": { "@id": "https://www.mastermindbehavior.com/#organization" },
      "areaServed": { "@type": "City", "name": "Perry",
        "containedInPlace": { "@type": "State", "name": "Georgia" } },
```

This supersedes the "205 city pages inject BreadcrumbList at runtime" premise — the
BreadcrumbList is in the served HTML.

### Pages with no schema (not in the staged scope — listed for completeness)
`/services`, `/about-us`, `/bcba-team`, `/blog`, `/areas-we-serve`,
`/building-skills-independence`, `/understanding-aba-therapy` — 0 JSON-LD tags on live
and staging alike. These were not part of the staged batch, so this is a gap rather than
a publish failure.

---

## Summary of open issues

> **Revised after follow-up verification.** Two changes from the first pass: the
> publish-date issue was retracted as a false positive (see Task 1), and all nine
> `/bcbas/*` pages were found to be serving `noindex,follow`, which drops every
> BCBA-page finding to informational.

| # | Issue | Severity | Evidence |
|---|---|---|---|
| 1 | ~~No BlogPosting schema on any of 337 posts~~ **FIXED** — see Change log | ~~High~~ | Live; 50 posts verified valid |
| 2 | ~~`/areas-we-serve/perry-043a7` still in sitemap (301s to `/perry`)~~ **FIXED** — see Change log | ~~Medium~~ | Sitemap now 578 entries, 0 non-200 |
| 3 | 337 of 337 posts attributed to the generic Clinical Team; 8 BCBAs have zero articles | **Medium** | Pagination walk = 337; 8/9 pages `w-dyn-empty` |
| 4 | All 9 noindexed `/bcbas/*` URLs are still submitted in `sitemap.xml` | **Low** | 9/9 `includeInSitemap: true` |
| 5 | ~~7 root pages carry no schema~~ **FIXED** — see Change log | ~~Low~~ | 7/7 live and verified |
| 6 | Sitemap carries no `lastmod` on any of 579 entries | **Low** | 0 occurrences |

### Downgraded to informational — the BCBA pages are deliberately deindexed

All nine `/bcbas/*` pages serve `<meta name="robots" content="noindex,follow">`, set
unconditionally in head custom code on the BCBAs collection template
(page `6a2e6dbfd8c767bf9acb51d9`). Verified live on 9/9. The original audit checked
title, description, canonical, and schema on these pages but **never checked
indexability**, which is why this was missed.

Because these pages are out of the index, the following carry no search impact and
should not be prioritized: the shared `MasterMindBehavior.com` title across all nine,
the absent meta descriptions / OG / Twitter tags, and the absent `Person`/`ProfilePage`
schema. They matter only if the noindex is ever reversed.

One strategic note: author-authority (E-E-A-T) work on YMYL medical content normally
depends on indexable author profiles. Fixing post-to-author attribution (#3) has limited
upside while `/bcbas/*` stays deindexed — these two decisions pull against each other and
should be settled together.

## Explicitly checked and NOT an issue

- **Post publish dates — correct, and varying per post.** Bound to Webflow's built-in
  `Created On`, which does not reset on republish. The earlier "all posts show today's
  date" claim was a misread of Webflow's `<!-- Last Published: -->` boilerplate comment
  and is retracted in full. (Task 1)
- Schema publish state — all staged groups are live; nothing pending. (Task 4)
- Sitemap health — 578/579 return 200; no 404s or 5xx.
- The `perry-043a7` → `perry` 301 fires correctly.
- BCBA canonicals — all 9 correct and self-referential.
- City page schema — present and server-rendered on 15/15 sampled.
- NC `MedicalOrganization` with no address — correct; no NC office or GBP exists.
- CallRail DNI is installed sitewide (company `477025173`), confirmed in page source.

---

## Change log — 2026-07-30: BlogPosting schema

**Status: LIVE on production as of 2026-07-30.** Published to `www.mastermindbehavior.com`
and `mastermindbehavior.com` after staging verification.

Addresses open issue #1. Implemented as a `<script type="application/ld+json">` block in
head custom code on the Blog Posts template (page `6627fd62e242d50407cfe1ad`), matching
the mechanism already proven on the city template.

### Emitted per post

`BlogPosting` (`headline`, `image`, `datePublished`, `inLanguage`, `url`,
`mainEntityOfPage`, `author`, `publisher`) plus the shared `MedicalOrganization` node,
referenced by `@id` so it resolves against the existing sitewide organization entity.

### Three constraints found during implementation

**1. The native JSON-LD page field cannot carry CMS bindings.** Webflow validates that
field as strict JSON, and the binding token itself contains `\}` — an invalid JSON escape
— so the API rejects it with `400 The provided schema markup must be valid JSON`. Head
custom code is the only mechanism that supports per-item bindings. Both existing schema
implementations on this site already use it; `jsonLdSchema` is null on every page.

**2. There is no date field to bind.** The Blog Posts collection has no date field, and
`get_bindable_sources` returns 27 sources with no date among them. `datePublished` binds
the built-in `Created On` via `{{wf {"path":"created-on","type":"Date"} }}`, which is not
enumerated by the API but does resolve — verified rendering real ISO timestamps
(`2024-11-28T20:14:27.098Z`) matching each item's stored `createdOn`. `Created On` is
stable across republishes.

**3. `description` is deliberately omitted.** `post-summary` is a multi-line field, and a
raw newline inside a JSON string would make the whole block unparseable. Double quotes
turned out to be safe — Webflow HTML-escapes bound values — but newlines are not, and the
field cannot be audited for them through the API (the `contains` filter cannot match a
newline). `description` adds little for article rich results, so the safe trade was to
leave it out.

### Verification

| Check | Staging | Production |
|---|---|---|
| Posts with valid, parseable JSON-LD | 11 / 11 | **38 / 38** (every 9th sitemap URL) + 12 / 12 targeted |
| Exactly one `ld+json` block per post | ✅ | ✅ |
| `datePublished` resolves to the item's real `createdOn` | ✅ | ✅ |
| `BlogPosting` + `MedicalOrganization` both present in `@graph` | ✅ | ✅ |
| Pre-existing page CSS after the head rewrite | byte-identical | byte-identical |
| `og:url`, hero preload, Finsweet loader | intact | intact |
| `BlogPosting` leakage onto non-post pages | 0 | 0 on `/`, `/contact`, `/areas-we-serve/perry`, `/early-intervention` |
| Existing schema on non-post pages still intact | — | ✅ 1 block each, unchanged |

Production sample was 38 of the 337 `/post/*` sitemap URLs, taken as every 9th entry of
the sorted list for an even spread, plus the 12 targeted posts (top-traffic and the
known quote-in-title edge case). 50 distinct posts checked, 0 failures.

### Cosmetic issue on 1 post — RESOLVED

`/post/how-to-teach-children-with-autism-to-accept-no` had a title containing straight
ASCII double quotes. Webflow escapes bound values, so the JSON stayed valid, but the
headline read `...Accept &quot;No&quot;` — JSON-LD is parsed as JSON, and parsers do not
HTML-decode inside a `<script type="application/ld+json">` block, so the entity survived
into the value Google ingests. In the HTML body the same entity decodes normally, so the
visible page was never affected.

**Fixed** by replacing the two straight quotes with typographic quotes in the CMS `name`
field. Curly quotes have no special meaning in HTML or JSON, so Webflow passes them
through unescaped. Verified live:

| | Before | After |
|---|---|---|
| JSON-LD `headline` | `...Accept &quot;No&quot;` | `...Accept “No”` |
| `<title>` / `<h1>` / `og:title` | rendered `"No"` | `“No”` |
| Slug and canonical | unchanged | **unchanged** |

Only the `name` field was touched — the slug is untouched, so no URL or inbound link
changed. This was the only one of 337 posts whose title contained a double quote,
confirmed by CMS filter.

---

## Change log — 2026-07-30: duplicate Perry sitemap entry

**Status: LIVE on production.** Addresses open issue #2.

### Cause

Not a missing redirect — the 301 was already in place and firing correctly. The Areas We
Serve collection held **two published items both named "Perry"**:

| Item | Slug | Created | Content |
|---|---|---|---|
| `66ad3c53921c8c113c3c241b` | `perry-043a7` | 2024-08-02 | empty — `local-detail-html`, `final-cta-body`, `verify-body` and all 3 nearby-city refs `null` |
| `6674696ea34ecacbc4eb3d61` | `perry` | 2024-06-20 | fully populated |

The `-043a7` suffix is Webflow's auto-generated collision hash, so the duplicate was
created by accident and left empty. Webflow builds its sitemap from every *published*
item regardless of whether a redirect rule shadows the URL, which is why a 301'ing URL
was still advertised.

### Fix applied

`includeInSitemap: false` on the duplicate item (`66ad3c53921c8c113c3c241b`), then a
production publish. The item and its 301 are left intact.

**Deletion was deliberately avoided.** `nearby-city-*` are reference fields, so deleting
the item could break those references on any city page pointing at it, and the redirect's
survival depends on whether it is a manual rule or one Webflow auto-created from a slug
change. Sitemap exclusion achieves the same result, is reversible, and risks neither.

### Verification (production, cache-busted)

| Check | Before | After |
|---|---|---|
| `<loc>` entries | 579 | **578** |
| `perry-043a7` in sitemap | present | **absent** |
| `/areas-we-serve/perry-043a7` | 301 → `/perry` | 301 → `/perry` (unchanged) |
| `/areas-we-serve/perry` | 200, in sitemap | 200, in sitemap |
| Non-200 entries across full sitemap | 1 | **0 of 578** |

Full HEAD sweep of all 578 entries returns 200 on every URL. One post initially returned
a curl connection failure (`000`, not an HTTP status) under 24-way parallelism and
returned 200 on three serial retries — the same transient behaviour noted during the
original audit, not a site fault.

### Not done

The nine noindexed `/bcbas/*` URLs remain in the sitemap by prior decision — keeping them
submitted is what lets Google recrawl and register the `noindex`. They should be excluded
once Search Console shows them dropped from the index.

---

## Change log — 2026-07-30: schema for the 7 hub pages

**Status: LIVE on production as of 2026-07-30.** Published to `www.mastermindbehavior.com`
and `mastermindbehavior.com`. Addresses open issue #5. Payloads are committed under
`schema/hub-pages/`.

### Rationale

The site's entity graph had leaves but no trunk. Six `#service` entities, 205 city
`Service` nodes, two `MedicalBusiness` offices and 337 `BlogPosting`s all pointed at
`/#organization`, but the seven hub pages that organise them declared nothing. These
additions link the hubs into the existing graph **by `@id` reference rather than
redefinition**, the same pattern the city template already uses.

| Page | Type | Links to |
|---|---|---|
| `/services` | `CollectionPage` + `ItemList` | the 6 existing `#service` `@id`s |
| `/about-us` | `AboutPage` | `mainEntity` → `#organization` |
| `/bcba-team` | `CollectionPage` + 8 × `Person` | `worksFor` → `#organization` |
| `/blog` | `Blog` | `publisher` → `#organization` |
| `/areas-we-serve` | `CollectionPage` + `ItemList` | the 3 state hubs |
| `/understanding-aba-therapy` | `CollectionPage` | `isPartOf` → `/blog#webpage` |
| `/building-skills-independence` | `CollectionPage` | `isPartOf` → `/blog#webpage` |

`BreadcrumbList` added to all seven — the most direct rich-result win, and city pages
already had them while hubs did not.

### Why `/bcba-team` matters most

`/bcbas/*` is noindexed **and** orphaned — the team page renders 9 CMS cards but contains
zero links to the individual profiles. The eight clinicians therefore did not exist as
entities to Google at all. `/bcba-team` *is* indexed, so `Person` schema there recovers
the practitioner-authority layer without reopening the noindex decision, and mints stable
`Person` `@id`s that `BlogPosting.author` can point at if attribution is ever fixed.

### Two deliberate choices

**Person data is hardcoded.** `/bcba-team` is a static page rendering a CMS list, and
page-level custom code cannot bind to individual list items. The 8 Persons ship as
literal JSON: accurate today, but it must be edited by hand when the roster changes.
Accepted knowingly as maintenance debt in exchange for the E-E-A-T.

**Kelly Brzak carries no credential claim.** Her `credentials` field is null, her card
renders no credential line (unlike the other seven), and her bio describes a former
elementary teacher with a Master's in Child Development — it never claims BCBA. Email was
searched and holds nothing on her credentials. Her `Person` node therefore has `name`,
`description`, `image` and `worksFor` only, with **no `jobTitle` and no
`honorificSuffix`**. Asserting a BCBA certification for her would fabricate a
professional credential on YMYL medical content.

### Verification

| Check | Staging | Production |
|---|---|---|
| Pages emitting exactly one valid, parseable JSON-LD block | 7 / 7 | **7 / 7** |
| `BreadcrumbList` present | 7 / 7 | **7 / 7** |
| Node counts | 10 on `/bcba-team`, 2 elsewhere | same |
| 8 `Person` entities live on `/bcba-team` | ✅ | ✅ |
| Kelly Brzak node carries no `jobTitle` / `honorificSuffix` | ✅ | ✅ confirmed live |
| Dangling `@id` references inside each graph | none | none |
| The 6 `#service` `@id`s referenced by `/services` exist on target pages | 6 / 6 | 6 / 6 |
| Pages that already had schema | unchanged | unchanged — 1 block each on `/`, `/contact`, a city page, 2 posts, a state hub, a service page |

---

## Internal linking analysis — 2026-07-30 (analysis only, no changes made)

Measured across all 337 posts (fetched in full), not sampled.

### The link graph

| Source | → services | → city pages | → state hubs | → other posts |
|---|---|---|---|---|
| Blog (337 posts, ~96% of site traffic) | 2.05/post | **0** | **0** | 3.26/post |
| Homepage | — | 0 | 3 | — |
| `/areas-we-serve` | — | 190 | — | — |
| State hubs (NJ 100 / GA 78 / NC 12) | — | 190 total | — | — |
| A city page | 7 | 1 | 3 | **0** |

Zero-city and zero-state-hub figures verified on 48 posts: the 10 highest-traffic
(≈92% of all organic traffic) plus a 38-post spread across the sitemap.

**The local layer is not unlinked — it is sealed off from the traffic.** The blog forms a
closed loop with the service pages; the only inbound path to the local subgraph is the
homepage.

### 15 city pages have no internal links at all

`toms-river · trenton · union · vernon · vineland · voorhees · wall · wayne ·
west-milford · west-new-york · west-orange · westfield · willingboro · winslow ·
woodbridge` — all New Jersey. The NJ state hub links **exactly 100** cities (Webflow's
per-list cap) while GA (78) and NC (12) sit under it and lose nothing. Strong inference,
not proven. Needs pagination or a second list.

`/areas-we-serve` also still links `perry-043a7` — an internal link into a redirect.

### State-hub linking has a far smaller addressable surface than expected

An earlier recommendation in this document assumed a state-hub link would be
"editorially natural in any ABA post." **That was wrong.** Three sources inflate apparent
state mentions, none editorial:

1. the boilerplate closing block ("serving families across New Jersey, Georgia, and
   North Carolina") — on 212 posts;
2. the embedded insurance widget, which renders a state dropdown as page text;
3. incidental rhetoric (e.g. *"whether the family is in Naples or in New Jersey"*).

Excluding all three:

| | Posts | Share |
|---|---|---|
| Genuinely state-specific (state in slug and subject) | **6** | 1.8% |
| Insurance/school topic, could be made state-specific | 17 | 5.0% |
| No natural geographic hook | ~264 | 78% |

The six: `aba-therapy-services-in-georgia-overview`, `how-georgia-laws-support-autism-services`,
`how-access-school-based-aba-therapy-in-georgia`, `autism-prevalence-in-north-carolina`,
`is-aba-therapy-covered-by-insurance-north-carolina`, `medicaid-and-aba-coverage-in-nj`.

**Conclusion: internal linking cannot rescue the city pages.** There is not enough honest
editorial surface. The local layer needs its own demand strategy.

### The unlinked boilerplate — the one at-scale opportunity

| | Posts |
|---|---|
| Have the "Why Mastermind" closing block | 212 |
| Block names all three states | 212 |
| Those state names linked to hubs | **0** |
| Block links to `/contact` | 212 |

A sentence that is already about service areas, already beside a working `/contact` link,
with the state names as plain text. Honest to link. Two caveats: it is boilerplate, which
Google discounts heavily, and it lives in each post's rich-text `post-body`, so it is 212
scripted CMS edits rather than one template change.

### The 13 posts with zero service links — mapping (NOT YET APPLIED)

Every one has a cluster already set in the CMS; the cluster→service mapping is consistent
with the other 324 posts.

| Post | Cluster | Service target |
|---|---|---|
| autism-diagnostic-criteria-dsm-5 | Diagnosis, Causes & Brain Science | `/early-intervention` |
| autism-facial-expressions | Medical & Co-occurring | `/early-intervention` |
| autism-physical-traits | Medical & Co-occurring | `/early-intervention` |
| best-dogs-for-autism | Parenting, Advocacy & Daily Support | `/parent-training` |
| free-sensory-toys-for-autism | Sensory Processing & Stimming | `/behavior-support` |
| how-to-handle-regression-in-learned-skills | Emotional Regulation & Coping | `/behavior-support` |
| teaching-abstract-thinking-skills-through-aba | Academic & Cognitive Skills | `/skill-development` |
| the-impact-of-peer-modeling-on-skill-development | Emotional Regulation & Coping | `/skill-development` * |
| the-role-of-functional-play-in-developing-critical-thinking-skills | Academic & Cognitive Skills | `/skill-development` |
| the-role-of-storytelling-in-enhancing-language-skills-for-autism | Communication & Language | `/skill-development` |
| understanding-perseverative-behaviors-and-how-to-redirect-them-in-autism | Challenging Behaviors & Assessment | `/behavior-support` |
| what-is-choice-theory | Academic & Cognitive Skills | `/skill-development` |
| what-is-respite-care-autism | Access, Insurance & Resources | `/in-home-aba-therapy` |

\* cluster says Emotional Regulation, but the post is explicitly about skill development —
override the cluster mapping here.

Three need a human eye on the anchor sentence rather than the target: **best-dogs-for-autism**
(listicle, no natural service sentence), **what-is-choice-theory** (Glasser's framework,
only loosely ABA), **what-is-respite-care-autism** (closest natural anchor is
*"how it fits next to ongoing services like ABA"*).

**Implementation note.** Webflow rich-text updates require resending the entire
`post-body` field; these 13 total ~305 KB. Prefer linking an existing phrase over
inserting new sentences, and work in small batches.

### Execution status — 3 of 13 applied and live

| Post | Service | Anchor (existing prose, linked in place) | Diff blocks |
|---|---|---|---|
| what-is-respite-care-autism | `/in-home-aba-therapy` | "in-home ABA therapy" | 2 |
| teaching-abstract-thinking-skills-through-aba | `/skill-development` | "develop essential cognitive skills" | 44 * |
| autism-facial-expressions | `/early-intervention` | "the right support and interventions" | 1 |

Each verified by diffing the live page against its pre-change state. No prose was
rewritten — in all three cases an existing phrase was wrapped in a link.

\* **The 44 blocks are not corruption.** One is the link; the other 43 are Webflow
re-rendering `<figure>` markup. The live page had been serving a stale 2026-07-13 publish,
and an item-level republish brought it in line with what was already stored. Side effect
worth knowing: 4 in-article images went from `loading="lazy"` to `loading="auto"`, which
browsers treat as eager. **This was already in the stored CMS field before the edit** —
it was not introduced here — but any item-level republish will surface it. Full-site
publishes do not. Where a remaining post contains figures, set `loading="lazy"` in the
same edit, since the whole field is being rewritten anyway.

### Remaining 10 — not yet applied

`autism-diagnostic-criteria-dsm-5` · `autism-physical-traits` · `best-dogs-for-autism` ·
`free-sensory-toys-for-autism` · `how-to-handle-regression-in-learned-skills` ·
`the-impact-of-peer-modeling-on-skill-development` ·
`the-role-of-functional-play-in-developing-critical-thinking-skills` ·
`the-role-of-storytelling-in-enhancing-language-skills-for-autism` ·
`understanding-perseverative-behaviors-and-how-to-redirect-them-in-autism` ·
`what-is-choice-theory`

Targets are in the mapping table above. Method that works: fetch the item, find an
existing phrase that genuinely matches the target service, wrap it in place, resend the
full `post-body`, publish the item, then diff the live page against its previous state to
confirm only the link changed.

**Why this stopped at 3:** Webflow has no partial update for rich text, so every link
costs the entire `post-body` twice (fetch + write). The remaining 10 are ~250 KB of
round-trip. The method is proven and safe; it is simply expensive per link, and is the
wrong tool for anything larger than this batch.
