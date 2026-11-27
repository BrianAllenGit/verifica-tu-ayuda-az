import { chromium } from 'playwright';
import fs from 'fs';
const url = process.argv[2]; const tag = process.argv[3];
const b = await chromium.launch();
const p = await b.newPage({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36', locale: 'en-US', viewport:{width:1280,height:900} });
const reqs = [];
p.on('request', r => { const u = r.url(); if (!/\.(png|jpg|svg|woff2?|css|gif)/.test(u)) reqs.push(u); });
await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
fs.writeFileSync(`/out/${tag}_page.txt`, await p.innerText('body'));
await p.waitForTimeout(4000);
const labels = await p.$$('a.accordion__item__label');
console.log('labels', labels.length);
let out = '';
for (let i = 0; i < labels.length; i++) {
  const t = (await labels[i].innerText()).trim();
  await labels[i].scrollIntoViewIfNeeded();
  await labels[i].click();
  await p.waitForTimeout(1200);
  const li = await labels[i].evaluateHandle(e => e.closest('li'));
  const html = await li.evaluate(e => e.innerHTML);
  const txt = await li.evaluate(e => e.innerText);
  out += `\n=====${i} ${t}\n${txt}\n`;
  fs.writeFileSync(`/out/${tag}_${i}.html`, html);
}
fs.writeFileSync(`/out/${tag}_scenarios.txt`, out);
fs.writeFileSync(`/out/${tag}_reqs.txt`, reqs.join('\n'));
await p.screenshot({path:`/out/${tag}_after.png`, fullPage:false});
console.log(out.length);
await b.close();
