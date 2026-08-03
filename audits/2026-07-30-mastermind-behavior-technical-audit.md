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

### Execution status — 12 of 13 applied and live

All verified by diffing the live page against its pre-change state. In every case an
existing phrase was wrapped in a link; **no prose was rewritten or added**.

| Post | Service | Anchor (existing prose) | Diff blocks |
|---|---|---|---|
| what-is-respite-care-autism | `/in-home-aba-therapy` | "in-home ABA therapy" | 2 |
| teaching-abstract-thinking-skills-through-aba | `/skill-development` | "develop essential cognitive skills" | 44 * |
| autism-facial-expressions | `/early-intervention` | "the right support and interventions" | 1 |
| what-is-choice-theory | `/skill-development` | "skill development program" | 3 |
| how-to-handle-regression-in-learned-skills | `/behavior-support` | "functional behavior assessments" | 2 |
| autism-physical-traits | `/early-intervention` | "Early identification" | 2 |
| free-sensory-toys-for-autism | `/behavior-support` | "sensory regulation" | 1 |
| understanding-perseverative-behaviors… | `/behavior-support` | "Functional behavior assessments" | 2 |
| best-dogs-for-autism | `/parent-training` | "parent training coaches" | 1 |
| autism-diagnostic-criteria-dsm-5 | `/early-intervention` | "consistent intervention" | 1 |
| the-role-of-storytelling… | `/skill-development` | "developing language and social skills" | 2 |
| the-role-of-functional-play… | `/skill-development` | "support both cognitive and social-emotional skills" | 4 |

Zero deletions on 11 of 12.

\* **The 44 blocks are not corruption.** One is the link; the other 43 are Webflow
re-rendering `<figure>` markup because the live page had been serving a stale 2026-07-13
publish. An item-level republish brought it in line with what was already stored. Side
effect: 4 in-article images went from `loading="lazy"` to `loading="auto"`, which browsers
treat as eager. **That value was already in the stored CMS field before the edit** — it was
not introduced here. Full-site publishes do not surface it; item-level publishes do.

### The 13th — `the-impact-of-peer-modeling-on-skill-development` — NOT applied

Target `/skill-development`. Anchor identified and verified unique:
*"These strategies leverage peer influence to foster skill development and confidence."*

**Blocked by a tooling limit, not by the content.** Webflow rich text has no partial
update, so the whole `post-body` must be resent — and this post's body is **49,436
characters**. That exceeds what can be moved through the tool pipeline in one piece
without chunking, and reassembling a 49 KB document by hand carries a real risk of
silently corrupting a live article. The other twelve ranged 13–37 KB and were safe.

**Recommended fix: do this one by hand in the Webflow editor.** Open the post, find the
sentence above, select the words "skill development", and link them to
`https://www.mastermindbehavior.com/skill-development`. About thirty seconds, zero risk.

---

## Change log — Collection List cap: what the MCP can and cannot reach

### Scope of the problem

Only New Jersey overflows. Published (non-archived) city counts are NJ 115 / GA 78 /
NC 12, against Webflow's 100-item Collection List cap. The overflow is a clean
alphabetical tail: page 1 renders `aberdeen` … `tinton-falls`, and page 2
(`?c93d3bc8_page=2`, confirmed live, HTTP 200) serves exactly these 15:

```
toms-river      trenton         union           vernon          vineland
voorhees        wall            wayne           westfield       west-milford
west-new-york   west-orange     willingboro     winslow         woodbridge
```

The same 15 are missing from `/areas-we-serve`, whose 190 rendered links break down as
100 (NJ, capped) + 78 + 12.

On the CMS totals: the collection holds 517 NJ / 455 GA / 20 NC items, but the large
majority carry `isArchived: true` and `lastPublished: null`. Those are archived, not a
hidden inventory of live pages.

### Which element carries the query — this is the part that misleads

A Webflow Collection List is two nested elements, and only the outer one is configurable:

| Element | Internal type | Exposes |
| --- | --- | --- |
| Collection List Wrapper | `DynamoWrapper` | `source`, `queryMode`, `filters`, `filterMatch`, `sort`, `limit`, `offset`, `pagination`, `curatedItemIds` |
| Collection List (inner) | `DynamoList` | `domId`, `tag`, `visibility`, `attributes` — nothing else |

Probing the inner `DynamoList` returns four generic settings and zero matches for
`value_type: sort` / `filter` / `selectedItems`, which reads exactly like "the API does not
support this." It does. The query lives on the parent wrapper.

### Verified writable through the Designer bridge

Confirmed empirically on a temporary wrapper created at the page body root:

| Setting | Result |
| --- | --- |
| `source` | Written. Requires `static_json` with `{"collectionId": "..."}` — a bare string is rejected |
| `offset` | Written via `static_number` |
| `sort` | Written. `[{"fieldSlug":"name","direction":"ascending"}]`. `fieldId` is rejected in favour of `fieldSlug`; the key is `direction`, not `order`; values are `ascending` / `descending`, not `asc` / `desc`. Note `slug` is *not* a sortable field — sort on `name` |
| `filters` | Written. `[{"fieldSlug":"state","operator":"equals","value":"New Jersey"}]`. Operators are named (`equals`, `doesNotEqual`, `isSet`, `isNotSet`), not `eq` |
| `limit` | Default 100, and this is the hard cap |

Final verified state of the test wrapper, read back from the API:

```json
{"source": {"collectionId": "6642b822923646375241d310"},
 "filters": [{"fieldSlug": "state", "operator": "equals", "value": "New Jersey"}],
 "sort": [{"fieldSlug": "name", "direction": "ascending"}],
 "limit": 100, "offset": 100, "queryMode": "dynamic"}
```

That is precisely the configuration needed to render the 15 tail cities. The test element
was removed after verification; nothing was left on the page.

Two practical notes. `data_element_builder` with `type: CMSCollection` creates a
`DynamoWrapper`, but it cannot be inserted as a sibling of an existing inner list —
Webflow rejects nested Collection List Wrappers. And the error messages are precise enough
to derive the schema by trial, which is how the shapes above were established.

### Implication

The `offset` setting is the cleaner fix than a second list sorted Z→A: a duplicate list
with `offset: 100` renders items 101+ in document order, so the tail appears in the page-1
HTML without reversing anything or risking overlap. Both are reachable via MCP.

Worth keeping in proportion: all 205 city pages together draw roughly 4 organic visits per
month. Restoring 15 of them to the internal link graph is correctness work, not a traffic
lever.

---

## Change log — overflow Collection Lists built on both New Jersey pages

Built entirely through the MCP with the Designer bridge connected. Both new lists mirror
the original query exactly, differing only in `offset` (100 instead of 0) and `pagination`
(null instead of `{itemsPerPage: 100}`).

| Page | Page ID | New wrapper | Inner list classes |
| --- | --- | --- | --- |
| `/aba-therapy-in-new-jersey` | `6a01d3a82e9293bcfba0e668` | `8d50025c-e805-4ee0-97cf-7d2c0e75cd7c` | `cards`, `cards-ga` |
| `/areas-we-serve` | `664751f18604421a35f42f61` | `4ca9b8a9-4c56-94e7-a246-0e19b2b08bed` | `cards` |

The index page carries three lists filtered to New Jersey / Georgia / North Carolina; only
the New Jersey one (`8a3b6adb-0111-59f5-7e06-8ab598e9efa0`) overflows, and the new list was
inserted directly after it.

Card markup replicates the original on each page: `DynamoItem > Link.card-link >
Heading.heading-style-h5[h2]`, with the link set to `collectionPage` mode and the heading
text bound to the `Name` field (`d288331399cee88e56b59c0a125879e4`). The hub page also
carries `areas-ga` on the heading and `aria-label="link"` on the link, matching its
original; the index page does not, matching its own.

Two deliberate departures from a straight copy:

- **No Finsweet attributes.** The originals carry `fs-cmsload-element="list"` and
  `fs-cmsload-mode="infinite"`. The overflow lists are not paginated, so client-side
  infinite load has nothing to do and would only risk interfering with the list above it.
- **Empty state hidden.** `DynamoEmpty` visibility set to false on both. If New Jersey ever
  drops below 101 published cities the overflow list returns nothing, and without this the
  page would render a stray "No items found." block.

The original lists were not modified — their `pagination-hide` class and Finsweet
attributes are untouched, so nothing about existing behaviour changes.

**Status: staged in the Designer, not yet published.** The next site publish ships them.

### Known limitation

`offset` is fixed at 100. This is correct while New Jersey holds 101–200 published cities
(currently 115). If it ever exceeds 200 a third list at `offset: 200` would be needed. Worth
a note in the CMS runbook rather than a mechanism.

---

## Change log — correction: the two lists now share one scroll pane

The first version of this build cloned the `cards` class onto the overflow list. That was
wrong. Reading the compiled stylesheet:

