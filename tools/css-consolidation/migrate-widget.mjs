// Transform the live .mb-iw widget sheet onto the dominant palette.
// Every substitution is a literal, anchored string swap so anything the map does
// not name is guaranteed byte-identical -- the diff is provably colour-only.
import { readFileSync, writeFileSync } from 'node:fs';

const src = readFileSync('/tmp/wf/w/widget.css', 'utf8');

const TOKEN_BLOCK_OLD = `    --mb-bg: transparent;          /* widget sits on the page background */
    --mb-surface: #ffffff;         /* card */
    --mb-ink: #18313a;             /* primary text (deep teal-charcoal) */
    --mb-muted: #5b6f76;           /* secondary text (teal-grey) */
    --mb-line: #dce7e9;            /* hairline borders (teal-tinted) */
    --mb-soft: #eef4f5;            /* subtle fills */

    --mb-primary: #186c78;         /* Mastermind brand teal: CTAs + accents */
    --mb-primary-strong: #0e505c;  /* hover / active */
    --mb-primary-soft: #e3f1f3;    /* selected chip fill */

    --mb-good: #006078;            /* accepted accent (deepest brand teal) */
    --mb-good-soft: #e1f0f2;       /* accepted panel fill */
    --mb-warm: #bf5247;            /* brand coral: "let's check" accent */
    --mb-warm-soft: #fbeae6;       /* "let's check" panel fill */`;

const TOKEN_BLOCK_NEW = `    /* Palette migrated to the site-dominant .mm-* set. The dominant name each
       value comes from is in the comment; values are copied, never approximated.
       Two roles the old sheet folded into --mb-primary are split out, because
       dominant uses teal and red for different jobs:
         --mb-primary*  decorative teal  (eyebrows, chip borders, focus rings)
         --mb-action*   the CTA red      (buttons -- matches .btn-primary)
       Three colours that were hardcoded hexes are now tokens so a future
       rebrand cannot miss them. */
    --mb-bg: transparent;          /* widget sits on the page background */
    --mb-surface: #ffffff;         /* --white       (already matched) */
    --mb-ink: #2c2c2c;             /* --text        was #18313a */
    --mb-heading: #1a2744;         /* --navy        NEW: readable emphasis */
    --mb-muted: #5a5a5a;           /* --text-light  was #5b6f76 */
    --mb-line: #e5e5e5;            /* --border      was #dce7e9 */
    --mb-line-strong: #c9c9c9;     /* NEW: hover borders, was hardcoded #b6c9cd */
    --mb-placeholder: #8a8a8a;     /* --text-muted  was hardcoded #95a7ac */
    --mb-soft: #e8f6f6;            /* --teal-light  was #eef4f5 */

    --mb-primary: #3ba5a8;         /* --teal        was #186c78 */
    --mb-primary-strong: #2d8a8d;  /* --teal-dark   was #0e505c */
    --mb-primary-soft: #e8f6f6;    /* --teal-light  was #e3f1f3 */
    --mb-primary-rgb: 59,165,168;  /* alpha variants cannot read a hex token */

    --mb-action: #db5b4f;          /* --cta         NEW: button fill */
    --mb-action-strong: #b34a40;   /* --cta-hover   NEW: button hover */
    --mb-action-rgb: 219,91,79;

    --mb-good: #2d8a8d;            /* --teal-dark   was #006078 */
    --mb-good-soft: #e8f6f6;       /* --teal-light  was #e1f0f2 */
    --mb-good-line: #b4dedf;       /* NEW: was hardcoded #c2e0e4 */
    --mb-warm: #b34a40;            /* --cta-hover   was #bf5247; kept dark
                                      because .mb-hint renders it as body text
                                      (--accent #e8734a would be 3.0:1 on white) */
    --mb-warm-soft: #fef0eb;       /* --accent-light was #fbeae6 */
    --mb-warm-line: #e8beb8;       /* NEW: was hardcoded #f2cfc8 */`;

