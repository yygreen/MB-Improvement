#!/usr/bin/env python3
"""Sweep the live sitemap for pages belonging to a topic cluster.

Written after a 302-click financing page stayed invisible through three
rounds of auditing because the ad-hoc regex used at the time matched on
'insurance|cost|financ|medicaid|...' and never included 'benefits'.

Two lessons are baked in:

1. A slug filter alone is not a cluster map. Slugs are written by whoever
   wrote the post, not by the taxonomy. This fetches candidate pages and
   classifies on the rendered text as well.
2. The filter has to be a named, reviewable list rather than something
   retyped per-audit. It lives here so the next sweep starts from the last
   one instead of from memory.

Run: python3 tools/seo/sweep-cluster.py [cluster] [--full]
     --full also fetches every sitemap URL to catch slugs the terms miss.
"""
import urllib.request, re, ssl, html, sys, json, pathlib, time

CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
BASE = 'https://www.mastermindbehavior.com'

# Slug terms: cheap first pass. Deliberately over-inclusive; false positives
# are dropped by the body check below, false negatives are invisible forever.
CLUSTERS = {
    'financing': {
        'slug_terms': [
            'insurance', 'cost', 'financ', 'medicaid', 'medicare', 'coverage',
            'covered', 'pay', 'paying', 'afford', 'grant', 'fund', 'expens',
            'price', 'pricing', 'waiver', 'ssi', 'ssdi', 'aid', 'benefit',
            'disability', 'money', 'budget', 'reimburse', 'claim', 'deductible',
            'copay', 'out-of-pocket', 'scholarship', 'tax', 'able-account',
            'subsidy', 'assistance', 'how-much', 'rate', 'fee', 'bill',
        ],
        # A page is in the cluster if its body carries enough of these.
        'body_terms': [
            'insurance', 'medicaid', 'ssi', 'copay', 'deductible', 'premium',
            'coverage', 'reimburse', 'out-of-pocket', 'grant', 'waiver',
            'benefit', 'cost', 'afford', 'fee schedule', 'prior authorization',
        ],
        'body_hits_required': 4,
    },
}


def get(u, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            if a == tries - 1:
                return ''
            time.sleep(2 ** a)
    return ''


def page_text(h):
    b = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    # drop the related-articles rail so a sidebar mention cannot pull a page in
    for marker in ('Recent articles', 'Does anything here apply'):
        i = b.find(marker)
        if i > 0:
            b = b[:i]
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', b)))


def main():
    cluster = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 'financing'
    full = '--full' in sys.argv
    cfg = CLUSTERS[cluster]

    sm = get(BASE + '/sitemap.xml')
    urls = [u for u in re.findall(r'(?<=<loc>)[^<]+', sm)]
    print(f'sitemap: {len(urls)} URLs')

    if full:
        candidates = urls
        print('mode: FULL (fetching every URL)')
    else:
        pat = re.compile('|'.join(re.escape(t) for t in cfg['slug_terms']), re.I)
        candidates = [u for u in urls if pat.search(u)]
        print(f'mode: slug filter, {len(candidates)} candidates from '
              f'{len(cfg["slug_terms"])} terms')

    inside, rejected = [], []
    for i, u in enumerate(candidates, 1):
        h = get(u)
        if not h:
            continue
        t = page_text(h)
        hits = [w for w in cfg['body_terms'] if w in t.lower()]
        title = (re.search(r'<title>(.*?)</title>', h) or [None, ''])[1]
        rec = {'url': u.replace(BASE, ''), 'title': title,
               'words': len(t.split()), 'hits': len(hits)}
        (inside if len(hits) >= cfg['body_hits_required'] else rejected).append(rec)
        if i % 25 == 0:
            print(f'  ...{i}/{len(candidates)}')

    inside.sort(key=lambda r: -r['hits'])
    out = pathlib.Path(f'content/ops/cluster-{cluster}.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'cluster': cluster, 'in': inside,
                               'rejected': rejected}, indent=2) + '\n')

    print(f'\nIN CLUSTER: {len(inside)}')
    for r in inside:
        print(f'  {r["hits"]:2d} hits  {r["words"]:5d}w  {r["url"]}')
    print(f'\nrejected (matched slug, failed body check): {len(rejected)}')
    for r in rejected[:12]:
        print(f'   {r["hits"]} hits  {r["url"]}')
    print(f'\nwritten to {out}')


if __name__ == '__main__':
    main()
