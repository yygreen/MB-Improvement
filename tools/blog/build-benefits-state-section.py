#!/usr/bin/env python3
"""Generate the State-Mandated Autism Benefits section for the benefits post.

The section as written profiled California, Arizona and Florida in three
tables, and gave the three states we actually serve a single paragraph with
no sources and no links. Every row in those tables said "Required" or
"Included" with nothing behind it.

This replaces them with New Jersey, Georgia and North Carolina, every figure
read out of data/funding/*.json and every state pointing at its guide. That
is the whole argument for building the datasets: the highest-traffic page in
the cluster should be the one that sends families into it.

Run: python3 tools/blog/build-benefits-state-section.py [outfile]
Exit 0 only if every gate holds.
"""
import json, pathlib, re, sys, hashlib

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                   'content/blog/fragments/benefits-state-section.html')
STATES = [
    ('new-jersey', 'New Jersey', '/post/aba-therapy-funding-new-jersey'),
    ('georgia', 'Georgia', '/post/aba-therapy-funding-georgia'),
    # NC was rewritten in place on its existing URL rather than published at a
    # new slug, so it does not follow the aba-therapy-funding-* pattern. The
    # live-URL check in the writer catches this if it ever moves.
    ('north-carolina', 'North Carolina',
     '/post/is-aba-therapy-covered-by-insurance-north-carolina'),
]

data = {s: json.load(open(f'data/funding/{s}.json')) for s, _, _ in STATES}

# Prose is written here rather than lifted from the datasets, because the
# dataset values are research notes addressed to us and run to paragraphs.
# The figures, though, are asserted against the datasets below: if a statute
# or a cap ever changes in the data, this refuses to build.
COPY = {
    'new-jersey': {
        'intro': ('New Jersey&#x27;s mandate is P.L. 2009, c. 115, which the Department of '
                  'Banking and Insurance refers to as Chapter 115. It reaches hospital, '
                  'medical and health service corporation contracts, insurance company '
                  'policies and HMO coverage issued or renewed in New Jersey on or after '
                  'February 9, 2010.'),
        'rows': [
            ('The law', 'P.L. 2009, c. 115, at N.J.S.A. 17:48-6ii and parallel sections'),
            ('Ages covered for ABA', 'Under 21'),
            ('Annual dollar cap',
             '$36,000 is the figure usually quoted, but the insurance regulator has said '
             'it often cannot lawfully be applied. Ask your plan to confirm in writing '
             'whether it is applying a dollar maximum to ABA, and on what basis'),
            ('Visit or hour limits',
             'None set by the statute, and a carrier may not cut your other therapy '
             'benefits because they were used to treat autism'),
        ],
    },
    'georgia': {
        'intro': ('Georgia&#x27;s mandate is Ava&#x27;s Law, at O.C.G.A. 33-24-59.10, as '
                  'expanded by SB 118 in 2018. The original requirement reaches plans '
                  'issued or renewed in Georgia on or after July 1, 2015.'),
        'rows': [
            ('The law', "Ava&#x27;s Law, O.C.G.A. 33-24-59.10, as expanded by SB 118"),
            ('Ages covered', '20 years of age or under. SB 118 struck the word six and '
                             'inserted 20'),
            ('Annual dollar cap',
             '$35,000 a year for applied behavior analysis specifically. It is a ceiling '
             'a plan may choose to apply, not a budget you are handed'),
            ('Visit or hour limits',
             'None permitted. The statute says a policy &#x22;shall not include any limits '
             'on the number of visits&#x22;'),
        ],
    },
    'north-carolina': {
        'intro': ('North Carolina&#x27;s mandate came in through Session Law 2015-271 and '
                  'is codified at N.C.G.S. 58-3-192. It applies to contracts issued, '
                  'renewed or amended on or after July 1, 2016.'),
        'rows': [
            ('The law', 'Session Law 2015-271, codified at N.C.G.S. 58-3-192'),
            ('Ages covered',
             'The statute says adaptive behavior treatment &#x22;may be limited to '
             'individuals 18 years of age or younger&#x22;. Read the shape of that '
             'sentence: it is something a plan is permitted to do, not a statement that '
             'older children are excluded'),
            ('Annual dollar cap',
             '$40,000 a year, with a catch. That is a 2015 base which the statute then '
             'indexes, so the live ceiling is higher and we could not find the current '
             'amount published anywhere citable. Ask your insurer for it in writing'),
            ('Visit or hour limits',
             'None set. The only limit the statute names is the annual dollar maximum'),
        ],
    },
}

INTRO = (
    '<h2>State-Mandated Autism Benefits</h2>'
    '<p>Most states now require some form of autism coverage on fully insured '
    'commercial plans, but the age caps, dollar limits and provider rules differ '
    'enough that a general statement about state mandates is not much use to any '
    'one family. What follows is what the law actually says in the three states '
    'our practice serves. Every figure below comes from the statute itself or from '
    'the state insurance regulator, and each state links to a fuller guide that '
    'names the source.</p>'
)

