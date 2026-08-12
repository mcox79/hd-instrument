"""exp_definitional_grounding_v5 -- TERM-BOUNDARY repair of the v4 definitional fact set.

Pre-reg: preregs/2026-08-12_definitional_term_boundary_v5.md (committed BEFORE this run).

WHAT CHANGES vs v4
  F7  hdlab/definitional_extraction: proper-name expansion may not cross punctuation
  F8  hdlab/definitional_extraction: the glossary split point is the LAST token before the colon
  F9  THIS CELL ONLY: a line-aware biology loader, so the OpenStax glossary is not flattened
      into 50 run-on pseudo-sentences before the parser ever sees it

F7/F8 are committed at e01db310b with a named regression test per real v4 row, INCLUDING all
eight director-confirmed F1 proper-noun gains. F9 is a SECOND VARIABLE and is declared as such
in the pre-reg; the cell therefore reports the corruption rate for BOTH arms so the director can
attribute the change.

NOT SCORED HERE. The cell writes an UNSCORED 50-row sample and claims no quality band. The
corruption rate, the yield triples, and the two out-of-scope fault counts ARE auto-reported:
they are counts against an on-disk ground truth, not judgements.

CELL-TEMPLATE MANDATORY:
 - final_metrics_atomicity: tmp_replace
 - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
 - start marker + crash metrics; heartbeat n/a (single ~60s pass)
 - crlb_n/a: deterministic symbolic extraction, no estimator noise floor; the feasibility bound
   is BINOMIAL and the band edges sit on it (se=7.0pp at n=50, p~0.45) -- see pre-reg
 - arms_differ_verified: v4 / PARSER_ONLY / CANONICAL fact sets are sha256-compared
 - discriminator-fires gate (META_RULE_K): corruption rate MUST fall below 4% or the cell
   emits HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE and no quality band may be read off the sample
 - cardinality n/a: no seed/sweep axis
 - deterministic_seeding: fixed seed 42; sorted(set(...)) only
ASCII-only.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import random
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class                 # noqa: E402
from hdlab.definitional_extraction import (                            # noqa: E402
    extract_definitions, split_glossary_entries, build_term)
from hdlab.hd_fact_store import HDFactStore                            # noqa: E402
from hdlab.low_information_filter import build_profile                 # noqa: E402
from hdlab.thematic_role_labeler import lemma_word                     # noqa: E402
from experiments.exp_definitional_grounding_v3 import (                # noqa: E402
    sample_for_audit, PMI_CONTROL_PAIRS, TOK)
from experiments.exp_definitional_grounding_v4 import build_def_v4     # noqa: E402

ANCHOR_NAME = "definitional_grounding_v5"
MEANING_RELATION = "GROUNDED_MEANING"
N_DIM = 2048
MAX_SOURCE_SENTENCES = 10

OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_definitional_grounding_v5")
NEW_FOUNDATION = os.path.join(REPO_ROOT, "data", "foundation",
                              "reading_grounding_v5_termboundary")
V4_FACTS = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v4_parsefix",
                        "definitional_facts_v4.jsonl")
BIO_CLEAN = os.path.join(REPO_ROOT, "data", "corpora", "textbook_concepts_biology",
                         "cleaned", "concepts_biology.clean.txt")

# The eight proper-noun rows the director CONFIRMED the v4 F1 fix got right. Losing any of them
# means the boundary fix undid the one thing that demonstrably worked (pre-reg
# HARD_FAIL_F1_REGRESSION).
F1_GAINS_MUST_SURVIVE = [
    ("Chon", "counsellor"), ("Naeem", "campaigner"), ("Olkin", "scientist"),
    ("Rajagopalan", "student"), ("Shanhui Fan", "expert"), ("Currie Technologies", "seller"),
    ("Piraeus", "port"), ("Drosophila", "fly"),
]
CONTROL_ROWS_MUST_SURVIVE = [
    ("aorta", "artery"), ("cholesterol", "lipid"), ("arthropoda", "phylum"),
    ("arteriole", "vessel"),
]
# v4's fault list + the three director-cited v4 TERM MERGES + the eight director-cited glossary
# corruptions. Every one must be absent from v5.
FAULT_ROWS_MUST_DIE = [
    ("fan", "expert"), ("technology", "seller"), ("kidney", "ureter"),
    ("system", "locomotion"), ("structure", "function"), ("dialysis", "medical"),
    ("kidney", "pair"), ("bubble", "region"), ("effect", "magnification"),
    ("DNA RNA", "polymer"), ("Mars Bas Lansdorp", "founder"),
    ("Wembley Stadium Bowie", "performer"),
    ("abiotic environment equilibrium", "state"), ("apex consumers biome", "community"),
    ("cell centrosome cleavage furrow", "constriction"),
    ("photosynthesis place thylakoid", "chloroplast"),
    ("postsynaptic membranes temporary", "memory"),
    ("secretes digestive juices", "enzyme"), ("body temperature endotherm", "organism"),
]


# ======================================================================== instrumentation
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_json(os.path.join(output_dir, "metrics.json"), {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME})


# ======================================================================== F9: line-aware corpus
def _clean_sentences(text: str) -> List[str]:
    """Byte-identical recipe to experiments.exp_reading_grounding_loop_cycle1_v1.clean_sentences.
    Duplicated (not imported) only so the v5 loader below can call it PER LINE."""
    # ASCII source: the sentence-final quote class is built with chr() so the two curly
    # variants cycle1's recipe carries literally never appear as non-ASCII bytes here.
    quotes = "'\"" + chr(0x2019) + chr(0x201d)
    parts = re.split("[.!?]+[" + quotes + "]?", text)
    return [s.strip() for s in parts if s.strip()]


def load_biology_sentences_lineaware(limit_sentences: Optional[int] = None
                                     ) -> List[Tuple[str, str]]:
    """F9. IDENTICAL to `exp_reading_grounding_loop_cycle2_v1.load_biology_sentences` except that
    the sentence split is applied PER LINE instead of over `" ".join(lines)`.

    Why this matters: the cleaned OpenStax file holds ONE GLOSSARY ENTRY PER LINE (line 8715 is
    exactly `equilibrium: the steady state of a system ...`), and glossary lines carry no
    terminal `.`, so joining them produces run-on pseudo-sentences up to 4776 chars in which the
    boundary between one entry and the next is unrecoverable. MEASURED: joined = 11332 sentences,
    50 of them >1000 chars, max 4776; per-line = 12559 sentences, 0 of them >1000 chars, max 591.
    A line boundary in a markdown-stripped file is a paragraph boundary, so splitting there
    cannot merge two halves of one real sentence -- it only ADDS boundaries that were already present.
    """
    with open(BIO_CLEAN, encoding="utf-8") as f:
        lines = f.readlines()
    out: List[Tuple[str, str]] = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"^\d+\.\s+", "", s)
        out.extend(("bio", x) for x in _clean_sentences(s))
    return out if limit_sentences is None else out[:limit_sentences]


def load_corpus_v5(limit: Optional[int], lineaware: bool) -> List[Tuple[str, str]]:
    """v3's corpus, with ONLY the bio_new loader swapped when `lineaware` is set."""
    from experiments.exp_reading_grounding_loop_cycle1_v1 import build_curriculum_pool
    from experiments.exp_reading_grounding_loop_cycle2_v1 import SEGMENT_POOL_LOADERS
    out: List[Tuple[str, str]] = [("bootstrap", s) for _t, s in build_curriculum_pool(limit)]
    for seg, loader in SEGMENT_POOL_LOADERS.items():
        if seg == "bio_new" and lineaware:
            loader = load_biology_sentences_lineaware
        out.extend((seg, s) for _t, s in loader(limit))
    return out


