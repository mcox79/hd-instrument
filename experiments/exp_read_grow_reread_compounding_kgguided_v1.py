# CELL: read_grow_reread_compounding_kgguided_v1
# QUESTION (the USER's explicit phase-2 opener):
#   "Read one book, then read it AGAIN -- do you gain any more knowledge? Is it a
#    foundation you're building?"  Decisive test of COMPOUNDING across re-reads.
#
# THE MECHANISM UNDER TEST (glass-box, no runtime LLM):
#   Re-reading the SAME text with the SAME deterministic extractor gains NOTHING
#   (identical sentences -> identical edges = the deterministic-flat null). Re-reading
#   can ONLY compound if comprehension is KNOWLEDGE-GUIDED: on a re-read the foundation
#   built earlier resolves constructions that were unextractable cold.
#   The accumulated knowledge here is a GENUS VOCABULARY -- the set of nouns that have
#   been asserted as the genus for >= T distinct terms (learned categories, 0 curated seed).
#   Two COVERAGE-ADDITIVE constructions fire ONLY when their genus is in that vocabulary
#   (so they extract ZERO cold, when the vocabulary is empty):
#     KG_COREF : pronoun-subject copular ("It is an ORGANELLE") -> resolve pronoun to the
#                most-recent mentioned noun phrase; emit (antecedent, genus) iff genus known.
#     KG_APPOS : apposition ("the Golgi apparatus, an ORGANELLE, ...") -> emit (term, genus)
#                iff genus known.
#   The base Hearst extractor (COP + SUCH-AS, verbatim from isa_growth_v1) is a pure function
#   of the sentence -> re-running it is bit-flat by construction.
#
# ARMS (ONE variable = the re-read / knowledge-guidance schedule):
#   (a) PASS-1 COLD      : base extractor only, single pass over read-pool sections.
#   (b) PASS-2 GUIDED    : 2nd pass over the SAME sections with KG constructions ON
#                          (genus vocabulary from pass-1 feeds back).
#   (c) PASS-3 GUIDED    : 3rd pass, KG consulting the pass-2 vocabulary.
#   (d) PASS-2 NAIVE     : 2nd pass, KG OFF (base only) = the deterministic-flat control;
#                          == pass-1 by construction; isolates gain=knowledge not re-exposure.
#   (e) FREQ-ONLY        : predict the globally-most-common genus for EVERY held-out term
#                          (the "gain is just high-frequency re-weighting" guard, per a9787ced).
#
# METRIC = held-out foundation quality on the ~1000 glossary is-a gold pairs:
#   coverage (correct genus, fair paraphrase-robust WordNet genus-match) AND extraction
#   precision, PER PASS. Does coverage/precision RISE pass-1 -> pass-2 -> pass-3 (compounding),
#   and does the rise BEAT BOTH cold-pass-1 AND frequency (arm b/c > arm a AND > arm e)?
#
# BRANCHES (both first-class; DEFLATE a null, do not dress it as a win):
#   HARD_PASS : guided re-reading COMPOUNDS -- best-guided coverage beats cold pass-1 by the
#               pre-registered margin AND beats naive-reread AND beats frequency, without
#               precision collapse, and KG fired on held-out-relevant terms. USER hypothesis
#               CONFIRMED: re-reading builds foundation via the bootstrap.
#   HARD_FAIL : re-reading is deterministically flat / knowledge-guidance adds nothing over
#               cold pass-1, OR the gain is frequency-equivalent. INFORMATIVE: localizes that
#               compounding needs a capability hand-rules re-application lacks (the learned reader).
#
# PRIOR-WORK (honesty): the genus-vocabulary-as-learned-category idea REDISCOVERS the
#   self-bootstrapped concept-class set C of exp_read_grow_knowledge_guided_bootstrap_v1
#   (a9787ced), which found guided re-reading FREQUENCY-EQUIVALENT on its regime. NEW here:
#   (1) COVERAGE-ADDITIVE KG_COREF + KG_APPOS constructions (a9787ced only re-selected heads /
#       filtered existing candidates, adding little coverage); (2) explicit naive-reread control
#       isolating re-exposure; (3) freq-only arm as an explicit guard; (4) the compounding curve
#       on the DIRECT is-a foundation coverage of the OpenStax Concepts-of-Biology gold.
#   Base extractor + fair genus-match scorer + glossary gold REUSED from isa_growth_v1 (3d3e85592).
#
# Compute architecture: (b) sequential-CPU. Justification: pure regex / Perceptron POS /
#   WordNet / symbolic dict accumulation. No matmul, no substrate vectors, no SGD. Tags cached
#   once and reused across passes (no re-tagging). Diagnostic compounding-curve cell
#   (compute-proportionality: cheapest decisive method). Storage = no_storage (no HD vectors).
#   Determinism: FIXED int index / sorted(); no built-in hash() / list(set()) seeds ordering.
#   CRLB: n/a -- no additive-noise cleanup floor in this symbolic-extraction cell.
#
# CELL-TEMPLATE MANDATORY:
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - ARMS-MUST-DIFFER: foundation digests logged; (pass2_naive == pass1) is INTENTIONAL
#   (arms_differ_exempted) -- it IS the deterministic-flat null; (pass2_guided == pass2_naive)
#   is the HARD_FAIL_FLAT outcome, handled in the verdict, NOT a bug-assert.
# - all bands tagged HYPOTHESIZED@ (this file) then confirmed MEASURED@ at smoke/full.