CLOSE = (
    '<p>Two things decide whether any of this reaches your family. The first is '
    'whether your employer buys coverage from an insurer or self-funds it, because '
    'a self-funded plan sits outside state insurance law and the state cap, the '
    'state deadline and the state regulator are not levers you hold. The second is '
    'your state Medicaid position, which is separate from the commercial mandate '
    'and is often more generous on age. Both are covered in the state guides above, '
    'and the terms themselves are explained on our '
    '<a href="/insurance-terminology">insurance terminology page</a>.</p>'
)


def table(rows):
    head = ('<table><thead><tr><th style="text-align: left;"></th>'
            '<th style="text-align: left;"></th></tr></thead><tbody>')
    body = ''.join(
        f'<tr><td style="text-align: left;"><strong>{k}</strong></td>'
        f'<td style="text-align: left;">{v}</td></tr>' for k, v in rows)
    return head + body + '</tbody></table>'


parts = [INTRO]
for slug, name, guide in STATES:
    c = COPY[slug]
    parts.append(f'<h3>{name} Coverage</h3>')
    parts.append(f'<p>{c["intro"]}</p>')
    parts.append(table(c['rows']))
    parts.append(f'<p><a href="{guide}">Read the full {name} funding guide</a>, '
                 f'which covers Medicaid, the appeal deadlines and what to do when a '
                 f'plan says no.</p>')
parts.append(CLOSE)
htmlout = ''.join(parts)

# ---------------------------------------------------------------- gates
g = []

# 1. Every cap printed must match the dataset, and must carry its catch.
for slug, name, _ in STATES:
    cap = data[slug]['mandate']['annual_dollar_cap']
    lit = f'${cap["cap_usd"]:,}'
    if lit not in htmlout:
        g.append(f'{slug}: cap literal {lit} from the dataset is not in the section')
    status = cap['cap_status']
    # the sentence carrying the figure must not stop at the figure
    for m in re.finditer(re.escape(lit) + r'(.{0,200})', htmlout, re.S):
        tail = m.group(1)
        if status == 'stale_base_indexed' and 'catch' not in tail:
            g.append(f'{slug}: stale base cap printed without its catch')
        if status == 'rarely_applicable' and 'cannot lawfully' not in tail:
            g.append(f'{slug}: rarely-applicable cap printed without the regulator caveat')
        if status == 'applies_to_aba_only' and 'ceiling' not in tail:
            g.append(f'{slug}: aba-only cap printed without the ceiling framing')

# 2. No currency literal that is not one of those three caps.
known = {f'${data[s]["mandate"]["annual_dollar_cap"]["cap_usd"]:,}' for s, _, _ in STATES}
for m in re.finditer(r'\$\d[\d,]*', htmlout):
    if m.group(0) not in known:
        g.append(f'unexplained currency literal: {m.group(0)}')

# 3. Ages must match the datasets.
for slug, needle in [('new-jersey', 'under 21'), ('georgia', '20 years of age or under'),
                     ('north-carolina', '18 years of age or younger')]:
    if needle.lower() not in data[slug]['mandate']['age_limit']['value'].lower():
        g.append(f'{slug}: age wording {needle!r} not supported by the dataset')
    if needle.lower() not in htmlout.lower():
        g.append(f'{slug}: age wording {needle!r} missing from the section')

# 4. Each guide linked exactly once, and no state left out.
for _, name, guide in STATES:
    if htmlout.count(f'href="{guide}"') != 1:
        g.append(f'{guide} linked {htmlout.count(chr(34) + guide + chr(34))} times, want 1')

# 5. The states we do not serve must be gone.
for bad in ('California', 'Arizona', 'Florida'):
    if bad in htmlout:
        g.append(f'{bad} still present; this section is about the states we serve')

# 6. House copy gates.
if re.search(r'[—–]', htmlout):
    g.append('em or en dash in fresh copy')
if re.search(r'\bRBT\b', htmlout):
    g.append('RBT acronym in fresh copy')
if re.search(r'\bclinic|\bcenter-based|\bcenters\b', htmlout, re.I):
    g.append('clinic or center language in fresh copy')
if re.search(r'\bguarantee', htmlout, re.I):
    g.append('outcome guarantee language')
if 'Every state' in htmlout:
    g.append('the unsourced every-state claim survived')

if g:
    for e in g:
        print('GATE', e)
    sys.exit(1)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(htmlout, encoding='utf-8')
print(f'{len(htmlout)} chars  md5={hashlib.md5(htmlout.encode()).hexdigest()}')
for slug, name, guide in STATES:
    cap = data[slug]['mandate']['annual_dollar_cap']
    print(f'  {name}: ${cap["cap_usd"]:,} ({cap["cap_status"]}) -> {guide}')
