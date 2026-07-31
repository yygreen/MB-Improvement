import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const snap = async (file, w) => {
  const pg = await b.newPage({ viewport: { width: w, height: 1000 } });
  await pg.route(/^https?:/, r => r.abort()); await pg.goto('file:///tmp/wf/std/' + file, { waitUntil: 'domcontentloaded' });
  await pg.waitForTimeout(600);
  const r = await pg.evaluate(() => {
    const out = [];
    document.querySelectorAll('.mm-embed *').forEach((n, i) => {
      const b = n.getBoundingClientRect();
      const c = getComputedStyle(n);
      out.push([i, n.tagName, (n.className||'').toString().slice(0,20),
        Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height),
        c.fontSize, c.fontWeight, c.color, c.backgroundColor, c.display].join('|'));
    });
    return { rows: out, docHeight: document.body.scrollHeight };
  });
  await pg.close(); return r;
};
for (const w of [1440, 768, 390]) {
  const a = await snap('cmp_base.html', w), c = await snap('cmp_after.html', w);
  let diffs = 0, first = [];
  const n = Math.max(a.rows.length, c.rows.length);
  for (let i = 0; i < n; i++) if (a.rows[i] !== c.rows[i]) { diffs++; if (first.length < 4) first.push({ base: a.rows[i], after: c.rows[i] }); }
  console.log(`viewport ${w}: elements ${a.rows.length} vs ${c.rows.length} | docHeight ${a.docHeight} vs ${c.docHeight} | differing ${diffs}`);
  first.forEach(f => { console.log('   base :', f.base); console.log('   after:', f.after); });
}
await b.close();