import os
import re
import sys
import json
import time
import argparse
import traceback
import hashlib
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

import nltk  # noqa: F401  (ensures the dep is present; pos_tag/wordnet pulled below)
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

ANCHOR_NAME = "read_grow_reread_compounding_kgguided_v1"
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


# ----------------------------- linguistics helpers (REUSED from isa_growth_v1) -----------------------------

_LEM = WordNetLemmatizer()
_NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
_ADJ_TAGS = {"JJ", "JJR", "JJS"}
_DET_TAGS = {"DT", "PDT"}
_SKIP_LEAD = {"DT", "PDT", "CD", "RB", "RBR", "RBS", "PRP$"} | _ADJ_TAGS
_QUANTIFIERS = {"all", "any", "some", "each", "every", "most", "many", "several",
                "certain", "various", "one", "two", "both", "either", "no", "the",
                "a", "an", "this", "that", "these", "those"}
_TYPE_WORDS = {"type", "kind", "form", "sort", "group", "class", "category", "variety",
               "example", "member", "set", "collection"}
_PRON = {"it", "they", "this", "these", "those", "there", "he", "she", "we", "you",
         "i", "who", "which", "that", "what", "one", "some", "many", "all"}
_COREF_PRON = {"it", "they", "these", "this", "those"}   # pronouns we attempt to resolve
_BE = {"is", "are", "was", "were"}
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*|[.,;:()]")

_WN_CACHE = {}


def _tokenize(text):
    return _TOKEN_RE.findall(text)


def _lemma_noun(word):
    return _LEM.lemmatize(word.lower(), pos="n")


def _norm_term(tokens):
    out = [_lemma_noun(t) for t in tokens if t.isalpha()]
    return " ".join(out).strip()


def _wn_related(a, b):
    """Lenient (fair) genus match: exact, WordNet synonym, or <=2-hop hypernym either direction."""
    if a == b:
        return True
    key = (a, b) if a < b else (b, a)
    if key in _WN_CACHE:
        return _WN_CACHE[key]
    res = False
    try:
        sa = wn.synsets(a, pos=wn.NOUN)
        sb = wn.synsets(b, pos=wn.NOUN)
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
        res = False
    _WN_CACHE[key] = res
    return res


# ----------------------------- section / glossary parsing (REUSED) -----------------------------

def parse_sections(text):
    lines = text.split("\n")
    sec_starts = [i for i, ln in enumerate(lines)
                  if ln.startswith("##### ") and not ln.startswith("###### ")]
    sections = []
    for si, start in enumerate(sec_starts):
        end = sec_starts[si + 1] if si + 1 < len(sec_starts) else len(lines)
        title = lines[start][6:].strip()
        body = lines[start + 1:end]
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
        sections.append({"title": title, "prose": "\n".join(prose_lines), "glossary": glossary})
    return sections


def genus_of_definition(defn):
    toks = _tokenize(defn)
    if not toks:
        return None
    tags = pos_tag(toks)
    i = 0
    n = len(tags)
    while i < n and (tags[i][1] in _SKIP_LEAD or tags[i][0].lower() in _QUANTIFIERS):
        i += 1
    if i >= n:
        return None
    if tags[i][1] not in _NOUN_TAGS:
        return None
    genus = _lemma_noun(tags[i][0])
    if genus in _TYPE_WORDS:
        j = i + 1
        if j < n and tags[j][0].lower() == "of":
            j += 1
            while j < n and (tags[j][1] in _SKIP_LEAD or tags[j][0].lower() in _QUANTIFIERS):
                j += 1
            if j < n and tags[j][1] in _NOUN_TAGS:
                genus = _lemma_noun(tags[j][0])
    return genus


def _split_sentences(prose):
    txt = re.sub(r"\s+", " ", prose)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", txt)
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def _first_noun_after(tags, i):
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


def _subject_before(tags, i):
    run = []
    j = i - 1
    saw_noun = False
    while j >= 0 and tags[j][1] in _NOUN_TAGS:
        run.append(tags[j][0]); saw_noun = True; j -= 1
    while j >= 0 and tags[j][1] in _ADJ_TAGS:
        run.append(tags[j][0]); j -= 1
    run.reverse()
    if not saw_noun:
        return None, False, None
    return _norm_term(run), True, run[-1] if run else None


# ----------------------------- BASE is-a extractor (verbatim logic; tags pre-computed) -----------------------------

