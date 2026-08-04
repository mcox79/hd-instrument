# -*- coding: utf-8 -*-
"""
Clean 2 public-domain Project Gutenberg Sherlock Holmes short-story
collections into plain reading text, for the detective-fiction cross-span
causal-attribution transfer probe (data/eval_gold_mention_role_mcguffey_v1/
gold_causal_crossspan_detective_v3_DRAFT.jsonl). Same strip-boilerplate
approach as data/corpora/clean_gutenberg_multi_v1.py (PG_START/PG_END
markers). Pure stdlib (re). No network at run time -- raw/*.txt already
downloaded verbatim from gutenberg.org (public domain in the US; PG
trademark applies only to the packaged header/footer, stripped here).

Books (slug, pg_id, raw filename, title, author):
  adventures  1661  The Adventures of Sherlock Holmes   Arthur Conan Doyle
  memoirs      834  The Memoirs of Sherlock Holmes      Arthur Conan Doyle

Output per book: data/corpora/sherlock_holmes/cleaned/<slug>.clean.txt
"""
import os
import re

BASE = r"d:/AI/hd-instrument/data/corpora/sherlock_holmes"

BOOKS = [
    dict(slug="adventures", pg_id=1661, file="adventures_1661.txt",
         title="The Adventures of Sherlock Holmes", author="Arthur Conan Doyle"),
    dict(slug="memoirs", pg_id=834, file="memoirs_834.txt",
         title="The Memoirs of Sherlock Holmes", author="Arthur Conan Doyle"),
]

PG_START = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)


def clean_book(b):
    raw_path = os.path.join(BASE, "raw", b["file"])
    with open(raw_path, encoding="utf-8") as f:
        text = f.read()
    ms, me = PG_START.search(text), PG_END.search(text)
    body = text[ms.end():me.start()] if (ms and me) else text
    body = re.sub(r"\[Illustration.*?\]", "", body, flags=re.S)
    body = re.sub(r"\r\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

    out_dir = os.path.join(BASE, "cleaned")
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
