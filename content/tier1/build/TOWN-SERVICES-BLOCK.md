# Town-page services block — approved spec (2026-08-05)

Client-approved design for the services block on the Areas We Serve
collection template (992 town pages). Visual reference:
`town-services-block.mockup.html` (same directory).

## Decisions (client-confirmed this session)

1. Heading: **"ABA services in {State Name}"** — state field, never the town.
   Client explicitly considered and rejected "ABA Therapy Services in {Town}".
2. Byline: **one fixed sentence**, state name is its only variable. Client
   explicitly rejected a town-name mention in the byline:
   "All four are delivered in your home by a BCBA-led team, anywhere we
   serve in {State Name}."
3. Four cards, fixed labels, no descriptors, no anchor rotation:
   Early Intervention / Parent Training / Behavior Support / Transition
   Planning -> `/{service}-{{state-key}}`
4. `<nav aria-label="ABA services">` semantics; block sits AFTER the town
   page's unique content, before the footer; warm background #f9f6f1.
5. Wrapped in conditional visibility: **state-key is set** — an item with a
   missing key renders nothing rather than a dead href.
6. Total fixed text ~30 words; the town name never appears anywhere in the
   block. Optional future experiment (client-agreed shape): town-name byline
   trialed on North Carolina's 20 pages only, months after launch, with GSC
   data — never a 992-page launch bet.

## Ship order (client-confirmed)

1. Taylor sign-off on the 12 state pages -> FAQ schema regenerated, OG
   images, sitemap-included
2. `BACKFILL 992` typed confirmation -> state-key written (NJ 517 /
   GA 455 / NC 20, chunks of 25, 0.42s pacing)
3. Production publish #1: the 12 state pages + the staged old-path link
   fixes; verify all 12 on the production domain
4. A few days later, production publish #2: this block on the collection
   template. The block must never go live before the state pages exist in
   production.

## Verification at ship

Extend tools/seo/link-audit.sh: sample several towns from EACH state
(NC's 20 must not hide behind the NJ majority); assert the block renders,
all four hrefs carry that town's correct state suffix, and return 200.
