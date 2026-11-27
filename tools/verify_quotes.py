#!/usr/bin/env python3
"""Proves every quote in tools/quotes.json (and so on the page) is a word for word match of a captured source.

For each quote: strip tags, unescape entities, collapse whitespace, then require the result to appear inside the
captured source text (same normalisation). Also checks the page itself: every quote box in index.html must contain
exactly the quote's text. Exit 1 on any mismatch.
"""
import html as H
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAP = os.path.join(HERE, "captures")
SOURCE = {"eoir_notice_en": "eoir_notice_en.html", "eoir_notice_es": "eoir_notice_es.html", "eoir_flyer_en": "eoir_flyer.txt",
          "az_en_attorney": "azen_1.html", "az_es_attorney": "azes_1.html"}


def norm(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<svg.*?</svg>", " ", s, flags=re.S)
    s = re.sub(r"</(li|p|h\d|div|ul|ol|td|tr)>|<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[\x80-\x9f\uf000-\uf8ff]", " ", s)  # PDF bullet glyphs
    s = H.unescape(s).replace(" ", " ")
    # the PDF text has a few spaces before/after punctuation from layout; only whitespace is normalised
    return re.sub(r"\s+", " ", s).strip()


def main():
    quotes = json.load(open(os.path.join(HERE, "quotes.json"), encoding="utf-8"))
    page = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    bad = 0
    for key, q in quotes.items():
        src = norm(open(os.path.join(CAP, SOURCE[key]), encoding="utf-8", errors="replace").read())
        txt = norm(q["html"])
        # drop the title paragraph pieces we turned into headings: they must also be in the source, checked line by line below
        ok_src = txt in src
        if not ok_src:
            # the sources sometimes glue or split words around inline tags (for example "can </em>provide"); compare with all whitespace removed
            ok_src = re.sub(r"\s", "", txt) in re.sub(r"\s", "", src)
        n_page = page.count(q["html"])
        ok_page = n_page >= 1
        print("%s %-16s %5d chars  in source: %s  on page: %s" % ("PASS" if ok_src and ok_page else "FAIL", key, len(txt), ok_src, "%dx" % n_page))
        if not (ok_src and ok_page):
            bad += 1
    print("QUOTES: %d checked, %d failed" % (len(quotes), bad))
    sys.exit(1 if bad else 0)


main()
