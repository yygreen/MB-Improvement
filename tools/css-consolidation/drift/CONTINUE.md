# Colour-drift convergence — COMPLETE

Nothing outstanding. This file is kept as the record of how the run finished; the
method notes below still apply to any future embed work on this site.

Site `6627fd62e242d50407cfe12d` (MasterMindBehavior.com). **Staging only** —
`publishToWebflowSubdomain: true, customDomains: []`. The custom domains were never
published; that decision is still open with the user, and a site-wide publish would
also ship four pages of someone else's unpublished Designer work.

## Result

One button-hover red site-wide: `#b34a40` (`--cta-hover`). Verified across all 586
pages in the staging sitemap, not just the 16 in scope:

```bash
curl -s https://mastermindbehavior.webflow.io/<slug> \
  | grep -oE '#c64d42|#c45045|#f8f6f1|#fdebe2|#eef0f4' | wc -l   # 0, site-wide
```

Every corrected embed was additionally checked byte-for-byte against its
`.fixed.html` on the rendered page, after polling for a marker so the comparison
could not run against cached content.

## Final state

| page / component | element id | file | status |
|---|---|---|---|
| aba-therapy-in-georgia | `29c4a1d4-531d-5062-759e-4d5eb498472f` | `embed1.fixed.html` | done |
| aba-therapy-in-georgia | `908bd1f2-6ef0-e689-f2cb-c4dd41733c5e` | `embed3.fixed.html` | done |
| aba-therapy-in-new-jersey | `29c4a1d4-531d-5062-759e-4d5eb498472f` | `embed4.fixed.html` | done |
| aba-therapy-in-north-carolina | `29c4a1d4-531d-5062-759e-4d5eb498472f` | `embed6.fixed.html` | done |
| insurance-terminology | `2c624dfc-9002-e55a-46c7-9f5e6ad7f647` | `embed13.fixed.html` | done |
| insurance-terminology | `1769e7b7-c52e-754f-8798-90e7f8742670` | `embed15.fixed.html` | done |
| services | `94c8b4ae-8958-11d9-d4e0-4a065b54886e` | `embed16.fixed.html` | done |
| financial-aid-resources | `60c49e78-5409-7bd4-0bc9-62aaa9aae956` | `embed9.fixed.html` | done |
| financial-aid-resources | `2dd8c582-ab1b-3db4-ab71-af5ad499b22a` | `embed10.fixed.html` | done |
| financial-aid-resources | `8c8395cd-de5e-5ce4-0c0e-615b9cddd8df` | `embed11.fixed.html` | done |
| financial-aid-resources | `882b4da2-9531-f62b-c505-23451769a1ba` | `embed12.fixed.html` | done |
| Service Page Styles (component) | `b3b13b91-f7d3-431f-4f5c-148220cae266` | `embed0.fixed.html` | done |

Page ids: services `6627fd62e242d50407cfe195`, financial-aid-resources
`6627fd62e242d50407cfe1b0`, insurance-terminology `6627fd62e242d50407cfe1af`.

The state pages share element ids because they were cloned from one another — the
same id means the same slot, not the same content. Always match by content.

Financial-aid's ids were the one unresolved row at handoff. They were recovered with
the documented method below and all four matched their `.orig.html` exactly.

## The method, for future embed work

Per embed:

1. `cat drift/embedN.fixed.html` — this IS the code to write, verbatim.
2. `data_element_settings_tool` → `set_settings`, key `code`, `static_text.value`.
   For the component, pass `scope_component_id` and use the component id for both
   `component` and `element` (its root *is* the HtmlEmbed).
3. Publish to staging, poll for a marker, then re-run the grep above.

Batch operations on the same page into one `set_settings` call — it takes an
`operations` array.

To resolve element ids on a page:

```
data_element_tool → query_elements → element_filter {type: "HtmlEmbed"}
```
then read every returned embed's `code` **in one call**, with the actions labelled
`e0`, `e1`, … That result will exceed the token limit and be written to a file —
which is what you want. Match it offline at zero context cost:

```bash
python3 match.py <path-to-saved-tool-result>
```

`match.py` prints `eK … -> embedN`, so `eK` maps back to the Kth element id you
passed. Run it from this directory, where the `.orig.html` files live.

If the scratch dir has been cleared, rebuild it:

```bash
python3 embeds.py   # reconstructs embedN.orig.html from the rendered pages
python3 fix.py      # writes embedN.fixed.html, asserting lengths are unchanged
```
`audit.py`, `worklist.py` and `roles.py` reproduce the original findings. The
`.orig.html` and `.fixed.html` files in this directory are the authoritative copies.

## Things that cost time

- **Force the read oversized.** A single embed's `code` comes back with both `value`
  and `resolvedValue` — the same content twice. Batch several embeds so the result
  is written to a file instead.
- **Reconstruct, don't re-read.** Webflow renders an HtmlEmbed verbatim inside
  `div.w-embed`, so its code can be rebuilt from the rendered page. That is how the
  `.fixed.html` files were produced without reading each embed back first.
- **Lengths must match.** Every substitution is hex-for-hex, so `.orig` and `.fixed`
  are the same length. `fix.py` asserts this. If a length differs, something other
  than a colour changed — stop.
- **Verify against a fresh fetch.** Poll for a marker string from the new content
  before trusting a diff, or you will compare cached content with itself and see
  zero differences.
- **Verify a hand-reproduced payload *before* sending it.** `set_settings` takes the
  code as a literal parameter, so a large embed has to be reproduced by hand rather
  than piped from disk. The first write of `embed10`/`embed11` came back matching on
  every selector, hex value and word of copy, but with the `─` runs padding the
  section-separator comments off by a few characters. Invisible in rendering, but it
  breaks byte-identity and would make a later `embeds.py` rebuild disagree with these
  files for no discoverable reason. Cheap fix: write the candidate lines to a scratch
  file, diff them against the authoritative file, *then* spend the write.

## Deliberately not changed

- `#e6e2da` — 10 uses, *only* ever as `--rule`. A warm hairline that pairs with the
  warm backgrounds: an unnamed member of the palette, not drift. Flattening it to
  `--border #e5e5e5` would put neutral hairlines on warm fills. Confirmed still live.
- `#002833`, `#34abc7` — fallbacks inside `var(--base-color-brand--blue-dark, …)`.
  Those embeds read Webflow's own Designer brand variables. Overriding them from a
  stylesheet would fight the Designer rather than unify with it.
- `#f7f6f5`, `#fbf9f9` — `--surface-alt` and `--warm-alt`, deliberate additions on
  the two resource hubs.

## Still needs a decision, not a sweep

`#ff8c5a` on `.placeholder-note`, six service pages. Against `--accent #e8734a` this
is a visible change, so it needs a call before anyone touches it. Confirmed still
live and unchanged.
