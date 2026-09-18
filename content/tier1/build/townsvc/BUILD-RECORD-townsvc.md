# Build record: town services block staged (2026-08-09)

Staged on the Areas We Serve collection template per "Can you stage this
block now", with a 3-town demo. Placement as re-confirmed: after the final
CTA section ("Nurturing potential..."), before the footer. Verified on
staging; production untouched.

## The embed-token trap (recorded so nobody repeats it)

First attempt was a single HtmlEmbed whose code carried Webflow CMS-binding
tokens ({{wf {"path":...} }}), mirroring the syntax the template's own SEO
title stores. Page-settings fields resolve those tokens; EMBED CODE WRITTEN
VIA THE API DOES NOT - they render literally. The embed was built to fail
closed (hidden unless data-sk equals a real state key), so nothing broke,
but the approach is a dead end. Field insertion in embeds is a Designer-
editor feature, not a property of the stored code string.

## The build that works: native elements, real bindings

- Style-only HtmlEmbed 20121375-5646-1783-51cb-c7c2302127b7 (CSS targets
  data-mm-svc attributes; no markup, no tokens).
- Native DOM tree after it: section[data-mm-svc] > div[data-mm-svc-inner] >
  h2 (static span + span with text BOUND to `state`) + p[data-mm-svc-lede]
  (static span + bound span + ".") + nav[aria-label="ABA services",
  data-mm-svc-nav] > 4 Link elements. Section element id
  b8619ad4-9890-281b-43b7-31f25725e8f9.
- Hrefs: `link` setting bound to four new Link fields
  (service-link-{early-intervention,parent-training,behavior-support,
  transition-planning}); Link fields take plain URL strings, not objects.
- Visibility: bound to new Switch field `show-services-block` - visibility
  bindings REQUIRE a boolean source; binding to the PlainText state-key is
  rejected as incompatible. Server-side conditional: a town with the switch
  off omits the block from markup entirely (better than the CSS-hide spec).
- DOM `text` and Link `link`/`text` settings are bindable; bindings must be
  applied AFTER element creation (builder-time bindings fail with "Element
  is not inside a CMS context").

## Verified on staging

jersey-city, savannah, elizabeth-city: block present after the final CTA,
heading/byline carry the bound state name, all four hrefs carry the correct
state path, aria-label intact, no raw tokens anywhere. edison (no switch):
block absent from markup. All 12 target pages 200. Screenshots sent.

## Backfill (still gated on the typed confirmation "BACKFILL 213")

Per item, derived from `state`: state-key, show-services-block=true, and
the four service-link paths. 213 live towns (NJ 115 / GA 78 / NC 20);
exclude any a-state=true items. Chunks of <=100, then publish items, then
staging publish + link-audit sampling every state.

## Background softened (same day)

Client: the flat beige band with a border-top "looks weird" against the
rounded CTA card above; suggested a white-to-beige gradient. Shipped:
border-top dropped, background now
radial-gradient(ellipse at 80% 0%, rgba(59,165,168,0.08), transparent 55%)
over linear-gradient(180deg, #fff 0%, #f9f6f1 60%), top padding widened to
clamp(44px, 6vw, 72px). The teal radial deliberately mirrors the Tier 1
hero treatment so the block shares a visual language with the pages it
links to. Verified in context on staging (jersey-city); screenshot sent.

## Gradient revision 2 (same day)

Client flagged the teal radial tinting the block's top edge ("white on the
top"). Radial removed; background is now a plain
linear-gradient(180deg, #fff 0%, #f9f6f1 65%) - pure white where it meets
the CTA card, warm behind the cards. Verified in context on staging.

## Full rollout (2026-08-09, per "roll out to all town pages")

The REST route died on first call - 401, the exposed token had been rotated
- so the rollout ran through the MCP connection in five state-sharded
windows (slug-sorted, disjoint offsets) executed by parallel subagents:
NJ 0-57 and 58-114, GA 0-38 and 39-77, NC 0-19. Each shard wrote only the
six derived fields, skipped items already current (the 3 demo towns),
published its items, and wrote a manifest (banked in this directory).

Reconciliation: 213 unique towns across manifests, zero overlaps, per-state
counts exactly NJ 115 / GA 78 / NC 20, 210 written + 3 already current,
213 published, zero errors.

Verified after the staging publish: 24 towns sampled across the three
states (10 NJ / 8 GA / 6 NC, seeded random) - block present after the
final CTA, bound state name rendering, all four hrefs carrying the
correct state path, aria-label intact - 24/24 PASS. Edison, the town
used earlier to prove the block absent without the switch, now renders it.

Staging subdomain only; production untouched. The block reaches production
whenever the site's next production publish runs, per the agreed ship order.
