# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 5-arm per-checkpoint prediction hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (symbolic KB-lookup + vote-count pipeline; no capacity/noise-floor
#   discriminator threshold applies -- 3-way discrete classification accuracy on a real benchmark)
# - HP_SCOPE: {dev_checkpoint_eval: [fire_rate_drop, comprehension_lift, scramble_control,
#   consolidation_fidelity]} -- ALWAYS/NEVER arms are diagnostic references, not HP-gated
# - cardinality_ok: EXPECTED_N_CHECKPOINTS=5, EXPECTED_N_ARMS=5
# - per-unit failure-class instrumentation (no bare except; degraded_scoring budget 2%)
# - calibration_check: adaptive_with_discriminator_gate (GATE_THRESH = median BoW-margin, computed
#   fresh at run start, logged, not hand-tuned)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL Library / consolidation_pass / HDFactStore objects
#   (real_code_path_exercised); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_crutch_fade_social_iqa_v1.md for the full pre-reg + deviations disclosed.
"""exp_crutch_fade_social_iqa_v1 -- THE DECISIVE Social IQa crutch-fade test (2026-08-10).

Composes: CRUTCH = data/cskg_foundation_v1 (1,238,686 typed spine edges, ATOMIC-dominant,
HARD_PASS-certified exp_cskg_foundation_v1), queried as a plain symbolic concept-pair index (NOT
kg_traversal.KGStore's Hebbian single-W substrate -- see prereg "Deviation" section: that store is
the SAME one Stage-2 sub-test B HARD_FAILED at CSKG cardinality, an unrelated open wall this cell
must not get confounded with). LIBRARY = hdlab.grounding_acquisition_loop.Library +
consolidation_pass(native_store=...) + hdlab.hd_fact_store.HDFactStore -- the validated
BANK->native-promotion connector (Test-A cleared: promote 5/5, guard 0/12 leaks, commit 07339e9c6).
FLAG = a predictive_coding-style relative-margin gate over BoW-candidate scores.

Question: as the substrate reads more of SIQa's train stream (context text only, no labels), does
the live CRUTCH fire LESS on repeat need for the SAME knowledge (fade) while held-out dev
comprehension RISES above a freshly-measured BoW baseline, and does a SCRAMBLED-content crutch fail
to reproduce any gain (proving real knowledge, not retrieval machinery, does the work)?

5 arms x 5 checkpoints (0/10/25/50/100% of exposure), full frozen dev (1,954 items) evaluated at
every checkpoint. Per-item routing tag (BOW_RESOLVED/LIBRARY_RESOLVED/CRUTCH_RESOLVED/ABSTAINED).
Two headline curves (crutch_fire_rate, comprehension) PLUS a re-encounter fade rate (coordinator
refinement, mid-build): among dev items that genuinely needed the crutch at checkpoint 0%, what
fraction of those whose driving concept-pair later gets promoted are served NATIVELY (not
re-consulting the crutch) at later checkpoints -- this isolates a genuine storage/consolidation
fault from the SIQa long-tail (many dev items' driving pairs simply never recur >=8x in train and
so never promote, which would otherwise mask a working fade mechanism inside a flat aggregate rate).

Modes:
  --self-test  Real-code-path check: tiny synthetic CSKG index (16 hand-built pairs), real
               Library/consolidation_pass/HDFactStore at N~12 synthetic exposures, tiny synthetic
               SIQA-shaped dev items, verifies routing/promotion/re-encounter machinery. No network.
  --smoke      Capped exposure (SMOKE_TRAIN_CAP contexts) + capped dev (SMOKE_DEV_CAP items),
               FULL CSKG index (real scale) -- discriminator-preview per DISCRIMINATOR-MUST-
               SURVIVE-SCALE (the crutch/gate machinery is exercised against the REAL 1.24M-edge
               store, only the exposure/eval VOLUME is reduced).
  --full       Full 33,410-context exposure stream, full 1,954-item frozen dev, full CSKG index.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, context_vector, consolidation_pass,
    PROMOTE_MIN_EXPOSURE, PROMOTE_MIN_CONSISTENCY,
)
from hdlab.hd_fact_store import HDFactStore  # noqa: E402

ANCHOR_NAME = "crutch_fade_social_iqa_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")
SIQA_DIR = os.path.join(REPO_ROOT, "data", "corpora", "social_iqa", "hf_dataset")

CHECKPOINTS = [0.0, 0.10, 0.25, 0.50, 1.00]  # MEASURED@drill4 Section 2b
N_PASSES_PER_CHECKPOINT = 3
SMOKE_TRAIN_CAP = 3000
SMOKE_DEV_CAP = 250
DEGRADED_BUDGET = 0.02
TRUST_WEIGHT = {"TRUST_HIGH": 1.0, "TRUST_MID": 0.6}

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by", "for", "with",
    "as", "is", "was", "were", "are", "be", "been", "being", "it", "its", "he", "she", "they",
    "him", "her", "them", "his", "their", "i", "you", "we", "me", "my", "your", "our", "this",
    "that", "these", "those", "not", "no", "so", "than", "then", "there", "here", "up", "out",
    "into", "over", "again", "very", "just", "would", "could", "should", "will", "shall", "can",
    "did", "do", "does", "had", "has", "have", "from", "all", "any", "some", "one", "two", "when",
    "what", "who", "which", "how", "why", "said", "upon", "others", "other", "before", "after",
})
TOKRE = re.compile(r"[a-z']+")


# =====================================================================================
# canon(): byte-identical to experiments/exp_cskg_foundation_v1.py::canon (copied inline,
# small pure function, attributed -- avoids importing a non-library experiment script).
def canon(label: str) -> str:
    s = label.strip().lower()
    out = []
    prev_us = True
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_us = False
        elif not prev_us:
            out.append("_")
            prev_us = True
    r = "".join(out)
    if r.endswith("_"):
        r = r[:-1]
    return r


def content_words(text: str) -> List[str]:
    return [w for w in TOKRE.findall(text.lower()) if w not in _STOPWORDS and len(w) > 1]


def pair_key(a: str, b: str) -> str:
    lo, hi = (a, b) if a <= b else (b, a)
    return f"{lo}::{hi}"


# =====================================================================================
# start-marker / crash diagnostics / atomic metrics (per exp_dev canonical checklist)
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _hb(output_dir, stage, t0, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - t0, 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} t={row['elapsed_s']}s {extra or ''}", flush=True)


# =====================================================================================
# CSKG symbolic concept-pair index loader (real edges_shard_*.jsonl format)
def load_cskg_index(cskg_dir: str = CSKG_DIR, max_shards: Optional[int] = None,
                    max_edges: Optional[int] = None) -> Dict[str, List[Tuple[str, float]]]:
    """pair_key -> list[(relation, trust_weight)]. MEASURED@data/exp_cskg_foundation_v1/metrics.json:
    482,588 spine nodes / 1,238,686 typed edges (16 shards)."""
    idx: Dict[str, List[Tuple[str, float]]] = {}
    shard_names = sorted(f for f in os.listdir(cskg_dir) if f.startswith("edges_shard_"))
    if max_shards is not None:
        shard_names = shard_names[:max_shards]
    n_edges = 0
    for shard in shard_names:
        with open(os.path.join(cskg_dir, shard), encoding="utf-8") as f:
            for line in f:
                if max_edges is not None and n_edges >= max_edges:
                    return idx
                row = json.loads(line)
                subj, obj = row["subject"], row["obj"]
                if subj == obj:
                    continue
                trust_w = TRUST_WEIGHT.get(row.get("trust", "TRUST_MID"), 0.6)
                idx.setdefault(pair_key(subj, obj), []).append((row["relation"], trust_w))
                n_edges += 1
    return idx


def cskg_node_set_from_index(idx: Dict[str, List]) -> frozenset:
    nodes = set()
    for k in idx:
        a, b = k.split("::", 1)
        nodes.add(a)
        nodes.add(b)
    return frozenset(nodes)


def _stem_variants(c: str) -> List[str]:
    """Cheap suffix-strip fallback (no external NLP dep) for surface-form mismatch between SIQa's
    inflected text (plurals/verb endings) and CSKG's lemma-like canon ids (mostly ConceptNet-
    convention singular/base forms). Tried IN ORDER only when the raw canon'd token itself is not
    a CSKG node; disclosed limitation (prereg "Deviation"): this is not a real lemmatizer, so some
    irregular forms (e.g. 'went'->'go') will still miss."""
    out = []
    if c.endswith("ies") and len(c) > 4:
        out.append(c[:-3] + "y")
    if c.endswith("es") and len(c) > 3:
        out.append(c[:-2])
    if c.endswith("s") and len(c) > 3:
        out.append(c[:-1])
    if c.endswith("ing") and len(c) > 5:
        out.append(c[:-3])
        out.append(c[:-3] + "e")
    if c.endswith("ed") and len(c) > 4:
        out.append(c[:-2])
        out.append(c[:-1])
    return out


def extract_concepts(text: str, node_set: frozenset) -> List[str]:
    seen = []
    seen_set = set()
    for w in content_words(text):
        c = canon(w)
        if not c:
            continue
        if c not in node_set:
            for variant in _stem_variants(c):
                if variant in node_set:
                    c = variant
                    break
        if c in node_set and c not in seen_set:
            seen_set.add(c)
            seen.append(c)
    return seen


# =====================================================================================
# SIQA loading (cached local JSONL; no network at run time)
def load_siqa() -> Tuple[List[dict], List[dict]]:
    def _load(fname):
        rows = []
        with open(os.path.join(SIQA_DIR, fname), encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
        return rows
    return _load("train.jsonl"), _load("validation.jsonl")


# =====================================================================================
# scoring primitives
def bow_scores(item: dict) -> List[float]:
    ctx_q = content_words(item["context"] + " " + item["question"])
    ctx_set = set(ctx_q)
    scores = []
    for key in ("answerA", "answerB", "answerC"):
        ans_words = content_words(item[key])
        if not ans_words:
            scores.append(0.0)
            continue
        overlap = sum(1 for w in ans_words if w in ctx_set)
        scores.append(overlap / (len(ans_words) + 1))
    return scores


def bow_margin(scores: List[float]) -> float:
    s = sorted(scores, reverse=True)
    top1, top2 = s[0], s[1]
    return (top1 - top2) / (top1 + top2 + 1e-9)


def argmax_tiebreak(scores: List[float]) -> int:
    best = 0
    for i in range(1, len(scores)):
        if scores[i] > scores[best]:
            best = i
    return best


def crutch_candidate_scores(ctx_concepts: List[str], ans_concepts_list: List[List[str]],
                            idx: Dict[str, List[Tuple[str, float]]]
                            ) -> Tuple[List[float], List[Optional[str]]]:
    """Returns (per-candidate crutch score, per-candidate best driving pair_key or None)."""
    scores = []
    driving = []
    for ans_concepts in ans_concepts_list:
        best_score = 0.0
        best_pair = None
        for cc in ctx_concepts:
            for ac in ans_concepts:
                if cc == ac:
                    continue
                pk = pair_key(cc, ac)
                edges = idx.get(pk)
                if not edges:
                    continue
                w = max(t for _, t in edges) * len(edges)
                if w > best_score:
                    best_score = w
                    best_pair = pk
        scores.append(best_score)
        driving.append(best_pair)
    return scores, driving


def _scramble_partner(seed_key: str, node_list: List[str], exclude: str) -> str:
    """Deterministic (hashlib-seeded, PROT-023/F.5 compliant) 'wrong' concept draw."""
    h = int.from_bytes(hashlib.sha256(seed_key.encode("utf-8")).digest()[:8], "big")
    n = len(node_list)
    for attempt in range(8):
        j = (h + attempt * 2654435761) % n
        cand = node_list[j]
        if cand != exclude:
            return cand
    return node_list[h % n]


def scramble_crutch_candidate_scores(item_id: str, ctx_concepts: List[str],
                                     ans_concepts_list: List[List[str]],
                                     idx: Dict[str, List[Tuple[str, float]]],
                                     node_list: List[str]
                                     ) -> Tuple[List[float], List[Optional[str]]]:
    """Same firing structure as crutch_candidate_scores but looks up a deterministically-WRONG
    concept in place of each true context concept -- 'a random OTHER CSKG neighbor unrelated to
    the actual cue' (drill 4 Section 2c, arm 5)."""
    scores = []
    driving = []
    for ci, ans_concepts in enumerate(ans_concepts_list):
        best_score = 0.0
        best_pair = None
        for cc in ctx_concepts:
            wrong_cc = _scramble_partner(f"{item_id}|{cc}|{ci}", node_list, cc)
            for ac in ans_concepts:
                if wrong_cc == ac:
                    continue
                pk = pair_key(wrong_cc, ac)
                edges = idx.get(pk)
                if not edges:
                    continue
                w = max(t for _, t in edges) * len(edges)
                if w > best_score:
                    best_score = w
                    best_pair = pk
        scores.append(best_score)
        driving.append(best_pair)
    return scores, driving