def _isa_from_tags(toks, tags):
    """Base Hearst is-a edges (COP + SUCH-AS/including). Pure function of tags => bit-flat on re-read."""
    if len(toks) < 3 or len(toks) > 80:
        return []
    n = len(tags)
    edges = []
    # PATTERN COP
    for i in range(1, n - 1):
        w = tags[i][0].lower()
        if w in _BE and tags[i][1] in ("VBZ", "VBP", "VBD"):
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
            if term.split() and term.split()[-1] == genus:
                continue
            edges.append((term, genus, "COP"))
    # PATTERN SUCH_AS / INCLUDING
    for i in range(1, n - 1):
        w = tags[i][0].lower()
        trigger = None
        adv = 0
        if w == "such" and i + 1 < n and tags[i + 1][0].lower() == "as":
            trigger = i; adv = 2
        elif w == "including":
            trigger = i; adv = 1
        if trigger is None:
            continue
        g = None
        j = trigger - 1
        while j >= 0 and tags[j][1] in _NOUN_TAGS:
            g = _lemma_noun(tags[j][0]); break
        if g is None:
            jj = trigger - 1
            while jj >= 0 and tags[jj][1] in (_NOUN_TAGS | _ADJ_TAGS):
                if tags[jj][1] in _NOUN_TAGS:
                    g = _lemma_noun(tags[jj][0]); break
                jj -= 1
        if g is None:
            continue
        k = trigger + adv
        collected = 0
        while k < n and collected < 8:
            tg = tags[k][1]
            ww = tags[k][0]
            if ww in (".", ";", ":"):
                break
            if tg in ("VBZ", "VBP", "VBD", "MD"):
                break
            if tg in _NOUN_TAGS:
                run = [ww]
                while k + 1 < n and tags[k + 1][1] in _NOUN_TAGS:
                    k += 1; run.append(tags[k][0])
                term = _norm_term(run)
                if term and term.split()[-1] != g:
                    edges.append((term, g, "SUCHAS"))
                    collected += 1
            k += 1
    return edges


# ----------------------------- KNOWLEDGE-GUIDED layer (coverage-additive; genus-vocab gated) -----------------------------

def sentence_mentions(tags):
    """Normalized noun-phrase head-terms mentioned in a sentence (for the coref antecedent buffer)."""
    out = []
    i = 0
    n = len(tags)
    while i < n:
        if tags[i][1] in _NOUN_TAGS:
            run = []
            while i < n and tags[i][1] in _NOUN_TAGS:
                run.append(tags[i][0]); i += 1
            t = _norm_term(run)
            if t and t not in _PRON:
                out.append(t)
        else:
            i += 1
    return out


def kg_isa_from_tags(toks, tags, genus_vocab, recent_terms):
    """KG edges that fire ONLY when the genus is in genus_vocab (empty vocab => zero edges).
       KG_COREF: pronoun-subject copular resolved to most-recent mention.
       KG_APPOS: 'TERM, (a|an|the) GENUS[,.;: /that/which/VB]' apposition.
       Returns list of (term, genus, pattern)."""
    if len(toks) < 3 or len(toks) > 80 or not genus_vocab:
        return []
    n = len(tags)
    edges = []
    seen = set()

    # KG_COREF: pronoun-subject copular
    for i in range(1, n - 1):
        w = tags[i][0].lower()
        if w in _BE and tags[i][1] in ("VBZ", "VBP", "VBD"):
            prev = tags[i - 1][0].lower()
            if prev not in _COREF_PRON:
                continue  # only pronoun subjects (base already handles noun subjects)
            genus = _first_noun_after(tags, i)
            if genus is None or genus not in genus_vocab:
                continue
            ant = None
            for t in reversed(recent_terms):
                if t and t.split()[-1] != genus and t not in _PRON:
                    ant = t; break
            if ant is None:
                continue
            e = (ant, genus, "KG_COREF")
            if (ant, genus) not in seen:
                seen.add((ant, genus)); edges.append(e)
            break  # at most one coref resolution per sentence

    # KG_APPOS: apposition 'TERM , (det)? (adj)* GENUS <close>'
    for c in range(1, n - 2):
        if tags[c][0] != ",":
            continue
        # TERM = noun run (with optional leading adjectives) ending just before the comma
        j = c - 1
        run = []
        while j >= 0 and tags[j][1] in _NOUN_TAGS:
            run.append(tags[j][0]); j -= 1
        if not run:
            continue
        while j >= 0 and tags[j][1] in _ADJ_TAGS:
            run.append(tags[j][0]); j -= 1
        run.reverse()
        term = _norm_term(run)
        if not term or term in _PRON:
            continue
        # after comma: optional det, optional adjectives, then GENUS noun
        k = c + 1
        if k < n and tags[k][1] in _DET_TAGS:
            k += 1
        while k < n and tags[k][1] in _ADJ_TAGS:
            k += 1
        if k >= n or tags[k][1] not in _NOUN_TAGS:
            continue
        genus = _lemma_noun(tags[k][0])
        if genus not in genus_vocab:
            continue
        # appositive close: comma / sentence-punct / relativizer / verb
        nb_tok = tags[k + 1][0] if k + 1 < n else "."
        nb_tag = tags[k + 1][1] if k + 1 < n else "."
        if nb_tok not in (",", ".", ";", ":") and nb_tag != "WDT" and not nb_tag.startswith("VB"):
            continue
        if term.split()[-1] == genus:
            continue
        if (term, genus) not in seen:
            seen.add((term, genus)); edges.append((term, genus, "KG_APPOS"))

    return edges


