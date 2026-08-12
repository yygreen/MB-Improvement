#!/usr/bin/env python3
"""Generate a Webflow rich-text body from a funding guide markdown file, and gate it.

Never hand-retype the payload: it is generated here, asserted against the
funding dataset, and the same file is what gets pushed to the CMS.
"""
import json, re, sys, html, hashlib, pathlib

FIGURES = json.load(open('content/blog/guides/figures/figures.json'))
ALLOWED_LINKS = {
    '/in-home-aba-therapy', '/aba-therapy-in-new-jersey', '/contact',
    '/early-intervention-new-jersey', '/transition-planning-new-jersey',
    '/behavior-support-new-jersey', '/parent-training-new-jersey',
    '/insurance-terminology', '/financial-aid-resources',
    '/post/aba-therapy-funding-new-jersey',
    '/post/how-much-is-aba-therapy-with-insurance',
    '/post/cost-of-aba-therapy-for-autism',
    '/post/iep-vs-504-plan-for-autism',
    '/post/early-signs-of-autism-in-babies-and-kids',
    '/aba-therapy-in-north-carolina', '/aba-therapy-in-georgia',
    '/transition-planning-north-carolina', '/early-intervention-north-carolina',
    '/behavior-support-north-carolina', '/parent-training-north-carolina',
}
used_figures = []

SRC = sys.argv[1]
DATA = sys.argv[2]
OUT = sys.argv[3]

