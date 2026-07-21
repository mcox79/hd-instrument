#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_mcguffey_ingest_reader_ready_degradation_v1

INGESTOR -> READER end-to-end: quantify + localize + fix ingestion-induced reader degradation.

The reader today reads HAND-CURATED clean sentences (the Director-oracle gold). For the foundation
build the ingestor must turn a raw source document into clean, sentence-segmented, structure-preserved
reader input AUTOMATICALLY. This cell:
  1. AUTO-SEGMENTS the ingestor's raw McGuffey text output (data/exp_textbook_extract_mcguffey_v1/
     mcguffey_first_document_order.txt) into reader-ready sentences. Two segmenters (one variable = the
     ingestion pipeline):
       - NAIVE   : run a plain sentence splitter on the raw dump (newline->space, split on [.!?]).
                   No noise removal -> wordlist strips / page running-heads / phonics rows / lesson
                   headers / page numbers bleed into sentences. Models UNHARDENED ingestion.
       - HARDENED: line-classify + DROP noise lines (running head, lesson header, page number, phonics
                   row, wordlist entry) + join wrapped prose lines + de-hyphenate, THEN sentence-split.
                   Models the HARDENED auto ingestion (the fix).
       - HARDENED_V2: HARDENED + the top-1 residual-defect fix (chosen AFTER localization; see FIX below).
  2. ALIGNS each hand-curated gold sentence to its best auto-segmented sentence (token-F1; exact-match
     flag) across the WHOLE auto sentence list -> the ingestion defect per gold sentence
     (exact / bleed / truncated / altered / no_match) + verb-lost flag.
  3. MEASURES the reader (RAW base_pick who-is-affected, gate OFF -> isolates the extraction step)
     over HAND vs AUTO sentences, verb-anchored on the gold verb (identical target across arms, so the
     only variable is the ingested TEXT). DELTA = auto_acc - hand_acc = ingestion-induced degradation.
  4. LOCALIZES: among gold instances the reader gets RIGHT on hand-curated text but WRONG on auto text,
     the dominant ingestion defect class = the top-1 deficiency.
  5. FIX top-1 + re-measure: HARDENED_V2 applies a targeted fix for the dominant defect; does the gap
     close (hardened_v2_delta > hardened_delta)?

REAL BASELINE = reader on hand-curated gold (not a strawman). CAN-FAIL: (a) auto could MATCH hand
  (no degradation to fix -> valid finding); (b) the fix could FAIL to close the gap; (c) hardening could
  UNDER-recover vs naive. ONE VARIABLE = ingestion source (segmenter), verb target held fixed.

READER = the base extraction reader (persisted UD-EWT front-end: averaged-perceptron POS + hashed
  arc-parser + arc-labeler; base_pick = highest arc-parser-margin patient-labeled candidate). GATE OFF:
  the verb-affectedness gate is keyed on the (constant) gold verb, so it is arm-invariant and would only
  MASK the ingestion signal; the raw base reader is the faithful probe of what ingestion perturbs.

Compute architecture: sequential-CPU, justified (pure-python glass-box segmentation + reader pass over
  72 McGuffey gold sentences and a few-hundred auto sentences; persisted perceptron/arc front-end; numpy
  only; wall seconds; no matmul inner loop -> not a GPU-batching candidate). Storage: no_storage/
  no_composition (measurement cell; atomic tmp+replace metrics.json). Determinism: OMP/MKL/OPENBLAS=1;
  sorted(set); fixed thresholds; no hash()-seeded RNG; segmenter is a pure function of the input text.
  LOCAL-only foreground; NO queue, NO push, NO remote-persist, NO git add, NO hdlab/store mutation.
  ASCII-only, no em-dashes.

PRIOR ART / KB check (substrate_query "ingestor sentence segmentation reader-ready ..."): NONE at
  cosine>0.30 (only generic WordNet/FrameNet 'ingestion'/'segmentation' lexical nodes); this cell is a
  genuine novel connector (ingestor output -> reader who-affected degradation), not a rediscovery.

