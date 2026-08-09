# Build record: North Carolina hero images (2026-08-09)

Four generated hero images built into the NC Tier 1 pages, per "build the 4
for north carolina on staging". Assets uploaded via the Data API (create_asset
+ S3 multipart POST), CDN bytes verified identical to the local files before
wiring. Written into each page's part1 embed; NOT yet published - the publish
is held pending the production-reach decision recorded in CONTINUE.

## Source and selection

User-generated images pulled from a shared Drive folder (8 files, all
1376x768 JPEG). Matched to prompt frames by visual identification:

| Drive file (time) | Scene | Slot | Used |
| --- | --- | --- | --- |
| 9:17PM | kitchen, nesting cups | early-intervention | YES |
| 9:24PM | hallway, jacket zip | parent-training | YES |
| 9:28PM | living room, choice cards | behavior-support | YES |
| 9:32PM | laundry nook | transition-planning | NO - legible Tide and Gain logos |
| 9:37PM | reading "My First Animals" | EI alternate | held |
| 9:56PM | kitchen table, AAC fridge | BS alternate | held |
| 10:13PM | dishwasher | transition-planning | YES - replaces 9:32 |
| 10:21PM | porch, "Snowy Day" cover | GA porch | NO - recognizable published book cover |

The two rejections are the same failure class: identifiable third-party IP
in a commercial hero. The GA porch replacement with a generic cover ("A Day
Full of Joy") was approved in chat but is not in the Drive folder yet.

## Pipeline

- JPEG -> webp quality 82 (86-138KB each, from 650KB-7MB)
- The hero box is 4:3 object-fit:cover, so the center 1024x768 of each
  1376x768 frame is what renders. Each crop was rendered and inspected
  before upload: no story prop leaves the window on any of the four.
- Uploaded as <slug>-hero.webp; asset ids 6a78e39f714680f3b5abd614 (EI),
  6a78e3a0156a4015be093e13 (PT), 6a78e3a087d56fcc1023613c (BS),
  6a78e3a0736b942eb8a7bb57 (TP). CDN bytes cmp-identical to local.
- gen-embed-split.py HERO_IMG map filled for the four NC slugs; all
  generator gates pass; regeneration changed exactly the four NC part1
  files and nothing else. negtest-heroimg.py: all seven gates fire.
- part1 embeds rewritten via set_settings on the four pages (element ids
  per BUILD-RECORD-ga-nc-set.md; component half = page id).

## Verification still owed

verify-staged.py byte-compare of the rendered pages against the banked
part1 files runs at the next publish - held until the production decision.

## Addendum: New Jersey set + staging publish (same day)

Four more frames added to the Drive folder (10:26, 10:30, 10:37, 10:40 PM),
identified as the NJ set and built the same way: EI shape box, PT grocery
unpacking with BT observing, BS picture cards at the front door, TP teen
making his own lunch. One minor note accepted: plain "BLUE JAYS" block
lettering on the BS backpack - text only, no logo or trade dress, unlike the
rejected Tide/Gain and book-cover frames. Asset ids 6a78e6e6ada099bf0ebef310
(EI), 6a78e6e61af92c90aa0cfab6 (PT), 6a78e6e658560a803d64112e (BS),
6a78e6e60955b2e9f1a6acec (TP); CDN bytes cmp-identical.

Published to the staging subdomain (publishToWebflowSubdomain true,
customDomains []) after the user directed staging twice post-hold. All 8
pages verified: banked part1 renders verbatim (every non-style line), img
present, placeholder div gone. verify-staged.py shows h1/eyebrow diffs
against the PRE-SPLIT embed bank - stale expectations from before the
deliberate H1/eyebrow rewrite, not regressions; the embedsplit bank is the
current source of truth. Hero screenshots of all 8 sent to the user.

Georgia remains on placeholders: its porch frame was rejected (published
book cover) and the approved "A Day Full of Joy" replacement is not in the
Drive folder. The 9:37 and 9:56 frames read as GA (crepe myrtle, wicker
porch) and could serve GA EI / GA BS if the user confirms.

## Addendum 2: Georgia partial set (same day)

Per "why does it still show placeholder": the 9:37 and 9:56 frames carry the
GA cues (crepe myrtle, wicker porch, brick) and were wired as GA EI and GA BS.
Asset ids 6a78ecd60e6cceed2985ac3b (EI), 6a78ecd6bd634cf4b1f16b08 (BS); CDN
bytes cmp-identical; regeneration changed exactly the two GA part1 files;
published to the staging subdomain; both pages verified verbatim.

STILL ON PLACEHOLDERS: /parent-training-georgia and
/transition-planning-georgia. No clean frames exist - the GA porch frame was
rejected (recognizable published book cover) and its approved "A Day Full of
Joy" replacement was never added to the Drive folder; there is no fourth GA
frame at all. 10 of 12 pages now carry hero images.
