#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Foundation-build: emit a GENERAL first-name -> gender gazetteer.

SOURCE: NLTK 'names' corpus (Mark Kantrowitz / Bill Ross name list, ~8k first
names split male.txt / female.txt). GENERAL resource; NOT derived from any
LitBank book character list (anti-circular: the reading eval is held out).

RULE (unambiguous only = never-confidently-wrong): a name is emitted with gender
'masc' iff it appears ONLY in male.txt, 'fem' iff ONLY in female.txt. Names in
BOTH lists (ambiguous, e.g. George/Angel/Dorian) or NEITHER are OMITTED -> the
gazetteer ABSTAINS on them (no gender assigned -> agreement filter stays open).

OUTPUT: data/lexicons/name_gender_gazetteer.tsv  (lowercased name<TAB>gender),
sorted, ASCII-only, LF newlines. Committed so the reader is self-contained +
offline (no runtime nltk dependency) + deterministic + portable to remote.

Provenance/generality is documented in the file header so downstream VET can
confirm the anti-circular property without re-running.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "data", "lexicons")
OUT_PATH = os.path.join(OUT_DIR, "name_gender_gazetteer.tsv")


def main():
    from nltk.corpus import names  # local corpus; build-time only
    male = set(w.strip().lower() for w in names.words("male.txt") if w.strip())
    female = set(w.strip().lower() for w in names.words("female.txt") if w.strip())
    both = male & female
    masc = sorted(male - female)
    fem = sorted(female - male)
    rows = [(n, "masc") for n in masc] + [(n, "fem") for n in fem]
    rows.sort()
    # ASCII-only guard (a couple of accented names may appear; drop them so the
    # committed artifact is strictly ASCII per project convention).
    rows = [(n, g) for (n, g) in rows if all(ord(c) < 128 for c in n)]
    os.makedirs(OUT_DIR, exist_ok=True)
    header = [
        "# name_gender_gazetteer.tsv",
        "# GENERAL first-name -> gender gazetteer (foundation artifact).",
        "# SOURCE: NLTK 'names' corpus (Kantrowitz/Ross); build-time only.",
        "# RULE: name in ONLY male.txt -> masc; ONLY female.txt -> fem;",
        "#       names in BOTH (ambiguous) or NEITHER are OMITTED (abstain).",
        "# ANTI-CIRCULAR: general name list; NOT built from LitBank characters.",
        "# columns: name<TAB>gender   (name lowercased ASCII)",
        "# counts: male_only=%d female_only=%d ambiguous_omitted=%d"
        % (len(masc), len(fem), len(both)),
    ]
    with open(OUT_PATH, "w", encoding="ascii", newline="\n") as f:
        for h in header:
            f.write(h + "\n")
        for n, g in rows:
            f.write("%s\t%s\n" % (n, g))
    print("wrote %d entries (masc=%d fem=%d, ambiguous_omitted=%d) -> %s"
          % (len(rows), len(masc), len(fem), len(both), OUT_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
