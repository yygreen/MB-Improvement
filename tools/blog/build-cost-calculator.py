#!/usr/bin/env python3
"""Generate the ABA cost calculator widget from the funding and cost datasets.

Never hand-write the figures. Every number the widget can display is read out
of data/funding/*.json and data/costs/*.json here, asserted against the prose
those datasets carry, and baked into the emitted JS. The widget does no
network calls, so there is no CORS surface and nothing to go stale silently
between the page and the data.

The design rule this file exists to enforce: the calculator never invents a
price. It asks the family for the rate on their own quote or EOB, and applies
the sourced rules to it. Where a figure is flagged in the dataset, the widget
says so rather than printing a number we cannot stand behind.

Run: python3 tools/blog/build-cost-calculator.py [outfile]
Exit 0 only if every assertion holds.
"""
import json, pathlib, sys, re, hashlib

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                   'content/blog/widgets/aba-cost-calculator.js')
PATH_GATE = '/post/cost-of-aba-therapy-for-autism'
STATES = ['new-jersey', 'georgia', 'north-carolina']
errs = []

funding = {s: json.load(open(f'data/funding/{s}.json')) for s in STATES}
costs = {s: json.load(open(f'data/costs/{s}.json')) for s in STATES}


def fact(d, path):
    node = d
    for k in path.split('.'):
        node = node[int(k)] if k.isdigit() else node[k]
    return node


def need(state, ds, path, needle, why):
    """Assert a string we are about to render appears in the dataset value."""
    try:
        v = fact(ds, path)['value']
    except (KeyError, TypeError):
        errs.append(f'{state}: {path} missing entirely ({why})')
        return
    if needle not in v:
        errs.append(f'{state}: {why}: {needle!r} not in {path}')


model = {}
for s in STATES:
    f, c = funding[s], costs[s]
    cap = fact(f, 'mandate.annual_dollar_cap')
    age = fact(f, 'mandate.age_limit')
    visits = fact(f, 'mandate.visit_or_hour_limits')
    selffund = fact(f, 'self_funded_exemption.applies')
    mcaid_age = fact(f, 'medicaid.age_limit')
    mcaid_pa = fact(f, 'medicaid.prior_authorization')

    # gates: the widget's claims must come from the dataset, not from here
    need(s, f, 'mandate.annual_dollar_cap', f'${cap["cap_usd"]:,}', 'cap figure')
    # 'self-fund' rather than 'self-funded': Georgia's dataset says "self-funds"
    need(s, f, 'self_funded_exemption.applies', 'self-fund', 'self-funded exemption')

    # the Medicaid rate is optional: a state may legitimately have none sourced
    rate = None
    for key in ('direct_treatment_technician_home', 'direct_treatment_technician'):
        node = c['medicaid_rates'].get(key)
        if node and 'rate_per_unit' in node:
            rate = {'per_unit': node['rate_per_unit'],
                    'per_hour': round(node['rate_per_unit'] * 4, 2),
                    'code': node['code'],
                    'note': node['value']}
            need(s, c, f'medicaid_rates.{key}', f'${node["rate_per_unit"]:.2f}',
                 'medicaid rate figure')
            break

    flags = []
    for blk, path in (('funding', 'mandate.annual_dollar_cap'),
                      ('costs', 'medicaid_rates.schedule_name'),
                      ('costs', 'commercial_rates.published')):
        src = f if blk == 'funding' else c
        try:
            v = fact(src, path)['value']
        except (KeyError, TypeError):
            continue
        if v.startswith('FLAG'):
            flags.append(re.sub(r'^FLAG,\s*', '', v).strip())

    model[s] = {
        'name': f['state'],
        'cap': cap['cap_usd'],
        'capStatus': cap['cap_status'],
        'ageLimit': age['value'],
        'visitLimits': visits['value'],
        'selfFunded': selffund['value'],
        'medicaidAge': mcaid_age['value'],
        'medicaidPA': mcaid_pa['value'],
        'medicaidRate': rate,
        'flags': flags,
    }

