# Build record: link-pass completion + NJ sibling links (2026-08-17, published)

One token session. The figure swap it was requested for turned out to be
blocked, so the session did the queued CMS work instead.

## Blocked: the three figure swaps

The token carries CMS read/write but no `assets:read` / `assets:write`, and
the rebuilt who-pays-when figures (GA, NJ, NC) need an asset upload before
the guide bodies can point at them. The Webflow error was explicit:

    OAuthForbidden: You are missing the following scopes - 'assets:read'

Next token needs `cms:read`, `cms:write`, `assets:read`, `assets:write`.
The rebuilt images sit in `content/blog/guides/figures/`, all three
verified, waiting on nothing else.

## Shipped 1: NJ guide sibling links (+604 chars)

`/post/aba-therapy-funding-new-jersey`, item `6a7b1bd6d504baca3ff709d1`.
The NJ guide was the only one of the three that linked neither sibling.
One paragraph inserted before "Why Mastermind Behavior", mirroring the
Georgia guide's inline-comparison pattern. Every claim in it is asserted
against the sibling datasets at write time: GA's 20-or-under age and
statutory visit-limit ban, NC's 18-or-younger permission and the Medicaid
continuation past 21. A gate also rejects any dollar figure in the
paragraph, so no cap can ride along without its catch.

All three guides now link both siblings.

## Shipped 2: the five queued link-pass bodies

Generated and gated on 11 August, applied today after re-verifying against
the live CMS: emotional neglect, camel milk, vitamin D, GFCF, Defeat Autism
Now. All five written byte-identical and published. Every rewrite now
carries its service links (5 to 6 each, all three state hubs).

**The drift gate fired, and was right to.** Three of the five live bodies
no longer matched what the queued files were generated from. The cause is
known and mechanical: Webflow normalizes rich-text image URLs into CMS
space after a save (`.../cfe12d/<asset>` becomes
`.../cfe155/<newid>_<asset>`), so bodies containing figures drifted at
exactly their `img src` attributes and nowhere else. The comparison was
re-run modulo `cdn.prod.website-files.com` URLs; anything else differing
would still stop the write. Four, two and one URL rewrites respectively;
the two figure-less bodies matched byte-for-byte.

What was written is the transform of the live body, never the stale queued
file, so the normalized URLs stayed exactly as Webflow wants them.

**Live verification note.** The page-level em-dash sweep flagged all five
pages. The written bodies contain none (checked directly); the dashes are
pre-existing site chrome outside the post body. Recorded so the next sweep
does not rediscover it.

## Token hygiene

Token stored at `/tmp/wf4/t` (chmod 600, outside the repo), used for the
session, shredded after. Verified absent from every repo file and from all
of git history before shredding. The token should still be rotated.
