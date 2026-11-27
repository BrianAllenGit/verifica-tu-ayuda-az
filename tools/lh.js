const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const SITE = '/site';
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.svg': 'image/svg+xml', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml', '.webmanifest': 'application/manifest+json' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  const f = path.join(SITE, path.normalize(p));
  if (!f.startsWith(SITE) || !fs.existsSync(f)) { res.writeHead(404); return res.end('nf'); }
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});
(async () => {
  const lighthouse = (await import('lighthouse')).default;
  const chromeLauncher = await import('chrome-launcher');
  await new Promise(r => server.listen(8081, r));
  const chrome = await chromeLauncher.launch({ chromePath: chromium.executablePath(), chromeFlags: ['--headless=new', '--no-sandbox'] });
  const out = [];
  for (const [name, url] of [['es', 'http://localhost:8081/'], ['en', 'http://localhost:8081/?lang=en']]) {
    const r = await lighthouse(url, { port: chrome.port, output: 'json', logLevel: 'error', formFactor: 'mobile', onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] });
    const c = r.lhr.categories; const line = `lighthouse mobile ${name}: performance ${Math.round(c.performance.score * 100)}, accessibility ${Math.round(c.accessibility.score * 100)}, best-practices ${Math.round(c['best-practices'].score * 100)}, seo ${Math.round(c.seo.score * 100)}`;
    console.log(line); out.push(line);
    for (const [id, a] of Object.entries(r.lhr.audits)) if (a.score !== null && a.score < 1 && a.scoreDisplayMode !== 'informative' && a.scoreDisplayMode !== 'notApplicable') { const l = `  not 100: ${id} (${a.score}) ${a.displayValue || ''}`; console.log(l); out.push(l); }
    fs.writeFileSync(`/out/lighthouse-${name}.json`, JSON.stringify({ categories: Object.fromEntries(Object.entries(c).map(([k, v]) => [k, v.score])), fcp: r.lhr.audits['first-contentful-paint'].displayValue, lcp: r.lhr.audits['largest-contentful-paint'].displayValue, tbt: r.lhr.audits['total-blocking-time'].displayValue, cls: r.lhr.audits['cumulative-layout-shift'].displayValue }, null, 1));
  }
  fs.writeFileSync('/out/lighthouse.txt', out.join('\n') + '\n');
  await chrome.kill(); server.close();
})();