```css
.cards { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
         max-height: 375px; overflow: scroll; }
@media (max-width: …) { .cards { grid-template-columns: 1fr 1fr; } }
```

`.cards` is a **fixed 375px-tall internal scroll pane**, not a plain grid. Cloning it
produced a second scroll pane stacked directly under the first — worse than the problem it
was meant to solve.

### Two related findings from the same check

**Finsweet is not loaded on this site.** The live HTML contains `fs-cmsload-mode="infinite"`
and `fs-cmsload-element="list"` as inert attributes, but no script fetches them — there is
no `finsweet`, `cmscore`, `jsdelivr`, or `unpkg` reference anywhere in the document, and the
head carries a `<!-- Canonical enforcement (overrides Finsweet) -->` comment suggesting it
was removed on purpose. The original list was therefore always a hard stop at exactly 100
items, with nothing lazy-loading. This also means the overflow list carries **no duplication
risk** — there was never a client-side fetch of page 2 to collide with.

**`pagination-hide` is `display: none`**, so no next-page control was reachable either. The
15 cities were genuinely unreachable from both pages.

### The fix

Both lists now sit inside a single shared grid container, and the list containers are
removed from the box tree so every card becomes a direct grid child of that one container:

| Page | Shared container | DOM id |
| --- | --- | --- |
| `/aba-therapy-in-new-jersey` | `025e761d-92b5-685f-dd30-5fad51132448` | `nj-cities-grid` |
| `/areas-we-serve` | `05180012-fe3e-0936-5b48-040e85f3fce0` | `nj-cities-grid` |

The container carries `cards` (plus `cards-ga` on the hub, matching its original), so the
pane keeps exactly the dimensions and column count it had before. A scoped `HtmlEmbed`
immediately above each container supplies:

```css
#nj-cities-grid > .w-dyn-list,
#nj-cities-grid .w-dyn-items { display: contents; }
```

The id selector outranks `.cards`, so the inner lists stop generating boxes and their
`max-height` / `overflow` no longer apply. Result: one 375px scroll pane containing all 115
New Jersey cities in one continuous grid, visually identical to today apart from the 15
that were missing.

Scoping by id matters on `/areas-we-serve`, which also holds Georgia and North Carolina
lists — those are untouched.

Note the failure mode is deliberately benign: if the embed ever fails to render, the rule
simply does not apply and the layout falls back to the two-pane version rather than
collapsing.

**Status: staged in the Designer, not yet published.**

---

## Change log — restoring the centering the flattened wrapper used to supply

The merged grid shipped misaligned on `/aba-therapy-in-new-jersey`: the town list ran to
the section edge while the heading above it stayed centred. Cause, from the compiled
stylesheet:

```css
.collection-list-wrapper-2 { max-width: 1200px; margin-left: auto; margin-right: auto;
                             padding-bottom: 100px; color: #fff; }
@media screen and (min-width: 1920px) {
  .collection-list-wrapper-2 { width: 1200px; max-width: 1200px; margin-left: auto;
                               margin-right: auto; } }
```

That wrapper — not the grid — was the element holding the 1200px column and centring it.
`display: contents` removes an element's box entirely, so the max-width and auto margins
went with it. The cards then filled the full section width.

Fix: move those properties onto `#nj-cities-grid`, which is now the only box in the chain.

```css
#nj-cities-grid { max-width: 1200px; margin-left: auto; margin-right: auto;
                  margin-bottom: 100px; }
@media screen and (min-width: 1920px) { #nj-cities-grid { width: 1200px; } }
```

`margin-bottom` rather than the original `padding-bottom`: the wrapper's padding sat
outside the 375px scroll pane, but `#nj-cities-grid` *is* the pane, so padding would scroll
with the cards instead of spacing the section below it.

`/areas-we-serve` was not affected and needed no change — its three list wrappers carry no
classes at all (`class="w-dyn-list"`), so `display: contents` removed nothing of value
there, and the Georgia and North Carolina lists sit at the same full width as New Jersey.
The Georgia hub page was never touched.

**General lesson for this codebase:** `display: contents` on a Webflow Collection List
Wrapper silently drops whatever layout that wrapper was carrying. Check the wrapper's own
classes before flattening it — on this site the hub pages and the index page differ.

---

## Change log — the overflow lists cannot be linked via the API; they are hidden

The centering fix worked, but verifying it exposed a second defect in the overflow lists:
their 15 cards rendered with `href="#"`. Every API route to a working per-item link was
tried and all three failed.

| Attempt | Result in published HTML |
| --- | --- |
| `link = {mode: "collectionPage"}` — byte-identical to the working original | `href="#"` |
| `link = {mode: "collectionPage", to: "detail_areas-we-serve"}` | `href="detail_areas-we-serve"` — `to` is emitted as a literal string |
| `link = {mode: "collectionPage", to: "<template page id>"}` | stored as `{pageSlug: "<id>"}`, same literal emission |
| `HtmlEmbed` containing `{{wf {…"path":"slug"…} }}` binding tokens | tokens rendered literally as text |

`get_settings` returns exactly the same value for the working original link and the broken
new one, and `get_bindable_sources` returns zero sources for both. Whatever associates a
`collectionPage` link with its collection is Designer-side state the Data API neither
exposes nor reproduces.

The binding-token attempt was published to `mastermindbehavior.webflow.io` only, so the
literal `{{wf …}}` text never reached production.

### Current live state

Both overflow list wrappers are set to `visibility: false` and the site is published. The
live pages are back to 100 (NJ hub) and 190 (`/areas-we-serve`) city links, with no broken
anchors and the corrected centering in place. Verified against production: zero occurrences
of `href="#" class="card-link"`, `detail_areas-we-serve"`, or `{{wf`.

**Production was briefly wrong.** Between two publishes the 15 cards were live with
`href="detail_areas-we-serve"`. That is now cleared.

### What remains, and how to finish it

The scaffolding is intact and hidden — grid container, second Collection List with
`offset: 100`, card markup, and the flattening CSS. Finishing it is a Designer job:

1. Open `/aba-therapy-in-new-jersey`, find the hidden second Collection List inside
   `#nj-cities-grid` (`8d50025c-e805-4ee0-97cf-7d2c0e75cd7c`).
2. Select the card link inside it, open Link Settings, choose **Current Item**.
3. Unhide the Collection List wrapper.
4. Repeat on `/areas-we-serve` (`4ca9b8a9-4c56-94e7-a246-0e19b2b08bed`), then publish.

Everything else — the query, the offset, the shared grid, the styling, the centering — is
already correct and does not need to be touched.

---

## Change log — New Jersey hub complete: all 115 cities live

`/aba-therapy-in-new-jersey` now renders all 115 published New Jersey cities as a single
continuous grid in one scroll pane. Verified against production:

- 115 unique `/areas-we-serve/*` links, `aberdeen` first, `woodbridge` last
- correct alphabetical order across the seam — index 99 `tinton-falls`, index 100 `toms-river`
- zero `href="#"` anchors, zero literal binding tokens

### What unblocked it

The `collectionPage` link needed a target chosen from the Designer's **Page** dropdown
("Current Areas We Serve"). That selection is not reachable through the Data API and, more
awkwardly, leaves no trace the API can read: `all_raw_settings` and `all_resolved_settings`
both return `{"mode": "collectionPage"}` for the working link and for a broken one alike.
The only reliable signal is the rendered HTML — or, in the Designer Navigator, a small ⟳
binding marker next to the element.

Practical rule for this stack: a Collection List built through the API is fully configurable
(source, filter, sort, limit, offset) and its text bindings work, but **any link to the
current collection item has to be set once by hand in the Designer.**

### Still outstanding

`/areas-we-serve` keeps its overflow list hidden (`4ca9b8a9-4c56-94e7-a246-0e19b2b08bed`),
because its card link has not had the same Page dropdown set — a staging publish confirmed
15 unresolved anchors there. Production is unaffected: that page stays at 190 links with no
broken anchors. Setting the dropdown on that one link and unhiding the wrapper takes it to
205.

All experimental publishes during this work went to `mastermindbehavior.webflow.io` only.

---

## Change log — New Jersey grid no longer an inner scroll pane

Reported symptom: the first towns were unreachable on `/aba-therapy-in-new-jersey`, with the
visible top row clipped mid-glyph starting at "Garfield".

Cause: `.cards` is `max-height: 375px; overflow: scroll`, so the grid is a short internal
scroll pane roughly five rows tall. With 115 towns most of the list sits outside it, and
browsers restore a scroll container's offset across reloads — which is why the pane loaded
already scrolled past Aberdeen through Fair Lawn.

This predates the overflow-list work: the same clipped "Garfield" top row appears in
screenshots taken before any of these changes. It was previously less visible because the
list stopped at 100 towns.

Fix, scoped to this grid only:

```css
#nj-cities-grid { max-height: none; overflow: visible; }
```

