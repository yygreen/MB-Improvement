#!/usr/bin/env python3
"""Generate the two NC funding figures. Geometry is computed here, written into
the HTML, then re-derived from the published values and asserted."""
import json, pathlib, sys, re

DATA = json.load(open('data/funding/north-carolina.json'))
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
    n = {'three': 3}.get(tok)
    if n is None:
        n = int(tok)
    return float(n + offset)

# ---------------------------------------------------------------- figure 1
AX0, AX1 = 0.0, 22.0
def x(years):
    return round((years - AX0) / (AX1 - AX0) * 100, 2)

E_EI   = edge('early_intervention.age_range', r'birth to (three|\d+)', 0, 'EI end')
E_MAND = edge('mandate.age_limit', r'(\d+) years of age or younger', 1, 'mandate end')
# The school band and the Medicaid band both genuinely continue past this
# axis: 115C-107.1(a)(2) carries a student in services to the end of the
# school year in which they turn 22, and NC Medicaid's RB-BHT coverage
# continues over 21. Open-ended to the axis end is the honest render for
# both; the caveat carries the school rule.
BANDS = [
    ('NC Infant-Toddler Program',        'Birth to age three',       0.0,  E_EI,   '#c14a3f', False),
    ('School district, IEP',             'From the third birthday',  3.0,  AX1,    '#9a9484', True),
    ('State mandate, N.C.G.S. 58-3-192', 'May be limited to 18 or younger', 0.0, E_MAND, '#009499', False),
    ('NC Medicaid, RB-BHT',              'Continues past 21',        0.0,  AX1,    '#1a2744', True),
]
REFERRAL = 3.0 - 90 / 365.0           # transition meeting due no later than 90 days before age three
# 19 joins the ticks so the mandate band's edge is readable; it was the same
# unlabelled-edge defect the Georgia audit found.
TICKS = [0, 3, 5, 10, 15, 19, 21]

need('18 years of age or younger', 'mandate.age_limit', 'mandate age limit')
need('under 21', 'medicaid.age_limit', 'medicaid age')
need('over the age of 21', 'medicaid.age_limit', 'the 21-plus expansion')
need('birth to three', 'early_intervention.age_range', 'EI age range')
need('90 days before your child', 'school_services.idea_part_c_to_b_transition', 'transition meeting lead time')
need('third birthday', 'school_services.idea_part_c_to_b_transition', 'FAPE start')
need('the ages of three through 21', 'school_services.age_out', 'school age range')
need('the end of the school year in which that child reaches the age of 22',
     'school_services.age_out', 'the (a)(2) continuation')
need('has not graduated from high school', 'school_services.diploma_exit', 'diploma exit')

if None in (E_EI, E_MAND):
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

# The arrows continue past the axis for a reason, and the reason has to be on
# the image itself.
CAVEAT = ('<b>The school band runs past the chart, until graduation.</b> A student '
          'already receiving services keeps them to the end of the school year in '
          'which they turn 22, but graduating with a regular high school diploma '
          'ends them at any age. A GED, a certificate of completion or a '
          'certificate of attendance does not.')
for needle, why in [('regular high school diploma', 'the diploma exit'),
                    ('turn 22', 'the (a)(2) continuation')]:
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
<div class="caveat">{CAVEAT}</div>
<div class="credit">Mastermind Behavior. Sources: N.C.G.S. 58-3-192; N.C.G.S. 115C-107.1; NC Medicaid Policy 8F; NC DPI; NCDHHS; 34 CFR 300.102.</div>
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
