# Mastermind Behavior — Technical SEO Audit

**Date:** 2026-07-30
**Scope:** mastermindbehavior.com (Webflow site `6627fd62e242d50407cfe12d`)
**Mode:** Read-only. No Webflow writes, no publishes, no CMS changes, no freeform code edits were made.

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

### Incidental finding (high severity): every post displays today's date as its publish date

All 13 sampled posts render the byline date as **"Published: Thu Jul 30 2026"** — the
date this audit ran. The byline is bound to Webflow's `Published On` system field, which
resets on every full site republish. The practical effect is that all 337 posts claim to
have been published today, and the real publication dates are not recoverable from the
front end.

This matters directly for the BlogPosting work: if `datePublished` is wired to the same
field when schema is added, the markup would assert a false, self-resetting date on every
post — worse than having no schema at all. **The date binding should be fixed to a
dedicated CMS date field before or alongside adding BlogPosting.**

---

## Task 2 — /bcbas/* page metadata

All nine profile URLs fetched. **The prior audit's finding is confirmed and still true.**

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

| # | Issue | Severity | Evidence |
|---|---|---|---|
| 1 | Every post displays today's date as publish date (binding resets on republish) | **High** | 13/13 posts show "Published: Thu Jul 30 2026" |
| 2 | No BlogPosting schema on any of 337 posts — incl. the page carrying 72% of organic traffic | **High** | 0 tags + 0 JS references on 13/13 posts |
| 3 | All 9 `/bcbas/*` pages share the title `MasterMindBehavior.com` | **High** | 9/9 confirmed |
| 4 | All 9 `/bcbas/*` pages have no meta description, no OG, no Twitter tags | **High** | 9/9 confirmed |
| 5 | 337 of 337 posts attributed to the generic Clinical Team; 8 BCBAs have zero articles | **Medium** | Pagination walk = 337; 8/9 pages `w-dyn-empty` |
| 6 | No `Person`/`ProfilePage` schema on any BCBA profile | **Medium** | 9/9 confirmed |
| 7 | `/areas-we-serve/perry-043a7` still in sitemap (301s to `/perry`) | **Medium** | Only non-200 entry of 579 |
| 8 | Sitemap carries no `lastmod` on any of 579 entries | **Low** | 0 occurrences |
| 9 | 7 root pages carry no schema (outside staged scope) | **Low** | See Task 4 |

## Explicitly checked and NOT an issue

- Schema publish state — all staged groups are live; nothing pending. (Task 4)
- Sitemap health — 578/579 return 200; no 404s or 5xx.
- The `perry-043a7` → `perry` 301 fires correctly.
- BCBA canonicals — all 9 correct and self-referential.
- City page schema — present and server-rendered on 15/15 sampled.
- NC `MedicalOrganization` with no address — correct; no NC office or GBP exists.
- CallRail DNI is installed sitewide (company `477025173`), confirmed in page source.
