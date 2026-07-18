# CELL: read_grow_textbook_isa_growth_v1
# QUESTION: Does ingesting a full textbook GROW a useful glass-box knowledge foundation?
#   As more of the book is read (section by section), does the accumulated foundation
#   correctly answer more HELD-OUT is-a relation queries, and does that KEEP GOING
#   (non-plateau) rather than saturate -- AND beat a non-accumulating + a frequency baseline?
#
# GLASS-BOX (no runtime LLM): NLTK PerceptronTagger POS + WordNetLemmatizer + WordNet + regex/symbolic
#   Hearst lexico-syntactic is-a patterns. NO spaCy-default / Stanza / torch / transformers.
#
# DESIGN (design-gate compliant):
#   SOURCE   = textbook PROSE (glossary blocks stripped out and reserved as gold).
#   GOLD     = ~1000 glossary (term -> genus-head) is-a pairs (genus-differentia definitions).
#   HELD-OUT = every 5th glossary-bearing section (~20%): its PROSE is NEVER read; its glossary
#              is pure held-out eval -> coverage must come from CROSS-SECTION prose mentions
#              (genuine generalization, NOT memorization of the just-read definition).
#   ARMS (one variable = accumulation on/off):
#     (1) ACCUMULATING foundation across read-pool sections
#     (2) NON-ACCUMULATING (current-section-only, no memory)
#     (3) FREQUENCY majority-genus baseline (predict globally-most-common genus for every term)
#   METRIC = held-out correct-coverage (term answered with correct genus) vs #read-pool-sections.
#   CAN-FAIL: HARD_FAIL if the growth curve PLATEAUS early OR accumulation gives no benefit.
#            A genuine 'grow-from-reading plateaus at scale' is a FIRST-CLASS result -- reported honestly.
#
# CELL-TEMPLATE MANDATORY:
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - deterministic seeding only (FIXED int / stable index; no built-in hash() / list(set()))
# - all bands tagged HYPOTHESIZED@ (pre-reg) then confirmed MEASURED@ at smoke/full
#
# Compute architecture: (b) sequential-CPU. Justification: pure regex / POS-tagging / WordNet /
#   symbolic dict accumulation. No matmul, no substrate vectors. Diagnostic growth-curve cell
#   (compute-proportionality: cheapest decisive method for a does-it-grow question). Wall < few min.

import os
import re
import sys
import json
import time
import argparse
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import nltk
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

ANCHOR_NAME = "read_grow_textbook_isa_growth_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(
    REPO, "data", "corpora", "textbook_concepts_biology", "cleaned",
    "concepts_biology.clean.txt",
)

# ----------------------------- error-checking scaffolds -----------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "{}: {}".format(type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: {}".format(type(exc).__name__),
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ----------------------------- linguistics helpers -----------------------------

_LEM = WordNetLemmatizer()
_NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
_ADJ_TAGS = {"JJ", "JJR", "JJS"}
_SKIP_LEAD = {"DT", "PDT", "CD", "RB", "RBR", "RBS", "PRP$"} | _ADJ_TAGS
_QUANTIFIERS = {"all", "any", "some", "each", "every", "most", "many", "several",
                "certain", "various", "one", "two", "both", "either", "no", "the",
                "a", "an", "this", "that", "these", "those"}
_TYPE_WORDS = {"type", "kind", "form", "sort", "group", "class", "category", "variety",
               "example", "member", "set", "collection"}
_PRON = {"it", "they", "this", "these", "those", "there", "he", "she", "we", "you",
         "i", "who", "which", "that", "what", "one", "some", "many", "all"}
_BE = {"is", "are", "was", "were"}
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*|[.,;:()]")

# WordNet-relatedness cache (deterministic)
_WN_CACHE = {}


def _tokenize(text):
    return _TOKEN_RE.findall(text)


def _lemma_noun(word):
    return _LEM.lemmatize(word.lower(), pos="n")


def _norm_term(tokens):
    """Normalize a term (list of surface tokens) -> space-joined noun-lemmatized lowercase string."""
    out = [_lemma_noun(t) for t in tokens if t.isalpha()]
    return " ".join(out).strip()