# the three cap statuses each need a sentence, and every state must map to one
CAP_COPY = {
    'rarely_applicable':
        'The cap is on the books, but your plan often cannot lawfully apply it. '
        'Ask the insurer to confirm in writing whether it is applying a dollar '
        'maximum to ABA, and why.',
    'stale_base_indexed':
        'The figure in the statute is a base, not the live ceiling. It has been '
        'indexed for years and we could not find the current amount published '
        'anywhere we could cite. Ask your insurer for the current indexed '
        'maximum in writing.',
    'applies_to_aba_only':
        'The cap applies to applied behavior analysis specifically, not to '
        'everything the mandate covers. A plan may apply it, so read your plan '
        'documents and raise federal parity if it does.',
}
for s, m in model.items():
    if m['capStatus'] not in CAP_COPY:
        errs.append(f'{s}: cap_status {m["capStatus"]!r} has no explanatory copy')

if not any(m['medicaidRate'] for m in model.values()):
    errs.append('no state has a sourced Medicaid rate; the widget has no anchor')

if errs:
    for e in errs:
        print('ERROR', e)
    sys.exit(1)

payload = json.dumps({'states': model, 'capCopy': CAP_COPY},
                     ensure_ascii=False, separators=(',', ':'))

js = '''/* ABA cost calculator. GENERATED by tools/blog/build-cost-calculator.py.
   Do not edit by hand: every figure below is read out of data/funding/*.json
   and data/costs/*.json and asserted at build time. Edit the data, rebuild. */
(function () {
  "use strict";
  if (location.pathname.replace(/\\/+$/, "") !== "%PATH%") return;
  var D = %PAYLOAD%;
  var root = document.getElementById("mm-ccw");
  if (!root) {
    // Webflow's rich-text sanitiser may drop the id on save. Fall back to the
    // sentinel paragraph, so the widget survives that without a code change.
    var nodes = document.querySelectorAll("p, div");
    for (var i = 0; i < nodes.length; i++) {
      if ((nodes[i].textContent || "").trim().indexOf("Calculator loading.") === 0) {
        root = nodes[i]; break;
      }
    }
  }
  if (!root) return;

  var money = function (n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  };

  root.innerHTML = [
    '<div class="mm-ccw-box">',
    '  <div class="mm-ccw-h">What will ABA actually cost us?</div>',
    '  <p class="mm-ccw-sub">We will not guess your provider\\'s rate. Put in the number from your quote or an explanation of benefits, and this works out what your plan can and cannot do with it.</p>',
    '  <div class="mm-ccw-row">',
    '    <label>State<select id="mm-ccw-state"></select></label>',
    '    <label>Who is paying<select id="mm-ccw-plan">',
    '      <option value="insured">Fully insured plan</option>',
    '      <option value="selffunded">Self-funded employer plan</option>',
    '      <option value="medicaid">Medicaid</option>',
    '    </select></label>',
    '  </div>',
    '  <div class="mm-ccw-row">',
    '    <label>Hours a week<input id="mm-ccw-hours" type="number" min="1" max="40" step="1" value="15"></label>',
    '    <label>Rate an hour<input id="mm-ccw-rate" type="number" min="1" max="500" step="1" placeholder="from your quote"></label>',
    '  </div>',
    '  <div id="mm-ccw-out" class="mm-ccw-out"></div>',
    '</div>'
  ].join("");

  var sel = root.querySelector("#mm-ccw-state");
  Object.keys(D.states).forEach(function (k) {
    var o = document.createElement("option");
    o.value = k; o.textContent = D.states[k].name; sel.appendChild(o);
  });

  function render() {
    var s = D.states[sel.value];
    var plan = root.querySelector("#mm-ccw-plan").value;
    var hours = parseFloat(root.querySelector("#mm-ccw-hours").value) || 0;
    var rateEl = root.querySelector("#mm-ccw-rate");
    var rate = parseFloat(rateEl.value) || 0;
    var out = [];

    if (plan === "medicaid") {
      if (s.medicaidRate) {
        out.push('<p><b>' + s.name + ' Medicaid publishes its rate.</b> Code ' +
          s.medicaidRate.code + ' pays $' + s.medicaidRate.per_hour.toFixed(2) +
          ' an hour, billed as $' + s.medicaidRate.per_unit.toFixed(2) +
          ' per 15 minute unit.</p>');
        out.push('<p class="mm-ccw-big">' + money(s.medicaidRate.per_hour * hours * 52) +
          ' a year at ' + hours + ' hours a week</p>');
        out.push('<p class="mm-ccw-note">That is what the state pays the provider, not what you pay. On Medicaid this is generally not billed to you.</p>');
      } else {
        out.push('<p><b>' + s.name + ' does not publish a Medicaid rate we could source.</b> We are not going to print one. Ask your plan for the adaptive behavior fee schedule in writing.</p>');
      }
      out.push('<p class="mm-ccw-note"><b>Age.</b> ' + s.medicaidAge + '</p>');
      out.push('<p class="mm-ccw-note"><b>Prior authorization.</b> ' + s.medicaidPA + '</p>');
    } else if (plan === "selffunded") {
      out.push('<p><b>The ' + s.name + ' mandate does not reach your plan.</b> ' + s.selfFunded + '</p>');
      if (rate && hours) {
        out.push('<p class="mm-ccw-big">' + money(rate * hours * 52) + ' a year at ' +
          hours + ' hours a week</p>');
        out.push('<p class="mm-ccw-note">No state dollar cap applies, which cuts both ways: nothing limits the benefit, and nothing obliges the plan to provide one. Your appeal rights are federal rather than state.</p>');
      } else {
        out.push('<p class="mm-ccw-note">Put in your hourly rate to see the annual figure.</p>');
      }
    } else {
      if (rate && hours) {
        var annual = rate * hours * 52;
        out.push('<p class="mm-ccw-big">' + money(annual) + ' a year at ' + hours +
          ' hours a week</p>');
        out.push('<p><b>The ' + s.name + ' cap is ' + money(s.cap) + '.</b> ' +
          D.capCopy[s.capStatus] + '</p>');
        if (annual > s.cap) {
          out.push('<p class="mm-ccw-note">Your figure is ' + money(annual - s.cap) +
            ' above that cap. Whether that gap is real depends entirely on the sentence above, which is why we will not show you a single confident number.</p>');
        } else {
          out.push('<p class="mm-ccw-note">Your figure sits inside that cap, so the ceiling is unlikely to be what limits your care. Hours authorized usually matter more.</p>');
        }
      } else {
        out.push('<p class="mm-ccw-note">Put in your hourly rate to see the annual figure. If you do not have one yet, ask a provider for their rate for code 97153.</p>');
      }
      out.push('<p class="mm-ccw-note"><b>Visit limits.</b> ' + s.visitLimits + '</p>');
    }

    if (s.flags.length) {
      out.push('<div class="mm-ccw-flag"><b>What we could not source</b><ul><li>' +
        s.flags.join("</li><li>") + '</li></ul></div>');
    }
    root.querySelector("#mm-ccw-out").innerHTML = out.join("");
  }

  root.addEventListener("input", render);
  root.addEventListener("change", render);
  render();
})();
'''.replace('%PATH%', PATH_GATE).replace('%PAYLOAD%', payload)

