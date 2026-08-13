# Correction: the tel URI claim was overstated (2026-08-13)

I described `tel:732.813.7333` on `/financial-aid-resources` as "not a
valid tel URI" whose button "won't dial on many phones", and changed it to
E.164 on that basis. **That was wrong, and it was asserted without being
tested.**

## What was tested afterwards

All four forms parse identically as `tel:` URIs in Chromium:

| href | protocol | pathname |
|---|---|---|
| `tel:732.813.7333` | `tel:` | `732.813.7333` |
| `tel:7328137333` | `tel:` | `7328137333` |
| `tel:+17328137333` | `tel:` | `+17328137333` |
| `tel:+1-732-813-7333` | `tel:` | `+1-732-813-7333` |

RFC 3966 lists `.`, `-`, `(` and `)` as **visual separators**, which are
legal inside a tel URI. Dialers strip them. The dots were never the defect.

## What is actually true

RFC 3966 wants a global number beginning `+`, or a local number carrying a
`;phone-context=` parameter. `tel:732.813.7333` is a local number with
neither. So is the site nav's `tel:7328137333`, which I had described as
fine. Both are equally non-strict, and in practice both dial on iOS and
Android. The realistic failure case is a visitor outside the US whose
dialer has no country context to prepend.

## What was not tested, and cannot be here

Whether a call connects. That needs a handset on a real network. The only
claim supportable from this environment is that browsers parse and accept
the href.

## Consequence

The E.164 change in `content/pages/financial-aid-resources.embed.html`
stands, because it is marginally better practice and harmless. But it is an
improvement, not a fix, and the hero embed should not be prioritised on the
strength of my original claim.

## Rule this reinforces

The house rule is that an unverifiable citation gets flagged, never
softened. The same applies to a claimed defect: assert it after testing, or
label it as suspected. "Won't dial on many phones" was a testable claim
stated as fact without the test.
