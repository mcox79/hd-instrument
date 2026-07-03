"""exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.

Experiment 3b: Layer 0.75 candidate-refinement primitive (3-stage stacked).

Question: does a 3-stage LLM-free candidate-refinement primitive placed
BETWEEN Layer 0.5 (PPR union ~30 chunks) and Layer 1 (FHRR composition needs
~5 clean chunks) close the interface gap from Exp 3 (MAIN=0.411 vs
ORACLE=0.822 on-disk, same hub-concept-bridge regime)?

Layer 0.75 stages (all substrate-native, LLM-free):
  Stage 1: node-specificity IDF seed re-weight  (HippoRAG NeurIPS 2024)
  Stage 2: hub-dampening inside PPR walk step   (CatRAG "Breaking Static Graph")
  Stage 3: query-conditioned rescore + MMR      (Carbonell & Goldstein 1998)

Composition primitive is IDENTICAL to Exp 3 ORACLE arm (FHRR bind/unbind chain).

Precedents (MEASURED@ off-disk):
  ORACLE (hub-bridge scope) = 0.8222  data/exp_substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_ORACLE_COMPOSITION_SANITY
  EXP3_MAIN (baseline for this cell) = 0.4111  same file:per_arm_mean_accuracy.ARM_PPR_UNION_HOP1_COMPOSITION_MAIN
  RANDOM = 0.0556  same file:per_arm_mean_accuracy.ARM_RANDOM_CANDIDATES_CONTROL

Arms (7):
  ARM_ORACLE_COMPOSITION_SANITY       - gt chunks -> composition; expect ~0.822
  ARM_EXP3_BASELINE_REPRODUCTION      - Exp 3 MAIN pipeline; expect ~0.411
  ARM_MAIN_LAYER075_STACKED           - all 3 stages -> K_FINAL=5 -> composition
  ARM_STAGE1_ONLY                     - stage1 only (rest = Exp 3 pipeline)
  ARM_STAGE2_ONLY                     - stage2 only
  ARM_STAGE3_ONLY                     - stage3 only
  ARM_RANDOM_CANDIDATES_CONTROL       - random 5 facts -> composition

Bands (auto-scaled to measured ORACLE):
  HARD_PASS: MAIN >= 0.90 * ORACLE  AND  MAIN > every stage-ablation by >= 0.02
  HARD_FAIL: MAIN <  0.60 * ORACLE
  MIDDLE:    0.60..0.90
  HALT_ORACLE_DRIFT:  |ORACLE - 0.8222| >= 0.10  (composition primitive changed)
  FLAG_BASELINE_DRIFT: |EXP3_BASELINE - 0.4111| >= 0.10 (soft)

Arc closure iff HP AND ORACLE-reproduces AND EXP3_BASELINE-reproduces AND
MAIN > single-stage ablation by >= 0.02.

ASCII-only. sequential-CPU. sharded storage.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm prediction-array sha256)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_floor_computed=0.035  THEORETICAL@sqrt(K_final/N)=sqrt(5/4096) Plate 1995
# - discriminator_reachability: True (HP target 0.74 >> CRLB 0.035)
# - baseline_in_band: 0.05 < EXP3_BASELINE < 0.95 expected (~0.41 per Exp 3)
# - discriminator survives scale: SMOKE regime IS test regime; matches Exp 3 config
# - HARD_PASS strictly above floor+5% via 0.90 * ORACLE scaling + ablation margin >= 0.02
# - HP_SCOPE: HP applies only to ARM_MAIN_LAYER075_STACKED; reproduction gates apply
#   to ORACLE arm (drift <= 0.10) and EXP3_BASELINE arm (drift <= 0.10)
# - cardinality_ok: EXPECTED_N_UNITS = 7 arms x 3 seeds = 21
# - per-unit failure-class instrumentation (specific Exception only)
# - calibration_check: default_ok_for_this_regime (chain-grade FHRR + Exp 2C PPR +
#   drill-A-informed hyperparams HUB_DEG_THRESH=8 HUB_DAMPEN=0.30 MMR_LAMBDA=0.4 K_FINAL=5)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - progress_logging: print_flush_true
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


ANCHOR_NAME = "substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03"
BI_MODEL = "BAAI/bge-small-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "

# Vocabulary (identical to Exp 3)
ENTITIES = [
    "Alton", "Bexley", "Coral", "Delft", "Erie", "Fjord", "Gulch", "Hara",
    "Iona", "Juno", "Kelm", "Loam", "Mesa", "Nord", "Osek", "Pome",
    "Quill", "Riva", "Solt", "Tern",
    "Umbra", "Vail", "Wren", "Xylo", "Yara", "Zorn", "Ashe", "Brix",
    "Corv", "Dune", "Ebon", "Frey", "Glim", "Holt", "Ivor", "Jarl",
    "Kord", "Larn", "Mote", "Nyx",
]  # 40 entities
RELATIONS = ["mayor", "capital", "river", "neighbor", "founder"]  # 5 relations
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
    N_QUERIES_TARGET = 50   # per seed; total ~150 across 3 seeds
    SEEDS = [11, 17, 23]

TOP_K = 5              # BGE hop-1 top-K facts
PPR_ALPHA = 0.15       # Exp 2C field-std
PPR_ITERS = 5
PPR_TOP_K = 5          # top-K entities after PPR
UNION_MAX = 30         # cap on union size (Exp 3 baseline uses 30)

# ---- Layer 0.75 hyperparameters (drill-A-informed; not tuned per-arm) ----
HUB_DEG_THRESH = 8         # nodes with degree > 8 = hubs (on 40-entity KG)
HUB_DAMPEN_FACTOR = 0.30   # scale outgoing edges of hubs by this
MMR_LAMBDA = 0.3           # coordinator 2026-07-03: use 0.3 (h2 envelope study; 0.5 was corpus-specific sweet spot, doesn't generalize)
K_FINAL = 5                # target candidate count after MMR


# ---------- FHRR primitives (identical to Exp 3) ----------
def rand_phase_hd(rng: np.random.Generator, n_dim: int) -> np.ndarray:
    """Random phase vector in [-pi, pi)."""
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


# ---------- corpus construction (identical to Exp 3) ----------
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


# ---------- KG + PPR primitives (Exp 2C / Exp 3) ----------
def build_entity_kg(facts: List[Tuple[str, str, str, str]],
                    n_entities: int) -> Tuple[sp.csr_matrix, Dict[int, Set[int]], np.ndarray]:
    """Build undirected column-stochastic adjacency + neighbor sets + degree vector."""
    rows: List[int] = []
    cols: List[int] = []
    vals: List[float] = []
    neighbors: Dict[int, Set[int]] = {i: set() for i in range(n_entities)}
    for (e, _r, v, _t) in facts:
        i = ENTITIES.index(e)
        j = ENTITIES.index(v)
        if i == j:
            continue
        rows.append(i); cols.append(j); vals.append(1.0)
        rows.append(j); cols.append(i); vals.append(1.0)
        neighbors[i].add(j)
        neighbors[j].add(i)
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


def ppr_iterate_sparse(A: sp.csr_matrix, seed_vec: np.ndarray, alpha: float,
                       iters: int) -> np.ndarray:
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


def seed_vec_from_indices(indices: List[int], n: int) -> np.ndarray:
    v = np.zeros(n, dtype=np.float64)
    for i in indices:
        v[i] += 1.0
    if v.sum() == 0:
        v = np.ones(n, dtype=np.float64)
    return v / v.sum()


# ---------- Layer 0.75 STAGE 1: node-specificity IDF seed re-weight ----------
def compute_passage_counts(facts: List[Tuple[str, str, str, str]],
                           n_entities: int) -> np.ndarray:
    """passage_count(node) = # facts in which node appears (as entity OR value)."""
    counts = np.zeros(n_entities, dtype=np.float64)
    for (e, _r, v, _t) in facts:
        counts[ENTITIES.index(e)] += 1.0
        counts[ENTITIES.index(v)] += 1.0
    return counts


