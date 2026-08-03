# -*- coding: utf-8 -*-
"""
Clean Project Gutenberg "Anne of Green Gables" (PG #45, L. M. Montgomery) into
plain reading-narrative text, plus the SAME stdlib complexity/composition stats
used for the McGuffey graded-reader ladder (data/corpora/graded_readers_graded/
clean_gutenberg.py compute_stats(), reused verbatim below for direct
comparability -- this is a data-prep + verify pass, not a new mechanism).

Pure stdlib (re, json) -- no LLM / torch / spaCy / NLTK-model involved.
No network at run time: this script expects raw/anne_of_green_gables_45.txt
(already downloaded from https://www.gutenberg.org/cache/epub/45/pg45.txt).

Divergence from the graded-reader cleaner (structural, not a new mechanism):
  - Anne has no LESSON/vocab/apparatus structure. Its native structural unit is
    the CHAPTER heading ("CHAPTER I. Mrs. Rachel Lynde Is Surprised"), which we
    keep as '# CHAPTER n  <title>' markers so downstream chapter-segmented
    analyses (coref density, causal spot-check) have a ground-truth boundary.
  - We strip only the PG license header/footer and the front-matter Table of
    Contents block; the reading prose itself (including dialogue, dashes, and
    curly quotes) is kept VERBATIM -- no content/name/possessive stripping.

Output:
  cleaned/anne_of_green_gables.clean.txt   plain narrative text, chapter markers
  cleaned/anne_of_green_gables.meta.json   provenance + complexity/composition stats
  cleaned/anne_of_green_gables.chapters.json  chapter -> (start_line, end_line, title) in the clean file
"""
import json
import re

BASE = r"d:/AI/hd-instrument/data/corpora/anne_of_green_gables"
RAW = BASE + "/raw"
OUT = BASE + "/cleaned"

BOOK = dict(
    slug="anne_of_green_gables",
    file="anne_of_green_gables_45.txt",
    title="Anne of Green Gables",
    author="L. M. Montgomery",
    pg_id=45,
    reading_level="Natural narrative novel (curriculum rung 2, mid-hard); dense "
                   "same-gender cast + sustained single-arc plot, per "
                   "notes/curriculum_selection_for_self_improving_reader_2026-08-02.md",
)

PG_START = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)
PG_END = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)

CHAPTER_HDR = re.compile(r"^CHAPTER\s+([IVXLC]+)\.\s*(.*)$")
TOC_LINE = re.compile(r"^\s*CHAPTER\s+[IVXLC]+\s+\S")  # ToC rows: "CHAPTER I          Mrs. ..."


def roman_to_int(r):
    vals = dict(I=1, V=5, X=10, L=50, C=100)
    tot, prev = 0, 0
    for ch in reversed(r.upper()):
        v = vals.get(ch, 0)
        tot += -v if v < prev else v
        prev = max(prev, v)
    return tot