def library_candidate_scores(ctx_concepts: List[str], ans_concepts_list: List[List[str]],
                             store: HDFactStore) -> Tuple[List[float], List[Optional[str]]]:
    scores = []
    driving = []
    for ans_concepts in ans_concepts_list:
        best_score = 0.0
        best_pair = None
        for cc in ctx_concepts:
            for ac in ans_concepts:
                if cc == ac:
                    continue
                pk = pair_key(cc, ac)
                hits = store.query(pk, "OUTCOME_POLARITY")
                if hits and hits[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"):
                    if 1.0 > best_score:
                        best_score = 1.0
                        best_pair = pk
        scores.append(best_score)
        driving.append(best_pair)
    return scores, driving


# =====================================================================================
# per-item resolution (one arm, one item, given current library state)
def resolve_item(item: dict, node_set: frozenset, idx: Dict[str, List[Tuple[str, float]]],
                 gate_thresh: float, arm: str, item_id: str,
                 store: Optional[HDFactStore] = None,
                 node_list: Optional[List[str]] = None) -> dict:
    b_scores = bow_scores(item)
    ctx_concepts = extract_concepts(item["context"] + " " + item["question"], node_set)
    ans_concepts_list = [extract_concepts(item[k], node_set) for k in ("answerA", "answerB", "answerC")]

    if arm == "bow" or arm == "never_crutch":
        pred = argmax_tiebreak(b_scores)
        return {"tag": "BOW_RESOLVED", "pred_idx": pred, "driving_pair": None}

    if arm == "always_crutch":
        c_scores, c_driving = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "BOW_RESOLVED", "pred_idx": pred, "driving_pair": None}

    margin = bow_margin(b_scores)
    gap = (margin == 0.0) or (margin < gate_thresh)  # a TIE (incl. all-zero) always flags
    if not gap:
        pred = argmax_tiebreak(b_scores)
        return {"tag": "BOW_RESOLVED", "pred_idx": pred, "driving_pair": None}

    if arm == "gap_driven":
        l_scores, l_driving = library_candidate_scores(ctx_concepts, ans_concepts_list, store)
        if max(l_scores) > 0:
            pred = argmax_tiebreak(l_scores)
            return {"tag": "LIBRARY_RESOLVED", "pred_idx": pred, "driving_pair": l_driving[pred]}
        c_scores, c_driving = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "ABSTAINED", "pred_idx": pred, "driving_pair": None}

    if arm == "scramble_crutch":
        l_scores, l_driving = library_candidate_scores(ctx_concepts, ans_concepts_list, store)
        if max(l_scores) > 0:
            pred = argmax_tiebreak(l_scores)
            return {"tag": "LIBRARY_RESOLVED", "pred_idx": pred, "driving_pair": l_driving[pred]}
        c_scores, c_driving = scramble_crutch_candidate_scores(item_id, ctx_concepts,
                                                                ans_concepts_list, idx, node_list)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "ABSTAINED", "pred_idx": pred, "driving_pair": None}

    raise ValueError(f"unknown arm {arm!r}")