raw = pathlib.Path(SRC).read_text(encoding='utf-8')
body = raw.split('---\n', 1)[1]
body = body.split('\n## Build notes', 1)[0].rstrip()
# drop the leading H1: Webflow renders the item name as the page H1
body = re.sub(r'\A\s*#\s+.*?\n', '', body, count=1).strip()
body = re.sub(r'\n-{3,}\s*\Z', '', body).strip()

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\[([^\]]+)\]\((https://[^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
    return s

out, lines, i = [], body.split('\n'), 0
while i < len(lines):
    ln = lines[i]
    if not ln.strip():
        i += 1; continue
    if ln.startswith('@figure '):
        slug = ln.split(None, 1)[1].strip()
        f = FIGURES.get(slug)
        if f is None:
            raise SystemExit(f'unknown figure slug: {slug}')
        used_figures.append(slug)
        out.append(
            '<figure class="w-richtext-align-center w-richtext-figure-type-image" '
            f'style="max-width:{f["width"]}px"><div>'
            f'<img width="{f["width"]}" src="{f["url"]}" loading="lazy" '
            f'alt="{html.escape(f["alt"], quote=True)}"></div></figure>')
        i += 1; continue
    if ln.startswith('## '):
        out.append(f'<h2>{inline(ln[3:].strip())}</h2>'); i += 1; continue
    if re.match(r'^\d+\.\s', ln):
        items = []
        while i < len(lines) and re.match(r'^\d+\.\s', lines[i]):
            txt = re.sub(r"^\d+\.\s+", "", lines[i])
            items.append("<li>" + inline(txt) + "</li>"); i += 1
        out.append('<ol>' + ''.join(items) + '</ol>'); continue
    if ln.startswith('- '):
        items = []
        while i < len(lines) and lines[i].startswith('- '):
            items.append("<li>" + inline(lines[i][2:]) + "</li>"); i += 1
        out.append('<ul>' + ''.join(items) + '</ul>'); continue
    s = ln.strip()
    mq = re.fullmatch(r'\*\*(.+\?)\*\*', s)
    if mq:
        out.append('<h3>' + inline(mq.group(1)) + '</h3>')
    else:
        out.append('<p>' + inline(s) + '</p>')
    i += 1

doc = ''.join(out)

# ---------------------------------------------------------------- gates
errs, warns = [], []

def err(m): errs.append(m)

# 1. copy gates
if re.search(r'[—–]', doc):
    err('em or en dash in body copy')
for pat, why in [
    (r'(?i)\bour (clinic|center|facility|centre)\b', 'implies a clinic or center'),
    (r'(?i)\bclinic-based\b', 'implies a clinic'),
    (r'(?i)\b(guarantee|guaranteed|will improve|proven results)\b', 'outcome guarantee'),
    (r'\bRBT\b', 'RBT acronym (house rule: Behavior Technician)'),
    (r'(?i)\bDr\.?\s+[A-Z][a-z]+,?\s*(BCBA|Ph\.?D)', 'named BCBA attribution'),
]:
    if re.search(pat, doc):
        err(f'{why}: {re.search(pat, doc).group(0)!r}')

phones = set(re.findall(r'\b\d{3}[.\-]\d{3}[.\-]\d{4}\b', doc))
OURS = '732.813.7333'
AGENCY = {'888.653.4463', '1.888.653.4463', '888-653-4463', '1-888-653-4463',
          '877.652.7624', '1.877.652.7624', '844.276.2444', '1.844.276.2444',
          '609.588.8522', '888.866.6205', '585.425.5296', '800.446.7467',
          '1.800.446.7467', '855.408.1212', '1.855.408.1212'}
stray = {p for p in phones if p != OURS and p not in AGENCY}
if stray:
    err(f'unrecognised phone number(s): {sorted(stray)}')

# 2. tag balance
tags = re.findall(r'</?([a-z0-9]+)[^>]*>', doc)
stack = []
for t in re.finditer(r'<(/?)([a-z0-9]+)[^>]*?(/?)>', doc):
    close, name, self_close = t.group(1), t.group(2), t.group(3)
    if self_close or name in ('br', 'img'):
        continue
    if close:
        if not stack or stack[-1] != name:
            err(f'tag mismatch at {t.start()}: </{name}> closes {stack[-1] if stack else "nothing"}')
            break
        stack.pop()
    else:
        stack.append(name)
if stack:
    err(f'unclosed tags: {stack}')
if '<p>---</p>' in doc or '<p>--</p>' in doc:
    err('stray horizontal rule left in body')
if re.search(r'<p><strong>[^<]*\?</strong></p>', doc):
    err('a question is still rendering as a bold paragraph rather than a heading')
if '<h2>Why Mastermind Behavior</h2>' not in doc:
    err('missing the Why Mastermind Behavior section')
if doc.index('<h2>Why Mastermind Behavior</h2>') > doc.index('<h2>Sources</h2>'):
    err('Why Mastermind Behavior must come before Sources')
if re.search(r'<\s+href', doc):
    err('clipped anchor tag (< href)')

# 3. every claim number must be traceable to the dataset
ds = json.load(open(DATA))
blob = json.dumps(ds)
norm_blob = re.sub(r'\\s+', ' ', ' '.join(re.findall(r'"value": "(.*?)", "source_url"', blob)).replace('\\"', '"'))
REQUIRED_BY_STATE = {
 'new-jersey': [
    ('$36,000', 'the cap figure'), ('180 days', 'internal appeal deadline'),
    ('four months', 'external review deadline'),
    ('1-888-653-4463', 'early intervention referral line'),
    ('120 days', 'part C to B evaluation request'), ('90 calendar days', 'evaluation to IEP'),
    ('48 hours', 'expedited external review'), ('February 9, 2010', 'mandate effective date'),
    ('under the age of twenty-one', 'medicaid age limit'),
    ('300% Federal Poverty Level', 'early intervention cost floor'),
 ],
 'north-carolina': [
    ('$40,000', 'the cap base figure'), ('Consumer Price Index', 'the indexing clause'),
    ('120 days', 'external review deadline'), ('three days', 'expedited external review'),
    ('July 1, 2016', 'mandate effective date'),
    ('ordered by a licensed physician or licensed psychologist', 'the order requirement'),
    ('180-calendar days', 'medicaid authorization window'),
    ('90 calendar days', 'medicaid authorization window above 16 hours'),
    ('birth to three', 'early intervention age range'),
    ('inability to pay', 'early intervention cost floor'),
    ('Smart NC', 'the external review body'),
 ],
 'georgia': [
    ('$35,000', 'the cap figure'), ('20 years of age or under', 'age limit'),
    ('July 1, 2015', 'mandate effective date'),
 ],
}
REQUIRED = REQUIRED_BY_STATE[ds['state_key']]
for needle, what in REQUIRED:
    if needle not in doc:
        err(f'missing required fact in body ({what}): {needle}')
    if needle not in norm_blob:
        err(f'fact not present in dataset ({what}): {needle}')

# 4. every direct quote must appear verbatim in the dataset.
# Quotes are extracted from the markdown source, where they are unambiguous,
# rather than from the HTML, where href attributes also use double quotes.
md_text = re.sub(r'\[([^\]]+)\]\(https://[^)]+\)', r'\1', body)
qs = re.findall(r'"([^"]{12,})"', md_text)
unmatched = []
for q in qs:
    probe = re.sub(r'\s+', ' ', q).strip().rstrip('.,;:')
    if probe not in norm_blob:
        unmatched.append(probe)
if unmatched:
    for u in unmatched:
        err(f'quoted string not found verbatim in dataset: {u[:90]!r}')

# 4b. figures
if not used_figures:
    err('no figure placed in this guide')
for slug in used_figures:
    f = FIGURES[slug]
    if not f['alt'].strip():
        err(f'figure {slug} has no alt text')
    if not f['url'].startswith('https://cdn.prod.website-files.com/'):
        err(f'figure {slug} is not on the Webflow CDN: {f["url"]}')
    if f['width'] != 600:
        err(f'figure {slug} must render at 600px, got {f["width"]}')
if 'w-richtext-align-fullwidth' in doc:
    err('a figure is set to full width; the article column is 821px and charts must not stretch')
if doc.count('<figure') != len(used_figures) or doc.count('</figure>') != len(used_figures):
    err('figure element count does not match the number of placed figures')

# 5. internal links resolve to known properties
for href in re.findall(r'href="(https://www\.mastermindbehavior\.com[^"]*)"', doc):
    if href.split('mastermindbehavior.com')[1] not in ALLOWED_LINKS:
        err(f'unexpected internal link: {href}')
n_links = len(re.findall(r'href="https://www\.mastermindbehavior\.com', doc))
n_h2 = doc.count('<h2>')
if n_links < 6:
    err(f'only {n_links} internal links in a page with {n_h2} sections; link contextually, not just at the end')
tail = doc.index('<h2>Why Mastermind Behavior</h2>')
if len(re.findall(r'href="https://www\.mastermindbehavior\.com', doc[:tail])) < 3:
    err('internal links are bunched at the end; at least three must sit in the body')

pathlib.Path(OUT).write_text(doc, encoding='utf-8')
print(f'{len(doc)} chars  md5={hashlib.md5(doc.encode()).hexdigest()}')
print(f'quotes checked against dataset: {len(qs)}')
for w in warns: print('WARN', w)
for e in errs: print('ERROR', e)
sys.exit(1 if errs else 0)