def build_profile_for(corpus):
    """IDENTICAL profile construction to v3/v4 so the PMI floor calibration is unchanged."""
    return build_profile([[lemma_word(t) for t in TOK.findall(s)] for _seg, s in corpus])


# ======================================================================== corruption audit
_BOUND_CH = set(".,;:()[]\"!?")
_BOUND_TOK = {"and", "or", "but", "nor", "is", "are", "was", "were", "has", "have", "had",
              "that", "which", "who", "said", "says", "then", "also", "when", "while",
              "because", "if", "from", "by", "with", "for", "to", "of", "in", "on", "at",
              "as", "into", "through", "during", "between", "among"}
_GLOSSARY_LINE = re.compile(r"^([A-Za-z][A-Za-z0-9'\-]*(?: [A-Za-z0-9'\-]+){0,5}): (.+)$")


def _norm_term(term: str) -> str:
    x = TOK.findall(term)
    if not x:
        return ""
    return " ".join([y.lower() for y in x[:-1]] + [lemma_word(x[-1])])


def true_glossary_keys() -> set:
    """GROUND TRUTH. The cleaned OpenStax file holds one glossary entry per LINE; those line
    boundaries are the true term boundaries and they exist on disk. Only the corpus loader's
    `" ".join(lines)` destroyed them."""
    keys = set()
    for ln in io.open(BIO_CLEAN, encoding="utf-8"):
        m = _GLOSSARY_LINE.match(ln.strip())
        if m and len(m.group(2)) > 15:
            keys.add(_norm_term(m.group(1)))
    return keys