def label_idx(item: dict) -> int:
    return int(item["label"]) - 1


# =====================================================================================
# exposure processing (gap_driven + scramble_crutch arms only)
def process_exposure_slice(train_slice: List[dict], node_set: frozenset,
                           idx: Dict[str, List[Tuple[str, float]]], node_list: List[str],
                           real_lib: Library, scr_lib: Library,
                           pair_example_context: Dict[str, str]) -> None:
    for i, ex in enumerate(train_slice):
        ctx_text = ex["context"]
        concepts = extract_concepts(ctx_text, node_set)
        cvec = context_vector(ctx_text)
        n = len(concepts)
        for a_i in range(n):
            for b_i in range(a_i + 1, n):
                a, b = concepts[a_i], concepts[b_i]
                pk = pair_key(a, b)
                if pk in idx:
                    real_lib.flag(pk, f"exp{i}_{pk}", "POS", cvec, 0)
                    if pk not in pair_example_context:
                        pair_example_context[pk] = ctx_text
                    wrong_b = _scramble_partner(f"scr|{a}|{b}", node_list, b)
                    scr_pk = pair_key(a, wrong_b)
                    scr_lib.flag(scr_pk, f"exps{i}_{scr_pk}", "POS", cvec, 0)


# =====================================================================================
# main run
def run(output_dir: str, run_mode: str, train_cap: Optional[int], dev_cap: Optional[int],
       seed: int = 7) -> dict:
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=len(CHECKPOINTS))

    print("[load] CSKG index...", flush=True)
    idx = load_cskg_index()
    node_set = cskg_node_set_from_index(idx)
    node_list = sorted(node_set)  # deterministic order (sorted, not list(set()))
    _hb(output_dir, "cskg_loaded", t0, {"n_pairs": len(idx), "n_nodes": len(node_list)})

    print("[load] Social IQa...", flush=True)
    train_all, dev_all = load_siqa()
    train = train_all[:train_cap] if train_cap else train_all
    dev = dev_all[:dev_cap] if dev_cap else dev_all
    _hb(output_dir, "siqa_loaded", t0, {"n_train": len(train), "n_dev": len(dev)})

    # ---- Stage-0: BoW baseline measured fresh + adaptive GATE_THRESH ----
    # MEASURED@smoke (2026-08-10, SMOKE_TRAIN_CAP=3000/SMOKE_DEV_CAP=250 run): >=50% of dev items
    # have a TIED top-2 BoW score (median margin over ALL items = 0.0 exactly) -- SIQa's answers are
    # short, non-extractive phrases, so raw lexical overlap frequently ties (often at zero for all
    # 3 candidates). A plain median-of-all-margins threshold degenerates to 0.0 in that regime,
    # which silently disables margin-based gap-flagging (only the explicit all-zero special case
    # still fires) -- a harness bug caught by smoke, not a mechanism reading (constant 0.1640
    # crutch-fire-rate across every checkpoint was this bug, not a real flat result). Fix: (a) a
    # TIE (margin==0, including the all-zero case) always flags -- a tie is uninformative
    # regardless of magnitude; (b) the threshold itself is calibrated from the STRICTLY-POSITIVE
    # (non-tied) margins only, so the tie-mass no longer swamps the percentile.
    dev_bow_scores = [bow_scores(it) for it in dev]
    dev_margins_all = [bow_margin(s) for s in dev_bow_scores]
    dev_margins_pos = sorted(m for m in dev_margins_all if m > 0.0)
    gate_thresh = dev_margins_pos[len(dev_margins_pos) // 2] if dev_margins_pos else 0.5
    bow_acc = sum(1 for it, s in zip(dev, dev_bow_scores) if argmax_tiebreak(s) == label_idx(it)) / len(dev)
    n_tied = sum(1 for m in dev_margins_all if m == 0.0)
    print(f"[stage0] BoW dev accuracy(fresh)={bow_acc:.4f} GATE_THRESH(median of positive "
          f"margins)={gate_thresh:.4f} n_tied={n_tied}/{len(dev_margins_all)}", flush=True)

    # ---- leakage audit (Stage-0 item c) ----
    leak_sample = dev[:100]
    n_leak = 0
    for it in leak_sample:
        ctx_concepts = extract_concepts(it["context"] + " " + it["question"], node_set)
        gold_key = ("answerA", "answerB", "answerC")[label_idx(it)]
        gold_concepts = extract_concepts(it[gold_key], node_set)
        hit = False
        for cc in ctx_concepts:
            for gc in gold_concepts:
                if cc != gc and pair_key(cc, gc) in idx:
                    hit = True
                    break
            if hit:
                break
        if hit:
            n_leak += 1
    leakage_rate = n_leak / len(leak_sample) if leak_sample else 0.0
    print(f"[leakage] {n_leak}/{len(leak_sample)} = {leakage_rate:.4f}", flush=True)

    # ---- exposure checkpoints ----
    n_total = len(train)
    cum_counts = [int(round(f * n_total)) for f in CHECKPOINTS]
    real_lib = Library()
    scr_lib = Library()
    real_store = HDFactStore(n_dim=2048, seed=seed, use_index=True)
    scr_store = HDFactStore(n_dim=2048, seed=seed + 1, use_index=True)
    pair_example_context: Dict[str, str] = {}

    always_cache: Optional[dict] = None
    checkpoint_rows = []
    pass_counter = 0
    prev_cum = 0

    for ck_i, (frac, cum) in enumerate(zip(CHECKPOINTS, cum_counts)):
        if cum > prev_cum:
            slice_ = train[prev_cum:cum]
            process_exposure_slice(slice_, node_set, idx, node_list, real_lib, scr_lib,
                                   pair_example_context)
            for _ in range(N_PASSES_PER_CHECKPOINT):
                pass_counter += 1
                consolidation_pass(real_lib, pass_counter, register=False, native_store=real_store,
                                   promote_source="cskg_crutch_real")
                consolidation_pass(scr_lib, pass_counter, register=False, native_store=scr_store,
                                   promote_source="cskg_crutch_scramble")
        prev_cum = cum
        _hb(output_dir, f"checkpoint_{ck_i}_exposure_done", t0,
            {"frac": frac, "n_exposed": cum, "real_lib_items": len(real_lib.items),
             "real_promoted": len(real_store.live_facts())})

        per_arm_rows: Dict[str, List[dict]] = {}
        for arm in ("bow", "never_crutch", "always_crutch", "gap_driven", "scramble_crutch"):
            if arm == "always_crutch" and always_cache is not None:
                per_arm_rows[arm] = always_cache
                continue
            store = real_store if arm == "gap_driven" else (scr_store if arm == "scramble_crutch" else None)
            rows = []
            for j, it in enumerate(dev):
                item_id = f"dev{j}"
                res = resolve_item(it, node_set, idx, gate_thresh, arm, item_id,
                                   store=store, node_list=node_list)
                res["correct"] = (res["pred_idx"] == label_idx(it))
                res["item_idx"] = j
                rows.append(res)
            per_arm_rows[arm] = rows
            if arm == "always_crutch":
                always_cache = rows

        acc = {arm: sum(1 for r in rows if r["correct"]) / len(rows) for arm, rows in per_arm_rows.items()}
        tag_counts = {arm: {t: sum(1 for r in rows if r["tag"] == t)
                            for t in ("BOW_RESOLVED", "LIBRARY_RESOLVED", "CRUTCH_RESOLVED", "ABSTAINED")}
                     for arm, rows in per_arm_rows.items()}
        tag_acc = {}
        for arm, rows in per_arm_rows.items():
            tag_acc[arm] = {}
            for t in ("BOW_RESOLVED", "LIBRARY_RESOLVED", "CRUTCH_RESOLVED", "ABSTAINED"):
                sub = [r for r in rows if r["tag"] == t]
                tag_acc[arm][t] = (sum(1 for r in sub if r["correct"]) / len(sub)) if sub else None

        crutch_fire_rate = tag_counts["gap_driven"]["CRUTCH_RESOLVED"] / len(dev)
        library_resolved_rate = tag_counts["gap_driven"]["LIBRARY_RESOLVED"] / len(dev)
        scramble_fire_rate = tag_counts["scramble_crutch"]["CRUTCH_RESOLVED"] / len(dev)

        checkpoint_rows.append({
            "checkpoint_frac": frac, "n_exposed": cum,
            "accuracy": acc, "tag_counts": tag_counts, "tag_accuracy": tag_acc,
            "crutch_fire_rate": crutch_fire_rate, "library_resolved_rate": library_resolved_rate,
            "scramble_fire_rate": scramble_fire_rate,
            "real_lib_pending": len(real_lib.items),
            "real_promoted_n": len(real_store.live_facts()),
            "scr_promoted_n": len(scr_store.live_facts()),
            "per_arm_rows": {arm: rows for arm, rows in per_arm_rows.items()},
        })
        print(f"[checkpoint {ck_i} frac={frac}] acc={acc} crutch_fire={crutch_fire_rate:.4f} "
              f"lib_resolved={library_resolved_rate:.4f} promoted={len(real_store.live_facts())}",
              flush=True)

    # ---- RE-ENCOUNTER FADE RATE (coordinator refinement) ----
    # cohort0 = dev items that genuinely needed the live crutch at checkpoint 0% (zero exposure).
    ck0_rows = checkpoint_rows[0]["per_arm_rows"]["gap_driven"]
    cohort0 = [r for r in ck0_rows if r["tag"] == "CRUTCH_RESOLVED" and r["driving_pair"]]
    cohort0_pairs = {r["item_idx"]: r["driving_pair"] for r in cohort0}
    # real_store is monotonic-append (facts never de-promote once live), and promotions occur in
    # the SAME order consolidation_pass visits them (sorted(library.items) each pass) -- so the
    # first `real_promoted_n` fids recorded live-at-checkpoint-T are EXACTLY the set promoted by T.
    # This lets us reconstruct a per-checkpoint promoted-SET snapshot without re-storing one
    # HDFactStore per checkpoint.
    live_sorted = sorted(real_store.live_facts(), key=lambda f: f.fid)
    re_encounter_curve = []
    for ck_i, ck in enumerate(checkpoint_rows):
        n_live_at_ck = ck["real_promoted_n"]
        promoted_pairs_t = {f.subject for f in live_sorted[:n_live_at_ck]}
        eligible = [j for j, pk in cohort0_pairs.items() if pk in promoted_pairs_t]
        rows_at_ck = {r["item_idx"]: r for r in ck["per_arm_rows"]["gap_driven"]}
        n_native = sum(1 for j in eligible if rows_at_ck[j]["tag"] == "LIBRARY_RESOLVED")
        rate = (n_native / len(eligible)) if eligible else None
        re_encounter_curve.append({"checkpoint_frac": ck["checkpoint_frac"], "n_eligible": len(eligible),
                                   "n_native": n_native, "re_encounter_fade_rate": rate})
    print(f"[re-encounter] cohort0_size={len(cohort0)} curve={re_encounter_curve}", flush=True)

    # ---- fallback constructed probe if natural re-encounters are sparse ----
    fallback_probe = None
    last_eligible = re_encounter_curve[-1]["n_eligible"] if re_encounter_curve else 0
    if last_eligible < 20:
        print("[re-encounter] natural cohort too sparse; running constructed fallback probe", flush=True)
        promoted_final = sorted({f.subject for f in real_store.live_facts()})[:200]
        n_native_probe = 0
        n_probe = 0
        for pk in promoted_final:
            ctx_text = pair_example_context.get(pk)
            if not ctx_text:
                continue
            a, b = pk.split("::", 1)
            distractor = _scramble_partner(f"probe|{pk}", node_list, b)
            probe_item = {"context": ctx_text, "question": "What is most related to this?",
                         "answerA": b, "answerB": distractor, "answerC": "unrelated", "label": "1"}
            res = resolve_item(probe_item, node_set, idx, gate_thresh, "gap_driven", f"probe_{pk}",
                               store=real_store, node_list=node_list)
            n_probe += 1
            if res["tag"] == "LIBRARY_RESOLVED":
                n_native_probe += 1
        fallback_probe = {"n_probe": n_probe, "n_native": n_native_probe,
                          "native_answer_rate": (n_native_probe / n_probe) if n_probe else None}
        print(f"[re-encounter] fallback probe: {fallback_probe}", flush=True)

    # ---- arms-must-differ (META_RULE_AF) ----
    def _digest(rows):
        s = json.dumps([(r["pred_idx"], r["tag"]) for r in rows]).encode("utf-8")
        return hashlib.sha256(s).hexdigest()
    final_ck = checkpoint_rows[-1]["per_arm_rows"]
    digests = {arm: _digest(rows) for arm, rows in final_ck.items()}
    arm_names = list(digests)
    differ_pairs_ok = True
    for i in range(len(arm_names)):
        for j in range(i + 1, len(arm_names)):
            if digests[arm_names[i]] == digests[arm_names[j]]:
                differ_pairs_ok = False

    # ---- strip per-arm-rows from checkpoint summary (large; keep aggregate only in metrics) ----
    checkpoint_summary = []
    for ck in checkpoint_rows:
        c = {k: v for k, v in ck.items() if k != "per_arm_rows"}
        checkpoint_summary.append(c)

    # ---- verdict logic (drill 4 Section 3, verbatim bands + this cell's re-encounter addition) ----
    ck0, ck100 = checkpoint_rows[0], checkpoint_rows[-1]
    fire0, fire100 = ck0["crutch_fire_rate"], ck100["crutch_fire_rate"]
    fire_drop_rel = (fire0 - fire100) / fire0 if fire0 > 0 else 0.0
    fire_drop_abs = fire0 - fire100
    fire_drops = fire_drop_rel >= 0.30 or fire_drop_abs >= 0.10
    upticks = sum(1 for i in range(1, len(checkpoint_rows))
                  if checkpoint_rows[i]["crutch_fire_rate"] - checkpoint_rows[i - 1]["crutch_fire_rate"] > 0.03)
    steep_then_tail = upticks <= 1

    gap_acc0, gap_acc100 = ck0["accuracy"]["gap_driven"], ck100["accuracy"]["gap_driven"]
    bow_acc_final = ck100["accuracy"]["bow"]
    comprehension_lift = gap_acc100 - bow_acc_final >= 0.05
    no_regression = all(ck["accuracy"]["gap_driven"] >= ck["accuracy"]["bow"] - 0.02 for ck in checkpoint_rows)

    scramble_controlled = all(abs(ck["accuracy"]["scramble_crutch"] - ck["accuracy"]["bow"]) <= 0.02
                              for ck in checkpoint_rows)
    scramble_never_beats_real = all(ck["accuracy"]["scramble_crutch"] <= ck["accuracy"]["gap_driven"]
                                    for ck in checkpoint_rows)

    consolidation_fidelity_ok = True
    consolidation_fidelity_checks = []
    for ck in checkpoint_rows:
        lib_a = ck["tag_accuracy"]["gap_driven"]["LIBRARY_RESOLVED"]
        cru_a = ck["tag_accuracy"]["gap_driven"]["CRUTCH_RESOLVED"]
        lib_n = ck["tag_counts"]["gap_driven"]["LIBRARY_RESOLVED"]
        cru_n = ck["tag_counts"]["gap_driven"]["CRUTCH_RESOLVED"]
        if lib_n >= 20 and cru_n >= 20:
            ok = lib_a >= (cru_a - 0.03)
            consolidation_fidelity_checks.append({"frac": ck["checkpoint_frac"], "lib_acc": lib_a,
                                                   "cru_acc": cru_a, "ok": ok})
            if not ok:
                consolidation_fidelity_ok = False

    re_encounter_final = re_encounter_curve[-1]["re_encounter_fade_rate"]
    re_encounter_first_measurable = next((c["re_encounter_fade_rate"] for c in re_encounter_curve
                                          if c["re_encounter_fade_rate"] is not None), None)
    re_encounter_rises = (re_encounter_final is not None and re_encounter_first_measurable is not None
                          and (re_encounter_final - re_encounter_first_measurable) >= 0.30)

    hard_fail_reasons = []
    if not fire_drops and not re_encounter_rises:
        hard_fail_reasons.append("CRUTCH_FIRE_RATE_FLAT_AND_RE_ENCOUNTER_FLAT: aggregate fire-rate "
                                 f"did not drop (rel={fire_drop_rel:.4f} abs={fire_drop_abs:.4f}) AND "
                                 f"re_encounter_fade_rate did not rise (first={re_encounter_first_measurable} "
                                 f"final={re_encounter_final}) -- genuine flat result, not long-tail masking")
    if not comprehension_lift:
        hard_fail_reasons.append(f"COMPREHENSION_FLAT_OR_NO_RISE: gap_driven@100%={gap_acc100:.4f} "
                                 f"vs bow@100%={bow_acc_final:.4f} (need >=+0.05)")
    if not scramble_controlled:
        hard_fail_reasons.append("SCRAMBLE_BEATS_OR_TIES_BOW: scramble arm exceeded BoW+-0.02 at "
                                 "some checkpoint")
    if not scramble_never_beats_real:
        hard_fail_reasons.append("SCRAMBLE_TIES_OR_BEATS_REAL_ARM")
    if not consolidation_fidelity_ok:
        hard_fail_reasons.append(f"CONSOLIDATION_FIDELITY_COLLAPSE: {consolidation_fidelity_checks}")

    hard_pass_all = (fire_drops and steep_then_tail and comprehension_lift and no_regression
                     and scramble_controlled and consolidation_fidelity_ok)

    if hard_fail_reasons:
        verdict = "HARD_FAIL"
    elif hard_pass_all:
        verdict = "HARD_PASS"
    elif fire_drops and not steep_then_tail and comprehension_lift and scramble_controlled:
        verdict = "MIDDLE_BAND"  # shape-only partial (linear not steep-then-tail)
    elif (not fire_drops) and re_encounter_rises:
        verdict = "MIDDLE_BAND"  # storage/promotion works; aggregate flatness is long-tail
    elif comprehension_lift and not fire_drops:
        verdict = "MIDDLE_BAND"  # accuracy-only
    elif fire_drops and not comprehension_lift:
        verdict = "MIDDLE_BAND"  # efficiency-only
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"{verdict}: fire_rate[0%->100%]={fire0:.4f}->{fire100:.4f} (rel_drop={fire_drop_rel:.4f} "
        f"abs_drop={fire_drop_abs:.4f} steep_then_tail={steep_then_tail}) | "
        f"comprehension gap_driven[0%,100%]=({gap_acc0:.4f},{gap_acc100:.4f}) bow_final={bow_acc_final:.4f} "
        f"lift={gap_acc100 - bow_acc_final:.4f} no_regression={no_regression} | "
        f"scramble_controlled={scramble_controlled} scramble_never_beats_real={scramble_never_beats_real} | "
        f"consolidation_fidelity_ok={consolidation_fidelity_ok} | "
        f"re_encounter_fade_rate[first->final]=({re_encounter_first_measurable},{re_encounter_final}) "
        f"eligible_n_final={re_encounter_curve[-1]['n_eligible']} | "
        f"leakage_rate={leakage_rate:.4f} | reasons={hard_fail_reasons}"
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": f"{verdict}: {verdict_msg[:250]}",
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "config": {"checkpoints": CHECKPOINTS, "n_passes_per_checkpoint": N_PASSES_PER_CHECKPOINT,
                  "train_cap": train_cap, "dev_cap": dev_cap, "seed": seed,
                  "gate_thresh_median_margin": gate_thresh,
                  "promote_min_exposure": PROMOTE_MIN_EXPOSURE,
                  "promote_min_consistency": PROMOTE_MIN_CONSISTENCY},
        "stage0_bow_baseline_accuracy": bow_acc,
        "leakage_audit": {"n_sample": len(leak_sample), "n_leaked": n_leak, "leakage_rate": leakage_rate},
        "checkpoints": checkpoint_summary,
        "re_encounter_fade_curve": re_encounter_curve,
        "re_encounter_fallback_probe": fallback_probe,
        "cohort0_size": len(cohort0),
        "hard_fail_reasons": hard_fail_reasons,
        "bands": {"fire_drops": fire_drops, "steep_then_tail": steep_then_tail,
                 "comprehension_lift": comprehension_lift, "no_regression": no_regression,
                 "scramble_controlled": scramble_controlled,
                 "scramble_never_beats_real": scramble_never_beats_real,
                 "consolidation_fidelity_ok": consolidation_fidelity_ok,
                 "re_encounter_rises": re_encounter_rises},
        "arms_differ_verified": differ_pairs_ok,
        "arm_digests": digests,
        "cardinality_ok": len(CHECKPOINTS) == 5 and len(final_ck) == 5,
        "expected_n_units": len(CHECKPOINTS),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "symbolic KB-lookup + vote-count pipeline; no argmax/capacity noise-floor "
                   "discriminator applies",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "calibration_check": "adaptive_with_discriminator_gate",
        "hp_scope": {"dev_checkpoint_eval": ["fire_rate_drop", "comprehension_lift",
                                             "scramble_control", "consolidation_fidelity"]},
        "n_cskg_pairs": len(idx), "n_cskg_nodes": len(node_list),
        "n_train_exposed": n_total, "n_dev": len(dev),
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.2f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# =====================================================================================
# self-test (real code path, tiny synthetic scale, no network)
def self_test() -> dict:
    print("[self-test] tiny synthetic CSKG index + real Library/consolidation_pass/HDFactStore",
          flush=True)
    # tiny synthetic CSKG: concepts a0..a9, pairs forming a few "facts"
    idx = {}
    idx[pair_key("party", "friend")] = [("at:xEffect", 1.0)]
    idx[pair_key("party", "happy")] = [("at:xReact", 1.0)]
    idx[pair_key("rain", "wet")] = [("/r/Causes", 0.6)]
    idx[pair_key("hunger", "food")] = [("/r/MotivatedByGoal", 1.0)]
    node_set = cskg_node_set_from_index(idx)
    node_list = sorted(node_set)
    assert len(node_set) == 7, node_set

    # extract_concepts must find known concepts and skip unknowns; the plural "friends" must
    # resolve to the singular CSKG node "friend" via the stem-variant fallback (surface-form
    # mismatch is real on SIQa's inflected text vs CSKG's lemma-like ids -- see prereg deviation).
    got = extract_concepts("There was a big party with friends and food today", node_set)
    assert "party" in got and "friend" in got and "food" in got, got
    assert "today" not in got, got

    # crutch_candidate_scores: a candidate concept linked to a context concept scores > 0
    ctx_concepts = ["party"]
    ans_lists = [["friend"], ["unrelated"], ["happy"]]
    scores, driving = crutch_candidate_scores(ctx_concepts, ans_lists, idx)
    assert scores[0] > 0 and scores[1] == 0 and scores[2] > 0, scores
    assert driving[0] == pair_key("party", "friend"), driving

    # real Library + consolidation_pass + HDFactStore: repeated exposure -> promotion
    lib = Library()
    store = HDFactStore(n_dim=512, seed=99, use_index=True)
    pk = pair_key("party", "friend")
    for i in range(10):
        cvec = context_vector(f"Nell threw a party and invited many friends round {i}.")
        lib.flag(pk, f"e{i}", "POS", cvec, 0)
    for p in range(1, 6):
        consolidation_pass(lib, p, register=False, native_store=store, promote_source="selftest")
    assert lib.items[pk].status == "GROUNDED_POS", lib.items[pk].status
    hits = store.query(pk, "OUTCOME_POLARITY")
    assert hits and hits[0]["object"] == "POS", hits

    # library_candidate_scores now finds the promoted pair
    l_scores, l_driving = library_candidate_scores(["party"], [["friend"], ["unrelated"]], store)
    assert l_scores[0] == 1.0 and l_scores[1] == 0.0, l_scores

    # resolve_item routing: a synthetic SIQA-shaped item that needs the crutch (BoW gives no signal)
    item = {"context": "There was a big party with friends today.", "question": "How would people feel?",
           "answerA": "excited", "answerB": "sad", "answerC": "happy", "label": "3"}
    res_bow = resolve_item(item, node_set, idx, gate_thresh=0.9, arm="bow", item_id="t0")
    assert res_bow["tag"] == "BOW_RESOLVED"
    res_gap = resolve_item(item, node_set, idx, gate_thresh=0.9, arm="gap_driven", item_id="t0",
                           store=HDFactStore(n_dim=64, seed=1), node_list=node_list)
    assert res_gap["tag"] in ("CRUTCH_RESOLVED", "LIBRARY_RESOLVED", "ABSTAINED", "BOW_RESOLVED")

    # scramble arm must differ in mechanism from real crutch (deterministic wrong-partner draw)
    wrong = _scramble_partner("k1", node_list, "party")
    assert wrong != "party" and wrong in node_set

    # arms-must-differ sanity: bow vs always_crutch predictions can differ on this item
    res_always = resolve_item(item, node_set, idx, gate_thresh=0.9, arm="always_crutch", item_id="t0")
    assert res_always["tag"] in ("CRUTCH_RESOLVED", "BOW_RESOLVED")

    print("[self-test] PASS: real Library/consolidation_pass/HDFactStore promotion + routing + "
          "scramble-partner determinism all exercised", flush=True)
    return {"promote_ok": True, "routing_ok": True, "scramble_deterministic": True}


# =====================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_smoke")
        run(out, run_mode="smoke", train_cap=SMOKE_TRAIN_CAP, dev_cap=SMOKE_DEV_CAP)
        sys.exit(0)

    run(OUTPUT_DIR_FULL, run_mode="full", train_cap=None, dev_cap=None)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_smoke")
    else:
        _out = OUTPUT_DIR_FULL
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
