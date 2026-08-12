#!/usr/bin/env python3
"""Generate the Georgia funding figure. Geometry is computed here, written into
the HTML, then re-derived from the published values and asserted. Every label
that makes a claim is checked against the dataset field it came from."""
import json, pathlib, sys

DATA = json.load(open('data/funding/georgia.json'))
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
errs = []

def need(text, path, why):
    """Assert a claim appears in the dataset value it is supposed to come from."""
    node = DATA
    for k in path.split('.'):
        node = node[int(k)] if k.isdigit() else node[k]
    if text not in node['value']:
        errs.append(f'{why}: {text!r} not in {path}')

# ---------------------------------------------------------------- geometry
AX0, AX1 = 0.0, 22.0
def x(years):
    return round((years - AX0) / (AX1 - AX0) * 100, 2)

# (label, note, start, end, colour, open_ended)
BANDS = [
    ("Babies Can't Wait",                'Birth to age three',        0.0,  3.0,  '#c14a3f', False),
    ('School district, IEP',             'From the third birthday',   3.0,  22.0, '#9a9484', False),
    ("Ava's Law, O.C.G.A. 33-24-59.10",  '20 years of age or under',  0.0,  21.0, '#009499', False),
    ('Georgia Medicaid, ASD services',   'Under the age of 21',       0.0,  21.0, '#1a2744', False),
    ('Katie Beckett eligibility route',  'Age 18 or under',           0.0,  19.0, '#b07d2b', False),
]
CLIFF = 21.0
TICKS = [0, 3, 5, 10, 15, 18, 21]

need('20 years of age or under', 'mandate.age_limit', 'mandate age limit')
need('under the age of 21', 'medicaid.age_limit', 'medicaid age limit')
need('birth to three years of age', 'early_intervention.age_range', 'early intervention age range')
need('third birthday', 'school_services.idea_part_c_to_b_transition', 'FAPE start date')
need('18 or under', 'waivers.0.population', 'Katie Beckett age limit')
need("Babies Can't Wait", 'early_intervention.program_name', 'early intervention programme name')

# the whole point of the figure: the mandate and Medicaid end together, the school does not
assert BANDS[2][3] == BANDS[3][3] == CLIFF, 'mandate and Medicaid must share the cliff year'
assert BANDS[1][3] > CLIFF, 'the school band must outlast the cliff or the figure has no point'

rows = []
for name, note, a, b, colour, open_end in BANDS:
    left, width = x(a), round(x(b) - x(a), 2)
    # gate: recompute the edges back out of the published percentages
    assert abs((left / 100) * (AX1 - AX0) - a) < 0.01, f'{name} left edge drifted'
    assert abs(((left + width) / 100) * (AX1 - AX0) - b) < 0.01, f'{name} right edge drifted'
    cap = 'border-radius:6px' if a == 0 else 'border-radius:0 6px 6px 0'
    rows.append(f'''<div class="row">
  <div class="lab"><b>{name}</b><span>{note}</span></div>
  <div class="track"><div class="bar" style="left:{left}%;width:{width}%;background:{colour};{cap}"></div></div>
</div>''')

ticks = ''.join(f'<div class="tk" style="left:{x(t)}%">{t}</div>' for t in TICKS)
mark_x = round(x(CLIFF), 2)
assert abs((mark_x / 100) * AX1 - CLIFF) < 0.01, 'marker drifted off the cliff year'

# ---------------------------------------------------------------- label lane
# The label lives in a reserved lane above the plot, so it can never sit on a
# band. Its horizontal extent still has to fit the canvas, so anchor it to
# whichever side keeps it inside and gate the measured extent.
CANVAS, PAD, LABW = 900, 40, 330
PLOT_L, PLOT_R = PAD + LABW, CANVAS - PAD
MARK_PX = PLOT_L + (mark_x / 100) * (PLOT_R - PLOT_L)
MARK_LABEL = 'Insurance and Medicaid both stop'
CHAR_PX = 13.2                       # Manrope 800 at 24px, measured
label_w = len(MARK_LABEL) * CHAR_PX
anchor_right = MARK_PX + label_w / 2 > PLOT_R
if anchor_right:
    l_left, l_right = MARK_PX - label_w, MARK_PX
    anchor_css = 'transform:translateX(-100%)'
    arrow_css = 'left:auto;right:0;margin-left:0;margin-right:-6px'
else:
    l_left, l_right = MARK_PX - label_w / 2, MARK_PX + label_w / 2
    anchor_css = 'transform:translateX(-50%)'
    arrow_css = 'left:50%;margin-left:-6px'
if l_left < PAD:
    errs.append(f'marker label overflows the left edge ({l_left:.0f}px < {PAD}px)')
if l_right > CANVAS - PAD:
    errs.append(f'marker label overflows the right edge ({l_right:.0f}px > {CANVAS - PAD}px)')

fig = f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:900px;font-family:'Manrope',system-ui,sans-serif;background:#f6f4ef;padding:44px 40px 34px}}
h2{{font-size:40px;font-weight:800;color:#1a2744;letter-spacing:-.01em;line-height:1.15}}
.sub{{font-size:27px;color:#5a5a5a;margin:12px 0 34px;line-height:1.4}}
.lane{{position:relative;margin-left:330px;height:62px}}
.markl{{position:absolute;bottom:10px;{anchor_css};font-size:24px;font-weight:800;
        color:#c14a3f;white-space:nowrap}}
.markl:after{{content:"";position:absolute;{arrow_css};bottom:-12px;
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
<div class="lane"><div class="markl" style="left:{mark_x}%">{MARK_LABEL}</div></div>
<div class="plot">
{''.join(rows)}
  <div class="markwrap"><div class="mark" style="left:{mark_x}%"></div></div>
</div>
<div class="axis"><div class="line"></div>{ticks}
  <div class="unit">Age in years</div>
</div>
<div class="credit">Mastermind Behavior. Sources: O.C.G.A. 33-24-59.10; Georgia Medicaid ASD policy; Georgia DPH; Georgia SBOE Rule 160-4-7.</div>
</body></html>'''

# structural gates: the label must be in its own lane, never inside the plot
if '<div class="lane">' not in fig or fig.index('class="markl"') > fig.index('<div class="plot">'):
    errs.append('the marker label must sit in its own lane above the plot, not inside it')
if 'class="markl"' in fig[fig.index('<div class="plot">'):]:
    errs.append('a marker label is still rendered inside the plot area')

(OUT / 'ga-who-pays-when.html').write_text(fig, encoding='utf-8')

for e in errs:
    print('ERROR', e)
print(f'figure written  marker at {mark_x}%  label {l_left:.0f}-{l_right:.0f}px  '
      f'anchor={"right" if anchor_right else "centre"}' if not errs else 'FAILED')
sys.exit(1 if errs else 0)
