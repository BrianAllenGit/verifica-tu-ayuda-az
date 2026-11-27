import { chromium } from 'playwright';
import fs from 'fs';
const [,, url, name] = process.argv;
const b = await chromium.launch();
const p = await b.newPage({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36', locale: 'en-US', viewport:{width:1280,height:900} });
await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.waitForTimeout(5000);
const sel = '[aria-expanded="false"], summary, .cursor-pointer, button.accordion, .accordion-header, [role=tab]';
const els = await p.$$(sel);
console.log('toggles', els.length);
for (const e of els) { try { await e.click({timeout:1500}); await p.waitForTimeout(250);} catch(e){} }
await p.waitForTimeout(1500);
fs.writeFileSync(`/out/${name}_expanded.txt`, await p.innerText('body'));
fs.writeFileSync(`/out/${name}_expanded.html`, await p.content());
await p.screenshot({path:`/out/${name}.png`, fullPage:false});
console.log((await p.innerText('body')).length);
await b.close();
