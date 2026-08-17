#!/usr/bin/env python3
"""Re-sync the repo's mirror of the shared service sheet from the live site.

tools/css-consolidation/service-pages.shared.css is a MIRROR of the "Service
Page Styles" component in Webflow. Webflow is the source of truth: edits are made
there and the file exists so the consolidation tooling (collision-check,
rebase-shared) has something to parse. It goes stale whenever a change is made in
the Designer and not written back - which is what happened with the 2026-08-04
hero convergence, leaving the mirror asserting 48px/1.15/800 while live rendered
clamp(32px, 5vw, 52px)/1.08/600 for four months of tooling runs.

Fetching beats retyping: this cannot introduce a transcription error, and the
diff it produces is the honest list of what drifted.

    python3 tools/tier1/sync-shared-from-live.py            # show the diff
    python3 tools/tier1/sync-shared-from-live.py --apply     # write it

Run it after any Designer edit to the shared component.
"""
import difflib
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIRROR = ROOT / "tools/css-consolidation/service-pages.shared.css"
# any page that loads the shared component; /services deliberately does NOT
PAGE = "https://www.mastermindbehavior.com/parent-training"
MARK = ".mm-embed .hero-headline"


def main():
    req = urllib.request.Request(PAGE, headers={"User-Agent": "mb-sync/1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")

    blocks = []
    for m in re.finditer(r"<style[^>]*>", html):
        body = html[m.end():html.index("</style>", m.end())]
        if MARK in body:
            blocks.append(body)
    if len(blocks) != 1:
        sys.exit(f"expected exactly 1 style block carrying {MARK}, found {len(blocks)}")
    live = blocks[0]

    # sanity: the shared sheet is large and scoped; a wrong block would not be
    assert len(live) > 15000, f"style block suspiciously small ({len(live)} bytes)"
    assert live.count(".mm-embed") > 100, "block is not the scoped service sheet"

    old = MIRROR.read_text()
    if old == live:
        print("mirror is already in sync")
        return

    diff = list(difflib.unified_diff(old.splitlines(), live.splitlines(),
                                     "repo mirror", f"live ({PAGE})", lineterm="", n=0))
    changed = sum(1 for l in diff if l[:1] in "+-" and l[:3] not in ("+++", "---"))
    print("\n".join(diff))
    print(f"\n{changed} changed line(s)")

    if "--apply" in sys.argv:
        MIRROR.write_text(live)
        print(f"written to {MIRROR.relative_to(ROOT)}")
    else:
        print("re-run with --apply to write")


if __name__ == "__main__":
    main()