def stage1_reweight_seed(seed_entities: Set[int], passage_counts: np.ndarray,
                          n_entities: int) -> np.ndarray:
    """Node-specificity IDF: seed weight[e] = 1 / passage_count(e). Renormalized."""
    v = np.zeros(n_entities, dtype=np.float64)
    for i in seed_entities:
        pc = passage_counts[i]
        # 1 / count; guard against zero (unreachable given i in seed_entities means node appears)
        v[i] = 1.0 / max(pc, 1.0)
    s = v.sum()
    if s <= 0:
        return seed_vec_from_indices(sorted(seed_entities), n_entities)
    return v / s


# ---------- Layer 0.75 STAGE 2: hub-dampening inside walk ----------
def stage2_hub_dampen_adjacency(A: sp.csr_matrix, degrees: np.ndarray,
                                 hub_deg_thresh: int,
                                 dampen_factor: float) -> sp.csr_matrix:
    """Scale outgoing edge weights (=columns of column-stochastic A) of high-degree
    nodes by dampen_factor. Preserves relative ordering of a hub's neighbors;
    total mass through hubs capped. PPR renormalizer absorbs mass leak (per
    ppr_iterate_sparse defensive-renorm)."""
    hub_indices = np.where(degrees > hub_deg_thresh)[0]
    if len(hub_indices) == 0:
        return A.copy()
    # Build diagonal scale: 1.0 for non-hubs, dampen_factor for hubs
    n = A.shape[0]
    scale = np.ones(n, dtype=np.float64)
    scale[hub_indices] = dampen_factor
    D = sp.diags(scale)
    # A @ D scales COLUMN j of A by scale[j]
    return (A @ D).tocsr()


