"""exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.

Experiment 3E: Layer 0.75 v3-CLEAN arc-closure attempt (LLM-free).

Question (arc-closure discipline per feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03):
does the v3-clean pipeline (uniform PPR -> v3 structural KG-slot filter -> FHRR
composition; NO Stage 1 IDF-reweight, NO Stage 2 hub-dampen) close the retrieval-
architecture arc when tested at Exp 3C FULL scale (N_DIM=8192, 100q x 3 seeds)?

Skunkworks path (b) recommendation: v3-only isolated SMOKE (0.7667 = 92% of ORACLE
0.8222 at N=4096 30q x 3 seeds) is INSUFFICIENT for arc-closure. Need:
  (i)   FULL scale (N=8192, 100q x 3 seeds)
  (ii)  MAIN arm = v3-clean stacked (drop S1+S2 based on 3D VET diagnosis)
  (iii) 3-seed cv < 0.10
  (iv)  ALL seeds >= 0.60

Rationale for drop-S1S2: Exp 3D VET (Skunkworks-verified) showed
  MAIN_S1_S2_V3_STACKED = 0.5111 (S1+S2 present)
  MAIN_V3_CLEAN         = 0.7667 (S1+S2 absent)
  gap = 0.2556 = S1+S2 SUBTRACT from structural filtering. Stage 2 hub-dampen
  demotes hop-2 hub-subject facts (mid IS a hub by construction). Optimal
  pipeline: uniform PPR -> v3 filter -> composition.

Precedents (MEASURED@d:/AI/hd-instrument/data/exp_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy):
  ORACLE_COMPOSITION_SANITY       = 0.8222
  EXP3_BASELINE_REPRODUCTION      = 0.4111
  STAGE3_V1_QUERY_ONLY_RESCORE    = 0.0111
  STAGE3_V2_ITERATIVE_QUERY_AUG   = 0.0333
  MAIN_LAYER075_STACKED_V3        = 0.5111  (this cell = ARM_V3_STACKED_WITH_S1S2)
  STAGE3_V3_STRUCTURAL_SLOT_ONLY  = 0.7667  (this cell = ARM_MAIN_V3_CLEAN)
  RANDOM_CONTROL                  = 0.0556

Arms (7):
  ARM_ORACLE_COMPOSITION_SANITY           (target ~0.82 drift <= 0.10)
  ARM_EXP3_BASELINE_REPRODUCTION          (target ~0.41 drift <= 0.10)
  ARM_STAGE3_V1_QUERY_ONLY_RESCORE        (Fix#28 gate ~0.011 drift <= 0.005)
  ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY  (Fix#28 gate ~0.033 drift <= 0.005)
  ARM_MAIN_V3_CLEAN                       (DISCRIMINATOR; target 0.74+ full closure)
  ARM_V3_STACKED_WITH_S1S2                (Exp 3D MAIN reproduce ~0.511 drift <= 0.05)
  ARM_RANDOM_CANDIDATES_CONTROL           (chance ~0.05)

Bands (arc-closure discipline):
  HARD_PASS_FULL_ARC_CLOSURE:
       MAIN_V3_CLEAN >= 0.90 * ORACLE (~0.74)
       AND per-seed cv < 0.10 AND all seeds >= 0.60
  HARD_PASS_MEASURED_MECHANISM:
       MAIN_V3_CLEAN >= 0.60 * ORACLE (~0.49) but arc-closure gate breached
  MIDDLE_BAND:  0.413 <= MAIN_V3_CLEAN < 0.60 * ORACLE
  HARD_FAIL:    MAIN_V3_CLEAN < 0.413
  HALT_ORACLE_DRIFT:            |ORACLE - 0.8222| >= 0.10
  FLAG_V3_STACKED_S1S2_DRIFT:   |V3_STACKED_WITH_S1S2 - 0.5111| >= 0.05
  FLAG_V1_HF_DRIFT:             |STAGE3_V1 - 0.0111| >= 0.005 (soft; Fix#28)
  FLAG_V2_HF_DRIFT:             |STAGE3_V2 - 0.0333| >= 0.005 (soft; Fix#28)

ASCII-only. mixed CPU (BGE batched torch, PPR + FHRR sequential per query). sharded storage.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm prediction-array sha256)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_floor_computed=0.025  THEORETICAL@sqrt(K_final/N)=sqrt(5/8192) Plate 1995
# - discriminator_reachability: True (HP 0.74 >> CRLB 0.025)
# - baseline_in_band: 0.05 < EXP3_BASELINE=0.4111 < 0.95 MEASURED@ Exp 3D
# - discriminator survives scale: SMOKE at N=4096 matches Exp 3D SMOKE regime
#     (prior chain-grade evidence); FULL at N=8192 100q x 3 seeds matches Exp 3C scale
# - HARD_PASS strictly above floor: 0.90 * ORACLE scaling + cv gate + all-seeds-gate
# - HP_SCOPE: HP applies only to ARM_MAIN_V3_CLEAN; reproduction gates on
#     ORACLE (drift <= 0.10), EXP3_BASELINE (soft), V1/V2 (soft), V3_STACKED_WITH_S1S2 (0.05)
# - cardinality_ok: EXPECTED_N_UNITS = 7 arms x 3 seeds = 21 (FULL); 7 * 1 = 7 (SMOKE)
# - per-unit failure-class instrumentation (specific Exception only)
# - calibration_check: default_ok_for_this_regime (v3 has no thresholds to tune)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - progress_logging: print_flush_true (see arc-closure §17)
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except (AttributeError, TypeError, ValueError):
    pass

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import argparse
import hashlib
import json
import platform
import random
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
import scipy.sparse as sp

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402


ANCHOR_NAME = "substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03"
BI_MODEL = "BAAI/bge-small-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "

# Vocabulary (identical to Exp 3B/3C/3D)
ENTITIES = [
    "Alton", "Bexley", "Coral", "Delft", "Erie", "Fjord", "Gulch", "Hara",
    "Iona", "Juno", "Kelm", "Loam", "Mesa", "Nord", "Osek", "Pome",
    "Quill", "Riva", "Solt", "Tern",
    "Umbra", "Vail", "Wren", "Xylo", "Yara", "Zorn", "Ashe", "Brix",
    "Corv", "Dune", "Ebon", "Frey", "Glim", "Holt", "Ivor", "Jarl",
    "Kord", "Larn", "Mote", "Nyx",
]  # 40 entities
RELATIONS = ["mayor", "capital", "river", "neighbor", "founder"]
HUB_INDICES = [0, 1, 2]
HUB_OVER_SAMPLE = 3.0

# ---------- CLI ----------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if "--self-test" in sys.argv:
    RUN_MODE = "self_test"
elif "--full" in sys.argv:
    RUN_MODE = "full"
elif "--smoke" in sys.argv:
    RUN_MODE = "smoke"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()

if RUN_MODE == "full":
    N_DIM = 8192
    N_QUERIES_TARGET = 100
    SEEDS = [11, 17, 23]
else:
    N_DIM = 4096
    N_QUERIES_TARGET = 24
    SEEDS = [11]

TOP_K = 5
PPR_ALPHA = 0.15
PPR_ITERS = 5
PPR_TOP_K = 5
UNION_MAX = 30

# ---- Layer 0.75 hyperparameters (matched to Exp 3D for reproduction gates) ----
HUB_DEG_THRESH = 8
HUB_DAMPEN_FACTOR = 0.30
K_FINAL = 5

# ---- v1 (query-only rescore + MMR) hyperparameters ----
MMR_LAMBDA_V1 = 0.3

# ---- v2 (iterative query-augmentation) hyperparameters ----
B_BRIDGES = 5
W_QUERY_ANCHOR = 1.0
W_AUG = 1.0
BRIDGE_MIN_COOCCUR = 2


# ---------- FHRR primitives ----------
def rand_phase_hd(rng: np.random.Generator, n_dim: int) -> np.ndarray:
    return (rng.random(n_dim, dtype=np.float64) * 2.0 - 1.0) * np.pi


def bind_phase(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    s = a + b
    return (s + np.pi) % (2.0 * np.pi) - np.pi


def unbind_phase(query: np.ndarray, bound: np.ndarray) -> np.ndarray:
    s = bound - query
    return (s + np.pi) % (2.0 * np.pi) - np.pi


def phase_cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.cos(a - b)))


def phase_cos_batch(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    return np.mean(np.cos(B - a[None, :]), axis=1)


# ---------- corpus construction (identical to Exp 3B/3C/3D) ----------
def build_corpus(rng_seed: int, n_dim: int, n_queries_target: int) -> Dict:
    rng = np.random.default_rng(rng_seed)
    py_rng = random.Random(rng_seed)
    E = len(ENTITIES)
    R = len(RELATIONS)

    weights = np.ones(E, dtype=np.float64)
    for h in HUB_INDICES:
        weights[h] = HUB_OVER_SAMPLE
    weights_norm = weights / weights.sum()

    facts_dict: Dict[str, Dict[str, str]] = {e: {} for e in ENTITIES}
    for e in ENTITIES:
        for r in RELATIONS:
            v_idx = int(rng.choice(E, p=weights_norm))
            facts_dict[e][r] = ENTITIES[v_idx]

    facts: List[Tuple[str, str, str, str]] = []
    for e in ENTITIES:
        for r in RELATIONS:
            v = facts_dict[e][r]
            text = "The %s of %s is %s." % (r, e, v)
            facts.append((e, r, v, text))

    entity_codebook = np.zeros((E, n_dim), dtype=np.float64)
    for i in range(E):
        entity_codebook[i] = rand_phase_hd(rng, n_dim)
    relation_codebook = np.zeros((R, n_dim), dtype=np.float64)
    for i in range(R):
        relation_codebook[i] = rand_phase_hd(rng, n_dim)
    value_codebook = entity_codebook

    n_facts = len(facts)
    fact_hds = np.zeros((n_facts, n_dim), dtype=np.float64)
    for i, (e, r, v, _t) in enumerate(facts):
        ei = ENTITIES.index(e)
        ri = RELATIONS.index(r)
        vi = ENTITIES.index(v)
        inner = bind_phase(relation_codebook[ri], value_codebook[vi])
        fact_hds[i] = bind_phase(entity_codebook[ei], inner)

    in_deg = np.zeros(E, dtype=np.int64)
    for (_e, _r, v, _t) in facts:
        in_deg[ENTITIES.index(v)] += 1
    hub_empirical = sorted(range(E), key=lambda i: -in_deg[i])[:3]
    hub_set = set(hub_empirical) | set(HUB_INDICES)

    queries: List[Dict] = []
    tries = 0
    max_tries = n_queries_target * 100
    while len(queries) < n_queries_target and tries < max_tries:
        tries += 1
        e0 = py_rng.choice(ENTITIES)
        r1 = py_rng.choice(RELATIONS)
        r2 = py_rng.choice(RELATIONS)
        mid = facts_dict[e0][r2]
        mid_idx = ENTITIES.index(mid)
        if mid_idx not in hub_set:
            continue
        answer = facts_dict[mid][r1]
        if answer == e0 or mid == e0:
            continue
        text = "What is the %s of the %s of %s?" % (r1, r2, e0)
        gt1 = gt2 = None
        for i, (e, r, v, _t) in enumerate(facts):
            if e == e0 and r == r2:
                gt1 = i
            if e == mid and r == r1:
                gt2 = i
        if gt1 is None or gt2 is None:
            continue
        queries.append({
            "text": text, "e0": e0, "r1": r1, "r2": r2,
            "mid": mid, "answer": answer,
            "gt_chunks": [gt1, gt2],
            "mid_is_hub": mid_idx in hub_set,
        })

    return {
        "facts": facts,
        "fact_hds": fact_hds,
        "entity_codebook": entity_codebook,
        "relation_codebook": relation_codebook,
        "value_codebook": value_codebook,
        "queries": queries,
        "facts_dict": facts_dict,
        "in_deg": in_deg.tolist(),
        "hub_set": sorted(hub_set),
        "hub_empirical_top3": hub_empirical,
    }


# ---------- KG + PPR primitives (Exp 2C / 3 / 3B/C/D; unchanged) ----------
def build_entity_kg(facts, n_entities):
    rows, cols, vals = [], [], []
    neighbors: Dict[int, Set[int]] = {i: set() for i in range(n_entities)}
    for (e, _r, v, _t) in facts:
        i = ENTITIES.index(e); j = ENTITIES.index(v)
        if i == j: continue
        rows.append(i); cols.append(j); vals.append(1.0)
        rows.append(j); cols.append(i); vals.append(1.0)
        neighbors[i].add(j); neighbors[j].add(i)
    C = sp.coo_matrix((vals, (rows, cols)), shape=(n_entities, n_entities),
                      dtype=np.float64).tocsr()
    col_sums = np.asarray(C.sum(axis=0)).ravel()
    col_safe = np.where(col_sums > 0, col_sums, 1.0)
    inv = sp.diags(1.0 / col_safe)
    A = C @ inv
    if (col_sums == 0).any():
        A = A.tolil()
        for j in np.where(col_sums == 0)[0]:
            A[:, j] = 0.0
        A = A.tocsr()
    degrees = np.array([len(neighbors[i]) for i in range(n_entities)], dtype=np.int64)
    return A, neighbors, degrees


def ppr_iterate_sparse(A, seed_vec, alpha, iters):
    s = seed_vec.astype(np.float64)
    s_sum = float(s.sum())
    if s_sum <= 0:
        raise ValueError("PPR seed must have positive mass")
    s = s / s_sum
    x = s.copy()
    for _ in range(iters):
        x = (1.0 - alpha) * (A @ x) + alpha * s
        raw = float(x.sum())
        if raw > 0 and abs(raw - 1.0) > 0.005:
            x = x / raw
    return x


def seed_vec_from_indices(indices, n):
    v = np.zeros(n, dtype=np.float64)
    for i in indices: v[i] += 1.0
    if v.sum() == 0:
        v = np.ones(n, dtype=np.float64)
    return v / v.sum()


# ---------- Stage 1: node-specificity IDF seed re-weight ----------
def compute_passage_counts(facts, n_entities):
    counts = np.zeros(n_entities, dtype=np.float64)
    for (e, _r, v, _t) in facts:
        counts[ENTITIES.index(e)] += 1.0
        counts[ENTITIES.index(v)] += 1.0
    return counts


def stage1_reweight_seed(seed_entities, passage_counts, n_entities):
    v = np.zeros(n_entities, dtype=np.float64)
    for i in seed_entities:
        pc = passage_counts[i]
        v[i] = 1.0 / max(pc, 1.0)
    s = v.sum()
    if s <= 0:
        return seed_vec_from_indices(sorted(seed_entities), n_entities)
    return v / s


# ---------- Stage 2: hub-dampening ----------
def stage2_hub_dampen_adjacency(A, degrees, hub_deg_thresh, dampen_factor):
    hub_indices = np.where(degrees > hub_deg_thresh)[0]
    if len(hub_indices) == 0:
        return A.copy()
    n = A.shape[0]
    scale = np.ones(n, dtype=np.float64)
    scale[hub_indices] = dampen_factor
    D = sp.diags(scale)
    return (A @ D).tocsr()


# ---------- Stage 3 v1: query-only rescore + MMR ----------
def stage3_v1_rescore_mmr(candidate_indices, query_bge, fact_bge, k_final, mmr_lambda):
    if not candidate_indices:
        return []
    cand_arr = np.array(candidate_indices, dtype=np.int64)
    cand_emb = fact_bge[cand_arr]
    sims_q = cand_emb @ query_bge
    sims_cc = cand_emb @ cand_emb.T
    selected: List[int] = []
    remaining = set(range(len(cand_arr)))
    while remaining and len(selected) < k_final:
        best_i = None; best_score = -np.inf
        for i in remaining:
            if not selected:
                score = mmr_lambda * sims_q[i]
            else:
                red = max(sims_cc[i, j] for j in selected)
                score = mmr_lambda * sims_q[i] - (1.0 - mmr_lambda) * red
            if score > best_score:
                best_score = score; best_i = i
        if best_i is None: break
        selected.append(best_i); remaining.discard(best_i)
    return [int(cand_arr[i]) for i in selected]


# ---------- Stage 3 v2: iterative query-augmentation ----------
def extract_bridge_candidates(candidate_indices, facts, query_text, b_bridges, min_cooccur):
    entity_to_facts: Dict[int, Set[int]] = {}
    for fi in candidate_indices:
        e, _r, v, _t = facts[fi]
        ei = ENTITIES.index(e); vi = ENTITIES.index(v)
        entity_to_facts.setdefault(ei, set()).add(fi)
        entity_to_facts.setdefault(vi, set()).add(fi)
    bridge_pool = [(ei, len(fs)) for ei, fs in entity_to_facts.items()
                   if len(fs) >= min_cooccur]
    q_lower = query_text.lower()
    bridge_pool = [(ei, cnt) for (ei, cnt) in bridge_pool
                   if ENTITIES[ei].lower() not in q_lower]
    bridge_pool.sort(key=lambda t: -t[1])
    return [ei for (ei, _c) in bridge_pool[:b_bridges]]


def stage3_v2_iterative_query_augmentation(candidate_indices, query_text, query_bge,
                                             fact_bge, facts, k_final, b_bridges,
                                             w_query, w_aug, bridge_min_cooccur,
                                             bge_encode_fn):
    if not candidate_indices:
        return [], []
    cand_arr = np.array(candidate_indices, dtype=np.int64)
    cand_emb = fact_bge[cand_arr]
    cos_q0 = cand_emb @ query_bge
    bridges = extract_bridge_candidates(candidate_indices, facts, query_text,
                                          b_bridges, bridge_min_cooccur)
    if not bridges:
        scores = cos_q0
    else:
        aug_texts = [query_text + " " + ENTITIES[b] for b in bridges]
        aug_emb = bge_encode_fn(aug_texts)
        cos_aug = aug_emb @ cand_emb.T
        aug_agg = cos_aug.max(axis=0)
        scores = w_query * cos_q0 + w_aug * aug_agg
    order = np.argsort(scores)[::-1][:k_final]
    selected = [int(cand_arr[i]) for i in order]
    return selected, bridges


# ---------- Stage 3 v3: STRUCTURAL KG-slot filtering (MAIN mechanism) ----------
def stage3_v3_structural_slot_filter(candidate_indices, facts, e0, r1, r2,
                                       extracted_bridges, k_final):
    """LLM-free structural KG-slot filter (Exp 3D primitive; MAIN of v3-clean).

    Query semantics: "What is the r1 of the r2 of e0?"
      hop-1 fact:  (e0, r2, mid_entity)   -- retrieves the bridge mid
      hop-2 fact:  (mid_entity, r1, ans)  -- retrieves the final answer

    v3 output = union of:
      HOP_1_CANDIDATE = {f in P_1 | f.subject == e0 AND f.relation == r2}
      HOP_2_CANDIDATE = {f in P_1 | f.subject == b AND f.relation == r1
                                     for b in extracted_bridges}

    Cap union at k_final. If union empty, fallback to P_1[:k_final].
    """
    bridge_set = set(extracted_bridges)
    e0_i = ENTITIES.index(e0)

    hop_1_cands: List[int] = []
    hop_2_cands: List[int] = []
    distractors: List[int] = []
    for fi in candidate_indices:
        e, r, v, _t = facts[fi]
        si = ENTITIES.index(e)
        vi = ENTITIES.index(v)
        if si == e0_i and r == r2:
            hop_1_cands.append(fi)
        if si in bridge_set and r == r1:
            hop_2_cands.append(fi)
        if vi in bridge_set and si != e0_i:
            distractors.append(fi)

    union_ordered: List[int] = []
    seen: Set[int] = set()
    for fi in hop_1_cands + hop_2_cands:
        if fi not in seen:
            union_ordered.append(fi)
            seen.add(fi)

    diag = {
        "n_hop_1_cands": len(hop_1_cands),
        "n_hop_2_cands": len(hop_2_cands),
        "n_distractors": len(distractors),
        "n_union_pre_cap": len(union_ordered),
        "fallback_to_p1": False,
    }

    if not union_ordered:
        diag["fallback_to_p1"] = True
        filtered = list(candidate_indices[:k_final])
    else:
        filtered = union_ordered[:k_final]

    return filtered, diag


# ---------- composition primitive (identical to Exp 3D ORACLE) ----------
def composition_primitive(q, corpus, retrieved_idx):
    e0 = q["e0"]; r1 = q["r1"]; r2 = q["r2"]
    E_cb = corpus["entity_codebook"]
    R_cb = corpus["relation_codebook"]
    V_cb = corpus["value_codebook"]
    e0i = ENTITIES.index(e0)
    r1i = RELATIONS.index(r1)
    r2i = RELATIONS.index(r2)
    if not retrieved_idx:
        return ENTITIES[0]
    retrieved_hds = corpus["fact_hds"][retrieved_idx]

    q1 = bind_phase(E_cb[e0i], R_cb[r2i])
    best_sim = -np.inf; mid_idx = 0
    for k in range(retrieved_hds.shape[0]):
        candidate_mid = unbind_phase(q1, retrieved_hds[k])
        sims = phase_cos_batch(candidate_mid, V_cb)
        s = float(sims.max())
        if s > best_sim: best_sim = s; mid_idx = int(sims.argmax())

    q2 = bind_phase(V_cb[mid_idx], R_cb[r1i])
    best_sim = -np.inf; ans_idx = 0
    for k in range(retrieved_hds.shape[0]):
        candidate_ans = unbind_phase(q2, retrieved_hds[k])
        sims = phase_cos_batch(candidate_ans, V_cb)
        s = float(sims.max())
        if s > best_sim: best_sim = s; ans_idx = int(sims.argmax())
    return ENTITIES[ans_idx]


# ---------- BGE retrieval ----------
def bge_load_encoder():
    import torch
    from transformers import AutoModel, AutoTokenizer
    DEV = torch.device("cpu")
    tok = AutoTokenizer.from_pretrained(BI_MODEL)
    mdl = AutoModel.from_pretrained(BI_MODEL).to(DEV).eval()

    def encode(texts):
        out = []
        for i in range(0, len(texts), 32):
            batch = texts[i:i + 32]
            t = tok(batch, return_tensors="pt", padding=True, truncation=True,
                    max_length=64).to(DEV)
            with torch.no_grad():
                o = mdl(**t)
            v = o.last_hidden_state[:, 0, :].float().cpu().numpy()
            v = v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-8)
            out.append(v)
        return np.concatenate(out, 0).astype(np.float32)

    return tok, mdl, encode


def bge_top_k(q_emb, fact_emb, top_k):
    sims = q_emb @ fact_emb.T
    out = []
    for i in range(sims.shape[0]):
        order = np.argsort(sims[i])[::-1][:top_k].tolist()
        out.append(order)
    return out


# ---------- pipeline: PPR union ----------
def ppr_pipeline_union(bge_ret, corpus, A, n_entities, use_stage1, passage_counts):
    seed_entities: Set[int] = set()
    for idx in bge_ret:
        e, _r, v, _t = corpus["facts"][idx]
        seed_entities.add(ENTITIES.index(e))
        seed_entities.add(ENTITIES.index(v))
    if use_stage1:
        seed_vec = stage1_reweight_seed(seed_entities, passage_counts, n_entities)
    else:
        seed_vec = seed_vec_from_indices(sorted(seed_entities), n_entities)
    ppr_dist = ppr_iterate_sparse(A, seed_vec, PPR_ALPHA, PPR_ITERS)
    top_k_ent = np.argsort(ppr_dist)[::-1][:PPR_TOP_K].tolist()
    top_k_ent_set = set(top_k_ent)
    ppr_facts: List[int] = []
    for i, (e, _r, v, _t) in enumerate(corpus["facts"]):
        if ENTITIES.index(e) in top_k_ent_set or ENTITIES.index(v) in top_k_ent_set:
            ppr_facts.append(i)
    union = list(dict.fromkeys(bge_ret + ppr_facts))
    if len(union) > UNION_MAX:
        union = union[:UNION_MAX]
    return union


# ---------- arms ----------
def arm_oracle(q, corpus):
    return composition_primitive(q, corpus, q["gt_chunks"])


def arm_exp3_baseline(q, corpus, bge_ret, A, n_entities, passage_counts):
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities, False, passage_counts)
    return composition_primitive(q, corpus, union)


def arm_main_v3_clean(q, corpus, bge_ret, A, n_entities, passage_counts):
    """MAIN discriminator: uniform PPR (no S1, no S2) -> v3 filter -> composition.
    Reproduces Exp 3D's ARM_STAGE3_V3_STRUCTURAL_SLOT_ONLY (0.7667 at N=4096 SMOKE).
    """
    p1_pool = ppr_pipeline_union(bge_ret, corpus, A, n_entities, False, passage_counts)
    bridges = extract_bridge_candidates(p1_pool, corpus["facts"], q["text"],
                                          B_BRIDGES, BRIDGE_MIN_COOCCUR)
    filtered, v3_diag = stage3_v3_structural_slot_filter(
        p1_pool, corpus["facts"], q["e0"], q["r1"], q["r2"], bridges, K_FINAL)
    return composition_primitive(q, corpus, filtered), p1_pool, bridges, v3_diag


def arm_v3_stacked_with_s1s2(q, corpus, bge_ret, A_dampened, n_entities, passage_counts):
    """Exp 3D MAIN reproduction: S1 + S2 + v3 stacked. Target 0.511 drift <= 0.05."""
    p1_pool = ppr_pipeline_union(bge_ret, corpus, A_dampened, n_entities, True, passage_counts)
    bridges = extract_bridge_candidates(p1_pool, corpus["facts"], q["text"],
                                          B_BRIDGES, BRIDGE_MIN_COOCCUR)
    filtered, v3_diag = stage3_v3_structural_slot_filter(
        p1_pool, corpus["facts"], q["e0"], q["r1"], q["r2"], bridges, K_FINAL)
    return composition_primitive(q, corpus, filtered), p1_pool, bridges, v3_diag


def arm_stage3_v1_only(q, corpus, bge_ret, A, n_entities, passage_counts,
                        query_bge, fact_bge):
    """Fix#28 reproduction: expects ~0.011."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities, False, passage_counts)
    filtered = stage3_v1_rescore_mmr(union, query_bge, fact_bge, K_FINAL, MMR_LAMBDA_V1)
    return composition_primitive(q, corpus, filtered)


