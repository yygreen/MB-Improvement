#!/usr/bin/env python3
"""Rendered hero-type lint: catches drift the source-based hero-lint cannot see.

tools/css-consolidation/drift/hero-lint.py greps the HTML, so it catches wrong
heading semantics and duplicated skeletons. It CANNOT see computed type, which
is where the remaining drift lives: a page can have perfect markup and still
render its h1 at the wrong size, weight or colour because a page-specific
override wins over the shared sheet.

This lint renders each page in Chromium and compares the hero's computed type
against the reference page, /aba-therapy-in-new-jersey.

    python3 tools/tier1/hero-type-lint.py                 # lint staging
    python3 tools/tier1/hero-type-lint.py --prod          # lint production
    python3 tools/tier1/hero-type-lint.py --family service

Reference spec measured 2026-08-05 at 1440px:
    h1       52px / 56px line-height / weight 600 / #1a2744, x=120, column 582
    eyebrow  13px / letter-spacing 1.04px / uppercase, 27px above the h1

Requires playwright and the sandbox Chromium; see BUILD-RECORD notes for why the
browser must be launched with --no-proxy-server here.
"""
import json
import os
import subprocess
import sys
import pathlib

REFERENCE = "aba-therapy-in-new-jersey"

# pages that should share the reference hero exactly
FAMILY = {
    "state": ["aba-therapy-in-new-jersey", "aba-therapy-in-georgia",
              "aba-therapy-in-north-carolina"],
    "service": ["in-home-aba-therapy", "early-intervention", "parent-training",
                "behavior-support", "skill-development", "transition-planning"],
    "resource": ["insurance-terminology", "financial-aid-resources"],
}
# known to be on a different hero system; reported as INFO, not failure,
# until a decision is taken to converge them (see BUILD-RECORD-HERO-DRIFT.md)
OTHER_SYSTEM = ["bcba-team", "services", "about-us", "areas-we-serve", "contact"]

TOLERANCE = {"fontSize": 1, "lineHeight": 2, "left": 2, "gapToH1": 3}

PROBE = r"""
import { chromium } from 'playwright';
const BASE = process.argv[2], SLUGS = JSON.parse(process.argv[3]);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-proxy-server'] });
const out = {};
for (const slug of SLUGS) {
  const p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  try {
    await p.goto(`${BASE}/${slug}`, { waitUntil: 'load', timeout: 90000 });
    await p.waitForTimeout(1800);
    out[slug] = await p.evaluate(() => {
      const px = v => Math.round(parseFloat(v) || 0);
      const h1 = document.querySelector('h1');
      if (!h1) return { error: 'no h1' };
      const c = getComputedStyle(h1), r = h1.getBoundingClientRect();
      let eyebrow = null;
      const cands = [...document.querySelectorAll('div,span,p')].filter(e => {
        const b = e.getBoundingClientRect();
        return e.children.length === 0 && (e.textContent||'').trim().length > 2
          && b.height > 0 && b.top + scrollY < r.top + scrollY
          && b.top + scrollY > r.top + scrollY - 140;
      });
      const e = cands[cands.length - 1];
      if (e) { const ec = getComputedStyle(e), er = e.getBoundingClientRect();
        eyebrow = { text: e.textContent.trim().slice(0,40), fontSize: px(ec.fontSize),
          letterSpacing: ec.letterSpacing, textTransform: ec.textTransform,
          left: Math.round(er.left), gapToH1: Math.round(r.top - er.bottom) }; }
      return { h1: { text: h1.textContent.trim().slice(0,44), cls: h1.className.toString(),
        fontSize: px(c.fontSize), lineHeight: px(c.lineHeight), fontWeight: c.fontWeight,
        color: c.color, left: Math.round(r.left), width: Math.round(r.width) }, eyebrow };
    });
  } catch (err) { out[slug] = { error: err.message.split('\n')[0] }; }
  await p.close();
}
await b.close();
console.log(JSON.stringify(out));
"""


