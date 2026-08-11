#!/usr/bin/env python3
"""Add contextual internal links to the seven shipped rewrites.

Every edit is an exact-string replacement asserted to occur exactly once, so a
drifted body fails loudly instead of being silently mangled. Output is gated
before anything is sent to the CMS.
"""
import re, sys, hashlib, pathlib

SRC = pathlib.Path(sys.argv[1])          # dir holding the shipped bodies
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
B = 'https://www.mastermindbehavior.com'

def L(path, text):
    return f'<a href="{B}{path}">{text}</a>'

STATES = (f"{L('/aba-therapy-in-new-jersey','New Jersey')}, "
          f"{L('/aba-therapy-in-georgia','Georgia')}, or "
          f"{L('/aba-therapy-in-north-carolina','North Carolina')}")
STATES_AND = (f"{L('/aba-therapy-in-new-jersey','New Jersey')}, "
              f"{L('/aba-therapy-in-georgia','Georgia')}, and "
              f"{L('/aba-therapy-in-north-carolina','North Carolina')}")

PLAN = {
 'does-emotional-neglect-cause-autism': ('neglect-post-body-v2.html', [
   ("New Jersey, Georgia, or North Carolina", STATES),
   ('href="https://www.mastermindbehavior.com/services"',
    'href="https://www.mastermindbehavior.com/in-home-aba-therapy"'),
   ("evidence-based support, and a team that treats you as part of the solution",
    f"{L('/early-intervention','evidence-based support')}, and a team that treats you as part of the solution"),
 ]),
 'camel-milk-for-autism': ('camel-post-body.html', [
   ("New Jersey, Georgia, or North Carolina", STATES),
   ("speech and occupational therapy matched to need, and parent coaching.",
    f"speech and occupational therapy matched to need, and {L('/parent-training-new-jersey','parent coaching')}."),
 ]),
 'vitamin-d-and-autism': ('vitd-post-body.html', [
   ("New Jersey, Georgia, or North Carolina", STATES),
   ("Whatever role nutrition plays, it operates in a small remainder rather than the main story.",
    "Whatever role nutrition plays, it operates in a small remainder rather than the main story. "
    f"If what you want is a plan rather than a supplement, that is what {L('/in-home-aba-therapy','in-home ABA therapy')} is for."),
 ]),
 'autism-and-gluten-free-casein-free-gfcf-diet': ('gfcf-post-body.html', [
   ("New Jersey, Georgia, or North Carolina, our team is happy to talk it through.",
    f"{STATES}, {L('/contact','our team is happy to talk it through')}."),
   ("Not to talk you out of it, but to protect calcium, vitamin D, and overall intake while you run the trial, and to set a defined review point rather than an open-ended commitment.",
    "Not to talk you out of it, but to protect calcium, vitamin D, and overall intake while you run the trial, and to set a defined review point rather than an open-ended commitment. "
    f"If the goal underneath the diet is progress on skills and behavior, that is what {L('/in-home-aba-therapy','in-home ABA therapy')} is built for."),
 ]),
 'dairy-and-autism': ('dairy-post-body.html', [
   ("New Jersey, Georgia, and North Carolina", STATES_AND),
   ("<strong>Set a review date.</strong> An open-ended elimination with no checkpoint tends to become permanent by default rather than by decision.",
    "<strong>Set a review date.</strong> An open-ended elimination with no checkpoint tends to become permanent by default rather than by decision. "
    f"If the goal is progress on behavior rather than on diet, {L('/behavior-support-new-jersey','behavior support')} is the more direct route."),
 ]),
 'can-emfs-cause-autism': ('emf-post-body.html', [
   ("New Jersey, Georgia, or North Carolina, our team can help you work out the next step.",
    f"{STATES}, {L('/contact','our team can help you work out the next step')}."),
   ("the useful next step is a developmental screening, not an EMF meter.",
    f"the useful next step is a {L('/early-intervention','developmental screening')}, not an EMF meter."),
 ]),
 'what-is-defeat-autism-now': ('dan-post-body.html', [
   ("New Jersey, Georgia, or North Carolina", STATES),
   ("<strong>Parent training</strong>, which reduces family stress and supports child progress",
    f"<strong>{L('/parent-training-new-jersey','Parent training')}</strong>, which reduces family stress and supports child progress"),
 ]),
}

ALLOWED = {
 '/in-home-aba-therapy','/contact','/early-intervention','/insurance-terminology',
 '/aba-therapy-in-new-jersey','/aba-therapy-in-georgia','/aba-therapy-in-north-carolina',
 '/behavior-support-new-jersey','/parent-training-new-jersey','/transition-planning-new-jersey',
 '/early-intervention-new-jersey',
}
errs = []
for slug, (fname, edits) in PLAN.items():
    body = (SRC / fname).read_text(encoding='utf-8')
    before = len(re.findall(rf'href="{re.escape(B)}[^"]*"', body))
    for old, new in edits:
        n = body.count(old)
        if n != 1:
            errs.append(f'{slug}: anchor appears {n} times, expected 1: {old[:60]!r}')
            continue
        body = body.replace(old, new, 1)
    links = re.findall(rf'href="{re.escape(B)}([^"]*)"', body)
    svc = [l for l in links if not l.startswith('/post/')]
    bad = [l for l in svc if l not in ALLOWED]
    faq = body.find('<h2>FAQ') if '<h2>FAQ' in body else body.find('<h2>Where can I get support')
    in_body = [l for l in re.findall(rf'href="{re.escape(B)}([^"]*)"', body[:faq]) if not l.startswith('/post/')]
    if bad: errs.append(f'{slug}: link outside the allowlist: {bad}')
    if len(svc) < 4: errs.append(f'{slug}: only {len(svc)} service links, need 4')
    if not in_body: errs.append(f'{slug}: no service link before the FAQ')
    if re.search(r'[—–]', body): errs.append(f'{slug}: em or en dash introduced')
    if '<a href' in body and re.search(r'<a[^>]*>\s*</a>', body): errs.append(f'{slug}: empty anchor')
    if body.count('<a ') != body.count('</a>'): errs.append(f'{slug}: unbalanced anchor tags')
    (OUT / f'{slug}.html').write_text(body, encoding='utf-8')
    print(f'{slug:48s} {before} -> {len(links)} links  ({len(svc)} service, {len(in_body)} before FAQ)  '
          f'md5 {hashlib.md5(body.encode()).hexdigest()[:12]}')

for e in errs: print('ERROR', e)
sys.exit(1 if errs else 0)
