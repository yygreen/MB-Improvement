# Hero image prompt, aba-therapy-funding-georgia

Replaces the shared photograph currently on the live page. Georgia went out
reusing the New Jersey hero (a parent at a kitchen table with paperwork),
which is state-neutral but means two funding guides carry the same image.
Webflow content-addresses by MD5, so the file even keeps its New Jersey
name in the URL.

Same house spec as New Jersey. The scene is deliberately not the same.

## Spec

    aspect        16/9
    delivery      WebP, >= 1600x900
    composition   subject left of centre; the blog template puts the title
                  beneath, so the right third can carry light and negative space
    safe area     outer 6% expendable
    thumbnail     also crop a 600x338 version; it must still read at 300px wide

## The prompt

> Candid documentary lifestyle photograph. Real, lived-in American family home,
> not a set. Natural light only. Warm neutral palette. 35mm, eye level, f/2.0,
> shallow depth of field. Unposed and mid-moment: nobody looks at the camera.
> Photographic realism, no illustration, no HDR.
>
> A father in his late thirties stands at a kitchen counter on a bright weekday
> morning, phone held to his ear with one shoulder, pen in hand, writing in a
> spiral notebook open on the counter in front of him. He is looking down at
> what he is writing, not into the distance. A mug and a set of car keys sit
> near his elbow. His posture is alert and slightly leaning in: someone taking
> down an answer he intends to hold somebody to, not someone receiving bad news.
> A child's backpack hangs on a chair back at the edge of frame, out of focus,
> the only sign that this is about a child. The child is not in frame.
>
> Georgia house: brick ranch interior, pine floors, wide low windows, a ceiling
> fan overhead, painted cabinets, warm humid morning light with strong sun
> falling across the counter. Pines and a crepe myrtle visible soft outside the
> window. Deep green summer foliage.
>
> Exclude: clinic, therapy office, classroom, waiting room. No medical equipment,
> clipboards, charts, scrubs, lanyards or ID badges. No logos, signage, screens
> showing content, or any legible text, including on the notebook page. No
> puzzle-piece imagery or autism-awareness symbolism. No state flags, peaches,
> or Southern-kitsch decor. No posed stock smiles, no eye contact with the
> camera, no thumbs-up. No watermarks. No insurance-company branding of any kind.

## Why this scene rather than New Jersey's

New Jersey's hero is a parent **reading** something that arrived: evening
light, a letter that has been read more than once. That matches a page whose
turning point is a denial.

Georgia's turning point is different. SB 118 put the medical necessity
determination with the covering entity, so the page's central instruction is
to make the insurer put things in writing: ask for the established criteria,
get the current terms, diary the annual redetermination. The matching image is
a parent **writing down** what they are being told, in the morning, on a call
they initiated.

Different verb, different time of day, different architecture. Two guides in
the same cluster should not look like the same photograph twice.

## The exclusions that are not stylistic

- **No clinic.** Program-wide copy gate, and this page sells in-home
  specifically. An institutional room contradicts the page it sits on.
- **No puzzle piece.** Widely rejected by autistic people and much of the
  advocacy world. On a BCBA-owned provider it would do real damage.
- **No legible text, and here it is the notebook that will betray you.** A
  generator asked for someone writing will happily invent a carrier name, a
  reference number and a dollar figure on the page. That is a fabricated
  document on a page whose entire argument is that every number is sourced,
  and which explicitly refuses to print a Georgia appeal deadline it could not
  verify. Keep the notebook page out of focus and unreadable.
- **No trademarks or trade dress.** No insurer branding, no recognisable
  product packaging, no logo on the notebook, phone or mug.

## What to check before accepting a candidate

1. Zoom to 200% on the notebook page and on any paper in frame. If any word or
   number resolves, reject.
2. Confirm no lanyard, badge, scrub top or clipboard crept in.
3. Confirm the room could not be mistaken for a waiting area.
4. Confirm the phone is a plain slab with no visible logo and a blank or
   unreadable screen.
5. Check the 600x338 thumbnail crop still reads as a person on the phone taking
   notes, not as an abstract of hands.
6. Confirm his expression reads as focused, not exasperated. The page is about
   the leverage a family has, not about how hard this is.
7. Confirm it does not read as the New Jersey hero with the furniture changed.
   Different posture, different light, different time of day.

## After a candidate is chosen

Upload as `aba-therapy-funding-georgia_hero-photo.webp` plus a 600x338
`_thumb-photo.webp`, then set `main-image` and `thumbnail-image` on item
`6a7c8d78e54812e5af77f596` and publish. The bytes must differ from the New
Jersey hero or Webflow will content-address them back to the same asset,
which is exactly how the current sharing happened.
