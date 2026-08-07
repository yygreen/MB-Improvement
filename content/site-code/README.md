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

## Eyebrow colour unification

Before: four colours across 33 eyebrow elements on 25 pages.

    #3ba5a8  rgb(59,165,168)  x18   hubs, service pages, /in-home-aba-therapy, /services
    #34abc7  rgb(52,171,199)  x10   /blog topics + all nine /bcbas/ author eyebrows
    #2f8487  rgb(47,132,135)  x2    /bcba-team
    #186c78  rgb(24,108,120)  x1    /first-90-days-of-aba-therapy

After: 33 of 33 at #3ba5a8, the reference teal.

Five classes were corrected AT SOURCE via the style API, not patched over:

    .mm-eyebrow              #2f8487 -> #3ba5a8, plus 26->28px margin, 10->8px gap,
                             and font-family added (it had none, so the text was
                             falling back to system-ui)
    .mm-eyebrow-line         28x1px -> 24x2px
    .g90-eyebrow             #186c78 -> #3ba5a8
    .author-profile_eyebrow  #34abc7 -> #3ba5a8
    .author-box_eyebrow      hsla(191.43,58.57%,49.22%) -> #3ba5a8

The sixth, .mm-topics-eyebrow, is declared inside the /blog topics embed rather than
as a Webflow class. It is overridden in the site head block, prefixed with `body` for
(0,1,1): the embed's own rule is (0,1,0) inside a body <style>, which beats an
equal-specificity head rule on document order. Verified by measurement, not by
reading the CSS back.

NOT CHANGED, and left for a decision: the /blog topics embed uses #34abc7 for three
other things in the same block, the card top-borders, the card CTA text, and the
filter-status link. The brief was eyebrows, so only the eyebrow moved. That block's
eyebrow now differs from the cards beneath it.

.mm-eyebrow is shared with the state hubs, /insurance-terminology,
/financial-aid-resources and /autism-screening-checklist, whose embeds already
override it to exactly these values. Confirmed by before/after geometry snapshot:
those seven pages are byte-identical across the change. The class edit only had an
effect where the class was actually being used unoverridden, which is /bcba-team.
