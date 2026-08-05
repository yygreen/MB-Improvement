# Build record: 9 nav-pathway link blocks (2026-08-05)

Ship plan step 2, built per "start working through this to staging, dont push
anything live yet". Staged on the staging subdomain only; production
untouched. AWAITING USER APPROVAL of the screenshots before these ride any
production publish (they are edits to client-approved pages).

## What was built

Three block types (the first two derived from the client-approved
town-services-block mockup tokens; the third from the site's own
"Find Your Local Team" section):

1. **Card-style states section** ("{Service} in Your State") on each of the
   4 service pages with state variants: markup mirrors the existing
   "Find Your Local Team" section and reuses its stylesheet classes
   (section-navy, areas-grid, area-card), wrapped in `div.mm-embed` because
   the shared sheet scopes every rule under it. Three cards link to that
   service's state pages. (Replaced the original "Available in:" strip on
   user request "can we not build a similar section for the services in
   state".)
2. **"Available in:" strip** on /in-home-aba-therapy and /skill-development
   (no per-state pages; links the three state hubs). User keep/drop call
   pending: these duplicate the hub links in each page's existing
   "Find Your Local Team" section.
3. **Four-card services block** on each of the 3 state hubs: heading
   "ABA services in {State}", the approved fixed byline sentence, and the
   four service links for that state.

Placement (repositioned 2026-08-05 on user feedback "find a better embed
position" — the first pass sat before the footer): one new HtmlEmbed per
page, now DIRECTLY UNDER THE HERO. On the six service pages the hero is its
own embed (af8a739b-...), so the strip sits between the hero and the
insurance-logos section. On the three hubs the main embed (29c4a1d4-...) is
just the hero, so the services block sits between the hero and the rest of
the state content / city grid. Pure move_element operations; no existing
element was edited; removal is one remove_element call per page.
NOTE: the 992-page town block (production publish #2, not yet built) keeps
its client-approved placement "after unique content, before the footer";
revisit with the client if the under-hero pattern should apply there too.

Generator: `tools/tier1/gen-link-blocks.py` (gates: no em dashes, no RBT /
clinic / center / guarantee tokens, href whitelist, single section root).
Banked byte-exact at `content/tier1/build/linkblocks/<slug>.embed.html`.
Element ids: `content/tier1/build/linkblocks/manifest.json`.
Verifier: `python3 tools/tier1/verify-linkblocks.py` (line-verbatim render
check, block-before-footer check, link 200s, no em dash in block). Run
2026-08-05 after the staging publish: all 9 pass. verify-staged.py and
link-audit.sh staging both still pass in the same run.

## Decision made this session (flagged for user in the screenshots)

/in-home-aba-therapy and /skill-development have no per-state Tier 1 pages,
so their strips link to the three state hubs (/aba-therapy-in-<state>)
instead. The other four strips link to their service's three state pages.

## Rides-a-publish escalation (read this)

Until now the 12 Tier 1 pages had ZERO inbound links from published pages.
These 9 blocks change that: they live on six production service pages and
three production hubs, so an unplanned full-site production publish would
now take the 12 pages live WITH inbound navigation. This was accepted by
the client-confirmed ship plan (blocks staged before production publish #1),
but the noindex/draft mitigation from CONTINUE.md is now more urgent, not
less. Do not let a production publish happen before Taylor sign-off.

## Traps recorded

- data_element_builder cannot use a ComponentInstance as a before/after
  anchor ("Cannot insert elements directly into a component instance");
  anchor on the preceding sibling with position "after" instead.
- The six generic service pages are clones sharing element ids: the
  pre-footer embed is 7c08cadb-3d4f-0168-4cee-601897904faa and the footer
  instance 18c8c568-5eef-41ab-ffa6-a404af56534e on ALL six. The three hubs
  share 908bd1f2-6ef0-e689-f2cb-c4dd41733c5e (pre-footer bottom-CTA embed)
  and bea2227e-ceaf-c889-b790-08b33ed57f46 (footer).
- HtmlEmbed code is written with data_element_settings_tool set_settings
  key "code" (static_text); discovered via get_settings value_type "code".
- The service pages' shared stylesheet scopes EVERY rule under `.mm-embed`;
  block markup outside that wrapper renders completely unstyled. Wrap any
  new embed's markup in `<div class="mm-embed">`.
- Screenshots in this container: Chromium resets TLS through the explicit
  agent proxy; instead add /root/.ccr/ca-bundle.crt certs to the NSS store
  (certutil -d sql:/root/.pki/nssdb -A -t "C,,") and launch Chromium with
  --no-proxy-server so the transparent egress gateway intercepts. Use
  waitUntil "load" (networkidle never settles: third-party trackers), and
  compute clip coords from getBoundingClientRect + scrollY, not
  boundingBox(), when clipping a fullPage screenshot.
- The GA hub carries a stray second navigation component instance outside
  page-wrapper (pre-existing; left alone).
- Existing pages render per-page dynamic tracking phone numbers
  (732.314.7512 / 732.631.3965 / 732.639.5368 / 732.838.7965 etc. in heroes,
  CTAs and footer) — presumably call-tracking swap on the client's approved
  pages. Fresh Tier 1 copy still uses 732.813.7333 only, per the standing
  constraint. Observation only; nothing changed.

## Open before production

1. User approval of the 9 screenshots (sent 2026-08-05).
2. Everything already listed in CONTINUE.md: Taylor sign-off, sign-off
   cleanup (edits, FAQPage schema, OG images, sitemap inclusion),
   BACKFILL 992 typed confirmation, IEP-sentence client email.
