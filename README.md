# Verifica tu ayuda · Arizona

"Is this person really allowed to help me with my immigration case?" A free, ad-free, zero-tracking, Spanish-first page (Spanish and English) for immigrants and families in Arizona who were offered help with immigration papers (for example by a "notario") and want to check the person before paying or signing.

Status: private draft. Not published. Planned address once shipped: https://brianallengit.github.io/verifica-tu-ayuda-az/

## What the page does

One reason to arrive (is this person allowed to help me?) and one action to leave with (check the official lists, report a scam):

1. Look up a lawyer at the State Bar of Arizona (link).
2. Look up an accredited representative or recognized organization on the official EOIR lists, and the EOIR list of disciplined practitioners (links).
3. Report a scam to the Arizona Attorney General or the FTC (links).

Below the steps, quoted word for word with each source's credit: the U.S. Department of Justice (EOIR) Notario National Notice (2009, English and its own Spanish), the ACLU of Arizona "Find an attorney" passage (English and its own Spanish, including its notary warning), and the 2011 EOIR flyer "Read This Before You Take Legal Advice" (English only). Links to the EOIR free legal services list and AZLawHelp.

## No legal wording is written by us

All legal wording is quoted unchanged (`tools/quotes.json`, built from pages saved in `tools/captures/`). `python3 tools/verify_quotes.py` proves each quote is a word for word match of its capture and that it is on the page. Everything else is a link or a short navigation label; the Spanish labels are listed in [docs/NEEDS-NATIVE-READ.md](docs/NEEDS-NATIVE-READ.md). Sources, their terms and what was left out are in [docs/SOURCES.md](docs/SOURCES.md).

## Privacy promise

- No cookies, no localStorage, no accounts, no forms, no analytics, no ads, no third-party fonts or scripts.
- A strict Content Security Policy blocks every outside request. The page loads only its own HTML, CSS and one small script.
- The language choice lives only in the page address (`?lang=en`).
- Links leave the site. Other sites have their own privacy rules.
- GitHub Pages, the planned host, may keep standard visit logs that the page cannot see or control.

## Accessibility and checks

WCAG 2.2 AA target. axe-core 0 violations (ES and EN at 375 and 1280), no sideways scroll at 320, 375 and 768, Lighthouse mobile 100/100/100/100 in both languages. Evidence: [docs/DEFINITION-OF-DONE.md](docs/DEFINITION-OF-DONE.md), [docs/screenshots](docs/screenshots), [docs/lighthouse](docs/lighthouse).

## Run it

Open `index.html` in a browser. Nothing to install.

## Change the content

```
python3 tools/extract_quotes.py   # rebuilds tools/quotes.json from tools/captures/
python3 tools/build.py            # rewrites index.html, docs/SOURCES.md, docs/NEEDS-NATIVE-READ.md
python3 tools/verify_quotes.py    # every quote must match its capture
./tools/audit.sh                  # axe, overflow, screenshots (Docker only)
./tools/dod.sh                    # icons, head and JSON-LD validation, keyboard, Lighthouse (Docker only)
```

`tools/fetch/` has the capture scripts (headless Chromium in Docker; nothing is installed on the host). When a link or quote is checked again, update `CHECKED` in `tools/build.py`.

## Deploy to GitHub Pages (only when the owner says so)

1. Make the repository public. 2. Settings, Pages, branch `main`, folder `/ (root)`. 3. If the address changes, update `SITE_URL` in `tools/build.py` and rebuild.

## License

MIT for the code and the page's own wording, see `LICENSE`. Quoted U.S. Department of Justice text is public domain; quoted ACLU of Arizona text stays under its copyright and is shown under the ACLU of Arizona user agreement (noncommercial, unedited, with notice). The organizations named own their names and materials; this page is not affiliated with them.
