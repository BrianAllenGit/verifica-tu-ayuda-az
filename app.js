(function () {
  'use strict';
  // Nothing is stored and nothing is sent. The language choice lives only in the page address (?lang=en).
  var TITLES = { es: 'Verifica tu ayuda: ¿puede esta persona ayudarte de verdad?', en: 'Check your helper: can this person really help you?' };
  var DESCS = {
    es: '¿Esta persona puede ayudarte con tu caso de inmigración? Revisa las listas oficiales y reporta estafas de notarios. Gratis, sin rastreo. Español e inglés.',
    en: 'Is this person allowed to help with your immigration case? Check the official lists and report notario scams. Free, no tracking. Spanish and English.'
  };
  var root = document.documentElement;

  function current() { return root.classList.contains('en') ? 'en' : 'es'; }

  function setLang(lang, keepHash) {
    if (lang !== 'en') lang = 'es';
    root.classList.toggle('en', lang === 'en');
    root.lang = lang;
    document.title = TITLES[lang];
    var md = document.querySelector('meta[name="description"]');
    if (md) md.setAttribute('content', DESCS[lang]);
    document.getElementById('lang-es').setAttribute('aria-pressed', String(lang === 'es'));
    document.getElementById('lang-en').setAttribute('aria-pressed', String(lang === 'en'));
    try {
      var hash = keepHash ? location.hash : '';
      history.replaceState(null, '', location.pathname + (lang === 'en' ? '?lang=en' : '') + hash);
    } catch (e) { /* file:// or old browser: the page still works */ }
  }

  function initial() {
    var m = /[?&]lang=(en|es)\b/.exec(location.search);
    if (m) return m[1];
    var h = /^#(en|es)-/.exec(location.hash);
    if (h) return h[1];
    return 'es'; // Spanish first
  }

  document.getElementById('lang-es').addEventListener('click', function () { setLang('es'); });
  document.getElementById('lang-en').addEventListener('click', function () { setLang('en'); });

  var printers = document.querySelectorAll('.js-print');
  for (var i = 0; i < printers.length; i++) printers[i].addEventListener('click', function () { window.print(); });

  // Move keyboard and screen reader focus to the section a menu button jumps to.
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var t = document.getElementById(a.getAttribute('href').slice(1));
    if (t && t.hasAttribute('tabindex')) setTimeout(function () { t.focus({ preventScroll: true }); }, 0);
  });

  setLang(initial(), true);
  if (location.hash && current() === 'en') {
    var el = document.getElementById(location.hash.slice(1));
    if (el) el.scrollIntoView();
  }
})();
