#!/usr/bin/env python3
"""Recompute the char counts a rewrite claims for itself, and gate the copy.

The uploaded drafts stated lengths that were wrong in four of six fields, and I
then repeated the mistake by hand three more times. Counting is the computer's
job: this rewrites the claimed number to the measured one and fails on anything
that breaches a copy gate or a SERP limit.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2] / "content/blog/rewrites"
# Literal tokens, then word-bounded patterns. "our clinic" as a bare substring
# matches "our clinical team", which is fine copy: a clinical team is not a clinic.
# Same trap as the `padding: 18px 40px !important` false positive on the hero fix.
FORBIDDEN = ["—", "–"]
# "RBTs" needs the optional plural: \bRBT\b does not match it, because s is a word
# char. And clinic-based is only a breach when it describes OUR service; using it to
# contrast against in-home is exactly the distinction the pages should be drawing,
# so match the possessive/first-person forms rather than the bare phrase.
FORBIDDEN_RE = [r"\bRBTs?\b", r"\bRegistered Behavior Technicians?\b",
                r"\bour clinic\b",
                r"\b(our|we run a|we offer|we provide)\s+clinic-based\b",
                r"\bguarantee(s|d)?\b(?!\s+(the onset|children|a free|that these))"]
TITLE_MAX, DESC_MIN, DESC_MAX = 60, 120, 160

def field(text, label):
    m = re.search(rf"\*\*{label} \((\d+) chars\):\*\* (.+)", text)
    assert m, f"missing field: {label}"
    return m.group(0), int(m.group(1)), m.group(2).strip()

def main():
    fixed, fails = 0, []
    for f in sorted(ROOT.glob("*.md")):
        if f.name == "CITATION-AUDIT.md":
            continue
        t = f.read_text()
        for label in ("SEO title", "Meta description"):
            line, claimed, value = field(t, label)
            if claimed != len(value):
                t = t.replace(line, f"**{label} ({len(value)} chars):** {value}")
                fixed += 1
        f.write_text(t)

        _, _, title = field(t, "SEO title")
        _, _, desc = field(t, "Meta description")
        body = t.split("\n---\n", 1)[1]
        if len(title) > TITLE_MAX:
            fails.append(f"{f.name}: title {len(title)} > {TITLE_MAX}")
        if not DESC_MIN <= len(desc) <= DESC_MAX:
            fails.append(f"{f.name}: description {len(desc)} outside {DESC_MIN}-{DESC_MAX}")
        for w in FORBIDDEN:
            if w in body:
                fails.append(f"{f.name}: forbidden token {w!r} in body")
        for pat in FORBIDDEN_RE:
            m = re.search(pat, body)
            if m:
                fails.append(f"{f.name}: forbidden pattern {pat} matched {m.group(0)!r}")
        if body.count("# ") < 4:
            fails.append(f"{f.name}: suspiciously few headings")
        print(f"{f.name:48} title {len(title):3}  desc {len(desc):3}  words {len(body.split()):5}")

    print(f"\nrewrote {fixed} stale count(s)")
    if fails:
        print("\nFAILED:")
        for x in fails:
            print("  ", x)
        sys.exit(1)
    print("all gates pass")

if __name__ == "__main__":
    main()
