// Merge two near-duplicate stylesheets that load on the SAME page into one.
//
// WHY THIS EXISTS
//
// Several pages inline two copies of essentially the same sheet, one per HTML embed.
// They are not byte-identical -- they have drifted -- and the LATER embed wins wherever
// they disagree, because that is how the cascade works for equal specificity.
//
// This is the only kind of duplication that actually costs page weight. Duplication
// ACROSS pages costs nothing at render time: a Webflow component is authored once but
// still inlines into every page that instances it. Componentising cross-page duplication
// buys maintainability (one edit, no future drift); merging within-page duplication buys
// bytes. Do not confuse the two -- the first hub component made its pages 604 B *larger*.
//
// MERGE SEMANTICS
//
//   winning value for (context, selector, property) = later sheet's, else earlier sheet's
//   emission order = rules unique to the earlier sheet first, then the later sheet in full
//
// Placing earlier-only rules first is safe precisely because they do not appear in the
// later sheet, so nothing they could conflict with follows them. Everything shared takes
// the later sheet's value and its position, which is what the browser resolves to today.
//
// usage: node merge-page-sheets.mjs <earlier.css> <later.css> <out.css>
'use strict';
import { readFileSync, writeFileSync } from 'node:fs';

function stripComments(css) {
  let out = '', quote = null;
  for (let i = 0; i < css.length; i++) {
    const c = css[i];
    if (quote) {
      out += c;
      if (c === '\\') { out += css[++i] ?? ''; continue; }
      if (c === quote) quote = null;
      continue;
    }
    if (c === '"' || c === "'") { quote = c; out += c; continue; }
    if (c === '/' && css[i + 1] === '*') {
      const end = css.indexOf('*/', i + 2);
      i = end === -1 ? css.length : end + 1;
      out += ' ';
      continue;
    }
    out += c;
  }
  return out;
}

const normSpace = s => s.replace(/\s+/g, ' ').trim();
const normContext = s => normSpace(s).replace(/\s*([:,()])\s*/g, '$1').toLowerCase();
const normSelector = s => normSpace(s).replace(/\s*([>+~])\s*/g, ' $1 ');

function parseDecls(body) {
  const out = new Map();
  let buf = '', depth = 0, quote = null;
  const push = () => {
    const d = normSpace(buf); buf = '';
    if (!d) return;
    const i = d.indexOf(':');
    if (i < 0) return;
    out.set(d.slice(0, i).trim().toLowerCase(), d.slice(i + 1).trim());
  };
  for (let i = 0; i < body.length; i++) {
    const c = body[i];
    if (quote) { buf += c; if (c === '\\') { buf += body[++i] ?? ''; continue; } if (c === quote) quote = null; continue; }
    if (c === '"' || c === "'") { quote = c; buf += c; continue; }
    if (c === '(') depth++;
    if (c === ')') depth--;
    if (c === ';' && depth === 0) { push(); continue; }
    buf += c;
  }
  push();
  return out;
}

// Ordered list of {context, prelude, selectors, decls}
function parseRules(css) {
  const src = stripComments(css);
  const rules = [];
  const stack = [];
  let buf = '', quote = null;
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (quote) { buf += c; if (c === '\\') { buf += src[++i] ?? ''; continue; } if (c === quote) quote = null; continue; }
    if (c === '"' || c === "'") { quote = c; buf += c; continue; }
    if (c === '{') {
      const prelude = normSpace(buf); buf = '';
      if (prelude.startsWith('@')) { stack.push(prelude); continue; }
      let depth = 1, q2 = null, end = -1;
      const bodyStart = i + 1;
      for (let k = bodyStart; k < src.length; k++) {
        const d = src[k];
        if (q2) { if (d === '\\') { k++; continue; } if (d === q2) q2 = null; continue; }
        if (d === '"' || d === "'") { q2 = d; continue; }
        if (d === '{') depth++;
        else if (d === '}') { depth--; if (depth === 0) { end = k; break; } }
      }
      if (end < 0) break;
      rules.push({
        context: stack.map(normContext).join(' && '),
        contextRaw: [...stack],
        prelude,
        selectors: prelude.split(',').map(normSelector).filter(Boolean),
        decls: parseDecls(src.slice(bodyStart, end)),
      });
      i = end;
      continue;
    }
    if (c === '}') { stack.pop(); buf = ''; continue; }
    if (c === ';') { buf = ''; continue; }
    buf += c;
  }
  return rules;
}

