#!/usr/bin/env python3
"""Gate for the state funding dataset.

Every fact that reaches a family through a guide, the cost calculator, or the
mandate lookup widget must be traceable to a primary source and must carry the
date it was checked. Coverage rules change; a fact with no expiry is a fact
that will quietly go wrong.

Run: python3 tools/funding/validate-funding.py [--max-age-days 180]
Exit 0 only if every state file passes. Anything else is a build failure.
"""
import json, sys, re, glob, argparse
from datetime import date, datetime

# Primary sources only. A .com citation is a research lead, not a source.
ALLOWED_HOST_SUFFIXES = (
    '.gov', '.us', '.mil',
    'ecfr.gov', 'govinfo.gov',
    'bacb.com',          # credentialing body, authoritative for its own certs
)

REQUIRED_BLOCKS = [
    'mandate', 'self_funded_exemption', 'medicaid',
    'early_intervention', 'appeals',
]

# data/costs/*.json carries the published Medicaid fee schedule figures the cost
# calculator renders. Same fail-closed rules, different required blocks.
COST_REQUIRED_BLOCKS = ['medicaid_rates', 'commercial_rates']

# The single most consequential field on the whole property: a state mandate
# does not reach self-funded ERISA plans, so a widget that answers "yes, your
# plan must cover ABA" without this branch can send a family into an appeal
# they cannot win.
SAFETY_CRITICAL = ['self_funded_exemption']

FACT_KEYS = {'value', 'source_url', 'source_type', 'source_title', 'verified_on'}
SOURCE_TYPES = {'statute', 'regulation', 'medicaid_manual', 'doi_bulletin',
                'agency_page', 'federal', 'waiver_document'}


def is_fact(node):
    return isinstance(node, dict) and 'value' in node


def walk(node, path, errs, warns, max_age_days, today):
    if is_fact(node):
        check_fact(node, path, errs, warns, max_age_days, today)
        check_rate(node, path, errs)
        check_cap(node, path, errs)
        return
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, f'{path}.{k}', errs, warns, max_age_days, today)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f'{path}[{i}]', errs, warns, max_age_days, today)


def check_rate(f, path, errs):
    """A machine-readable rate must match the prose a family will read.

    The calculator renders rate_per_unit; the guide renders value. If they drift
    apart, the page says one number and the widget says another, and nobody
    notices until a parent does.
    """
    if 'rate_per_unit' not in f:
        return
    r = f['rate_per_unit']
    if not isinstance(r, (int, float)) or r <= 0:
        errs.append(f'{path}: rate_per_unit must be a positive number, got {r!r}')
        return
    if f.get('minutes_per_unit') != 15:
        errs.append(f'{path}: rate_per_unit needs minutes_per_unit 15, got {f.get("minutes_per_unit")!r}')
    txt = f.get('value') or ''
    if f'${r:.2f}' not in txt:
        errs.append(f'{path}: prose does not contain the rate it is paired with '
                    f'(${r:.2f} missing from value)')
    if 'code' in f and f['code'] not in txt:
        errs.append(f'{path}: prose does not name the CPT code {f["code"]}')


CAP_STATUSES = {'rarely_applicable', 'stale_base_indexed', 'applies_to_aba_only'}


def check_cap(f, path, errs):
    """The calculator does arithmetic with cap_usd; the page renders value.

    cap_status is what stops the widget printing a bare ceiling. Every state's
    cap carries a catch, and a calculator that shows the number without the
    catch is worse than one that shows nothing.
    """
    if 'cap_usd' not in f:
        return
    c = f['cap_usd']
    if not isinstance(c, int) or c <= 0:
        errs.append(f'{path}: cap_usd must be a positive integer, got {c!r}')
        return
    if f'${c:,}' not in (f.get('value') or ''):
        errs.append(f'{path}: prose does not contain the cap it is paired with (${c:,})')
    if f.get('cap_status') not in CAP_STATUSES:
        errs.append(f'{path}: cap_usd needs a cap_status in {sorted(CAP_STATUSES)}, '
                    f'got {f.get("cap_status")!r}')


def check_fact(f, path, errs, warns, max_age_days, today):
    missing = FACT_KEYS - set(f)
    if missing:
        errs.append(f'{path}: missing {sorted(missing)}')
        return
    if f['value'] in (None, '', 'TODO', 'UNVERIFIED'):
        errs.append(f'{path}: value not filled in ({f["value"]!r})')
    url = f['source_url'] or ''
    if not url.startswith('https://'):
        errs.append(f'{path}: source_url must be https, got {url!r}')
    else:
        host = url.split('/')[2].lower().split(':')[0]
        if not any(host.endswith(s) for s in ALLOWED_HOST_SUFFIXES):
            errs.append(f'{path}: {host} is not a primary source')
    if f['source_type'] not in SOURCE_TYPES:
        errs.append(f'{path}: source_type {f["source_type"]!r} not in {sorted(SOURCE_TYPES)}')
    try:
        v = datetime.strptime(f['verified_on'], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        errs.append(f'{path}: verified_on must be YYYY-MM-DD, got {f["verified_on"]!r}')
        return
    if v > today:
        errs.append(f'{path}: verified_on {v} is in the future')
    age = (today - v).days
    if age > max_age_days:
        errs.append(f'{path}: STALE, verified {age} days ago (limit {max_age_days})')
    elif age > max_age_days * 0.75:
        warns.append(f'{path}: verified {age} days ago, re-check soon')
    # site copy rule travels with the data, since these strings get rendered
    if isinstance(f['value'], str) and ('—' in f['value'] or '–' in f['value']):
        warns.append(f'{path}: value contains an em/en dash, will trip the copy gate')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-age-days', type=int, default=180)
    a = ap.parse_args()
    today = date.today()
    files = ([(p, REQUIRED_BLOCKS) for p in sorted(glob.glob('data/funding/*.json'))] +
             [(p, COST_REQUIRED_BLOCKS) for p in sorted(glob.glob('data/costs/*.json'))])
    if not files:
        print('no state files found under data/funding/ or data/costs/'); return 1
    failed = False
    for path, required_blocks in files:
        errs, warns = [], []
        try:
            d = json.load(open(path))
        except json.JSONDecodeError as e:
            print(f'FAIL {path}: not valid JSON: {e}'); failed = True; continue
        for b in required_blocks:
            if b not in d:
                errs.append(f'missing required block: {b}')
        for b in SAFETY_CRITICAL:
            if b in required_blocks:
                blk = d.get(b)
                if not blk or (isinstance(blk, dict) and not blk):
                    errs.append(f'SAFETY-CRITICAL block {b} is empty')
        walk(d, path.split('/')[-1].replace('.json', ''), errs, warns, a.max_age_days, today)
        n_facts = sum(1 for _ in re.finditer(r'"value"', open(path).read()))
        if errs:
            failed = True
            print(f'FAIL {path}  ({n_facts} facts, {len(errs)} errors)')
            for e in errs[:40]:
                print(f'   - {e}')
            if len(errs) > 40:
                print(f'   ... and {len(errs)-40} more')
        else:
            print(f'PASS {path}  ({n_facts} facts, 0 errors, {len(warns)} warnings)')
        for w in warns[:10]:
            print(f'   ! {w}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
