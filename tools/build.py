#!/usr/bin/env python3
"""Builds index.html, docs/SOURCES.md and docs/NEEDS-NATIVE-READ.md from one place.

Run:  python3 tools/build.py     (after tools/extract_quotes.py when the captures change)
No dependencies. The output files are committed, so the site itself has no build step.
Rule: no legal wording on the page is written by us. Quoted text lives in tools/quotes.json (copied from captured source pages),
everything else is a link or a short navigation label (every Spanish one is listed in docs/NEEDS-NATIVE-READ.md).
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKED = "2026-11-27"
CHECKED_TXT = {"es": "27 de noviembre de 2026", "en": "November 27, 2026"}
SITE_URL = "https://brianallengit.github.io/verifica-tu-ayuda-az/"
NAME = "Verifica tu ayuda · Arizona"
E = html.escape

# id -> (url, Spanish label, English label, what we took from it, terms note)
SOURCES = {
    "eoir_notice_en": (
        "https://www.justice.gov/eoir/notario-national-notice",
        "Departamento de Justicia (EOIR): Notario National Notice, 22 de julio de 2009 (en inglés)",
        "Department of Justice (EOIR): Notario National Notice, July 22, 2009",
        "Quoted in full, word for word (English).",
        "US government work. justice.gov Legal Policies: \"Unless otherwise indicated, information on Department of Justice websites is in the public domain and may be copied and distributed without permission. Citation of the Department of Justice as source of the information is appreciated.\" Read 2026-11-27 at https://www.justice.gov/legalpolicies.",
    ),
    "eoir_notice_es": (
        "https://www.justice.gov/eoir/nationalnotariosnotice072209spanish",
        "Departamento de Justicia (EOIR): Aviso nacional sobre notarios, 22 de julio de 2009 (en español)",
        "Department of Justice (EOIR): Notario National Notice, Spanish version, July 22, 2009",
        "Quoted in full, word for word (Spanish, the Department's own translation).",
        "Same justice.gov public-domain policy as above.",
    ),
    "eoir_flyer": (
        "https://www.justice.gov/eoir/UPILFlyer06222011.pdf",
        "Departamento de Justicia (EOIR): Read This Before You Take Legal Advice (hoja de 2011, en inglés)",
        "Department of Justice (EOIR): Read This Before You Take Legal Advice (2011 flyer)",
        "Quoted in full, word for word (English only; no Spanish version was found on justice.gov). Listed on https://www.justice.gov/eoir/find-legal-representation. Its phone numbers, e-mail and two website addresses are the flyer's own, from 2011, and were not re-verified.",
        "Same justice.gov public-domain policy as above.",
    ),
    "acluaz_en": (
        "https://www.acluaz.org/know-your-rights/know-your-rights-during-and-after-workplace-raid/",
        "ACLU de Arizona: Know Your Rights Before, During, and After a Workplace Raid (en inglés)",
        "ACLU of Arizona: Know Your Rights Before, During, and After a Workplace Raid",
        "Quoted word for word: the whole \"Find an attorney\" subsection (including its notary warning and its sentence on how to check a lawyer and a non-lawyer).",
        "ACLU of Arizona User Agreement https://www.acluaz.org/user-agreement/ (read 2026-11-27, effective July 1, 2024): text may be copied or distributed, in print or digital form, with no editorial changes, no misleading excerpts, and the notice \"Copyright [year] ACLU of Arizona.\"; the page itself says nothing to the contrary.",
    ),
    "acluaz_es": (
        "https://www.acluaz.org/es/know-your-rights/conozca-sus-derechos-antes-durante-y-despues-de-una-redada-en-el-lugar-de-trabajo/",
        "ACLU de Arizona: Conozca sus derechos antes, durante y después de una redada en el lugar de trabajo (en español)",
        "ACLU of Arizona: Know Your Rights Before, During, and After a Workplace Raid (Spanish version)",
        "Quoted word for word: the whole \"Busque un abogado\" subsection, in the ACLU of Arizona's own Spanish.",
        "Same ACLU of Arizona User Agreement as above.",
    ),
    "azbar": (
        "https://www.azbar.org/search-for-a-legal-professional",
        "Colegio de Abogados del Estado de Arizona (State Bar of Arizona): buscar a un abogado",
        "State Bar of Arizona: search for a legal professional",
        "Link only. The page says (English and Spanish) to use the official State Bar search tools and not to rely on credentials from someone who contacts you unsolicited; none of its text is copied.",
        "State Bar terms https://www.azbar.org/about-us/terms-and-conditions-of-use/ say the site's material \"may not be copied, displayed, distributed, downloaded, linked, modified, posted, reproduced, republished, or transmitted\" without written consent. No text is copied. UNVERIFIED and for a human: whether a plain hyperlink to this public page is acceptable under that clause.",
    ),
    "eoir_roster": (
        "https://www.justice.gov/eoir/recognition-accreditation-roster-reports",
        "Departamento de Justicia (EOIR): listas de organizaciones reconocidas y representantes acreditados",
        "Department of Justice (EOIR): Recognized Organizations and Accredited Representatives rosters",
        "Link only. Official PDF lists (recognized organizations, accredited representatives, and both by state). Page says \"Updated April 28, 2025\"; the PDF contents were not read.",
        "Link only.",
    ),
    "eoir_discipline": (
        "https://www.justice.gov/eoir/list-of-currently-disciplined-practitioners",
        "Departamento de Justicia (EOIR): lista de profesionales sancionados actualmente (en inglés)",
        "Department of Justice (EOIR): List of Currently Disciplined Practitioners",
        "Link only. Official list of people not allowed to practice before EOIR; the page showed an update dated Nov. 23, 2026.",
        "Link only.",
    ),
    "eoir_probono": (
        "https://www.justice.gov/eoir/list-pro-bono-legal-service-providers",
        "Departamento de Justicia (EOIR): lista de proveedores de servicios legales gratuitos (pro bono)",
        "Department of Justice (EOIR): List of Pro Bono Legal Service Providers",
        "Link only. Official list by immigration court. EOIR says it does not endorse the organizations.",
        "Link only.",
    ),
    "azag": (
        "https://www.azag.gov/complaints/consumer",
        "Oficina del Fiscal General de Arizona: presentar una queja de consumidor (en inglés)",
        "Arizona Attorney General: File a Consumer Complaint",
        "Link only. The page (English) lists a Spanish online form and a Spanish PDF form, and says the office investigates consumer complaints and cannot act as your attorney.",
        "Link only. AZ AG reuse terms not read; no text is copied.",
    ),
    "azag_es": (
        "https://consumer-complaint.azag.gov/publiccomplaint/begin.aspx?lang=es",
        "Oficina del Fiscal General de Arizona: queja de consumidor en línea (en español)",
        "Arizona Attorney General: online consumer complaint form (Spanish)",
        "Link only, copied from the Spanish link on the AG page above. The form itself was not opened or filled in.",
        "Link only.",
    ),
    "ftc_es": (
        "https://reportefraude.ftc.gov/",
        "Comisión Federal de Comercio (FTC): ReporteFraude.ftc.gov (en español)",
        "Federal Trade Commission (FTC): ReporteFraude.ftc.gov (Spanish)",
        "Link only. The FTC site describes itself as the federal government's website where you can report fraud, scams and bad business practices.",
        "Link only. The FTC consumer-advice pages returned an automated-request block, so none of their text is used.",
    ),
    "ftc_en": (
        "https://reportfraud.ftc.gov/",
        "Comisión Federal de Comercio (FTC): ReportFraud.ftc.gov (en inglés)",
        "Federal Trade Commission (FTC): ReportFraud.ftc.gov",
        "Link only.",
        "Link only.",
    ),
    "azlh": (
        "https://www.azlawhelp.org/",
        "AZLawHelp (Arizona Bar Foundation)",
        "AZLawHelp (Arizona Bar Foundation)",
        "Link only. Named by the quoted ACLU of Arizona passage as a place for information on legal services providers in your county.",
        "Link only.",
    ),
}

SPANISH_UI = []  # every Spanish string written for this page, for docs/NEEDS-NATIVE-READ.md

TEXT = {
    "title": "Verifica tu ayuda: ¿puede esta persona ayudarte de verdad?",
    "title_en": "Check your helper: can this person really help you?",
    "desc": "¿Esta persona puede ayudarte con tu caso de inmigración? Revisa las listas oficiales y reporta estafas de notarios. Gratis, sin rastreo. Español e inglés.",
    "desc_en": "Is this person allowed to help with your immigration case? Check the official lists and report notario scams. Free, no tracking. Spanish and English.",
    "imgalt": "Verifica tu ayuda, Arizona: ¿puede esta persona ayudarte con tu caso de inmigración? Check your helper: is this person allowed to help you?",
}
SPANISH_UI += [TEXT["title"], TEXT["desc"], TEXT["imgalt"]]


def ext(url, label, extra=""):
    return '<a href="%s" rel="noopener noreferrer"%s>%s</a>' % (E(url, quote=True), extra, label)


def sources(lang, ids, level=3):
    head = {"es": "De dónde viene esta información", "en": "Where this information comes from"}[lang]
    chk = {"es": "revisado el", "en": "checked on"}[lang]
    li = []
    for i in ids:
        url, es, en, _f, _t = SOURCES[i]
        li.append('<li>%s <span class="chk">(%s <time datetime="%s">%s</time>)</span></li>'
                  % (ext(url, E(es if lang == "es" else en)), chk, CHECKED, CHECKED_TXT[lang]))
    return '<div class="src"><h%d>%s</h%d><ul>%s</ul></div>' % (level, head, level, "".join(li))


with open(os.path.join(ROOT, "tools", "quotes.json"), encoding="utf-8") as _f:
    QUOTES = json.load(_f)


def quote(lang, key):
    """A passage copied word for word from its source, with the credit its terms require."""
    q = QUOTES[key]
    es = lang == "es"
    link = '<a href="%s" rel="noopener noreferrer">%s</a>' % (E(q["url"], quote=True), E(q["url"]))
    read = ("Leído el %s." if es else "Read on %s.") % CHECKED_TXT[lang]
    if q["kind"] == "doj":
        label = "Cita del Departamento de Justicia de EE. UU. (EOIR), palabra por palabra y sin cambios" if es else "Quoted from the U.S. Department of Justice (EOIR), word for word and unchanged"
        d = q["doc_date"]
        notice = ("Fuente: U.S. Department of Justice, Executive Office for Immigration Review (EOIR), %s. Documento de %s. Información del gobierno de EE. UU., de dominio público. %s"
                  if es else "Source: U.S. Department of Justice, Executive Office for Immigration Review (EOIR), %s. Document dated %s. U.S. government information, in the public domain. %s") % (link, E(d), read)
    else:
        label = "Cita de la ACLU de Arizona, palabra por palabra y sin cambios" if es else "Quoted from the ACLU of Arizona, word for word and unchanged"
        notice = ("Copyright %s ACLU of Arizona. Originally posted by the ACLU of Arizona at %s. %s") % (q["year"], link, read)
    if es:
        SPANISH_UI.append(label)
    return '<figure class="quote" lang="%s"><p class="qlabel" lang="%s">%s</p><div class="qbody">%s</div><figcaption>%s</figcaption></figure>' % (
        q["lang"], lang, E(label), q["html"], notice)


def btn(url, label, cls="primary", lang_attr=""):
    return '<a class="btn %s" href="%s" rel="noopener noreferrer"%s>%s</a>' % (cls, E(url, quote=True), lang_attr, E(label))


def content(lang):
    es = lang == "es"
    p = lang
    h = []
    A = h.append

    def T(a, b):
        if es:
            SPANISH_UI.append(re.sub(r"<[^>]+>", "", a) if isinstance(a, str) else " | ".join(re.sub(r"<[^>]+>", "", x) for x in a))
        return a if es else b

    def sec(i, title, body):
        A('<section class="panel" id="%s-%s" tabindex="-1" aria-labelledby="%s-%s-h"><h2 id="%s-%s-h">%s</h2>%s</section>' % (p, i, p, i, p, i, title, body))

    A('<section class="notice" aria-labelledby="%s-imp-h"><h2 id="%s-imp-h">%s</h2><p>%s</p></section>' % (
        p, p, T("Importante", "Important"),
        T("Esta página da <strong>información general</strong> y enlaces a listas oficiales. <strong>No es consejo legal</strong> y no puede decirte si una persona es de confianza. "
          "No guarda ni recoge ningún dato tuyo. Los enlaces te llevan a otros sitios.",
          "This page gives <strong>general information</strong> and links to official lists. <strong>It is not legal advice</strong> and it cannot tell you whether a person is trustworthy. "
          "It does not save or collect any information about you. Links take you to other sites.")))

    # 1 steps: navigation only, every link is an official list or report page
    steps = [
        (T("Si la persona dice que es <strong>abogado</strong>: búscala por nombre en el Colegio de Abogados del Estado de Arizona.",
           "If the person says they are a <strong>lawyer</strong>: look up the name at the State Bar of Arizona."),
         [btn(SOURCES["azbar"][0], T("Buscar a un abogado (State Bar of Arizona)", "Look up a lawyer (State Bar of Arizona)"), "primary")]),
        (T("Si dice que es <strong>representante acreditado</strong> o que trabaja en una <strong>organización reconocida</strong>: busca el nombre en las listas oficiales de EOIR.",
           "If the person says they are an <strong>accredited representative</strong> or work for a <strong>recognized organization</strong>: look for the name on the official EOIR lists."),
         [btn(SOURCES["eoir_roster"][0], T("Listas de EOIR: organizaciones reconocidas y representantes acreditados", "EOIR lists: recognized organizations and accredited representatives"), "primary"),
          btn(SOURCES["eoir_discipline"][0], T("Lista de EOIR: profesionales sancionados (en inglés)", "EOIR list: disciplined practitioners"), "secondary")]),
        (T("Si ya pagaste o firmaste y algo no está bien: <strong>repórtalo</strong>.",
           "If you already paid or signed and something is wrong: <strong>report it</strong>."),
         [btn(SOURCES["azag_es"][0] if es else "https://consumer-complaint.azag.gov/publiccomplaint/begin.aspx",
              T("Queja al Fiscal General de Arizona (en español)", "Complaint to the Arizona Attorney General"), "primary"),
          btn(SOURCES["ftc_es"][0] if es else SOURCES["ftc_en"][0], T("Reportar a la FTC (en español)", "Report to the FTC"), "primary")]),
    ]
    body = '<p>%s</p><ol class="steps">%s</ol>' % (
        T("Antes de pagar o firmar, haz estas comprobaciones. Cada botón abre una lista o una página oficial.",
          "Before you pay or sign, do these checks. Each button opens an official list or page."),
        "".join('<li><p>%s</p><div class="calls">%s</div></li>' % (t, "".join(b)) for t, b in steps))
    sec("steps", T("Qué hacer ahora", "What to do now"), body + sources(lang, ["azbar", "eoir_roster", "eoir_discipline", "azag", "azag_es", "ftc_es" if es else "ftc_en"]))

    # 2 DOJ notice, quoted whole
    sec("notice", T("Lo que dice el Departamento de Justicia sobre los notarios", "What the Department of Justice says about notarios"),
        "<p>%s</p>%s%s" % (
            T("Este aviso es de 2009 y sigue publicado en el sitio del Departamento de Justicia. Se copia completo.",
              "This notice is from 2009 and is still posted on the Department of Justice site. It is copied in full."),
            quote(lang, "eoir_notice_" + lang), sources(lang, ["eoir_notice_" + lang])))

    # 3 how to check
    sec("check", T("Cómo comprobar a alguien", "How to check someone"),
        "<p>%s</p>%s<p>%s</p>%s%s" % (
            T("Esto lo dice la ACLU de Arizona.", "This is what the ACLU of Arizona says."),
            quote(lang, "az_%s_attorney" % lang),
            T("Esta hoja del Departamento de Justicia es de 2011 y solo existe en inglés. Se copia completa. Sus teléfonos y direcciones son de 2011 y no se revisaron.",
              "This Department of Justice flyer is from 2011. It is copied in full. Its phone numbers and addresses are from 2011 and were not re-checked.") if es else
            "This Department of Justice flyer is from 2011. It is copied in full. Its phone numbers and addresses are from 2011 and were not re-checked.",
            quote(lang, "eoir_flyer_en"),
            sources(lang, ["acluaz_" + lang, "eoir_flyer"])))

    # 4 free help (links only)
    sec("help", T("Ayuda legal gratuita o de bajo costo", "Free or low-cost legal help"),
        "<p>%s</p><div class=\"calls\">%s%s</div>%s" % (
            T("Para buscar organizaciones que dan ayuda legal gratuita o de bajo costo, usa estas listas.",
              "To find organizations that give free or low-cost legal help, use these lists."),
            btn(SOURCES["eoir_probono"][0], T("Lista de EOIR: servicios legales gratuitos (pro bono)", "EOIR list: free (pro bono) legal services"), "primary"),
            btn(SOURCES["azlh"][0], T("AZLawHelp (Arizona Bar Foundation)", "AZLawHelp (Arizona Bar Foundation)"), "secondary"),
            sources(lang, ["eoir_probono", "azlh"])))

    # 5 about
    li = T([
        "<strong>No es consejo legal.</strong> Es una página de enlaces y de citas copiadas de fuentes oficiales y de la ACLU de Arizona. Nada aquí garantiza que una persona sea de confianza. Habla con un abogado o un representante acreditado sobre tu caso.",
        "<strong>No recogemos datos.</strong> Esta página no tiene analíticas, anuncios, cookies, formularios ni cuentas, y no guarda nada.",
        "<strong>Los enlaces salen de este sitio.</strong> Los otros sitios tienen sus propias reglas de privacidad.",
        "Cada enlace se revisó el <time datetime=\"%s\">%s</time>. Las citas son del Departamento de Justicia de EE. UU. (de dominio público) y de la ACLU de Arizona; se copian <strong>palabra por palabra y sin cambios</strong>, con el crédito que cada fuente pide. Los títulos, botones y avisos fuera de un recuadro de cita son de esta página." % (CHECKED, CHECKED_TXT["es"]),
        "Esta página no está afiliada a ninguna de las organizaciones nombradas ni al gobierno.",
        "En un teléfono o computadora compartidos, el historial del navegador puede mostrar que visitaste esta página.",
        "Es gratis y siempre lo será.",
    ], [
        "<strong>This is not legal advice.</strong> It is a page of links and of quotes copied from official sources and the ACLU of Arizona. Nothing here guarantees that a person is trustworthy. Talk to a lawyer or an accredited representative about your case.",
        "<strong>We collect no data.</strong> This page has no analytics, ads, cookies, forms or accounts, and it saves nothing.",
        "<strong>Links leave this site.</strong> Other sites have their own privacy rules.",
        "Every link was checked on <time datetime=\"%s\">%s</time>. The quotes are from the U.S. Department of Justice (public domain) and the ACLU of Arizona; they are copied <strong>word for word and unchanged</strong>, with the credit each source asks for. Headings, buttons and notices outside a quote box are this page's own." % (CHECKED, CHECKED_TXT["en"]),
        "This page is not affiliated with any of the organizations named or with the government.",
        "On a shared phone or computer, the browser history can show that you visited this page.",
        "It is free and always will be.",
    ])
    sec("about", T("Sobre esta página", "About this page"),
        '<ul class="list">%s</ul><div class="calls no-print"><button type="button" class="btn primary big js-print">%s</button></div>' % (
            "".join("<li>%s</li>" % x for x in li), T("Imprimir esta página", "Print this page")))
    h.insert(1, h.pop(0))  # the action comes first, the notice right after it
    return "\n".join(h)


def jsonld_graph():
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": SITE_URL + "#org", "name": NAME, "url": SITE_URL, "logo": SITE_URL + "apple-touch-icon.png",
             "description": "Free, ad-free, zero-tracking page in Spanish and English that links to the official lists for checking whether a person may help with an immigration case in Arizona."},
            {"@type": "WebSite", "@id": SITE_URL + "#website", "url": SITE_URL, "name": NAME, "description": TEXT["desc"],
             "inLanguage": ["es", "en"], "publisher": {"@id": SITE_URL + "#org"}},
            {"@type": "WebPage", "@id": SITE_URL + "#webpage", "url": SITE_URL, "name": TEXT["title"], "description": TEXT["desc"],
             "inLanguage": ["es", "en"], "isPartOf": {"@id": SITE_URL + "#website"}, "publisher": {"@id": SITE_URL + "#org"},
             "dateModified": CHECKED,
             "primaryImageOfPage": {"@type": "ImageObject", "url": SITE_URL + "og-image.png", "width": 1200, "height": 630},
             "about": {"@type": "Thing", "name": "Checking whether a person is allowed to give immigration legal help, and reporting notario fraud"}},
        ],
    }


def page():
    foot_es = ("Este sitio no tiene analíticas y no guarda nada. Está alojado en GitHub Pages, que puede guardar registros estándar de visitas "
               "que nosotros no podemos ver ni controlar. Nosotros no agregamos nada.")
    foot_en = ("This site has no analytics and saves nothing. It is hosted on GitHub Pages, which may keep standard visit logs "
               "that we cannot see or control. We add nothing.")
    SPANISH_UI.extend([foot_es, "Ir al contenido", "Verifica tu ayuda", "Inmigración · Arizona",
                       "¿Esta persona de verdad puede ayudarme con mi caso de inmigración? Compruébalo en las listas oficiales antes de pagar o firmar.",
                       "Imprimir esta página"])
    jsonld = json.dumps(jsonld_graph(), ensure_ascii=False, indent=1).replace("</", "<\\/")
    es_html, en_html = content("es"), content("en")
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{site}">
<link rel="alternate" hreflang="es" href="{site}">
<link rel="alternate" hreflang="en" href="{site}">
<link rel="alternate" hreflang="x-default" href="{site}">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{imgalt}">
<meta property="og:url" content="{site}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_US">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}og-image.png">
<meta name="twitter:image:alt" content="{imgalt}">
<meta name="theme-color" content="#115e59">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<script type="application/ld+json">{jsonld}</script>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; manifest-src 'self'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<link rel="stylesheet" href="style.css">
<noscript><link rel="stylesheet" href="noscript.css"></noscript>
</head>
<body>
<a class="skip es" href="#main">Ir al contenido</a>
<a class="skip en" href="#main" lang="en">Skip to content</a>
<header class="top">
  <div class="brand">
    <h1 class="es">Verifica tu ayuda <span class="where">Inmigración · Arizona</span></h1>
    <h1 class="en" lang="en">Check your helper <span class="where">Immigration · Arizona</span></h1>
  </div>
  <div class="langs no-print" role="group" aria-label="Idioma / Language">
    <button type="button" id="lang-es" data-lang="es" lang="es" aria-label="ES, Español" aria-pressed="true">ES</button>
    <button type="button" id="lang-en" data-lang="en" lang="en" aria-label="EN, English" aria-pressed="false">EN</button>
  </div>
</header>

<main id="main" tabindex="-1">
<div class="es wrap">
<p class="lead">¿Esta persona de verdad puede ayudarme con mi caso de inmigración? Compruébalo en las listas oficiales antes de pagar o firmar.</p>
{es}
</div>
<div class="en wrap" lang="en">
<p class="lead">Is this person really allowed to help me with my immigration case? Check the official lists before you pay or sign.</p>
{en}
</div>
</main>

<footer>
  <p class="es">{foot_es}</p>
  <p class="en" lang="en">{foot_en}</p>
  <p>{name} · MIT</p>
</footer>
<script src="app.js"></script>
</body>
</html>
""".format(desc=TEXT["desc"], title=TEXT["title"], imgalt=TEXT["imgalt"], jsonld=jsonld, site=SITE_URL, name=NAME,
           es=es_html, en=en_html, foot_es=foot_es, foot_en=foot_en)


