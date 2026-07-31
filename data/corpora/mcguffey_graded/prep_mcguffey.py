#!/usr/bin/env python3
"""Clean + segment + characterize McGuffey's Eclectic Readers (grades 1-6).

DATA PREP (not an experiment). Public-domain source (Project Gutenberg).
Turns raw g{1..6}_*.txt into ordered clean reading passages per grade, verifies
the grading is genuinely monotonic (difficulty curve), and reports tokenizer
coverage against our v2 16K BPE (from the ARC checkpoint). ASCII-only outputs,
atomic writes, no bare/Base except.
"""
import os
import re
import io
import sys
import json
import math
import unicodedata
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CORP = os.path.join(REPO, "data", "corpora", "mcguffey_graded")
CLEAN = os.path.join(CORP, "clean")
CKPT = os.path.join(REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")

GRADES = [
    ("g1", "g1_first.txt"),
    ("g2", "g2_second.txt"),
    ("g3", "g3_third.txt"),
    ("g4", "g4_fourth.txt"),
    ("g5", "g5_fifth.txt"),
    ("g6", "g6_sixth.txt"),
]

# ---- 1. ASCII normalization -------------------------------------------------
_UNI = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "—": "--", "–": "-", "…": "...", "•": " ",
    "™": " ", " ": " ",
}


def to_ascii(text):
    for k, v in _UNI.items():
        text = text.replace(k, v)
    # fold remaining accented latin (cafe' etc) to nearest ascii
    text = unicodedata.normalize("NFKD", text)
    out = []
    for ch in text:
        o = ord(ch)
        if o < 128:
            out.append(ch)
        elif unicodedata.combining(ch):
            continue  # drop combining marks left by NFKD
        else:
            out.append(" ")
    return "".join(out)


# ---- 2. slice PG body -------------------------------------------------------
# Per-grade front-matter cutoff: reading proper begins at the first line
# matching this regex.  Everything before it (PG boilerplate, preface, alphabet,
# teaching-method notes, punctuation/articulation/elocution apparatus, TOCs,
# author lists, ad catalogs) is front matter and is dropped.  These markers are
# specific to this fixed 6-file public-domain corpus and are documented here.
FRONT_CUT = {
    "g1": re.compile(r"^\s*LESSON\s+I\."),
    "g2": re.compile(r"^\s*LESSON\s+I\."),
    "g3": re.compile(r"^\s*LESSON\s+I\."),
    "g4": re.compile(r"^\s*MCGUFFEY'S FOURTH READER\."),
    "g5": re.compile(r"^\s*McGuffey's Fifth Reader\s*$"),
    "g6": re.compile(r"^\s*MCGUFFEY'S SIXTH READER\. \(63\)"),
}


def slice_body(text, gid):
    lines = text.split("\n")
    lo, hi = 0, len(lines)
    for i, ln in enumerate(lines):
        if "START OF THE PROJECT GUTENBERG" in ln:
            lo = i + 1
        if "END OF THE PROJECT GUTENBERG" in ln:
            hi = i
            break
    body = lines[lo:hi]
    cut = FRONT_CUT.get(gid)
    if cut is not None:
        for j, ln in enumerate(body):
            if cut.match(ln):
                return body[j + 1:]  # drop the heading marker line itself
    return body


