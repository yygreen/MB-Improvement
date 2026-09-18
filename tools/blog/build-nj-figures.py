#!/usr/bin/env python3
"""Generate the two NJ funding figures. Geometry is computed here, written into
the HTML, then re-derived from the published values and asserted."""
import json, pathlib, sys, re

DATA = json.load(open('data/funding/new-jersey.json'))
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
errs = []


def field(path):
    node = DATA
    for k in path.split('.'):
        node = node[int(k)] if k.isdigit() else node[k]
    return node


def need(text, path, why):
    """Assert a claim appears in the dataset value it is supposed to come from."""
    if text not in field(path)['value']:
        errs.append(f'{why}: {text!r} not in {path}')


WORDS = {'three': 3, 'twenty-one': 21}


def edge(path, pattern, offset, why):
    """Derive a closed band's exclusive right edge from the dataset prose.

    The school band used to end at a hardcoded 22.0 with no dataset field
    behind it, which is the defect the Georgia figure audit found. offset
    turns an inclusive age into an exclusive edge.
    """
    m = re.search(pattern, field(path)['value'], re.I)
    if not m:
        errs.append(f'{why}: {pattern!r} does not match {path}, cannot derive the edge')
        return None
    tok = m.group(1).lower()
    n = WORDS.get(tok)
    if n is None:
        n = int(tok)
    return float(n + offset)

# ---------------------------------------------------------------- figure 1
AX0, AX1 = 0.0, 22.0
def x(years):
    return round((years - AX0) / (AX1 - AX0) * 100, 2)

E_EI   = edge('early_intervention.age_range', r'birth and age (three|\d+)', 0, 'EI end')
E_MAND = edge('mandate.age_limit', r'under (\d+) years of age', 0, 'mandate end')
E_MCD  = edge('medicaid.age_limit', r'under the age of (twenty-one|\d+)', 0, 'medicaid end')
E_DDD  = edge('waivers.0.population', r'Being (\d+) Years of age or older', 0, 'DDD floor')

# The school band is open-ended by law, not by drawing style: N.J.A.C. 6A:14
# ends the entitlement at the close of the school year in which the student
# turns 21, so the true edge varies with the birthday and can reach just
# short of 22. An arrow past the axis plus the caveat is the honest render;
# a hard bar at 22 would promise most families a year they do not get.
BANDS = [
    ('New Jersey Early Intervention', 'Birth to age three',      0.0,  E_EI,   '#c14a3f', False),
    ('School district, IEP',          'From the third birthday', 3.0,  AX1,    '#9a9484', True),
    ('Chapter 115, commercial insurance', 'ABA for under 21',    0.0,  E_MAND, '#009499', False),
    ('NJ FamilyCare, EPSDT autism benefit', 'Under 21',          0.0,  E_MCD,  '#1a2744', False),
    ('DDD waiver programs',           'Age 21 and over',        E_DDD, AX1,    '#6f6a5e', True),
]
REFERRAL = 3.0 - 120 / 365.0          # 120 days before the third birthday
TICKS = [0, 3, 5, 10, 15, 21]

need('under 21 years of age', 'mandate.age_limit', 'commercial ABA age')
need('under the age of twenty-one', 'medicaid.age_limit', 'medicaid age')
need('birth and age three', 'early_intervention.age_range', 'EI age range')
need('at least 120 days prior to the preschooler attaining age three',
     'school_services.idea_part_c_to_b_transition', 'referral lead time')
need('third birthday', 'school_services.idea_part_c_to_b_transition', 'FAPE start')
need('age three through 21', 'school_services.age_out', 'school age range')
need('continue to be provided services for the balance of that school year',
     'school_services.age_out', 'the finish-the-year rule')
need('graduation', 'school_services.diploma_exit', 'diploma exit')
if DATA['waivers'][0]['population']['value'].find('21 Years of age or older') < 0:
    errs.append('waiver age floor not found in waivers[0].population')

if None in (E_EI, E_MAND, E_MCD, E_DDD):
    for e in errs:
        print('ERROR', e)
    sys.exit(1)

# every edge must be readable: closed edges are ticks; open-ended bands must
# run exactly to the axis end, where the arrow says "continues", never stop
# at an unlabelled year inside the plot
for name, _, a, b, _, open_end in BANDS:
    if open_end:
        if b != AX1:
            errs.append(f'{name} is open-ended but stops at {b:g}, inside the axis; '
                        f'an arrow that stops mid-plot labels nothing')
    elif b not in TICKS:
        errs.append(f'{name} ends at {b:g}, which is not a tick; the reader cannot '
                    f'tell where the band stops')
    if a not in (0.0, 3.0) and a not in TICKS:
        errs.append(f'{name} starts at {a:g}, which is not a tick')