def arm_stage3_v2_only(q, corpus, bge_ret, A, n_entities, passage_counts,
                        query_bge, fact_bge, bge_encode_fn):
    """Fix#28 reproduction: expects ~0.033."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities, False, passage_counts)
    filtered, _bridges = stage3_v2_iterative_query_augmentation(
        union, q["text"], query_bge, fact_bge, corpus["facts"],
        K_FINAL, B_BRIDGES, W_QUERY_ANCHOR, W_AUG, BRIDGE_MIN_COOCCUR, bge_encode_fn)
    return composition_primitive(q, corpus, filtered)


def arm_random_control(q, corpus, rng, k=K_FINAL):
    n_facts = corpus["fact_hds"].shape[0]
    rand_idx = rng.choice(n_facts, size=k, replace=False).tolist()
    return composition_primitive(q, corpus, rand_idx)


# ---------- per-seed run ----------
def run_seed(seed, bge_encode_fn):
    print("[seed=%d] building hub-and-spoke corpus N_DIM=%d target_q=%d" % (
        seed, N_DIM, N_QUERIES_TARGET), flush=True)
    t0 = time.perf_counter()
    corpus = build_corpus(seed, N_DIM, N_QUERIES_TARGET)
    fact_texts = [t for (_e, _r, _v, t) in corpus["facts"]]
    n_queries = len(corpus["queries"])
    n_facts = len(corpus["facts"])
    print("  built facts=%d hub_bridge_queries=%d hub_empirical_top3=%s elapsed=%.1fs" % (
        n_facts, n_queries, corpus["hub_empirical_top3"],
        time.perf_counter() - t0), flush=True)

    if n_queries < 10:
        return {"seed": seed, "vacuous": True, "n_queries": n_queries,
                "per_arm": {}, "elapsed_s": time.perf_counter() - t0}

    print("[seed=%d] building entity KG..." % seed, flush=True)
    A, neighbors, degrees = build_entity_kg(corpus["facts"], len(ENTITIES))
    passage_counts = compute_passage_counts(corpus["facts"], len(ENTITIES))
    A_dampened = stage2_hub_dampen_adjacency(A, degrees, HUB_DEG_THRESH, HUB_DAMPEN_FACTOR)
    print("  KG built n_edges=%d degrees_max=%d n_hubs=%d elapsed=%.1fs" % (
        A.nnz // 2, int(degrees.max()),
        int((degrees > HUB_DEG_THRESH).sum()), time.perf_counter() - t0), flush=True)

    print("[seed=%d] BGE encoding + top_k=%d retrieval..." % (seed, TOP_K), flush=True)
    tr = time.perf_counter()
    q_emb = bge_encode_fn([Q_INSTR + q["text"] for q in corpus["queries"]])
    fact_emb = bge_encode_fn(fact_texts)
    bge_retrieved = bge_top_k(q_emb, fact_emb, TOP_K)
    print("  bge_done elapsed=%.1fs" % (time.perf_counter() - tr), flush=True)

    rng = np.random.default_rng(seed + 1000)
    arm_names = [
        "ARM_ORACLE_COMPOSITION_SANITY",
        "ARM_EXP3_BASELINE_REPRODUCTION",
        "ARM_STAGE3_V1_QUERY_ONLY_RESCORE",
        "ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY",
        "ARM_MAIN_V3_CLEAN",
        "ARM_V3_STACKED_WITH_S1S2",
        "ARM_RANDOM_CANDIDATES_CONTROL",
    ]
    preds_by_arm: Dict[str, List[str]] = {n: [] for n in arm_names}
    per_query_diag: List[Dict] = []

    v3_clean_fallback_count = 0
    v3_clean_slot_fire_count = 0
    v3_s1s2_fallback_count = 0
    v3_s1s2_slot_fire_count = 0

    n_entities = len(ENTITIES)
    for qi, q in enumerate(corpus["queries"]):
        bge_ret = bge_retrieved[qi]
        query_bge = q_emb[qi]

        p_oracle = arm_oracle(q, corpus)
        p_exp3_base = arm_exp3_baseline(q, corpus, bge_ret, A, n_entities, passage_counts)
        p_s3v1 = arm_stage3_v1_only(q, corpus, bge_ret, A, n_entities, passage_counts,
                                     query_bge, fact_emb)
        p_s3v2 = arm_stage3_v2_only(q, corpus, bge_ret, A, n_entities, passage_counts,
                                     query_bge, fact_emb, bge_encode_fn)
        p_main, main_p1_pool, main_bridges, main_v3_diag = arm_main_v3_clean(
            q, corpus, bge_ret, A, n_entities, passage_counts)
        p_s1s2, s1s2_p1_pool, s1s2_bridges, s1s2_v3_diag = arm_v3_stacked_with_s1s2(
            q, corpus, bge_ret, A_dampened, n_entities, passage_counts)
        p_rand = arm_random_control(q, corpus, rng)

        preds_by_arm["ARM_ORACLE_COMPOSITION_SANITY"].append(p_oracle)
        preds_by_arm["ARM_EXP3_BASELINE_REPRODUCTION"].append(p_exp3_base)
        preds_by_arm["ARM_STAGE3_V1_QUERY_ONLY_RESCORE"].append(p_s3v1)
        preds_by_arm["ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY"].append(p_s3v2)
        preds_by_arm["ARM_MAIN_V3_CLEAN"].append(p_main)
        preds_by_arm["ARM_V3_STACKED_WITH_S1S2"].append(p_s1s2)
        preds_by_arm["ARM_RANDOM_CANDIDATES_CONTROL"].append(p_rand)

        if main_v3_diag["fallback_to_p1"]:
            v3_clean_fallback_count += 1
        else:
            v3_clean_slot_fire_count += 1
        if s1s2_v3_diag["fallback_to_p1"]:
            v3_s1s2_fallback_count += 1
        else:
            v3_s1s2_slot_fire_count += 1

        if qi < 10:
            gt_set = set(q["gt_chunks"])
            mid_idx = ENTITIES.index(q["mid"])
            per_query_diag.append({
                "qi": qi, "text": q["text"], "e0": q["e0"], "r1": q["r1"], "r2": q["r2"],
                "mid": q["mid"], "mid_idx": mid_idx, "answer": q["answer"],
                "gt_chunks": q["gt_chunks"], "bge_top5": bge_ret,
                "p_oracle": p_oracle, "p_exp3_base": p_exp3_base,
                "p_main_v3_clean": p_main, "p_v3_stacked_with_s1s2": p_s1s2,
                "p_s3v1": p_s3v1, "p_s3v2": p_s3v2, "p_rand": p_rand,
                "main_p1_pool_size": len(main_p1_pool),
                "gt_in_main_p1_pool": sorted(gt_set & set(main_p1_pool)),
                "main_bridges": [ENTITIES[b] for b in main_bridges],
                "mid_in_main_bridges": mid_idx in main_bridges,
                "main_v3_diag": main_v3_diag,
                "s1s2_p1_pool_size": len(s1s2_p1_pool),
                "gt_in_s1s2_p1_pool": sorted(gt_set & set(s1s2_p1_pool)),
                "s1s2_bridges": [ENTITIES[b] for b in s1s2_bridges],
                "mid_in_s1s2_bridges": mid_idx in s1s2_bridges,
                "s1s2_v3_diag": s1s2_v3_diag,
            })
        if qi % 10 == 0:
            print("  q=%d/%d elapsed=%.1fs" % (qi, n_queries, time.perf_counter() - t0),
                  flush=True)

    truths = [q["answer"] for q in corpus["queries"]]
    per_arm = {}
    for name in arm_names:
        preds = preds_by_arm[name]
        correct = sum(1 for (p, t) in zip(preds, truths) if p == t)
        acc = correct / len(truths) if truths else 0.0
        per_arm[name] = {"accuracy": acc, "n_correct": correct, "n": len(truths)}

    # ARMS-MUST-DIFFER (META_RULE_AF) with SUCCESS-MODE EXEMPTION for MAIN_V3_CLEAN
    # vs ORACLE at 100% GT-coverage.
    digests = {}
    for name in arm_names:
        blob = "|".join(preds_by_arm[name]).encode("utf-8")
        digests[name] = hashlib.sha256(blob).hexdigest()[:16]

    exempt_pairs: Set[Tuple[str, str]] = set()
    # Success-mode exemption: if all diag queries had 2/2 GT in main pool + no fallback,
    # MAIN_V3_CLEAN receives the same input as ORACLE and MUST emit identical output.
    if per_query_diag and all(
        len(d["gt_in_main_p1_pool"]) == 2 and not d["main_v3_diag"]["fallback_to_p1"]
        for d in per_query_diag
    ):
        exempt_pairs.add(tuple(sorted(["ARM_ORACLE_COMPOSITION_SANITY",
                                        "ARM_MAIN_V3_CLEAN"])))

    seen: Dict[str, str] = {}
    arms_differ_violations = []
    for name, dig in digests.items():
        if dig in seen:
            other = seen[dig]
            pair = tuple(sorted([other, name]))
            if pair not in exempt_pairs:
                arms_differ_violations.append((other, name, dig))
        else:
            seen[dig] = name

    return {
        "seed": seed,
        "n_queries": len(corpus["queries"]),
        "n_facts": n_facts,
        "n_dim": N_DIM,
        "top_k": TOP_K,
        "vacuous": False,
        "per_arm": per_arm,
        "arm_digests": digests,
        "arms_differ_violations": arms_differ_violations,
        "arms_differ_exempted_pairs": [list(p) for p in sorted(exempt_pairs)],
        "hub_empirical_top3": corpus["hub_empirical_top3"],
        "hub_set": corpus["hub_set"],
        "degrees_max": int(degrees.max()),
        "n_hubs_by_degree": int((degrees > HUB_DEG_THRESH).sum()),
        "per_query_diag": per_query_diag,
        "v3_fire_summary": {
            "v3_clean_slot_fire_count": v3_clean_slot_fire_count,
            "v3_clean_fallback_count": v3_clean_fallback_count,
            "v3_s1s2_slot_fire_count": v3_s1s2_slot_fire_count,
            "v3_s1s2_fallback_count": v3_s1s2_fallback_count,
            "n_queries": len(corpus["queries"]),
        },
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed):
    active = [s for s in per_seed if not s.get("vacuous", False)]
    if not active:
        return ("HARD_FAIL",
                "HARD_FAIL_ALL_VACUOUS: no seeds produced >=10 hub-bridge queries.",
                {})

    arm_names = ["ARM_ORACLE_COMPOSITION_SANITY",
                 "ARM_EXP3_BASELINE_REPRODUCTION",
                 "ARM_STAGE3_V1_QUERY_ONLY_RESCORE",
                 "ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY",
                 "ARM_MAIN_V3_CLEAN",
                 "ARM_V3_STACKED_WITH_S1S2",
                 "ARM_RANDOM_CANDIDATES_CONTROL"]
    per_arm_mean = {}
    per_arm_per_seed = {n: [] for n in arm_names}
    for name in arm_names:
        accs = [s["per_arm"][name]["accuracy"] for s in active]
        per_arm_mean[name] = float(np.mean(accs))
        per_arm_per_seed[name] = accs

    oracle = per_arm_mean["ARM_ORACLE_COMPOSITION_SANITY"]
    exp3_base = per_arm_mean["ARM_EXP3_BASELINE_REPRODUCTION"]
    s3v1 = per_arm_mean["ARM_STAGE3_V1_QUERY_ONLY_RESCORE"]
    s3v2 = per_arm_mean["ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY"]
    main_v3_clean = per_arm_mean["ARM_MAIN_V3_CLEAN"]
    v3_s1s2 = per_arm_mean["ARM_V3_STACKED_WITH_S1S2"]
    rand_ctrl = per_arm_mean["ARM_RANDOM_CANDIDATES_CONTROL"]

    # Precedents from Exp 3D MEASURED@ off-disk 2026-07-03
    ORACLE_PRECEDENT = 0.8222
    EXP3_BASELINE_PRECEDENT = 0.4111
    STAGE3_V1_PRECEDENT = 0.0111
    STAGE3_V2_PRECEDENT = 0.0333
    V3_S1S2_PRECEDENT = 0.5111

    oracle_drift = abs(oracle - ORACLE_PRECEDENT)
    exp3_base_drift = abs(exp3_base - EXP3_BASELINE_PRECEDENT)
    s3v1_drift = abs(s3v1 - STAGE3_V1_PRECEDENT)
    s3v2_drift = abs(s3v2 - STAGE3_V2_PRECEDENT)
    v3_s1s2_drift = abs(v3_s1s2 - V3_S1S2_PRECEDENT)

    hp_full_target = 0.90 * oracle
    hp_measured_target = 0.60 * oracle
    hp_exp3_baseline_floor = EXP3_BASELINE_PRECEDENT   # 0.4111

    # Per-seed stability (arc-closure discipline)
    main_seeds = per_arm_per_seed["ARM_MAIN_V3_CLEAN"]
    seed_mean = float(np.mean(main_seeds))
    seed_std = float(np.std(main_seeds, ddof=0))
    cv = (seed_std / seed_mean) if seed_mean > 0 else float("inf")
    min_seed = float(min(main_seeds)) if main_seeds else 0.0
    all_seeds_above_060 = min_seed >= 0.60
    cv_ok = cv < 0.10

    # Cardinality
    expected_units = 7 * len(active)
    actual_units = sum(len(s["per_arm"]) for s in active)
    cardinality_ok = actual_units == expected_units
    arms_differ_ok = all(len(s["arms_differ_violations"]) == 0 for s in active)

    summary = ("ORACLE=%.3f (drift=%.3f vs %.3f) EXP3_BASE=%.3f (drift=%.3f vs %.3f) "
                "S3V1=%.3f (drift=%.3f vs %.3f) S3V2=%.3f (drift=%.3f vs %.3f) "
                "V3_STACKED_S1S2=%.3f (drift=%.3f vs %.3f) "
                "MAIN_V3_CLEAN=%.3f seeds=%s cv=%.3f min_seed=%.3f RANDOM=%.3f | "
                "hp_full=%.3f hp_measured=%.3f | "
                "cardinality_ok=%s arms_differ_ok=%s cv_ok(<0.10)=%s all_seeds_ge_0.60=%s") % (
        oracle, oracle_drift, ORACLE_PRECEDENT,
        exp3_base, exp3_base_drift, EXP3_BASELINE_PRECEDENT,
        s3v1, s3v1_drift, STAGE3_V1_PRECEDENT,
        s3v2, s3v2_drift, STAGE3_V2_PRECEDENT,
        v3_s1s2, v3_s1s2_drift, V3_S1S2_PRECEDENT,
        main_v3_clean, [round(x, 3) for x in main_seeds], cv, min_seed, rand_ctrl,
        hp_full_target, hp_measured_target,
        cardinality_ok, arms_differ_ok, cv_ok, all_seeds_above_060)

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d got %d. %s" % (
                    expected_units, actual_units, summary), per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical. %s" % summary,
                per_arm_mean)

    # ORACLE drift
    if oracle_drift >= 0.10:
        return ("HARD_FAIL",
                "HALT_ORACLE_DRIFT: ORACLE=%.3f drifted %.3f from precedent %.3f. "
                "Composition primitive changed. Do NOT trust MAIN_V3_CLEAN interp. %s" % (
                    oracle, oracle_drift, ORACLE_PRECEDENT, summary), per_arm_mean)

    soft_flags = []
    if exp3_base_drift >= 0.10:
        soft_flags.append("FLAG_BASELINE_DRIFT: EXP3_BASELINE=%.3f drift=%.3f" % (
            exp3_base, exp3_base_drift))
    if s3v1_drift >= 0.005:
        soft_flags.append("FLAG_V1_HF_DRIFT: STAGE3_V1=%.3f drift=%.3f vs %.4f" % (
            s3v1, s3v1_drift, STAGE3_V1_PRECEDENT))
    if s3v2_drift >= 0.005:
        soft_flags.append("FLAG_V2_HF_DRIFT: STAGE3_V2=%.3f drift=%.3f vs %.4f" % (
            s3v2, s3v2_drift, STAGE3_V2_PRECEDENT))
    if v3_s1s2_drift >= 0.05:
        soft_flags.append("FLAG_V3_STACKED_S1S2_DRIFT: V3_STACKED_S1S2=%.3f drift=%.3f vs %.4f "
                          "(cannot fully validate S1+S2-subtract diagnosis)" % (
                              v3_s1s2, v3_s1s2_drift, V3_S1S2_PRECEDENT))
    soft_note = (" | " + "; ".join(soft_flags)) if soft_flags else ""

    # HARD_FAIL: below baseline
    if main_v3_clean < hp_exp3_baseline_floor:
        return ("HARD_FAIL",
                "HARD_FAIL_V3_CLEAN_REGRESSED: MAIN_V3_CLEAN=%.3f < EXP3_BASELINE_FLOOR=%.3f. "
                "v3-clean regressed at FULL scale below the Exp 3 baseline. SMOKE result "
                "(0.7667 at N=4096) was regime-artifact; the mechanism does NOT survive "
                "the FULL regime. ESCALATE to path (a) BridgeRAG tripartite s(q, b, c) or "
                "revisit v3 slot-fire discipline. %s%s" % (
                    main_v3_clean, hp_exp3_baseline_floor, summary, soft_note),
                per_arm_mean)

    # MIDDLE_BAND: 0.413 <= MAIN < 0.60 * ORACLE
    if main_v3_clean < hp_measured_target:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_V3_CLEAN_PARTIAL: MAIN_V3_CLEAN=%.3f in [%.3f, %.3f). "
                "Partial signal above EXP3 baseline but below MEASURED_MECHANISM tier "
                "(0.60 * ORACLE). Route to Director for regime assessment. %s%s" % (
                    main_v3_clean, hp_exp3_baseline_floor, hp_measured_target,
                    summary, soft_note),
                per_arm_mean)

    # Fix#28-mirror gate: strict arc-closure requires ALL 4 criteria simultaneously
    arc_closure_gates = [
        ("main_ge_0.90_oracle", main_v3_clean >= hp_full_target),
        ("cv_lt_0.10", cv_ok),
        ("all_seeds_ge_0.60", all_seeds_above_060),
        ("v3_stacked_s1s2_drift_lt_0.05", v3_s1s2_drift < 0.05),
    ]
    all_arc_closure_gates_pass = all(x[1] for x in arc_closure_gates)
    failed_gates = [name for (name, ok) in arc_closure_gates if not ok]

    if all_arc_closure_gates_pass:
        return ("HARD_PASS",
                "HARD_PASS_FULL_ARC_CLOSURE_V3_CLEAN: MAIN_V3_CLEAN=%.3f >= 0.90 * ORACLE=%.3f "
                "(hp_full=%.3f) AND cv=%.3f<0.10 AND all seeds >= 0.60 (min=%.3f) AND "
                "V3_STACKED_S1S2 reproduces Exp 3D MAIN within 0.05 (drift=%.3f vs %.3f). "
                "Retrieval-architecture arc CLOSES on hub-concept-bridge scope at FULL scale: "
                "uniform PPR + v3 structural KG-slot filter + FHRR composition validated with "
                "3-seed stability. Path a' (structural triple filter) vindicated over path (b) "
                "(BGE-augmentation) at both interface AND full-closure tier. S1+S2-subtract "
                "diagnosis reproduced (gap=%.3f). Next: 170K-atom Director-KB scale re-test. "
                "%s%s" % (
                    main_v3_clean, oracle, hp_full_target, cv, min_seed,
                    v3_s1s2_drift, V3_S1S2_PRECEDENT,
                    main_v3_clean - v3_s1s2, summary, soft_note),
                per_arm_mean)

    # HARD_PASS_MEASURED_MECHANISM: MAIN clears 0.60 * ORACLE but arc-closure gate breached
    return ("HARD_PASS",
            "HARD_PASS_MEASURED_MECHANISM_V3_CLEAN: MAIN_V3_CLEAN=%.3f >= 0.60 * ORACLE=%.3f "
            "(hp_measured=%.3f). Mechanism validated at FULL scale but arc-closure gate NOT "
            "cleared: failed_gates=%s. Do NOT frame as arc-closure. Stability/scale gap "
            "surfaced; Director determines whether to accept MEASURED_MECHANISM tier as "
            "sufficient or route to iteration. V3_STACKED_S1S2=%.3f (drift=%.3f). %s%s" % (
                main_v3_clean, oracle, hp_measured_target, failed_gates,
                v3_s1s2, v3_s1s2_drift, summary, soft_note),
            per_arm_mean)


# ---------- selftest ----------
def selftest():
    """Formula selftest per PROT-022."""
    rng = np.random.default_rng(0)
    n = 512

    # 1. bind/unbind identity
    a = rand_phase_hd(rng, n); b = rand_phase_hd(rng, n)
    c = bind_phase(a, b)
    sim = phase_cos(unbind_phase(a, c), b)
    assert sim > 0.99, "bind/unbind identity: sim=%.4f" % sim

    # 2. Triple unbind
    e = rand_phase_hd(rng, n); r = rand_phase_hd(rng, n); v = rand_phase_hd(rng, n)
    triple = bind_phase(e, bind_phase(r, v))
    sim = phase_cos(unbind_phase(bind_phase(e, r), triple), v)
    assert sim > 0.99, "triple unbind: sim=%.4f" % sim

    # 3. Corpus + hub structure
    corpus = build_corpus(11, 256, n_queries_target=5)
    in_deg = corpus["in_deg"]
    hub_in = sum(in_deg[h] for h in HUB_INDICES)
    hub_frac = hub_in / max(sum(in_deg), 1)
    expected_baseline = 3.0 / 40.0
    assert hub_frac >= 2 * expected_baseline, (
        "hub-injection failed: hub_frac=%.3f expected>=%.3f" % (
            hub_frac, 2 * expected_baseline))

    # 4. Queries respect hub-bridge scope
    if len(corpus["queries"]) >= 1:
        for q in corpus["queries"]:
            mid_idx = ENTITIES.index(q["mid"])
            assert mid_idx in set(corpus["hub_set"]), (
                "scope violation: query mid=%r idx=%d" % (q["mid"], mid_idx))

    # 5. Composition primitive
    if len(corpus["queries"]) >= 1:
        p = arm_oracle(corpus["queries"][0], corpus)
        assert p in ENTITIES, "oracle arm returned invalid: %r" % p

    # 6. Entity KG + PPR
    A, neigh, degrees = build_entity_kg(corpus["facts"], len(ENTITIES))
    seed_v = seed_vec_from_indices([0], len(ENTITIES))
    ppr = ppr_iterate_sparse(A, seed_v, 0.15, 5)
    assert abs(ppr.sum() - 1.0) < 0.01, "PPR mass leaked: %.4f" % ppr.sum()

    # 7. v3 STRUCTURAL SLOT FILTER: exact synthetic case
    mini_facts = [
        (ENTITIES[0], "mayor",  ENTITIES[5],  "The mayor of Alton is Fjord."),
        (ENTITIES[1], "river",  ENTITIES[5],  "The river of Bexley is Fjord."),
        (ENTITIES[5], "capital", ENTITIES[6], "The capital of Fjord is Gulch."),
        (ENTITIES[7], "founder", ENTITIES[10], "The founder of Hara is Kelm."),
        (ENTITIES[8], "neighbor", ENTITIES[10], "The neighbor of Iona is Kelm."),
        (ENTITIES[15], "mayor", ENTITIES[16], "The mayor of Pome is Quill."),
    ]
    candidate_indices_mini = list(range(6))
    v3_selected, v3_diag = stage3_v3_structural_slot_filter(
        candidate_indices_mini, mini_facts,
        e0="Alton", r1="capital", r2="mayor",
        extracted_bridges=[5, 10], k_final=5)
    assert 0 in v3_selected, "v3: hop-1 fact 0 missing: %r" % v3_selected
    assert 2 in v3_selected, "v3: hop-2 fact 2 missing: %r" % v3_selected
    assert v3_diag["n_hop_1_cands"] == 1, "v3 hop1 count: %d" % v3_diag["n_hop_1_cands"]
    assert v3_diag["n_hop_2_cands"] == 1, "v3 hop2 count: %d" % v3_diag["n_hop_2_cands"]
    assert v3_diag["fallback_to_p1"] is False

    # 8. v3 fallback
    v3_fb, v3_fb_diag = stage3_v3_structural_slot_filter(
        candidate_indices_mini, mini_facts,
        e0="Xylo", r1="river", r2="founder",
        extracted_bridges=[5, 10], k_final=3)
    assert v3_fb_diag["fallback_to_p1"] is True
    assert len(v3_fb) == 3

    # 9. v1 MMR
    d = 32
    fake_emb = np.random.default_rng(0).standard_normal((100, d)).astype(np.float32)
    fake_emb = fake_emb / (np.linalg.norm(fake_emb, axis=1, keepdims=True) + 1e-8)
    q_e = fake_emb[3]
    candidates = [3, 17, 42, 55, 68, 71, 82, 90, 95, 99]
    selected = stage3_v1_rescore_mmr(candidates, q_e, fake_emb, k_final=5, mmr_lambda=0.4)
    assert len(selected) == 5

    # 10. v2 bridge extraction
    bridges = extract_bridge_candidates(candidate_indices_mini, mini_facts,
                                          "What is the capital of the mayor of Alton?",
                                          b_bridges=5, min_cooccur=2)
    assert 5 in bridges

    # 11. Verdict formulas
    def _mk_arm(o, e3b, sv1, sv2, mvc, vs12, rnd):
        return {
            "vacuous": False,
            "per_arm": {
                "ARM_ORACLE_COMPOSITION_SANITY": {"accuracy": o, "n_correct": 0, "n": 30},
                "ARM_EXP3_BASELINE_REPRODUCTION": {"accuracy": e3b, "n_correct": 0, "n": 30},
                "ARM_STAGE3_V1_QUERY_ONLY_RESCORE": {"accuracy": sv1, "n_correct": 0, "n": 30},
                "ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY": {"accuracy": sv2, "n_correct": 0, "n": 30},
                "ARM_MAIN_V3_CLEAN": {"accuracy": mvc, "n_correct": 0, "n": 30},
                "ARM_V3_STACKED_WITH_S1S2": {"accuracy": vs12, "n_correct": 0, "n": 30},
                "ARM_RANDOM_CANDIDATES_CONTROL": {"accuracy": rnd, "n_correct": 0, "n": 30},
            },
            "arms_differ_violations": [],
        }

    # 11a. HARD_PASS_FULL_ARC_CLOSURE (all seeds >= 0.60, cv < 0.10, main >= 0.90 * oracle)
    fake_hp = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.76, 0.51, 0.06),
                _mk_arm(0.82, 0.41, 0.011, 0.033, 0.78, 0.51, 0.06),
                _mk_arm(0.82, 0.41, 0.011, 0.033, 0.77, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_hp)
    assert v == "HARD_PASS" and "FULL_ARC_CLOSURE" in msg, "HP_FULL: %s | %s" % (v, msg)

    # 11b. HARD_PASS_MEASURED_MECHANISM (main above 0.60*oracle but cv too high)
    fake_measured = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.55, 0.51, 0.06),
                      _mk_arm(0.82, 0.41, 0.011, 0.033, 0.75, 0.51, 0.06),
                      _mk_arm(0.82, 0.41, 0.011, 0.033, 0.65, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_measured)
    assert v == "HARD_PASS" and "MEASURED_MECHANISM" in msg, (
        "HP_MEASURED: %s | %s" % (v, msg))

    # 11c. MIDDLE_BAND (main in [0.413, 0.49))
    fake_mid = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.45, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_mid)
    assert v == "MIDDLE_BAND", "MB: %s | %s" % (v, msg)

    # 11d. HARD_FAIL (main below baseline floor)
    fake_hf = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.10, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_hf)
    assert v == "HARD_FAIL" and "REGRESSED" in msg, "HF: %s | %s" % (v, msg)

    # 11e. HALT_ORACLE_DRIFT
    fake_drift = [_mk_arm(0.40, 0.41, 0.011, 0.033, 0.78, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_drift)
    assert v == "HARD_FAIL" and "ORACLE_DRIFT" in msg

    # 11f. Arc-closure gate: cv too high -> MEASURED_MECHANISM (not FULL_ARC_CLOSURE)
    fake_cv_break = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.60, 0.51, 0.06),
                      _mk_arm(0.82, 0.41, 0.011, 0.033, 0.90, 0.51, 0.06),
                      _mk_arm(0.82, 0.41, 0.011, 0.033, 0.80, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_cv_break)
    # mean 0.767 which is > 0.90 * 0.82 = 0.738, so this should demote to MEASURED
    # due to cv breach; failed_gates should include cv_lt_0.10
    assert v == "HARD_PASS" and "MEASURED_MECHANISM" in msg, (
        "cv-break: %s | %s" % (v, msg))
    assert "cv_lt_0.10" in msg, "cv gate should be flagged: %s" % msg

    # 11g. Arc-closure gate: one seed below 0.60 -> MEASURED_MECHANISM
    fake_min_break = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.55, 0.51, 0.06),
                       _mk_arm(0.82, 0.41, 0.011, 0.033, 0.78, 0.51, 0.06),
                       _mk_arm(0.82, 0.41, 0.011, 0.033, 0.80, 0.51, 0.06)]
    v, msg, _ = compute_verdict(fake_min_break)
    assert v == "HARD_PASS" and "MEASURED_MECHANISM" in msg
    assert "all_seeds_ge_0.60" in msg

    # 11h. Arc-closure gate: V3_STACKED_S1S2 drift too high -> MEASURED_MECHANISM
    fake_s1s2_break = [_mk_arm(0.82, 0.41, 0.011, 0.033, 0.76, 0.20, 0.06),
                        _mk_arm(0.82, 0.41, 0.011, 0.033, 0.78, 0.20, 0.06),
                        _mk_arm(0.82, 0.41, 0.011, 0.033, 0.77, 0.20, 0.06)]
    v, msg, _ = compute_verdict(fake_s1s2_break)
    assert v == "HARD_PASS" and "MEASURED_MECHANISM" in msg
    assert "v3_stacked_s1s2_drift" in msg

    print("[selftest] PASS: exp3e v3-clean arc-closure formula OK", flush=True)


# ---------- start marker + crash diag ----------
def _write_start_marker(out_dir, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------- main ----------
def main():
    print("[config] anchor=%s mode=%s n_dim=%d target_q=%d seeds=%s top_k=%d "
          "ppr_alpha=%.2f ppr_iters=%d union_max=%d "
          "hub_deg_thresh=%d hub_dampen=%.2f mmr_lambda_v1=%.2f k_final=%d "
          "b_bridges=%d w_query=%.1f w_aug=%.1f bridge_min_cooccur=%d" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_QUERIES_TARGET, SEEDS, TOP_K,
              PPR_ALPHA, PPR_ITERS, UNION_MAX,
              HUB_DEG_THRESH, HUB_DAMPEN_FACTOR, MMR_LAMBDA_V1, K_FINAL,
              B_BRIDGES, W_QUERY_ANCHOR, W_AUG, BRIDGE_MIN_COOCCUR), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=7 * len(SEEDS))

    print("[bge] loading encoder once (shared across seeds)...", flush=True)
    tb = time.perf_counter()
    _tok, _mdl, bge_encode_fn = bge_load_encoder()
    print("  bge_ready elapsed=%.1fs" % (time.perf_counter() - tb), flush=True)

    t_all = time.perf_counter()
    per_seed = []
    for seed in SEEDS:
        res = run_seed(seed, bge_encode_fn)
        per_seed.append(res)
        if res.get("vacuous", False):
            print("[seed=%d done] VACUOUS n_queries=%d" % (seed, res.get("n_queries", 0)),
                  flush=True)
        else:
            print("[seed=%d done] arms=%s" % (
                seed,
                {k: round(v["accuracy"], 3) for k, v in res["per_arm"].items()}),
                flush=True)

    verdict, verdict_msg, per_arm_mean = compute_verdict(per_seed)
    elapsed = time.perf_counter() - t_all

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_dim": N_DIM,
        "target_queries": N_QUERIES_TARGET,
        "n_seeds": len(SEEDS),
        "top_k": TOP_K,
        "ppr_alpha": PPR_ALPHA,
        "ppr_iters": PPR_ITERS,
        "ppr_top_k": PPR_TOP_K,
        "union_max": UNION_MAX,
        "hub_deg_thresh": HUB_DEG_THRESH,
        "hub_dampen_factor": HUB_DAMPEN_FACTOR,
        "mmr_lambda_v1": MMR_LAMBDA_V1,
        "k_final": K_FINAL,
        "b_bridges": B_BRIDGES,
        "w_query_anchor": W_QUERY_ANCHOR,
        "w_aug": W_AUG,
        "bridge_min_cooccur": BRIDGE_MIN_COOCCUR,
        "hub_indices": HUB_INDICES,
        "hub_over_sample": HUB_OVER_SAMPLE,
        "per_seed": per_seed,
        "per_arm_mean_accuracy": per_arm_mean,
        "expected_n_units": 7 * len([s for s in per_seed if not s.get("vacuous", False)]),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed
                              if not s.get("vacuous", False)),
        "cardinality_ok": (sum(len(s.get("per_arm", {})) for s in per_seed
                               if not s.get("vacuous", False))
                           == 7 * len([s for s in per_seed if not s.get("vacuous", False)])),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.025,
        "crlb_formula_reference": "sqrt(K_final/N_dim) = sqrt(5/8192) per Plate 1995",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "scope": "hub_concept_bridge_only",
        "oracle_precedent": 0.8222,
        "exp3_baseline_precedent": 0.4111,
        "stage3_v1_precedent": 0.0111,
        "stage3_v2_precedent": 0.0333,
        "v3_s1s2_precedent": 0.5111,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    print("[VERDICT] %s" % verdict_msg, flush=True)
    print("[metrics] written to %s (elapsed=%.1fs)" % (final, elapsed), flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out_dir, e)
        raise
