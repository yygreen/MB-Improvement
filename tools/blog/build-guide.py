#!/usr/bin/env python3
"""Generate a Webflow rich-text body from a funding guide markdown file, and gate it.

Never hand-retype the payload: it is generated here, asserted against the
funding dataset, and the same file is what gets pushed to the CMS.
"""
import json, re, sys, html, hashlib, pathlib

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
          '1.800.446.7467'}
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
REQUIRED = [
    ('$36,000', 'the cap figure'),
    ('180 days', 'internal appeal deadline'),
    ('four months', 'external review deadline'),
    ('1-888-653-4463', 'early intervention referral line'),
    ('120 days', 'part C to B evaluation request'),
    ('90 calendar days', 'evaluation to IEP'),
    ('48 hours', 'expedited external review'),
    ('February 9, 2010', 'mandate effective date'),
    ('under the age of twenty-one', 'medicaid age limit'),
    ('300% Federal Poverty Level', 'early intervention cost floor'),
]
for needle, what in REQUIRED:
    if needle not in doc:
        err(f'missing required fact in body ({what}): {needle}')
    if needle not in norm_blob:
        err(f'fact not present in dataset ({what}): {needle}')

# 4. every direct quote must appear verbatim in the dataset.
# Quotes are extracted from the markdown source, where they are unambiguous,
# rather than from the HTML, where href attributes also use double quotes.
md_text = re.sub(r'\[([^\]]+)\]\(https://[^)]+\)', r'\1', body)
qs = re.findall(r'"([^"]{25,})"', md_text)
unmatched = []
for q in qs:
    probe = re.sub(r'\s+', ' ', q).strip().rstrip('.,;:')
    if probe not in norm_blob:
        unmatched.append(probe)
if unmatched:
    for u in unmatched:
        err(f'quoted string not found verbatim in dataset: {u[:90]!r}')

# 5. internal links resolve to known properties
for href in re.findall(r'href="(https://www\.mastermindbehavior\.com[^"]*)"', doc):
    if href.split('mastermindbehavior.com')[1] not in (
            '/in-home-aba-therapy', '/aba-therapy-in-new-jersey', '/contact'):
        err(f'unexpected internal link: {href}')

pathlib.Path(OUT).write_text(doc, encoding='utf-8')
print(f'{len(doc)} chars  md5={hashlib.md5(doc.encode()).hexdigest()}')
print(f'quotes checked against dataset: {len(qs)}')
for w in warns: print('WARN', w)
for e in errs: print('ERROR', e)
sys.exit(1 if errs else 0)
