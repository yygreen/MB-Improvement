#!/usr/bin/env python3
"""Extract FAQ question/answer pairs from tier1 embedsplit part2 files.

Parses the mm-faq accordion markup (<summary class="mm-acc__q"> questions,
<div class="mm-acc__a"> answers), strips HTML tags from answers (text kept
verbatim otherwise), and emits a FAQPage JSON-LD object per slug.

Gates enforced per page:
  - at least 3 QA pairs
  - every answer non-empty after tag stripping
  - no "RBT" token in any question or answer

Usage:
  python3 gen-faq-schema.py                 # print {slug: FAQPage} JSON to stdout
  python3 gen-faq-schema.py --out DIR       # also write DIR/<slug>.faq.json
"""
import html
import json
import re
import sys
from pathlib import Path

EMBEDSPLIT_DIR = Path(__file__).resolve().parents[2] / "content" / "tier1" / "build" / "embedsplit"

SLUGS = [
    "early-intervention-new-jersey",
    "parent-training-new-jersey",
    "behavior-support-new-jersey",
    "transition-planning-new-jersey",
    "early-intervention-georgia",
    "parent-training-georgia",
    "behavior-support-georgia",
    "transition-planning-georgia",
    "early-intervention-north-carolina",
    "parent-training-north-carolina",
    "behavior-support-north-carolina",
    "transition-planning-north-carolina",
]

ITEM_RE = re.compile(
    r'<summary class="mm-acc__q">(.*?)</summary>\s*'
    r'<div class="mm-acc__a">(.*?)</div>\s*</details>',
    re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(fragment: str) -> str:
    """Remove HTML tags; join paragraph breaks with a single space. Text verbatim otherwise."""
    # Turn paragraph/element boundaries into spaces so words don't fuse.
    text = TAG_RE.sub(" ", fragment)
    text = html.unescape(text)
    # Collapse whitespace introduced by markup, keep wording untouched.
    return re.sub(r"\s+", " ", text).strip()


def extract_pairs(path: Path):
    src = path.read_text(encoding="utf-8")
    # Constrain to the mm-faq section to avoid picking up unrelated markup.
    m = re.search(r'<section class="mm-section mm-faq">(.*?)</section>', src, re.DOTALL)
    if not m:
        raise ValueError(f"{path.name}: no mm-faq section found")
    faq_html = m.group(1)
    pairs = []
    for q_raw, a_raw in ITEM_RE.findall(faq_html):
        q = strip_tags(q_raw)
        a = strip_tags(a_raw)
        pairs.append((q, a))
    return pairs


def gate(slug: str, pairs) -> list:
    errors = []
    if len(pairs) < 3:
        errors.append(f"{slug}: only {len(pairs)} QA pairs (need >= 3)")
    for i, (q, a) in enumerate(pairs, 1):
        if not q:
            errors.append(f"{slug} Q{i}: empty question")
        if not a:
            errors.append(f"{slug} Q{i}: empty answer after tag stripping")
        if re.search(r"\bRBT\b", q) or re.search(r"\bRBT\b", a):
            errors.append(f"{slug} Q{i}: contains forbidden token 'RBT'")
    return errors


def faq_jsonld(pairs) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }


def main():
    out_dir = None
    if "--out" in sys.argv:
        out_dir = Path(sys.argv[sys.argv.index("--out") + 1])
        out_dir.mkdir(parents=True, exist_ok=True)

    all_errors = []
    result = {}
    counts = {}
    for slug in SLUGS:
        path = EMBEDSPLIT_DIR / f"{slug}.part2.html"
        pairs = extract_pairs(path)
        all_errors.extend(gate(slug, pairs))
        result[slug] = faq_jsonld(pairs)
        counts[slug] = len(pairs)

    if all_errors:
        for e in all_errors:
            print(f"GATE FAIL: {e}", file=sys.stderr)
        sys.exit(1)

    if out_dir:
        for slug, obj in result.items():
            (out_dir / f"{slug}.faq.json").write_text(
                json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    print(json.dumps({"counts": counts, "faq": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
