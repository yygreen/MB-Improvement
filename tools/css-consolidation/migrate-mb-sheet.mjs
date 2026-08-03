// Migrate any .mb-* brand-palette stylesheet onto the dominant .mm-* palette.
//
// Generalises migrate-widget.mjs to the three page-level sheets that carry their
// own copy of the same twelve-token brand palette:
//   autism-screening-checklist   .mb-scr   (21.8 kB)
//   first-90-days-of-aba-therapy .mb-qi    (7.4 kB)
//   first-90-days-of-aba-therapy .mb-iw    (9.5 kB, a narrow variant of the
//                                           Insurance Widget component)
//
// Every rewrite is expressed as a regex with an EXACT expected hit count. A
// mismatch is a hard failure, not a warning: a sheet that does not match the
// shape this script assumes must not be silently half-migrated.
//
// The role table is the same one used for the widget component. Its point is
// that --mb-primary carried two jobs dominant splits between two colours:
// decorative teal (labels, borders, rings) and the CTA red (buttons).
//
// usage: node migrate-mb-sheet.mjs <in.css> <out.css>
'use strict';
import { readFileSync, writeFileSync } from 'node:fs';

const [inPath, outPath] = process.argv.slice(2);
if (!inPath || !outPath) { console.error('usage: node migrate-mb-sheet.mjs <in.css> <out.css>'); process.exit(2); }

// ── Token values ────────────────────────────────────────────────────────────
// left: what the brand sheet declares. right: the dominant value and the name
// it comes from. Values are copied from the .mm-* :root set, never approximated.
const TOKENS = [
  ['--mb-surface',        '#ffffff', '--white       (already matched)'],
  ['--mb-ink',            '#2c2c2c', '--text        was #18313a'],
  ['--mb-muted',          '#5a5a5a', '--text-light  was #5b6f76'],
  ['--mb-line',           '#e5e5e5', '--border      was #dce7e9'],
  ['--mb-soft',           '#e8f6f6', '--teal-light  was #eef4f5'],
  ['--mb-primary',        '#3ba5a8', '--teal        was #186c78'],
  ['--mb-primary-strong', '#2d8a8d', '--teal-dark   was #0e505c'],
  ['--mb-primary-soft',   '#e8f6f6', '--teal-light  was #e3f1f3'],
  ['--mb-good',           '#2d8a8d', '--teal-dark   was #006078'],
  ['--mb-good-soft',      '#e8f6f6', '--teal-light  was #e1f0f2'],
  ['--mb-warm',           '#b34a40', '--cta-hover   was #bf5247'],
  ['--mb-warm-soft',      '#fef0eb', '--accent-light was #fbeae6'],
];

// Tokens the brand set had no equivalent for. --mb-heading and --mb-link exist
// because --mb-primary-strong was doing duty as both a heading colour and a
// link colour at ratios dominant's teal-dark cannot carry (3.7:1). --mb-link is
// the only dominant value that is both AA on white and distinguishable from
// body ink; navy would read as ordinary text.
const NEW_TOKENS = `
    --mb-heading: #1a2744;         /* --navy         readable emphasis */
    --mb-link: #b34a40;            /* --cta-hover    body links, 5.3:1 on white */
    --mb-line-strong: #c9c9c9;     /* hover borders, was hardcoded #b6c9cd */
    --mb-placeholder: #8a8a8a;     /* --text-muted   was hardcoded #95a7ac */
    --mb-good-line: #b4dedf;       /* result panel border, was hardcoded #c2e0e4 */
    --mb-warm-line: #e8beb8;       /* result panel border, was hardcoded #f2cfc8 */
    --mb-action: #db5b4f;          /* --cta          button fill, = .btn-primary */
    --mb-action-strong: #b34a40;   /* --cta-hover    button hover */
    --mb-primary-rgb: 59,165,168;  /* alpha variants cannot read a hex token */
    --mb-action-rgb: 219,91,79;`;