# ---- 3. apparatus filters ---------------------------------------------------
# Header lines that begin a non-reading (apparatus) section.  Once one is seen,
# the block is dropped up to the next blank line (blocks are blank-separated).
APPARATUS_HEADER = re.compile(
    r"^\s*("
    r"DEFINITIONS|NOTE[S]?\b|REMARK|EXERCISE[S]?|QUESTION[S]?|ARTICULATION|"
    r"ELEMENTARY|SLATE|TABLE OF|EXAMPLE[S]?\b|CORRECT\b|INCORRECT\b|"
    r"SUBVOCAL|ASPIRATE|SUBSTITUTE[S]?|FAULT[S]?|PUNCTUATION|ALPHABET|"
    r"PREFACE|INTRODUCTOR|LIST OF|ALPHABETICAL|SELECTIONS IN|CONTENTS|"
    r"ECLECTIC|COPYRIGHT|CINCINNATI|ACCENT|INFLECTION|VOCABULAR|CHART|"
    r"THE ALPHABET|SCRIPT|ORAL|SPELL"
    r")",
    re.IGNORECASE,
)
# a line that is purely a section title / heading in ALL CAPS
CAPS_HEAD = re.compile(r"^[^a-z]*[A-Z][^a-z]*$")
# elocution accent mark: word ending in a lone apostrophe (charge', on', voluntarily')
ACCENT_TRAIL = re.compile(r"[A-Za-z]{2,}'(?=[\s,.;:!?)\"]|$)")
# syllabified glossary headword: hyphen+apostrophe cluster (gran'a-ry, En-tan'gled)
SYLL = re.compile(r"[A-Za-z]*'[A-Za-z]*-|-[A-Za-z]*'|[A-Za-z]+-[A-Za-z]+-[A-Za-z]")
# mid-word pronunciation accent (oth'er, pe-ti'tion) but NOT contractions/possessives
_CONTR = re.compile(r"'(s|t|ll|re|ve|d|m|clock|em|n|tis|twas)\b", re.IGNORECASE)
_MIDAP = re.compile(r"[A-Za-z]'[A-Za-z]")


def has_pron_accent(s):
    return bool(_MIDAP.search(_CONTR.sub("", s)))
# lesson/selection/roman headers
LESSON_HEAD = re.compile(r"^\s*(LESSON|SELECTION|CHAPTER)\b", re.IGNORECASE)
ROMAN_ONLY = re.compile(r"^\s*[IVXLCDM]+\.?\s*$")
PAGE_MARK = re.compile(r"^\s*\(?\s*[ivxlcdm0-9]+\s*\)?\.?\s*$", re.IGNORECASE)
# leading enumerator to strip from a kept reading line ("1. ", "IV. ")
LEAD_NUM = re.compile(r"^\s*(\d{1,3}|[IVXLC]{1,6})\.\s+")
TRAIL_PAGE = re.compile(r"\s*\(\d{1,3}\)\s*$")  # trailing page ref like " (7)"