rows = []
for name, note, a, b, colour, open_end in BANDS:
    left, width = x(a), round(x(b) - x(a), 2)
    # gate: recompute the edges from the published percentages
    assert abs((left / 100) * (AX1 - AX0) - a) < 0.01, f'{name} left edge drifted'
    assert abs(((left + width) / 100) * (AX1 - AX0) - b) < 0.01, f'{name} right edge drifted'
    cap = 'border-radius:0 6px 6px 0' if not open_end else \
          'border-radius:0;clip-path:polygon(0 0,calc(100% - 16px) 0,100% 50%,calc(100% - 16px) 100%,0 100%)'
    if a == 0:
        cap = cap.replace('border-radius:0 6px 6px 0', 'border-radius:6px')
    rows.append(f'''<div class="row">
  <div class="lab"><b>{name}</b><span>{note}</span></div>
  <div class="track"><div class="bar" style="left:{left}%;width:{width}%;background:{colour};{cap}"></div></div>
</div>''')

ticks = ''.join(
    f'<div class="tk" style="left:{x(t)}%">{t}</div>' for t in TICKS)
mark_x = round(x(REFERRAL), 2)
assert 2.6 < (mark_x / 100) * AX1 < 2.75, 'referral marker is not ~4 months before age three'

# The arrows continue past the axis for a reason, and the reason has to be on
# the image itself. Numbers interpolate from the derived edges above.
CAVEAT = (f'<b>The school band has no single end date.</b> Services run to the close '
          f'of the school year in which a student turns {E_MAND:g}, so the exact edge '
          f'depends on the birthday. Graduating with a regular high school diploma '
          f'ends them sooner, at any age. A GED, a certificate of completion or a '
          f'certificate of attendance does not.')
for needle, why in [('regular high school diploma', 'the diploma exit'),
                    (f'turns {E_MAND:g}', 'the finish-the-year rule')]:
    if needle not in CAVEAT:
        errs.append(f'caveat does not carry {why}')

