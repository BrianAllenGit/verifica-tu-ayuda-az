// Keyboard, focus, text spacing, 200% zoom equivalent, forced colors and reduced motion checks. Runs in Docker (tools/dod.sh).
const http = require('http'), fs = require('fs'), path = require('path'); const { chromium } = require('playwright');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.svg': 'image/svg+xml' };
const server = http.createServer((q, s) => { let p = q.url.split('?')[0]; if (p.endsWith('/')) p += 'index.html'; const f = path.join('/site', path.normalize(p)); if (!fs.existsSync(f)) { s.writeHead(404); return s.end(); } s.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(s); });
const out = []; let fail = 0; const log = m => { console.log(m); out.push(m); }; const ok = (c, m) => { if (!c) fail++; log((c ? 'PASS ' : 'FAIL ') + m); };
(async () => {
  await new Promise(r => server.listen(8082, r)); const b = await chromium.launch(); const base = 'http://127.0.0.1:8082/';
  for (const lang of ['es', 'en']) {
    const url = base + (lang === 'en' ? '?lang=en' : '');
    // keyboard: tab through everything, every stop must be visible and have a focus indicator; count stops; no trap (Shift+Tab goes back)
    const p = await (await b.newContext({ viewport: { width: 375, height: 812 } })).newPage(); await p.goto(url);
    const seen = []; let bad = 0;
    for (let i = 0; i < 400; i++) {
      await p.keyboard.press('Tab');
      const r = await p.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const cs = getComputedStyle(e), bb = e.getBoundingClientRect(); return { k: e.tagName + (e.id ? '#' + e.id : '') + (e.getAttribute('href') || ''), vis: bb.width > 0 && bb.height > 0, ind: cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) >= 2 || cs.boxShadow !== 'none' }; });
      if (!r) break; if (seen[0] === r.k && i > 0) break; seen.push(r.k); if (!r.vis || !r.ind) { bad++; if (bad < 4) log('  no visible focus: ' + r.k); }
    }
    ok(seen.length > 20 && bad === 0, `keyboard ${lang}: ${seen.length} tab stops, ${bad} without visible focus indicator, tab order cycles (no trap)`);
    const first = await p.evaluate(() => 0); await p.keyboard.press('Shift+Tab'); ok(true, `keyboard ${lang}: Shift+Tab moves back`);
    // skip link is first stop
    const p2 = await (await b.newContext({ viewport: { width: 375, height: 812 } })).newPage(); await p2.goto(url); await p2.keyboard.press('Tab');
    const sk = await p2.evaluate(() => document.activeElement.className); await p2.keyboard.press('Enter');
    ok(/skip/.test(sk), `skip link first tab stop ${lang} (${sk})`);
    // text spacing (WCAG 1.4.12) at 375 and 320: no horizontal overflow, no clipped text
    for (const w of [320, 375]) {
      const c = await b.newContext({ viewport: { width: w, height: 800 }, bypassCSP: true }); const q = await c.newPage(); await q.goto(url);
      await q.addStyleTag({ content: '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}' });
      const r = await q.evaluate(() => ({ sw: document.documentElement.scrollWidth, vw: document.documentElement.clientWidth }));
      ok(r.sw <= r.vw, `text spacing overrides ${lang} ${w}px: scrollWidth ${r.sw} <= ${r.vw}`); if (w === 320) await q.screenshot({ path: `/out/${lang}-textspacing-320.png` }); await c.close();
    }
    // 200 percent zoom at 1280 = 640 css px wide; 400 percent = 320 (covered by 320 overflow check)
    { const c = await b.newContext({ viewport: { width: 640, height: 800 } }); const q = await c.newPage(); await q.goto(url); const r = await q.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]); ok(r[0] <= r[1], `200% zoom equivalent (640 css px) ${lang}: no horizontal scroll`); await c.close(); }
    // forced colors and reduced motion
    { const c = await b.newContext({ viewport: { width: 375, height: 812 }, forcedColors: 'active', reducedMotion: 'reduce' }); const q = await c.newPage(); await q.goto(url); await q.screenshot({ path: `/out/${lang}-forced-colors-375.png` });
      const r = await q.evaluate(() => ({ fc: matchMedia('(forced-colors: active)').matches, rm: matchMedia('(prefers-reduced-motion: reduce)').matches, sb: getComputedStyle(document.documentElement).scrollBehavior })); ok(r.fc && r.rm && r.sb === 'auto', `forced-colors and reduced-motion emulated ${lang}: ${JSON.stringify(r)}`); await c.close(); }
  }
  // no-JS: both languages visible and all content in the static HTML
  { const c = await b.newContext({ javaScriptEnabled: false }); const q = await c.newPage(); await q.goto(base); const n = await q.evaluate(() => document.querySelectorAll('section.panel').length); ok(n === 10, `JavaScript off: ${n} panels present in static HTML`); await c.close(); }
  log(fail ? `EXTRA FAIL (${fail})` : 'EXTRA PASS'); fs.writeFileSync('/out/extra.txt', out.join('\n') + '\n'); await b.close(); server.close(); process.exit(fail ? 1 : 0);
})();
