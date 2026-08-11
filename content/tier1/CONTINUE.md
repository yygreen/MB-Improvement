# CONTINUE — Tier 1 state-service program, MasterMindBehavior.com

Handoff for a new Claude session. Written 2026-08-05, after the full 12-page
complex went live on staging. Read this top to bottom before touching anything.

## Standing constraints (never violate)

1. **Staging only.** Publish with `publishToWebflowSubdomain: true,
   customDomains: []`. NOTHING goes to production without Taylor's clinical
   sign-off, and nothing may be staged that is unsafe if someone else runs a
   full-site production publish (see "rides a publish" below).
2. Push all work to the session's designated branch. As of 2026-08-05 that
   is `claude/tier1-state-service-continue-fn9xeg`, fast-forwarded from
   `claude/mastermind-behavior-css-unify-es1c30` (PR #1) so it carries the
   full history. Never push elsewhere.
3. Site id `6627fd62e242d50407cfe12d`. Phone is 732.813.7333 only.
4. Copy gates: no em dashes in fresh client-facing copy (verbatim coverage
   rows are the sole exemption); Behavior Technicians / BT, never RBT; no
   clinic or center implied; no outcome guarantees; no competitor names;
   never attribute blog posts to named BCBAs (client-confirmed).
5. If a citation cannot be verified, FLAG it — never soften it.
6. Never hand-retype payloads: generate them, gate them with assertions,
   verify byte-identity against the rendered page afterward.

## What exists (all verified on staging, all banked in this repo)

12 pages at https://mastermindbehavior.webflow.io/<slug>, slugs =
{early-intervention, parent-training, behavior-support, transition-planning}
x {new-jersey, georgia, north-carolina}. Page ids, embed element ids, word
counts, verification results, citation status: see
`content/tier1/build/BUILD-RECORD.md` (NJ pilot),
`BUILD-RECORD-nj-set.md` (NJ other 3), `BUILD-RECORD-ga-nc-set.md` (GA/NC 8).

- Embeds banked byte-exact at `content/tier1/build/<slug>.embed.html`;
  generators `tools/tier1/gen-nj-pages.py`, `gen-ga-nc-pages.py` (style block
  is lifted programmatically from the pilot embed — single shared stylesheet
  by construction; hub table rows read verbatim from
  `tools/tier1/{georgia,north-carolina}-hub-rows.txt`).
- Verifier: `python3 tools/tier1/verify-staged.py` — h1/title/meta (unescape
  entities before comparing), embed line-identity, link 200s, Service
  JSON-LD, em dashes confined to <td>. Run after ANY publish.
- Link audit: `bash tools/seo/link-audit.sh staging` — currently RESULT: pass,
  0 Tier 1 targets pending.
- Schema validator: `tools/schema/validate-schema.py` (0 invalid on all 12).
- All 12: draft:false (so reviewable), sitemap-excluded, Service schema via
  `bulk_update_pages_schema_markup` (NOT update_page_settings — it silently
  stores null), no OG images yet, FAQPage schema deliberately absent.

## The gates (in order) and who holds them

1. **Taylor clinical review** of all 12 staging URLs. The 11 non-pilot pages
   are fresh Claude drafts — full review, not a trim pass. Reviewer flags
   live in the three BUILD-RECORD files ("NOT RE-VERIFIED" sections) and
   `content/tier1/transition-planning-new-jersey.review.md`.
2. **`BACKFILL 992`** — exact typed confirmation from the user before writing
   `state-key` (field id `b7eaa9f53404cc3f95776a69ee0a95f6`, collection
   `6642b822923646375241d310`): NJ 517 "new-jersey", GA 455 "georgia",
   NC 20 "north-carolina". Chunks of 25, 0.42s sleep, fieldData only (never
   flip isDraft), Designer tab must be closed. Dry-run already verified.
3. The hedged sentence "Your BCBA can contribute to the IEP process."
   (appears on all 3 transition pages) stays until the client's batched
   email answers attend-vs-written-input. Tighten after.

## Ship plan (client-confirmed; details in build/TOWN-SERVICES-BLOCK.md)

1. After Taylor sign-off: apply edits, regenerate FAQPage schema from FINAL
   Section 6 text, add OG images, flip pages sitemap-INCLUDED.
2. DONE 2026-08-05: the 9 nav-pathway link blocks are BUILT and STAGED
   (staging subdomain only), verified, and screenshotted for the user —
   approval still pending. Final shape after three rounds of user feedback:
   the 4 service pages with state variants have their EXISTING "Find Your
   Local Team" section retargeted to the service's state pages (6-line
   embed edit, gen-fylt-retarget.py, banked under build/linkblocks/fylt/);
   the 3 hubs carry the four-card block under the hero. SEVEN placements
   total: the in-home/skill-development strips were DROPPED on user
   decision (duplicated existing hub links). See
   build/BUILD-RECORD-linkblocks.md and
   build/linkblocks/ (embeds, manifest.json with element ids, generator
   tools/tier1/gen-link-blocks.py, verifier tools/tier1/verify-linkblocks.py).
   Session decision to review: in-home-aba-therapy and skill-development
   strips link to the three STATE HUBS (no per-state pages exist for them).
   The 12 pages stay OUT of the global nav — decided; do not revisit.
