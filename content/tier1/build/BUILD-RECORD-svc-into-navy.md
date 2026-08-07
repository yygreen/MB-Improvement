# Services baked into the navy Areas We Serve band

Three hub pages: /aba-therapy-in-north-carolina, /aba-therapy-in-georgia,
/aba-therapy-in-new-jersey.

## What moved

The `.mm-svc` block (four service cards) was a standalone embed sitting high on the
page, second section after the hero, on warm #f9f6f1. It is now the last block inside
the navy Areas We Serve section, after the town grid.

Measured section order on the NC hub before the change:

     97  mm-hero
    824  mm-svc                        warm #f9f6f1   <- was here
   1111  section-4 / section_logo      insurance logos
   1183  mm-section                    How In-Home ABA Works
   1924  mm-section--warm              Insurance and Coverage
   3771  mm-section                    What to Expect
   5212  section-2                     navy #192744   <- now here, after the towns
   5720  bottom-cta

NOTE this is a real information-architecture change, not only a visual one. The four
service links move from just under the hero to near the foot of the page. That was the
brief, but it is worth knowing: those are the only links from a hub to its four state
service pages.

## Restyle for the dark band

Kept: markup, headings, copy, hrefs, grid, card radius and padding.
Changed only what the dark background required.

    background        #f9f6f1                -> transparent (section-2 supplies navy)
    border-top        1px #e6e2da            -> 1px rgba(255,255,255,0.14)
    padding           clamp() with side pad  -> vertical only; section-2 gives 40px sides
    inner max-width   900px                  -> 1200px, to match the heading and towns
    h2 colour         #1a2744                -> #fff
    lede colour/size  #5a5a5a 16px           -> #b9c3d6 17px, matching the section lede
    card background   #fff                   -> #232f4e
    card border       #e6e2da                -> rgba(255,255,255,0.14)
    card text         #1a2744                -> #fff
    arrow / hover     #3ba5a8                -> #5fc6c9, the dark-band teal
    hover             box-shadow             -> background lift to #2a3757

## The New Jersey trap

NC and GA have a flat navy section: embed, then collection list. Anchoring the move
"after" the Collection List Wrapper put the block exactly where intended.

New Jersey does not. Its navy section wraps the towns in an explicit grid Block
(`#nj-cities-grid`, `.cards.cards-ga`) that contains TWO collection lists rather than
one. Anchoring after Collection List Wrapper 2 therefore placed the services INSIDE the
grid, between the two lists, where it became a grid item.

Caught by measurement, not by eye. The verifier compares the inner width of the block
against the section heading:

    NC  innerLeft 120  innerWidth 1200
    GA  innerLeft 120  innerWidth 1200
    NJ  innerLeft 120  innerWidth  227   <- exactly one town-grid column

227px is the measured column width of the town grid, which is what identified the
cause. Re-anchored after the grid Block itself rather than after the inner list.

## Verified on staging, all three

    inside the navy section      true
    after the town list          true
    effective background         rgb(25, 39, 68)
    inner left / width           120 / 1200, same as the section h2
    h2 colour                    rgb(255, 255, 255)
    card background / text       rgb(35, 47, 78) / rgb(255, 255, 255)
    .mm-svc instances per page   1   (no duplicate left behind)
    service hrefs                all four correct and state-matched on each hub

Staging only.
