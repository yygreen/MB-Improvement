# Build record: town grids on the 12 Tier 1 state pages (2026-08-05)

Built per "can you use the dynamic town element on the page that is also
incorporated on /aba-therapy-in-new-jersey". Staging subdomain only.

## What shipped

A "Towns We Serve Across {State}" section on each of the 12 state pages,
directly after the page's content embed and before the footer. Visual
language matches the hub city grid (navy #1a2744 section, white town links
in a responsive auto-fill grid, teal hover).

Delivered as THREE Webflow components in group "Tier 1", each instanced on
that state's four service pages:

| Component | id | Towns | Pages |
| --- | --- | --- | --- |
| Town Grid NJ | b9c3e0ea-22fc-0b54-2f3e-85eb8aa8d263 | 115 | 4 NJ |
| Town Grid GA | 108392e7-f0a9-4cfe-53ea-e45f13f3ec27 | 77 | 4 GA |
| Town Grid NC | 69c4d422-8f49-77f9-6024-b3da71dd561d | 20 | 4 NC |

Components (not 12 copies) so the town list has ONE edit point per state.
Generator: `tools/tier1/gen-town-grids.py`, reading `tools/tier1/towns.json`.
Banked markup: `content/tier1/build/towngrids/<state>.embed.html`.

Verified after publish: correct town count on all 12 pages, exactly one h1
each, and all 212 distinct town links return 200. verify-staged.py,
verify-linkblocks.py and link-audit.sh staging all still pass.

## The blocker: this could NOT be a real CMS Collection List

The hub grid is a genuine Collection List whose card link uses Webflow's
link mode "collectionPage" (link to the current item's page). That mode
cannot be reproduced through the Data API:

- Building the list works: DynamoWrapper source/filters/sort/limit set fine
  via set_settings, and the item TEXT binding to the Name field renders
  correctly (towns appeared, alphabetically, filtered by state).
- The LINK does not. `link = {mode:"collectionPage"}` publishes as
  `href="#"`. Adding `to.pageSlug` publishes the slug literally
  (`href="detail_areas-we-serve"`).
- `get_bindable_sources` on the card link returns 50 CMS sources, every one
  bindable only to string / textContent / altText / id / richText. NOTHING
  is bindable to a `link` value, so there is no API path to "link to
  current item".

A first pilot with 100 dynamic cards therefore rendered 100 dead links; it
was removed. The static grid is generated from the LIVE hub pages (the
client-approved source of truth) so the hrefs are real.

Trade-off: the grid does not auto-pick-up newly added towns. Re-run the
generator and re-apply if the town list changes. To make it truly dynamic
someone with Designer access can rebuild the list natively and set the card
link to "Current Areas We Serve" - one click per component.

## Data findings worth acting on

1. **The CMS holds 992 Areas We Serve items but only 212 are live.**
   NJ 517 / GA 455 / NC 20 by the `state` field, but the great majority are
   `isArchived: true` with `lastPublished: null`. Live counts, scraped from
   the three hubs: **NJ 115, GA 78, NC 20**.
   This matters for the pending `BACKFILL 992` task: writing state-key to
   all 992 would be writing mostly to archived items. Re-scope that gate to
   the ~212 live items before running it, and re-confirm with the user.
2. **Duplicate town names exist.** Georgia has two "Perry" items
   (`perry` and `perry-043a7`); the hub renders both. The generator dedupes
   by name and keeps the first, so GA shows 77 rather than 78. Worth a CMS
   cleanup decision.
3. The NC list includes `greenville-urfem` (the odd slug recorded earlier as
   avoided in Tier 1 copy). It IS live and returns 200, so it is included
   here; the earlier avoidance was about which city to name in prose.

## Traps recorded

- Publishing is rate limited (429 too_many_requests). Space publishes out;
  batch edits and publish once.
- A heading embed placed inside the navy section must use light colours;
  the first pass used the navy body colour and rendered invisible.
- The page's own copy also contains /areas-we-serve/ links, so counting town
  links must be scoped to inside `mm-towns__inner`, not the whole document.

## Embed split so the town grid sits mid-page (2026-08-07)

Asked for: one embed, then the navy town block, then a second embed carrying the
FAQ and the closing CTA.

Before, all 12 rendered as

    nav -> [one embed: hero .. where-we-serve, FAQ, closing CTA] -> Town Grid -> footer

so the navy slab landed after the page had already asked for the call. A Webflow
component cannot be nested inside an HtmlEmbed, so the only way to place it
mid-page is to cut the embed in two and put the component between the halves.

`tools/tier1/gen-embed-split.py` generates both halves from the banked embeds
(verified byte-identical to live for all 12 before generating) and gates:
sections are not reordered or lost, part 2 is exactly FAQ + CTA, divs and
sections balance, and the visible copy of part1 + part2 equals the original
character for character.

### The stylesheet stays in part 1 only

Every `.mm-*` rule lives in one inline <style> at the top of the embed, and it is
the only style block on the page carrying `.mm-section`. CSS applies by selector,
not DOM position, and both halves keep the `.mm-embed mm-t1` wrapper the rules
are scoped to - so part 2 needs no copy. Duplicating it would add ~4.7 KB per
page and create a second source of truth that could drift. Verified on staging:
the FAQ and CTA in embed 2 render fully styled.

### Two ordering traps

1. `data_element_builder` refuses `creation_position: after` when the anchor is a
   ComponentInstance - "Cannot insert elements directly into a component
   instance" - even though this is a sibling insert, not a nested one. Workaround:
   create the new embed after the EXISTING embed, then `move_element` the Town
   Grid component to sit `before` it. move_element has no such restriction.
2. Write part 2 into the new embed BEFORE truncating the original to part 1. The
   reverse order leaves the page with no FAQ and no closing CTA if the second
   call fails.

Verified on /early-intervention-north-carolina: render order is
hero -> sections -> TOWN GRID -> faq -> cta-close, both embeds byte-identical to
their generated files, visible copy unchanged against the original embed, and
still exactly one h1.
