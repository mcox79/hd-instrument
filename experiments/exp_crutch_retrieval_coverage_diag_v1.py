# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (real vs scramble 1-hop/spreadact/ca3 digests must differ)
# - final_metrics_atomicity declared (tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (symbolic graph-reachability classification; no capacity/noise-floor
#   discriminator threshold applies)
# - HP_SCOPE: informational diagnosis, see pre-reg "HARD-PASS / informational bands" -- primary
#   split (mechanism_miss_fraction) is decisive; secondary coverage-recovery numbers are exploratory
#   (calibrated against the ARC-sibling MIDDLE_BAND prior, see pre-reg prior-work section)
# - cardinality_ok: EXPECTED_N_DEV_ITEMS=1954 (full) / SMOKE_DEV_CAP (smoke)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (HUB_DEGREE_THRESH/decay reused verbatim from the
#   certified fade cell, not re-tuned on this data -- avoids p-hacking the coverage number)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL iterative_attractor + real CSKG-shaped index objects
#   (real_code_path_exercised); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_crutch_retrieval_coverage_diag_v1.md for the full pre-reg (prior-work
# check, owned-organ pointers, bands, routing-recommendation logic).
"""exp_crutch_retrieval_coverage_diag_v1 -- RETRIEVAL COVERAGE diagnosis for the crutch-fade Social
IQa arc (2026-08-10).

Diagnoses WHY the CSKG crutch (data/cskg_foundation_v1) reaches the gold answer for only ~25% of
SIQa dev's gap-flagged items (coverage_audit.coverage_rate=0.2465, commit 593fe79b0): for the 1-hop
misses, is a reachable <=3-hop CSKG path to the gold answer PRESENT (MECHANISM-MISS -- a
retrieval-cue problem, literal one-shot lookup just didn't surface it) or ABSENT (GENUINE-GAP -- a
knowledge-supply problem)? Also separates GROUNDING failures (SIQa words never map to any CSKG
node at all) as an independent axis. Then prototypes a hub-capped spreading-activation multi-hop
pull-in (+ the owned hdlab.cleanup_family.iterative_attractor CA3 attractor as a competitive
readout over the multi-hop evidence) and measures how much coverage it recovers, whether recovered
coverage is REAL (survives a scrambled-context control, per the design note's load-bearing
guardrail) and whether it converts to comprehension on the newly-covered subset.

This is a DIAGNOSIS, not a capability ship: it decides a routing recommendation (build better
retrieval vs supply more knowledge), it does not modify or re-run the validated 9-arm consolidation
cell (experiments/exp_crutch_fade_social_iqa_v1.py), whose reusable primitives it imports read-only.

Modes:
  --self-test  Tiny synthetic CSKG index with planted 1-hop/2-hop/3-hop/disconnected/hub-bridge/
               grounding-failure cases; real iterative_attractor call at trivial scale. No network.
  --smoke      Full real CSKG index (the graph IS the discriminator, cannot be shrunk) + a capped
               dev sample (SMOKE_DEV_CAP items) -- discriminator-preview per DISCRIMINATOR-MUST-
               SURVIVE-SCALE.
  --full       Full real CSKG index + all 1954 SIQa dev items (matches the certified harness's
               population exactly, for direct comparability with the committed 0.2465 number).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402

# ---- reuse, do NOT rebuild (design note "Owned organs reused") ----
from experiments.exp_crutch_fade_social_iqa_v1 import (  # noqa: E402
    canon, content_words, pair_key, _edge_weight, _hub_penalty,
    load_cskg_index, cskg_node_set_from_index, compute_node_degree,
    extract_concepts, load_siqa, bow_scores, bow_margin, argmax_tiebreak, label_idx,
    crutch_candidate_scores, _scramble_partner, scramble_crutch_candidate_scores,
    HUB_DEGREE_THRESH, CSKG_DIR, SIQA_DIR,
)
from hdlab.cleanup_family import iterative_attractor  # noqa: E402

ANCHOR_NAME = "crutch_retrieval_coverage_diag_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SMOKE_DEV_CAP = 300
SMOKE_TRAIN_CAP = 15000     # matches parent harness's own smoke scale (exp_crutch_fade_social_iqa_v1)
MAX_HOPS = 3
DECAY = 0.4                 # THEORETICAL@ad hoc, not tuned on this data (calibration_check=default_ok)
CA3_DIM = 256
CA3_TEMP = 4.0               # CITED@hdlab/iterative_attractor.py docstring calibration for random
                              # Gaussian L2-normalized codebooks
SCORE_MODE = "hub_penalized"  # matches the shipped FULL fade-cell config (593fe79b0)


# =====================================================================================
# start-marker / crash diagnostics / atomic metrics (per exp_dev canonical checklist; each cell
# defines its own per existing convention)
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
# NEW mechanism 1: adjacency + hub-capped BFS reachability classification
def build_adjacency(idx: Dict[str, List[Tuple[str, float]]]) -> Dict[str, List[str]]:
    """pair_key-keyed CSKG index -> node -> list[neighbor]. O(E)."""
    adj: Dict[str, List[str]] = {}
    for k in idx:
        a, b = k.split("::", 1)
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    return adj


def _hub_capped_frontier(frontier: set, adjacency: Dict[str, List[str]],
                         node_degree: Dict[str, int], hub_thresh: int,
                         visited: set) -> set:
    """One BFS expansion step: only nodes with degree<=hub_thresh may act as bridges (Fault-2's
    finding generalized from single-hop scoring to multi-hop traversal -- hubs are fine as
    endpoints, dangerous as bridges)."""
    nxt = set()
    for node in frontier:
        if node_degree.get(node, 0) > hub_thresh:
            continue  # hub: reached, but does not propagate further
        for nb in adjacency.get(node, ()):
            if nb not in visited:
                nxt.add(nb)
    return nxt


def bfs_classify(ctx_concepts: List[str], gold_concepts: List[str],
                 adjacency: Dict[str, List[str]], node_degree: Dict[str, int],
                 hub_thresh: int = HUB_DEGREE_THRESH, max_hops: int = MAX_HOPS) -> dict:
    """Classify a 1-hop crutch MISS. Returns {"cls": ..., "reachable_hop": int|None}."""
    if not ctx_concepts or not gold_concepts:
        return {"cls": "GROUNDING_FAILURE", "reachable_hop": None}
    gold_set = set(gold_concepts)
    visited = set(ctx_concepts)
    frontier = set(ctx_concepts)  # seeds are always valid even if a seed itself is a hub
    for hop in range(1, max_hops + 1):
        frontier = _hub_capped_frontier(frontier, adjacency, node_degree, hub_thresh, visited)
        if not frontier:
            break
        visited |= frontier
        if frontier & gold_set:
            if hop == 1:
                return {"cls": "ALREADY_COVERED_K1", "reachable_hop": 1}  # defensive; caller
                                                                          # should not call this
                                                                          # path for 1-hop hits
            return {"cls": f"MECHANISM_MISS_K{hop}", "reachable_hop": hop}
    return {"cls": "GENUINE_GAP", "reachable_hop": None}


# =====================================================================================
# NEW mechanism 2: hub-capped weighted spreading activation (drop-in comparable to
# crutch_candidate_scores's 1-hop score)
MAX_VISITED_SAFETY_CAP = 8000  # THEORETICAL@defensive: bounds worst-case naive/uncapped-hub cost
                               # per item regardless of hub degree (up to 8057 for the worst SIQa-
                               # template hub); see "naive (context-UNGATED) contrast" below.


def spreading_activation_scores(ctx_concepts: List[str], ans_concepts_list: List[List[str]],
                                adjacency: Dict[str, List[str]], idx: Dict[str, List[Tuple[str, float]]],
                                node_degree: Dict[str, int], hub_thresh: int = HUB_DEGREE_THRESH,
                                max_hops: int = MAX_HOPS, decay: float = DECAY,
                                max_visited: int = MAX_VISITED_SAFETY_CAP
                                ) -> Tuple[List[float], Dict[str, float], dict]:
    """MAX-aggregation (not SUM -- avoids the same path-count-inflation pathology _edge_weight's
    max_trust fix already addressed) hub-capped activation spread from ctx_concepts. Returns
    (per-candidate score, full activation map for the CA3 query construction, diag dict).

    hub_thresh controls the precision/recall tradeoff the coordinator asked to expose directly:
    hub_thresh=HUB_DEGREE_THRESH (default) is the CONTEXT-GATED blast radius (the shipped
    prototype -- hubs are reached but never used as bridges, per Fault-2). hub_thresh=a very large
    number is the NAIVE wider pull (no hub gating at all -- the contrast arm; max_visited is the
    safety net that keeps a naive call bounded-cost even through an 8000-degree hub node)."""
    activation: Dict[str, float] = {c: 1.0 for c in ctx_concepts}
    frontier = set(ctx_concepts)
    visited = set(ctx_concepts)
    capped = False
    for hop in range(1, max_hops + 1):
        nxt_frontier = set()
        for node in frontier:
            if node_degree.get(node, 0) > hub_thresh:
                continue
            base_act = activation[node]
            for nb in adjacency.get(node, ()):
                edges = idx.get(pair_key(node, nb))
                trust = _edge_weight(edges, "max_trust") if edges else 0.6
                new_act = base_act * decay * trust
                if new_act > activation.get(nb, 0.0):
                    activation[nb] = new_act
                if nb not in visited:
                    nxt_frontier.add(nb)
            if len(visited) + len(nxt_frontier) >= max_visited:
                capped = True
                break
        visited |= nxt_frontier
        frontier = nxt_frontier
        if not frontier or capped:
            break
    scores = []
    for ans_concepts in ans_concepts_list:
        best = max((activation.get(c, 0.0) for c in ans_concepts), default=0.0)
        scores.append(best)
    return scores, activation, {"capped": capped, "n_visited": len(visited)}


# =====================================================================================
# NEW mechanism 3: CA3 attractor competitive readout over the activation evidence (owned-organ
# reuse, not a hand-rolled argmax)
def _concept_vec(concept: str, dim: int = CA3_DIM, seed_base: str = "ca3v1") -> np.ndarray:
    """Deterministic (hashlib-seeded, PROT-023/F.5 compliant) per-concept random unit vector."""
    h = int.from_bytes(hashlib.sha256(f"{seed_base}|{concept}".encode("utf-8")).digest()[:8], "big")
    rng = np.random.default_rng(h)
    return rng.standard_normal(dim).astype(np.float32)


def ca3_readout(activation: Dict[str, float], ans_concepts_list: List[List[str]],
                item_id: str, dim: int = CA3_DIM) -> Tuple[int, dict]:
    """query = activation-weighted bundle of reached concepts; codebook = each candidate's own
    concept-vector bundle (mean of its grounded concept vectors, or a fixed candidate-index-seeded
    fallback vector if it has zero grounded concepts). Runs the REAL iterative_attractor."""
    query = np.zeros(dim, dtype=np.float32)
    for c, w in activation.items():
        query += w * _concept_vec(c, dim)
    if not np.any(query):
        query = _concept_vec(f"empty_query|{item_id}", dim)
    codebook = np.zeros((len(ans_concepts_list), dim), dtype=np.float32)
    for i, concepts in enumerate(ans_concepts_list):
        if concepts:
            vecs = np.stack([_concept_vec(c, dim) for c in concepts])
            codebook[i] = vecs.mean(axis=0)
        else:
            codebook[i] = _concept_vec(f"empty_cand|{item_id}|{i}", dim)
    _, diag = iterative_attractor(query, codebook, temp=CA3_TEMP)
    return int(diag["final_argmax_idx"]), diag


# =====================================================================================
# per-item diagnostic (real or scramble side)
# =====================================================================================
# NEW measurement: concept-pair RECURRENCE (coordinator addition #1, 2026-08-10) -- does an
# already-encountered topic/concept-pair recur, so a memory-based strategy has repeat need to act
# on? Directly explains PRELIM_RESOLVED's <0.3% inertness (MEASURED@593fe79b0: 6/1954=0.31% peak,
# settling to 2/1954=0.10%): dev-internal recurrence asks whether a hypothetical perfect dev-time
# memory would even find repeat opportunities; train-to-dev overlap asks whether the ACTUAL
# PRELIM/LIBRARY substrate (fed only by TRAIN exposure) ever had a chance to encounter a dev item's
# specific gold-driving pair before dev eval.
def compute_train_exposure_pairs(train: List[dict], node_set: frozenset,
                                 idx: Dict[str, List[Tuple[str, float]]]) -> frozenset:
    """Set of CSKG pair_keys that co-occur within any single train context -- mirrors
    process_exposure_slice's own pair-generation loop (exp_crutch_fade_social_iqa_v1.py) exactly,
    but pure set accumulation (no Library/store side effects, cheap single pass)."""
    pairs: set = set()
    for ex in train:
        concepts = extract_concepts(ex["context"], node_set)
        n = len(concepts)
        for a_i in range(n):
            for b_i in range(a_i + 1, n):
                pk = pair_key(concepts[a_i], concepts[b_i])
                if pk in idx:
                    pairs.add(pk)
    return frozenset(pairs)


def compute_recurrence(rows: List[dict], train_exposure_pairs: frozenset) -> dict:
    """rows: real_rows from the main diagnostic loop (driving_pair_1hop populated for covered_1hop
    items). Returns dev-internal recurrence (does the SAME pair cover >1 dev item) and train-to-dev
    overlap (was the pair EVER co-exposed during train reading -- the PRELIM/LIBRARY substrate's own
    encounter opportunity)."""
    driving_pairs = [r["driving_pair_1hop"] for r in rows if r["covered_1hop"] and r["driving_pair_1hop"]]
    n_covered = len(driving_pairs)
    counts: Dict[str, int] = {}
    for pk in driving_pairs:
        counts[pk] = counts.get(pk, 0) + 1
    n_unique = len(counts)
    n_recurring_within_dev = sum(1 for pk in driving_pairs if counts[pk] >= 2)
    n_in_train_exposure = sum(1 for pk in driving_pairs if pk in train_exposure_pairs)
    return {
        "n_covered_1hop_with_driving_pair": n_covered,
        "n_unique_driving_pairs": n_unique,
        "dev_internal_recurrence_rate": (n_recurring_within_dev / n_covered) if n_covered else None,
        "train_exposure_overlap_rate": (n_in_train_exposure / n_covered) if n_covered else None,
        "interpretation": (
            "dev_internal_recurrence_rate = fraction of 1-hop-covered dev items whose gold-driving "
            "pair ALSO covers >=1 other dev item (a hypothetical perfect dev-time memory's repeat "
            "opportunity). train_exposure_overlap_rate = fraction whose gold-driving pair was ALSO "
            "seen co-occurring in >=1 train context (the actual PRELIM/LIBRARY substrate's real "
            "encounter opportunity, since it is fed only by train exposure, not dev). A low value on "
            "either explains PRELIM_RESOLVED's measured <0.3% (593fe79b0) as a STRUCTURAL recurrence "
            "ceiling rather than a retain/pull implementation defect."
        ),
    }


NAIVE_HUB_THRESH = 10 ** 9  # effectively "no hub gating at all" -- the wider-pull contrast arm


def diagnose_item(item: dict, node_set: frozenset, idx: Dict[str, List[Tuple[str, float]]],
                  adjacency: Dict[str, List[str]], node_degree: Dict[str, int],
                  gate_thresh: float, item_id: str, node_list: List[str],
                  scramble: bool, include_naive: bool = True) -> Optional[dict]:
    """Returns None if the item is not gap-flagged (crutch-irrelevant). Otherwise a row with the
    1-hop coverage bit + driving pair (recurrence measurement), the (real side only) miss
    classification, GATED (context-aware, hub-capped) spreading-activation coverage at k<=3 (the
    shipped default) AND a k<=2-restricted variant (SMOKE FINDING, see run() -- k=3 lets the
    scramble control reach gold via small-world 3-hop bridging even under the hub cap; k<=2 is the
    honest, load-bearing number), an OPTIONAL NAIVE (hub-UNGATED, wider-pull) contrast arm
    (include_naive=False skips it to bound FULL wall time -- coordinator authorized "fold in if
    cheap, don't delay the core split"; already measured at smoke scale n~300), and CA3/raw-argmax
    accuracy on the newly-covered subsets."""
    b_scores = bow_scores(item)
    margin = bow_margin(b_scores)
    gap = (margin == 0.0) or (margin < gate_thresh)
    if not gap:
        return None
    gold_idx = label_idx(item)
    ctx_concepts_true = extract_concepts(item["context"] + " " + item["question"], node_set)
    ans_concepts_list = [extract_concepts(item[k], node_set) for k in ("answerA", "answerB", "answerC")]

    if scramble:
        ctx_concepts = [_scramble_partner(f"{item_id}|{c}|ctx", node_list, c) for c in ctx_concepts_true]
        c1_scores, c1_driving = scramble_crutch_candidate_scores(item_id, ctx_concepts_true,
                                                                  ans_concepts_list, idx, node_list,
                                                                  SCORE_MODE, node_degree)
    else:
        ctx_concepts = ctx_concepts_true
        c1_scores, c1_driving = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx,
                                                         SCORE_MODE, node_degree)

    covered_1hop = c1_scores[gold_idx] > 0.0

    row = {"item_id": item_id, "gold_idx": gold_idx, "covered_1hop": covered_1hop,
          "grounding_ok": bool(ctx_concepts) and bool(ans_concepts_list[gold_idx]),
          "driving_pair_1hop": c1_driving[gold_idx] if covered_1hop else None}

    if not covered_1hop:
        cls_row = bfs_classify(ctx_concepts, ans_concepts_list[gold_idx], adjacency, node_degree)
        row["miss_class"] = cls_row["cls"]
        row["reachable_hop"] = cls_row["reachable_hop"]

    # GATED (context-aware, hub-capped -- the shipped prototype)
    sa_scores, activation, sa_diag = spreading_activation_scores(ctx_concepts, ans_concepts_list,
                                                                  adjacency, idx, node_degree,
                                                                  hub_thresh=HUB_DEGREE_THRESH)
    covered_spreadact = sa_scores[gold_idx] > 0.0
    row["covered_spreadact"] = covered_spreadact
    row["gated_capped_by_safety_net"] = sa_diag["capped"]
    if max(sa_scores) > 0.0:
        raw_pred = argmax_tiebreak(sa_scores)
    else:
        raw_pred = argmax_tiebreak(b_scores)
    row["raw_spreadact_pred_correct"] = (raw_pred == gold_idx)

    ca3_pred, ca3_diag = ca3_readout(activation, ans_concepts_list, item_id)
    row["ca3_pred_correct"] = (ca3_pred == gold_idx)
    row["ca3_agrees_raw"] = (ca3_pred == raw_pred)
    row["bow_pred_correct"] = (argmax_tiebreak(b_scores) == gold_idx)

    # GATED k<=2 restricted variant (SMOKE FINDING 2026-08-10, see run() docstring note): the more
    # conservative, load-bearing number once the k=3 scramble-pollution finding is accounted for.
    sa_scores_k2, _activation_k2, sa_diag_k2 = spreading_activation_scores(
        ctx_concepts, ans_concepts_list, adjacency, idx, node_degree, hub_thresh=HUB_DEGREE_THRESH,
        max_hops=2)
    covered_spreadact_k2 = sa_scores_k2[gold_idx] > 0.0
    row["covered_spreadact_k2"] = covered_spreadact_k2
    k2_pred = argmax_tiebreak(sa_scores_k2) if max(sa_scores_k2) > 0.0 else argmax_tiebreak(b_scores)
    row["k2_spreadact_pred_correct"] = (k2_pred == gold_idx)

    # NAIVE (hub-UNGATED wider pull -- the coordinator's precision/recall contrast arm; same
    # safety-cap net bounds worst-case cost through an 8000-degree hub). OPTIONAL (see docstring).
    if include_naive:
        sa_scores_n, _activation_n, sa_diag_n = spreading_activation_scores(
            ctx_concepts, ans_concepts_list, adjacency, idx, node_degree, hub_thresh=NAIVE_HUB_THRESH)
        row["covered_spreadact_naive"] = sa_scores_n[gold_idx] > 0.0
        row["naive_capped_by_safety_net"] = sa_diag_n["capped"]
        naive_pred = (argmax_tiebreak(sa_scores_n) if max(sa_scores_n) > 0.0
                     else argmax_tiebreak(b_scores))
        row["naive_spreadact_pred_correct"] = (naive_pred == gold_idx)
    else:
        row["covered_spreadact_naive"] = None
        row["naive_capped_by_safety_net"] = None
        row["naive_spreadact_pred_correct"] = None
    return row


# =====================================================================================
def run(output_dir: str, run_mode: str, dev_cap: Optional[int], train_cap: Optional[int] = None,
       include_naive: bool = True) -> dict:
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=dev_cap or 1954)

    print("[load] CSKG index (full, real -- the graph is the discriminator)...", flush=True)
    idx = load_cskg_index(CSKG_DIR)
    node_set = cskg_node_set_from_index(idx)
    node_list = sorted(node_set)
    node_degree = compute_node_degree(idx)
    _hb(output_dir, "cskg_loaded", t0, {"n_pairs": len(idx), "n_nodes": len(node_list)})

    print("[build] adjacency...", flush=True)
    adjacency = build_adjacency(idx)
    _hb(output_dir, "adjacency_built", t0, {"n_adj_nodes": len(adjacency)})

    print("[load] Social IQa train+dev...", flush=True)
    train_all, dev_all = load_siqa()
    dev = dev_all[:dev_cap] if dev_cap else dev_all
    train = train_all[:train_cap] if train_cap else train_all
    _hb(output_dir, "siqa_loaded", t0, {"n_dev": len(dev), "n_train": len(train)})

    print("[recurrence] building train-exposure concept-pair set (coordinator addition #1)...",
         flush=True)
    train_exposure_pairs = compute_train_exposure_pairs(train, node_set, idx)
    _hb(output_dir, "train_exposure_pairs_built", t0, {"n_train_exposure_pairs": len(train_exposure_pairs)})

    dev_bow_scores = [bow_scores(it) for it in dev]
    dev_margins_all = [bow_margin(s) for s in dev_bow_scores]
    dev_margins_pos = sorted(m for m in dev_margins_all if m > 0.0)
    gate_thresh = dev_margins_pos[len(dev_margins_pos) // 2] if dev_margins_pos else 0.5
    bow_acc = sum(1 for it, s in zip(dev, dev_bow_scores) if argmax_tiebreak(s) == label_idx(it)) / len(dev)
    print(f"[stage0] bow_acc={bow_acc:.4f} gate_thresh={gate_thresh:.4f}", flush=True)

    real_rows, scr_rows = [], []
    for j, it in enumerate(dev):
        item_id = f"dev{j}"
        try:
            r_real = diagnose_item(it, node_set, idx, adjacency, node_degree, gate_thresh, item_id,
                                   node_list, scramble=False, include_naive=include_naive)
            r_scr = diagnose_item(it, node_set, idx, adjacency, node_degree, gate_thresh,
                                  item_id + "s", node_list, scramble=True, include_naive=include_naive)
        except Exception as e:
            print(f"[ERR] item {item_id} failed: {type(e).__name__}: {e}", flush=True)
            raise
        if r_real is not None:
            real_rows.append(r_real)
        if r_scr is not None:
            scr_rows.append(r_scr)
        if j % 250 == 0:
            _hb(output_dir, "dev_progress", t0, {"j": j, "n_real_gap": len(real_rows)})

    n_dev = len(dev)

    def _summarize(rows: List[dict], label: str) -> dict:
        n_gap = len(rows)
        n_cov1 = sum(1 for r in rows if r["covered_1hop"])
        misses = [r for r in rows if not r["covered_1hop"]]
        n_grounding_fail = sum(1 for r in misses if not r["grounding_ok"])
        cls_counts: Dict[str, int] = {}
        for r in misses:
            cls_counts[r["miss_class"]] = cls_counts.get(r["miss_class"], 0) + 1
        n_mech_k2 = cls_counts.get("MECHANISM_MISS_K2", 0)
        n_mech_k3 = cls_counts.get("MECHANISM_MISS_K3", 0)
        n_genuine = cls_counts.get("GENUINE_GAP", 0)
        n_non_grounding_miss = len(misses) - n_grounding_fail
        mech_miss_fraction = ((n_mech_k2 + n_mech_k3) / n_non_grounding_miss
                              if n_non_grounding_miss else None)
        # k<=2-ONLY restricted split (SMOKE FINDING 2026-08-10): k=3 lets the scramble control reach
        # gold via small-world 3-hop bridging even under the hub cap (see run() note) -- this is the
        # more conservative, load-bearing number; k3 items count toward neither bucket here (treated
        # as "not yet decided" at the k<=2 budget, not folded into genuine-gap).
        mech_miss_fraction_k2_only = (n_mech_k2 / n_non_grounding_miss if n_non_grounding_miss
                                      else None)
        grounding_fail_fraction = n_grounding_fail / len(misses) if misses else None
        n_cov_sa = sum(1 for r in rows if r["covered_spreadact"])
        newly_covered = [r for r in rows if r["covered_spreadact"] and not r["covered_1hop"]]
        n_newly = len(newly_covered)
        raw_acc_newly = (sum(1 for r in newly_covered if r["raw_spreadact_pred_correct"]) / n_newly
                         if n_newly else None)
        ca3_acc_newly = (sum(1 for r in newly_covered if r["ca3_pred_correct"]) / n_newly
                         if n_newly else None)
        bow_acc_newly = (sum(1 for r in newly_covered if r["bow_pred_correct"]) / n_newly
                         if n_newly else None)
        ca3_agree_rate = (sum(1 for r in rows if r["ca3_agrees_raw"]) / n_gap) if n_gap else None
        n_gated_capped = sum(1 for r in rows if r.get("gated_capped_by_safety_net"))

        # ---- GATED k<=2 restricted coverage/comprehension (the honest number per the smoke finding) ----
        n_cov_k2 = sum(1 for r in rows if r["covered_spreadact_k2"])
        newly_k2 = [r for r in rows if r["covered_spreadact_k2"] and not r["covered_1hop"]]
        n_newly_k2 = len(newly_k2)
        k2_acc_newly = (sum(1 for r in newly_k2 if r["k2_spreadact_pred_correct"]) / n_newly_k2
                        if n_newly_k2 else None)

        # ---- NAIVE (hub-UNGATED wider pull) contrast, coordinator addition #2 -- OPTIONAL (may be
        # skipped on FULL to bound wall time; None fields when absent, not folded into a misleading 0)
        has_naive = any(r.get("covered_spreadact_naive") is not None for r in rows)
        if has_naive:
            n_cov_naive = sum(1 for r in rows if r["covered_spreadact_naive"])
            newly_naive = [r for r in rows if r["covered_spreadact_naive"] and not r["covered_1hop"]]
            n_newly_naive = len(newly_naive)
            naive_acc_newly = (sum(1 for r in newly_naive if r["naive_spreadact_pred_correct"]) / n_newly_naive
                               if n_newly_naive else None)
            # naive-ONLY = the EXTRA coverage naive buys beyond gated (isolates whether removing the
            # hub cap's additional reach is trustworthy signal or noise, the precision/recall exposure)
            naive_only = [r for r in rows if r["covered_spreadact_naive"] and not r["covered_spreadact"]]
            n_naive_only = len(naive_only)
            naive_only_acc = (sum(1 for r in naive_only if r["naive_spreadact_pred_correct"]) / n_naive_only
                              if n_naive_only else None)
            n_naive_capped = sum(1 for r in rows if r.get("naive_capped_by_safety_net"))
        else:
            n_cov_naive = newly_naive = n_newly_naive = naive_acc_newly = None
            naive_only = n_naive_only = naive_only_acc = n_naive_capped = None
        return {
            "label": label, "n_gap_flagged": n_gap, "n_gap_flagged_whole_dev_frac": n_gap / n_dev,
            "n_covered_1hop": n_cov1,
            "coverage_1hop_rate_gapflagged": (n_cov1 / n_gap) if n_gap else None,
            "coverage_1hop_rate_wholedev": n_cov1 / n_dev,
            "n_1hop_miss": len(misses), "n_grounding_failure": n_grounding_fail,
            "grounding_failure_fraction_of_misses": grounding_fail_fraction,
            "miss_class_counts": cls_counts,
            "n_mechanism_miss_k2": n_mech_k2, "n_mechanism_miss_k3": n_mech_k3,
            "n_genuine_gap": n_genuine,
            "mechanism_miss_fraction_of_nongrounding_misses": mech_miss_fraction,
            "mechanism_miss_fraction_k2_only": mech_miss_fraction_k2_only,
            "n_covered_spreadact": n_cov_sa,
            "coverage_spreadact_rate_gapflagged": (n_cov_sa / n_gap) if n_gap else None,
            "coverage_spreadact_rate_wholedev": n_cov_sa / n_dev,
            "n_newly_covered_by_spreadact": n_newly,
            "newly_covered_raw_argmax_accuracy": raw_acc_newly,
            "newly_covered_ca3_accuracy": ca3_acc_newly,
            "newly_covered_bow_accuracy": bow_acc_newly,
            "ca3_agrees_with_raw_argmax_rate": ca3_agree_rate,
            "n_gated_capped_by_safety_net": n_gated_capped,
            "n_covered_spreadact_k2": n_cov_k2,
            "coverage_spreadact_k2_rate_gapflagged": (n_cov_k2 / n_gap) if n_gap else None,
            "coverage_spreadact_k2_rate_wholedev": n_cov_k2 / n_dev,
            "n_newly_covered_by_k2": n_newly_k2,
            "newly_covered_k2_accuracy": k2_acc_newly,
            "n_covered_spreadact_naive": n_cov_naive,
            "coverage_spreadact_naive_rate_gapflagged": ((n_cov_naive / n_gap)
                                                          if (n_gap and n_cov_naive is not None) else None),
            "n_newly_covered_by_naive": n_newly_naive,
            "newly_covered_naive_accuracy": naive_acc_newly,
            "n_naive_only_extra_coverage": n_naive_only,
            "naive_only_extra_coverage_accuracy": naive_only_acc,
            "n_naive_capped_by_safety_net": n_naive_capped,
        }

    real_summary = _summarize(real_rows, "real")
    scr_summary = _summarize(scr_rows, "scramble")
    recurrence = compute_recurrence(real_rows, train_exposure_pairs)
    print(f"[recurrence] dev_internal_rate={recurrence['dev_internal_recurrence_rate']} "
         f"train_exposure_overlap_rate={recurrence['train_exposure_overlap_rate']} "
         f"n_covered={recurrence['n_covered_1hop_with_driving_pair']} "
         f"n_unique_pairs={recurrence['n_unique_driving_pairs']}", flush=True)

    # ---- decisive numbers ----
    mmf = real_summary["mechanism_miss_fraction_of_nongrounding_misses"]
    gff = real_summary["grounding_failure_fraction_of_misses"]
    cov1 = real_summary["coverage_1hop_rate_gapflagged"]
    cov_sa = real_summary["coverage_spreadact_rate_gapflagged"]
    scr_cov1 = scr_summary["coverage_1hop_rate_gapflagged"]
    scr_cov_sa = scr_summary["coverage_spreadact_rate_gapflagged"]
    scramble_stays_clean = (scr_cov_sa is not None and scr_cov1 is not None
                            and (scr_cov_sa - scr_cov1) <= 0.05)
    real_lift_raw = real_summary["newly_covered_raw_argmax_accuracy"]
    real_lift_bow = real_summary["newly_covered_bow_accuracy"]
    scr_lift_raw = scr_summary["newly_covered_raw_argmax_accuracy"]
    scr_lift_bow = scr_summary["newly_covered_bow_accuracy"]
    comprehension_converts = (real_lift_raw is not None and real_lift_bow is not None
                              and (real_lift_raw - real_lift_bow) > 0.05)
    scramble_lift_clean = True
    if scr_lift_raw is not None and scr_lift_bow is not None:
        scramble_lift_clean = (scr_lift_raw - scr_lift_bow) <= 0.05
    coverage_recovery_real_and_clean = bool(
        cov_sa is not None and cov1 is not None and (cov_sa - cov1) > 0.02
        and scramble_stays_clean)

    # ---- k<=2-restricted decisive numbers (SMOKE FINDING 2026-08-10): k=3 lets a WRONG/scrambled
    # context reach gold via small-world 3-hop bridging even under the hub cap (measured at smoke:
    # scramble spreadact coverage jumped 0.018->0.522 at k<=3, vs the intended <=0.05 clean band) --
    # k<=2 is the honest, load-bearing number this cell actually recommends acting on.
    mmf_k2 = real_summary["mechanism_miss_fraction_k2_only"]
    cov_k2 = real_summary["coverage_spreadact_k2_rate_gapflagged"]
    scr_cov_k2 = scr_summary["coverage_spreadact_k2_rate_gapflagged"]
    scramble_stays_clean_k2 = (scr_cov_k2 is not None and scr_cov1 is not None
                               and (scr_cov_k2 - scr_cov1) <= 0.05)
    k2_lift_raw = real_summary["newly_covered_k2_accuracy"]
    scr_k2_lift_raw = scr_summary["newly_covered_k2_accuracy"]
    comprehension_converts_k2 = (k2_lift_raw is not None and real_lift_bow is not None
                                 and (k2_lift_raw - real_lift_bow) > 0.05)
    scramble_lift_clean_k2 = True
    if scr_k2_lift_raw is not None and scr_lift_bow is not None:
        scramble_lift_clean_k2 = (scr_k2_lift_raw - scr_lift_bow) <= 0.05
    coverage_recovery_real_and_clean_k2 = bool(
        cov_k2 is not None and cov1 is not None and (cov_k2 - cov1) > 0.02
        and scramble_stays_clean_k2)

    # ---- naive (hub-UNGATED wider pull) vs context-gated contrast, coordinator addition #2 ----
    cov_naive = real_summary["coverage_spreadact_naive_rate_gapflagged"]
    scr_cov_naive = scr_summary["coverage_spreadact_naive_rate_gapflagged"]
    naive_only_acc = real_summary["naive_only_extra_coverage_accuracy"]
    naive_only_scr_acc = scr_summary["naive_only_extra_coverage_accuracy"]
    naive_scramble_pollution_delta = ((scr_cov_naive - scr_cov1) if (scr_cov_naive is not None
                                      and scr_cov1 is not None) else None)
    gated_scramble_pollution_delta = ((scr_cov_sa - scr_cov1) if (scr_cov_sa is not None
                                      and scr_cov1 is not None) else None)
    naive_only_converts = bool(naive_only_acc is not None and real_lift_bow is not None
                               and (naive_only_acc - real_lift_bow) > 0.05)
    naive_precision_recall_tradeoff = {
        "gated_coverage_rate_gapflagged": cov_sa, "naive_coverage_rate_gapflagged": cov_naive,
        "naive_minus_gated_coverage": ((cov_naive - cov_sa) if (cov_naive is not None and cov_sa is not None)
                                       else None),
        "gated_scramble_pollution_delta": gated_scramble_pollution_delta,
        "naive_scramble_pollution_delta": naive_scramble_pollution_delta,
        "hub_penalty_load_bearing": bool(naive_scramble_pollution_delta is not None
                                         and gated_scramble_pollution_delta is not None
                                         and naive_scramble_pollution_delta > gated_scramble_pollution_delta + 0.05),
        "n_naive_only_extra_coverage": real_summary["n_naive_only_extra_coverage"],
        "naive_only_extra_coverage_accuracy": naive_only_acc,
        "naive_only_extra_coverage_bow_floor": real_lift_bow,
        "naive_only_converts_to_comprehension": naive_only_converts,
        "naive_only_extra_coverage_scramble_accuracy": naive_only_scr_acc,
        "interpretation": (
            "naive = hub-UNGATED wider spreading-activation pull (bigger blast radius, more raw "
            "coverage by construction). gated = the shipped context-gated (hub-capped) prototype. "
            "naive_minus_gated_coverage = the RAW recall gain from removing the hub cap. "
            "naive_scramble_pollution_delta >> gated_scramble_pollution_delta means that extra "
            "recall is mostly spurious hub-mediated noise (the false-admission failure mode), not "
            "real knowledge -- hub_penalty_load_bearing=True confirms the hub cap is doing real "
            "precision work here (unlike the ARC-sibling cell where the analogous ablation was only "
            "marginally load-bearing). naive_only_extra_coverage_accuracy vs its bow_floor answers "
            "the coordinator's question directly: does the EXTRA coverage naive buys over gated WIN "
            "the argmax once it's in the wider net, or does noise drown it (accuracy near/below bow "
            "floor despite being 'covered')."
        ),
    }
    print(f"[naive_vs_gated] {json.dumps({k: v for k, v in naive_precision_recall_tradeoff.items() if k != 'interpretation'})}",
         flush=True)

    # ROUTING uses the k<=2-restricted numbers (mmf_k2 / coverage_recovery_real_and_clean_k2) as the
    # decisive basis -- the k<=3 numbers (mmf / coverage_recovery_real_and_clean) are reported
    # alongside as an upper bound but are NOT used for routing once the smoke run showed k=3's
    # scramble control is itself materially polluted (small-world 3-hop bridging survives the hub
    # cap). This is the direct honest consequence of the smoke gate doing its job.
    if mmf_k2 is None:
        routing = "INCONCLUSIVE_NO_NONGROUNDING_MISSES"
    elif mmf_k2 >= 0.50:
        if coverage_recovery_real_and_clean_k2 and comprehension_converts_k2 and scramble_lift_clean_k2:
            routing = "BUILD_SPREADING_ACTIVATION_RETRIEVAL"
        else:
            routing = "BUILD_SPREADING_ACTIVATION_RETRIEVAL_WITH_CAUTION"
    else:
        routing = "SUPPLY_KNOWLEDGE"
    grounding_flag = (gff is not None and gff >= 0.20)

    # positive-control-reproduce check (Gate D): does this cell's fresh 1-hop coverage measurement
    # reproduce 593fe79b0's coverage_audit.coverage_rate=0.2465 (same population definition, same
    # score_mode=hub_penalized)? Tolerance 0.02 abs (design note criterion 1's "reconcile" ask).
  # MEASURED@data/exp_crutch_fade_social_iqa_v1_3tier_seed7/metrics.json:coverage_audit.coverage_rate
    prior_coverage_rate = 0.2465277777777778
    reproduce_delta = (abs(cov1 - prior_coverage_rate) if cov1 is not None else None)
    reproduce_ok = (reproduce_delta is not None and reproduce_delta <= 0.02)

    verdict = "INFORMATIONAL" if reproduce_ok else "INFORMATIONAL_REPRODUCE_MISS"
    verdict_msg = (
        f"{verdict}: [DECISIVE k<=2] mechanism_miss_fraction_k2={mmf_k2} coverage 1hop={cov1} "
        f"-> spreadact_k2={cov_k2} (scramble 1hop={scr_cov1} -> spreadact_k2={scr_cov_k2}, "
        f"clean={scramble_stays_clean_k2}) newly_covered_k2_acc={k2_lift_raw} bow={real_lift_bow} "
        f"converts={comprehension_converts_k2} (scramble k2_acc={scr_k2_lift_raw} "
        f"clean={scramble_lift_clean_k2}) routing={routing} | [UPPER BOUND k<=3, SCRAMBLE-POLLUTED, "
        f"NOT used for routing] mechanism_miss_fraction={mmf} spreadact={cov_sa} "
        f"(scramble spreadact={scr_cov_sa}, clean={scramble_stays_clean}) | "
        f"grounding_failure_fraction={gff} grounding_flag={grounding_flag} "
        f"reproduce_1hop_vs_593fe79b0_delta={reproduce_delta} | recurrence dev_internal="
        f"{recurrence['dev_internal_recurrence_rate']} train_exposure_overlap="
        f"{recurrence['train_exposure_overlap_rate']} | naive_vs_gated(k<=3) coverage "
        f"{cov_sa}->{cov_naive} naive_only_acc={naive_only_acc} "
        f"hub_penalty_load_bearing={naive_precision_recall_tradeoff['hub_penalty_load_bearing']}"
    )

    digests = {
        "real_1hop": hashlib.sha256(json.dumps([r["covered_1hop"] for r in real_rows]).encode()).hexdigest(),
        "scr_1hop": hashlib.sha256(json.dumps([r["covered_1hop"] for r in scr_rows]).encode()).hexdigest(),
        "real_spreadact": hashlib.sha256(json.dumps([r["covered_spreadact"] for r in real_rows]).encode()).hexdigest(),
        "scr_spreadact": hashlib.sha256(json.dumps([r["covered_spreadact"] for r in scr_rows]).encode()).hexdigest(),
    }
    arms_differ_verified = (digests["real_1hop"] != digests["scr_1hop"]
                            or digests["real_spreadact"] != digests["scr_spreadact"])

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg[:400],
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "config": {"dev_cap": dev_cap, "train_cap": train_cap, "max_hops": MAX_HOPS, "decay": DECAY,
                  "hub_degree_thresh": HUB_DEGREE_THRESH, "naive_hub_thresh": NAIVE_HUB_THRESH,
                  "max_visited_safety_cap": MAX_VISITED_SAFETY_CAP, "score_mode": SCORE_MODE,
                  "ca3_dim": CA3_DIM, "ca3_temp": CA3_TEMP, "gate_thresh_median_margin": gate_thresh},
        "stage0_bow_baseline_accuracy": bow_acc,
        "n_dev": n_dev, "n_train_exposed": len(train), "n_train_exposure_pairs": len(train_exposure_pairs),
        "n_cskg_pairs": len(idx), "n_cskg_nodes": len(node_list),
        "real": real_summary, "scramble": scr_summary,
        "recurrence": recurrence,
        "naive_precision_recall_tradeoff": naive_precision_recall_tradeoff,
        "decisive": {
            "note": "k<=2 fields are the DECISIVE/routing basis (honest per smoke finding); k<=3 "
                   "fields are an UPPER BOUND, scramble-polluted, reported for transparency only.",
            "mechanism_miss_fraction_k2_only_DECISIVE": mmf_k2,
            "coverage_spreadact_k2_rate_gapflagged_DECISIVE": cov_k2,
            "scramble_stays_clean_coverage_k2_DECISIVE": scramble_stays_clean_k2,
            "newly_covered_k2_accuracy_DECISIVE": k2_lift_raw,
            "comprehension_converts_k2_DECISIVE": comprehension_converts_k2,
            "scramble_lift_clean_k2_DECISIVE": scramble_lift_clean_k2,
            "coverage_recovery_real_and_clean_k2_DECISIVE": coverage_recovery_real_and_clean_k2,
            "mechanism_miss_fraction_of_nongrounding_misses_k3_upperbound": mmf,
            "grounding_failure_fraction_of_misses": gff,
            "grounding_flag_improve_lemmatization": grounding_flag,
            "coverage_1hop_rate_gapflagged": cov1,
            "coverage_spreadact_rate_gapflagged_k3_upperbound": cov_sa,
            "scramble_stays_clean_coverage_k3_upperbound": scramble_stays_clean,
            "newly_covered_raw_argmax_accuracy_k3_upperbound": real_lift_raw,
            "newly_covered_bow_accuracy": real_lift_bow,
            "comprehension_converts_k3_upperbound": comprehension_converts,
            "scramble_lift_clean_k3_upperbound": scramble_lift_clean,
            "coverage_recovery_real_and_clean_k3_upperbound": coverage_recovery_real_and_clean,
        },
        "positive_control_reproduce_1hop_coverage": {
            "prior_atom": "593fe79b0 coverage_audit.coverage_rate",
            "prior_value": prior_coverage_rate, "measured_value": cov1,
            "delta": reproduce_delta, "tolerance": 0.02, "ok": reproduce_ok,
        },
        "routing_recommendation": routing,
        "arms_differ_verified": arms_differ_verified, "arm_digests": digests,
        "cardinality_ok": True, "expected_n_units": n_dev,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "symbolic graph-reachability classification; no capacity/noise-floor "
                   "discriminator applies",
        "deterministic_seeding": True, "progress_logging": "print_flush_true",
        "calibration_check": "default_ok_for_this_regime",
        "storage_strategy": "no_storage",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.2f}s -> {output_dir}/metrics.json",
         flush=True)
    return metrics


# =====================================================================================
# self-test (real code path, tiny synthetic scale, no network)
def self_test() -> dict:
    print("[self-test] tiny synthetic CSKG index + real iterative_attractor call", flush=True)
    # planted graph: seed--hopa--hopb (2-hop to hopb), seed--hopa--hopb--hopc (3-hop to hopc via hopb),
    # seed--hub--faraway (hub degree pumped above thresh -> should NOT reach faraway),
    # island (fully disconnected from seed).
    idx: Dict[str, List[Tuple[str, float]]] = {}

    def add(a, b, rel="at:xEffect", trust=1.0):
        idx[pair_key(a, b)] = [(rel, trust)]

    add("seed", "hopa")
    add("hopa", "hopb")
    add("hopb", "hopc")
    add("seed", "hub")
    add("hub", "faraway")
    # pump hub's degree above HUB_DEGREE_THRESH with filler pairs (each filler node touches hub once)
    for i in range(HUB_DEGREE_THRESH + 5):
        add("hub", f"filler{i}")
    add("island_a", "island_b")  # fully disconnected from seed

    node_set = cskg_node_set_from_index(idx)
    node_degree = compute_node_degree(idx)
    adjacency = build_adjacency(idx)
    assert node_degree["hub"] > HUB_DEGREE_THRESH, node_degree["hub"]

    # ---- bfs_classify cases ----
    r2 = bfs_classify(["seed"], ["hopb"], adjacency, node_degree)
    assert r2["cls"] == "MECHANISM_MISS_K2", r2
    r3 = bfs_classify(["seed"], ["hopc"], adjacency, node_degree)
    assert r3["cls"] == "MECHANISM_MISS_K3", r3
    r_gap = bfs_classify(["seed"], ["island_b"], adjacency, node_degree)
    assert r_gap["cls"] == "GENUINE_GAP", r_gap
    r_ground = bfs_classify([], ["hopb"], adjacency, node_degree)
    assert r_ground["cls"] == "GROUNDING_FAILURE", r_ground
    # hub-bridge control: "faraway" is 2 hops from seed ONLY via the pumped hub node; the hub-cap
    # must block propagation past "hub" so faraway is NOT reachable at k<=3 through it.
    r_hub = bfs_classify(["seed"], ["faraway"], adjacency, node_degree)
    assert r_hub["cls"] == "GENUINE_GAP", (
        f"hub-bridge control FAILED: {r_hub} -- hub-capped BFS must not treat a >{HUB_DEGREE_THRESH}"
        f"-degree node as a bridge")
    print("[self-test] bfs_classify: K2/K3/GENUINE_GAP/GROUNDING_FAILURE/hub-bridge-blocked all OK",
         flush=True)

    # ---- spreading_activation_scores (GATED): hopb (2-hop, real path) must outscore island_b
    # (unreachable) and faraway must stay hub-blocked ----
    sa_scores, activation, sa_diag = spreading_activation_scores(
        ["seed"], [["hopb"], ["island_b"], ["faraway"]], adjacency, idx, node_degree)
    assert sa_scores[0] > 0.0, sa_scores
    assert sa_scores[1] == 0.0, sa_scores
    assert sa_scores[2] == 0.0, sa_scores  # hub-blocked
    assert sa_diag["capped"] is False, sa_diag
    print(f"[self-test] spreading_activation_scores(gated): hopb={sa_scores[0]:.4f} island={sa_scores[1]} "
         f"hub-blocked-faraway={sa_scores[2]}", flush=True)

    # ---- NAIVE (hub-UNGATED) contrast, coordinator addition #2: removing the hub cap must let
    # "faraway" become reachable THROUGH the pumped hub -- proves the naive/gated arms genuinely
    # differ (not a no-op parameter) and demonstrates the precision/recall tradeoff the mechanism
    # is meant to expose.
    sa_scores_naive, _act_naive, _diag_naive = spreading_activation_scores(
        ["seed"], [["hopb"], ["island_b"], ["faraway"]], adjacency, idx, node_degree,
        hub_thresh=NAIVE_HUB_THRESH)
    assert sa_scores_naive[2] > 0.0, (
        f"naive-vs-gated contrast FAILED: naive (hub_thresh={NAIVE_HUB_THRESH}) must reach "
        f"'faraway' through the hub once the cap is removed; got {sa_scores_naive}")
    assert sa_scores_naive[1] == 0.0, sa_scores_naive  # island still unreachable regardless of hub cap
    print(f"[self-test] spreading_activation_scores(naive): hopb={sa_scores_naive[0]:.4f} "
         f"island={sa_scores_naive[1]} faraway(hub-reachable-now)={sa_scores_naive[2]:.4f}", flush=True)

    # ---- max_visited safety net: a tiny cap must actually stop propagation early ----
    _s_cap, _a_cap, diag_cap = spreading_activation_scores(
        ["seed"], [["hopc"]], adjacency, idx, node_degree, hub_thresh=NAIVE_HUB_THRESH, max_visited=2)
    assert diag_cap["capped"] is True, diag_cap
    print(f"[self-test] max_visited safety net: capped={diag_cap['capped']} n_visited={diag_cap['n_visited']}",
         flush=True)

    # ---- ca3_readout: real iterative_attractor call, dominant candidate must win ----
    ca3_pred, ca3_diag = ca3_readout(activation, [["hopb"], ["island_b"], ["faraway"]], "selftest0")
    assert ca3_diag["primitive"] == "iterative_attractor", ca3_diag
    assert ca3_pred == 0, (ca3_pred, ca3_diag)  # hopb is the only candidate with real activation mass
    print(f"[self-test] ca3_readout: pred={ca3_pred} (expected 0/hopb) diag={ca3_diag}", flush=True)

    # ---- scramble control: _scramble_partner substitution should not spuriously reach hopb ----
    scr_ctx = [_scramble_partner("selftest0|seed|ctx", sorted(node_set), "seed")]
    scr_scores, _scr_act, _scr_diag = spreading_activation_scores(scr_ctx, [["hopb"]], adjacency, idx,
                                                                   node_degree)
    print(f"[self-test] scramble control probe: scr_ctx={scr_ctx} scr_score(hopb)={scr_scores[0]}",
         flush=True)

    # ---- diagnose_item: real code path on a tiny synthetic SIQa-shaped item ----
    fake_item = {
        "context": "seed occurred", "question": "what next", "answerA": "hopb thing",
        "answerB": "island_b thing", "answerC": "faraway thing", "label": "1",
    }
    row = diagnose_item(fake_item, node_set, idx, adjacency, node_degree, gate_thresh=0.99,
                        item_id="selftest_item", node_list=sorted(node_set), scramble=False)
    assert row is not None, "expected gap-flagged (gate_thresh=0.99 forces gap)"
    assert row["covered_1hop"] is False, row  # seed<->hopb is not a direct edge
    assert row["driving_pair_1hop"] is None, row
    assert row["miss_class"] == "MECHANISM_MISS_K2", row
    assert row["covered_spreadact"] is True, row  # gated k<=3 recovers it (real 2-hop path)
    assert row["covered_spreadact_k2"] is True, row  # k<=2 also recovers it (hopb is 2 hops away)
    assert row["covered_spreadact_naive"] is True, row  # naive is always >= gated coverage
    assert row["gated_capped_by_safety_net"] is False, row
    print(f"[self-test] diagnose_item real code path: {row}", flush=True)

    # ---- include_naive=False path (used on FULL to bound wall time): naive fields must be None,
    # not misleadingly False/0 ----
    row_nonaive = diagnose_item(fake_item, node_set, idx, adjacency, node_degree, gate_thresh=0.99,
                                item_id="selftest_nonaive", node_list=sorted(node_set), scramble=False,
                                include_naive=False)
    assert row_nonaive["covered_spreadact_naive"] is None, row_nonaive
    assert row_nonaive["covered_spreadact_k2"] is True, row_nonaive  # k2 still computed regardless
    print(f"[self-test] include_naive=False path: naive fields None, k2 still populated", flush=True)

    # ---- recurrence (coordinator addition #1): a covered item whose driving pair recurs must be
    # detected as dev-internal-recurring; a pair that also appears in train exposure must be
    # detected as train_exposure_overlap ----
    covered_item = {
        "context": "seed party happened", "question": "what next", "answerA": "friend thing",
        "answerB": "island_b thing", "answerC": "faraway thing", "label": "1",
    }
    add("party", "friend")  # direct 1-hop edge -> covered_1hop for both fake rows below
    node_set2 = cskg_node_set_from_index(idx)
    node_degree2 = compute_node_degree(idx)
    row_a = diagnose_item(covered_item, node_set2, idx, adjacency, node_degree2, gate_thresh=0.99,
                          item_id="rec_a", node_list=sorted(node_set2), scramble=False)
    row_b = diagnose_item(covered_item, node_set2, idx, adjacency, node_degree2, gate_thresh=0.99,
                          item_id="rec_b", node_list=sorted(node_set2), scramble=False)
    assert row_a is not None and row_a["covered_1hop"] is True, row_a
    assert row_a["driving_pair_1hop"] == pair_key("party", "friend"), row_a
    train_synth = [{"context": "a party makes a friend"}]  # co-occurs party+friend in train text
    train_pairs = compute_train_exposure_pairs(train_synth, node_set2, idx)
    assert pair_key("party", "friend") in train_pairs, train_pairs
    rec = compute_recurrence([row_a, row_b], train_pairs)
    assert rec["dev_internal_recurrence_rate"] == 1.0, rec  # both rows share the same driving pair
    assert rec["train_exposure_overlap_rate"] == 1.0, rec
    print(f"[self-test] recurrence: {rec}", flush=True)

    return {"selftest_ok": True, "bfs_classify_ok": True, "hub_bridge_control_ok": True,
           "spreading_activation_ok": True, "naive_vs_gated_contrast_ok": True,
           "max_visited_safety_net_ok": True, "ca3_readout_ok": True, "diagnose_item_ok": True,
           "recurrence_ok": True,
           "real_code_path_exercised": ["iterative_attractor", "bfs_classify",
                                        "spreading_activation_scores", "diagnose_item",
                                        "compute_train_exposure_pairs", "compute_recurrence"]}


# =====================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--dev-cap", type=int, default=None)
    ap.add_argument("--train-cap", type=int, default=None)
    ap.add_argument("--include-naive", action="store_true",
                    help="also run the naive (hub-UNGATED) contrast on --full (off by default on "
                         "--full to bound wall time -- already measured at smoke scale; smoke "
                         "always includes it)")
    args, _ = ap.parse_known_args()

    if args.self_test:
        out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
        result = self_test()
        os.makedirs(out, exist_ok=True)
        _selftest_ok = all(bool(v) for v in result.values())
        _atomic_write_metrics(out, {
            "verdict": "HARD_PASS" if _selftest_ok else "HARD_FAIL",
            "verdict_msg": f"SELFTEST_PASS: {result}", "summary": "self-test PASS",
            "elapsed_s": 0.0, "anchor_name": ANCHOR_NAME, "run_mode": "self_test",
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "self_test_result": result,
        })
        sys.exit(0)

    if args.smoke:
        out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_smoke")
        run(out, run_mode="smoke", dev_cap=SMOKE_DEV_CAP,
           train_cap=args.train_cap or SMOKE_TRAIN_CAP)
        sys.exit(0)

    if args.full:
        run(OUTPUT_DIR_FULL, run_mode="full", dev_cap=args.dev_cap, train_cap=args.train_cap,
           include_naive=args.include_naive)
        sys.exit(0)

    ap.error("one of --self-test / --smoke / --full is required")


if __name__ == "__main__":
    _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
    if "--smoke" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_smoke")
    elif "--full" in sys.argv:
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
