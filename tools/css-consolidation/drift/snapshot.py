# Bank EVERY embed on the hero-family pages, not just the ones that carried colour
# drift. Rollback previously covered one embed per page; a structural change needs
# the whole page restorable.
#
#   python3 snapshot.py            # fetch staging and write snapshots/
#   python3 snapshot.py --verify   # re-fetch and confirm snapshots still match live
#
# Same reconstruction as embeds.py: Webflow renders an HtmlEmbed verbatim inside
# <div class="w-embed">, so the wrapper's inner HTML is the embed's code.
import re, os, sys, json, hashlib, urllib.request

STAGING = 'https://mastermindbehavior.webflow.io'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshots')
PAGES = [
    # service family (share the Service Page Styles component)
    'behavior-support', 'early-intervention', 'in-home-aba-therapy',
    'parent-training', 'skill-development', 'transition-planning',
    # state family
    'aba-therapy-in-georgia', 'aba-therapy-in-new-jersey',
    'aba-therapy-in-north-carolina',
]

def fetch(slug):
    with urllib.request.urlopen(f'{STAGING}/{slug}', timeout=45) as r:
        return r.read().decode('utf-8', 'replace')

def embeds(html):
    """Every <div class="...w-embed..."> wrapper's inner HTML, in document order."""
    out = []
    for m in re.finditer(r'<div class="[^"]*w-embed[^"]*"[^>]*>', html):
        depth, end = 1, None
        for t in re.finditer(r'<div\b[^>]*>|</div>', html[m.end():]):
            depth += 1 if t.group(0).startswith('<div') else -1
            if depth == 0:
                end = m.end() + t.start()
                break
        if end is not None:
            out.append(html[m.end():end])
    return out

def main():
    verify = '--verify' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    manifest, mismatches, total = {}, [], 0
    for slug in PAGES:
        try:
            code = embeds(fetch(slug))
        except Exception as e:
            print(f'  !! {slug}: fetch failed ({e})')
            mismatches.append(slug)
            continue
        total += len(code)
        entries = []
        for i, c in enumerate(code):
            name = f'{slug}.embed{i}.html'
            path = os.path.join(OUT, name)
            digest = hashlib.sha256(c.encode()).hexdigest()[:16]
            entries.append({'file': name, 'bytes': len(c.encode()), 'sha256_16': digest})
            if verify:
                if not os.path.exists(path):
                    print(f'  MISSING  {name}'); mismatches.append(name); continue
                prev = open(path, encoding='utf-8').read()
                if prev != c:
                    print(f'  CHANGED  {name}'); mismatches.append(name)
            else:
                open(path, 'w', encoding='utf-8').write(c)
        manifest[slug] = entries
        print(f'  {slug:32} {len(code)} embed(s)')

    mpath = os.path.join(OUT, 'manifest.json')
    if verify:
        print(f'\n{total} embed(s) checked across {len(PAGES)} pages')
        print('MATCH - snapshots still reflect live' if not mismatches
              else f'{len(mismatches)} differ from the snapshot: {mismatches}')
        sys.exit(1 if mismatches else 0)
    json.dump(manifest, open(mpath, 'w'), indent=1)
    print(f'\n{total} embed(s) banked to snapshots/ across {len(PAGES)} pages')

if __name__ == '__main__':
    main()