def sources_md():
    out = ["# Sources", "",
           "Every external fact and quote on the site, with the page it was read on and the terms that allow (or do not allow) using it.",
           "All pages were read on %s. This file is generated by `tools/build.py`; edit the lists there." % CHECKED, "",
           "Rule: no legal wording on the page is written by us. It is either quoted word for word (`tools/quotes.json`, proven by `tools/verify_quotes.py` against `tools/captures/`) or it is a link.", "",
           "## Source pages", "", "| # | Source | URL | What the page uses | Terms |", "|---|---|---|---|---|"]
    for n, (k, (url, _es, en, facts, terms)) in enumerate(SOURCES.items(), 1):
        out.append("| %d | %s | %s | %s | %s |" % (n, en, url, facts, terms.replace("|", "/")))
    out += ["", "## Quotes (5 records, 4 shown per language)", "",
            "| Key | Source | Shown in |", "|---|---|---|",
            "| eoir_notice_en | DOJ/EOIR Notario National Notice, July 22, 2009 | English view |",
            "| eoir_notice_es | DOJ/EOIR Aviso nacional sobre notarios, 22 de julio de 2009 | Spanish view |",
            "| eoir_flyer_en | DOJ/EOIR \"Read This Before You Take Legal Advice\", 2011 (English only) | both views |",
            "| az_en_attorney | ACLU of Arizona, \"Find an attorney\" subsection | English view |",
            "| az_es_attorney | ACLU of Arizona, \"Busque un abogado\" subsection | Spanish view |",
            "", "## Looked for and left out", "",
            "- FTC consumer-advice pages and publications on notario fraud (consumer.ftc.gov, bulkorder.ftc.gov): the automated fetch got an \"abusive automated request\" block page. Not worked around. Only the ReportFraud.ftc.gov and ReporteFraude.ftc.gov report pages (which loaded) are linked. A person could open the FTC pages in a browser and, if they allow copying (US government work, likely public domain, unconfirmed), add a quote.",
            "- USCIS \"avoid scams\" and notario pages: the guessed addresses returned \"Page Not Found\"; nothing was used.",
            "- EOIR Fraud and Abuse Prevention Program page: the guessed address returned 404. Its contact details appear only inside the quoted 2011 flyer and were not re-verified.",
            "- Arizona Attorney General notario warning: the guessed address returned 404 (search fell back to an unrelated result). Only the AG's consumer complaint page is linked. AG reuse terms were not read.",
            "- State Bar of Arizona lawyer lookup: the search page loads and says (English and Spanish) to use the official State Bar tools and not to trust credentials from unsolicited contacts. Its terms forbid copying and, literally, linking without written consent, so only a link is used. The State Bar's own unauthorized-practice page lists 602.340.7280 while the quoted ACLU of Arizona text says (602) 340-7239 for the State Bar; the page uses neither number outside the quote.",
            "- EOIR roster PDFs: not opened. They are linked from the roster page, which was read.",
            "- An official Spanish version of the 2011 EOIR flyer: not found on justice.gov; the flyer is shown in English in both views.",
            "- The ILRC family-plan sentence on the two categories of people who can give advice: not used (link-only source, \"All rights reserved\").",
            "", "## Notes for the reviewer", "",
            "- Spanish headings, buttons and notices written for this page were produced by an AI and need a native-speaker read: see NEEDS-NATIVE-READ.md. The quoted Spanish is the Department of Justice's and the ACLU of Arizona's own.",
            "- The 2009 DOJ notice and the 2011 flyer are old. They remain posted on justice.gov (the notice's page shows \"Updated July 20, 2021\" in English and \"Updated August 26, 2015\" in Spanish). A human should decide whether to keep them.",
            "- The notice's Spanish page contains the source's own accent typo \"Pràcticas\" and the quote keeps it, because the text is copied unchanged.",
            ""]
    return "\n".join(out)


