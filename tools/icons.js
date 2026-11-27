// Renders PNG icons from favicon.svg. Runs inside the Playwright image (see tools/dod.sh).
const { chromium } = require('playwright'); const fs = require('fs');
const svg = fs.readFileSync('/site/favicon.svg', 'utf8');
(async () => {
  const b = await chromium.launch();
  for (const [n, px, pad] of [['favicon-32.png', 32, 0], ['apple-touch-icon.png', 180, 0], ['icon-192.png', 192, 0], ['icon-512.png', 512, 0]]) {
    const p = await b.newPage({ viewport: { width: px, height: px } });
    await p.setContent(`<html><body style="margin:0;background:#115e59">${svg.replace('<svg ', `<svg width="${px}" height="${px}" style="display:block" `)}</body></html>`);
    await p.screenshot({ path: '/out/' + n }); await p.close();
  }
  await b.close();
})();