def _wn_related(a, b):
    """Lenient genus match: exact, or WordNet synonym / <=2-hop hypernym either direction."""
    if a == b:
        return True
    key = (a, b) if a < b else (b, a)
    if key in _WN_CACHE:
        return _WN_CACHE[key]
    res = False
    try:
        sa = wn.synsets(a, pos=wn.NOUN)
        sb = wn.synsets(b, pos=wn.NOUN)
        # synonym: share a lemma name
        lem_a = set()
        for s in sa[:6]:
            for l in s.lemmas():
                lem_a.add(l.name().lower())
        if b in lem_a:
            res = True
        if not res:
            lem_b = set()
            for s in sb[:6]:
                for l in s.lemmas():
                    lem_b.add(l.name().lower())
            if a in lem_b:
                res = True
        if not res:
            # hypernym within 2 hops either direction
            def hyper_lemmas(syns, hops):
                acc = set()
                frontier = list(syns[:4])
                for _ in range(hops):
                    nxt = []
                    for s in frontier:
                        for h in s.hypernyms() + s.instance_hypernyms():
                            for l in h.lemmas():
                                acc.add(l.name().lower())
                            nxt.append(h)
                    frontier = nxt
                return acc
            if b in hyper_lemmas(sa, 2) or a in hyper_lemmas(sb, 2):
                res = True
    except Exception:
        # WordNet lookup failure is non-fatal for a single pair; treat as unrelated.
        res = False
    _WN_CACHE[key] = res
    return res


# ----------------------------- section / glossary parsing -----------------------------

def parse_sections(text):
    """Split text into level-5 (#####) sections. Return list of dicts:
       {title, prose, glossary: [(term_surface, definition), ...]}.
       Glossary blocks are removed from prose and returned separately as gold."""
    lines = text.split("\n")
    # find section boundaries: lines starting with exactly '##### '
    sec_starts = [i for i, ln in enumerate(lines) if ln.startswith("##### ") and not ln.startswith("###### ")]
    sections = []
    for si, start in enumerate(sec_starts):
        end = sec_starts[si + 1] if si + 1 < len(sec_starts) else len(lines)
        title = lines[start][6:].strip()
        body = lines[start + 1:end]
        # locate a Glossary subsection ('###### Glossary') and following '######'/'#####'
        prose_lines = []
        glossary = []
        in_gloss = False
        for ln in body:
            if ln.startswith("###### "):
                in_gloss = ln[7:].strip().lower().startswith("glossary")
                continue
            if in_gloss:
                m = re.match(r"^([A-Za-z][A-Za-z0-9 '/\-]{0,60}):\s+(.+)$", ln)
                if m:
                    glossary.append((m.group(1).strip(), m.group(2).strip()))
            else:
                prose_lines.append(ln)
        sections.append({
            "title": title,
            "prose": "\n".join(prose_lines),
            "glossary": glossary,
        })
    return sections


def genus_of_definition(defn):
    """Genus-differentia head extraction: first noun after leading det/adj/quantifier;
       'type/kind/form of X' -> head of X. Returns genus lemma or None."""
    toks = _tokenize(defn)
    if not toks:
        return None
    tags = pos_tag(toks)
    i = 0
    n = len(tags)
    # skip leading determiners / adjectives / quantifier words
    while i < n and (tags[i][1] in _SKIP_LEAD or tags[i][0].lower() in _QUANTIFIERS):
        i += 1
    if i >= n:
        return None
    if tags[i][1] not in _NOUN_TAGS:
        return None
    genus = _lemma_noun(tags[i][0])
    # type/kind/form of X override
    if genus in _TYPE_WORDS:
        j = i + 1
        # look for 'of' then a noun
        if j < n and tags[j][0].lower() == "of":
            j += 1
            while j < n and (tags[j][1] in _SKIP_LEAD or tags[j][0].lower() in _QUANTIFIERS):
                j += 1
            if j < n and tags[j][1] in _NOUN_TAGS:
                genus = _lemma_noun(tags[j][0])
    return genus


# ----------------------------- Hearst is-a extractor -----------------------------

def _split_sentences(prose):
    # regex sentence splitter (deterministic; avoids punkt dependency)
    # collapse newlines to spaces, split on sentence-final punctuation followed by space+cap
    txt = re.sub(r"\s+", " ", prose)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", txt)
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def _subject_before(tags, i):
    """Trailing (adj* noun+) run immediately before index i -> (term_norm, has_noun, head_surface)."""
    run = []
    j = i - 1
    saw_noun = False
    # first consume trailing nouns
    while j >= 0 and tags[j][1] in _NOUN_TAGS:
        run.append(tags[j][0]); saw_noun = True; j -= 1
    # then optional leading adjectives that modify the compound
    while j >= 0 and tags[j][1] in _ADJ_TAGS:
        run.append(tags[j][0]); j -= 1
    run.reverse()
    if not saw_noun:
        return None, False, None
    head_surface = None
    for w, t in reversed(list(zip([r for r in run], [None] * len(run)))):
        break
    return _norm_term(run), True, run[-1] if run else None