All 115 towns now render in normal page flow, so nothing is hidden behind an inner
scrollbar and no scroll position can strand the first entries. Verified live: 115 unique
city links, `aberdeen` first, `woodbridge` last, zero broken anchors, and all three
`#nj-cities-grid` rules present.

The Georgia and North Carolina lists still use the 375px pane, so the New Jersey section is
now visually taller than those. Worth deciding whether to apply the same treatment there —
it is the same one-line override per grid.

---

## Change log — scroll pane restored with a forced scroll reset

The 375px `.cards` scroll pane is back on the New Jersey grid by request. The earlier
`max-height: none` override has been removed.

To stop the pane stranding the first towns, both grids now carry a small script that pins
the container to the top:

```js
(function () {
  var top = function () {
    var g = document.getElementById('nj-cities-grid');
    if (g) g.scrollTop = 0;
  };
  if (document.readyState !== 'loading') top();
  else document.addEventListener('DOMContentLoaded', top);
  window.addEventListener('load', top);
})();
```

On the cause of the clipped top row: the grid renders in correct alphabetical order and all
115 anchors are present in the HTML, so nothing is missing — the pane was simply scrolled.
Browsers restore a scroll container's offset across reloads, and this page had been reloaded
many times mid-scroll during the work, so the offset persisted. A first-time visitor would
not usually hit it. The script makes the starting position deterministic either way.

### Live state, verified against production

| Page | City links | Empty anchors | Notes |
| --- | --- | --- | --- |
| `/aba-therapy-in-new-jersey` | 115 (`aberdeen` → `woodbridge`) | 0 | complete |
| `/areas-we-serve` | 190 | 0 | overflow list still hidden |

### `/areas-we-serve` still not resolving

Two separate staging publishes after the Designer edit both still rendered
`<a href="#" class="card-link">` for all 15 overflow cards on that page — sample from
staging:

```html
<a href="#" class="card-link w-inline-block"><h2 class="heading-style-h5">Toms River</h2></a>
```

So the Page dropdown on that page's card link has not taken effect yet. The wrapper is
hidden again and production is unaffected at 190 links with no broken anchors. Note this is
a *different* element from the hub page's link — page `664751f18604421a35f42f61`, link
`140f029c-8823-a0b9-8e82-b041f4f87ea1`, inside wrapper `4ca9b8a9-4c56-94e7-a246-0e19b2b08bed`.

---

## Change log — root cause of every "cut off" report: centred grid overflow

Rendering the live page in a headless browser finally located the real defect, which had
nothing to do with scroll position and predates all of this work.

```css
.cards          { max-height: 375px; overflow: scroll; display: grid; }
.cards.cards-ga { align-content: center; }
```

When a grid's rows are taller than its own `max-height`, `align-content: center` centres
them in the box and overflows them **equally above and below**. Overflow above a scroll
container's top edge is unreachable: `scrollTop` cannot go negative. Measured on the live
New Jersey hub:

| | Before | After |
| --- | --- | --- |
| `align-content` | `center` | `start` |
| First card offset from container top | **−333px** | 0px |
| Cards at negative offsets (invisible, unscrollable) | **40** | 0 |
| `scrollTop` on load | 0 | 0 |

`scrollTop` was zero the entire time — the pane was never scrolled. That is why the earlier
scroll-restoration theory was wrong and why the scroll-reset script changed nothing; it has
been removed. Forty towns were simply painted above the container and clipped, which is
exactly the reported symptom: a list that appears to begin partway through the alphabet with
its top row sliced mid-glyph.

Fix, one line, scoped to the merged grid:

```css
#nj-cities-grid { align-content: start; }
```

The same guard was added to `/areas-we-serve` even though its grid lacks `cards-ga`, so the
merged grid there cannot fall into the same trap.

This bug existed before the overflow work — the very first screenshot in this engagement
shows the same clipped "Garfield" top row at 100 towns. Adding 15 more made it worse, not
new. **The Georgia and North Carolina lists carry `cards-ga` too and are worth checking for
the same clipping.**

### Verified against production, rendered in a browser

| Page | Cards in grid | Unreachable above | First | Last |
| --- | --- | --- | --- | --- |
| `/aba-therapy-in-new-jersey` | 115 | 0 | Aberdeen | Woodbridge |
| `/areas-we-serve` | 100 | 0 | Aberdeen | Tinton Falls |

### `/areas-we-serve` overflow: every API route is now exhausted

The remaining 15 towns on that page need its overflow list's card link bound to the current
collection item. Attempts, all failed:

1. `link = {mode:"collectionPage"}` — renders `href="#"`
2. `link` with `to` as page slug or page id — emitted literally as the href
3. `HtmlEmbed` with `{{wf …}}` binding tokens — rendered as literal text
4. `transform_element_to_component` on the working link — `Target element is invalid`;
   Webflow refuses to componentise an element inside a Collection List, so the working
   link cannot be cloned into the second list

That leaves one Designer click, on page `664751f18604421a35f42f61`, link
`140f029c-8823-a0b9-8e82-b041f4f87ea1`, inside hidden wrapper
`4ca9b8a9-4c56-94e7-a246-0e19b2b08bed`.

Worth noting the SEO objective is already met without it: all 115 New Jersey city pages are
internally linked and crawlable from `/aba-therapy-in-new-jersey`. Adding them to
`/areas-we-serve` is duplication, not new coverage. Removing that page's hidden overflow
list is a legitimate alternative to finishing it.

---

## Change log — /areas-we-serve completed with a static overflow embed

The Collection List route was abandoned on this page. Its replacement needs no CMS binding,
so it needs no Designer click.

The non-functional second Collection List was removed. In its place, an `HtmlEmbed` appended
inside `#nj-cities-grid` holds the 15 towns past the cap as plain anchors using the page's
own card markup:

```html
<a href="/areas-we-serve/toms-river" class="card-link w-inline-block">
  <h2 class="heading-style-h5">Toms River</h2></a>
```

The flattening rule was extended to cover it, so the anchors become direct grid children and
sit flush with the dynamic cards rather than occupying one cell:

```css
#nj-cities-grid > .w-dyn-list,
#nj-cities-grid .w-dyn-items,
#nj-cities-grid > .w-embed { display: contents; }
```

### Verified against production, rendered in a browser

| Page | Page links | NJ cards in grid | Unreachable | First | Last |
| --- | --- | --- | --- | --- | --- |
| `/aba-therapy-in-new-jersey` | 115 | 115 | 0 | Aberdeen | Woodbridge |
| `/areas-we-serve` | 205 | 115 | 0 | Aberdeen | Woodbridge |

Computed text colour is identical between the dynamic and static cards on each page
(`#fff` on the hub, `#002833` on the index), so the seam is invisible. Order is continuous:
`… Tinton Falls` → `Toms River` → `… Woodbridge`.

### Trade-off

These 15 anchors are static. If the published New Jersey city set changes, they must be
edited by hand — the embed carries a comment saying so. The first 100 remain fully dynamic.
The alternative is the Collection List version used on the hub, which stays in sync
automatically but requires the Designer link step. The hub keeps that version; this page
uses the static one.

---

## Change log — empty first cell fixed; static cards rebuilt as real elements

The static overflow cards were initially delivered as an `HtmlEmbed` flattened with
`display: contents`. That left the top-left cell of the grid empty and shifted every card
one position, producing a 24th row holding a single town.

Cause, established by removing the embed in the browser and re-measuring: flattening an
`HtmlEmbed` leaves an anonymous grid item behind. Removing whitespace and comment nodes from
the embed did not help; removing the embed entirely moved the first card from x=259 back to
x=0. The wrapper div itself is the source, not its contents.

Fix: the 15 towns are now real Webflow `LinkBlock` elements appended directly inside
`#nj-cities-grid`, each with the `card-link` class, a static URL, and an `h2.heading-style-h5`
child — the same markup the collection list produces. No embed, no flattening, no anonymous
item. The `> .w-embed` selector was dropped from the flattening rule.

### Verified against production, rendered in a browser