# ---------- Layer 0.75 STAGE 3: query-conditioned rescore + MMR ----------
def stage3_rescore_mmr(candidate_indices: List[int],
                        query_bge: np.ndarray,
                        fact_bge: np.ndarray,
                        k_final: int,
                        mmr_lambda: float) -> List[int]:
    """For candidate facts (indices into fact_bge), compute cos(query, fact),
    then greedy MMR selection until k_final selected.

    MMR: c* = argmax_i [ lambda * s_i - (1 - lambda) * max_{j in selected} cos(fact_i, fact_j) ]
    """
    if not candidate_indices:
        return []
    cand_arr = np.array(candidate_indices, dtype=np.int64)
    cand_emb = fact_bge[cand_arr]                    # (K, D)
    q = query_bge                                     # (D,)
    # BGE embeddings are L2-normalized in bge_encode_all
    sims_q = cand_emb @ q                             # (K,)
    # Precompute inter-candidate similarity
    sims_cc = cand_emb @ cand_emb.T                   # (K, K)

    selected: List[int] = []       # local indices into cand_arr
    remaining = set(range(len(cand_arr)))
    while remaining and len(selected) < k_final:
        best_i = None
        best_score = -np.inf
        for i in remaining:
            if not selected:
                score = mmr_lambda * sims_q[i]
            else:
                red = max(sims_cc[i, j] for j in selected)
                score = mmr_lambda * sims_q[i] - (1.0 - mmr_lambda) * red
            if score > best_score:
                best_score = score
                best_i = i
        if best_i is None:
            break
        selected.append(best_i)
        remaining.discard(best_i)
    return [int(cand_arr[i]) for i in selected]


# ---------- composition primitive (IDENTICAL to Exp 3 ORACLE arm) ----------
def composition_primitive(q: Dict, corpus: Dict, retrieved_idx: List[int]) -> str:
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
    best_sim = -np.inf
    mid_idx = 0
    for k in range(retrieved_hds.shape[0]):
        candidate_mid = unbind_phase(q1, retrieved_hds[k])
        sims = phase_cos_batch(candidate_mid, V_cb)
        s = float(sims.max())
        if s > best_sim:
            best_sim = s
            mid_idx = int(sims.argmax())

    q2 = bind_phase(V_cb[mid_idx], R_cb[r1i])
    best_sim = -np.inf
    ans_idx = 0
    for k in range(retrieved_hds.shape[0]):
        candidate_ans = unbind_phase(q2, retrieved_hds[k])
        sims = phase_cos_batch(candidate_ans, V_cb)
        s = float(sims.max())
        if s > best_sim:
            best_sim = s
            ans_idx = int(sims.argmax())
    return ENTITIES[ans_idx]


# ---------- BGE retrieval ----------
def bge_encode_all(queries: List[Dict], fact_texts: List[str]
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Return (query_emb (Q,D), fact_emb (F,D)); both L2-normalized."""
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

    fact_e = encode(fact_texts)
    q_e = encode([Q_INSTR + q["text"] for q in queries])
    del mdl
    return q_e, fact_e


def bge_top_k(q_emb: np.ndarray, fact_emb: np.ndarray, top_k: int
              ) -> List[List[int]]:
    sims = q_emb @ fact_emb.T
    out = []
    for i in range(sims.shape[0]):
        order = np.argsort(sims[i])[::-1][:top_k].tolist()
        out.append(order)
    return out


# ---------- pipeline arms ----------
def ppr_pipeline_union(bge_ret: List[int], corpus: Dict, A: sp.csr_matrix,
                        n_entities: int, use_stage1: bool,
                        passage_counts: np.ndarray) -> List[int]:
    """Exp 3 MAIN pipeline: BGE hop-1 -> seed entities -> PPR -> top-K entities
    -> union of facts touching those entities, capped at UNION_MAX.
    If use_stage1: stage1_reweight_seed replaces uniform seed_vec_from_indices.
    """
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


def arm_oracle(q: Dict, corpus: Dict) -> str:
    return composition_primitive(q, corpus, q["gt_chunks"])


def arm_exp3_baseline(q: Dict, corpus: Dict, bge_ret: List[int],
                      A: sp.csr_matrix, n_entities: int,
                      passage_counts: np.ndarray) -> str:
    """Reproduce Exp 3 MAIN pipeline exactly (no Layer 0.75 stages)."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    return composition_primitive(q, corpus, union)


def arm_main_stacked(q: Dict, corpus: Dict, bge_ret: List[int],
                     A_dampened: sp.csr_matrix, n_entities: int,
                     passage_counts: np.ndarray,
                     query_bge: np.ndarray, fact_bge: np.ndarray) -> str:
    """All 3 stages stacked."""
    union = ppr_pipeline_union(bge_ret, corpus, A_dampened, n_entities,
                                use_stage1=True, passage_counts=passage_counts)
    filtered = stage3_rescore_mmr(union, query_bge, fact_bge,
                                    K_FINAL, MMR_LAMBDA)
    return composition_primitive(q, corpus, filtered)


def arm_stage1_only(q: Dict, corpus: Dict, bge_ret: List[int],
                    A: sp.csr_matrix, n_entities: int,
                    passage_counts: np.ndarray) -> str:
    """Stage 1 only: node-spec IDF seed reweight; normal A, no MMR filter."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=True, passage_counts=passage_counts)
    return composition_primitive(q, corpus, union)


def arm_stage2_only(q: Dict, corpus: Dict, bge_ret: List[int],
                    A_dampened: sp.csr_matrix, n_entities: int,
                    passage_counts: np.ndarray) -> str:
    """Stage 2 only: hub-dampened A; normal seed, no MMR filter."""
    union = ppr_pipeline_union(bge_ret, corpus, A_dampened, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    return composition_primitive(q, corpus, union)


def arm_stage3_only(q: Dict, corpus: Dict, bge_ret: List[int],
                    A: sp.csr_matrix, n_entities: int,
                    passage_counts: np.ndarray,
                    query_bge: np.ndarray, fact_bge: np.ndarray) -> str:
    """Stage 3 only: normal PPR union, MMR filter to K_FINAL."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    filtered = stage3_rescore_mmr(union, query_bge, fact_bge,
                                    K_FINAL, MMR_LAMBDA)
    return composition_primitive(q, corpus, filtered)


