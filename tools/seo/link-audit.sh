#!/usr/bin/env bash
# Link audit for the Mastermind service pages and, later, the city-page services block.
#
#   bash tools/seo/link-audit.sh            # audit production
#   bash tools/seo/link-audit.sh staging    # audit the webflow.io subdomain
#
# Check 1: no body links to the old /areas-we-serve/aba-therapy-in-{state}
#          redirect paths on the six service pages.
# Check 2: every URL the city-page services block will emit returns 200.
#          Tier 1 targets 404 until those pages ship; the check reports them
#          as PENDING rather than failing, and flips to a hard gate once live.
set -u
HOST="https://www.mastermindbehavior.com"
[ "${1:-}" = "staging" ] && HOST="https://mastermindbehavior.webflow.io"
fail=0
echo "== 1. old redirect-path links on the six service pages =="
for s in behavior-support early-intervention in-home-aba-therapy parent-training skill-development transition-planning; do
  n=$(curl -s --max-time 30 "$HOST/$s" | grep -oc 'areas-we-serve/aba-therapy-in-')
  if [ "$n" = "0" ]; then echo "  ok    $s"; else echo "  FAIL  $s ($n old-path links)"; fail=1; fi
done
echo "== 2. services-block targets (/{service}-{state-key}) =="
pending=0
for svc in early-intervention transition-planning parent-training behavior-support; do
  for st in new-jersey georgia north-carolina; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$HOST/$svc-$st")
    case "$code" in
      200) echo "  ok       /$svc-$st";;
      404) echo "  PENDING  /$svc-$st (Tier 1 page not yet built)"; pending=$((pending+1));;
      *)   echo "  FAIL     /$svc-$st ($code)"; fail=1;;
    esac
  done
done
echo
echo "state-hub sanity:"
for st in new-jersey georgia north-carolina; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$HOST/aba-therapy-in-$st")
  [ "$code" = "200" ] && echo "  ok    /aba-therapy-in-$st" || { echo "  FAIL  /aba-therapy-in-$st ($code)"; fail=1; }
done
echo "== 3. per-state town sampling (NC's 20 must not hide behind NJ's 517) =="
# Sample towns from EACH state's hub city grid: first, middle, last. Every
# sampled town must 200. Once the town services block ships, each sampled
# town page must carry the block with that state's href suffix; until then
# the block is reported PENDING, not failed.
blockpending=0
for st in new-jersey georgia north-carolina; do
  towns=$(curl -s --max-time 30 "$HOST/aba-therapy-in-$st" \
    | grep -o 'href="/areas-we-serve/[a-z0-9-]*"' | sed 's/href="//;s/"//' | sort -u)
  count=$(echo "$towns" | grep -c .)
  if [ "$count" = "0" ]; then echo "  FAIL  $st: no towns found on hub"; fail=1; continue; fi
  sample=$(echo "$towns" | awk -v n="$count" 'NR==1 || NR==int((n+1)/2) || NR==n')
  for t in $sample; do
    page=$(curl -s -w '\n%{http_code}' --max-time 30 "$HOST$t")
    code=$(echo "$page" | tail -1)
    if [ "$code" != "200" ]; then echo "  FAIL     $t ($code)"; fail=1; continue; fi
    if echo "$page" | grep -q 'class="mm-svc"'; then
      bad=$(echo "$page" | grep -o "href=\"/\(early-intervention\|parent-training\|behavior-support\|transition-planning\)-[a-z-]*\"" | grep -vc -- "-$st\"")
      if [ "$bad" = "0" ]; then echo "  ok       $t (block, $st links)"; else echo "  FAIL     $t (block carries $bad wrong-state links)"; fail=1; fi
    else
      echo "  ok       $t (200; block PENDING)"; blockpending=$((blockpending+1))
    fi
  done
done
echo
[ "$fail" = "0" ] && echo "RESULT: pass ($pending Tier 1 targets pending, town block pending on $blockpending sampled towns)" || echo "RESULT: FAIL"
exit $fail