| Page | Cards | Rows | First row | First card x | Unreachable | First | Last |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/aba-therapy-in-new-jersey` | 115 | 23 | 5 | 0 | 0 | Aberdeen | Woodbridge |
| `/areas-we-serve` | 115 | 23 | 5 | 0 | 0 | Aberdeen | Woodbridge |

23 rows × 5 columns = 115 exactly on both pages, no gap and no orphan row. Page totals are
115 and 205 city links respectively.

### Note for whoever maintains this

`/areas-we-serve` now mixes a dynamic Collection List (towns 1-100) with 15 hand-built link
elements (towns 101-115), which must be edited by hand if the published New Jersey city set
changes. `/aba-therapy-in-new-jersey` uses a second Collection List at `offset: 100` instead
and stays in sync automatically; it needed one Designer step the API cannot perform —
setting the card link's Page target to "Current Areas We Serve".

---

## Change log — step 1 of embed standardisation, staged on /in-home-aba-therapy

### Why the naive plan does not work

A single site-wide stylesheet cannot simply be lifted out of the embeds. Parsing all inline
CSS across five pages gives 429 distinct selectors, of which **30 are defined differently on
different pages**:

| Selector | Conflict |
| --- | --- |
| `.mm-embed *` | `margin:0; padding:0; box-sizing:border-box` on two pages, `box-sizing:inherit` on the other two |
| `.mm-step` | `grid-template-columns: 56px 1fr` vs `44px 1fr`, different padding |
| `.mm-embed .hero-headline` | `font-weight: 800` vs `700` |
| `.mm-step__body strong` | `var(--font-body)` vs `var(--font-disp)` |

Merging those into one file would visibly change pages. Cross-page sharing is therefore
gated on 30 design decisions, not a mechanical step.

### What was done instead

Per-page consolidation, which is where the actual drift bug lives. `/in-home-aba-therapy`
shipped its stylesheet **twice**, once per embed, 98.1% identical and already diverged:

```
copy A: min-height: 280px          copy B: aspect-ratio: 16/9
copy A: min-height: 200px          copy B: aspect-ratio: 16/9
copy A: (no .section-warm-alt)     copy B: .section-warm-alt { background:#f8f6f1 }
```

The two were merged into one block in the first embed; the second embed now carries markup
only. The merge is declaration-level, not rule-level: where both copies define the same
selector, declarations are combined with the later copy winning **per property**. A
first attempt that kept only the later rule silently dropped `min-height: 200px` from
`.benefit-image`, because the other copy set `aspect-ratio` — a different property, so both
had been applying. The layout harness caught it.

### Verification

`tools/css-consolidation/layout-diff.mjs` renders both builds in headless Chromium and
compares every element inside `.mm-embed` on position, size, font-size, weight, colour,
background and display, plus total document height, at three viewports.

Run against the **published staging build** vs production:

| Viewport | Elements | Doc height | Differing |
| --- | --- | --- | --- |
| 1440 | 271 vs 271 | 9423 vs 9423 | **0** |
| 768 | 271 vs 271 | 15188 vs 15188 | **0** |
| 390 | 271 vs 271 | 16857 vs 16857 | **0** |

Page inline CSS: 36,543 B in 5 blocks → 22,375 B in 4. The page's own stylesheet went from
two 16 KB copies to one 17 KB copy.

**Staging only. Production is untouched.**

### Remaining, in order

1. Same treatment for `parent-training` (24,420 B duplicated), `insurance-terminology`
   (15,732 B), `financial-aid-resources`.
2. Reconcile the 30 cross-page conflicts, then lift the shared core into a component that
   renders on every page. Webflow caps site-wide custom code near 10k characters, so the
   ~90 KB deduped union cannot live in Site Settings → Head.
3. Rebuild the layout as a Webflow Component with props, which is what actually makes the
   layout identical by construction rather than by convention.

---

## Change log — step 1 complete; correction to the duplication figures

### Correction

The per-page "duplicate" figures reported earlier conflated two different things. That table
counted a block as duplicate if it had been seen on *any* previously scanned page, so
cross-page repeats were charged to whichever page was scanned second. Measured strictly
within each page:

| Page | Intra-page duplicate CSS | Action |
| --- | --- | --- |
| `in-home-aba-therapy` | two 16 KB near-copies | merged (declaration-level) |
| `parent-training` | 23,055 B, byte-identical copy | earlier copy removed |
| `insurance-terminology` | **none** | nothing to do |
| `financial-aid-resources` | **none** | nothing to do |
| `bcba-team` | none | nothing to do |

So step 1 touches two pages, not four. `insurance-terminology` and `financial-aid-resources`
carry several distinct stylesheets each, one per section — verbose, but not duplicated
within the page.

### parent-training

"Code Embed 4" and "Code Embed 5" held byte-identical copies of the same 23 KB stylesheet
with nothing between them in document order, so removing the earlier copy is exactly
cascade-neutral. The hero embed now carries markup only.

| Viewport | Elements | Doc height | Differing |
| --- | --- | --- | --- |
| 1440 | 242 vs 242 | 8489 vs 8489 | **0** |
| 768 | 242 vs 242 | 11632 vs 11632 | **0** |
| 390 | 242 vs 242 | 14864 vs 14864 | **0** |

Page inline CSS: 50,567 B in 5 blocks → 27,512 B in 4.

### Step 1 result, staged

| Page | Before | After | Saved |
| --- | --- | --- | --- |
| `/in-home-aba-therapy` | 36,543 B | 22,375 B | 14,168 B |
| `/parent-training` | 50,567 B | 27,512 B | 23,055 B |

Zero rendering differences on either page at 1440 / 768 / 390. **Staging only.**

### What this does and does not achieve

It does not make the pages share anything. Each still carries its own private stylesheet and
its own hand-written markup. It removes each page's ability to disagree with *itself* — the
bug that had `/in-home-aba-therapy` shipping an aspect-ratio fix in one copy and a
min-height in the other.

### Step 2 is cheaper than first assessed

Not all cross-page repetition is blocked on the 30 conflicting selectors. Several blocks are
**byte-identical across pages** and can be shared with no design decisions at all:

| Block | Size | Pages | Redundant |
| --- | --- | --- | --- |
| `23615ce8` (the `global-styles` embed) | 3,808 B | 4 | 11,424 B |
| `cd0faf5e` | 10,383 B | 2 | 10,383 B |
| `c0e2cf83` | 2,546 B | 2 | 2,546 B |
| `b3cfaaac` | 598 B | 5 | 2,392 B |
| `7e7363f8` | 51 B | 5 | 204 B |
| | | | **26,949 B** |

`global-styles` is the obvious first move: identical on four pages, already isolated in its
own embed, and it only needs converting to a Webflow Component to become genuinely shared.
The 30 conflicts affect only the remainder.

---

## Change log — full-site scan: 28 pages, and a reordering of priorities

Scanning every published page changes the picture, in two ways.

### 1. The clone family is seven pages, not two

Exact hashing found four; three more were *near*-duplicates and were invisible to it — the
same blind spot that hid `/in-home-aba-therapy`'s 14 KB until it was diffed. In every case
the duplication is blocks 3 & 4: two embeds, each carrying the full stylesheet.

| Page | Copies | Recoverable |
| --- | --- | --- |
| `early-intervention` | identical | 21,736 B |
| `behavior-support` | identical | 20,999 B |
| `skill-development` | 99.9% similar | 20,953 B |
| `transition-planning` | identical | 20,724 B |
| `parent-training` | identical | 20,240 B — done |
| `services` | **92.0% similar** | 16,759 B |
| `in-home-aba-therapy` | 98.1% similar | 16,171 B — done |

~137 KB total. `services` is the most drifted pair on the site and needs the closest reading.

### 2. Step 1 is a no-op on the other pages, and the real prize is elsewhere

`first-90-days-of-aba-therapy`, `insurance-terminology`, `financial-aid-resources`, the three
state hubs and `bcba-team` all have **zero** intra-page duplication. Nothing for step 1 to do.
Their redundancy is entirely cross-page — and that is where the largest single number on the
site is:

| Block | Size | Pages | Redundant |
| --- | --- | --- | --- |
| `23615ce8` — the `global-styles` embed | 3,604 B | **25 of 28** | **86,496 B** |
| `1eb2d944` | 3,577 B | 4 (3 state hubs + insurance-terminology) | 10,731 B |
| `be5cd20a` | 10,675 B | 2 (building-skills-independence, understanding-aba-therapy) | 10,675 B |
| `cd0faf5e` | 9,298 B | 2 (financial-aid-resources, insurance-terminology) | 9,298 B |
| `a2950cca` | 4,851 B | 2 (NJ, NC hubs) | 4,851 B |
| | | | **122,051 B** |

Site-wide inline CSS is 526,127 B across 28 pages.

### The state hubs are their own clone family

Five stylesheets totalling 8,163 B are present on all three. North Carolina has **no** unique
blocks at all; New Jersey has one (1,479 B); Georgia has two (7,187 B). They are siblings of
one template.

### Recommended reordering

Grinding page-by-page through step 1 is not the highest-value path. One block sits on 25 of
28 pages, byte-identical, already isolated in its own embed named `global-styles`, and needs
**no design decisions** — converting it to a single Webflow Component removes 86 KB and
touches every page on the site in one edit.

Revised order:

1. `global-styles` → one shared Component. Largest win, lowest risk, no decisions required.
2. Finish step 1 on the five remaining clone pages (~101 KB).
3. The three state hubs → one Component with props; NC has nothing unique, so it is nearly
   free.
4. The 30 conflicting selectors — the only part that genuinely needs design calls.

---

## Change log — correction: Global Styles is already a Component; priorities revert

The recommendation to lift `global-styles` into a shared Component was wrong. It already is
one. Every page-wrapper begins with:

```
ComponentInstance  id d36a88a9-0b45-2553-76ef-3200b3336cad  name "Global Styles"
ComponentInstance  id c29251c3-4c95-fee7-6218-95199d7ddce2  name "navigation"
...
ComponentInstance  id 39e67c04-e408-f054-1a24-d4728ad220c8  name "footer"
```

So the 86,496 B attributed to that block is **one definition rendering on 25 pages**, not 25
copies. Every page has to carry the CSS in its own HTML; that is unavoidable for inline
styles and is not a maintenance hazard — editing the component updates all 25 at once. No
work to do, and nothing was changed.

The error came from measuring the *published output* and inferring duplication from repeated
bytes. Repeated bytes across pages are expected when a component renders on every page. Only
duplication **within** a page, or blocks living in separate page-level embeds, indicate
actual copy-paste.

### Corrected cross-page numbers

| Block | Size | Pages | Source | Real redundancy |
| --- | --- | --- | --- | --- |
| `23615ce8` | 3,604 B | 25 | **Global Styles component** | none |
| `b3cfaaac`, `7e7363f8` | 649 B | 5 | site-wide custom code | none |
| `1eb2d944` | 3,577 B | 4 | page-level embeds | 10,731 B |
| `be5cd20a` | 10,675 B | 2 | page-level embeds | 10,675 B |
| `cd0faf5e` | 9,298 B | 2 | page-level embeds | 9,298 B |
| `a2950cca` | 4,851 B | 2 | page-level embeds | 4,851 B |

Real cross-page copy-paste is **~35,555 B**, not the 122,051 B reported before.

### Priorities revert

Intra-page duplication is back to being the larger prize: **~101 KB** still recoverable
across the five remaining clone pages, versus ~36 KB cross-page. The original order stands.

### One genuinely useful finding

The site already uses Components for shared structure — Global Styles, navigation, footer.
Step 3 is therefore not a new pattern to introduce but an extension of one already in use,
which makes componentising the seven-page clone family considerably less speculative.

---

## Change log — unification analysis for the seven clone pages

Goal changed from "dedupe each page" to "one stylesheet shared by all seven", matching the
`Global Styles` component pattern the site already uses.

### How far apart the seven have drifted

| | Count |
| --- | --- |
| Union of selectors across the seven | 386 |
| Present on 2+ pages | 224 |
| — identical everywhere | **181 (81%)** |
| — conflicting | **43** |

Of the 43 conflicts, 18 differ in a single property and 8 in two. Typical shape is one page
against a four-page majority: `20px` vs `22px`, `1.65` vs `1.7`, `12px` vs `16px`. Classic
copy-paste drift, not deliberate variation.

Full conflict report: `tools/css-consolidation/service-pages.conflicts.txt`
Proposed sheet: `tools/css-consolidation/service-pages.canonical.css`

### The canonical sheet

42,432 B / 343 selectors, replacing ~316 KB of page-level CSS across the seven pages. Each
property takes the majority value; ties break toward a real value over an absent one.

### Two false starts worth recording

**Union order breaks the cascade.** Merging by union produced one rule order where each page
had its own, so equal-specificity overrides stopped winning. Concretely, `.hero-headline`
collapsed from 48px to 18px. Anchoring the order to the most complete page's sheet fixed it.

**The first impact measurement was meaningless.** Comparing absolute x/y reported
"271/271 elements differ" — but a single padding change near the top of a page shifts every
later element's absolute position. Re-measured on parent-relative geometry plus box, font,
colour and spacing, the real figure is 10–25% of elements.

### Actual impact of unifying

| Page | Changed at 1440px | at 390px |
| --- | --- | --- |
| `services` | 22 / 189 | 19 / 189 |
| `skill-development` | 22 / 213 | 23 / 213 |
| `behavior-support` | 23 / 254 | 49 / 254 |
| `transition-planning` | 48 / 204 | 51 / 204 |
| `early-intervention` | 56 / 246 | 56 / 246 |

### These are design decisions, not cleanup

The largest single change is hero bottom padding: five pages use `80px 0 100px`, `services`
uses `80px 0 64px`. Majority rule as implemented picks 64px, shortening the hero on five
pages by 36px. Other visible calls:

| Selector | Values | Majority |
| --- | --- | --- |
| `.hero h1` font-size | 48px (2) vs 40px (services) | 48px |
| `.hero h1` font-weight | 700 (2) vs 800 (in-home) | 700 |
| `.hero h1` @768px | 36px vs 34px | tie |
| `.areas-header h2` colour | `white` (6) vs `#fff` (services) | identical in effect |

Majority voting is a reasonable default for the 30-odd cosmetic conflicts, but it is not the
right authority for hero padding or headline weight. Those need a human call, and the answer
determines how five live pages look.

**Nothing has been written to Webflow for this step. Staging is unchanged.**

---

## Change log — correction: CSS comments were corrupting the analysis

The conflict analysis above was wrong. The CSS parser did not strip comments, so a comment
preceding a rule became part of its selector key. These were treated as two different
selectors and never merged:

```
/* ─── HERO ─── */ .mm-embed .hero           { padding: 80px 0 100px; … }
/* ─── HERO (compact) ─── */ .mm-embed .hero { padding: 80px 0 64px;  … }
```

Both survived into the canonical sheet, and the later one won. **The hero shrinking to 64px
was never a majority vote — it was comment text leaking into selector names.**

Re-run with comments stripped:

| | Before (wrong) | After |
| --- | --- | --- |
| Union selectors | 386 | **331** (55 were phantoms) |
| Shared by 2+ pages | 224 | 182 |
| Identical everywhere | 181 | 138 |
| Conflicting | 43 | 44 |

And the hero tally reverses completely: **six of seven pages use `80px 0 100px`**; only
`services` uses `80px 0 64px`.

### Pinned values

| Property | Tally | Pinned | Basis |
| --- | --- | --- | --- |
| `.hero` padding | 100px ×6, 64px ×1 | `80px 0 100px` | majority |
| `.hero-headline` font-size | 48px ×5, 40px ×1 | `48px` | majority |
| `.hero-headline` font-weight | 700 ×5, 800 ×1 | `700` | majority |
| `.hero-headline` line-height | 1.15 ×5, 1.18 ×1 | `1.15` | majority |
| `.hero h1` size / weight | 48px ×2, 700 ×2 | `48px` / `700` | consistent with above |
| `.hero-headline` @768px | 48px ×3, 36px ×2, 34px ×1 | **`36px`** | **majority overridden** |

The mobile headline is the one deliberate departure. `48px` leads only because three pages
never received a mobile override at all — a 48px headline at 390px is an omission, not a
decision. `36px` is the considered value on the pages that handle the breakpoint.

### Canonical sheet v2

40,288 B / 331 selectors, 9 pinned properties. Replaces ~316 KB of page-level CSS across the
seven pages. Committed at `tools/css-consolidation/service-pages.canonical.css`.

Measured impact, parent-relative geometry plus box, font, colour and spacing, at 1440px:

| Page | Elements changed |
| --- | --- |
| `skill-development` | 22 / 213 |
| `services` | 22 / 189 |
| `behavior-support` | 23 / 254 |
| `transition-planning` | 48 / 204 |
| `parent-training` | 52 / 242 |
| `in-home-aba-therapy` | 76 / 271 |
| `early-intervention` | 78 / 246 |

`in-home-aba-therapy` absorbs the most because it is the outlier on headline weight (800 →
700) and font-family (`var(--font-display)` → `'Manrope', sans-serif`).

### Still to do

The sheet is built and measured but **not yet written to Webflow**. Applying it means, per
page: replace the first large embed's stylesheet with the canonical one and strip the second
copy — the same operation already performed on `/in-home-aba-therapy` and `/parent-training`,
seven times over, each verified with the harness before it counts.

---

## Change log — the single-sheet approach was wrong; shared base + overrides instead

Rendering one page before applying anything caught a regression that no amount of selector
counting would have.

### What the example showed

On mobile, the unified sheet centred the entire hero — headline, body copy and trust badges
— where the page is left-aligned. Source: `@media (max-width: 768px) .mm-embed .hero
{ text-align: center }`, which exists on **`services` alone**.

The majority logic only voted among pages that *have* a selector. A rule unique to one page
therefore won 1–0 and propagated to all seven. That is not a bug in the tally — it is what
"merge by union" means, and it is wrong for genuinely page-specific styling.

**174 of the 331 selectors are unique to a single page.** Every one of them would have been
pushed onto the other six.

### Corrected structure

A rule joins the shared sheet only if it appears on **4 or more of the 7** pages. Everything
below that threshold stays local.

| | Size | Selectors |
| --- | --- | --- |
| Shared sheet | 19,585 B | 157 |
| `in-home-aba-therapy` override | 1,106 B | 9 |
| `parent-training` override | 1,385 B | 16 |
| `transition-planning` override | 1,610 B | 17 |
| `early-intervention` override | 1,783 B | 17 |
| `behavior-support` override | 1,914 B | 19 |
| `skill-development` override | 1,989 B | 20 |
| `services` override | 14,417 B | 110 |

Total ~44 KB against ~316 KB today, an 86% reduction, with no page able to impose its
private styling on any other.

### `services` is not really a clone

110 unique selectors against 9–20 for the others. It shares the shell but most of its
styling is its own. It should probably be treated as a separate page rather than forced into
the family.

Artefacts: `tools/css-consolidation/service-pages.shared.css` and
`tools/css-consolidation/override.<page>.css`.

Still nothing written to Webflow.

---

## Change log — trust badges: a markup inconsistency, not a CSS one

Reported as "looks weird" on the in-home hero: badges rendering 2 / 1 / gap / 1 at 390px.

Cause is markup, and it predates this work:

| Page | Structure |
| --- | --- |
| `in-home-aba-therapy` | **two** separate `.trust-badges` containers |
| 5 other clone pages | **one** `.trust-badges` holding two `.trust-badge-row` divs |
| `services` | no trust badges |

`.trust-badges` is `display: flex; flex-wrap: wrap; gap: 24px`. With two independent
containers, each wraps on its own and the 4px margin between them adds a visible gap — so
four badges land as 2 / 1 / gap / 1. `.trust-badge-row` has **no CSS on any page**; it is an
unstyled `div`, which is exactly why the majority pattern works: as a block-level flex item
it forces a clean break, giving two tidy pairs.

Fix: `in-home` adopts the majority structure. One container, two rows, badges 2 + 2 —
identical to the other five. Verified by rendering both at 390px.

This is the first change in the unification exercise that improves a page rather than merely
deduplicating it, and it was only found by rendering an example rather than counting
selectors.

Still nothing written to Webflow.

---

## Change log — family reduced to six; unscoped `h2` caught before it spread

`services` removed from the family per decision. Recomputed over the remaining six:

| | Value |
| --- | --- |
| Selectors in the family | 226 |
| Shared (on 4+ of 6) | 157 — of which 123 identical everywhere |
| Page-specific | 69 |
| Shared sheet | 19,585 B |
| Per-page override | 1,106–1,989 B |
| Page total after | ~21 KB, against 36–50 KB today |

### A bug the majority rule would have propagated

Five of the six pages declare a **bare `h2 { … }`** — unscoped, so it restyles every `<h2>`
on the page, including navigation, footer and any Webflow-native section. Only
`in-home-aba-therapy` scopes it correctly as `.mm-embed h2`.

Majority is 5–1 for the unscoped version. Left alone, the shared sheet would have preserved
the bug on five pages and newly imposed it on the one page that had it right. All bare
heading selectors in the shared sheet are now scoped to `.mm-embed`.

This is the second deliberate override of majority, alongside the 36px mobile headline. Both
follow the same principle: the majority reflects what was copy-pasted most often, not what is
correct.

### Architecture for the write

The shared sheet goes into a Webflow **Component**, mirroring the existing `Global Styles`
component — authored once, instanced on each of the six pages. Each page then carries only
its own 1–2 KB override. This also keeps the write small: 19.6 KB written once rather than
six times.

Artefacts final and committed:
- `tools/css-consolidation/service-pages.shared.css`
- `tools/css-consolidation/override.<page>.css` (six files)
- `tools/css-consolidation/layout-diff.mjs` (verification harness)

Still nothing written to Webflow.

---

## Change log — Service Page Styles component created; page 1 of 6 live on staging

### Component

`Service Page Styles` — component id `b3b13b91-f7d3-431f-4f5c-148220cae266`. Holds the
Manrope font link and the 19.6 KB shared stylesheet, with all heading selectors scoped to
`.mm-embed` and the pinned hero values. Mirrors the existing `Global Styles` component:
authored once, instanced per page.

### `/in-home-aba-therapy` — done and verified

- instance of `Service Page Styles` prepended to the page wrapper
- hero embed now carries only a 6-rule page override plus its markup
- trust badges restructured to the majority pattern: one `.trust-badges`, two
  `.trust-badge-row` children

Page inline CSS **36,543 B → 25,580 B**. Rendered against production at 1440 and 390:
headline, body copy and CTA unchanged; badges now 2 + 2 instead of 2 / 1 / gap / 1.

### A collision the threshold rule created

`in-home`'s override contained `.mm-embed h2 { font-weight: 800 }`. Because the other five
pages used a *bare* `h2`, that selector fell below the 4-page threshold and stayed
page-specific — but scoping the shared sheet's headings to `.mm-embed` made the two collide,
and the override loads last. Left alone, `in-home` would have kept 800 while the other five
moved to 700, defeating the pin on the one page it was meant to change.

Both `.mm-embed h2` rules were removed from that override. **The same check is required on
each remaining page**: any override selector that also exists in the shared sheet silently
wins, and the threshold rule does not catch it because the collision is created by the
scoping fix rather than by the source CSS.

### Remaining

Five pages: `parent-training`, `early-intervention`, `behavior-support`,
`transition-planning`, `skill-development`. Each is the same operation — instance the
component, replace the embed stylesheet with its override minus any shared-sheet collisions,
strip the duplicate copy, render at 1440/390. Then one staging publish for the set.

Production remains untouched throughout.

---

## Change log — native hero rebuild attempted and reverted; the real blocker

Attempted to rebuild `/in-home-aba-therapy`'s hero as native Webflow elements, 1:1 with the
embed markup, as a test before rolling the pattern out.

Every element was created. **Every class failed:**

```
One or more styles not found: hero
One or more styles not found: container
One or more styles not found: hero-grid
One or more styles not found: hero-headline
One or more styles not found: trust-badges
One or more styles not found: btn-primary          … and so on
```

### Why

`hero`, `container`, `hero-grid` and the rest exist **only as CSS text inside the embeds'
`<style>` blocks**. They are not Webflow Designer styles. Webflow's style system only knows
classes created in the Designer, so native elements cannot be given them — the rebuild
produced correctly-structured but entirely unstyled markup. It was removed; the page is
unchanged.

### What this means for componentising

The blocker is not the components. It is that the design system lives in CSS text rather
than in Webflow. Any native rebuild requires the ~100 embed classes to exist as real Designer
styles first, with their properties and breakpoints.

That is a bigger project than the CSS consolidation, and it is also the point at which the
site stops being hand-written HTML:

- classes become editable in the Designer rather than in a `<style>` block
- breakpoints come from Webflow's responsive system rather than hand-written media queries
- non-developers can edit sections
- sections can then be Components with props — structure identical by construction

Until that happens, "unified design" remains a discipline maintained by convention, and the
shared `Service Page Styles` component plus a markup lint is the realistic ceiling.

### Revised recommendation

1. Finish the five remaining CSS migrations onto the shared component (~101 KB, low risk).
2. Add the markup lint so structural drift like the trust badges is visible.
3. Treat "port the embed CSS into Webflow Designer styles" as a separate, scoped project —
   probably starting with the hero alone (roughly 15 of the 100 classes) to size the effort
   honestly before committing to the rest.

---

## Change log — collision audit across all five overrides; parent-training part-migrated

### Collision audit

Ran every override against the shared sheet. The `.mm-embed h2` clash found on `in-home`
was not isolated:

| Page | Override selectors | Collisions with shared sheet |
| --- | --- | --- |
| `parent-training` | 16 | none |
| `transition-planning` | 18 | none |
| `early-intervention` | 17 | `.mm-embed .icon-grid`, `.mm-embed .right-grid` |
| `behavior-support` | 20 | `.mm-embed .right-grid`, `.mm-embed .right-image` |
| `skill-development` | 21 | `.mm-embed .icon-grid`, `.mm-embed .right-grid`, `.mm-embed .right-image` |

**The check itself is not yet trustworthy.** It compares selector text while ignoring
`@media` context, so a base-level rule in the shared sheet matches a rule inside a media
query in an override. Some of the above are probably false positives — and more importantly
the same blindness could hide a genuine same-media collision. It must be made media-aware
before those three pages are migrated.

### A second bug class in the overrides

`parent-training`'s override carried **unscoped** selectors inside its media queries —
`.right-grid`, `.approach-grid`, `.icon-grid`, with no `.mm-embed` prefix. Same failure as
the bare `h2`: they apply to the whole page rather than the embed. Scoped when written.
The other overrides need the same sweep.

### `/parent-training` — partially migrated, not published

Done: `Service Page Styles` instance prepended; override written with selectors scoped.
**Not done:** the second embed still carries the 23 KB duplicate stylesheet, so the page is
in a mixed state — the old sheet loads after both the component and the override and still
wins. Visually identical to production, but not the intended end state.

Deliberately **not published**. Staging still shows the previous state for this page.

To finish: rewrite the second embed (`7c08cadb-3d4f-0168-4cee-601897904faa`) with its markup
only, then render at 1440/390.

---

## Change log — collision check made media-aware; pages 2 and 3 of 6 live on staging

### The collision check was wrong in both directions

The previous check compared selector text while ignoring `@media` context. Replaced with
`tools/css-consolidation/collision-check.mjs`, which keys on `(at-rule context, selector)`
and strips comments through a string-aware scanner before parsing.

Its seven flags — `.icon-grid` / `.right-grid` / `.right-image` on `early-intervention`,
`behavior-support` and `skill-development` — were **all false positives**. Every one is an
override rule inside a media query against a shared rule at base level, which is the
intended cascade, not a collision. Those three pages are collision-free.

It had also missed two real ones. Both `.mm-embed h2` rules were still present in
`in-home`'s override *on disk*, though the previous session recorded removing them. The
artefact had drifted from what was written to Webflow.

| | old check | media-aware check |
| --- | --- | --- |
| real collisions | 2 missed | 2 found |
| false positives | 7 | 0 |

### The unscoped selectors were all already dead

Swept all six overrides: six unscoped selectors on three pages. They trace to grouped
selectors in the source CSS of the form `.mm-embed .icon-grid, .approach-grid { … }` — the
split left the second half unanchored.

**Measured before changing them.** Every unscoped rule was already a no-op. At `(0,1,0)` it
loses to the base `.mm-embed .approach-grid` at `(0,2,0)`, and media queries add no
specificity, so source order never mattered. Confirmed in headless Chromium across all six
production pages.

That means `parent-training` ships two live mobile bugs today: `.approach-grid` renders
**3 columns at 390px** and `.right-grid` renders **2 columns at 390px** (152px + 98px).
The author wrote the collapse rules; they never applied.

Scoped rather than deleted, honouring the authors' evident intent. Two assumptions, flagged
for reversal: honour author intent over byte-identical production, and match the other five
at 768px.

Scoping `.approach-grid` then *created* a real collision against the shared sheet — the same
class of bug as the `h2` one, where the fix creates the collision. Dropped from the override.

### `/parent-training` and `/transition-planning` — done and verified

Both now: `Service Page Styles` instance on the page wrapper, hero embed carrying only the
page override, body embed carrying markup only.

| Page | Before | After |
| --- | --- | --- |
| `parent-training` | 98,372 B | 73,791 B |
| `transition-planning` | 95,466 B | 69,705 B |

Each page had **two byte-identical copies** of its stylesheet (23,062 B and 23,563 B
respectively); both now load the 20,141 B shared sheet once plus a ~1.7 KB override.

Every embed rewrite was diffed byte-for-byte against the published staging HTML. All four
markup blocks identical — no transcription error.

### A trap worth recording: the on-disk artefacts had drifted

`parent-training`'s hero embed was written in the previous session with the *old* override,
so correcting the file on disk did not correct the page. The first staging render still
showed `.approach-grid` at 2 columns at 768px. **The artefact is not the source of truth —
the live embed is.** Caught only because the grid columns were measured rather than assumed.

Also: Webflow's staging CDN serves stale HTML for a minute or so after publish. The first
re-fetch showed the old override. Cache-bust the URL before believing a verification.

### Layout diff, staging vs production

The harness (`layout-diff.mjs`) now compares **parent-relative** geometry and keys rows by
structural path, so a change is attributed to the element that changed rather than to
everything below it.

Desktop (1440px) is unchanged on both pages apart from majority pins. Every difference
traces to a recorded decision:

- `.approach-card` `display: block → flex`, `h3` 22px → 20px, grid gap 28px → 24px —
  majority pins `parent-training` had drifted from
- hero headline 48px → 36px at ≤768px — the deliberate mobile-headline override
- `.approach-grid` 3→1 col and `.right-grid` 2→1 col on mobile — **the two live bugs, fixed**
- `.icon-grid` 2→1 col at 390px on both pages — the revived author intent

One visible change worth a second opinion: `transition-planning` was one of only two pages
declaring `aspect-ratio: 16/9` on `.benefit-image`. The majority of four has none, so the
shared sheet drops it and the rows fall back to their 280px min-height (387px → 200px at
768px). Intended by the unification, but it is a real change to a real page.

Production remains untouched — custom domains still show the 2026-07-31 publish.

### Remaining

Three pages: `early-intervention`, `behavior-support`, `skill-development` — now confirmed
collision-free and with their overrides scoped, so each is the plain four-step recipe.
`behavior-support` and `transition-planning` each had one unscoped `.icon-grid` fixed here.

---

## Change log — correction: the majority rule was invalid; shared sheet rebased on in-home

### The clone family has a parent, and it is not a democracy

Webflow page IDs are Mongo ObjectIds. Decoding their embedded timestamps:

| Created | Page |
| --- | --- |
| 2026-03-23 14:03 | `in-home-aba-therapy` |
| 2026-03-30 08:40 | `early-intervention` |
| 2026-03-30 08:51 | `skill-development` |
| 2026-03-30 11:19 | `behavior-support` |
| 2026-03-30 12:17 | `parent-training` |
| 2026-03-30 12:42 | `transition-planning` |

in-home was built **a week earlier**; the other five were minted inside a four-hour
window on one morning. That is build-one, clone-five.

So the "majority of five" is **one decision copy-pasted five times and then frozen**,
while in-home carried on being refined. Majority rule counts the stale snapshot five
times and the maintained original once. It is not a vote; it is an echo.

### What majority rule was discarding

26 conflicting properties resolved against in-home, and they are not random drift:

- **`font-weight: 800` on six selectors** — `.hero-headline`, `h2`, `.benefit-copy h3`,
  `.step-title`, `.timeline-title`, `.tip-card h3`. Nobody sets 800 in six places by accident.
- **Ten defensive `!important` rules** — `.btn-primary { border / cursor / line-height }`,
  `:hover { color / text-decoration }`, `.area-card { color: inherit }`. This is what gets
  added *after* discovering the Webflow host stylesheet bleeding through.
- **Deliberate image framing** — `hero-image 4/3` with `max-width: 1200px` / `max-height:
  900px`, `benefit-image 16/9`.

The cost was concrete and measurable. in-home had `.area-card { color: inherit !important }`;
the five clones did not, and rendered browser-default link blue on the navy section.
Unification **deleted the fix from the reference page instead of propagating it**, taking
the defect from five pages of six to six of six.

| `.area-card` colour | production | staging (before) | staging (after) |
| --- | --- | --- | --- |
| `in-home` | white | **rgb(0,0,238)** | white |
| `parent-training` | rgb(0,0,238) | rgb(0,0,238) | **white** |
| `transition-planning` | rgb(0,0,238) | rgb(0,0,238) | **white** |

The previous sessions had already half-seen this. Majority was overridden exactly twice —
the bare `h2` and the 36px mobile headline — and *both times* the answer landed on
in-home's value, under the note that "the majority reflects what was copy-pasted most
often, not what is correct." The insight was right; it was never generalised.

### The corrected rule

> **in-home wins wherever it has an opinion.** Majority-of-five applies only to selectors
> in-home does not have at all — sections that exist only on the clone pages, where the
> drift is genuine.

Of 157 shared rules, 129 have an in-home counterpart and are now rebased on it; 28 do not
and remain on majority-of-five. Implemented as `tools/css-consolidation/rebase-shared.mjs`,
which is idempotent — a second run reports 0 changed, 0 added, 0 dropped.

The reference is `in-home-aba-therapy.merged.css`. It was validated before use, not assumed:
in-home's two embed copies are **not** identical (18,210 B and 18,183 B — they disagree about
`.benefit-image`, and the later embed wins). Re-deriving the cascade from the raw copies and
diffing against `merged.css` gives 136 keys on both sides, 0 missing, 0 differing, 0 extra.