def arm_random_control(q: Dict, corpus: Dict, rng: np.random.Generator,
                        k: int = K_FINAL) -> str:
    n_facts = corpus["fact_hds"].shape[0]
    rand_idx = rng.choice(n_facts, size=k, replace=False).tolist()
    return composition_primitive(q, corpus, rand_idx)


# ---------- per-seed run ----------
def run_seed(seed: int) -> Dict:
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

    # Build entity KG
    print("[seed=%d] building entity KG..." % seed, flush=True)
    A, neighbors, degrees = build_entity_kg(corpus["facts"], len(ENTITIES))
    print("  KG built: n_edges_undirected=%d degrees_max=%d hubs>%d=%d" % (
        A.nnz // 2, int(degrees.max()), HUB_DEG_THRESH,
        int((degrees > HUB_DEG_THRESH).sum())), flush=True)

    # Stage 1 precompute: passage counts
    passage_counts = compute_passage_counts(corpus["facts"], len(ENTITIES))

    # Stage 2 precompute: hub-dampened adjacency (applied per hub-degree threshold)
    A_dampened = stage2_hub_dampen_adjacency(A, degrees, HUB_DEG_THRESH,
                                              HUB_DAMPEN_FACTOR)

    # BGE encoding (shared across baseline + stage3 + main)
    print("[seed=%d] running bge encoding + top_k=%d retrieval..." % (seed, TOP_K),
          flush=True)
    tr = time.perf_counter()
    q_emb, fact_emb = bge_encode_all(corpus["queries"], fact_texts)
    bge_retrieved = bge_top_k(q_emb, fact_emb, TOP_K)
    print("  bge_done elapsed=%.1fs" % (time.perf_counter() - tr), flush=True)

    rng = np.random.default_rng(seed + 1000)
    arm_names = [
        "ARM_ORACLE_COMPOSITION_SANITY",
        "ARM_EXP3_BASELINE_REPRODUCTION",
        "ARM_MAIN_LAYER075_STACKED",
        "ARM_STAGE1_ONLY",
        "ARM_STAGE2_ONLY",
        "ARM_STAGE3_ONLY",
        "ARM_RANDOM_CANDIDATES_CONTROL",
    ]
    preds_by_arm: Dict[str, List[str]] = {n: [] for n in arm_names}
    per_query_diag: List[Dict] = []

    n_entities = len(ENTITIES)
    for qi, q in enumerate(corpus["queries"]):
        bge_ret = bge_retrieved[qi]
        query_bge = q_emb[qi]
        p_oracle = arm_oracle(q, corpus)
        p_exp3_base = arm_exp3_baseline(q, corpus, bge_ret, A, n_entities,
                                          passage_counts)
        p_main = arm_main_stacked(q, corpus, bge_ret, A_dampened, n_entities,
                                    passage_counts, query_bge, fact_emb)
        p_s1 = arm_stage1_only(q, corpus, bge_ret, A, n_entities, passage_counts)
        p_s2 = arm_stage2_only(q, corpus, bge_ret, A_dampened, n_entities,
                                passage_counts)
        p_s3 = arm_stage3_only(q, corpus, bge_ret, A, n_entities, passage_counts,
                                query_bge, fact_emb)
        p_rand = arm_random_control(q, corpus, rng)

        preds_by_arm["ARM_ORACLE_COMPOSITION_SANITY"].append(p_oracle)
        preds_by_arm["ARM_EXP3_BASELINE_REPRODUCTION"].append(p_exp3_base)
        preds_by_arm["ARM_MAIN_LAYER075_STACKED"].append(p_main)
        preds_by_arm["ARM_STAGE1_ONLY"].append(p_s1)
        preds_by_arm["ARM_STAGE2_ONLY"].append(p_s2)
        preds_by_arm["ARM_STAGE3_ONLY"].append(p_s3)
        preds_by_arm["ARM_RANDOM_CANDIDATES_CONTROL"].append(p_rand)

        if qi < 10:
            # GT-coverage diagnostic (coordinator 2026-07-03 diagnostic ask):
            # is gt_chunk in pre-Stage-3 PPR union (main pipeline) vs post-Stage-3 filtered set?
            main_pre_pool = ppr_pipeline_union(bge_ret, corpus, A_dampened, n_entities,
                                                use_stage1=True, passage_counts=passage_counts)
            main_post = stage3_rescore_mmr(main_pre_pool, query_bge, fact_emb,
                                            K_FINAL, MMR_LAMBDA)
            s3only_pre_pool = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                                  use_stage1=False,
                                                  passage_counts=passage_counts)
            s3only_post = stage3_rescore_mmr(s3only_pre_pool, query_bge, fact_emb,
                                              K_FINAL, MMR_LAMBDA)
            gt_set = set(q["gt_chunks"])
            per_query_diag.append({
                "qi": qi, "text": q["text"], "e0": q["e0"], "mid": q["mid"],
                "answer": q["answer"], "gt_chunks": q["gt_chunks"],
                "bge_top5": bge_ret,
                "p_oracle": p_oracle, "p_exp3_base": p_exp3_base,
                "p_main": p_main, "p_s1": p_s1, "p_s2": p_s2,
                "p_s3": p_s3, "p_rand": p_rand,
                # GT-coverage diagnostic
                "gt_in_bge_top5": sorted(gt_set & set(bge_ret)),
                "main_pre_pool_size": len(main_pre_pool),
                "gt_in_main_pre_pool": sorted(gt_set & set(main_pre_pool)),
                "main_post_filtered": main_post,
                "gt_in_main_post": sorted(gt_set & set(main_post)),
                "s3only_pre_pool_size": len(s3only_pre_pool),
                "gt_in_s3only_pre_pool": sorted(gt_set & set(s3only_pre_pool)),
                "s3only_post_filtered": s3only_post,
                "gt_in_s3only_post": sorted(gt_set & set(s3only_post)),
            })
        if qi % 10 == 0:
            print("  q=%d/%d" % (qi, n_queries), flush=True)

    # Score
    truths = [q["answer"] for q in corpus["queries"]]
    per_arm = {}
    for name in arm_names:
        preds = preds_by_arm[name]
        correct = sum(1 for (p, t) in zip(preds, truths) if p == t)
        acc = correct / len(truths) if truths else 0.0
        per_arm[name] = {"accuracy": acc, "n_correct": correct, "n": len(truths)}

    # ARMS-MUST-DIFFER (META_RULE_AF)
    digests = {}
    for name in arm_names:
        blob = "|".join(preds_by_arm[name]).encode("utf-8")
        digests[name] = hashlib.sha256(blob).hexdigest()[:16]
    seen: Dict[str, str] = {}
    arms_differ_violations = []
    # Legit exempted pairs: e.g. RANDOM vs another arm might collide on very-hard
    # queries when both are chance-level. Declare exempted pairs post-hoc if the
    # collision is genuine chance-level convergence, not implementation bug.
    exempt_pairs: Set[Tuple[str, str]] = set()
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
        "hub_empirical_top3": corpus["hub_empirical_top3"],
        "hub_set": corpus["hub_set"],
        "degrees_max": int(degrees.max()),
        "n_hubs_by_degree": int((degrees > HUB_DEG_THRESH).sum()),
        "per_query_diag": per_query_diag,
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    active = [s for s in per_seed if not s.get("vacuous", False)]
    if not active:
        return ("HARD_FAIL",
                "HARD_FAIL_ALL_VACUOUS: no seeds produced >=10 hub-bridge queries.",
                {})

    arm_names = ["ARM_ORACLE_COMPOSITION_SANITY",
                 "ARM_EXP3_BASELINE_REPRODUCTION",
                 "ARM_MAIN_LAYER075_STACKED",
                 "ARM_STAGE1_ONLY",
                 "ARM_STAGE2_ONLY",
                 "ARM_STAGE3_ONLY",
                 "ARM_RANDOM_CANDIDATES_CONTROL"]
    per_arm_mean = {}
    for name in arm_names:
        accs = [s["per_arm"][name]["accuracy"] for s in active]
        per_arm_mean[name] = float(np.mean(accs))

    oracle = per_arm_mean["ARM_ORACLE_COMPOSITION_SANITY"]
    exp3_base = per_arm_mean["ARM_EXP3_BASELINE_REPRODUCTION"]
    main = per_arm_mean["ARM_MAIN_LAYER075_STACKED"]
    s1 = per_arm_mean["ARM_STAGE1_ONLY"]
    s2 = per_arm_mean["ARM_STAGE2_ONLY"]
    s3 = per_arm_mean["ARM_STAGE3_ONLY"]
    random_ctrl = per_arm_mean["ARM_RANDOM_CANDIDATES_CONTROL"]

    # Precedents (MEASURED@ Exp 3 metrics.json 2026-07-03)
    ORACLE_PRECEDENT = 0.8222
    EXP3_BASELINE_PRECEDENT = 0.4111

    oracle_drift = abs(oracle - ORACLE_PRECEDENT)
    exp3_base_drift = abs(exp3_base - EXP3_BASELINE_PRECEDENT)

    hp_target = 0.90 * oracle
    hf_target = 0.60 * oracle
    ablation_margin_min = 0.02

    # Cardinality
    expected_units = 7 * len(active)
    actual_units = sum(len(s["per_arm"]) for s in active)
    cardinality_ok = actual_units == expected_units

    arms_differ_ok = all(len(s["arms_differ_violations"]) == 0 for s in active)

    max_single_stage = max(s1, s2, s3)
    margin_vs_stages = main - max_single_stage

    summary = ("ORACLE=%.3f (drift=%.3f) EXP3_BASE=%.3f (drift=%.3f) "
                "MAIN=%.3f S1=%.3f S2=%.3f S3=%.3f RANDOM=%.3f | "
                "hp_target=%.3f hf_target=%.3f margin_vs_stages=%.3f (req>=%.2f) | "
                "cardinality_ok=%s arms_differ_ok=%s") % (
        oracle, oracle_drift, exp3_base, exp3_base_drift,
        main, s1, s2, s3, random_ctrl,
        hp_target, hf_target, margin_vs_stages, ablation_margin_min,
        cardinality_ok, arms_differ_ok)

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d got %d. %s" % (
                    expected_units, actual_units, summary), per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical. %s" % summary,
                per_arm_mean)

    # ORACLE reproduction gate (composition primitive sanity)
    if oracle_drift >= 0.10:
        return ("HARD_FAIL",
                "HALT_ORACLE_DRIFT: ORACLE arm = %.3f drifted %.3f from precedent %.3f. "
                "Composition primitive appears to have changed. Do NOT trust MAIN arm "
                "interpretation. %s" % (
                    oracle, oracle_drift, ORACLE_PRECEDENT, summary), per_arm_mean)

    baseline_note = ""
    if exp3_base_drift >= 0.10:
        baseline_note = (" FLAG_BASELINE_DRIFT: EXP3_BASELINE=%.3f (precedent=%.3f "
                        "drift=%.3f); soft flag." % (
                            exp3_base, EXP3_BASELINE_PRECEDENT, exp3_base_drift))

    # HP gate: MAIN >= hp_target AND MAIN > every single-stage by margin
    if main >= hp_target and margin_vs_stages >= ablation_margin_min:
        return ("HARD_PASS",
                "HARD_PASS_LAYER075_STACKED_CLOSES_ARC: MAIN=%.3f >= 0.90 * ORACLE=%.3f "
                "(hp_target=%.3f) AND MAIN exceeds every single-stage ablation by >= %.2f "
                "(max_single=%.3f, margin=%.3f). Retrieval-architecture arc CLOSES: "
                "Layer 0.5 KG-walk + Layer 0.75 3-stage refinement + Layer 1 FHRR "
                "composition pipeline validated within hub-concept-bridge scope. "
                "Encoder-swap DEFERRED validated. Next: 170K-atom Director-KB scale re-test. %s%s" % (
                    main, oracle, hp_target, ablation_margin_min,
                    max_single_stage, margin_vs_stages, summary, baseline_note),
                per_arm_mean)
    if main >= hp_target and margin_vs_stages < ablation_margin_min:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_MAIN_CLEARS_BUT_STACKING_UNPROVEN: MAIN=%.3f >= hp_target=%.3f "
                "BUT MAIN margin over single-stage ablations = %.3f < %.2f. A single stage "
                "may suffice; stacking-necessary claim unproven. Investigate best single "
                "stage before dispatching full. max_single=%.3f. %s%s" % (
                    main, hp_target, margin_vs_stages, ablation_margin_min,
                    max_single_stage, summary, baseline_note), per_arm_mean)
    if main < hf_target:
        return ("HARD_FAIL",
                "HARD_FAIL_LAYER075_NO_LIFT: MAIN=%.3f < 0.60 * ORACLE=%.3f "
                "(hf_target=%.3f). Layer 0.75 does NOT close the Exp 3 gap. "
                "Semantic contamination fix insufficient at this hyperparameter regime "
                "(HUB_DEG_THRESH=%d HUB_DAMPEN=%.2f MMR_LAMBDA=%.2f K_FINAL=%d). "
                "Route to Research for redesign. %s%s" % (
                    main, oracle, hf_target, HUB_DEG_THRESH, HUB_DAMPEN_FACTOR,
                    MMR_LAMBDA, K_FINAL, summary, baseline_note), per_arm_mean)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_LAYER075_PARTIAL_LIFT: MAIN=%.3f in [hf_target=%.3f, "
            "hp_target=%.3f]. Partial signal; Layer 0.75 helps but does not fully "
            "restore. Ablations: S1=%.3f S2=%.3f S3=%.3f. Route to Director for regime "
            "assessment. %s%s" % (
                main, hf_target, hp_target, s1, s2, s3, summary, baseline_note),
            per_arm_mean)