def probe(base, slugs):
    # the script must sit where `playwright` resolves. PLAYWRIGHT_DIR lets the
    # caller point at an install outside the repo (this sandbox keeps one in the
    # scratchpad); otherwise it runs from the repo root.
    where = pathlib.Path(os.environ.get("PLAYWRIGHT_DIR", pathlib.Path.cwd()))
    path = where / ".hero-type-probe.mjs"
    path.write_text(PROBE)
    r = subprocess.run(["node", str(path), base, json.dumps(slugs)],
                       capture_output=True, text=True, timeout=900, cwd=where)
    path.unlink(missing_ok=True)
    if r.returncode != 0:
        sys.exit(f"probe failed:\n{r.stderr[-1500:]}")
    return json.loads(r.stdout)


def compare(ref, got, slug):
    """Yield findings for one page against the reference."""
    if "error" in got:
        yield f"could not measure: {got['error']}"
        return
    rh, gh = ref["h1"], got["h1"]
    for key in ("fontSize", "lineHeight", "left"):
        if abs(rh[key] - gh[key]) > TOLERANCE[key]:
            yield f"h1 {key}: {gh[key]} (reference {rh[key]})"
    if rh["fontWeight"] != gh["fontWeight"]:
        yield f"h1 font-weight: {gh['fontWeight']} (reference {rh['fontWeight']})"
    if rh["color"] != gh["color"]:
        yield f"h1 colour: {gh['color']} (reference {rh['color']})"
    re_, ge = ref.get("eyebrow"), got.get("eyebrow")
    if re_ and not ge:
        yield "no eyebrow found above the h1"
    elif re_ and ge:
        if abs(re_["fontSize"] - ge["fontSize"]) > TOLERANCE["fontSize"]:
            yield f"eyebrow font-size: {ge['fontSize']} (reference {re_['fontSize']})"
        if re_["textTransform"] != ge["textTransform"]:
            yield f"eyebrow text-transform: {ge['textTransform']} (reference {re_['textTransform']})"
        if abs(re_["left"] - ge["left"]) > TOLERANCE["left"]:
            yield f"eyebrow left edge: {ge['left']} (reference {re_['left']}) - eyebrow not aligned with the h1"
        if abs(re_["gapToH1"] - ge["gapToH1"]) > TOLERANCE["gapToH1"]:
            yield f"eyebrow gap to h1: {ge['gapToH1']}px (reference {re_['gapToH1']}px)"


def main():
    base = ("https://www.mastermindbehavior.com" if "--prod" in sys.argv
            else "https://mastermindbehavior.webflow.io")
    only = None
    if "--family" in sys.argv:
        only = sys.argv[sys.argv.index("--family") + 1]

    families = {k: v for k, v in FAMILY.items() if only is None or k == only}
    slugs = sorted({s for v in families.values() for s in v} | {REFERENCE})
    data = probe(base, slugs + (OTHER_SYSTEM if only is None else []))

    ref = data.get(REFERENCE)
    if not ref or "error" in ref:
        sys.exit(f"reference page {REFERENCE} could not be measured")

    r = ref["h1"]
    print(f"reference {REFERENCE} @ {base}")
    print(f"  h1 {r['fontSize']}px/{r['lineHeight']} weight {r['fontWeight']} "
          f"{r['color']} left={r['left']}")
    if ref.get("eyebrow"):
        e = ref["eyebrow"]
        print(f"  eyebrow {e['fontSize']}px {e['textTransform']} left={e['left']} gap={e['gapToH1']}")

    findings = 0
    for fam, fam_slugs in families.items():
        print(f"\n{fam} family")
        for slug in fam_slugs:
            out = list(compare(ref, data.get(slug, {"error": "not fetched"}), slug))
            if out:
                findings += len(out)
                print(f"  FAIL  {slug}")
                for f in out:
                    print(f"          - {f}")
            else:
                print(f"  ok    {slug}")

    if only is None:
        print("\nother hero systems (informational, not gated)")
        for slug in OTHER_SYSTEM:
            out = list(compare(ref, data.get(slug, {"error": "not fetched"}), slug))
            print(f"  {slug}: {len(out)} difference(s) from the reference hero")

    print(f"\n{findings} finding(s) in gated families")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