def native_md():
    seen, rows = set(), []
    for s in SPANISH_UI:
        s = html.unescape(re.sub(r"\s+", " ", s)).strip()
        if s and s not in seen:
            seen.add(s)
            rows.append(s)
    out = ["# Spanish text written for this page (needs a native-speaker read)", "",
           "Generated by `tools/build.py`. Every Spanish string below was written by an AI, not copied from a source. The quoted Spanish (DOJ/EOIR, ACLU of Arizona) is not listed here because it is copied unchanged.",
           "Questions for the reader: natural for Mexican and Central American Spanish readers in Arizona? Is \"Fiscal General\" the right term for the Arizona Attorney General's office? Is \"notario\" explained enough by the quoted notice? Any phrase that sounds like legal advice?", "",
           "Also written by us, in `app.js`: the ES page title and description (same strings as the first two items below).", ""]
    out += ["%d. %s" % (i, r) for i, r in enumerate(rows, 1)]
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    out = page()
    assert chr(0x2014) not in out, "em dash found"
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
    md = sources_md()
    nm = native_md()
    assert chr(0x2014) not in md + nm
    open(os.path.join(ROOT, "docs", "SOURCES.md"), "w", encoding="utf-8").write(md)
    open(os.path.join(ROOT, "docs", "NEEDS-NATIVE-READ.md"), "w", encoding="utf-8").write(nm)
    t, d = TEXT["title"], TEXT["desc"]
    print("built index.html (%d bytes); title %d chars, desc %d chars; en title %d, en desc %d" % (len(out), len(t), len(d), len(TEXT["title_en"]), len(TEXT["desc_en"])))
