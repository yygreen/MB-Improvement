// Rebase the shared sheet onto /in-home-aba-therapy as the design reference.
//
// WHY THIS EXISTS
//
// The shared sheet was originally built by majority vote across six pages. That is
// invalid here. Webflow page IDs are Mongo ObjectIds, and their embedded timestamps
// show in-home-aba-therapy was created 2026-03-23, while the other five were created
// between 08:40 and 12:42 on 2026-03-30 -- one page cloned five times in a morning.
//
// So the "majority of five" is one decision copy-pasted five times and then frozen,
// while in-home carried on being refined. Majority rule counts the stale snapshot
// five times and the maintained original once, and therefore systematically discards
// in-home's later work: font-weight 800 across six selectors, defensive !important
// rules hardening against the Webflow host stylesheet, and deliberate image ratios.
//
// The cost was concrete. in-home had `.area-card { color: inherit !important }` -- the
// fix for browser-default link blue on the navy section. The five clones did not.
// Majority rule deleted the fix from the reference page instead of propagating it,
// taking the defect from 5-of-6 pages to 6-of-6.
//
// THE RULE
//
//   in-home wins wherever it has an opinion.
//   Majority-of-five applies only to selectors in-home does not have at all --
//   sections that exist only on the clone pages, where the drift is genuine.
//
// The reference is in-home-aba-therapy.merged.css, the correctly-cascaded merge of
// in-home's two stylesheet copies (they are not identical; the later embed wins).
//
// usage: node rebase-shared.mjs [--apply]
'use strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = dirname(fileURLToPath(import.meta.url));
const APPLY = process.argv.includes('--apply');

// --- shared parsing helpers (same semantics as collision-check.mjs) ---------

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

// Split a declaration block into {prop: value}, respecting parens and strings so
// that rgba(0,0,0,.06) and var(--x) survive intact.
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

const fmtDecls = m => [...m].map(([k, v]) => `${k}: ${v};`).join(' ');

// Walk a sheet, tracking at-rule nesting. Returns rules with source offsets so the
// original file can be rewritten in place rather than regenerated.
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
      const bodyStart = i + 1;
      let depth = 1, q2 = null, end = -1;
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
        selectors: prelude.split(',').map(normSelector).filter(Boolean),
        prelude,
        body: src.slice(bodyStart, end),
        bodyStart, bodyEnd: end,
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

// --- build the reference index --------------------------------------------

const refCss = readFileSync(join(DIR, 'in-home-aba-therapy.merged.css'), 'utf8');
const sharedPath = join(DIR, 'service-pages.shared.css');
const sharedCss = readFileSync(sharedPath, 'utf8');

const ref = new Map();  // "context||selector" -> Map(prop -> value)
for (const r of parseRules(refCss)) {
  for (const sel of r.selectors) {
    const key = `${r.context}||${sel}`;
    const decls = parseDecls(r.body);
    if (ref.has(key)) for (const [k, v] of decls) ref.get(key).set(k, v); // later wins
    else ref.set(key, new Map(decls));
  }
}

// --- rewrite the shared sheet ---------------------------------------------

const sharedRules = parseRules(sharedCss);
const edits = [];
const report = { changed: [], added: [], dropped: [], untouched: 0, noRef: 0 };

for (const rule of sharedRules) {
  // only rebase rules whose every selector the reference also declares
  const keys = rule.selectors.map(s => `${rule.context}||${s}`);
  if (!keys.every(k => ref.has(k))) { report.noRef++; continue; }

  const have = parseDecls(rule.body);
  // merge the reference blocks for each selector in the group
  const want = new Map();
  for (const k of keys) for (const [p, v] of ref.get(k)) want.set(p, v);

  const label = `${rule.context || '<base>'} :: ${rule.prelude}`;
  let dirty = false;
  const next = new Map();

  for (const [p, v] of want) {
    if (!have.has(p)) { report.added.push(`${label} { ${p}: ${v} }`); dirty = true; }
    else if (have.get(p) !== v) { report.changed.push(`${label} { ${p} }  ${have.get(p)}  ->  ${v}`); dirty = true; }
    next.set(p, v);
  }
  for (const [p, v] of have) {
    if (!want.has(p)) { report.dropped.push(`${label} { ${p}: ${v} }`); dirty = true; }
  }

  if (dirty) edits.push({ start: rule.bodyStart, end: rule.bodyEnd, text: ' ' + fmtDecls(next) + ' ' });
  else report.untouched++;
}

console.log(`reference rules : ${ref.size}`);
console.log(`shared rules    : ${sharedRules.length}  (${report.noRef} have no in-home counterpart -> left to majority-of-five)\n`);
console.log(`CHANGED (${report.changed.length}) -- majority value replaced by in-home's:`);
report.changed.forEach(x => console.log('   ' + x));
console.log(`\nADDED (${report.added.length}) -- in-home declares, shared sheet had dropped:`);
report.added.forEach(x => console.log('   ' + x));
console.log(`\nDROPPED (${report.dropped.length}) -- shared sheet had, in-home does not declare:`);
report.dropped.forEach(x => console.log('   ' + x));
console.log(`\nunchanged rules: ${report.untouched}`);

if (!APPLY) { console.log('\n(dry run -- pass --apply to write)'); process.exit(0); }

let out = sharedCss;
for (const e of edits.sort((a, b) => b.start - a.start)) {
  out = out.slice(0, e.start) + e.text + out.slice(e.end);
}
writeFileSync(sharedPath, out);
console.log(`\nwritten: ${sharedPath} (${out.length} B)`);
