# Website definition of done: evidence

Mirrors Brian's website definition of done (vault: `me/working-together/web-definition-of-done.md`). Run 2026-11-27 inside Docker only (Playwright image, axe-core 4.10.2, Lighthouse 12.2.1 in the throwaway container). Re-run with `./tools/audit.sh` and `./tools/dod.sh`. Planned address (not live): https://brianallengit.github.io/verifica-tu-ayuda-az/

Language approach: one page, one canonical URL, both languages in the same static HTML; `es`, `en` and `x-default` alternates all point to it (same reasoning as the sibling site conoce-tus-derechos-az). `?lang=en` works as a share link.

## 1. Accessibility
- [x] axe-core 0 violations, ES and EN at 375 and 1280 (`docs/screenshots/audit-report.txt`): 40 rules passed, 0 incomplete, 0 console errors in each of the four runs.
- [x] Keyboard: 28 tab stops in each language, 0 without a visible focus indicator, no trap, skip link first (`docs/lighthouse/extra.txt`).
- [x] One visible H1 per language, headings in order (a first run caught a skipped heading level in the quote boxes; fixed), landmarks, no inputs, no meaningful images in the body.
- [x] Contrast (axe color-contrast passes) and targets: 0 tap targets under 44px at 320, 375, 768.
- [x] reduced-motion and forced-colors (screenshots in `docs/lighthouse/`). JavaScript off: both languages shown, all 10 panels in the static HTML.
- [ ] Not machine-verifiable: real screen reader pass, native Spanish read, real-device phone test.

## 2. Phone first
- [x] No horizontal scroll and nothing past the edge at 320, 375, 768 in ES and EN; 1280 screenshots in `docs/screenshots/`. Text-spacing overrides at 320 and 375 and 200% zoom equivalent: no overflow.

## 3. Languages
- [x] ES default, visible ES/EN switch, `lang` on `<html>` updates, hreflang es/en/x-default in the head.

## 4. Search
- [x] Title 58 characters, meta description 154, canonical, robots meta, `robots.txt`, `sitemap.xml` with alternates (`docs/lighthouse/validate.txt`, 55 checks, 0 fail).
- [x] JSON-LD `@graph`: Organization, WebSite, WebPage; parses, ids resolve, name and description equal the visible ones. No FAQPage or HowTo (not needed). Run Google's Rich Results Test by hand at ship time.
- [x] All content is in the static HTML.

## 5. Link previews
- [x] Open Graph and Twitter tags complete; `og-image.png` 1200x630, under 1 MB. Parsed from the built HTML. [ ] Platform debuggers by hand at ship time (cannot read a private repo).

## 6. AI answers
- [x] Plain lead and "what to do now" steps at the top; `llms.txt` with summary, sources and limits; no "best" claims.

## 7. App polish
- [x] Favicon set, apple-touch-icon, theme-color, manifest, print styles.
- [x] Lighthouse mobile (Docker, local server): ES 100/100/100/100, EN 100/100/100/100 (performance, accessibility, best practices, SEO). Informational: cache TTL, compression and render-blocking depend on the production host.

## 8. Trust and safety
- [x] Zero tracking, storage, ads, third-party requests (audit fails on any external request; 0 seen). Strict CSP.
- [x] Facts come from sources whose terms were read (`docs/SOURCES.md`); quotes verified word for word (`tools/verify_quotes.py`, 5 of 5). No legal wording written by us.
- [x] No person named in the HTML or JSON-LD. The planned host contains the GitHub handle, as for the sibling sites.

## Open before shipping
- [ ] Native Spanish read of `docs/NEEDS-NATIVE-READ.md`.
- [ ] State Bar of Arizona terms: a human decides whether a plain link to its public lookup page is acceptable (see `docs/SOURCES.md`).
- [ ] Decide whether to keep the 2009 notice and 2011 flyer (old but still posted by DOJ), and whether to add FTC consumer pages that a bot could not read.
- [ ] Rich Results Test, link debuggers, live-URL checks for robots, sitemap, llms.txt, manifest.
