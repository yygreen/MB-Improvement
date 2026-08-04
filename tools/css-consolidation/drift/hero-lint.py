# Structural lint for the hero families. Colour drift is caught by verify.sh;
# this catches the drift a colour grep cannot see - wrong heading semantics and
# divergent hero skeletons.
#
#   python3 hero-lint.py          # lint staging
#   python3 hero-lint.py --wait   # poll until the h1 fix has landed, then lint
#
# Exit 0 = clean, 1 = at least one finding.
import re, sys, time, urllib.request

STAGING = 'https://mastermindbehavior.webflow.io'
SERVICE = ['behavior-support', 'early-intervention', 'in-home-aba-therapy',
           'parent-training', 'skill-development', 'transition-planning']
STATE   = ['aba-therapy-in-georgia', 'aba-therapy-in-new-jersey',
           'aba-therapy-in-north-carolina']

def get(slug):
    with urllib.request.urlopen(f'{STAGING}/{slug}', timeout=45) as r:
        return r.read().decode('utf-8', 'replace')

def text(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).strip()

def owned(html):
    """Only the regions this workstream owns: the .mm-embed blocks.

    Shared chrome (nav, footer) is excluded deliberately. The footer's h6 column
    headings produce an h2 -> h6 jump on every page of the site, which is a real
    but separate a11y nit - gating on it here would leave this lint permanently
    red and useless as a regression check.
    """
    out, i = [], 0
    while True:
        m = re.search(r'<div[^>]*class="[^"]*mm-embed[^"]*"[^>]*>', html[i:])
        if not m:
            return ''.join(out)
        s = i + m.end()
        depth, j = 1, s
        for t in re.finditer(r'<div\b[^>]*>|</div>', html[s:]):
            depth += 1 if t.group(0).startswith('<div') else -1
            if depth == 0:
                j = s + t.start()
                break
        else:
            j = len(html)
        out.append(html[s:j])
        i = j

def headings(html):
    return [(m.group(1), text(m.group(2))) for m in
            re.finditer(r'<(h[1-6])[^>]*>(.*?)</\1>', owned(html), re.S)]

def check(slug, html):
    """Yield findings for one page."""
    hs = headings(html)
    h1s = [t for tag, t in hs if tag == 'h1']

    # 1. exactly one h1
    if len(h1s) != 1:
        yield f'{len(h1s)} h1 elements (want exactly 1): {h1s[:3]}'
        if not h1s:
            return

    # 2. the h1 must not be the eyebrow. The eyebrow is the short label above the
    #    headline; if the h1 carries an eyebrow class, or is ALL CAPS and short,
    #    it is the label rather than the headline.
    for m in re.finditer(r'<h1[^>]*class="([^"]*)"', html):
        if 'eyebrow' in m.group(1):
            yield f'h1 carries an eyebrow class ({m.group(1)}) - the label is the h1, not the headline'

    h1 = h1s[0]
    if len(h1) < 45 and h1 == h1.upper() and any(c.isalpha() for c in h1):
        yield f'h1 looks like an eyebrow label rather than a headline: {h1!r}'

    # 3. the eyebrow must still be styled. It is only styled by a .hero-eyebrow
    #    rule; if the markup uses the class, some rule must define it.
    if re.search(r'class="[^"]*hero-eyebrow', html):
        css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
        # a rule that applies regardless of tag
        if not re.search(r'(?<![\w.])\.hero-eyebrow\s*[{,]', css):
            yield 'markup uses .hero-eyebrow but no tag-independent rule defines it'

    # 4. heading order must not skip levels
    levels = [int(tag[1]) for tag, _ in hs]
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            yield f'heading level jumps h{a} -> h{b}'
            break

def main():
    if '--wait' in sys.argv:
        for _ in range(30):
            h = get('in-home-aba-therapy')
            if not re.search(r'<h1[^>]*class="[^"]*hero-eyebrow', h):
                break
            time.sleep(6)

    findings = 0
    for family, slugs in (('service', SERVICE), ('state', STATE)):
        print(f'\n{family} family')
        for slug in slugs:
            try:
                out = list(check(slug, get(slug)))
            except Exception as e:
                out = [f'fetch failed: {e}']
            if out:
                findings += len(out)
                print(f'  FAIL  {slug}')
                for f in out:
                    print(f'          - {f}')
            else:
                print(f'  ok    {slug}')

    print(f'\n{findings} finding(s)')
    sys.exit(1 if findings else 0)

if __name__ == '__main__':
    main()