def term_crosses_boundary(subject: str, sentence: str) -> Optional[str]:
    """T1 of the pre-reg's operational CORRUPTED definition. Locate the subject's tokens as an
    in-order MINIMAL window in `sentence` (closed-class tokens that build_term drops may be
    skipped); return the boundary class iff the raw text of that window contains a character or
    an interior token that cannot occur inside one term. None = clean."""
    st = [t.lower() for t in TOK.findall(subject)]
    if len(st) < 2:
        return None
    spans = [(m.group(0), m.start(), m.end()) for m in TOK.finditer(sentence)]
    low = [s[0].lower() for s in spans]
    best = None
    for i, t in enumerate(low):
        if t != st[0] and lemma_word(t) != st[0]:
            continue
        k, j = 0, i
        while j < len(low) and k < len(st):
            if low[j] == st[k] or lemma_word(low[j]) == st[k]:
                k += 1
            elif is_closed_class(lemma_word(low[j])) or low[j] in ("a", "an", "the"):
                pass
            else:
                break
            j += 1
        if k == len(st) and (best is None or (j - i) < best[1]):
            best = (i, j - i, j)
    if best is None:
        return "NOT_CONTIGUOUS"
    i, _w, j = best
    txt = sentence[spans[i][1]:spans[j - 1][2]]
    if any(c in _BOUND_CH for c in txt):
        return "PUNCT"
    inner = [t.lower() for t in TOK.findall(txt)][1:-1]
    if any(t in _BOUND_TOK for t in inner):
        return "FUNC"
    return None


def audit_corruption(rows: List[dict], gloss_keys: set) -> dict:
    """The pre-registered CORRUPTED rate. T1 OR T2. Reported as a LOWER BOUND -- T2 cannot fire
    when a corrupted term coincides with some OTHER valid glossary key, and T1 cannot fire on a
    same-clause merge with no punctuation."""
    t1 = Counter()
    n_t1 = n_t2 = n_gloss = 0
    flagged: List[dict] = []
    for r in rows:
        sent = (r.get("source_sentences") or [""])[0]
        a = term_crosses_boundary(r["subject"], sent)
        b = False
        if r.get("pattern") == "GLOSSARY_COLON" and r.get("segment") == "bio_new":
            n_gloss += 1
            b = _norm_term(r["subject"]) not in gloss_keys
        if a:
            n_t1 += 1
            t1[a] += 1
        if b:
            n_t2 += 1
        if a or b:
            flagged.append({"subject": r["subject"], "object": r["object"],
                            "pattern": r.get("pattern"), "test": a or "T2_GLOSSARY_KEY"})
    n = max(1, len(rows))
    return {
        "n_facts": len(rows),
        "T1_boundary_crossing": n_t1,
        "T1_by_class": dict(t1),
        "T2_glossary_key_mismatch": n_t2,
        "n_glossary_facts_evaluable": n_gloss,
        "T2_rate_within_glossary": round(n_t2 / max(1, n_gloss), 4),
        "n_corrupt": len(flagged),
        "corruption_rate": round(len(flagged) / n, 4),
        "note": "LOWER BOUND; see pre-reg s.MEASURED",
        "examples": flagged[:40],
    }