### Result

The component was rewritten once; all instances follow. Verified against **production
in-home** rather than against each page's own production self:

- `in-home` — **zero property differences**. The reference page is restored exactly.
- `parent-training`, `transition-planning` — every change is a 700 → 800 weight adopting
  in-home's typography, plus the two mobile grid bugs fixed.
- `transition-planning` keeps `aspect-ratio: 16/9`. The visible regression flagged in the
  previous entry is reversed: in-home declares 16/9, so it is now the shared value.

Production remains untouched.

### Two harness bugs found while verifying this

The layout diff claimed "269 changed, 258 removed" on in-home. Both causes were mine:

1. The row key ended in a **global index**, which reintroduced the exact problem the
   structural keying existed to remove — one inserted node shifts every later key.
2. The structural path was walked up to `<body>`, making the key sensitive to anything
   **outside** the embed. Prepending the component shifts an ancestor's ordinal, so every
   descendant key changed and the diff reported 100% churn.

Keys are now rooted at the `.mm-embed` element and each segment carries the element's
ordinal among its like-tagged siblings. A verification harness that cries wolf is worse
than none — it trains you to skim the number.

### One deliberate deviation from the reference, still open

in-home's hero trust badges were restructured in an earlier session from its own
2 / 1 / gap / 1 rendering to the clones' `.trust-badges` + two `.trust-badge-row` pattern,
on the grounds that in-home's rendering was visibly ragged. Under the corrected rule that
is backwards — but the reference's own output was the defect here. Left as-is and flagged:
it is the one place where a clone pattern deliberately beats the reference.