3. Run backfill (after typed confirmation).
4. **Production publish #1**: 12 pages + 9 link blocks + the long-staged
   old-path link fixes (tools/css-consolidation/linkfix/, -45 bytes each,
   already in Webflow). Then `bash tools/seo/link-audit.sh` against
   production, verify-staged against production URLs, and re-check the six
   service pages' fixed hrefs.
5. A few days later, **production publish #2**: the town services block —
   ONE HtmlEmbed on the Areas We Serve collection template, spec + approved
   mockup at `content/tier1/build/TOWN-SERVICES-BLOCK.md` /
   `town-services-block.mockup.html`. State-name heading + one fixed
   byline; client explicitly rejected town names in both. Conditional
   visibility on state-key is set. Never ship this before the 12 pages
   exist on production.
6. Extend link-audit to sample towns from EACH state (NC has only 20 items;
   don't let NJ's 517 mask a state-scoped bug).
7. Optional later experiment (client-agreed shape): town-name byline on NC's
   20 pages only, months post-launch, GSC-informed.

## "Rides a publish" warning (the sharpest live edge)

All 12 pages are NOT draft and NOT noindexed (the Data API cannot set
per-page robots). Protections today: sitemap-excluded ONLY — the "zero
inbound links" protection is GONE as of 2026-08-05: the 9 staged link
blocks sit on six production service pages and three production hubs, so a
full-site production publish now takes the 12 pages live WITH inbound
navigation. That order (blocks staged before production publish #1) is the
client-confirmed plan, but it sharpens this edge. Mitigate before the risk
materializes: add noindex via Designer page-settings head code, or flip the
pages to draft (breaks review URLs). The staged old-path link fixes ride
the same publish — that part is fine and intended.

## Traps already paid for (do not rediscover)

- `update_page_settings` silently drops jsonLdSchema; only
  `bulk_update_pages_schema_markup` persists.
- /areas-we-serve/greensboro, /greenville, /fayetteville are GEORGIA pages
  (first two 301 to the GA hub). NC lives at greensboro-nc, fayetteville-nc;
  greenville-urfem exists but was avoided (Jacksonville used).
- Rendered pages entity-encode apostrophes (&#x27;) — unescape before
  comparing metas. A site-wide marketing HTML comment contains an em dash —
  strip comments and scripts before em-dash checks.
- New pages report hasMoreChildren:true at depth 0 with an actually-empty
  body; check depth 1.
- Semrush: get_report_schema first; export_columns is an array of named
  columns; domain rankings via `resource_organic` with display_filter.
  phrase_organic returns NOTHING FOUND for low-volume state phrases.
- After any publish, poll the newest page for 200 before trusting diffs.
- /services does NOT load the shared "Service Page Styles" component; every
  other service page does. It carries a standalone copy of an older sheet, so
  "delete the local rule and let the shared one take over" is the WRONG fix
  there — it converges by value instead. See BUILD-RECORD-HERO-DRIFT.md.
- `tools/css-consolidation/rebase-shared.mjs` rebases onto a PRE-convergence
  snapshot of in-home-aba-therapy, so a run would have reverted the whole
  2026-08-04 hero convergence. It now refuses to run (exit 2) while the
  reference is stale. Re-snapshot the reference before rebasing again.
- The repo mirror of the shared sheet goes stale whenever the Designer is
  edited. Refresh it with `tools/tier1/sync-shared-from-live.py --apply`.
- GSC MCP may be unavailable; cannibalization checks so far are
  Semrush-only — carry that flag in records.

## Backlog (not Tier 1, don't lose)

RESOLVED 2026-08-11 (client-confirmed, verified): "15 unlinked city pages" and
"NJ 115-vs-100 Collection List cap" are both fixed. Measured on production the
same day: every town page reachable from /areas-we-serve, and 0 sitemap town
URLs lacking a hub link. Do not re-raise these.

OPEN, found 2026-08-11: the Areas We Serve collection holds TWO live items
named "Perry", both Georgia. `perry` (6674696ea34ecacbc4eb3d61) is the real
page with full Houston County content. `perry-043a7`
(66ad3c53921c8c113c3c241b) is an empty duplicate: content, local-detail,
final-cta and verify bodies all null. It is already sitemap-excluded and its
URL 301s to /areas-we-serve/perry, but because it is still LIVE the collection
list renders a second, identical "Perry" card on /areas-we-serve, and the
2026-08-10 services-block backfill wrote fields to it. Fix is to archive or
unpublish the duplicate item; awaiting client go-ahead (destructive). This is
also the whole explanation of the 213-vs-212 gap: 213 live non-hub items but
only 212 real town pages.

Remaining: 13th internal link on the pilot review doc (manual editor task); footer
h2->h6 heading jump site-wide; dead `.placeholder-note` CSS rule; sitemap
lastmod; button
system convergence (state `.mm-btn` spec as base, see
tools/css-consolidation/DESIGN-SYSTEM.md); possible Designer-styles port;
pilot page lacks links to its 3 NJ siblings (add post-review, one sentence);
sister-state footer links omitted everywhere (post-review decision).
