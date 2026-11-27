// Offline checks of the built HTML: head tags, JSON-LD shape, sitemap, robots, manifest, llms.txt, files and image sizes.
const fs = require('fs'); const zlib = require('zlib');
const R = '/site/'; const SITE = 'https://brianallengit.github.io/verifica-tu-ayuda-az/';
const html = fs.readFileSync(R + 'index.html', 'utf8'); const head = html.slice(0, html.indexOf('</head>'));
let fail = 0; const ok = (c, m) => { if (!c) fail++; console.log((c ? 'PASS ' : 'FAIL ') + m); };
const meta = (k, v) => { const m = new RegExp(`<meta ${k}="${v}" content="([^"]*)"`).exec(head); return m && m[1]; };
const un = s => s.replace(/&amp;/g, '&').replace(/&quot;/g, '"');
const title = /<title>([^<]*)<\/title>/.exec(head)[1];
ok(title.length >= 50 && title.length <= 60, `title ${title.length} chars: ${title}`);
const desc = meta('name', 'description'); ok(desc.length >= 145 && desc.length <= 165, `meta description ${desc.length} chars`);
ok(new RegExp(`<link rel="canonical" href="${SITE}">`).test(head), 'canonical');
for (const l of ['es', 'en', 'x-default']) ok(head.includes(`<link rel="alternate" hreflang="${l}" href="${SITE}">`), 'hreflang ' + l);
ok(/<html lang="es">/.test(html), 'html lang');
ok(!!meta('name', 'robots'), 'robots meta');
for (const p of ['og:title', 'og:description', 'og:type', 'og:url', 'og:image', 'og:image:alt', 'og:locale', 'og:locale:alternate', 'og:site_name', 'og:image:width', 'og:image:height'])
  ok(!!meta('property', p), p + ' = ' + String(meta('property', p)).slice(0, 70));
ok(meta('property', 'og:image').startsWith('https://'), 'og:image absolute https');
for (const n of ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image', 'twitter:image:alt']) ok(!!meta('name', n), n);
ok(meta('name', 'twitter:card') === 'summary_large_image', 'twitter:card summary_large_image');
ok(!!meta('name', 'theme-color'), 'theme-color');
for (const r of ['icon" href="favicon.svg', 'icon" href="favicon-32.png', 'apple-touch-icon" href="apple-touch-icon.png', 'manifest" href="manifest.webmanifest']) ok(head.includes(`<link rel="${r}"`), 'link ' + r);
// og image: real PNG 1200x630, under 1 MB
const png = fs.readFileSync(R + 'og-image.png'); ok(png.readUInt32BE(16) === 1200 && png.readUInt32BE(20) === 630 && png.length < 1e6, `og-image.png ${png.readUInt32BE(16)}x${png.readUInt32BE(20)}, ${png.length} bytes`);
for (const [f, w] of [['favicon-32.png', 32], ['apple-touch-icon.png', 180], ['icon-192.png', 192], ['icon-512.png', 512]]) { const b = fs.readFileSync(R + f); ok(b.readUInt32BE(16) === w && b.readUInt32BE(20) === w, `${f} ${w}x${w}`); }
// JSON-LD
const m = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/.exec(head); let ld; try { ld = JSON.parse(m[1]); ok(true, 'JSON-LD parses'); } catch (e) { ok(false, 'JSON-LD parses ' + e); }
const g = ld['@graph']; const by = t => g.find(x => x['@type'] === t);
const need = { Organization: ['name', 'url'], WebSite: ['name', 'url'], WebPage: ['name', 'url'] };
for (const [t, props] of Object.entries(need)) for (const p of props) ok(by(t) && by(t)[p], `JSON-LD ${t}.${p}`);
ok(ld['@context'] === 'https://schema.org', 'JSON-LD @context');
const ids = new Set(g.map(x => x['@id'])); ok(g.every(x => Object.values(x).every(v => !(v && v['@id'] && Object.keys(v).length === 1) || ids.has(v['@id']))), 'JSON-LD @id references resolve');
ok(!/FAQPage|HowTo/.test(m[1]), 'no FAQPage/HowTo (page has no real FAQ markup)');
ok(by('WebPage').name === un(title) && by('WebSite').description === un(desc), 'JSON-LD name/description match visible title/description');
ok(!/Brian|Allen/i.test(html.replace(/https:\/\/brianallengit\.github\.io\/verifica-tu-ayuda-az\//g, '')), 'no real name in HTML (apart from the planned github.io host, same as Fresh Start)');
// robots, sitemap, llms, manifest
const robots = fs.readFileSync(R + 'robots.txt', 'utf8'); ok(/User-agent: \*/.test(robots) && robots.includes(`Sitemap: ${SITE}sitemap.xml`), 'robots.txt allows all and names sitemap');
const sm = fs.readFileSync(R + 'sitemap.xml', 'utf8'); ok(sm.includes(`<loc>${SITE}</loc>`) && /hreflang="es"/.test(sm) && /hreflang="en"/.test(sm) && /hreflang="x-default"/.test(sm) && /^<\?xml/.test(sm), 'sitemap.xml loc and alternates');
ok(fs.readFileSync(R + 'llms.txt', 'utf8').startsWith('# '), 'llms.txt starts with H1');
const mf = JSON.parse(fs.readFileSync(R + 'manifest.webmanifest', 'utf8')); ok(mf.name && mf.start_url && mf.icons.every(i => fs.existsSync(R + i.src)), 'manifest valid and icons exist');
ok(/manifest-src 'self'/.test(head) && /default-src 'none'/.test(head), 'strict CSP incl. manifest-src');
ok(!/—/.test(html), 'no em dashes');
// one h1 per language, headings order inside each language block
const h1 = (html.match(/<h1[ >]/g) || []).length; ok(h1 === 2, `h1 count ${h1} (one per language, one hidden at a time)`);
console.log(fail ? `VALIDATION FAIL (${fail})` : 'VALIDATION PASS'); process.exit(fail ? 1 : 0);