def _first_noun_after(tags, i):
    """First noun lemma after index i, skipping det/adj/quantifier; type-of override. Returns lemma or None."""
    n = len(tags)
    j = i + 1
    while j < n and (tags[j][1] in _SKIP_LEAD or tags[j][0].lower() in _QUANTIFIERS):
        j += 1
    if j >= n or tags[j][1] not in _NOUN_TAGS:
        return None
    genus = _lemma_noun(tags[j][0])
    if genus in _TYPE_WORDS:
        k = j + 1
        if k < n and tags[k][0].lower() == "of":
            k += 1
            while k < n and (tags[k][1] in _SKIP_LEAD or tags[k][0].lower() in _QUANTIFIERS):
                k += 1
            if k < n and tags[k][1] in _NOUN_TAGS:
                genus = _lemma_noun(tags[k][0])
    return genus


def ie_isa_extract(sentence):
    """Return list of (term_norm, genus_lemma, pattern) is-a edges from one sentence."""
    toks = _tokenize(sentence)
    if len(toks) < 3 or len(toks) > 80:
        return []
    tags = pos_tag(toks)
    n = len(tags)
    edges = []

    # PATTERN COP: [subject NP] (is|are|was|were) [det/adj]* GENUS
    for i in range(1, n - 1):
        w = tags[i][0].lower()
        if w in _BE and tags[i][1] in ("VBZ", "VBP", "VBD"):
            # reject pronoun / expletive subjects
            prev = tags[i - 1][0].lower()
            if prev in _PRON:
                continue
            term, has_noun, head = _subject_before(tags, i)
            if not has_noun or not term:
                continue
            if head and head.lower() in _PRON:
                continue
            genus = _first_noun_after(tags, i)
            if genus is None:
                continue
            # reject trivial identity (term head == genus)
            if term.split() and term.split()[-1] == genus:
                continue
            edges.append((term, genus, "COP"))

    # PATTERN SUCH_AS / INCLUDING: GENUS (such as | including) T1, T2, and T3
    for i in range(1, n - 1):
        w = tags[i][0].lower()
        trigger = None
        adv = 0
        if w == "such" and i + 1 < n and tags[i + 1][0].lower() == "as":
            trigger = i; adv = 2
        elif w == "including":
            trigger = i; adv = 1
        elif w in ("especially",) and i + 1 < n and tags[i + 1][0].lower() == "such":
            continue
        if trigger is None:
            continue
        # genus = last noun before trigger
        g = None
        j = trigger - 1
        while j >= 0 and tags[j][1] in _NOUN_TAGS:
            g = _lemma_noun(tags[j][0]); break
        # allow adj before, but need a noun
        if g is None:
            jj = trigger - 1
            while jj >= 0 and tags[jj][1] in (_NOUN_TAGS | _ADJ_TAGS):
                if tags[jj][1] in _NOUN_TAGS:
                    g = _lemma_noun(tags[jj][0]); break
                jj -= 1
        if g is None:
            continue
        # collect hyponym noun heads in the list after trigger (stop at sentence-final punct / verb)
        k = trigger + adv
        collected = 0
        while k < n and collected < 8:
            tg = tags[k][1]
            ww = tags[k][0]
            if ww in (".", ";", ":"):
                break
            if tg == "VBZ" or tg == "VBP" or tg == "VBD" or tg == "MD":
                break
            if tg in _NOUN_TAGS:
                # take head of this noun run
                run = [ww]
                while k + 1 < n and tags[k + 1][1] in _NOUN_TAGS:
                    k += 1; run.append(tags[k][0])
                term = _norm_term(run)
                if term and term.split()[-1] != g:
                    edges.append((term, g, "SUCHAS"))
                    collected += 1
            k += 1

    return edges


# ----------------------------- growth-curve driver -----------------------------