# ----------------------------- gold + eval (REUSED) -----------------------------

def build_gold(sections, heldout_every=5):
    gloss_rank = -1
    gold_all, gold_heldout, gold_readpool = {}, {}, {}
    heldout_flags = []
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
    n_total = len(gold)
    if n_total == 0:
        return 0.0, 0.0, 0, 0, 0
    n_correct = n_answered = 0
    for term, gg in gold.items():
        if term in foundation and len(foundation[term]) > 0:
            n_answered += 1
            pred = foundation[term].most_common(1)[0][0]
            if strict:
                ok = (pred == gg)
            else:
                ok = (pred == gg) or _wn_related(pred, gg)
                if not ok:
                    for cand in foundation[term]:
                        if cand == gg or _wn_related(cand, gg):
                            ok = True; break
            if ok:
                n_correct += 1
    return n_correct / n_total, n_answered / n_total, n_correct, n_answered, n_total


def extraction_precision(foundation, gold_all):
    ps = pl = denom = 0
    for term, cnt in foundation.items():
        if term in gold_all:
            gg = gold_all[term]
            for genus, k in cnt.items():
                denom += k
                if genus == gg:
                    ps += k; pl += k
                elif _wn_related(genus, gg):
                    pl += k
    return (ps / denom if denom else 0.0), (pl / denom if denom else 0.0), denom


def foundation_digest(foundation):
    """Deterministic digest of the argmax-genus per term (sorted; no built-in hash())."""
    rows = []
    for term in sorted(foundation.keys()):
        if len(foundation[term]) > 0:
            rows.append(term + "|" + foundation[term].most_common(1)[0][0])
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


# ----------------------------- multi-pass compounding driver -----------------------------

def _snapshot(foundation, gold_all, gold_ho):
    cc_s, any_s, ncs, nas, _ = eval_coverage(foundation, gold_ho, strict=True)
    cc_l, any_l, ncl, _, _ = eval_coverage(foundation, gold_ho, strict=False)
    ps, pl, denom = extraction_precision(foundation, gold_all)
    return {
        "n_foundation_terms": len(foundation),
        "n_edges_total": sum(sum(c.values()) for c in foundation.values()),
        "heldout_correct_cov_strict": round(cc_s, 5),
        "heldout_correct_cov_lenient": round(cc_l, 5),
        "heldout_any_cov": round(any_l, 5),
        "heldout_n_correct_lenient": ncl,
        "extraction_precision_strict": round(ps, 5),
        "extraction_precision_lenient": round(pl, 5),
        "extraction_precision_denom": denom,
        "foundation_digest": foundation_digest(foundation),
    }


def _add_edges(foundation, genus_term_count, edges):
    for term, genus, _pat in edges:
        foundation[term][genus] += 1
        genus_term_count[genus].add(term)