def is_apparatus_line(ln):
    s = ln.strip()
    if not s:
        return False
    if APPARATUS_HEADER.match(s):
        return True
    if LESSON_HEAD.match(s):
        return True
    if ROMAN_ONLY.match(s):
        return True
    if PAGE_MARK.match(s):
        return True
    if ACCENT_TRAIL.search(s):
        return True
    if SYLL.search(s):
        return True
    if has_pron_accent(s):
        return True
    # copyright / catalog codes: EP486, M'G 4TH REV, ISBN-ish
    if re.match(r"^\s*(EP\s?\d|M'?G\b|COPYRIGHT|Copyright)", s):
        return True
    # all-caps heading with few words (title / running head)
    letters = [c for c in s if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.85 and len(s.split()) <= 8:
        return True
    # columnar vocabulary list (words separated by 2+ spaces, no sentence punct)
    has_punct = re.search(r"[.?!,;:]", s)
    cols = re.split(r"\s{2,}", s)
    if len(cols) >= 3 and not has_punct:
        return True
    # phonics / short-word vocab line (>=3 short tokens, no punctuation)
    toks = s.split()
    if len(toks) >= 3 and not has_punct and all(len(t) <= 5 for t in toks):
        return True
    return False


def clean_grade(raw, gid):
    """Return list of passages; each passage = list of sentence strings."""
    body = slice_body(raw, gid)
    # remove bracket blocks ([Illustration ...], [Transcriber ...]) via depth
    depth = 0
    kept = []
    skip_block = False
    for ln in body:
        # bracket depth spanning multiple lines
        opens, closes = ln.count("["), ln.count("]")
        if depth > 0 or "[" in ln:
            depth += opens - closes
            if depth < 0:
                depth = 0
            continue
        stripped = ln.strip()
        if stripped == "":
            skip_block = False
            kept.append("")  # preserve paragraph breaks
            continue
        if skip_block:
            continue
        if is_apparatus_line(ln):
            skip_block = True  # drop rest of this blank-delimited block too
            continue
        # strip leading enumerator and trailing page ref
        ln2 = LEAD_NUM.sub("", ln)
        ln2 = TRAIL_PAGE.sub("", ln2)
        kept.append(ln2.rstrip())

    # rebuild paragraphs (blank-line separated), then sentence-split
    text = "\n".join(kept)
    paras = re.split(r"\n\s*\n", text)
    passages = []
    for p in paras:
        joined = " ".join(x.strip() for x in p.split("\n") if x.strip())
        joined = re.sub(r"\s+", " ", joined).strip()
        if not joined:
            continue
        # sentence split on . ? ! (keep terminators)
        sents = re.split(r"(?<=[.?!])\s+", joined)
        good = []
        for s in sents:
            s = s.strip()
            words = re.findall(r"[A-Za-z]+", s)
            # keep prose sentences (>=3 words w/ terminal punct) OR verse lines
            # (>=4 words; verse fragments split by page-headers lack terminal .?!)
            if not re.search(r"[.?!]", s):
                if len(words) < 4:
                    continue
            elif len(words) < 3:
                continue
            # reject residual all-caps
            letters = [c for c in s if c.isalpha()]
            if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:
                continue
            good.append(s)
        if good:
            passages.append(good)
    return passages


# ---- 4. difficulty metrics --------------------------------------------------
VOWELS = "aeiouy"


def syllable_estimate(word):
    w = word.lower()
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


def grade_metrics(passages):
    words = []
    sent_lens = []
    long_words = 0
    total_syll = 0
    for psg in passages:
        for s in psg:
            wtoks = re.findall(r"[A-Za-z]+", s)
            if not wtoks:
                continue
            sent_lens.append(len(wtoks))
            for w in wtoks:
                words.append(w.lower())
                if len(w) >= 7:
                    long_words += 1
                total_syll += syllable_estimate(w)
    n_words = len(words)
    n_sent = len(sent_lens)
    types = set(words)
    counts = Counter(words)
    hapax = sum(1 for w, c in counts.items() if c == 1)
    mean_sl = (n_words / n_sent) if n_sent else 0.0
    ttr = (len(types) / n_words) if n_words else 0.0
    # Flesch-Kincaid grade level (readability, higher = harder)
    fk = (0.39 * mean_sl + 11.8 * (total_syll / n_words) - 15.59) if n_words else 0.0
    return {
        "n_passages": len(passages),
        "n_sentences": n_sent,
        "n_words": n_words,
        "n_types": len(types),
        "mean_sentence_len": round(mean_sl, 2),
        "type_token_ratio": round(ttr, 4),
        "hapax_frac": round(hapax / n_words, 4) if n_words else 0.0,
        "pct_long_words_ge7": round(100.0 * long_words / n_words, 2) if n_words else 0.0,
        "mean_syllables_per_word": round(total_syll / n_words, 3) if n_words else 0.0,
        "flesch_kincaid_grade": round(fk, 2),
    }


# ---- 5. tokenizer coverage --------------------------------------------------
def load_tokenizer():
    import torch
    from tokenizers import Tokenizer
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    return Tokenizer.from_str(ck["tokenizer_json"])


def tokenizer_coverage(passages, tk):
    n_words = 0
    n_subword_pieces = 0
    n_unk = 0
    n_multi = 0  # words that split into >=2 pieces
    for psg in passages:
        for s in psg:
            for w in re.findall(r"[A-Za-z']+", s):
                wl = w.lower()
                enc = tk.encode(wl)
                toks = enc.tokens
                if not toks:
                    continue
                n_words += 1
                n_subword_pieces += len(toks)
                if len(toks) >= 2:
                    n_multi += 1
                if any(t == "[UNK]" for t in toks):
                    n_unk += 1
    return {
        "n_words_scored": n_words,
        "pieces_per_word": round(n_subword_pieces / n_words, 3) if n_words else 0.0,
        "pct_words_fragmented": round(100.0 * n_multi / n_words, 2) if n_words else 0.0,
        "pct_words_with_unk": round(100.0 * n_unk / n_words, 3) if n_words else 0.0,
    }


# ---- 6. atomic write --------------------------------------------------------
def atomic_write(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="ascii", newline="\n") as f:
        f.write(data)
    os.replace(tmp, path)


def main():
    os.makedirs(CLEAN, exist_ok=True)
    tk = load_tokenizer()
    report = {"grades": {}, "difficulty_curve": {}, "coverage_curve": {}}
    manifest = {"corpus": "mcguffey_graded", "order": [], "grades": {}}
    words_by_grade = {}
    for gid, fn in GRADES:
        raw = to_ascii(io.open(os.path.join(CORP, fn), encoding="utf-8").read())
        passages = clean_grade(raw, gid)
        words_by_grade[gid] = [w.lower() for psg in passages for s in psg
                               for w in re.findall(r"[A-Za-z]+", s)]
        # write clean passages: one passage per block, blank-line separated
        blocks = []
        for psg in passages:
            blocks.append(" ".join(psg))
        clean_txt = "\n\n".join(blocks) + "\n"
        outpath = os.path.join(CLEAN, gid + ".txt")
        atomic_write(outpath, clean_txt)
        m = grade_metrics(passages)
        cov = tokenizer_coverage(passages, tk)
        report["grades"][gid] = {"metrics": m, "coverage": cov, "source": fn}
        manifest["order"].append(gid)
        manifest["grades"][gid] = {
            "clean_file": os.path.relpath(outpath, REPO).replace("\\", "/"),
            "n_passages": m["n_passages"],
            "n_words": m["n_words"],
        }
        print("[%s] passages=%d sents=%d words=%d mean_sl=%.2f ttr=%.4f "
              "long%%=%.2f fk=%.2f | pieces/word=%.3f frag%%=%.2f unk%%=%.3f"
              % (gid, m["n_passages"], m["n_sentences"], m["n_words"],
                 m["mean_sentence_len"], m["type_token_ratio"],
                 m["pct_long_words_ge7"], m["flesch_kincaid_grade"],
                 cov["pieces_per_word"], cov["pct_words_fragmented"],
                 cov["pct_words_with_unk"]))

    # monotonicity check on primary difficulty signals
    keys = [g for g, _ in GRADES]
    def series(metric):
        return [report["grades"][g]["metrics"][metric] for g in keys]
    for metric in ["mean_sentence_len", "pct_long_words_ge7",
                   "mean_syllables_per_word", "flesch_kincaid_grade"]:
        s = series(metric)
        incr = all(s[i + 1] >= s[i] for i in range(len(s) - 1))
        # count monotone-violating adjacent steps
        viol = [keys[i + 1] for i in range(len(s) - 1) if s[i + 1] < s[i]]
        report["difficulty_curve"][metric] = {
            "series": s, "strictly_nondecreasing": incr, "violations_at": viol,
        }
    report["coverage_curve"] = {
        g: report["grades"][g]["coverage"] for g in keys
    }
    # independent grading confirmation: a naive grade-1-vocabulary reader should
    # cover progressively LESS of each higher grade (genuine new signal per grade,
    # not more-of-the-same), and each grade should keep introducing new words.
    g1vocab = set(words_by_grade[keys[0]])
    simple_cov, new_rate, cum = [], [], set()
    for g in keys:
        toks = words_by_grade[g]
        n = len(toks)
        simple_cov.append(round(100.0 * sum(1 for w in toks if w in g1vocab) / n, 2) if n else 0.0)
        new_rate.append(round(100.0 * sum(1 for w in toks if w not in cum) / n, 2) if n else 0.0)
        cum |= set(toks)
    report["grading_confirmation"] = {
        "grade1_vocab_reader_coverage_pct": {
            "series": simple_cov,
            "strictly_nonincreasing": all(simple_cov[i + 1] <= simple_cov[i] for i in range(len(simple_cov) - 1)),
            "note": "naive grade-1-vocabulary reader; falling series = harder grades genuinely need new vocab",
        },
        "new_word_introduction_rate_pct": {
            "series": new_rate,
            "note": "pct of tokens whose word is unseen in all lower grades",
        },
    }
    atomic_write(os.path.join(CORP, "grading_report.json"),
                 json.dumps(report, indent=2))
    atomic_write(os.path.join(CORP, "manifest.json"),
                 json.dumps(manifest, indent=2))
    print("\nWROTE", os.path.join(CORP, "grading_report.json"))
    print("WROTE", os.path.join(CORP, "manifest.json"))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("PREP_FAILED:", type(e).__name__, str(e)[:500], file=sys.stderr)
        raise
