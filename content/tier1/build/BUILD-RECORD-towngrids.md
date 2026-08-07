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

## Layout pass (2026-08-07)

Four changes on top of the split, all generated by `gen-embed-split.py`:

1. FAQ section is white, closing CTA beige. Both are now stated explicitly in
   part 2's stylesheet rather than inherited, so neither depends on what happens
   to sit above it.
2. The "Where we serve" section is gone. Its paragraph of inline town links was a
   weaker duplicate of the navy Town Grid that now sits directly above it.
   Gate: no page may contain "Where we serve" or an /areas-we-serve/ link in
   either embed. Verified on staging - all 20 such links on the page are inside
   `.mm-towns`.
3. Hero is two columns, text left and placeholder image right, copying
   /in-home-aba-therapy: `minmax(0, 1.05fr) minmax(0, 1fr)`, gap
   `clamp(32px, 5vw, 64px)`, collapsing to one column at 900px. Values read off
   that page. Rendered at 1280px: 573px / 546px.
4. Hero column widened 900 -> 1200. A two-column hero needs it, and 1200 also
   matches the /aba-therapy-in-new-jersey reference. Body sections stay at 900,
   which is the better measure for prose.

The image is a labelled placeholder (`.mm-hero__placeholder`) until real art is
chosen; swapping it for an `img` needs no CSS change, `.mm-hero__media img` is
already there.

### Not a defect: the rendered phone number

Staging renders the hero button as "Call 732.427.8412" while the payload says
732.813.7333. That is CallRail's dynamic number insertion (`swap.js`, in the site
head) rewriting numbers for call tracking - it does the same to the number in the
global nav. The authored source is correct and the program's
"732.813.7333 only" rule is not violated; the swap happens in the browser.

## Hero trim + width alignment (2026-08-07)

Hero copy: three paragraphs beside an image was too much. The hero keeps the hook
and the one-line positioning sentence. The middle paragraph is NOT deleted - on
every page it carries the only link to the matching service page
(/early-intervention, /parent-training, ...), so deleting it would drop that
internal link entirely. It moves to the top of the first body section, where it
reads as a lead-in. Gated: the middle paragraph must contain a link, must appear
exactly once after the move, and the hero must be left with exactly two.

Widths: the hero ran 1200 and body sections 900 centred, so hero text began about
160px left of every heading below it. Sections now share the hero's 1200
container. Widening alone would leave prose running the full 1200, so paragraphs
and the accordion carry a 62ch measure inside it. Tables deliberately keep the
full width.

Measured on staging at 1440px - everything on one left edge:

    eyebrow 120, h1 120, hero copy 120, all five h2 120, body prose 120,
    accordion 120, table width 1200

x=120 is also where /aba-therapy-in-new-jersey starts its content, so the state
pages and the hub now share a left edge.

## Width, corrected (2026-08-07)

The previous pass aligned left edges but capped prose at 62ch, so the copy moved
without widening - it sat in the left two-thirds of an empty 1200 container. All
measure caps are gone now: the per-paragraph cap, the accordion cap in embed 2,
and the hero intro's own 62ch, which lives in the SOURCE embeds and so had to be
stripped in `align_widths` rather than in the generator's own text.

Measuring width rather than only position also caught a third block: the town
grid component sat at left 170 / width 1100 between two 1200 embeds. Its
`.mm-towns__inner` is now 1200 too, in `gen-town-grids.py` and in the NC
component.

Measured on staging at 1440px:

    EMBED 1  hero inner    120  1200
    EMBED 1  section 1-3   120  1200
    EMBED 1  body para     120  1200
    EMBED 1  table         120  1200
    TOWN GRID              120  1200
    EMBED 2  section 1-2   120  1200
    EMBED 2  accordion     120  1200
    EMBED 2  answer para   120  1200

The hero copy stays 582 - it is the left column of the two-column hero, not a
measure cap.

NOTE for the rollout: the Town Grid components for NEW JERSEY and GEORGIA still
carry `max-width: 1100px`. Each is a component, so one edit fixes all four pages
in that state.

## Rollout progress (2026-08-07)

NORTH CAROLINA COMPLETE - all 4 pages verified on staging: two embeds each,
town grid between them, both payloads byte-identical to the generated files,
accordion live, town grid container at 1200, exactly one h1 per page.

    early-intervention-north-carolina    done
    parent-training-north-carolina       done
    behavior-support-north-carolina      done
    transition-planning-north-carolina   done

REMAINING: the 8 New Jersey and Georgia pages, plus their two Town Grid
components, which still carry `max-width: 1100px`.

Component ids for the rest of the rollout:
    Town Grid NJ   b9c3e0ea-22fc-0b54-2f3e-85eb8aa8d263
    Town Grid GA   108392e7-... (read from a Georgia page tree)
    Town Grid NC   69c4d422-8f49-77f9-6024-b3da71dd561d   (already at 1200)

Per page the sequence is: create an HtmlEmbed AFTER the existing one (never
anchored on the town grid - the builder rejects that), move_element the town grid
`before` the new embed, write part 2, then truncate part 1. Writing part 2 before
part 1 matters: the reverse order leaves the page with no FAQ and no closing CTA
if the second call fails.

## CTA byline (2026-08-07)

A paragraph between the closing headline and the buttons, per service with the
state name inserted so the twelve pages do not close on the same sentence.

    early-intervention   "Tell us what you are seeing at home and we will walk you
                          through what starts when in {state}..."
    parent-training      "Bring the routine that is hardest right now..."
    behavior-support     "Describe what is happening at home... anywhere in {state}."
    transition-planning  "Tell us where your child sits in the {state} timeline..."

Each describes what the conversation IS rather than what it will achieve - the
copy gates forbid outcome guarantees, and a closing CTA is exactly where that
temptation lives. Gated against the same forbidden-token list as the rest.

Touches part 2 only (confirmed: no part 1 file changed), so pages already split
needed just their second embed rewritten.

Gate that needed tightening: counting the class name matched twice, because the
rule also appears in part 2's stylesheet. It counts the element now.

## Rollout status

    NORTH CAROLINA   4/4 complete
    NEW JERSEY       4/4 complete
    GEORGIA          4/4 complete

ROLLOUT COMPLETE - 12/12 verified on staging, every check passing:

    two embeds per page, town grid between them (order verified by offset)
    both payloads byte-identical to the generated files
    6 accordion items per page
    closing CTA byline present
    town grid container at 1200 on all three components
    exactly one h1 per page
    zero /areas-we-serve/ links outside the town grid

All three Town Grid components (NJ, GA, NC) now carry max-width 1200.

8/12 verified on staging: two embeds each, both payloads byte-identical to the
generated files, closing byline rendering, town grid container at 1200, and no
page carrying the withdrawn "anywhere in {state}" wording.

## Byline correction

The behavior-support byline originally ended "...would involve, anywhere in
{state}." The clause read as filler and was withdrawn on request, for all three
states rather than just the one it was spotted on. The sentence now ends on the
plan. The generator carries a note so nobody re-adds the state to this one line:
every phrasing that bolted it on read worse than leaving it off.