def build_gold(sections, heldout_every=5):
    """Return (gold_all, gold_heldout, gold_readpool, heldout_flags).
       gold maps norm_term -> genus_lemma. Held-out = every Nth glossary-bearing section."""
    gloss_rank = -1
    gold_all = {}
    gold_heldout = {}
    gold_readpool = {}
    heldout_flags = []  # per-section bool: is this section held-out (prose not read)
    for sec in sections:
        is_heldout = False
        if sec["glossary"]:
            gloss_rank += 1
            is_heldout = (gloss_rank % heldout_every == (heldout_every - 1))
            for term_surface, defn in sec["glossary"]:
                genus = genus_of_definition(defn)
                if genus is None:
                    continue
                nt = _norm_term(_tokenize(term_surface))
                if not nt:
                    continue
                gold_all[nt] = genus
                if is_heldout:
                    gold_heldout[nt] = genus
                else:
                    gold_readpool[nt] = genus
        heldout_flags.append(is_heldout)
    return gold_all, gold_heldout, gold_readpool, heldout_flags


def eval_coverage(foundation, gold, strict=True):
    """foundation: dict term -> Counter(genus). gold: dict term -> genus_lemma.
       Return (correct_cov, any_cov, n_correct, n_answered, n_total)."""
    n_total = len(gold)
    if n_total == 0:
        return 0.0, 0.0, 0, 0, 0
    n_correct = 0
    n_answered = 0
    for term, gg in gold.items():
        if term in foundation and len(foundation[term]) > 0:
            n_answered += 1
            pred = foundation[term].most_common(1)[0][0]
            if strict:
                ok = (pred == gg)
            else:
                ok = (pred == gg) or _wn_related(pred, gg)
            if not ok and not strict:
                # lenient also credits if ANY extracted genus for the term matches
                for cand in foundation[term]:
                    if cand == gg or _wn_related(cand, gg):
                        ok = True
                        break
            if ok:
                n_correct += 1
    return n_correct / n_total, n_answered / n_total, n_correct, n_answered, n_total


def extract_section(prose):
    """Extract all is-a edges from one section's prose. Return list of (term, genus)."""
    edges = []
    for sent in _split_sentences(prose):
        for term, genus, pat in ie_isa_extract(sent):
            edges.append((term, genus))
    return edges


def run_growth(sections, gold_all, gold_heldout, heldout_flags, verbose=False):
    """Accumulating vs non-accumulating growth curve on held-out gold. Returns metrics dict."""
    foundation = defaultdict(Counter)          # accumulating
    global_genus_counts = Counter()            # for frequency baseline
    curve = []                                  # per read-pool step
    read_rank = -1
    best_nonaccum_heldout = 0.0
    nonaccum_heldout_series = []
    for si, sec in enumerate(sections):
        if heldout_flags[si]:
            continue  # NEVER read held-out section prose (pure generalization test)
        edges = extract_section(sec["prose"])
        # non-accumulating foundation for THIS section only
        na = defaultdict(Counter)
        for term, genus in edges:
            na[term][genus] += 1
        # accumulate
        for term, genus in edges:
            foundation[term][genus] += 1
            global_genus_counts[genus] += 1
        read_rank += 1
        # evaluate on held-out gold
        acc_cc, acc_any, _, _, _ = eval_coverage(foundation, gold_heldout, strict=True)
        acc_cc_len, _, _, _, _ = eval_coverage(foundation, gold_heldout, strict=False)
        na_cc, _, _, _, _ = eval_coverage(na, gold_heldout, strict=True)
        best_nonaccum_heldout = max(best_nonaccum_heldout, na_cc)
        nonaccum_heldout_series.append(na_cc)
        # full-foundation coverage on ALL gold (supplementary; includes read-pool terms)
        all_cc, all_any, _, _, _ = eval_coverage(foundation, gold_all, strict=True)
        curve.append({
            "read_rank": read_rank,
            "section_idx": si,
            "n_edges_total": sum(sum(c.values()) for c in foundation.values()),
            "n_foundation_terms": len(foundation),
            "heldout_correct_cov": round(acc_cc, 5),
            "heldout_correct_cov_lenient": round(acc_cc_len, 5),
            "heldout_any_cov": round(acc_any, 5),
            "heldout_nonaccum_correct_cov": round(na_cc, 5),
            "all_correct_cov": round(all_cc, 5),
            "all_any_cov": round(all_any, 5),
        })
        if verbose and read_rank % 10 == 0:
            print("  [read_rank {:>3}] heldout_cc={:.4f} any={:.4f} nonaccum={:.4f} terms={} edges={}".format(
                read_rank, acc_cc, acc_any, na_cc, len(foundation),
                sum(sum(c.values()) for c in foundation.values())), flush=True)

    # frequency baseline: predict global-majority genus for EVERY held-out term
    freq_cc = 0.0
    freq_genus = None
    if global_genus_counts:
        freq_genus = global_genus_counts.most_common(1)[0][0]
        hits = sum(1 for gg in gold_heldout.values() if gg == freq_genus)
        freq_cc = hits / max(1, len(gold_heldout))

    # extraction precision on gold-term sample (of accumulated edges whose term is a gold term,
    # what fraction have a genus matching that term's gold genus -- strict + lenient)
    prec_strict_hits = prec_len_hits = prec_denom = 0
    for term, cnt in foundation.items():
        if term in gold_all:
            gg = gold_all[term]
            for genus, k in cnt.items():
                prec_denom += k
                if genus == gg:
                    prec_strict_hits += k
                    prec_len_hits += k
                elif _wn_related(genus, gg):
                    prec_len_hits += k
    extraction_precision_strict = prec_strict_hits / prec_denom if prec_denom else 0.0
    extraction_precision_lenient = prec_len_hits / prec_denom if prec_denom else 0.0

    return {
        "curve": curve,
        "best_nonaccum_heldout_cc": round(best_nonaccum_heldout, 5),
        "mean_nonaccum_heldout_cc": round(sum(nonaccum_heldout_series) / max(1, len(nonaccum_heldout_series)), 5),
        "freq_baseline_cc": round(freq_cc, 5),
        "freq_baseline_genus": freq_genus,
        "extraction_precision_strict": round(extraction_precision_strict, 5),
        "extraction_precision_lenient": round(extraction_precision_lenient, 5),
        "extraction_precision_denom": prec_denom,
    }


