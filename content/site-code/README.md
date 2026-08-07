# Site-wide head custom code

`head.current.html` is the block as it existed BEFORE the Manrope 600 fix.
`head.new.html` is what is stored now: byte-identical prefix plus `head.addition.html`.

Keep these in sync by hand only through the append path. `set_site_freeform_code`
REPLACES the whole block, and that block carries CallRail's swap.js, Google Tag
Manager, Plausible, the ahrefs and Google verification meta tags, the paginated-URL
noindex script, and the canonical enforcement MutationObserver. Overwriting it with a
partial transcription would silently break tracking and canonicals sitewide.

Procedure used, and the one to repeat:

  1. get_site_freeform_code -> transcribe to head.current.html
  2. PROVE the transcription is exact before writing anything: fetch a rendered page
     and assert the transcribed string appears verbatim in it. Webflow emits this
     block into <head> unmodified, so a substring match is a real check. It passed at
     3,290 bytes.
  3. new = current + addition, assert new.startswith(current) and that CallRail, GTM,
     Plausible and fixCanonical all survive
  4. write, publish to the Webflow subdomain only, re-measure

## Why the addition exists

Webflow's self-hosted Manrope on this site ships only the 500 and 700 weights. CSS
font matching searches UPWARD first for any requested weight above 500, so every
`font-weight: 600` was silently resolving to the 700 face.

This is invisible to computed style, which reports the value CSS asked for, not the
face that rendered. The only reliable test is to measure advance width: render the
same string at 600 and at 700 and compare. Identical widths mean one face is serving
both.

Measured before, at 52px, string "Handgloves Meet Therapy 123":

    /in-home-aba-therapy   600 -> 735.70px   700 -> 746.81px   distinct, correct
    /bcba-team             600 -> 746.81px   700 -> 746.81px   identical, substituted

22 of 36 main pages were substituting. After adding the Google Fonts link sitewide:
36 of 36 distinct, 0 substituting.

The `-webkit-font-smoothing: antialiased` rule in the same block fixes the second,
compounding cause: 11 pages sat on the browser default of `auto`, which paints strokes
thicker. All 36 now report antialiased.
