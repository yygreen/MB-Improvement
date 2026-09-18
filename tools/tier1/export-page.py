#!/usr/bin/env python3
"""Export a staging page as a single self-contained HTML file.

    python3 tools/tier1/export-page.py <slug> [outdir]

Fetches https://mastermindbehavior.webflow.io/<slug>, inlines the Webflow
stylesheet (rewriting url() references to absolute), strips remote and
inline scripts plus noscript pixels (JSON-LD is kept so structured data
stays reviewable), absolutises remaining asset and link URLs, and stamps a
provenance banner at the top of the body.

The result opens offline in any browser and looks like the staging page.
Useful for sending a page to a reviewer who should not be clicking around
the live staging site, and for archiving what a page looked like on a date.

Note: the export is a snapshot, NOT a source of truth. The banked embeds
under content/tier1/build/ remain the byte-exact record.
"""
import pathlib
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://mastermindbehavior.webflow.io"
STAMP = "2026-08-05"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 mb-export"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def export(slug):
    html = fetch(f"{BASE}/{slug}")
    original = len(html)

    # inline stylesheets; Webflow writes href before rel, so match the whole tag
    inlined = 0
    for tag in re.findall(r"<link\b[^>]*>", html):
        if 'rel="stylesheet"' not in tag:
            continue
        m = re.search(r'href="([^"]+)"', tag)
        if not m:
            continue
        url = urllib.parse.urljoin(BASE, m.group(1))
        css = fetch(url)
        css = re.sub(r'url\((["\']?)/(?!/)', lambda x: f"url({x.group(1)}{BASE}/", css)
        html = html.replace(tag, f"<style>\n/* inlined from {url} */\n{css}\n</style>", 1)
        inlined += 1
    assert inlined, f"{slug}: no stylesheet found to inline"

    # strip scripts (keep JSON-LD) and tracking noscript pixels
    html = re.sub(r'<script[^>]*\ssrc="[^"]*"[^>]*>\s*</script>', "", html)
    html = re.sub(
        r"<script(?![^>]*application/ld\+json)[^>]*>.*?</script>", "", html, flags=re.S
    )
    html = re.sub(r"<noscript>.*?</noscript>", "", html, flags=re.S)

    # absolutise remaining relative URLs
    html = re.sub(r'(\s(?:src|href|content))="/(?!/)',
                  lambda m: f'{m.group(1)}="{BASE}/', html)
    html = re.sub(
        r'srcset="([^"]*)"',
        lambda m: 'srcset="' + re.sub(r"(^|,\s*)/(?!/)", r"\1" + BASE + "/", m.group(1)) + '"',
        html,
    )

    banner = (
        '<div style="position:sticky;top:0;z-index:99999;background:#1a2744;color:#fff;'
        'font:600 13px/1.5 Manrope,system-ui,sans-serif;padding:9px 16px;text-align:center">'
        f"Static export of {BASE}/{slug} &mdash; STAGING ONLY, captured {STAMP}. "
        "Stylesheet inlined; tracking and chat scripts removed. Links go to staging.</div>"
    )
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + banner, html, count=1)

    for probe, label in (("<h1", "h1"), ("navbar_wrapper", "nav"), ("footer_link", "footer")):
        assert probe in html, f"{slug}: export is missing {label}"
    return html, original


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    outdir = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    outdir.mkdir(parents=True, exist_ok=True)
    html, original = export(slug)
    out = outdir / f"{slug}.export.html"
    out.write_text(html)
    print(f"{out}: {original:,} bytes fetched -> {len(html):,} bytes self-contained")