const SUBS = [
  [TOKEN_BLOCK_OLD, TOKEN_BLOCK_NEW],

  // Bold inline emphasis in body copy: teal at 2.9:1 is a label colour, not a
  // text colour. Navy is what dominant uses for emphasis.
  ['.mb-step b { color: var(--mb-primary); font-weight: 700; }',
   '.mb-step b { color: var(--mb-heading); font-weight: 700; }'],

  // Hover borders and placeholder: tokenised, no longer teal-tinted greys.
  ['.mb-chip:hover span { border-color: #b6c9cd; }',
   '.mb-chip:hover span { border-color: var(--mb-line-strong); }'],
  ['.mb-select:hover { border-color: #b6c9cd; }',
   '.mb-select:hover { border-color: var(--mb-line-strong); }'],
  ['.mb-input::placeholder { color: #95a7ac; }',
   '.mb-input::placeholder { color: var(--mb-placeholder); }'],
  ['.mb-input:hover { border-color: #b6c9cd; }',
   '.mb-input:hover { border-color: var(--mb-line-strong); }'],

  // Selected chip label sits on --teal-light; teal-dark on it is 3.7:1, navy 13.4:1.
  ['    color: var(--mb-primary-strong);\n    box-shadow: inset 0 0 0 1px var(--mb-primary);',
   '    color: var(--mb-heading);\n    box-shadow: inset 0 0 0 1px var(--mb-primary);'],

  // Focus rings were the old primary at alpha; follow whatever they now ring.
  ['outline: 3px solid rgba(24,108,120,.35);', 'outline: 3px solid rgba(var(--mb-primary-rgb),.35);'],
  ['box-shadow: 0 0 0 3px rgba(24,108,120,.25);', 'box-shadow: 0 0 0 3px rgba(var(--mb-primary-rgb),.25);'],

  // Primary action button -> the site's .btn-primary red.
  ['    color: #fff; background: var(--mb-primary);',
   '    color: #fff; background: var(--mb-action);'],
  ['.mb-check:hover { background: var(--mb-primary-strong); }',
   '.mb-check:hover { background: var(--mb-action-strong); }'],
  ['  .mb-check:focus-visible {\n    outline: 3px solid rgba(24,108,120,.4);',
   '  .mb-check:focus-visible {\n    outline: 3px solid rgba(var(--mb-action-rgb),.4);'],

  ['.mb-noscript a { color: var(--mb-primary-strong); font-weight: 700; }',
   '.mb-noscript a { color: var(--mb-heading); font-weight: 700; }'],

  ['.mb-panel.is-good { background: var(--mb-good-soft); border-color: #c2e0e4; }',
   '.mb-panel.is-good { background: var(--mb-good-soft); border-color: var(--mb-good-line); }'],
  ['.mb-panel.is-warm { background: var(--mb-warm-soft); border-color: #f2cfc8; }',
   '.mb-panel.is-warm { background: var(--mb-warm-soft); border-color: var(--mb-warm-line); }'],

  // Result CTAs mirror .btn-primary / .btn-secondary exactly.
  ['.mb-cta-primary { background: var(--mb-primary); color: #fff; }',
   '.mb-cta-primary { background: var(--mb-action); color: #fff; }'],
  ['.mb-cta-primary:hover { background: var(--mb-primary-strong); }',
   '.mb-cta-primary:hover { background: var(--mb-action-strong); }'],
  ['    background: var(--mb-surface); color: var(--mb-primary-strong);\n    border: 1.5px solid var(--mb-primary);',
   '    background: var(--mb-surface); color: var(--mb-heading);\n    border: 1.5px solid var(--mb-action);'],
  ['.mb-cta-secondary:hover { background: var(--mb-primary-soft); }',
   '.mb-cta-secondary:hover { background: var(--mb-action); color: #fff; }'],
  ['.mb-cta:focus-visible { outline: 3px solid rgba(24,108,120,.4); outline-offset: 2px; }',
   '.mb-cta:focus-visible { outline: 3px solid rgba(var(--mb-action-rgb),.4); outline-offset: 2px; }'],
  ['.mb-restart:focus-visible { outline: 3px solid rgba(24,108,120,.4); outline-offset: 2px; border-radius: 6px; }',
   '.mb-restart:focus-visible { outline: 3px solid rgba(var(--mb-primary-rgb),.4); outline-offset: 2px; border-radius: 6px; }'],
];

let out = src, applied = 0;
for (const [from, to] of SUBS) {
  const n = out.split(from).length - 1;
  if (n === 0) { console.error('MISS  ' + from.slice(0, 70).replace(/\n/g, '\\n')); continue; }
  out = out.split(from).join(to);
  applied += n;
  console.log(`ok  x${n}  ${from.slice(0, 66).replace(/\n/g, '\\n')}`);
}
console.log(`\napplied ${applied} substitution(s) across ${SUBS.length} rules`);

const leftovers = (out.match(/#186c78|#0e505c|#e3f1f3|#006078|#e1f0f2|#bf5247|#fbeae6|#18313a|#5b6f76|#dce7e9|#eef4f5|#b6c9cd|#95a7ac|#c2e0e4|#f2cfc8|rgba\(24,108,120/g) || []);
console.log(leftovers.length ? 'LEFTOVER old-palette colours: ' + [...new Set(leftovers)].join(', ')
                             : 'no old-palette colours remain');
writeFileSync('/tmp/wf/w/widget.dominant.css', out);
console.log(`bytes ${src.length} -> ${out.length}`);