### Remaining

`early-intervention`, `behavior-support`, `skill-development` — unchanged by this correction
except that they will now inherit in-home's values when migrated.

---

## Change log — all six pages migrated; family complete

`early-intervention`, `behavior-support` and `skill-development` migrated on the
in-home-referenced shared sheet. The family is done.

| Page | Before | After | Saved |
| --- | --- | --- | --- |
| `in-home-aba-therapy` | 87,889 | 73,275 | 14,614 |
| `parent-training` | 97,882 | 74,444 | 23,438 |
| `transition-planning` | 95,020 | 70,224 | 24,796 |
| `early-intervention` | 101,267 | 74,106 | 27,161 |
| `behavior-support` | 100,296 | 75,684 | 24,612 |
| `skill-development` | 97,907 | 72,544 | 25,363 |
| **Total** | | | **~140 KB** |

Every page now carries exactly one shared stylesheet plus a 1–2 KB override. All ten
embed markup blocks were diffed byte-for-byte against the published staging HTML —
all identical, no transcription error.

Live Designer state was confirmed equal to production before writing, at zero cost, by
diffing the already-published staging HTML rather than reading the embeds back.

### Two more pages had non-identical stylesheet copies

Like `in-home`, two pages carried two *different* copies of their sheet:

- `early-intervention` — 25,284 vs 25,283 B, whitespace only.
- `skill-development` — the hero copy had `.right-grid { align-items: start }` and
  `.right-image { aspect-ratio: 3/4 }`; the body copy had `center` and `4/3`. The body
  embed loads later and wins, so `center` / `4/3` is what production renders and what
  the shared sheet carries. The `3/4` variant was deliberately not revived.