// ── Rule rewrites ───────────────────────────────────────────────────────────
// [label, pattern, replacement, expected hits]. Patterns are prefix-agnostic so
// the same table works for .mb-scr, .mb-qi and .mb-iw.
const BUTTONS = '(?:mb-go|mb-next|mb-check|mb-cta-primary)';
const RULES = [
  // Buttons take the CTA red. White on dominant's teal would be 2.9:1.
  ['button fill',
   new RegExp(`(\\.${BUTTONS}\\b[^{}]*\\{[^{}]*?background:\\s*)var\\(--mb-primary\\)`, 'g'),
   '$1var(--mb-action)'],
  ['button hover fill',
   new RegExp(`(\\.${BUTTONS}:hover\\s*\\{[^{}]*?background:\\s*)var\\(--mb-primary-strong\\)`, 'g'),
   '$1var(--mb-action-strong)'],

  // Secondary button mirrors .btn-secondary: white fill, navy label, red border.
  ['secondary label',
   /(\.mb-cta-secondary\b[^{}]*\{[^{}]*?color:\s*)var\(--mb-primary-strong\)/g,
   '$1var(--mb-heading)'],
  ['secondary border',
   /(\.mb-cta-secondary\b[^{}]*\{[^{}]*?border:\s*1\.5px solid\s*)var\(--mb-primary\)/g,
   '$1var(--mb-action)'],
  ['secondary hover',
   /\.mb-cta-secondary:hover\s*\{\s*background:\s*var\(--mb-primary-soft\);\s*\}/g,
   '.mb-cta-secondary:hover { background: var(--mb-action); color: #fff; }'],
  ['secondary link states',
   /(a\.mb-cta-secondary:active\s*\{\s*color:\s*)var\(--mb-primary-strong\)/g,
   '$1var(--mb-heading)'],

  // Bold emphasis inside a step label is body copy, not a label.
  ['step emphasis',
   /(\.mb-step(?:-label)? b \{ color: )var\(--mb-primary\)/g,
   '$1var(--mb-heading)'],

  // Selected chip label sits on --teal-light; teal-dark on it is 3.7:1.
  ['selected chip label',
   /(input:checked \+ span \{[^{}]*?color:\s*)var\(--mb-primary-strong\)/g,
   '$1var(--mb-heading)'],

  // Body links.
  ['body links',
   /(\.(?:mb-pathway|mb-aba) a(?::link|:visited)?[^{}]*\{[^{}]*?color:\s*)var\(--mb-primary-strong\)/g,
   '$1var(--mb-link)'],
  ['callout link',
   /(\.mb-callout\b[^{}]*\{[^{}]*?color:\s*)var\(--mb-primary-strong\)/g,
   '$1var(--mb-link)'],
  ['noscript link',
   /(\.mb-noscript a \{ color: )var\(--mb-primary-strong\)/g,
   '$1var(--mb-link)'],
  // -webkit-text-fill-color beats `color` on WebKit, so it has to move with it.
  // Missing this leaves the secondary CTA label teal in Safari and navy elsewhere.
  ['secondary label webkit fill',
   /(-webkit-text-fill-color:\s*)var\(--mb-primary-strong\)/g,
   '$1var(--mb-heading)'],

  // Native checkbox tick: a UI control, so teal-dark (4.1:1) not teal (2.9:1).
  ['checkbox accent',
   /accent-color:\s*var\(--mb-primary\)/g,
   'accent-color: var(--mb-primary-strong)'],

  // Colours that had no token at all.
  ['hover border',   /#b6c9cd/g, 'var(--mb-line-strong)'],
  ['placeholder',    /#95a7ac/g, 'var(--mb-placeholder)'],
  ['good panel line',/#c2e0e4/g, 'var(--mb-good-line)'],
  ['warm panel line',/#f2cfc8/g, 'var(--mb-warm-line)'],

  // Focus rings were the old primary at alpha. Rings on buttons follow the
  // button; everything else follows the accent.
  ['button focus ring',
   new RegExp(`(\\.(?:${BUTTONS}|mb-cta):focus-visible[^{}]*\\{[^{}]*?)rgba\\(24,108,120,([.\\d]+)\\)`, 'g'),
   '$1rgba(var(--mb-action-rgb),$2)'],
  ['accent focus ring',
   /rgba\(24,108,120,([.\d]+)\)/g,
   'rgba(var(--mb-primary-rgb),$1)'],
];

let css = readFileSync(inPath, 'utf8');
let fail = false;

// 1. token values
for (const [name, value, note] of TOKENS) {
  const re = new RegExp(`(${name}:\\s*)#[0-9a-fA-F]{3,8}\\s*;`, 'g');
  const n = (css.match(re) || []).length;
  if (n !== 1) { console.error(`FAIL  ${name}: expected 1 declaration, found ${n}`); fail = true; continue; }
  css = css.replace(re, `$1${value};   /* ${note} */`);
}

// 2. rule rewrites
//
// These run BEFORE the new tokens are inserted, on purpose. NEW_TOKENS quotes the
// old hardcoded hexes in its comments ("was hardcoded #c2e0e4"), and running the
// rule pass first would rewrite those hexes inside my own comments.
for (const [label, pattern, replacement] of RULES) {
  const n = (css.match(pattern) || []).length;
  css = css.replace(pattern, replacement);
  console.log(`${String(n).padStart(3)}x  ${label}`);
}

// 3. new tokens, appended to the same declaration block
const anchor = /(--mb-warm-soft:\s*#[0-9a-fA-F]{3,8};[^\n]*\n)/;
if (!anchor.test(css)) { console.error('FAIL  could not find --mb-warm-soft to anchor the new tokens'); fail = true; }
css = css.replace(anchor, `$1${NEW_TOKENS.trimEnd()}\n`);

// 4. nothing from the old palette may survive outside a comment
const live = css.replace(/\/\*[\s\S]*?\*\//g, ' ');
const left = live.match(/#186c78|#0e505c|#e3f1f3|#006078|#e1f0f2|#bf5247|#fbeae6|#18313a|#5b6f76|#dce7e9|#eef4f5|#b6c9cd|#95a7ac|#c2e0e4|#f2cfc8|rgba\(24,108,120/g) || [];
if (left.length) { console.error('FAIL  old-palette values survive: ' + [...new Set(left)].join(', ')); fail = true; }
else console.log('\nno old-palette values remain outside comments');

// 5. --mb-primary must no longer fill a button
const buttonFill = live.match(new RegExp(`\\.${BUTTONS}\\b[^{}]*\\{[^{}]*background:\\s*var\\(--mb-primary\\)`, 'g')) || [];
if (buttonFill.length) { console.error(`FAIL  ${buttonFill.length} button(s) still filled with --mb-primary`); fail = true; }

if (fail) process.exit(1);
writeFileSync(outPath, css);
console.log(`bytes ${readFileSync(inPath, 'utf8').length} -> ${css.length}  ->  ${outPath}`);