def run_compounding(sections, gold_all, gold_ho, heldout_flags, n_passes=3,
                    genus_vocab_min=2, coref_window=6, verbose=False, hb=None):
    """GUIDED chain (pass1 cold, pass2..n guided) + NAIVE control chain (all base-only).
       Also computes the frequency-only baseline. Returns a metrics dict."""
    readpool = [si for si, h in enumerate(heldout_flags) if not h]

    # Pre-tag every read-pool sentence ONCE (reused across all passes; deterministic).
    tagged = {}
    for idx, si in enumerate(readpool):
        lst = []
        for s in _split_sentences(sections[si]["prose"]):
            toks = _tokenize(s)
            tags = pos_tag(toks)
            lst.append((toks, tags, sentence_mentions(tags)))
        tagged[si] = lst
        if hb is not None and idx % 40 == 0:
            hb(idx, len(readpool), "tagging")

    # --- GUIDED chain ---
    F = defaultdict(Counter)
    gtc = defaultdict(set)
    global_genus_counts = Counter()
    pass_records = []
    kg_edges_per_pass = []
    kg_heldout_relevant_per_pass = []
    n_kg_total = 0
    n_kg_heldout_rel = 0
    for p in range(1, n_passes + 1):
        guided = (p >= 2)
        kg_this = 0
        kg_ho_this = 0
        for idx, si in enumerate(readpool):
            genus_vocab = {g for g, terms in gtc.items() if len(terms) >= genus_vocab_min}
            recent = deque(maxlen=coref_window)
            for (toks, tags, ments) in tagged[si]:
                base = _isa_from_tags(toks, tags)
                _add_edges(F, gtc, base)
                if p == 1:  # accumulate frequency stats from the cold read
                    for _t, gg, _pt in base:
                        global_genus_counts[gg] += 1
                if guided:
                    kg = kg_isa_from_tags(toks, tags, genus_vocab, list(recent))
                    if kg:
                        _add_edges(F, gtc, kg)
                        kg_this += len(kg)
                        for (t, gg, _pt) in kg:
                            if t in gold_ho:
                                kg_ho_this += 1
                for m in ments:
                    recent.append(m)
            if hb is not None and idx % 60 == 0:
                hb(idx, len(readpool), "pass{}".format(p))
        n_kg_total += kg_this
        n_kg_heldout_rel += kg_ho_this
        kg_edges_per_pass.append(kg_this)
        kg_heldout_relevant_per_pass.append(kg_ho_this)
        rec = _snapshot(F, gold_all, gold_ho)
        rec["pass"] = p
        rec["mode"] = "cold" if p == 1 else "guided"
        rec["kg_edges_added_this_pass"] = kg_this
        rec["kg_heldout_relevant_this_pass"] = kg_ho_this
        pass_records.append(rec)
        if verbose:
            print("  [guided pass {}] cov_len={:.4f} prec_len={:.4f} terms={} kg_added={} kg_ho_rel={}".format(
                p, rec["heldout_correct_cov_lenient"], rec["extraction_precision_lenient"],
                rec["n_foundation_terms"], kg_this, kg_ho_this), flush=True)

    # --- NAIVE control chain (base-only, 2 passes) ---
    Fn = defaultdict(Counter)
    gtcn = defaultdict(set)
    naive_records = []
    for p in range(1, 3):
        for si in readpool:
            for (toks, tags, _m) in tagged[si]:
                _add_edges(Fn, gtcn, _isa_from_tags(toks, tags))
        rec = _snapshot(Fn, gold_all, gold_ho)
        rec["pass"] = p
        rec["mode"] = "naive_reread"
        naive_records.append(rec)
        if verbose:
            print("  [naive  pass {}] cov_len={:.4f} prec_len={:.4f} terms={}".format(
                p, rec["heldout_correct_cov_lenient"], rec["extraction_precision_lenient"],
                rec["n_foundation_terms"]), flush=True)

    # --- frequency-only baseline (predict global-majority genus for every held-out term) ---
    freq_genus = None
    freq_cc_strict = freq_cc_lenient = 0.0
    if global_genus_counts:
        freq_genus = global_genus_counts.most_common(1)[0][0]
        strict_hits = sum(1 for gg in gold_ho.values() if gg == freq_genus)
        len_hits = sum(1 for gg in gold_ho.values() if gg == freq_genus or _wn_related(freq_genus, gg))
        freq_cc_strict = strict_hits / max(1, len(gold_ho))
        freq_cc_lenient = len_hits / max(1, len(gold_ho))

    return {
        "pass_records": pass_records,
        "naive_records": naive_records,
        "n_kg_edges_total": n_kg_total,
        "n_kg_heldout_relevant_total": n_kg_heldout_rel,
        "kg_edges_per_pass": kg_edges_per_pass,
        "kg_heldout_relevant_per_pass": kg_heldout_relevant_per_pass,
        "freq_baseline_genus": freq_genus,
        "freq_baseline_cc_strict": round(freq_cc_strict, 5),
        "freq_baseline_cc_lenient": round(freq_cc_lenient, 5),
        "n_readpool_sections": len(readpool),
    }


# Pre-registered bands (HYPOTHESIZED@ this file; confirmed MEASURED@ at smoke/full).
# Primary metric = held-out correct-coverage LENIENT (fair paraphrase-robust WordNet genus-match).
BANDS = {
    "hp_gain_over_cold": 0.02,      # best-guided cov_lenient - pass1(cold) cov_lenient >= 2pp
    "hp_gain_over_naive": 0.02,     # best-guided - naive-reread >= 2pp (gain is knowledge, not re-exposure)
    "hp_gain_over_freq": 0.02,      # best-guided - freq-only cov_lenient >= 2pp (beats frequency)
    "hp_precision_tolerance": 0.05, # best-guided prec_lenient >= pass1 prec_lenient - 5pp (no precision collapse)
    "hp_min_kg_heldout_rel": 5,     # KG fired on >= 5 held-out-relevant terms (discriminator fired)
    "flat_gain_max": 0.005,         # HARD_FAIL_FLAT if best-guided - cold < 0.5pp
    "freq_equiv_margin": 0.005,     # HARD_FAIL_FREQ_EQUIV if best-guided - freq < 0.5pp
}