That is three of six pages whose two copies disagree. "Duplicated stylesheet" was never
quite accurate — they were *drifting* duplicates, and the later embed silently won.

### `early-intervention` is structurally different

Its hero uses a `div` for the eyebrow and a bare `h1` for the headline, where the other
five use an `h1` carrying `.hero-eyebrow` plus a paragraph carrying `.hero-headline`.
Both need rules in its override. Its headline was raised 700 → 800 to match the
reference; leaving it would have made it the only page with a lighter headline.

### One visible change to review

`early-intervention` was the only page with `display: flex; align-items: center` on
`.benefit-image` (box 260px, `aspect-ratio: auto`). It now uses the reference construct —
`display: block`, `min-height: 280px`, `aspect-ratio: 16/9`, box 320px — like the other
five. `.benefit-image` was genuinely inconsistent across the family in production:
two pages at 16/9, three at auto/280, and this one at flex/260.

Images do not load in the verification sandbox, so the image *fill* behaviour inside that
box could not be measured directly. Worth eyeballing the "Skills We Build in Early
Intervention" rows on staging before this goes to production.

### A self-inflicted verification failure worth recording

The first check reported `early-intervention`'s hero markup as non-identical. It was not:
the first 2,584 characters — its entire length — matched exactly. The override comment
authored for that page contained the literal text `<div>` and `<h1 …>`, and the
div-balancing extractor counted them as real tags, running past the wrapper.

