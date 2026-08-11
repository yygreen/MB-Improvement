#!/usr/bin/env python3
"""Generate the two NJ funding figures. Geometry is computed here, written into
the HTML, then re-derived from the published values and asserted."""
import json, pathlib, sys

DATA = json.load(open('data/funding/new-jersey.json'))
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
errs = []

def need(text, path, why):
    """Assert a claim appears in the dataset value it is supposed to come from."""
    node = DATA
    for k in path.split('.'):
        node = node[k]
    if text not in node['value']:
        errs.append(f'{why}: {text!r} not in {path}')

# ---------------------------------------------------------------- figure 1
AX0, AX1 = 0.0, 22.0
def x(years):
    return round((years - AX0) / (AX1 - AX0) * 100, 2)

BANDS = [
    ('New Jersey Early Intervention', 'Birth to age three',      0.0,  3.0,  '#c14a3f', False),
    ('School district, IEP',          'From the third birthday', 3.0,  22.0, '#9a9484', True),
    ('Chapter 115, commercial insurance', 'ABA for under 21',    0.0,  21.0, '#009499', False),
    ('NJ FamilyCare, EPSDT autism benefit', 'Under 21',          0.0,  21.0, '#1a2744', False),
    ('DDD waiver programs',           'Age 21 and over',        21.0, 22.0, '#6f6a5e', True),
]
REFERRAL = 3.0 - 120 / 365.0          # 120 days before the third birthday
TICKS = [0, 3, 5, 10, 15, 21]

need('under 21 years of age', 'mandate.age_limit', 'commercial ABA age')
need('under the age of twenty-one', 'medicaid.age_limit', 'medicaid age')
need('birth and age three', 'early_intervention.age_range', 'EI age range')
need('at least 120 days prior to the preschooler attaining age three',
     'school_services.idea_part_c_to_b_transition', 'referral lead time')
need('third birthday', 'school_services.idea_part_c_to_b_transition', 'FAPE start')
need('Being 21 Years of age or older', 'waivers.0.population'.replace('.0.', '.'), 'waiver age') \
    if False else None
if DATA['waivers'][0]['population']['value'].find('21 Years of age or older') < 0:
    errs.append('waiver age floor not found in waivers[0].population')

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
.credit{{margin-top:16px;font-size:23px;color:#8a8a8a}}
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
<div class="credit">Mastermind Behavior. Sources: N.J.A.C. 6A:14; DOBI Bulletin 10-02; NJ Medicaid SPA 19-0003; NJ DDD.</div>
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
