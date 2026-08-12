"""Build breadth_corpus_v1: a drop-in, ARC-format-matching general-text corpus
assembled from genuinely-broad text ALREADY on disk (no downloads).

Format matches experiments/exp_scale_meaning_learn_arc_heldout_v2.py's expectations:
one line = one sentence/passage unit, mixed case, punctuation intact, UTF-8.
Same quality gate reused verbatim: >=4 alpha-words, alpha-char-ratio >= 0.55,
no bibliographic-citation-fragment lines (_CITATION_RE).

Sources (all on-disk, no acquisition step):
  1. WordNet glosses (data/wordnet_gloss_cache_v1.json) - 25,312 concept definitions,
     broad conceptual coverage (not science-skewed).
  2. OneStopEnglish raw articles (data/corpora/onestop/Texts-SeparatedByReadingLevel) -
     news-register prose at 3 reading levels, 189 articles x 3 levels.
     NOTE: `du` reports this dir at ~1.6GB; TRUE file-content bytes measured this
     session = ~2.4MB (du inflated ~670x by this filesystem's per-file allocation
     overhead across 2656 small files). Corrected inventory number, not the du figure.
  3. LitBank coref-annotated novels (data/corpora/litbank_coref_conll) - 25 annotated
     public-domain novels (Dracula, Persuasion, Tess of the d'Urbervilles, Bleak House,
     etc.), reconstructed from CoNLL token columns. Narrative register (coref/event
     structure), Gutenberg-clean.
  4. RACE reading-comprehension articles (data/corpora/race/*.jsonl) - English exam
     passages, broad topics, narrative+expository mixed register.
  5. Wikipedia smoke sample (data/datasets/wikipedia_smoke_500.jsonl) - 500 modern
     Wikipedia articles, well-formed (has sentence/case structure unlike text8).
  6. McGuffey / graded readers (data/corpora/graded_readers_grade1/cleaned,
     data/corpora/graded_readers_graded/cleaned, data/corpora/mcguffey_readers) -
     19th-c. children's readers, narrative/moral-story register, Gutenberg-boilerplate
     stripped where a cleaned/ variant exists, heuristically stripped otherwise.
  7. UD English EWT sentences (data/corpora/ud_english_ewt/*.conllu) - "# text = "
     lines: weblogs, emails, reviews, newsgroups - informal web register, genuinely
     different from ARC's expository-science register.

Explicitly EXCLUDED after inspection (see report):
  - data/corpora/agreement/ - synthetic word-substituted probe sentences
    ("An agreeable insight executed in fifty surrounds there add billion...");
    not coherent natural text.
  - data/corpora/worldtree/ - science explanation sentences, same register as
    ARC (not breadth).
  - data/corpora/textbook_concepts_biology/ - science register, not breadth.
  - data/corpora/binder/, base_vocabulary/, word_image_early_vocab/ - feature
    norms / word lists, not prose.
  - text8 - flagged in the scoping note as degenerate (lowercased, no punctuation,
    no sentence boundaries); left OUT of this mixed prose corpus (format-incompatible
    with the line=sentence convention) but still usable as a separate arm if wanted.

Run: python tools/build_breadth_corpus_v1.py
Output: data/corpora/breadth_v1/breadth_corpus_v1.txt (+ MANIFEST.md, stats.json)
"""
import glob
import json
import os
import re
import sys
import unicodedata

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_REPO, "data")
OUT_DIR = os.path.join(DATA, "corpora", "breadth_v1")
OUT_TXT = os.path.join(OUT_DIR, "breadth_corpus_v1.txt")
OUT_MANIFEST = os.path.join(OUT_DIR, "MANIFEST.md")
OUT_STATS = os.path.join(OUT_DIR, "stats.json")

_WORD_RE = re.compile(r"[a-z]+")
_CITATION_RE = re.compile(r"\b\d+\s*\(\s*\d+\s*\)\s*:\s*\d+")
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“])")
_WS_RE = re.compile(r"\s+")

_ASCII_MAP = {
    0x2018: "'", 0x2019: "'", 0x201A: "'", 0x201B: "'",
    0x201C: '"', 0x201D: '"', 0x201E: '"', 0x201F: '"',
    0x2013: "-", 0x2014: "-", 0x2015: "-", 0x2212: "-",
    0x2026: "...", 0x00A0: " ", 0x2009: " ", 0x200B: "",
    0x00AB: '"', 0x00BB: '"',
}


def to_ascii(s):
    s = s.translate(_ASCII_MAP)
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    return s


def quality_ok(line, words):
    if len(words) < 4:
        return False
    n_alpha = sum(len(w) for w in words)
    n_all = len(line)
    if n_all > 0 and (n_alpha / float(n_all)) < 0.55:
        return False
    if _CITATION_RE.search(line):
        return False
    return True


def clean_line(raw):
    line = to_ascii(raw)
    line = _WS_RE.sub(" ", line).strip()
    return line


def emit(line, out, seen, stats, source):
    line = clean_line(line)
    if not line:
        return
    words = _WORD_RE.findall(line.lower())
    if not quality_ok(line, words):
        stats[source]["dropped_quality"] += 1
        return
    h = hash(line)
    if h in seen:
        stats[source]["dropped_dup"] += 1
        return
    seen.add(h)
    out.write(line + "\n")
    stats[source]["lines"] += 1
    stats[source]["tokens"] += len(words)