# ======================================================================== out-of-scope diagnostics
def audit_out_of_scope(rows: List[dict]) -> dict:
    """Counts for the two residual fault classes the director asked about but which this pass
    deliberately does NOT fix. REPORTED, NOT REPAIRED."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:                                      # noqa: BLE001 - degraded mode
        return {"available": False, "reason": "wordnet unavailable"}
    inverted, adj_head = [], []
    for r in rows:
        subj_l = (r.get("subject_head_lemma") or r["subject"]).lower()
        obj = r["object"].lower()
        # INVERTED HYPERNYMY: WordNet says the SUBJECT is a hypernym of the OBJECT, i.e. the
        # stored direction is the reverse of the taxonomic one (`bacteria -> fixation`-class).
        try:
            ss, so = wn.synsets(subj_l, pos="n"), wn.synsets(obj, pos="n")
        except Exception:                                  # noqa: BLE001
            continue
        if ss and so:
            up_from_obj = {h.name().split(".")[0] for s in so[:3]
                           for p in s.hypernym_paths() for h in p}
            up_from_subj = {h.name().split(".")[0] for s in ss[:3]
                            for p in s.hypernym_paths() for h in p}
            if subj_l in up_from_obj and obj not in up_from_subj:
                inverted.append("%s -> %s" % (r["subject"], r["object"]))
        # ADJECTIVAL HEAD: WordNet knows the object ONLY as an adjective/adverb.
        if not wn.synsets(obj, pos="n") and wn.synsets(obj):
            adj_head.append("%s -> %s" % (r["subject"], r["object"]))
    n = max(1, len(rows))
    return {
        "available": True,
        "IN_SCOPE": False,
        "note": "REPORTED NOT REPAIRED. Inverted hypernymy is NOT a parse bug -- it is not "
                "knowing which side of a definition carries the genus. The v5 term-boundary "
                "fix does not touch it.",
        "n_inverted_hypernymy": len(inverted),
        "rate_inverted_hypernymy": round(len(inverted) / n, 4),
        "examples_inverted": sorted(inverted)[:25],
        "n_adjectival_head": len(adj_head),
        "rate_adjectival_head": round(len(adj_head) / n, 4),
        "examples_adjectival": sorted(adj_head)[:25],
    }


# ======================================================================== yield
def multisense_yield(rows: List[dict], key: str) -> dict:
    by_subj = defaultdict(set)
    for r in rows:
        k = r.get(key)
        if k:
            by_subj[k].add(r["object"])
    multi = {s for s, o in by_subj.items() if len(o) > 1}
    in_multi = [r for r in rows if r.get(key) in multi]
    per_word = defaultdict(list)
    for r in in_multi:
        per_word[r[key]].append(len(r.get("source_sentences") or []))
    return {
        "key": key,
        "n_facts": len(rows),
        "n_distinct_subjects": len(by_subj),
        "n_multi_sense_words": len(multi),
        "n_facts_in_multi_sense_words": len(in_multi),
        "n_senses_with_gt1_source_sentence": sum(
            1 for r in in_multi if len(r.get("source_sentences") or []) > 1),
        "n_multi_sense_words_with_ANY_sense_gt1_sentence": sum(
            1 for v in per_word.values() if any(x > 1 for x in v)),
        "n_multi_sense_words_with_ALL_senses_gt1_sentence": sum(
            1 for v in per_word.values() if all(x > 1 for x in v)),
        "triple_words_senses_allmulti": [
            len(multi),
            sum(1 for r in in_multi if len(r.get("source_sentences") or []) > 1),
            sum(1 for v in per_word.values() if all(x > 1 for x in v))],
    }


def _digest(rows: List[dict]) -> str:
    h = hashlib.sha256()
    for r in rows:
        h.update(("%s|%s\n" % (r["subject"], r["object"])).encode("utf-8"))
    return h.hexdigest()


# ======================================================================== self-test
def _selftest_sampling_is_identical() -> None:
    facts = [{"subject": "s%d" % i, "object": "o%d" % i} for i in range(634)]
    got = sample_for_audit(facts, k=50, seed=42)
    rng = random.Random(42)
    expect = sorted(rng.sample(range(634), 50))
    assert [f["subject"] for f in got] == ["s%d" % i for i in expect], "HARD_FAIL_SAMPLING_DRIFT"


def _selftest_corruption_detector() -> None:
    """The detector must FIRE on the director's three named non-glossary merges and must NOT fire
    on the F1 gains. A detector that flags everything would make the discriminator vacuous."""
    assert term_crosses_boundary("DNA RNA", "Like DNA, RNA is a polymer of nucleotides") == "PUNCT"
    assert term_crosses_boundary(
        "Wembley Stadium Bowie",
        "At the concert at Wembley Stadium, Bowie was one of the best performers") == "PUNCT"
    assert term_crosses_boundary(
        "Shanhui Fan", "said Shanhui Fan, an expert in the study of light") is None
    assert term_crosses_boundary(
        "Currie Technologies", "CEO of Currie Technologies, the number one seller") is None
    assert term_crosses_boundary("Piraeus", "I would dock in Piraeus, the port") is None
    keys = true_glossary_keys()
    assert len(keys) > 800, len(keys)
    assert "equilibrium" in keys and "biome" in keys, "glossary ground truth not recovered"
    assert _norm_term("abiotic environment equilibrium") not in keys
    assert _norm_term("detrital food web") in keys


def _selftest_real_code_path_tiny() -> dict:
    """Exercise the REAL objects the FULL run uses (extractor, term builder, glossary splitter,
    profile, HDFactStore) at N~7."""
    exercised = set()
    corpus = [
        ("bio_new", "equilibrium: the steady state of a system in which relationships hold"),
        ("bio_new", "detrital food web: a type of food chain supported by decaying organisms"),
        ("bio_new", "The region of unwinding is called a transcription bubble"),
        ("adv_new", "Like DNA, RNA is a polymer of nucleotides"),
        ("adv_new", "At the concert at Wembley Stadium, Bowie was one of the best performers"),
        ("bootstrap", "I would dock in Piraeus, the port in Athens, take my pay"),
        ("bootstrap", "You can offset the electricity, said Shanhui Fan, an expert in the "
                      "study of light at Stanford University, who led the work"),
    ]
    exercised.add("split_glossary_entries")
    assert split_glossary_entries(corpus[0][1]) == [corpus[0][1]], "line-aware entry got split"
    exercised.add("build_term")
    assert build_term("Dialysis", "Dialysis is a medical process") == ("dialysis", "COMMON")
    exercised.add("build_profile")
    prof = build_profile_for(corpus * 6)
    exercised.add("extract_definitions")
    facts, refusals = build_def_v4(corpus, prof)
    pairs = {(f["subject"], f["object"]) for f in facts}
    assert ("Piraeus", "port") in pairs, pairs
    assert ("Shanhui Fan", "expert") in pairs, pairs
    assert not any(s == "DNA RNA" for s, _o in pairs), pairs
    assert not any(s.startswith("Wembley") for s, _o in pairs), pairs
    assert not any(s == "fan" for s, _o in pairs), pairs
    exercised.add("HDFactStore")
    store = HDFactStore(n_dim=N_DIM, seed=0)
    for f in facts:
        store.store(f["subject"], MEANING_RELATION, f["object"], "definitional:selftest",
                    "TRUST_MID")
    assert len(store.live_facts()) == len(facts), (len(store.live_facts()), len(facts))
    exercised.add("load_biology_sentences_lineaware")
    bio = load_biology_sentences_lineaware(50)
    assert len(bio) == 50 and all(len(s) < 2000 for _t, s in bio)
    declared = {"extract_definitions", "build_term", "split_glossary_entries", "HDFactStore",
                "build_profile", "load_biology_sentences_lineaware"}
    missing = declared - exercised
    assert not missing, "F.1 real_code_path: declared but not exercised: %s" % sorted(missing)
    return {"n_selftest_facts": len(facts), "pairs": sorted("%s|%s" % p for p in pairs),
            "refusals": dict(refusals), "exercised": sorted(exercised)}


def run_self_test() -> dict:
    t0 = time.perf_counter()
    _selftest_sampling_is_identical()
    _selftest_corruption_detector()
    tiny = _selftest_real_code_path_tiny()
    return {"verdict": "SELFTEST_PASS",
            "verdict_msg": "sampling identical + corruption detector calibrated + real code path",
            "summary": "selftest", "elapsed_s": round(time.perf_counter() - t0, 2), "tiny": tiny}


# ======================================================================== full
def run_full(limit: Optional[int]) -> dict:
    t0 = time.perf_counter()
    gloss_keys = true_glossary_keys()

    print("[progress] building PARSER_ONLY arm (v4 loader + F7/F8)", flush=True)
    corpus_joined = load_corpus_v5(limit, lineaware=False)
    prof_joined = build_profile_for(corpus_joined)
    facts_parser, refusals_parser = build_def_v4(corpus_joined, prof_joined)

    print("[progress] building CANONICAL arm (line-aware loader + F7/F8)", flush=True)
    corpus_line = load_corpus_v5(limit, lineaware=True)
    prof = build_profile_for(corpus_line)

    calib = {}
    for a, b in PMI_CONTROL_PAIRS:
        ok, reason = prof.eligible_meaning(a, b)
        calib["%s->%s" % (a, b)] = {"survives": bool(ok), "pmi": prof.pmi(a, b),
                                    "refusal": reason}
    survivors = sum(1 for v in calib.values() if v["survives"])
    if limit is None and survivors < len(PMI_CONTROL_PAIRS) - 1:
        raise AssertionError("BLOCK_DISPATCH_calibration_check: %r" % calib)

    facts, refusals = build_def_v4(corpus_line, prof)
    print("[progress] parser_only=%d canonical=%d" % (len(facts_parser), len(facts)), flush=True)

    v4 = [json.loads(l) for l in io.open(V4_FACTS, encoding="utf-8") if l.strip()]
    v4_pairs = {(r["subject"], r["object"]) for r in v4}
    v5_pairs = {(r["subject"], r["object"]) for r in facts}

    audit_v4 = audit_corruption(v4, gloss_keys)
    audit_parser = audit_corruption(facts_parser, gloss_keys)
    audit_canon = audit_corruption(facts, gloss_keys)

    checks = {
        "arms_differ_verified": len({_digest(v4), _digest(facts_parser), _digest(facts)}) == 3,
        "f1_gains_survived": {"%s|%s" % p: (p in v5_pairs) for p in F1_GAINS_MUST_SURVIVE},
        "control_rows_survived": {"%s|%s" % p: (p in v5_pairs)
                                  for p in CONTROL_ROWS_MUST_SURVIVE},
        "fault_rows_removed": {"%s|%s" % p: (p not in v5_pairs) for p in FAULT_ROWS_MUST_DIE},
        "v3_collision_keys_absent": {
            "fan": not any(s == "fan" for s, _o in v5_pairs),
            "technology": not any(s == "technology" for s, _o in v5_pairs)},
    }

    y_term_v4 = multisense_yield(v4, "subject")
    y_head_v4 = multisense_yield(v4, "subject_head_lemma")
    y_term = multisense_yield(facts, "subject")
    y_head = multisense_yield(facts, "subject_head_lemma")

    verdict, msgs = "STRUCTURAL_PASS_PENDING_B3", []
    if audit_canon["corruption_rate"] > 0.04:
        verdict = "HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE"
        msgs.append("corruption %.1f%% > 4%% (META_RULE_K vacuity guard)"
                    % (100 * audit_canon["corruption_rate"]))
    if len(facts) < 900:
        verdict = "HARD_FAIL_YIELD_COLLAPSE"
        msgs.append("v5 facts %d < 900" % len(facts))
    if not checks["arms_differ_verified"]:
        verdict = "BLOCK_DISPATCH_META_RULE_AF"
        msgs.append("two arms produced identical fact sets")
    if not all(checks["f1_gains_survived"].values()):
        verdict = "HARD_FAIL_F1_REGRESSION"
        msgs.append("F1 gains lost: %s"
                    % [k for k, v in checks["f1_gains_survived"].items() if not v])
    if not all(checks["control_rows_survived"].values()):
        verdict = "HARD_FAIL_CONTROL_ROWS"
        msgs.append("controls lost: %s"
                    % [k for k, v in checks["control_rows_survived"].items() if not v])
    if not all(checks["fault_rows_removed"].values()):
        verdict = "HARD_FAIL_REGRESSION"
        msgs.append("faults still present: %s"
                    % [k for k, v in checks["fault_rows_removed"].items() if not v])

    os.makedirs(NEW_FOUNDATION, exist_ok=True)
    fpath = os.path.join(NEW_FOUNDATION, "definitional_facts_v5.jsonl")
    tmp = fpath + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for r in facts:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, fpath)

    sample_path = os.path.join(OUT_DIR, "b3_audit_sample_DEF_V5.json")
    _atomic_write_json(sample_path, {
        "arm": "DEF_V5_TERM_BOUNDARY",
        "n_facts_in_arm": len(facts),
        "sample_seed": 42,
        "sampling": "random.Random(42).sample over fid order -- BIT-IDENTICAL to v2/v3/v4 B3, "
                    "asserted in run_self_test",
        "rubric": "MEANINGFUL / RELATED / NOISE per "
                  "notes/foundation_grounding_sample_2026-08-12.md",
        "scored": False,
        "note": "UNSCORED. The cell assigns no buckets and claims no quality band. Baselines: "
                "v3 DEF 38% and v4 DEF 40% MEANINGFUL "
                "(notes/director_handscore_b3_v4_parsefix_2026-08-12.md). Bands + the explicit "
                "FALSIFIER: preregs/2026-08-12_definitional_term_boundary_v5.md",
        "rows": sample_for_audit(facts)})

    return {
        "verdict": verdict,
        "verdict_msg": (
            "v5 term-boundary: %d facts (v4 1956, %+d); corruption %.1f%% -> %.1f%% "
            "(parser-only arm %.1f%%); %s"
            % (len(facts), len(facts) - len(v4), 100 * audit_v4["corruption_rate"],
               100 * audit_canon["corruption_rate"], 100 * audit_parser["corruption_rate"],
               "; ".join(msgs) if msgs else "all machine checks pass")),
        "summary": "definitional term-boundary repair v5",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "run_mode": "full" if limit is None else "smoke",
        "n_facts_v4": len(v4), "n_facts_v5": len(facts),
        "n_facts_v5_parser_only_arm": len(facts_parser),
        "n_pairs_kept_from_v4": len(v4_pairs & v5_pairs),
        "n_pairs_new_in_v5": len(v5_pairs - v4_pairs),
        "n_pairs_dropped_from_v4": len(v4_pairs - v5_pairs),
        "subject_type_mix": dict(Counter(f["subject_type"] for f in facts)),
        "multiword_subject_count": sum(1 for f in facts if " " in f["subject"]),
        "pattern_mix": dict(Counter(f["pattern"] for f in facts)),
        "segment_mix": dict(Counter(f["segment"] for f in facts)),
        "refusals": dict(refusals),
        "refusals_parser_only_arm": dict(refusals_parser),
        "checks": checks,
        "pmi_calibration_controls": calib,
        "corruption_audit_v4_BEFORE": audit_v4,
        "corruption_audit_v5_parser_only": audit_parser,
        "corruption_audit_v5_CANONICAL": audit_canon,
        "out_of_scope_faults_v4": audit_out_of_scope(v4),
        "out_of_scope_faults_v5": audit_out_of_scope(facts),
        "multisense_yield_v4_term": y_term_v4["triple_words_senses_allmulti"],
        "multisense_yield_v4_head_lemma": y_head_v4["triple_words_senses_allmulti"],
        "multisense_yield_v5_term": y_term["triple_words_senses_allmulti"],
        "multisense_yield_v5_head_lemma": y_head["triple_words_senses_allmulti"],
        "multisense_yield_v5_term_FULL": y_term,
        "multisense_yield_v5_head_lemma_FULL": y_head,
        "b3_audit_sample_path": sample_path,
        "facts_path": fpath,
        "prereg": "preregs/2026-08-12_definitional_term_boundary_v5.md",
        "quality_scored_here": False,
        "wire_status": "VET_PENDING",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if args.mode == "self-test":
        m = run_self_test()
        _atomic_write_json(os.path.join(OUT_DIR, "selftest_metrics.json"), m)
        print(json.dumps(m, indent=2)[:2500])
        return
    _write_start_marker(OUT_DIR, args.mode)
    limit = args.limit if args.limit is not None else (400 if args.mode == "smoke" else None)
    m = run_full(limit)
    out = os.path.join(OUT_DIR, "metrics.json" if args.mode == "full" else "smoke_metrics.json")
    _atomic_write_json(out, m)
    print(json.dumps({k: v for k, v in m.items()
                      if k not in ("multisense_yield_v5_term_FULL",
                                   "multisense_yield_v5_head_lemma_FULL")},
                     indent=2)[:6000])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUT_DIR, e)
        raise