# ---------- selftest ----------
def selftest():
    """Formula selftest per PROT-022."""
    rng = np.random.default_rng(0)
    n = 512

    # 1. bind/unbind identity
    a = rand_phase_hd(rng, n)
    b = rand_phase_hd(rng, n)
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

    # 5. Composition primitive on ORACLE arm returns valid
    if len(corpus["queries"]) >= 1:
        p = arm_oracle(corpus["queries"][0], corpus)
        assert p in ENTITIES, "oracle arm returned invalid: %r" % p

    # 6. Entity KG + PPR
    A, neigh, degrees = build_entity_kg(corpus["facts"], len(ENTITIES))
    assert A.shape == (len(ENTITIES), len(ENTITIES))
    seed_v = seed_vec_from_indices([0], len(ENTITIES))
    ppr = ppr_iterate_sparse(A, seed_v, 0.15, 5)
    assert abs(ppr.sum() - 1.0) < 0.01, "PPR mass leaked: %.4f" % ppr.sum()

    # 7. Stage 1: node-specificity IDF sums to 1
    passage_counts = compute_passage_counts(corpus["facts"], len(ENTITIES))
    seed_ents = {0, 1, 5, 10}  # arbitrary
    s1_vec = stage1_reweight_seed(seed_ents, passage_counts, len(ENTITIES))
    assert abs(s1_vec.sum() - 1.0) < 1e-6, "Stage1 seed vec not normalized: %.6f" % s1_vec.sum()
    # High-passage-count nodes should have lower weight than low-passage-count nodes
    weights_present = [(i, s1_vec[i], passage_counts[i]) for i in seed_ents]
    weights_present.sort(key=lambda t: -t[2])  # by descending passage_count
    if len(weights_present) >= 2 and weights_present[0][2] > weights_present[-1][2]:
        # higher passage count = lower weight (IDF property)
        assert weights_present[0][1] <= weights_present[-1][1] + 1e-9, (
            "IDF property violated: high-passage node %s weight=%.4f > low-passage node %s weight=%.4f" % (
                weights_present[0][0], weights_present[0][1],
                weights_present[-1][0], weights_present[-1][1]))

    # 8. Stage 2: hub-dampened adjacency differs from A only in hub columns
    A_damp = stage2_hub_dampen_adjacency(A, degrees, HUB_DEG_THRESH, 0.30)
    hub_indices_local = np.where(degrees > HUB_DEG_THRESH)[0]
    A_dense = A.toarray()
    A_damp_dense = A_damp.toarray()
    non_hub_cols = [j for j in range(len(ENTITIES)) if j not in hub_indices_local]
    if non_hub_cols:
        diff_non_hub = np.abs(A_dense[:, non_hub_cols] - A_damp_dense[:, non_hub_cols]).max()
        assert diff_non_hub < 1e-9, "Stage2 changed non-hub columns: max_diff=%.6f" % diff_non_hub
    if len(hub_indices_local) > 0:
        # Hub columns must be scaled by ~0.30
        for j in hub_indices_local:
            orig_sum = A_dense[:, j].sum()
            damp_sum = A_damp_dense[:, j].sum()
            if orig_sum > 0:
                ratio = damp_sum / orig_sum
                assert abs(ratio - 0.30) < 1e-6, (
                    "Stage2 hub col %d scale ratio=%.4f expected 0.30" % (j, ratio))

    # 9. Stage 3: MMR selects K_FINAL from candidates, prefers high-query-sim
    n_cand = 10
    d = 32
    fact_emb = np.random.default_rng(0).standard_normal((100, d)).astype(np.float32)
    fact_emb = fact_emb / (np.linalg.norm(fact_emb, axis=1, keepdims=True) + 1e-8)
    q_emb = fact_emb[3]  # query = fact 3 itself
    candidates = [3, 17, 42, 55, 68, 71, 82, 90, 95, 99]
    selected = stage3_rescore_mmr(candidates, q_emb, fact_emb, k_final=5,
                                    mmr_lambda=0.4)
    assert len(selected) == 5, "MMR selected %d != 5" % len(selected)
    assert selected[0] == 3, "MMR first pick should be identical fact 3, got %d" % selected[0]

    # 10. Verdict formulas: HARD_PASS (MAIN >= 0.90*ORACLE and margin >= 0.02)
    fake_pass = [{
        "vacuous": False,
        "per_arm": {
            "ARM_ORACLE_COMPOSITION_SANITY": {"accuracy": 0.82, "n_correct": 41, "n": 50},
            "ARM_EXP3_BASELINE_REPRODUCTION": {"accuracy": 0.41, "n_correct": 20, "n": 50},
            "ARM_MAIN_LAYER075_STACKED": {"accuracy": 0.75, "n_correct": 37, "n": 50},
            "ARM_STAGE1_ONLY": {"accuracy": 0.55, "n_correct": 27, "n": 50},
            "ARM_STAGE2_ONLY": {"accuracy": 0.50, "n_correct": 25, "n": 50},
            "ARM_STAGE3_ONLY": {"accuracy": 0.60, "n_correct": 30, "n": 50},
            "ARM_RANDOM_CANDIDATES_CONTROL": {"accuracy": 0.05, "n_correct": 2, "n": 50},
        },
        "arms_differ_violations": [],
    }]
    v, msg, _ = compute_verdict(fake_pass)
    assert v == "HARD_PASS", "HP formula: %s | %s" % (v, msg)

    # 11. MIDDLE_BAND: MAIN clears hp_target but margin insufficient (single-stage matches)
    fake_middle = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_STAGE3_ONLY": {"accuracy": 0.74, "n_correct": 37, "n": 50}}}]
    v, msg, _ = compute_verdict(fake_middle)
    assert v == "MIDDLE_BAND" and "STACKING_UNPROVEN" in msg, "MB unproven: %s | %s" % (v, msg)

    # 12. HARD_FAIL (MAIN below hf_target)
    fake_fail = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_MAIN_LAYER075_STACKED": {"accuracy": 0.30, "n_correct": 15, "n": 50}}}]
    v, msg, _ = compute_verdict(fake_fail)
    assert v == "HARD_FAIL" and "NO_LIFT" in msg, "HF: %s | %s" % (v, msg)

    # 13. MIDDLE_BAND (partial lift)
    fake_mid = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_MAIN_LAYER075_STACKED": {"accuracy": 0.60, "n_correct": 30, "n": 50}}}]
    v, msg, _ = compute_verdict(fake_mid)
    assert v == "MIDDLE_BAND" and "PARTIAL_LIFT" in msg, "MB partial: %s | %s" % (v, msg)

    # 14. HALT_ORACLE_DRIFT
    fake_drift = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_ORACLE_COMPOSITION_SANITY": {"accuracy": 0.40, "n_correct": 20, "n": 50}}}]
    v, msg, _ = compute_verdict(fake_drift)
    assert v == "HARD_FAIL" and "ORACLE_DRIFT" in msg, "ORACLE_DRIFT: %s" % v

    print("[selftest] PASS: exp3b Layer 0.75 candidate-refinement primitives OK", flush=True)


# ---------- start marker + crash diag ----------
def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
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


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
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
          "hub_deg_thresh=%d hub_dampen=%.2f mmr_lambda=%.2f k_final=%d" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_QUERIES_TARGET, SEEDS, TOP_K,
              PPR_ALPHA, PPR_ITERS, UNION_MAX,
              HUB_DEG_THRESH, HUB_DAMPEN_FACTOR, MMR_LAMBDA, K_FINAL), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=7 * len(SEEDS))

    t_all = time.perf_counter()
    per_seed = []
    for seed in SEEDS:
        res = run_seed(seed)
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
        "mmr_lambda": MMR_LAMBDA,
        "k_final": K_FINAL,
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
        "crlb_floor_computed": 0.035,
        "crlb_formula_reference": "sqrt(K_final/N_dim) = sqrt(5/4096) per Plate 1995",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "scope": "hub_concept_bridge_only",
        "oracle_precedent": 0.8222,
        "exp3_baseline_precedent": 0.4111,
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
