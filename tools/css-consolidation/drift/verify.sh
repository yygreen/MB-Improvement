#!/usr/bin/env bash
# Verify the colour-drift convergence end to end, from scratch, against staging.
#
#   bash verify.sh            # all checks
#   bash verify.sh quick      # checks 1 and 4 only (~15s, no full-site sweep)
#
# Run it from anywhere; it locates its own directory. Needs curl and python3.
# Read-only: it fetches pages and compares. It never writes to Webflow.
set -uo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGING="https://mastermindbehavior.webflow.io"
PROD="https://www.mastermindbehavior.com"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
MODE="${1:-full}"
fail=0
say() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()  { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
bad() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; fail=1; }

# The five values the sweep removed, and the values deliberately kept.
DRIFT='#c64d42|#c45045|#f8f6f1|#fdebe2|#eef0f4'

# The 16 hand-built pages the workstream owns. CMS/blog pages inherit the shared
# component but are not authored here, so they are covered by check 2, not the audit.
PAGES=(aba-therapy-in-georgia aba-therapy-in-new-jersey aba-therapy-in-north-carolina
       autism-screening-checklist behavior-support building-skills-independence
       early-intervention financial-aid-resources first-90-days-of-aba-therapy
       in-home-aba-therapy insurance-terminology parent-training services
       skill-development transition-planning understanding-aba-therapy)

# ── 1. The "done" criterion: no drift value on any of the 16 ──────────────────
say "1. Drift values across the 16 in-scope pages"
for s in "${PAGES[@]}"; do
  curl -sS --max-time 30 "$STAGING/$s" -o "$WORK/$s.html" || { bad "$s (fetch failed)"; continue; }
done
hits=$(grep -ohE "$DRIFT" "$WORK"/*.html 2>/dev/null | wc -l | tr -d ' ')
[ "$hits" = "0" ] && ok "0 occurrences of $DRIFT" || bad "$hits occurrence(s) found"

# ── 2. Same, across every page in the staging sitemap ─────────────────────────
if [ "$MODE" != "quick" ]; then
  say "2. Drift values across the whole staging sitemap"
  curl -sS --max-time 60 "$STAGING/sitemap.xml" \
    | grep -oE '<loc>[^<]+' | sed 's#<loc>##' \
    | sed "s#$PROD#$STAGING#" > "$WORK/urls.txt"
  n=$(wc -l < "$WORK/urls.txt" | tr -d ' ')
  scan() { c=$(curl -s --max-time 25 "$1" | grep -ocE "$2"); [ "$c" != "0" ] && echo "$1 ($c)"; }
  export -f scan
  xargs -P 24 -I{} bash -c 'scan "$@"' _ {} "$DRIFT" < "$WORK/urls.txt" > "$WORK/dirty.txt" 2>/dev/null
  if [ -s "$WORK/dirty.txt" ]; then
    bad "$(wc -l < "$WORK/dirty.txt" | tr -d ' ') of $n page(s) still carry a drift value:"
    sed 's/^/          /' "$WORK/dirty.txt"
  else
    ok "0 occurrences across all $n pages"
  fi
fi

# ── 3. Each applied embed is byte-identical to its authoritative .fixed.html ──
say "3. Byte-identity of each applied embed vs its .fixed.html"
python3 - "$D" "$WORK" <<'PY'
import re, sys, os, glob
D, W = sys.argv[1], sys.argv[2]
norm = lambda s: re.sub(r'\s+', '', s)
# embedN -> the page(s) it must appear on. The component feeds six pages.
MAP = {
 'embed0':  ['behavior-support','early-intervention','in-home-aba-therapy',
             'parent-training','skill-development','transition-planning'],
 'embed1':  ['aba-therapy-in-georgia'],        'embed3':  ['aba-therapy-in-georgia'],
 'embed4':  ['aba-therapy-in-new-jersey'],     'embed6':  ['aba-therapy-in-north-carolina'],
 'embed9':  ['financial-aid-resources'],       'embed10': ['financial-aid-resources'],
 'embed11': ['financial-aid-resources'],       'embed12': ['financial-aid-resources'],
 'embed13': ['insurance-terminology'],         'embed15': ['insurance-terminology'],
 'embed16': ['services'],
}
cache = {}
def page(s):
    if s not in cache:
        cache[s] = norm(open(os.path.join(W, s + '.html'), encoding='utf-8').read())
    return cache[s]
bad = 0
for name in sorted(MAP, key=lambda x: int(x[5:])):
    f = os.path.join(D, name + '.fixed.html')
    if not os.path.exists(f):
        print(f"  \033[31mFAIL\033[0m  {name}: {name}.fixed.html missing"); bad = 1; continue
    t = norm(open(f, encoding='utf-8').read())
    missing = [s for s in MAP[name] if t not in page(s)]
    if missing:
        print(f"  \033[31mFAIL\033[0m  {name} not byte-identical on: {', '.join(missing)}"); bad = 1
    else:
        n = len(MAP[name])
        print(f"  \033[32mPASS\033[0m  {name} matches on {n} page{'s' if n > 1 else ''}")
sys.exit(bad)
PY
[ $? -eq 0 ] || fail=1

# ── 4. The deliberate retentions are still present (guards against over-sweep) ─
say "4. Deliberately retained values still live"
check_kept() {
  c=$(grep -ohF "$1" "$WORK"/*.html 2>/dev/null | wc -l | tr -d ' ')
  [ "$c" -ge "$2" ] && ok "$1 present ($c, expected >=$2) - $3" \
                    || bad "$1 present $c, expected >=$2 - $3 - did a sweep go too far?"
}
check_kept '#ff8c5a' 6 'held for a decision, six service pages'
check_kept '#e6e2da' 12 'the warm hairline --rule'
check_kept '#002833' 7 'Designer brand-variable fallback'
check_kept '#f7f6f5' 1 'resource-hub token'
check_kept '#b34a40' 20 'the single button-hover red'

# ── 5. Negative control: production must still be unpublished ─────────────────
if [ "$MODE" != "quick" ]; then
  say "5. Negative control - custom domains NOT published"
  pc=$(curl -sS --max-time 30 "$PROD/financial-aid-resources" | grep -ocE '#c64d42|#c45045')
  [ "$pc" != "0" ] \
    && ok "production still carries the old values ($pc) - staging-only constraint held" \
    || bad "production is clean - it may have been published; confirm that was intended"
fi

say "Result"
[ "$fail" = "0" ] && { printf '  \033[32mAll checks passed.\033[0m\n\n'; exit 0; } \
                  || { printf '  \033[31mSomething failed above.\033[0m\n\n'; exit 1; }