# ---------------------------------------------------------------- gates
g = []
if 'FLAG,' in js:
    g.append('a raw FLAG, prefix leaked into the widget copy')
for s, m in model.items():
    if str(m['cap']) not in payload:
        g.append(f'{s}: cap missing from the baked payload')
if re.search(r'[—–]', js):
    g.append('em or en dash in widget copy')
if re.search(r'\bRBT\b', js):
    g.append('RBT acronym in widget copy')
if 'location.pathname' not in js or PATH_GATE not in js:
    g.append('widget is not path-gated')
# the whole point: no invented price anywhere in the emitted file
for m in re.finditer(r'\$\d[\d,]{2,}', js):
    lit = m.group(0)
    if not any(lit == f'${x["cap"]:,}' for x in model.values()):
        g.append(f'unexplained currency literal in widget: {lit}')
if g:
    for e in g:
        print('GATE', e)
    sys.exit(1)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(js, encoding='utf-8')
print(f'{len(js)} chars  md5={hashlib.md5(js.encode()).hexdigest()}')
print(f'states: {", ".join(model)}')
print('sourced Medicaid rates: ' +
      ', '.join(f'{s} ${m["medicaidRate"]["per_hour"]}/hr' for s, m in model.items()
                if m['medicaidRate']) or 'none')
print('flags carried into the widget: ' +
      str(sum(len(m['flags']) for m in model.values())))
