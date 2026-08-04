# Finishing the colour-drift convergence

Everything needed to finish is in this directory. Nothing has to be re-derived.

Site `6627fd62e242d50407cfe12d` (MasterMindBehavior.com). **Staging only** —
`publishToWebflowSubdomain: true, customDomains: []`. Never publish to the custom
domains; that decision is still open with the user, and a site-wide publish would
also ship four pages of someone else's unpublished Designer work.

## What "done" means

One button-hover red site-wide: `#b34a40` (`--cta-hover`). The check:

```bash
curl -s https://mastermindbehavior.webflow.io/<slug> \
  | grep -oE '#c64d42|#c45045' | wc -l    # must be 0
```

## State

| page | element / component id | file | status |
|---|---|---|---|
| aba-therapy-in-georgia | `29c4a1d4-531d-5062-759e-4d5eb498472f` | `embed1.fixed.html` | done |
| aba-therapy-in-georgia | `908bd1f2-6ef0-e689-f2cb-c4dd41733c5e` | `embed3.fixed.html` | done |
| aba-therapy-in-new-jersey | `29c4a1d4-531d-5062-759e-4d5eb498472f` | `embed4.fixed.html` | done |
| aba-therapy-in-north-carolina | `29c4a1d4-531d-5062-759e-4d5eb498472f` | `embed6.fixed.html` | done |
| insurance-terminology | `2c624dfc-9002-e55a-46c7-9f5e6ad7f647` | `embed13.fixed.html` | done |
| insurance-terminology | `1769e7b7-c52e-754f-8798-90e7f8742670` | `embed15.fixed.html` | done |
| **services** | `94c8b4ae-8958-11d9-d4e0-4a065b54886e` | `embed16.fixed.html` | **TODO** |
| **financial-aid-resources** | *not yet resolved* | `embed9,10,11,12` | **TODO** |
| **Service Page Styles** (component) | `b3b13b91-f7d3-431f-4f5c-148220cae266` | `embed0.fixed.html` | **TODO** |

Page ids: services `6627fd62e242d50407cfe195`, financial-aid-resources
`6627fd62e242d50407cfe1b0`, insurance-terminology `6627fd62e242d50407cfe1af`.

The state pages share element ids because they were cloned from one another — the
same id means the same slot, not the same content. Always match by content.

## The loop

Per embed:

1. `cat drift/embedN.fixed.html` — this IS the code to write, verbatim.
2. `data_element_settings_tool` → `set_settings`, key `code`, `static_text.value`.
   For the component, pass `scope_component_id` and use the component id for both
   `component` and `element` (its root *is* the HtmlEmbed).
3. Publish to staging, poll for a marker, then re-run the grep above.

Batch operations on the same page into one `set_settings` call — it takes an
`operations` array.

## Resolving financial-aid's element ids

```
data_element_tool → query_elements → element_filter {type: "HtmlEmbed"}
```
then read every returned embed's `code` **in one call**. That result will exceed
the token limit and be written to a file — which is what you want. Match it offline
at zero context cost:

```bash
cd /tmp/wf/sweep && python3 match.py <path-to-saved-tool-result>
```

`match.py` prints `e0 … -> embedN` per element, in the order the actions were sent,
so `eK` maps back to the Kth element id you passed.

If `/tmp` has been cleared, rebuild it:

```bash
python3 embeds.py   # reconstructs embedN.orig.html from the rendered pages
python3 fix.py      # writes embedN.fixed.html, asserting lengths are unchanged
```
Both scripts, plus `match.py`, are in the session scratchpad; `audit.py`,
`worklist.py` and `roles.py` reproduce the original findings. The `.orig.html` and
`.fixed.html` files in this directory are the authoritative copies.

## Things that cost me time

- **Force the read oversized.** A single embed's `code` comes back with both `value`
  and `resolvedValue` — the same content twice. Batch several embeds so the result
  is written to a file instead.
- **Reconstruct, don't re-read.** Webflow renders an HtmlEmbed verbatim inside
  `div.w-embed`, so its code can be rebuilt from the rendered page. That is how the
  `.fixed.html` files were produced without reading each embed back first.
- **Lengths must match.** Every substitution is hex-for-hex, so `.orig` and `.fixed`
  are the same byte length. `fix.py` asserts this. If a length differs, something
  other than a colour changed — stop.
- **Verify against a fresh fetch.** Poll for a marker string from the new content
  before trusting a diff, or you will compare cached content with itself and see
  zero differences.

## Deliberately not changed

- `#e6e2da` — 10 uses, *only* ever as `--rule`. A warm hairline that pairs with the
  warm backgrounds: an unnamed member of the palette, not drift. Flattening it to
  `--border #e5e5e5` would put neutral hairlines on warm fills.
- `#002833`, `#34abc7` — fallbacks inside `var(--base-color-brand--blue-dark, …)`.
  Those embeds read Webflow's own Designer brand variables. Overriding them from a
  stylesheet would fight the Designer rather than unify with it.
- `#f7f6f5`, `#fbf9f9` — `--surface-alt` and `--warm-alt`, deliberate additions on
  the two resource hubs.

## Needs a decision, not a sweep

`#ff8c5a` on `.placeholder-note`, six service pages. Against `--accent #e8734a` this
is a visible change, so ask before touching it.

## After the last embed

1. Re-run the 16-page sweep (`audit.py`) and confirm `#c64d42` and `#c45045` are gone.
2. Flip the `applied` column in `README.md`.
3. Append a change-log entry to
   `audits/2026-07-30-mastermind-behavior-technical-audit.md`.
4. Commit and push to `claude/mastermind-behavior-css-unify-es1c30`; PR #1 is open
   and draft.