def compute_verdict(res, gold_heldout_n, bands):
    curve = res["curve"]
    if not curve:
        return "HARD_FAIL_NO_CURVE", "no read-pool steps produced", {}
    final = curve[-1]["heldout_correct_cov"]
    final_len = curve[-1]["heldout_correct_cov_lenient"]
    n = len(curve)
    two_thirds = curve[int(n * 2 / 3)]["heldout_correct_cov"] if n >= 3 else 0.0
    one_third = curve[int(n * 1 / 3)]["heldout_correct_cov"] if n >= 3 else 0.0
    last_third_gain = final - two_thirds
    mid_third_gain = two_thirds - one_third
    best_nonaccum = res["best_nonaccum_heldout_cc"]
    freq = res["freq_baseline_cc"]
    accum_benefit = final - best_nonaccum
    beats_freq = final - freq

    diag = {
        "final_heldout_correct_cov": final,
        "final_heldout_correct_cov_lenient": final_len,
        "one_third_cov": one_third,
        "two_thirds_cov": two_thirds,
        "last_third_gain": round(last_third_gain, 5),
        "mid_third_gain": round(mid_third_gain, 5),
        "best_nonaccum_heldout_cc": best_nonaccum,
        "accum_benefit_over_nonaccum": round(accum_benefit, 5),
        "freq_baseline_cc": freq,
        "beats_freq_margin": round(beats_freq, 5),
        "n_heldout_gold": gold_heldout_n,
    }

    # HARD_FAIL: plateau OR no accumulation benefit
    if last_third_gain < bands["plateau_gain_max"]:
        return "HARD_FAIL_PLATEAU", "growth curve plateaus (last-third gain {:.4f} < {:.4f})".format(
            last_third_gain, bands["plateau_gain_max"]), diag
    if accum_benefit < bands["min_accum_benefit"]:
        return "HARD_FAIL_NO_ACCUM_BENEFIT", "accumulation gives no benefit over non-accumulating ({:.4f} < {:.4f})".format(
            accum_benefit, bands["min_accum_benefit"]), diag
    # HARD_PASS: grows, non-plateau, beats both baselines, above floor
    if (final >= bands["hp_final_floor"] and last_third_gain >= bands["hp_last_third_gain"]
            and accum_benefit >= bands["hp_accum_benefit"] and beats_freq >= bands["hp_beats_freq"]):
        return "HARD_PASS", "grows + non-plateau + beats non-accum({:.3f}) + freq({:.3f}); final_cc={:.3f}".format(
            best_nonaccum, freq, final), diag
    return "MIDDLE_BAND", "grows but below HARD_PASS thresholds; final_cc={:.3f} last3_gain={:.4f}".format(
        final, last_third_gain), diag


