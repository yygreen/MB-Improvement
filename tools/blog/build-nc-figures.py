#!/usr/bin/env python3
"""Generate the two NJ funding figures. Geometry is computed here, written into
the HTML, then re-derived from the published values and asserted."""
import json, pathlib, sys

DATA = json.load(open('data/funding/north-carolina.json'))
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
    ('NC Infant-Toddler Program',        'Birth to age three',       0.0,  3.0,  '#c14a3f', False),
    ('School district, IEP',             'From the third birthday',  3.0,  22.0, '#9a9484', True),
    ('State mandate, N.C.G.S. 58-3-192', 'May be limited to 18 or younger', 0.0, 19.0, '#009499', False),
    ('NC Medicaid, RB-BHT',              'Continues past 21',        0.0,  22.0, '#1a2744', True),
]
REFERRAL = 3.0 - 90 / 365.0           # transition meeting due no later than 90 days before age three
TICKS = [0, 3, 5, 10, 15, 21]

need('18 years of age or younger', 'mandate.age_limit', 'mandate age limit')
need('under 21', 'medicaid.age_limit', 'medicaid age')
need('over the age of 21', 'medicaid.age_limit', 'the 21-plus expansion')
need('birth to three', 'early_intervention.age_range', 'EI age range')
need('90 days before your child', 'school_services.idea_part_c_to_b_transition', 'transition meeting lead time')
need('third birthday', 'school_services.idea_part_c_to_b_transition', 'FAPE start')

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
assert 2.70 < (mark_x / 100) * AX1 < 2.80, 'marker is not ~90 days before age three'

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
<h2>Who pays, and until when</h2>
<div class="sub">The same child moves between systems on fixed dates. Age in years across the bottom.</div>
<div class="lane"><div class="markl" style="left:{mark_x}%">Transition meeting due</div></div>
<div class="plot">
{''.join(rows)}
  <div class="markwrap"><div class="mark" style="left:{mark_x}%"></div></div>
</div>
<div class="axis"><div class="line"></div>{ticks}
  <div class="unit">Age in years</div>
</div>
<div class="credit">Mastermind Behavior. Sources: N.C.G.S. 58-3-192; NC Medicaid Policy 8F; NC DPI; NCDHHS.</div>
</body></html>'''

if '<div class="lane">' not in fig1 or fig1.index('class="markl"') > fig1.index('<div class="plot">'):
    errs.append('the marker label must sit in its own lane above the plot, not inside it')
if 'class="markl"' in fig1[fig1.index('<div class="plot">'):]:
    errs.append('a marker label is still rendered inside the plot area')

(OUT / 'nc-who-pays-when.html').write_text(fig1, encoding='utf-8')

for e in errs:
    print('ERROR', e)
print('figures written' if not errs else 'FAILED')
sys.exit(1 if errs else 0)