def compute_verdict(res, bands):
    pr = res["pass_records"]
    if not pr:
        return "HARD_FAIL_NO_PASSES", "no read-pool passes produced", {}
    cold = pr[0]
    guided = pr[1:] if len(pr) > 1 else []
    cold_cov = cold["heldout_correct_cov_lenient"]
    cold_prec = cold["extraction_precision_lenient"]
    naive_cov = res["naive_records"][-1]["heldout_correct_cov_lenient"] if res["naive_records"] else cold_cov
    freq_cov = res["freq_baseline_cc_lenient"]

    if guided:
        best = max(guided, key=lambda r: r["heldout_correct_cov_lenient"])
        best_cov = best["heldout_correct_cov_lenient"]
        best_prec = best["extraction_precision_lenient"]
        best_pass = best["pass"]
    else:
        best_cov, best_prec, best_pass = cold_cov, cold_prec, 1

    gain_cold = best_cov - cold_cov
    gain_naive = best_cov - naive_cov
    gain_freq = best_cov - freq_cov
    prec_delta = best_prec - cold_prec
    kg_ho = res["n_kg_heldout_relevant_total"]

    diag = {
        "cold_pass1_cov_lenient": cold_cov,
        "cold_pass1_prec_lenient": cold_prec,
        "best_guided_pass": best_pass,
        "best_guided_cov_lenient": best_cov,
        "best_guided_prec_lenient": best_prec,
        "naive_reread_cov_lenient": naive_cov,
        "freq_only_cov_lenient": freq_cov,
        "gain_over_cold": round(gain_cold, 5),
        "gain_over_naive": round(gain_naive, 5),
        "gain_over_freq": round(gain_freq, 5),
        "precision_delta_guided_vs_cold": round(prec_delta, 5),
        "n_kg_edges_total": res["n_kg_edges_total"],
        "n_kg_heldout_relevant_total": kg_ho,
        "naive_equals_cold_by_construction": abs(naive_cov - cold_cov) < 1e-9,
    }

    # HARD_FAIL: deterministically flat OR frequency-equivalent OR mechanism never fired
    if res["n_kg_edges_total"] == 0:
        return ("HARD_FAIL_FLAT",
                "knowledge-guided re-reading fired ZERO new edges; re-reading is deterministically flat "
                "(hand-rules re-application adds nothing)", diag)
    if gain_cold < bands["flat_gain_max"]:
        return ("HARD_FAIL_FLAT",
                "re-reading does NOT compound: best-guided cov {:.4f} vs cold {:.4f} (gain {:.4f} < {:.4f})".format(
                    best_cov, cold_cov, gain_cold, bands["flat_gain_max"]), diag)
    if gain_freq < bands["freq_equiv_margin"]:
        return ("HARD_FAIL_FREQ_EQUIV",
                "re-read gain is frequency-equivalent: best-guided {:.4f} vs freq-only {:.4f} (margin {:.4f} < {:.4f})".format(
                    best_cov, freq_cov, gain_freq, bands["freq_equiv_margin"]), diag)

    # HARD_PASS: compounds over cold AND naive AND freq, no precision collapse, discriminator fired
    if (gain_cold >= bands["hp_gain_over_cold"] and gain_naive >= bands["hp_gain_over_naive"]
            and gain_freq >= bands["hp_gain_over_freq"] and prec_delta >= -bands["hp_precision_tolerance"]
            and kg_ho >= bands["hp_min_kg_heldout_rel"]):
        return ("HARD_PASS",
                "re-reading COMPOUNDS: pass{} cov {:.3f} beats cold {:.3f}(+{:.3f}) naive {:.3f} freq {:.3f}; "
                "prec_delta {:+.3f}; kg_ho_rel={}".format(
                    best_pass, best_cov, cold_cov, gain_cold, naive_cov, freq_cov, prec_delta, kg_ho), diag)

    return ("MIDDLE_BAND",
            "guided re-reading moves but below HARD_PASS: gain_cold={:.4f} gain_freq={:.4f} prec_delta={:+.4f} kg_ho={}".format(
                gain_cold, gain_freq, prec_delta, kg_ho), diag)


# ----------------------------- self-test -----------------------------