# Pre-registered bands (HYPOTHESIZED@ this file; confirmed MEASURED@ at smoke/full)
BANDS = {
    "hp_final_floor": 0.10,       # held-out correct-coverage at book-end >= 10%
    "hp_last_third_gain": 0.02,   # still climbing >= 2pp over final third (KEEPS GOING)
    "hp_accum_benefit": 0.05,     # accum beats best single-section non-accum by >= 5pp
    "hp_beats_freq": 0.05,        # accum beats frequency-majority by >= 5pp
    "plateau_gain_max": 0.005,    # HARD_FAIL if last-third gain < 0.5pp (saturated)
    "min_accum_benefit": 0.02,    # HARD_FAIL if accum barely beats non-accum
}


# ----------------------------- self-test -----------------------------

def self_test():
    print("[self-test] exercising REAL code path on tiny in-memory corpus", flush=True)
    # tiny synthetic textbook: prose defines terms; glossary holds gold; held-out section never read.
    text = "\n".join([
        "# Tiny Book",
        "## Unit One",
        "### Chapter A",
        "##### Section Alpha",
        "A mitochondrion is an organelle that makes energy.",
        "Ribosomes are organelles found in cells.",
        "Organelles such as lysosomes and vacuoles occur in cells.",
        "###### Glossary",
        "mitochondrion: an organelle that produces energy",
        "lysosome: an organelle that digests waste",
        "##### Section Beta",
        "A neuron is a cell that transmits signals.",
        "Cells such as neurons and gametes are specialized.",
        "###### Glossary",
        "neuron: a cell that transmits nerve impulses",
        "##### Section Gamma",
        "This held-out prose must never be read into the foundation at all here.",
        "###### Glossary",
        "vacuole: an organelle that stores materials",
    ])
    secs = parse_sections(text)
    assert len(secs) == 3, "expected 3 level-5 sections, got {}".format(len(secs))
    # glossary parsing + genus extraction
    g_alpha = dict(secs[0]["glossary"])
    assert "mitochondrion" in g_alpha, g_alpha
    assert genus_of_definition("an organelle that produces energy") == "organelle"
    assert genus_of_definition("the study of life") == "study"
    assert genus_of_definition("a type of organelle in cells") == "organelle", "type-of override"
    # prose glossary must be stripped from prose
    assert "mitochondrion: an organelle" not in secs[0]["prose"]
    # extractor: copular + such-as
    e = ie_isa_extract("A mitochondrion is an organelle that makes energy.")
    assert ("mitochondrion", "organelle", "COP") in e, e
    e2 = ie_isa_extract("Organelles such as lysosomes and vacuoles occur in cells.")
    got = {(t, g) for (t, g, p) in e2}
    assert ("lysosome", "organelle") in got and ("vacuole", "organelle") in got, e2
    # build gold with held-out = every 3rd glossary section (rank 2 = Gamma held-out)
    gold_all, gold_ho, gold_rp, hflags = build_gold(secs, heldout_every=3)
    assert "vacuole" in gold_ho, ("vacuole should be held-out gold", gold_ho, hflags)
    assert hflags[2] is True and hflags[0] is False
    # growth: reading Alpha+Beta prose should COVER held-out 'vacuole' via cross-section 'such as' in Alpha
    res = run_growth(secs, gold_all, gold_ho, hflags, verbose=False)
    curve = res["curve"]
    assert len(curve) == 2, ("2 read-pool sections", len(curve))
    final_cc = curve[-1]["heldout_correct_cov"]
    assert final_cc > 0.0, ("held-out vacuole must be covered from Alpha prose (generalization)", curve)
    # ARMS-MUST-DIFFER: accum vs nonaccum must differ in general (accum >= nonaccum here)
    assert curve[-1]["heldout_correct_cov"] >= curve[-1]["heldout_nonaccum_correct_cov"]
    # frequency baseline real (not None)
    assert res["freq_baseline_genus"] is not None
    # verdict function runs
    v, msg, diag = compute_verdict(res, len(gold_ho), BANDS)
    assert v in ("HARD_PASS", "HARD_FAIL_PLATEAU", "HARD_FAIL_NO_ACCUM_BENEFIT", "MIDDLE_BAND", "HARD_FAIL_NO_CURVE")
    print("[self-test] PASS: sections={} gold_all={} gold_heldout={} final_heldout_cc={:.3f} verdict={}".format(
        len(secs), len(gold_all), len(gold_ho), final_cc, v), flush=True)
    return True


# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke-sections", type=int, default=24,
                    help="number of leading sections used in smoke mode")
    ap.add_argument("--heldout-every", type=int, default=5)
    args, _ = ap.parse_known_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    run_mode = args.mode
    output_dir = os.path.join(REPO, "data", "exp_{}{}".format(
        ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    _write_start_marker(output_dir, run_mode, expected_n_units=1)

    t0 = time.perf_counter()
    with open(CORPUS, "r", encoding="utf-8") as f:
        text = f.read()
    sections_all = parse_sections(text)
    if run_mode == "smoke":
        sections = sections_all[:args.smoke_sections]
    else:
        sections = sections_all

    gold_all, gold_ho, gold_rp, hflags = build_gold(sections, heldout_every=args.heldout_every)
    n_read_pool = sum(1 for h in hflags if not h)
    n_heldout_sec = sum(1 for h in hflags if h)
    print("[{}] sections={} read_pool_sec={} heldout_sec={} gold_all={} gold_heldout={}".format(
        run_mode, len(sections), n_read_pool, n_heldout_sec, len(gold_all), len(gold_ho)), flush=True)

    if len(gold_ho) == 0:
        raise RuntimeError("no held-out gold terms; increase corpus slice or adjust heldout_every")

    res = run_growth(sections, gold_all, gold_ho, hflags, verbose=True)
    verdict, verdict_msg, diag = compute_verdict(res, len(gold_ho), BANDS)
    elapsed = time.perf_counter() - t0

    # discriminator-fires + design-gate checks (surfaced in metrics)
    curve = res["curve"]
    coverage_moved = (curve[-1]["heldout_any_cov"] - curve[0]["heldout_any_cov"]) if len(curve) >= 2 else 0.0
    gate = {
        "discriminator_fires": bool(coverage_moved > 0.0 and res["extraction_precision_denom"] > 0),
        "coverage_moved_heldout_any": round(coverage_moved, 5),
        "real_baselines": {
            "nonaccum_present": res["best_nonaccum_heldout_cc"] is not None,
            "freq_present": res["freq_baseline_genus"] is not None,
            "freq_genus": res["freq_baseline_genus"],
        },
        "difficulty_on": "held-out sections' prose NEVER read; gold = held-out glossary genus",
        "one_variable": "accumulation on/off (accum vs current-section-only)",
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "{}: final_heldout_cc={:.3f} freq={:.3f} nonaccum={:.3f} last3_gain={:.4f}".format(
            verdict, diag.get("final_heldout_correct_cov", 0.0), res["freq_baseline_cc"],
            res["best_nonaccum_heldout_cc"], diag.get("last_third_gain", 0.0)),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "bands": BANDS,
        "diag": diag,
        "gate": gate,
        "extraction_precision_strict": res["extraction_precision_strict"],
        "extraction_precision_lenient": res["extraction_precision_lenient"],
        "extraction_precision_denom": res["extraction_precision_denom"],
        "freq_baseline_cc": res["freq_baseline_cc"],
        "freq_baseline_genus": res["freq_baseline_genus"],
        "best_nonaccum_heldout_cc": res["best_nonaccum_heldout_cc"],
        "mean_nonaccum_heldout_cc": res["mean_nonaccum_heldout_cc"],
        "n_sections": len(sections),
        "n_read_pool_sections": n_read_pool,
        "n_heldout_sections": n_heldout_sec,
        "n_gold_all": len(gold_all),
        "n_gold_heldout": len(gold_ho),
        "growth_curve": res["curve"],
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[{}] VERDICT={} {}".format(run_mode, verdict, metrics["summary"]), flush=True)
    print("[{}] extraction_precision strict={:.3f} lenient={:.3f} (denom={})".format(
        run_mode, res["extraction_precision_strict"], res["extraction_precision_lenient"],
        res["extraction_precision_denom"]), flush=True)
    print("[{}] metrics -> {}".format(run_mode, os.path.join(output_dir, "metrics.json")), flush=True)


if __name__ == "__main__":
    OUT_FOR_CRASH = os.path.join(REPO, "data", "exp_{}".format(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUT_FOR_CRASH, e)
        raise
