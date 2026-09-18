# Mobile nav tagline copy change (2026-08-05)

Staged on the staging subdomain only; production still shows the old line.

## The change

Element: HtmlEmbed `447b192d-a6aa-a3a9-b95c-abc3f5dedef6` inside the
**navigation component** (`c29251c3-4c95-fee7-6218-95199d7ddce2`), class
`.mm-navtrust`. Mobile only: `display:none` above 991px, so it appears
under the CTAs in the open mobile menu.

Before: `BCBA owned. Serving New Jersey, Georgia and North Carolina.`
After:  `In-home ABA therapy, BCBA-owned. Serving New Jersey, Georgia and North Carolina.`

Only the `<p>` text changed; the `<style>` block is byte-identical.

Rationale (user asked for copy that makes the service clearer): "BCBA owned"
is insider shorthand and gives a cold visitor no idea what the company does.
The new line leads with the plain-English service and keeps the credential
directly behind it. "BCBA-owned" is hyphenated to match the dominant style
used in CMS copy elsewhere on the site. Two other options were offered
(credential-first, and a longer "for children with autism" variant); the
user chose this one.

## Scope warning

This is the FIRST edit this session to client-approved GLOBAL chrome. The
nav is a component, so the change is live on EVERY page of the staging site
(verified on the home page, a generic service page, a state hub, a Tier 1
state page and /contact). It must ride the same sign-off as the rest of the
Tier 1 work before production publish #1.

Copy gates: no em dash, no RBT, no clinic/center, no guarantee, phone
unchanged (the visible number is swapped at runtime by the call-tracking
script; the markup still points at tel:7328137333 in the sibling embed).

Reverting is one set_settings call restoring the original `<p>` text.