def self_test():
    print("[self-test] exercising REAL code path on a tiny in-memory corpus", flush=True)
    # Alpha establishes 'organelle' as a genus (>=2 distinct terms) so the vocab learns it.
    # A pronoun-copular ('It is an organelle') and an apposition are UNEXTRACTABLE cold
    # (empty vocab) but fire on the guided re-read -> compounding. Held-out 'vacuole' in Gamma.
    text = "\n".join([
        "# Tiny Book",
        "## Unit One",
        "### Chapter A",
        "##### Section Alpha",
        "A mitochondrion is an organelle that makes energy.",
        "A ribosome is an organelle found in cells.",
        "The lysosome digests waste. It is an organelle.",
        "The peroxisome, an organelle, breaks down fats.",
        "Organelles such as vacuoles occur in plant cells.",
        "###### Glossary",
        "mitochondrion: an organelle that produces energy",
        "lysosome: an organelle that digests waste",
        "##### Section Beta",
        "A neuron is a cell that transmits signals.",
        "A gamete is a cell involved in reproduction.",
        "###### Glossary",
        "neuron: a cell that transmits nerve impulses",
        "##### Section Gamma",
        "This held-out prose must never be read into the foundation.",
        "###### Glossary",
        "vacuole: an organelle that stores materials",
    ])
    secs = parse_sections(text)
    assert len(secs) == 3, "expected 3 level-5 sections, got {}".format(len(secs))
    assert genus_of_definition("an organelle that produces energy") == "organelle"
    assert genus_of_definition("a type of organelle in cells") == "organelle", "type-of override"
    # base extractor: copular + such-as fire; pronoun-subject copular does NOT (base drops it)
    e = _isa_from_tags(*_tag("A mitochondrion is an organelle that makes energy."))
    assert ("mitochondrion", "organelle", "COP") in e, e
    e_pron = _isa_from_tags(*_tag("It is an organelle."))
    assert e_pron == [], ("base must drop pronoun-subject copular", e_pron)
    # KG coref fires only with vocab + a recent antecedent
    toks, tags = _tag("It is an organelle.")
    assert kg_isa_from_tags(toks, tags, set(), ["lysosome"]) == [], "empty vocab => zero KG edges"
    kg = kg_isa_from_tags(toks, tags, {"organelle"}, ["lysosome"])
    assert ("lysosome", "organelle", "KG_COREF") in kg, ("coref should resolve It->lysosome", kg)
    # KG apposition fires only with vocab
    toks2, tags2 = _tag("The peroxisome, an organelle, breaks down fats.")
    assert kg_isa_from_tags(toks2, tags2, set(), []) == [], "empty vocab => zero KG appos"
    kg2 = kg_isa_from_tags(toks2, tags2, {"organelle"}, [])
    assert ("peroxisome", "organelle", "KG_APPOS") in kg2, ("appos should fire", kg2)

    gold_all, gold_ho, gold_rp, hflags = build_gold(secs, heldout_every=3)
    assert "vacuole" in gold_ho, ("vacuole held-out", gold_ho, hflags)
    assert hflags[2] is True and hflags[0] is False

    res = run_compounding(secs, gold_all, gold_ho, hflags, n_passes=3,
                          genus_vocab_min=2, coref_window=6, verbose=False)
    pr = res["pass_records"]
    assert len(pr) == 3, ("3 passes", len(pr))
    cold_cov = pr[0]["heldout_correct_cov_lenient"]
    best_guided = max(r["heldout_correct_cov_lenient"] for r in pr[1:])
    # COMPOUNDING: guided re-read must cover held-out 'vacuole' (via cross-section 'such as' in Alpha
    # this is already covered cold; the DISCRIMINATOR is that KG fires new edges at all + naive is flat)
    assert res["n_kg_edges_total"] > 0, ("KG must fire on the guided re-read", res["n_kg_edges_total"])
    # NAIVE control must be bit-flat vs cold pass-1 (deterministic-flat null)
    naive_cov = res["naive_records"][-1]["heldout_correct_cov_lenient"]
    assert abs(naive_cov - cold_cov) < 1e-9, ("naive re-read must equal cold pass-1", naive_cov, cold_cov)
    assert pr[0]["foundation_digest"] != pr[1]["foundation_digest"] or res["n_kg_edges_total"] > 0
    # guided foundation must DIFFER from naive foundation (ARMS-MUST-DIFFER, non-flat mechanism)
    assert pr[1]["foundation_digest"] != res["naive_records"][-1]["foundation_digest"], \
        "guided pass-2 foundation must differ from naive pass-2 (KG fired)"
    # freq baseline real
    assert res["freq_baseline_genus"] is not None
    v, msg, diag = compute_verdict(res, BANDS)
    assert v in ("HARD_PASS", "HARD_FAIL_FLAT", "HARD_FAIL_FREQ_EQUIV", "MIDDLE_BAND", "HARD_FAIL_NO_PASSES")
    print("[self-test] PASS: secs={} gold_all={} gold_ho={} cold_cov={:.3f} best_guided={:.3f} "
          "kg_total={} kg_ho_rel={} naive==cold={} verdict={}".format(
              len(secs), len(gold_all), len(gold_ho), cold_cov, best_guided,
              res["n_kg_edges_total"], res["n_kg_heldout_relevant_total"],
              abs(naive_cov - cold_cov) < 1e-9, v), flush=True)
    return True


def _tag(sentence):
    toks = _tokenize(sentence)
    return toks, pos_tag(toks)


# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke-sections", type=int, default=120,
                    help="number of leading sections used in smoke mode")
    ap.add_argument("--heldout-every", type=int, default=5)
    ap.add_argument("--n-passes", type=int, default=3)
    ap.add_argument("--genus-vocab-min", type=int, default=2)
    ap.add_argument("--coref-window", type=int, default=6)
    args, _ = ap.parse_known_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    run_mode = args.mode
    output_dir = os.path.join(REPO, "data", "exp_{}{}".format(
        ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    _write_start_marker(output_dir, run_mode, expected_n_units=args.n_passes)

    t0 = time.perf_counter()

    def _hb(idx, total, phase):
        print("  [hb {}] {}/{} sections elapsed={:.1f}s".format(
            phase, idx, total, time.perf_counter() - t0), flush=True)

    with open(CORPUS, "r", encoding="utf-8") as f:
        text = f.read()
    sections_all = parse_sections(text)
    sections = sections_all[:args.smoke_sections] if run_mode == "smoke" else sections_all

    gold_all, gold_ho, gold_rp, hflags = build_gold(sections, heldout_every=args.heldout_every)
    n_read_pool = sum(1 for h in hflags if not h)
    n_heldout_sec = sum(1 for h in hflags if h)
    print("[{}] sections={} read_pool_sec={} heldout_sec={} gold_all={} gold_heldout={}".format(
        run_mode, len(sections), n_read_pool, n_heldout_sec, len(gold_all), len(gold_ho)), flush=True)
    if len(gold_ho) == 0:
        raise RuntimeError("no held-out gold terms; increase corpus slice or adjust heldout_every")

    res = run_compounding(sections, gold_all, gold_ho, hflags,
                          n_passes=args.n_passes, genus_vocab_min=args.genus_vocab_min,
                          coref_window=args.coref_window, verbose=True, hb=_hb)
    verdict, verdict_msg, diag = compute_verdict(res, BANDS)
    elapsed = time.perf_counter() - t0

    pr = res["pass_records"]
    coverage_moved = (max(r["heldout_correct_cov_lenient"] for r in pr[1:]) - pr[0]["heldout_correct_cov_lenient"]) \
        if len(pr) > 1 else 0.0
    gate = {
        "discriminator_fires": bool(res["n_kg_edges_total"] > 0),
        "kg_edges_total": res["n_kg_edges_total"],
        "kg_heldout_relevant_total": res["n_kg_heldout_relevant_total"],
        "coverage_moved_guided_vs_cold": round(coverage_moved, 5),
        "real_baselines": {
            "cold_pass1": True,
            "naive_reread": bool(res["naive_records"]),
            "freq_only": res["freq_baseline_genus"] is not None,
            "freq_genus": res["freq_baseline_genus"],
        },
        "difficulty_on": "held-out sections' prose NEVER read; gold = held-out glossary genus; fair WN genus-match",
        "one_variable": "re-read / knowledge-guidance schedule (cold pass1 | guided pass2/3 | naive pass2)",
        "arms_differ_exempted": [["pass2_naive", "cold_pass1"]],
        "arms_differ_exempt_rationale": "naive re-read == cold pass-1 BY CONSTRUCTION is the deterministic-flat "
                                        "null the USER asked to demonstrate; guided-vs-naive equality would be "
                                        "HARD_FAIL_FLAT (handled in verdict), not an arm-bug.",
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "{}: cold={:.3f} best_guided={:.3f}(p{}) naive={:.3f} freq={:.3f} kg_ho_rel={}".format(
            verdict, diag.get("cold_pass1_cov_lenient", 0.0), diag.get("best_guided_cov_lenient", 0.0),
            diag.get("best_guided_pass", 0), diag.get("naive_reread_cov_lenient", 0.0),
            diag.get("freq_only_cov_lenient", 0.0), diag.get("n_kg_heldout_relevant_total", 0)),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "bands": BANDS,
        "diag": diag,
        "gate": gate,
        "pass_records": res["pass_records"],
        "naive_records": res["naive_records"],
        "kg_edges_per_pass": res["kg_edges_per_pass"],
        "kg_heldout_relevant_per_pass": res["kg_heldout_relevant_per_pass"],
        "n_kg_edges_total": res["n_kg_edges_total"],
        "n_kg_heldout_relevant_total": res["n_kg_heldout_relevant_total"],
        "freq_baseline_genus": res["freq_baseline_genus"],
        "freq_baseline_cc_strict": res["freq_baseline_cc_strict"],
        "freq_baseline_cc_lenient": res["freq_baseline_cc_lenient"],
        "n_sections": len(sections),
        "n_read_pool_sections": n_read_pool,
        "n_heldout_sections": n_heldout_sec,
        "n_gold_all": len(gold_all),
        "n_gold_heldout": len(gold_ho),
        "params": {"n_passes": args.n_passes, "genus_vocab_min": args.genus_vocab_min,
                   "coref_window": args.coref_window, "heldout_every": args.heldout_every},
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[{}] VERDICT={} {}".format(run_mode, verdict, metrics["summary"]), flush=True)
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