const [earlierPath, laterPath, outPath] = process.argv.slice(2);
if (!earlierPath || !laterPath || !outPath) {
  console.error('usage: node merge-page-sheets.mjs <earlier.css> <later.css> <out.css>');
  process.exit(2);
}

const earlier = parseRules(readFileSync(earlierPath, 'utf8'));
const later = parseRules(readFileSync(laterPath, 'utf8'));

// Key on a SINGLE selector, never on the comma group.
//
// Keying on the group is wrong and silently drops declarations: if a selector is grouped
// in one sheet (`.a, .b { background: red }`) and standalone in the other (`.a { … }`),
// the two keys differ, the grouped rule is classified "earlier-only" and emitted FIRST,
// and the later standalone rule then overrides it without the property. That is exactly
// how `.hero-cta` lost its background on the first attempt -- caught by the render diff,
// not by reading the output.
const key = (ctx, sel) => `${ctx}||${sel}`;

const flatten = rules => {
  const m = new Map();   // key -> {context, contextRaw, selector, decls}
  for (const r of rules) {
    for (const sel of r.selectors) {
      const k = key(r.context, sel);
      if (!m.has(k)) m.set(k, { context: r.context, contextRaw: r.contextRaw, selector: sel, decls: new Map() });
      for (const [p, v] of r.decls) m.get(k).decls.set(p, v);
    }
  }
  return m;
};

const earlierFlat = flatten(earlier);
const laterFlat = flatten(later);

// "Later wins" holds only at EQUAL importance. An !important declaration in the earlier
// sheet beats a non-important one in the later sheet, so a naive later-wins merge silently
// demotes it -- and the demoted value may then lose to some third rule it used to outrank.
//
// That is exactly what happened to `.hero-cta`: the earlier copy declared
// `background: #db5b4f !important`, the later copy dropped the !important, and both sheets
// carry `.mm-embed a { background-color: transparent !important }`. Taking the later value
// made the button transparent. Caught by the render diff, not by reading the CSS.
const important = v => /!\s*important\s*$/i.test(v);

let backfilled = 0, keptImportant = 0;
const merged = new Map();
// later sheet's order and values first
for (const [k, r] of laterFlat) merged.set(k, { ...r, decls: new Map(r.decls) });
// then reconcile against the earlier sheet
for (const [k, r] of earlierFlat) {
  const hit = merged.get(k);
  if (!hit) continue;
  for (const [p, v] of r.decls) {
    const cur = hit.decls.get(p);
    if (cur === undefined) { hit.decls.set(p, v); backfilled++; }
    else if (important(v) && !important(cur)) { hit.decls.set(p, v); keptImportant++; }
  }
}
// selectors the later sheet never mentions
const earlierOnly = [...earlierFlat].filter(([k]) => !merged.has(k)).map(([, r]) => r);

const emit = rules => {
  const out = [];
  let openCtx = null;
  for (const r of rules) {
    const ctx = r.contextRaw.join(' ');
    if (ctx !== openCtx) {
      if (openCtx) out.push('}');
      if (ctx) out.push(ctx + ' {');
      openCtx = ctx;
    }
    const body = [...r.decls].map(([p, v]) => `${p}: ${v};`).join(' ');
    out.push(`  ${r.selector} { ${body} }`);
  }
  if (openCtx) out.push('}');
  return out.join('\n');
};

const emitted = [];
if (earlierOnly.length) {
  emitted.push('/* --- selectors present only in the first embed\'s copy, preserved --- */');
  emitted.push(emit(earlierOnly));
}
emitted.push('/* --- merged: the later embed\'s values win, as they do today --- */');
emitted.push(emit([...merged.values()]));

const out = emitted.join('\n');
writeFileSync(outPath, out);

const before = readFileSync(earlierPath, 'utf8').length + readFileSync(laterPath, 'utf8').length;
console.log(`earlier: ${earlier.length} rules   later: ${later.length} rules`);
console.log(`rules only in earlier sheet : ${earlierOnly.length} (preserved, emitted first)`);
console.log(`properties backfilled from earlier: ${backfilled}   !important kept from earlier: ${keptImportant}`);
console.log(`bytes: ${before} -> ${out.length}  (saved ${before - out.length})`);
