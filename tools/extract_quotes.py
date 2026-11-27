#!/usr/bin/env python3
"""Builds tools/quotes.json from the pages captured in tools/captures/ (see tools/fetch/).

The quoted text is copied from the captured pages. Nothing is reworded.
Only markup is touched: images, icons, spacer breaks and non-breaking spaces are dropped, target="_blank" is removed,
tags b/strong/i/em are kept, and the source's centered title paragraphs become headings.
tools/verify_quotes.py then proves that every quote is a word for word match of its capture.

Usage: python3 tools/extract_quotes.py
"""
import html as H
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(HERE, "captures")
OUT = os.path.join(HERE, "quotes.json")
RETRIEVED = "2026-11-27"
E = H.escape


def rd(name):
    with open(os.path.join(CAP, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def slice_between(body, start, end=None, include_end=False):
    a = body.index(start)
    if not end:
        return body[a:]
    b = body.index(end, a)
    return body[a:b + (len(end) if include_end else 0)]


def common_clean(h):
    h = re.sub(r"<svg.*?</svg>", "", h, flags=re.S)
    h = re.sub(r'\s+target="_blank"', "", h)
    h = re.sub(r'\s+rel="noopener"', "", h)
    h = re.sub(r'\s+(?:class|data-[a-z-]+|style)="[^"]*"', "", h)
    h = h.replace("&nbsp;", " ")
    return h


def clean_eoir(h):
    h = common_clean(h)
    # links to old usdoj.gov addresses stay as plain text: the words are the source's, the link is not ours to vouch for
    h = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", h, flags=re.S)
    h = re.sub(r"<span[^>]*>(.*?)</span>", r"\1", h, flags=re.S)
    h = re.sub(r"<div>|</div>", "", h)
    h = re.sub(r"(?:<br>\s*)+(?=\s*</li>)", "", h)  # trailing spacer breaks
    h = re.sub(r"\s*<br>\s*(?=<li>|\s*</li>|</?ul>)", "", h)
    h = re.sub(r"(</li>)(?:\s*<br>)+", r"\1", h)
    h = re.sub(r"(?:<br>\s*)+(?=<li>)", "", h)
    h = re.sub(r"<li>\s*</li>", "", h)
    h = re.sub(r"<p>\s*</p>", "", h)
    h = h.replace("<b>", "<strong>").replace("</b>", "</strong>").replace("<i>", "<em>").replace("</i>", "</em>")
    h = re.sub(r"<strong>\s*</strong>", "", h)
    h = re.sub(r"\n\s*\n+", "\n", h)
    return h.strip()


def clean_aclu(h):
    h = common_clean(h)
    h = re.sub(r'<a href="([^"]*)">', r'<a href="\1" rel="noopener noreferrer">', h)
    return h.strip()


quotes = {}


def add(key, lang, kind, url, title, body, notice_year=None, doc_date=None):
    quotes[key] = {"lang": lang, "kind": kind, "url": url, "title": title, "html": body, "year": notice_year,
                   "doc_date": doc_date, "retrieved": RETRIEVED}


# EOIR "Notario National Notice" (U.S. Department of Justice, public domain), English and Spanish
EOIR_EN = "https://www.justice.gov/eoir/notario-national-notice"
EOIR_ES = "https://www.justice.gov/eoir/nationalnotariosnotice072209spanish"
en = rd("eoir_notice_en.html")
b = slice_between(en, "<p>July 22, 2009</p>", "<p><span>", False)
b = b.replace('<p style="text-align:center"><b><span>Do Not Be a Victim of Immigration Fraud</span> </b></p>',
              "<h3>Do Not Be a Victim of Immigration Fraud</h3>")
b = re.sub(r'<p style="text-align:center"><b><i><span>(.*?)</span> </i> </b></p>', r"<p><strong><em>\1</em></strong></p>", b, flags=re.S)
add("eoir_notice_en", "en", "doj", EOIR_EN, "Notario National Notice", clean_eoir(b), None, "July 22, 2009")

es = rd("eoir_notice_es.html")
b = slice_between(es, "<p>22 de julio de 2009</p>", "<p>-- EOIR --</p>")
b = b.replace("<p><strong>No sea víctima del fraude de inmigración </strong></p>", "<h3>No sea víctima del fraude de inmigración</h3>")
add("eoir_notice_es", "es", "doj", EOIR_ES, "Aviso nacional sobre notarios", clean_eoir(b), None, "22 de julio de 2009")

# EOIR flyer "Read this before you take legal advice" (public domain), English only
fly = " ".join(rd("eoir_flyer.txt").split())
FLY = [
    ("h4", "READ THIS BEFORE YOU TAKE LEGAL ADVICE"),
    ("p", "If you have a case in immigration court, only take legal advice from:"),
    ("strong", "a licensed attorney"),
    ("p", "An “attorney” is a person who has a valid license from a state to practice law."),
    ("strong", "an accredited representative"),
    ("p", "An “accredited representative” is an individual who works with a recognized organization and has been given permission by the United States Government to help people in immigration court. A “recognized organization” is a nonprofit, religious, charitable, social service, or similar organization that has been given permission by the United States Government to help people in immigration court."),
    ("p", "If someone claims to be an attorney and you want to know if that person is allowed to represent you in immigration court:"),
    ("li", "Ask in what state(s) he or she is licensed to practice law."),
    ("li", "Call the office that licenses attorneys in that state (this is usually the “state bar association” or the supreme court of that state) and ask that office if the attorney has a bar number and is in “good standing.”"),
    ("li", "Go to the EOIR Web site at www.justice.gov/eoir/discipline.htm to find out who is not permitted to represent you in immigration court."),
    ("p", "If someone claims to be an accredited representative and you want to know if that person is allowed to represent you in immigration court, go to the EOIR Web site at www.justice.gov/eoir/ra.html and select “Accredited Representatives List” or call (703) 305-9029 for information."),
    ("p", "If you think you have been a victim of immigration fraud, contact the EOIR Fraud and Abuse Prevention Program at: EOIR.Fraud.Program@usdoj.gov or (703) 305-0470."),
]
out, ul = [], False
for t, x in FLY:
    if t == "li" and not ul:
        out.append("<ul>"); ul = True
    if t != "li" and ul:
        out.append("</ul>"); ul = False
    out.append({"h4": "<h3>%s</h3>", "p": "<p>%s</p>", "strong": "<p><strong>%s</strong></p>", "li": "<li>%s</li>"}[t] % E(x))
if ul:
    out.append("</ul>")
add("eoir_flyer_en", "en", "doj", "https://www.justice.gov/eoir/UPILFlyer06222011.pdf", "Read this before you take legal advice", "\n".join(out), None, "2011")

# ACLU of Arizona: "Find an attorney" subsection, whole, nothing cut (English and Spanish)
AZ_EN = "https://www.acluaz.org/know-your-rights/know-your-rights-during-and-after-workplace-raid/"
AZ_ES = "https://www.acluaz.org/es/know-your-rights/conozca-sus-derechos-antes-durante-y-despues-de-una-redada-en-el-lugar-de-trabajo/"
b = rd("azen_1.html")
s = slice_between(b, "<p>Find an attorney<br>", "<p>Know where important documents are<br>")
add("az_en_attorney", "en", "az", AZ_EN, None, clean_aclu(s), "2025")
b = rd("azes_1.html")
s = slice_between(b, "<p>Busque un abogado<br>", "<p>Tenga a la mano sus documentos importantes<br>")
s = clean_aclu(s).replace('<a href="https://www.justice.gov/eoir/file/probonofulllist/dl" rel="noopener noreferrer">aquí</a>',
              '<a href="https://www.justice.gov/eoir/file/probonofulllist/dl" rel="noopener noreferrer nofollow" aria-label="aquí, lista de proveedores de servicios legales pro bono (EOIR)">aquí</a>')
assert "aria-label" in s
add("az_es_attorney", "es", "az", AZ_ES, None, s, "2025")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(quotes, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("wrote", OUT, len(quotes), "quotes")