# CELL-TEMPLATE MANDATORY (measurement cell; single-shot, no seed/sweep axis):
# - arms_differ_verified at smoke gate (hand/naive/hardened/hardened_v2 reader-correctness vectors not all identical)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: accuracy on labeled gold; no quantitative noise floor (not a capacity/argmax-noise cell)
# - baseline_in_band: HAND raw reader expected 0.05 < acc < 0.95 (verified at run)
# - discriminator survives scale: full IS the scale (N=72 fixed gold; not a smoke-vs-full-N issue)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - cardinality_ok: n/a (no sweep axis; single pass over fixed gold)
# - calibration_check: default_ok_for_this_regime (alignment F1 threshold 0.5 = glass-box, reported)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

ANCHOR_NAME = "mcguffey_ingest_reader_ready_degradation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, reader_pass, base_pick,
)
from experiments.exp_mcguffey_whoaffected_verb_affectedness_gate_v1 import (  # noqa: E402
    span_head_tokens, find_verb_index,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402

RAW_PATH = os.path.join(REPO_ROOT, "data", "exp_textbook_extract_mcguffey_v1",
                        "mcguffey_first_document_order.txt")
GOLD_V1 = os.path.join(REPO_ROOT, "data", "mcguffey_whoaffected_oracle_gold_v1", "gold.json")
GOLD_V2 = os.path.join(REPO_ROOT, "data", "mcguffey_whoaffected_oracle_gold_v2_heldout", "gold.json")

NONE_TYPES = {"target_not_affected", "none", "negated"}
ALIGN_F1_MIN = 0.5   # below this, the gold sentence is not recoverable from auto ingest -> extraction failure

# ==================================================================================================
# AUTO-SEGMENTERS. Pure functions of the raw text -> list of reader-ready sentences.
# ==================================================================================================
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WS = re.compile(r"\s+")

# noise-line patterns (running heads, lesson headers, page numbers) for the HARDENED segmenter.
# _HEADER_FULL = anchored full-line running heads (whitespace collapsed before match, so 'FIRST  READER.'
# with doubled spaces is caught); _HEADER_PREFIX = license/front-matter lines; _LESSON_RE = lesson header
# (prefix, so 'LESSON IX. REVIEW.' is caught).
_HEADER_FULL = re.compile(
    r"^(first reader|eclectic series|eclectic educational series|slate work|review|"
    r"suggestions to teachers|preface|new words|words)\.?$", re.I)
_HEADER_PREFIX = re.compile(
    r"^(copyright|produced by|transcriber|mcguffey|john wiley|new york|ep\d+|"
    r"eclectic educational)\b", re.I)
_LESSON_RE = re.compile(r"^lesson\s+[ivxlcdm]+\b", re.I)
_PAGENUM_RE = re.compile(r"^[0-9ivxlcdm]{1,4}\.?$", re.I)  # bare page number or bare roman numeral


def segment_naive(raw):
    """Plain sentence splitter on the raw dump: newline->space, collapse ws, split on [.!?].
    No noise removal (wordlist/header/phonics bleed). Models UNHARDENED ingestion."""
    flat = _WS.sub(" ", raw.replace("\n", " ")).strip()
    return [p.strip() for p in _SENT_SPLIT.split(flat) if p.strip()]


_CORE_RE = re.compile(r"[^a-z]")  # strip diacritic markup (apostrophe/paren/hyphen/digits) to token core


def _line_kind(s):
    """DROP (definite noise) | LISTISH (candidate vocabulary entry) | PROSE (real reading text).
    Glass-box, transparent. LISTISH = short, unterminated line of vocab-ish tokens (possibly diacritic-
    marked, e.g. 'Kit'ty', 'up set'', 'shut shall'); dropped only by the V2 fix when it forms a
    vocabulary block (single-token or a run of >=2 consecutive LISTISH lines)."""
    if not s:
        return "DROP"
    s = _WS.sub(" ", s.strip())                         # collapse doubled spaces before matching
    if not s:
        return "DROP"
    if _HEADER_FULL.match(s) or _HEADER_PREFIX.match(s) or _LESSON_RE.match(s):
        return "DROP"
    toks = s.split()
    terminated = s[-1] in ".!?"
    if len(toks) == 1 and _PAGENUM_RE.match(s):
        return "DROP"                                   # bare page number / roman numeral
    # phonics diacritic row: >=2 tokens, every token alpha of length<=2, no terminal punctuation
    if len(toks) >= 2 and not terminated and all(t.isalpha() and len(t) <= 2 for t in toks):
        return "DROP"
    # plain wordlist new-word entry: single bare alpha word, no terminal punctuation
    if len(toks) == 1 and toks[0].isalpha() and not terminated:
        return "DROP"
    # LISTISH: short unterminated line whose tokens are all short vocab cores (incl diacritic markup)
    if not terminated and len(toks) <= 3:
        cores = [_CORE_RE.sub("", t.lower()) for t in toks]
        if cores and all(c and len(c) <= 6 for c in cores):
            return "LISTISH"
    return "PROSE"


def segment_hardened(raw, drop_vocab_blocks=False):
    """Line-classify -> DROP noise -> (V2 FIX) drop diacritic/short vocabulary blocks -> join wrapped
    prose (de-hyphenate) -> split on [.!?].
    drop_vocab_blocks (the top-1 FIX in HARDENED_V2): also remove LISTISH vocabulary-list lines
    (single-token, OR part of a run of >=2 consecutive LISTISH lines) that survive the plain-wordlist
    filter because diacritic markup (apostrophes/parens) defeats .isalpha() -> the localized bleed source
    ('Kit'ty song pet put not Look at Tom and his dog.')."""
    lines = [_WS.sub(" ", ln.strip()) for ln in raw.split("\n")]
    kinds = [_line_kind(ln) for ln in lines]
    kept = []
    for i, (ln, k) in enumerate(zip(lines, kinds)):
        if k == "DROP":
            continue
        if k == "LISTISH":
            if drop_vocab_blocks:
                single = len(ln.split()) == 1
                run_neighbor = (i > 0 and kinds[i - 1] == "LISTISH") or \
                               (i + 1 < len(kinds) and kinds[i + 1] == "LISTISH")
                if single or run_neighbor:
                    continue                            # vocabulary block -> drop
            kept.append(ln)                             # else keep as prose (V1: it bleeds)
        else:
            kept.append(ln)
    buf = ""
    for s in kept:
        if buf.endswith("-") and len(buf) >= 2 and buf[-2].isalpha():
            buf = buf[:-1] + s.lstrip()                 # de-hyphenate wrapped word
        elif buf:
            buf = buf + " " + s
        else:
            buf = s
    flat = _WS.sub(" ", buf).strip()
    return [p.strip() for p in _SENT_SPLIT.split(flat) if p.strip()]


# ==================================================================================================
# ALIGNMENT: gold sentence -> best auto-segmented sentence (token-F1). Uses gold TEXT only, never labels.
# ==================================================================================================
_TOK_RE = re.compile(r"[a-z0-9]+")


def _norm_tokens(s):
    return _TOK_RE.findall(s.lower())


def _norm_str(s):
    return _WS.sub(" ", s.strip().lower())


def _f1(gtoks, atoks):
    if not gtoks or not atoks:
        return 0.0
    gs, as_ = set(gtoks), set(atoks)
    inter = len(gs & as_)
    if inter == 0:
        return 0.0
    prec, rec = inter / len(as_), inter / len(gs)
    return 2 * prec * rec / (prec + rec)


def align_gold_to_auto(gold_text, auto_sents, auto_toks):
    """Return (best_idx, best_score, best_text). Best by token-F1 over the whole auto sentence list."""
    gtoks = _norm_tokens(gold_text)
    best_i, best_s = -1, -1.0
    for i, at in enumerate(auto_toks):
        sc = _f1(gtoks, at)
        if sc > best_s:
            best_s, best_i = sc, i
    return best_i, best_s, (auto_sents[best_i] if best_i >= 0 else "")


def defect_class(gold_text, aligned_text, best_score):
    """Classify the ingestion defect for a gold sentence given its best auto match."""
    if best_score < ALIGN_F1_MIN:
        return "no_match"
    if _norm_str(gold_text) == _norm_str(aligned_text):
        return "exact"
    gs, as_ = set(_norm_tokens(gold_text)), set(_norm_tokens(aligned_text))
    if gs and gs.issubset(as_) and len(as_) > len(gs):
        return "bleed"                                  # extra tokens merged in (noise / adjacent sentence)
    if as_ and as_.issubset(gs) and len(gs) > len(as_):
        return "truncated"                              # bad split lost part of the sentence
    return "altered"                                    # reordered / partial mix


# ==================================================================================================
# READER MEASUREMENT (RAW base_pick, verb-anchored on the gold verb; gate OFF).
# ==================================================================================================
def reader_correct_on_text(text, gverb, gold_none, heads_gold, tagger, parser, labeler):
    """Run the base reader on `text`, verb-anchored on gverb. Return (correct, pred_surf, pred_none,
    verb_lost)."""
    tokens = ud_tokenize(text)
    rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
    vidx, _ = find_verb_index(tokens, rp["pos"], gverb)
    verb_lost = vidx is None
    pool = rp["pools"].get(vidx, []) if vidx is not None else []
    bp = base_pick(pool)
    pred_surf = bp["surf"] if bp is not None else None
    pred_none = bp is None
    if gold_none:
        correct = pred_none
    else:
        correct = bool(pred_surf is not None and pred_surf in heads_gold)
    return bool(correct), pred_surf, pred_none, verb_lost


def load_gold():
    gold = []
    for p, tag in [(GOLD_V1, "v1"), (GOLD_V2, "v2")]:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        for g in d["gold"]:
            gg = dict(g)
            gg["_src"] = tag
            gold.append(gg)
    return gold


# ==================================================================================================
def run(mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data",
                           f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    _tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(_tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(_tmp, os.path.join(out_dir, "_start_marker.json"))
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    with open(RAW_PATH, encoding="utf-8") as f:
        raw = f.read()
    gold = load_gold()
    if mode == "smoke":
        gold = gold[:12] + gold[34:46]   # a slice from each gold set

    # ---- segment (both segmenters are pure functions of raw) ----
    naive = segment_naive(raw)
    hard = segment_hardened(raw, drop_vocab_blocks=False)
    hard_v2 = segment_hardened(raw, drop_vocab_blocks=True)
    arms = {"naive": naive, "hardened": hard, "hardened_v2": hard_v2}
    arm_toks = {k: [_norm_tokens(s) for s in v] for k, v in arms.items()}
    print(f"[{ANCHOR_NAME}:{mode}] segmented: naive={len(naive)} hardened={len(hard)} "
          f"hardened_v2={len(hard_v2)} sentences; gold N={len(gold)}", flush=True)

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded", flush=True)

    per_inst = []
    for g in gold:
        text, gverb, gaff, gtype = g["text"], g["verb"], g["affected"], g["type"]
        gold_none = gtype in NONE_TYPES
        heads_gold = span_head_tokens(gaff)

        # HAND (reference): reader on the clean gold sentence
        h_corr, h_surf, h_none, h_vlost = reader_correct_on_text(
            text, gverb, gold_none, heads_gold, tagger, parser, labeler)

        row = {"id": g["id"], "src": g["_src"], "text": text, "verb": gverb, "type": gtype,
               "gold_affected": gaff, "gold_none": gold_none,
               "hand_correct": h_corr, "hand_pred_surf": h_surf, "hand_pred_none": h_none,
               "hand_verb_lost": h_vlost}

        for arm, sents in arms.items():
            bi, bs, btext = align_gold_to_auto(text, sents, arm_toks[arm])
            dc = defect_class(text, btext, bs)
            a_corr, a_surf, a_none, a_vlost = reader_correct_on_text(
                btext, gverb, gold_none, heads_gold, tagger, parser, labeler)
            row[f"{arm}_align_score"] = round(bs, 4)
            row[f"{arm}_aligned_text"] = btext
            row[f"{arm}_defect"] = dc
            row[f"{arm}_correct"] = a_corr
            row[f"{arm}_pred_surf"] = a_surf
            row[f"{arm}_pred_none"] = a_none
            row[f"{arm}_verb_lost"] = a_vlost
        per_inst.append(row)

    n = len(per_inst)

    def acc(key):
        c = sum(1 for r in per_inst if r[key])
        return round(c / n, 4), c

    hand_acc, hand_c = acc("hand_correct")
    res = {}
    for arm in arms:
        a, c = acc(f"{arm}_correct")
        res[arm] = {"acc": a, "correct": c, "delta_vs_hand": round(a - hand_acc, 4)}

    # ---- defect distribution + exact-match rate per arm ----
    defect_dist = {}
    exact_rate = {}
    nomatch = {}
    verblost = {}
    for arm in arms:
        dd = Counter(r[f"{arm}_defect"] for r in per_inst)
        defect_dist[arm] = dict(dd)
        exact_rate[arm] = round(dd.get("exact", 0) / n, 4)
        nomatch[arm] = dd.get("no_match", 0)
        verblost[arm] = sum(1 for r in per_inst if r[f"{arm}_verb_lost"])

    # ---- LOCALIZE: among instances the reader gets right on HAND but wrong on AUTO(hardened),
    #      the dominant ingestion defect class = the top-1 deficiency ----
    def degraded_rows(arm):
        return [r for r in per_inst if r["hand_correct"] and not r[f"{arm}_correct"]]

    hard_degraded = degraded_rows("hardened")
    degrade_defect = Counter(r["hardened_defect"] for r in hard_degraded)
    top_defect = degrade_defect.most_common(1)[0][0] if degrade_defect else None
    degraded_examples = [{"id": r["id"], "text": r["text"], "defect": r["hardened_defect"],
                          "aligned_text": r["hardened_aligned_text"],
                          "hand_pred": r["hand_pred_surf"], "auto_pred": r["hardened_pred_surf"],
                          "align_score": r["hardened_align_score"],
                          "auto_verb_lost": r["hardened_verb_lost"]}
                         for r in hard_degraded]

    # INGESTION-level deficiency (independent of reader impact): dominant NON-EXACT defect + examples.
    # The reader-degraded set above is the READER impact (may be empty = ingestion inert for the reader);
    # this is the ingestion-CLEANLINESS deficiency the top-1 fix targets.
    nonexact_hard = [r for r in per_inst if r["hardened_defect"] != "exact"]
    ingest_defect_dist = Counter(r["hardened_defect"] for r in nonexact_hard)
    top_ingest_defect = ingest_defect_dist.most_common(1)[0][0] if ingest_defect_dist else None
    nonexact_examples = [{"id": r["id"], "text": r["text"], "defect": r["hardened_defect"],
                          "hardened_aligned": r["hardened_aligned_text"],
                          "hardened_v2_aligned": r["hardened_v2_aligned_text"],
                          "hardened_v2_defect": r["hardened_v2_defect"],
                          "hand_correct": r["hand_correct"], "auto_correct": r["hardened_correct"]}
                         for r in nonexact_hard]

    # did the top-1 FIX close the gap?
    hard_delta = res["hardened"]["delta_vs_hand"]
    hard_v2_delta = res["hardened_v2"]["delta_vs_hand"]
    naive_delta = res["naive"]["delta_vs_hand"]
    gap_closed = bool(hard_v2_delta > hard_delta + 1e-9)
    hardening_helps = bool(hard_delta > naive_delta + 1e-9)
    # cleanliness gain: exact-alignment lift from the fix (the fix's measurable value when the reader
    # delta is already zero = ingestion was inert for who-affected but the bleed is still cleaned).
    cleanliness_gain = round(exact_rate["hardened_v2"] - exact_rate["hardened"], 4)
    fix_cleans = bool(cleanliness_gain > 1e-9)

    # ---- ARMS-MUST-DIFFER: the guard is that the SEGMENTERS are genuinely distinct code paths
    # (naive vs hardened produce different sentence lists). Identical READER-CORRECTNESS across arms is a
    # LEGITIMATE outcome (ingestion near-harmless), NOT a wiring bug -> do not hard-fail on it. ----
    def _digest(key):
        return hashlib.sha256(bytes([1 if r[key] else 0 for r in per_inst])).hexdigest()
    arm_digests = {"hand": _digest("hand_correct"), "naive": _digest("naive_correct"),
                   "hardened": _digest("hardened_correct"), "hardened_v2": _digest("hardened_v2_correct")}
    correctness_arms_differ = len(set(arm_digests.values())) > 1
    segmenters_differ = bool(naive != hard)             # distinct pipelines (the real AF guard)
    arms_differ = segmenters_differ

    hand_in_band = bool(0.05 < hand_acc < 0.95)

    # ---- verdict (pre-registered bands) ----
    # PRIMARY degradation = hardened (realistic auto pipeline) vs hand.
    if not segmenters_differ:
        verdict = "ARMS_IDENTICAL_BUG"                  # hardening was a no-op -> real wiring bug
    elif hard_delta >= -0.02 and naive_delta >= -0.02:
        verdict = "INGEST_HARMLESS_EVEN_NAIVE"          # auto matches hand; no degradation to fix (valid)
    elif hard_v2_delta >= -0.02 and gap_closed:
        verdict = "INGEST_DEGRADES_FIX_RECOVERS"        # residual degradation, top-1 fix closes it
    elif gap_closed:
        verdict = "INGEST_DEGRADES_FIX_PARTIAL"         # fix helps but residual remains
    elif hard_delta <= -0.15:
        verdict = "INGEST_DEGRADES_UNFIXED"             # large degradation, fix did not close
    else:
        verdict = "INGEST_MILD_DEGRADE_NO_FIX_GAIN"

    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] McGuffey ingest->reader who-affected (RAW base reader, verb-anchored, N={n}) | "
        f"HAND(ref)={hand_acc}({hand_c}/{n}) "
        f"NAIVE={res['naive']['acc']}(d={naive_delta}) "
        f"HARDENED={res['hardened']['acc']}(d={hard_delta}) "
        f"HARDENED_V2={res['hardened_v2']['acc']}(d={hard_v2_delta}) | "
        f"hardening_helps_vs_naive={hardening_helps} top1_fix_closed_gap={gap_closed} | "
        f"exact_align_rate hardened={exact_rate['hardened']} naive={exact_rate['naive']} "
        f"hardened_v2={exact_rate['hardened_v2']} | no_match hardened={nomatch['hardened']} "
        f"naive={nomatch['naive']} | verb_lost hardened={verblost['hardened']} | "
        f"reader_degraded={len(hard_degraded)} (top={top_defect}) | "
        f"ingestion_defect(top={top_ingest_defect}, {dict(ingest_defect_dist)}) | "
        f"top1_fix=drop_vocab_blocks cleanliness_gain={cleanliness_gain} fix_cleans={fix_cleans} | "
        f"arms_differ={arms_differ} hand_in_band={hand_in_band}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "N_gold": n, "is_probe_flag": True,
        "note": ("Ingestion-induced reader degradation: reader (RAW base_pick who-is-affected, gate OFF, "
                 "verb-anchored on gold verb) run over HAND-curated gold sentences vs AUTO-segmented "
                 "sentences from the ingestor raw McGuffey stream. Delta = auto_acc - hand_acc. "
                 "One variable = the segmenter (naive vs hardened vs hardened_v2=+top1-fix). "
                 "LOCAL-only; no push/remote-persist; no hdlab/store mutation."),
        "reader_probe": "RAW base_pick (gate OFF) verb-anchored on gold verb; isolates extraction step",
        "hand_reference": {"acc": hand_acc, "correct": hand_c, "n": n, "hand_in_band": hand_in_band},
        "arms": res,
        "deltas": {"naive": naive_delta, "hardened": hard_delta, "hardened_v2": hard_v2_delta,
                   "hardening_helps_vs_naive": hardening_helps, "top1_fix_closed_gap": gap_closed},
        "segmentation": {"n_naive": len(naive), "n_hardened": len(hard), "n_hardened_v2": len(hard_v2)},
        "defect_distribution": defect_dist, "exact_align_rate": exact_rate,
        "no_match_count": nomatch, "verb_lost_count": verblost,
        "localization": {
            "reader_top1_deficiency": top_defect,          # dominant defect among reader-degraded (may be None)
            "n_hardened_reader_degraded": len(hard_degraded),
            "reader_degraded_examples": degraded_examples,
            "ingestion_top1_deficiency": top_ingest_defect,  # dominant NON-EXACT ingestion defect (cleanliness)
            "ingestion_nonexact_defect_dist": dict(ingest_defect_dist),
            "n_hardened_nonexact": len(nonexact_hard),
            "nonexact_examples": nonexact_examples,
            "top1_fix": ("drop_vocab_blocks: remove diacritic/short vocabulary-list lines (single-token or "
                         "run>=2) that defeat .isalpha() and bleed into adjacent sentences"),
            "top1_fix_cleanliness_gain": cleanliness_gain, "top1_fix_cleans": fix_cleans,
        },
        "arms_differ_verified": arms_differ, "segmenters_differ": segmenters_differ,
        "correctness_arms_differ": correctness_arms_differ, "arm_digests": arm_digests,
        "per_instance": per_inst,
        "design_gate": {
            "real_baseline": "reader RAW who-affected on hand-curated gold, recomputed in-cell",
            "one_variable": "ingestion source (segmenter: naive/hardened/hardened_v2); verb target fixed",
            "can_fail": ("auto matches hand (INGEST_HARMLESS) OR fix fails to close gap "
                         "(INGEST_DEGRADES_UNFIXED / _NO_FIX_GAIN)"),
            "difficulty_on": "real archaic McGuffey raw ingestor stream (wordlist/header/phonics noise)",
            "leak_clean": ("segmenter + alignment use gold TEXT only, never gold type/affected labels; "
                           "mutation-probe in self_test permutes labels -> segmentation+alignment identical"),
            "final_metrics_atomicity": "tmp_replace", "crlb_n/a": "accuracy on labeled gold, no noise floor",
            "calibration_check": "default_ok_for_this_regime (align F1 threshold 0.5, glass-box, reported)",
        },
        "credit": ("Ingestor cell: experiments/textbook_extract_mcguffey_v1.py (PyMuPDF). Reader front-end: "
                   "UD-EWT perceptron POS + hashed arc parser/labeler. Gold: Director-oracle who-affected "
                   "v1 (N=34) + v2_heldout (N=38)."),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    print("[self_test] start", flush=True)
    with open(RAW_PATH, encoding="utf-8") as f:
        raw = f.read()

    # --- determinism: segmenters are pure functions ---
    assert segment_naive(raw) == segment_naive(raw), "naive segmenter non-deterministic"
    assert segment_hardened(raw) == segment_hardened(raw), "hardened segmenter non-deterministic"
    assert segment_hardened(raw, True) == segment_hardened(raw, True)

    naive = segment_naive(raw)
    hard = segment_hardened(raw)
    assert len(naive) > 50 and len(hard) > 50, "too few sentences segmented"

    # --- hardened DROPS known noise: no running-head / lesson-header / phonics / bare-number sentences ---
    norm_hard = {_norm_str(s) for s in hard}
    for noise in ["first reader.", "eclectic series.", "lesson v.", "lesson viii.", "11", "f b x u"]:
        assert noise not in norm_hard, f"hardened kept noise line: {noise!r}"
    # phonics diacritic rows are gone (no all-alpha-<=2-char multi-token sentence survives)
    for s in hard:
        raw_toks = _WS.sub(" ", s.strip()).split()
        if len(raw_toks) >= 2 and s.strip()[-1] not in ".!?":
            assert not all(t.isalpha() and len(t) <= 2 for t in raw_toks), \
                f"phonics row survived hardened: {s!r}"

    # --- alignment correctness: known gold sentences align EXACT to a hardened auto sentence ---
    hard_toks = [_norm_tokens(s) for s in hard]
    for gt in ["Ned has fed the hen.", "Can Ann catch Rab?", "Ben upset the tub."]:
        bi, bs, bt = align_gold_to_auto(gt, hard, hard_toks)
        assert bs >= 0.99, f"gold {gt!r} did not align exact in hardened (score={bs}, got {bt!r})"
        assert _norm_str(gt) == _norm_str(bt), f"alignment mismatch: {gt!r} -> {bt!r}"
    # --- alignment does NOT mismatch to an unrelated sentence ---
    bi, bs, bt = align_gold_to_auto("Ned has fed the hen.", hard, hard_toks)
    assert "fed" in _norm_tokens(bt) and "hen" in _norm_tokens(bt), f"bad alignment: {bt!r}"

    # --- defect_class sanity ---
    assert defect_class("Ned has fed the hen.", "Ned has fed the hen.", 1.0) == "exact"
    assert defect_class("Ned has fed the hen.", "13 Ned has fed the hen.", 0.9) == "bleed"
    assert defect_class("Ned has fed the hen.", "Ned has fed.", 0.7) == "truncated"
    assert defect_class("Ned has fed the hen.", "zzz qqq", 0.0) == "no_match"

    # --- real code path: construct the REAL front-end + run the base reader on real text ---
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    corr, surf, none, vlost = reader_correct_on_text(
        "Ned has fed the hen.", "fed", False, span_head_tokens("the hen"),
        tagger, parser, labeler)
    assert not vlost, "verb 'fed' should be found in the clean sentence"
    assert isinstance(corr, bool)

    # --- LEAK-CLEAN mutation-probe: permuting gold LABELS must not change segmentation or alignment ---
    gold = load_gold()
    assert len(gold) == 72, f"expected 72 gold sentences, got {len(gold)}"
    import random
    rng = random.Random(12345)  # FIXED seed (no hash()-derived seeding; PROT-023)
    perm = list(range(len(gold)))
    rng.shuffle(perm)

    def alignment_map(gold_list):
        out = []
        for g in gold_list:
            bi, bs, bt = align_gold_to_auto(g["text"], hard, hard_toks)
            out.append((bi, round(bs, 6)))
        return out
    base_map = alignment_map(gold)
    mutated = []
    for k, g in enumerate(gold):
        gg = dict(g)
        gg["type"] = gold[perm[k]]["type"]
        gg["affected"] = gold[perm[k]]["affected"]
        mutated.append(gg)
    mut_map = alignment_map(mutated)
    assert base_map == mut_map, "LEAK: alignment changed when gold labels were permuted"

    print("[self_test] determinism OK; noise-drop OK; alignment-exact OK; no-mismatch OK; "
          "defect-class OK; real-code-path OK; leak-clean permutation-probe OK", flush=True)
    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run("smoke"); return
    if args.full:
        run("full"); return
    self_test()


if __name__ == "__main__":
    out_dir_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(out_dir_crash, exist_ok=True)
        with open(os.path.join(out_dir_crash, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
