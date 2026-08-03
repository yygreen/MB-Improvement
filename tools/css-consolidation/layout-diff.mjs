// Headless-Chromium layout verification for the service-page CSS consolidation.
//
// Compares a baseline render against an after render and reports only meaningful
// differences.
//
// Geometry is compared PARENT-RELATIVE, not absolute. The earlier version used
// absolute x/y and reported "271/271 elements changed" for a single padding change
// near the top of a page -- every element below it shifted, drowning the signal.
// Offsets are measured against the element's own parent, so a change is attributed
// to the element that actually changed.
//
// Rows are also keyed by structural path rather than by index, so an inserted or
// removed node does not shift every subsequent row and read as a whole-page change.
//
// usage: node layout-diff.mjs <base.html> <after.html> [label]
import { chromium } from 'playwright';

const [baseFile, afterFile, label = ''] = process.argv.slice(2);
if (!baseFile || !afterFile) {
  console.error('usage: node layout-diff.mjs <base.html> <after.html> [label]');
  process.exit(2);
}

const VIEWPORTS = [1440, 768, 390];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

const snap = async (file, width) => {
  const page = await browser.newPage({ viewport: { width, height: 1000 } });
  // Block the network: we are measuring inline CSS, and remote fonts/images add
  // timing noise that surfaces as spurious geometry differences.
  await page.route(/^https?:/, r => r.abort());
  await page.goto('file://' + file, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(600);
  const result = await page.evaluate(() => {
    const rows = [];
    document.querySelectorAll('.mm-embed, .mm-embed *').forEach((n, i) => {
      const b = n.getBoundingClientRect();
      const p = n.parentElement ? n.parentElement.getBoundingClientRect() : { x: 0, y: 0 };
      const c = getComputedStyle(n);
      // Structural address, rooted at the embed and NOT at <body>.
      //
      // Two mistakes are baked out here. A global index makes one inserted node shift
      // every later key, so the whole page reads as changed. And walking the path up
      // to <body> makes the key sensitive to anything outside the embed -- prepending
      // the Service Page Styles component shifts an ancestor's ordinal and, again,
      // every descendant key changes. Each segment carries the element's ordinal among
      // its like-tagged siblings; the walk stops at the .mm-embed root, which is itself
      // identified by its position among the page's embeds.
      const seg = e => {
        const tag = e.tagName;
        const cls = (e.className || '').toString().trim().split(/\s+/)[0] || '';
        const sibs = e.parentElement ? [...e.parentElement.children].filter(x => x.tagName === tag) : [e];
        return `${tag}.${cls}[${sibs.indexOf(e)}]`;
      };
      const roots = [...document.querySelectorAll('.mm-embed')];
      const path = [];
      let e = n;
      for (; e && !e.classList.contains('mm-embed'); e = e.parentElement) path.push(seg(e));
      rows.push({
        key: `mm[${roots.indexOf(e)}]>` + path.reverse().join('>'),
        tag: n.tagName,
        cls: (n.className || '').toString().slice(0, 40),
        dx: Math.round(b.x - p.x),   // parent-relative
        dy: Math.round(b.y - p.y),
        w: Math.round(b.width),
        h: Math.round(b.height),
        cols: c.gridTemplateColumns,
        font: `${c.fontSize}/${c.fontWeight}`,
        color: c.color,
        bg: c.backgroundColor,
        display: c.display,
      });
    });
    return { rows, docHeight: document.body.scrollHeight };
  });
  await page.close();
  return result;
};

const FIELDS = ['dx', 'dy', 'w', 'h', 'cols', 'font', 'color', 'bg', 'display'];
let totalChanged = 0;

for (const width of VIEWPORTS) {
  const a = await snap(baseFile, width);
  const b = await snap(afterFile, width);
  const byKey = new Map(a.rows.map(r => [r.key, r]));
  const changes = [];

  for (const after of b.rows) {
    const before = byKey.get(after.key);
    if (!before) { changes.push({ after, diffs: ['<new element>'] }); continue; }
    const diffs = FIELDS
      .filter(f => String(before[f]) !== String(after[f]))
      .map(f => `${f}: ${before[f]} -> ${after[f]}`);
    if (diffs.length) changes.push({ after, diffs });
  }
  const afterKeys = new Set(b.rows.map(r => r.key));
  const missing = a.rows.filter(r => !afterKeys.has(r.key));

  totalChanged += changes.length + missing.length;
  console.log(`\n── ${label} @ ${width}px ──`);
  console.log(`   elements ${a.rows.length} -> ${b.rows.length} | docHeight ${a.docHeight} -> ${b.docHeight}`);
  console.log(`   changed ${changes.length}, removed ${missing.length}`);
  for (const c of changes.slice(0, 25)) {
    console.log(`   ${c.after.tag}.${c.after.cls}`);
    c.diffs.forEach(d => console.log(`      ${d}`));
  }
  if (changes.length > 25) console.log(`   … ${changes.length - 25} more`);
  for (const m of missing.slice(0, 10)) console.log(`   REMOVED ${m.tag}.${m.cls}`);
}

await browser.close();
console.log(`\ntotal differing elements across viewports: ${totalChanged}`);
