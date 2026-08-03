# -*- coding: utf-8 -*-
"""
Clean 4 additional public-domain Project Gutenberg novels into plain reading
text, for the deep-earn-step-2 combined-corpus PPMI+SVD probe (larger corpus
than the single-novel Anne-only PPMI cell, commit bfdbf6b17). Same
strip-boilerplate approach as data/corpora/anne_of_green_gables/clean_gutenberg.py
(PG_START/PG_END markers), simplified (no chapter-marker/complexity-stats
apparatus -- not needed for a co-occurrence-vocabulary corpus; this is a
data-prep pass, not a new mechanism).

Pure stdlib (re). No network at run time -- raw/*.txt already downloaded from
gutenberg.org (public domain in the US; PG trademark applies only to the
packaged header/footer, which we strip here).

Books (slug, pg_id, raw filename, title, author):
  wizard_of_oz          55   The Wonderful Wizard of Oz         L. Frank Baum
  tom_sawyer            74   The Adventures of Tom Sawyer       Mark Twain
  little_women         514   Little Women                       Louisa May Alcott
  alice_in_wonderland   11   Alice's Adventures in Wonderland   Lewis Carroll

Output per book: data/corpora/<slug>/cleaned/<slug>.clean.txt
"""
import os
import re

BASE = r"d:/AI/hd-instrument/data/corpora"

BOOKS = [
    dict(slug="wizard_of_oz", pg_id=55, file="wizard_of_oz_55.txt",
         title="The Wonderful Wizard of Oz", author="L. Frank Baum"),
    dict(slug="tom_sawyer", pg_id=74, file="tom_sawyer_74.txt",
         title="The Adventures of Tom Sawyer", author="Mark Twain"),
    dict(slug="little_women", pg_id=514, file="little_women_514.txt",
         title="Little Women", author="Louisa May Alcott"),
    dict(slug="alice_in_wonderland", pg_id=11, file="alice_in_wonderland_11.txt",
         title="Alice's Adventures in Wonderland", author="Lewis Carroll"),
]

PG_START = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)


def clean_book(b):
    raw_path = os.path.join(BASE, b["slug"], "raw", b["file"])
    with open(raw_path, encoding="utf-8") as f:
        text = f.read()
    ms, me = PG_START.search(text), PG_END.search(text)
    body = text[ms.end():me.start()] if (ms and me) else text
    body = re.sub(r"\[Illustration.*?\]", "", body, flags=re.S)
    body = re.sub(r"\r\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

    out_dir = os.path.join(BASE, b["slug"], "cleaned")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, b["slug"] + ".clean.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body)
    n_words = len(re.findall(r"[A-Za-z][A-Za-z'\-]*", body))
    return dict(slug=b["slug"], title=b["title"], author=b["author"],
                pg_id=b["pg_id"], n_words=n_words, out_path=out_path,
                source=f"Project Gutenberg eBook #{b['pg_id']} "
                       f"(https://www.gutenberg.org/ebooks/{b['pg_id']})",
                license="Public domain (US) -- Project Gutenberg; PG trademark "
                        "applies only to the packaged header/footer, stripped here")


if __name__ == "__main__":
    import json
    results = [clean_book(b) for b in BOOKS]
    print(json.dumps(results, indent=2))