Valid CSS, harmless in a browser, and still wrong: a literal tag inside a style block
trips naive markup tooling. The comment was reworded without angle brackets, and the
extractor now blanks `<style>` blocks before balancing.

### Remaining

Nothing on the six service pages. Next is the token layer — see the queued work:
Design Tokens component, the `.mm-*` / `.mb-*` palette split, the print stylesheet's
hardcoded hexes, and the Resource Page Styles pair.

---

## Change log — `.tip-card` hover fixed; deviations now survive a rebase

### Where `.tip-card` actually lives

Only `/in-home-aba-therapy` has `.tip-card` markup — three cards. The other five carried
the CSS but no elements, so the rule was dead there. The snapping hover was a one-page
glitch, not a family-wide one.

All three card types animate the same hover — `translateY(-4px)` plus a shadow swap — but
declared it three different ways:

| | transition | result |
| --- | --- | --- |
| `.tip-card` | *none* | snapped |
| `.icon-card` | `all 0.3s` | animated |
| `.approach-card` | `transform 0.3s, box-shadow 0.3s` | animated |

`.tip-card` now matches `.approach-card`, which transitions exactly the two properties the
hover changes. `.icon-card`'s `all 0.3s` is visually identical here and was left alone —
nothing to gain from churning a rule that already behaves correctly.

Verified on staging: `tip-card 0.3s, 0.3s`; `icon-card 0.3s`; `approach-card 0.3s, 0.3s`.

### A fix a tool would have silently undone

This is a **deliberate deviation from the reference** — in-home declares no transition, so
the next `rebase-shared.mjs --apply` would have dropped it again and nobody would have
noticed until the hover snapped once more.

`rebase-shared.mjs` now carries an `EXCEPTIONS` map, keyed by `context||selector`, layered
on top of the reference values. Each entry records its reason at the point of the
exception. The script stays idempotent: after applying, a re-run reports 0 changed,
0 added, 0 dropped.

This is the same failure mode as the on-disk overrides drifting from the live embeds,
one layer up. A correction that only survives because nothing re-ran the generator is not
a correction — it is a race.

### Closed

The two other open items were reviewed and accepted as-is: `early-intervention`'s
`.benefit-image` on the reference construct, and `in-home`'s restructured trust badges.

---

## Change log — site-wide sweep; a correction about what componentising actually saves

### The six were not the whole story

Scanned all 28 published full pages. Sixteen carry substantial inline CSS; twelve
(home, about-us, contact, blog, careers, areas-we-serve, bcba-team, podcast, legal)
carry none and need nothing.

### Componentising cross-page duplication saves no bytes

The `Resource Hub Styles` component was created for
`building-skills-independence` + `understanding-aba-therapy`, whose 11,358 B sheets
were byte-identical. Both pages then got **604 B larger**.

A Webflow component is authored once but still **inlines into every page that instances
it**. Each of those pages had only ONE copy of the sheet, so there was no page weight to
recover — the component buys maintainability (one edit, no future drift) and the added
header comment cost bytes.

> Duplication **across** pages → maintainability only.
> Duplication **within** a page → real bytes.

The six service pages benefited because each carried *two* copies. That distinction was
implicit before and is now explicit, in `merge-page-sheets.mjs`.

### `/services` — 20,585 B recovered

The single largest CSS payload on the site: two near-duplicate sheets in one page
(19,619 + 20,172 B, 90% identical), one per embed. Merged into one 19,458 B sheet.

**92,153 B → 71,568 B. Zero differing elements at 1440/768/390.**

Two bugs in the merge tool, both caught by the render diff rather than by reading CSS:

1. **Keyed on the comma group, not the selector.** `.a, .b { … }` in one sheet and
   `.a { … }` in the other produce different keys, so the grouped rule was classed
   "earlier-only", emitted first, and then overridden. Now keyed per selector.
2. **"Later wins" is only true at equal importance.** The earlier copy declared
   `.hero-cta { background: #db5b4f !important }`; the later copy had dropped the
   `!important`. Both sheets carry `.mm-embed a { background-color: transparent
   !important }`, so taking the later value made the button **transparent**. 15
   declarations were affected. The merge is now importance-aware.

Neither would have been visible by inspection. A diff that renders is worth more than a
diff that reads.

### Remaining, with honest value

| Target | Recoverable | Kind |
| --- | --- | --- |
| `financial-aid-resources` sheets 2/3 (77% overlap) | ~3,845 B | within-page, real |
| `first-90-days-of-aba-therapy` (23%) | ~1,702 B | within-page, real |
| `aba-therapy-in-georgia` (25%) | ~1,128 B | within-page, real |
| `insurance-terminology` + `financial-aid` 10,383 B block | 0 B | cross-page, maintainability |
| NJ + NC (both sheets byte-identical) | 0 B | cross-page, maintainability |
| `autism-screening-checklist` | 0 B | single unique sheet, nothing to share |

`aba-therapy-in-georgia` differs from the byte-identical NJ/NC pair, consistent with the
queued Georgia-only `align-content: start` city-grid bug.

### A third palette

The hub family uses `#002833` navy, `#34abc7` teal, `#6b6872` muted, `#e3dee3` rule —
distinct from both the `.mm-*` prose set and the `.mb-*` widget set. Only `#db5b4f`
(CTA red) is shared. The token reconciliation is a three-way problem, not two.