fig1 = f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:900px;font-family:'Manrope',system-ui,sans-serif;background:#f6f4ef;padding:44px 40px 34px}}
h2{{font-size:40px;font-weight:800;color:#1a2744;letter-spacing:-.01em;line-height:1.15}}
.sub{{font-size:27px;color:#5a5a5a;margin:12px 0 34px;line-height:1.4}}
.lane{{position:relative;margin-left:330px;height:62px}}
.markl{{position:absolute;bottom:10px;transform:translateX(-50%);font-size:24px;font-weight:800;
        color:#c14a3f;white-space:nowrap}}
.markl:after{{content:"";position:absolute;left:50%;bottom:-12px;margin-left:-6px;
              border:6px solid transparent;border-top-color:#c14a3f}}
.plot{{position:relative}}
.row{{display:flex;align-items:center;margin-bottom:18px}}
.lab{{width:330px;padding-right:22px;flex:none}}
.lab b{{display:block;font-size:26px;font-weight:800;color:#1a2744;line-height:1.22}}
.lab span{{display:block;font-size:25px;color:#6f6a5e;margin-top:3px}}
.track{{position:relative;flex:1;height:46px;background:#e6e2da;border-radius:6px}}
.bar{{position:absolute;top:0;height:46px}}
.markwrap{{position:absolute;left:330px;right:0;top:0;bottom:18px;pointer-events:none}}
.mark{{position:absolute;top:0;bottom:0;width:3px;background:#c14a3f;transform:translateX(-1px)}}
.axis{{position:relative;margin-left:330px;height:70px;margin-top:2px}}
.axis .line{{position:absolute;top:0;left:0;right:0;height:3px;background:#c9c4b8}}
.tk{{position:absolute;top:12px;transform:translateX(-50%);font-size:25px;color:#6f6a5e;white-space:nowrap}}
.unit{{position:absolute;top:44px;left:0;font-size:25px;color:#8a8a8a}}
.caveat{{margin-top:14px;font-size:24px;line-height:1.42;color:#5a5a5a}}
.caveat b{{font-weight:800;color:#1a2744}}
.credit{{margin-top:14px;font-size:23px;color:#8a8a8a}}
</style></head><body>
<h2>Who is responsible, and when</h2>
<div class="sub">The same child moves between systems on fixed dates. Age in years across the bottom.</div>
<div class="lane"><div class="markl" style="left:{mark_x}%">Referral to district due</div></div>
<div class="plot">
{''.join(rows)}
  <div class="markwrap"><div class="mark" style="left:{mark_x}%"></div></div>
</div>
<div class="axis"><div class="line"></div>{ticks}
  <div class="unit">Age in years</div>
</div>
<div class="caveat">{CAVEAT}</div>
<div class="credit">Mastermind Behavior. Sources: N.J.A.C. 6A:14; DOBI Bulletin 10-02; NJ Medicaid SPA 19-0003; NJ DDD; 34 CFR 300.102.</div>
</body></html>'''

# ---------------------------------------------------------------- figure 2
need('180 days', 'appeals.internal_appeal_deadline', 'stage 1 deadline')
need('10 business days', 'appeals.internal_appeal_deadline', 'stage 1 decision')
need('72 hours', 'appeals.internal_appeal_deadline', 'urgent decision')
need('20 business days', 'appeals.internal_appeal_deadline', 'stage 2 decision')
need('four-month period', 'appeals.external_review_deadline', 'external deadline')
need('48 hours', 'appeals.expedited_route', 'expedited decision')
need('Carriers bear the costs', 'appeals.how_to_file', 'no fee to family')

STEPS = [
    ('Denial', 'Your clock starts the day you receive the adverse determination.',
     '', '', '#c14a3f'),
    ('Stage 1 internal appeal', 'Filed with your carrier.',
     '180 days', 'to file. Decision in 10 business days, or 72 hours if urgent.', '#009499'),
    ('Stage 2 internal appeal', 'Still with your carrier.',
     '180 days', 'to file. Decision in 20 business days.', '#009499'),
    ('IHCAP external review', 'Decided by an independent review organization, not your carrier.',
     '4 months', 'from the final internal determination. Expedited decisions in 48 hours. No cost to you.', '#1a2744'),
]
step_html = ''.join(f'''<div class="step">
  <div class="dot" style="background:{c}"></div>
  <div class="body"><b>{t}</b><span class="d">{d}</span>
  {f'<span class="clock" style="color:{c}">{n}</span><span class="cn">{cn}</span>' if n else ''}</div>
</div>''' for t, d, n, cn, c in STEPS)

fig2 = f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:900px;font-family:'Manrope',system-ui,sans-serif;background:#f6f4ef;padding:44px 40px 34px}}
h2{{font-size:40px;font-weight:800;color:#1a2744;letter-spacing:-.01em;line-height:1.15}}
.sub{{font-size:27px;color:#5a5a5a;margin:12px 0 36px;line-height:1.4}}
.steps{{position:relative;padding-left:52px}}
.steps:before{{content:"";position:absolute;left:13px;top:14px;bottom:64px;width:4px;background:#e0dcd3}}
.step{{position:relative;margin-bottom:30px}}
.dot{{position:absolute;left:-52px;top:8px;width:30px;height:30px;border-radius:50%;border:5px solid #f6f4ef}}
.body b{{display:block;font-size:30px;font-weight:800;color:#1a2744;line-height:1.2}}
.d{{display:block;font-size:25px;color:#6f6a5e;margin-top:5px;line-height:1.35}}
.clock{{display:inline-block;font-size:34px;font-weight:800;margin-top:10px}}
.cn{{font-size:25px;color:#5a5a5a;margin-left:10px;line-height:1.35}}
.credit{{margin-top:6px;font-size:23px;color:#8a8a8a}}
</style></head><body>
<h2>The appeal clock in New Jersey</h2>
<div class="sub">Denials are often reversed. Missing a date is the avoidable way to lose.</div>
<div class="steps">{step_html}</div>
<div class="credit">Mastermind Behavior. Source: NJ Department of Banking and Insurance, UM appeals and IHCAP. Does not apply to self-funded plans.</div>
</body></html>'''

if '<div class="lane">' not in fig1 or fig1.index('class="markl"') > fig1.index('<div class="plot">'):
    errs.append('the marker label must sit in its own lane above the plot, not inside it')
if 'class="markl"' in fig1[fig1.index('<div class="plot">'):]:
    errs.append('a marker label is still rendered inside the plot area')

(OUT / 'nj-who-pays-when.html').write_text(fig1, encoding='utf-8')
(OUT / 'nj-appeal-clock.html').write_text(fig2, encoding='utf-8')

for e in errs:
    print('ERROR', e)
print('figures written' if not errs else 'FAILED')
sys.exit(1 if errs else 0)