def sentences_from_text(text):
    text = text.replace("\r", " ")
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    for p in paras:
        for s in _SENT_SPLIT_RE.split(p):
            s = s.strip()
            if s:
                yield s


PG_BOILER_RE = re.compile(
    r"project gutenberg|www\.gutenberg|\*\*\* ?(start|end) of|ebook is for the use|"
    r"gutenberg license|gutenberg-tm|produced by |transcriber",
    re.IGNORECASE)


def strip_pg_boilerplate(text):
    lines = text.split("\n")
    keep = [l for l in lines if not PG_BOILER_RE.search(l)]
    return "\n".join(keep)


# ---------------------------------------------------------------------------
# Source extractors: each yields raw sentence strings
# ---------------------------------------------------------------------------
def src_wordnet_glosses():
    path = os.path.join(DATA, "wordnet_gloss_cache_v1.json")
    if not os.path.exists(path):
        return
    d = json.load(open(path, encoding="utf-8"))
    for surface, gloss in d.items():
        surface = surface.replace("_", " ")
        yield f"{surface} : {gloss}"


def src_onestop():
    base = os.path.join(DATA, "corpora", "onestop", "Texts-SeparatedByReadingLevel")
    if not os.path.isdir(base):
        return
    for path in glob.glob(os.path.join(base, "*", "*.txt")):
        try:
            text = open(path, encoding="utf-8-sig", errors="ignore").read()
        except OSError:
            continue
        yield from sentences_from_text(text)


def src_litbank():
    base = os.path.join(DATA, "corpora", "litbank_coref_conll")
    if not os.path.isdir(base):
        return
    for path in glob.glob(os.path.join(base, "*.conll")):
        try:
            lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
        except OSError:
            continue
        toks = []
        for ln in lines:
            if not ln.strip():
                if toks:
                    yield " ".join(toks)
                    toks = []
                continue
            if ln.startswith("#"):
                continue
            parts = ln.split("\t")
            if len(parts) > 3 and parts[3] not in ("_", ""):
                toks.append(parts[3])
        if toks:
            yield " ".join(toks)


def src_race():
    for name in ("middle_test.jsonl", "high_test.jsonl"):
        path = os.path.join(DATA, "corpora", "race", name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="ignore") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    obj = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                article = obj.get("article", "")
                yield from sentences_from_text(article)


def src_wikipedia_smoke():
    path = os.path.join(DATA, "datasets", "wikipedia_smoke_500.jsonl")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
            except json.JSONDecodeError:
                continue
            text = obj.get("text", "")
            yield from sentences_from_text(text)


def src_graded_readers():
    cleaned_dirs = [
        os.path.join(DATA, "corpora", "graded_readers_grade1", "cleaned"),
        os.path.join(DATA, "corpora", "graded_readers_graded", "cleaned"),
    ]
    seen_stems = set()
    for d in cleaned_dirs:
        if not os.path.isdir(d):
            continue
        for path in glob.glob(os.path.join(d, "*.clean.txt")):
            seen_stems.add(os.path.basename(path).split(".")[0])
            text = open(path, encoding="utf-8", errors="ignore").read()
            text = strip_pg_boilerplate(text)
            yield from sentences_from_text(text)
    # mcguffey_readers/ raw dir: include readers not covered by a cleaned/ variant
    # (5th, 6th) -- dedup against cleaned stems by filename stem match.
    mg = os.path.join(DATA, "corpora", "mcguffey_readers")
    if os.path.isdir(mg):
        for path in glob.glob(os.path.join(mg, "*.txt")):
            stem = os.path.basename(path)
            if any(tag in stem for tag in ("primer", "1_first", "2_second", "3_third", "4_fourth")):
                continue  # already covered by cleaned/ variants above
            text = open(path, encoding="utf-8", errors="ignore").read()
            text = strip_pg_boilerplate(text)
            yield from sentences_from_text(text)


def src_ud_ewt():
    base = os.path.join(DATA, "corpora", "ud_english_ewt")
    for name in ("en_ewt-ud-train.conllu", "en_ewt-ud-test.conllu"):
        path = os.path.join(base, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="ignore") as f:
            for ln in f:
                if ln.startswith("# text = "):
                    yield ln[len("# text = "):].strip()


SOURCES = [
    ("wordnet_glosses", src_wordnet_glosses),
    ("onestop", src_onestop),
    ("litbank", src_litbank),
    ("race", src_race),
    ("wikipedia_smoke_500", src_wikipedia_smoke),
    ("graded_readers_mcguffey", src_graded_readers),
    ("ud_english_ewt", src_ud_ewt),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    seen = set()
    stats = {name: dict(lines=0, tokens=0, dropped_quality=0, dropped_dup=0) for name, _ in SOURCES}
    with open(OUT_TXT, "w", encoding="utf-8", newline="\n") as out:
        for name, fn in SOURCES:
            n_before = out.tell()
            for line in fn():
                emit(line, out, seen, stats, name)
            print(f"[{name}] lines={stats[name]['lines']} tokens={stats[name]['tokens']} "
                  f"dropped_quality={stats[name]['dropped_quality']} dropped_dup={stats[name]['dropped_dup']}",
                  file=sys.stderr)

    total_lines = sum(s["lines"] for s in stats.values())
    total_tokens = sum(s["tokens"] for s in stats.values())
    out_bytes = os.path.getsize(OUT_TXT)
    summary = dict(sources=stats, total_lines=total_lines, total_tokens=total_tokens,
                   output_bytes=out_bytes, output_path=OUT_TXT)
    with open(OUT_STATS, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