def clean_book(b):
    text = open(RAW + "/" + b["file"], encoding="utf-8").read()
    ms, me = PG_START.search(text), PG_END.search(text)
    body = text[ms.end():me.start()] if (ms and me) else text
    lines = body.split("\n")

    # skip the Table-of-Contents block: find the FIRST real chapter header that
    # is NOT immediately followed by another ToC-style row (ToC rows have the
    # title padded on the SAME line with multiple spaces, no period after the
    # roman numeral -- real headers use "CHAPTER I. Title").
    first = None
    for i, l in enumerate(lines):
        if CHAPTER_HDR.match(l.strip()):
            first = i
            break
    if first is None:
        raise SystemExit("no chapter header found")
    reading = lines[first:]

    out = []
    n_chapters = 0
    chapters = []  # list of dict(num, title, start_out_idx)
    for l in reading:
        s = l.strip()
        m = CHAPTER_HDR.match(s)
        if m:
            n_chapters += 1
            num = roman_to_int(m.group(1))
            title = m.group(2).strip()
            marker = "# CHAPTER %d  %s" % (num, title)
            out.append(marker)
            chapters.append(dict(num=num, title=title, start_out_idx=len(out) - 1))
            continue
        out.append(l.rstrip())

    joined = "\n".join(out)
    joined = re.sub(r"\[Illustration:.*?\]", "", joined, flags=re.S)
    clean = re.sub(r"\n{3,}", "\n\n", joined).strip() + "\n"

    with open(OUT + "/" + b["slug"] + ".clean.txt", "w", encoding="utf-8") as f:
        f.write(clean)

    meta = compute_stats(b, clean, n_chapters)
    with open(OUT + "/" + b["slug"] + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    with open(OUT + "/" + b["slug"] + ".chapters.json", "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2)

    return meta


# ---- stats: REUSED VERBATIM from data/corpora/graded_readers_graded/clean_gutenberg.py
# (compute_stats), so numbers are directly comparable to the McGuffey ladder ----
PRONOUNS = {"he", "she", "it", "they", "him", "her", "them", "his",
            "hers", "its", "their", "theirs"}
VERB_HINT = re.compile(r"\b\w+(ed|es|s|ing)\b", re.I)
COMMON_VERBS = {"is", "was", "are", "were", "be", "had", "has", "have", "did",
                "do", "said", "went", "came", "saw", "ran", "made", "took",
                "gave", "told", "found", "put", "got", "felt", "knew", "thought"}


def sentences(text):
    prose = "\n".join(ln for ln in text.split("\n") if not ln.startswith("#"))
    prose = re.sub(r"\s+", " ", prose)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]


def proper_nouns(sents):
    from collections import Counter
    counts = Counter()
    for s in sents:
        toks = re.findall(r"[A-Za-z][A-Za-z'\-]*", s)
        for i, t in enumerate(toks):
            if i > 0 and re.match(r"[A-Z][a-z]", t):
                counts[t] += 1
    return {t for t, c in counts.items()}, counts


def has_entity(s, pnset):
    toks = re.findall(r"[A-Za-z][A-Za-z'\-]*", s)
    if any(t in pnset for t in toks):
        return True
    if any(t.lower() in PRONOUNS for t in toks):
        return True
    return False


def has_verb(s):
    toks = [t.lower() for t in re.findall(r"[A-Za-z']+", s)]
    return any(t in COMMON_VERBS for t in toks) or bool(VERB_HINT.search(s))


def compute_stats(b, clean, n_chapters):
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", "\n".join(
        ln for ln in clean.split("\n") if not ln.startswith("#")))
    types = sorted(set(w.lower() for w in words))
    sents = sentences(clean)
    slen = [len(re.findall(r"[A-Za-z']+", s)) for s in sents]
    slen = [x for x in slen if x > 0]
    n = len(slen)
    mean_sl = round(sum(slen) / n, 2) if n else 0
    med_sl = sorted(slen)[n // 2] if n else 0

    CONN = re.compile(r"\b(and|but|which|that|because|when|while|though|although|"
                      r"if|as|so|for|or|nor|yet|who|whom|whose|where)\b", re.I)
    conn_counts = [len(CONN.findall(s)) + s.count(",") for s in sents]
    pct_simple = round(100 * sum(1 for c in conn_counts if c <= 1) / n, 1) if n else 0
    pct_short = round(100 * sum(1 for x in slen if x <= 15) / n, 1) if n else 0

    pnset, pncounts = proper_nouns(sents)
    recurring = {t for t, c in pncounts.items() if c >= 2}
    ent_verb = [has_entity(s, pnset) and has_verb(s) for s in sents]
    comp_pairs = 0
    for i in range(len(sents) - 1):
        if not (ent_verb[i] and ent_verb[i + 1]):
            continue
        toks1 = set(re.findall(r"[A-Za-z][A-Za-z'\-]*", sents[i]))
        toks2 = set(re.findall(r"[A-Za-z][A-Za-z'\-]*", sents[i + 1]))
        shares_name = bool((toks1 & toks2) & recurring)
        cont_pron = any(t.lower() in PRONOUNS for t in toks2)
        if shares_name or cont_pron:
            comp_pairs += 1
    comp_density = round(comp_pairs / (n - 1), 3) if n > 1 else 0

    pn_density = round(100 * sum(pncounts.values()) / len(words), 2) if words else 0
    pron_toks = sum(1 for w in words if w.lower() in PRONOUNS)
    pron_density = round(100 * pron_toks / len(words), 2) if words else 0

    return dict(
        title=b["title"], author=b["author"],
        source=f"Project Gutenberg eBook #{b['pg_id']} (https://www.gutenberg.org/ebooks/{b['pg_id']})",
        license="Public domain (US) -- Project Gutenberg; PG trademark applies only to the "
                "packaged header/footer, which we strip",
        reading_level=b["reading_level"],
        n_words=len(words), n_word_types=len(types), n_chapters=n_chapters,
        n_sentences_approx=n,
        mean_sentence_len=mean_sl, median_sentence_len=med_sl,
        max_sentence_len=max(slen) if slen else 0,
        pct_sentences_le15w=pct_short,
        pct_sentences_simple_le1connector=pct_simple,
        proper_noun_density_per100w=pn_density,
        pronoun_density_per100w=pron_density,
        n_recurring_names=len(recurring),
        composition_density_est=comp_density,
    )


if __name__ == "__main__":
    m = clean_book(BOOK)
    print(json.dumps(m, indent=2))
