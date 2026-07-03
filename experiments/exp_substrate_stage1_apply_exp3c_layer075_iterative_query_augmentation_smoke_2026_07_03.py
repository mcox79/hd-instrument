"""exp_substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03.

Experiment 3c: Layer 0.75 Stage 3 REDESIGN via iterative query-augmentation.

Question: does Stage 3 v2 (bridge-entity discovery from candidate pool + per-bridge
BGE-augmented query + aggregated rescore) close the interface gap that Exp 3B Stage 3 v1
(query-only cosine + MMR) architecturally could not close because bridge entities are by
definition not in the user query text for a multi-hop question?

Stages 1 + 2 UNCHANGED from Exp 3B (verified null-effect but not net-negative).
Only Stage 3 is replaced with the v2 iterative-query-augmentation primitive.

Precedents (MEASURED@ off-disk Exp 3B metrics.json 2026-07-03):
  ORACLE (hub-bridge scope)             = 0.8533
  EXP3_BASELINE (Exp 3 MAIN pipeline)   = 0.4133
  MAIN_LAYER075_STACKED (Exp 3B v1)     = 0.0267  (HF; v1 query-only Stage 3 was destructive)
  STAGE3_ONLY (Exp 3B v1)               = 0.0133  (HF; v1 query-only Stage 3 in isolation)
  STAGE1_ONLY                           = 0.3933
  STAGE2_ONLY                           = 0.4067
  RANDOM                                = 0.0467

Arms (8) - 7 from Exp 3B for direct comparison + 1 new to isolate Stage 3 v2:
  ARM_ORACLE_COMPOSITION_SANITY               (target ~0.85 drift <= 0.10)
  ARM_EXP3_BASELINE_REPRODUCTION              (target ~0.41 drift <= 0.10)
  ARM_MAIN_LAYER075_STACKED_V2                (S1 + S2 + S3_v2; discriminator)
  ARM_STAGE1_ONLY                             (S1 only; ~0.39 expected)
  ARM_STAGE2_ONLY                             (S2 only; ~0.41 expected)
  ARM_STAGE3_V1_QUERY_ONLY_RESCORE            (v1 mechanism; Fix#28 HF reproduction gate ~0.01)
  ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY      (v2 in isolation)
  ARM_RANDOM_CANDIDATES_CONTROL               (chance ~0.05)

Bands (dual HP bar per Director spawn):
  HARD_PASS_FULL_CLOSURE:      MAIN_V2 >= 0.90 * ORACLE (~0.77)
  HARD_PASS_INTERFACE_POSITIVE MAIN_V2 >= 0.413 AND STAGE3_V2_ONLY > 0.413
  MIDDLE_BAND:                 0.413 <= MAIN_V2 < 0.77 AND not interface-positive
  HARD_FAIL:                   MAIN_V2 < 0.413 AND STAGE3_V2_ONLY < 0.20
                               (escalate to path (a) BridgeRAG tripartite)
  HALT_ORACLE_DRIFT:           |ORACLE - 0.8533| >= 0.10  (composition primitive changed)
  FLAG_BASELINE_DRIFT:         |EXP3_BASELINE - 0.4133| >= 0.10 (soft)
  FLAG_V1_HF_DRIFT:            |STAGE3_V1 - 0.0133| >= 0.10 (soft; Fix#28 confidence check)

ASCII-only. sequential-CPU. sharded storage.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm prediction-array sha256)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_floor_computed=0.035  THEORETICAL@sqrt(K_final/N)=sqrt(5/4096) Plate 1995
# - discriminator_reachability: True (HP target 0.77 >> CRLB 0.035; interface-positive 0.413 feasible)
# - baseline_in_band: 0.05 < EXP3_BASELINE < 0.95 expected (~0.41 per Exp 3B)
# - discriminator survives scale: SMOKE regime IS test regime; matches Exp 3B config
# - HARD_PASS strictly above floor: 0.90 * ORACLE scaling + non-destructive interface gate
# - HP_SCOPE: HP applies only to ARM_MAIN_LAYER075_STACKED_V2; reproduction gates apply
#   to ORACLE (drift <= 0.10), EXP3_BASELINE (drift <= 0.10), STAGE3_V1 (drift <= 0.10)
# - cardinality_ok: EXPECTED_N_UNITS = 8 arms x 3 seeds = 24
# - per-unit failure-class instrumentation (specific Exception only)
# - calibration_check: default_ok_for_this_regime (Exp 3B hyperparams unchanged;
#   new v2 hyperparams: B_BRIDGES=5, W_QUERY_ANCHOR=1.0, W_AUG=1.0)
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


ANCHOR_NAME = "substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03"
BI_MODEL = "BAAI/bge-small-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "

# Vocabulary (identical to Exp 3B)
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

# ---- Layer 0.75 hyperparameters (unchanged from Exp 3B) ----
HUB_DEG_THRESH = 8         # nodes with degree > 8 = hubs (on 40-entity KG)
HUB_DAMPEN_FACTOR = 0.30   # scale outgoing edges of hubs by this
K_FINAL = 5                # target candidate count after Stage 3

# ---- Layer 0.75 v1 (query-only rescore) hyperparameters -- for REPRODUCTION arm ----
MMR_LAMBDA_V1 = 0.3        # Exp 3B setting

# ---- Layer 0.75 v2 (iterative query-augmentation) hyperparameters -- NEW ----
B_BRIDGES = 5              # top-B bridge candidates by pool-frequency
W_QUERY_ANCHOR = 1.0       # weight on cos(Q_0, fact)
W_AUG = 1.0                # weight on max-over-bridges cos(Q_aug, fact)
BRIDGE_MIN_COOCCUR = 2     # entity must appear in >= this many distinct facts in P_1


# ---------- FHRR primitives (identical to Exp 3B) ----------
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


# ---------- corpus construction (identical to Exp 3B) ----------
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


# ---------- KG + PPR primitives (Exp 2C / Exp 3 / Exp 3B; unchanged) ----------
def build_entity_kg(facts: List[Tuple[str, str, str, str]],
                    n_entities: int) -> Tuple[sp.csr_matrix, Dict[int, Set[int]], np.ndarray]:
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


# ---------- Stage 1: node-specificity IDF seed re-weight (unchanged from 3B) ----------
def compute_passage_counts(facts: List[Tuple[str, str, str, str]],
                           n_entities: int) -> np.ndarray:
    counts = np.zeros(n_entities, dtype=np.float64)
    for (e, _r, v, _t) in facts:
        counts[ENTITIES.index(e)] += 1.0
        counts[ENTITIES.index(v)] += 1.0
    return counts


def stage1_reweight_seed(seed_entities: Set[int], passage_counts: np.ndarray,
                          n_entities: int) -> np.ndarray:
    v = np.zeros(n_entities, dtype=np.float64)
    for i in seed_entities:
        pc = passage_counts[i]
        v[i] = 1.0 / max(pc, 1.0)
    s = v.sum()
    if s <= 0:
        return seed_vec_from_indices(sorted(seed_entities), n_entities)
    return v / s


# ---------- Stage 2: hub-dampening (unchanged from 3B) ----------
def stage2_hub_dampen_adjacency(A: sp.csr_matrix, degrees: np.ndarray,
                                 hub_deg_thresh: int,
                                 dampen_factor: float) -> sp.csr_matrix:
    hub_indices = np.where(degrees > hub_deg_thresh)[0]
    if len(hub_indices) == 0:
        return A.copy()
    n = A.shape[0]
    scale = np.ones(n, dtype=np.float64)
    scale[hub_indices] = dampen_factor
    D = sp.diags(scale)
    return (A @ D).tocsr()


# ---------- Stage 3 v1: query-only cosine rescore + MMR (Exp 3B; kept for REPRODUCTION arm) ----------
def stage3_v1_rescore_mmr(candidate_indices: List[int],
                           query_bge: np.ndarray,
                           fact_bge: np.ndarray,
                           k_final: int,
                           mmr_lambda: float) -> List[int]:
    """Exp 3B Stage 3 v1 (query-only cosine + MMR). Reproduced for HF gate."""
    if not candidate_indices:
        return []
    cand_arr = np.array(candidate_indices, dtype=np.int64)
    cand_emb = fact_bge[cand_arr]
    q = query_bge
    sims_q = cand_emb @ q
    sims_cc = cand_emb @ cand_emb.T

    selected: List[int] = []
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


# ---------- Stage 3 v2: iterative query-augmentation (NEW) ----------
def extract_bridge_candidates(candidate_indices: List[int],
                               facts: List[Tuple[str, str, str, str]],
                               query_text: str,
                               b_bridges: int,
                               min_cooccur: int) -> List[int]:
    """From candidate_indices (P_1), extract entity indices that appear in >= min_cooccur
    distinct facts in the pool, sorted by pool-frequency descending. Drop entities
    whose name already appears in the query text (they'd be trivial augmentations)."""
    entity_to_facts: Dict[int, Set[int]] = {}
    for fi in candidate_indices:
        e, _r, v, _t = facts[fi]
        ei = ENTITIES.index(e)
        vi = ENTITIES.index(v)
        entity_to_facts.setdefault(ei, set()).add(fi)
        entity_to_facts.setdefault(vi, set()).add(fi)
    bridge_pool = [(ei, len(fs)) for ei, fs in entity_to_facts.items()
                   if len(fs) >= min_cooccur]
    q_lower = query_text.lower()
    bridge_pool = [(ei, cnt) for (ei, cnt) in bridge_pool
                   if ENTITIES[ei].lower() not in q_lower]
    bridge_pool.sort(key=lambda t: -t[1])
    return [ei for (ei, _c) in bridge_pool[:b_bridges]]


def stage3_v2_iterative_query_augmentation(candidate_indices: List[int],
                                            query_text: str,
                                            query_bge: np.ndarray,
                                            fact_bge: np.ndarray,
                                            facts: List[Tuple[str, str, str, str]],
                                            k_final: int,
                                            b_bridges: int,
                                            w_query: float,
                                            w_aug: float,
                                            bridge_min_cooccur: int,
                                            bge_encode_fn) -> Tuple[List[int], List[int]]:
    """Stage 3 v2: iterative query-augmentation via bridge-entity discovery.

    Steps:
      A. Extract bridge candidates from candidate_indices (co-occurrence >= min).
      B. For each bridge b_i, form Q_i = query_text + " " + ENTITIES[b_i]; BGE-encode.
      C. Compute cos(Q_0, fact_j) and max_i cos(Q_i, fact_j) for j in candidate_indices.
      D. Aggregated score = w_query * cos_q0 + w_aug * max_i cos_aug_i
      E. Return top k_final by aggregated score. Also return the bridge indices for diag.

    Fallback: if 0 bridge candidates, reduce to query-only top-K over P_1 (no MMR).
    """
    if not candidate_indices:
        return [], []
    cand_arr = np.array(candidate_indices, dtype=np.int64)
    cand_emb = fact_bge[cand_arr]                       # (K_p1, D)
    cos_q0 = cand_emb @ query_bge                       # (K_p1,)

    bridges = extract_bridge_candidates(candidate_indices, facts, query_text,
                                         b_bridges, bridge_min_cooccur)

    if not bridges:
        # Fallback: query-only top-K (no MMR; simpler than v1)
        scores = cos_q0
    else:
        aug_texts = [query_text + " " + ENTITIES[b] for b in bridges]
        aug_emb = bge_encode_fn(aug_texts)              # (B, D)
        # (B, D) @ (D, K_p1) = (B, K_p1)
        cos_aug = aug_emb @ cand_emb.T
        aug_agg = cos_aug.max(axis=0)                    # (K_p1,)
        scores = w_query * cos_q0 + w_aug * aug_agg

    order = np.argsort(scores)[::-1][:k_final]
    selected = [int(cand_arr[i]) for i in order]
    return selected, bridges


# ---------- composition primitive (IDENTICAL to Exp 3B ORACLE) ----------
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


# ---------- BGE retrieval + on-demand augmented-query encoder ----------
def bge_load_encoder():
    """Load BGE model once; return (tokenizer, model, encode_fn)."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    DEV = torch.device("cpu")
    tok = AutoTokenizer.from_pretrained(BI_MODEL)
    mdl = AutoModel.from_pretrained(BI_MODEL).to(DEV).eval()

    def encode(texts: List[str]) -> np.ndarray:
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
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    return composition_primitive(q, corpus, union)


def arm_main_stacked_v2(q: Dict, corpus: Dict, bge_ret: List[int],
                         A_dampened: sp.csr_matrix, n_entities: int,
                         passage_counts: np.ndarray,
                         query_bge: np.ndarray, fact_bge: np.ndarray,
                         bge_encode_fn) -> Tuple[str, List[int], List[int]]:
    """All 3 v2 stages stacked. Returns (pred, p1_pool, bridges)."""
    p1_pool = ppr_pipeline_union(bge_ret, corpus, A_dampened, n_entities,
                                   use_stage1=True, passage_counts=passage_counts)
    filtered, bridges = stage3_v2_iterative_query_augmentation(
        p1_pool, q["text"], query_bge, fact_bge, corpus["facts"],
        K_FINAL, B_BRIDGES, W_QUERY_ANCHOR, W_AUG, BRIDGE_MIN_COOCCUR,
        bge_encode_fn)
    return composition_primitive(q, corpus, filtered), p1_pool, bridges


def arm_stage1_only(q: Dict, corpus: Dict, bge_ret: List[int],
                    A: sp.csr_matrix, n_entities: int,
                    passage_counts: np.ndarray) -> str:
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=True, passage_counts=passage_counts)
    return composition_primitive(q, corpus, union)


def arm_stage2_only(q: Dict, corpus: Dict, bge_ret: List[int],
                    A_dampened: sp.csr_matrix, n_entities: int,
                    passage_counts: np.ndarray) -> str:
    union = ppr_pipeline_union(bge_ret, corpus, A_dampened, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    return composition_primitive(q, corpus, union)


def arm_stage3_v1_only(q: Dict, corpus: Dict, bge_ret: List[int],
                       A: sp.csr_matrix, n_entities: int,
                       passage_counts: np.ndarray,
                       query_bge: np.ndarray, fact_bge: np.ndarray) -> str:
    """Exp 3B Stage 3 v1 (query-only rescore + MMR) -- Fix#28 HF reproduction gate."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    filtered = stage3_v1_rescore_mmr(union, query_bge, fact_bge,
                                       K_FINAL, MMR_LAMBDA_V1)
    return composition_primitive(q, corpus, filtered)


def arm_stage3_v2_only(q: Dict, corpus: Dict, bge_ret: List[int],
                        A: sp.csr_matrix, n_entities: int,
                        passage_counts: np.ndarray,
                        query_bge: np.ndarray, fact_bge: np.ndarray,
                        bge_encode_fn) -> Tuple[str, List[int], List[int]]:
    """Stage 3 v2 isolated: normal PPR union -> v2 aug -> composition."""
    union = ppr_pipeline_union(bge_ret, corpus, A, n_entities,
                                use_stage1=False, passage_counts=passage_counts)
    filtered, bridges = stage3_v2_iterative_query_augmentation(
        union, q["text"], query_bge, fact_bge, corpus["facts"],
        K_FINAL, B_BRIDGES, W_QUERY_ANCHOR, W_AUG, BRIDGE_MIN_COOCCUR,
        bge_encode_fn)
    return composition_primitive(q, corpus, filtered), union, bridges


def arm_random_control(q: Dict, corpus: Dict, rng: np.random.Generator,
                        k: int = K_FINAL) -> str:
    n_facts = corpus["fact_hds"].shape[0]
    rand_idx = rng.choice(n_facts, size=k, replace=False).tolist()
    return composition_primitive(q, corpus, rand_idx)


# ---------- per-seed run ----------
def run_seed(seed: int, bge_encode_fn) -> Dict:
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
    print("  KG built: n_edges_undirected=%d degrees_max=%d hubs>%d=%d" % (
        A.nnz // 2, int(degrees.max()), HUB_DEG_THRESH,
        int((degrees > HUB_DEG_THRESH).sum())), flush=True)

    passage_counts = compute_passage_counts(corpus["facts"], len(ENTITIES))
    A_dampened = stage2_hub_dampen_adjacency(A, degrees, HUB_DEG_THRESH,
                                              HUB_DAMPEN_FACTOR)

    print("[seed=%d] running bge encoding + top_k=%d retrieval..." % (seed, TOP_K),
          flush=True)
    tr = time.perf_counter()
    q_emb = bge_encode_fn([Q_INSTR + q["text"] for q in corpus["queries"]])
    fact_emb = bge_encode_fn(fact_texts)
    bge_retrieved = bge_top_k(q_emb, fact_emb, TOP_K)
    print("  bge_done elapsed=%.1fs" % (time.perf_counter() - tr), flush=True)

    rng = np.random.default_rng(seed + 1000)
    arm_names = [
        "ARM_ORACLE_COMPOSITION_SANITY",
        "ARM_EXP3_BASELINE_REPRODUCTION",
        "ARM_MAIN_LAYER075_STACKED_V2",
        "ARM_STAGE1_ONLY",
        "ARM_STAGE2_ONLY",
        "ARM_STAGE3_V1_QUERY_ONLY_RESCORE",
        "ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY",
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
        p_main, main_p1_pool, main_bridges = arm_main_stacked_v2(
            q, corpus, bge_ret, A_dampened, n_entities,
            passage_counts, query_bge, fact_emb, bge_encode_fn)
        p_s1 = arm_stage1_only(q, corpus, bge_ret, A, n_entities, passage_counts)
        p_s2 = arm_stage2_only(q, corpus, bge_ret, A_dampened, n_entities,
                                passage_counts)
        p_s3v1 = arm_stage3_v1_only(q, corpus, bge_ret, A, n_entities,
                                     passage_counts, query_bge, fact_emb)
        p_s3v2, s3v2_p1_pool, s3v2_bridges = arm_stage3_v2_only(
            q, corpus, bge_ret, A, n_entities, passage_counts,
            query_bge, fact_emb, bge_encode_fn)
        p_rand = arm_random_control(q, corpus, rng)

        preds_by_arm["ARM_ORACLE_COMPOSITION_SANITY"].append(p_oracle)
        preds_by_arm["ARM_EXP3_BASELINE_REPRODUCTION"].append(p_exp3_base)
        preds_by_arm["ARM_MAIN_LAYER075_STACKED_V2"].append(p_main)
        preds_by_arm["ARM_STAGE1_ONLY"].append(p_s1)
        preds_by_arm["ARM_STAGE2_ONLY"].append(p_s2)
        preds_by_arm["ARM_STAGE3_V1_QUERY_ONLY_RESCORE"].append(p_s3v1)
        preds_by_arm["ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY"].append(p_s3v2)
        preds_by_arm["ARM_RANDOM_CANDIDATES_CONTROL"].append(p_rand)

        if qi < 10:
            # GT-coverage diagnostic: track GT chunk survival through Stage 3 v2
            # for both MAIN (Stage1+Stage2 pool) and STAGE3_V2_ONLY (normal pool).
            main_post, main_bridges_d = stage3_v2_iterative_query_augmentation(
                main_p1_pool, q["text"], query_bge, fact_emb, corpus["facts"],
                K_FINAL, B_BRIDGES, W_QUERY_ANCHOR, W_AUG, BRIDGE_MIN_COOCCUR,
                bge_encode_fn)
            s3v2_post, s3v2_bridges_d = stage3_v2_iterative_query_augmentation(
                s3v2_p1_pool, q["text"], query_bge, fact_emb, corpus["facts"],
                K_FINAL, B_BRIDGES, W_QUERY_ANCHOR, W_AUG, BRIDGE_MIN_COOCCUR,
                bge_encode_fn)
            gt_set = set(q["gt_chunks"])
            mid_idx = ENTITIES.index(q["mid"])
            per_query_diag.append({
                "qi": qi, "text": q["text"], "e0": q["e0"], "mid": q["mid"],
                "mid_idx": mid_idx, "answer": q["answer"],
                "gt_chunks": q["gt_chunks"], "bge_top5": bge_ret,
                "p_oracle": p_oracle, "p_exp3_base": p_exp3_base,
                "p_main_v2": p_main, "p_s1": p_s1, "p_s2": p_s2,
                "p_s3v1": p_s3v1, "p_s3v2": p_s3v2, "p_rand": p_rand,
                # GT-coverage: MAIN pipeline (Stage 1 + Stage 2 pool)
                "main_p1_pool_size": len(main_p1_pool),
                "gt_in_main_p1_pool": sorted(gt_set & set(main_p1_pool)),
                "main_bridges": [ENTITIES[b] for b in main_bridges_d],
                "mid_in_main_bridges": mid_idx in main_bridges_d,
                "main_post_filtered": main_post,
                "gt_in_main_post": sorted(gt_set & set(main_post)),
                # GT-coverage: STAGE3_V2_ONLY pipeline (normal pool)
                "s3v2only_p1_pool_size": len(s3v2_p1_pool),
                "gt_in_s3v2only_p1_pool": sorted(gt_set & set(s3v2_p1_pool)),
                "s3v2only_bridges": [ENTITIES[b] for b in s3v2_bridges_d],
                "mid_in_s3v2only_bridges": mid_idx in s3v2_bridges_d,
                "s3v2only_post_filtered": s3v2_post,
                "gt_in_s3v2only_post": sorted(gt_set & set(s3v2_post)),
            })
        if qi % 10 == 0:
            print("  q=%d/%d" % (qi, n_queries), flush=True)

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
    exempt_pairs: Set[Tuple[str, str]] = set()
    for name, dig in digests.items():
        if dig in seen:
            other = seen[dig]
            pair = tuple(sorted([other, name]))
            if pair not in exempt_pairs:
                arms_differ_violations.append((other, name, dig))
        else:
            seen[dig] = name

    # GT-coverage summary (first-10-queries diagnostic aggregate)
    gt_cov_main_pre = 0
    gt_cov_main_post = 0
    gt_cov_s3v2_pre = 0
    gt_cov_s3v2_post = 0
    n_diag = len(per_query_diag)
    n_bridge_captured_mid_main = 0
    n_bridge_captured_mid_s3v2 = 0
    for d in per_query_diag:
        gt_cov_main_pre += len(d["gt_in_main_p1_pool"])
        gt_cov_main_post += len(d["gt_in_main_post"])
        gt_cov_s3v2_pre += len(d["gt_in_s3v2only_p1_pool"])
        gt_cov_s3v2_post += len(d["gt_in_s3v2only_post"])
        if d["mid_in_main_bridges"]:
            n_bridge_captured_mid_main += 1
        if d["mid_in_s3v2only_bridges"]:
            n_bridge_captured_mid_s3v2 += 1

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
        "gt_coverage_summary": {
            "n_diag_queries": n_diag,
            "gt_slots_diag": 2 * n_diag,
            "main_gt_pre_stage3": gt_cov_main_pre,
            "main_gt_post_stage3": gt_cov_main_post,
            "s3v2only_gt_pre_stage3": gt_cov_s3v2_pre,
            "s3v2only_gt_post_stage3": gt_cov_s3v2_post,
            "main_bridge_captured_mid": n_bridge_captured_mid_main,
            "s3v2only_bridge_captured_mid": n_bridge_captured_mid_s3v2,
        },
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
                 "ARM_MAIN_LAYER075_STACKED_V2",
                 "ARM_STAGE1_ONLY",
                 "ARM_STAGE2_ONLY",
                 "ARM_STAGE3_V1_QUERY_ONLY_RESCORE",
                 "ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY",
                 "ARM_RANDOM_CANDIDATES_CONTROL"]
    per_arm_mean = {}
    for name in arm_names:
        accs = [s["per_arm"][name]["accuracy"] for s in active]
        per_arm_mean[name] = float(np.mean(accs))

    oracle = per_arm_mean["ARM_ORACLE_COMPOSITION_SANITY"]
    exp3_base = per_arm_mean["ARM_EXP3_BASELINE_REPRODUCTION"]
    main_v2 = per_arm_mean["ARM_MAIN_LAYER075_STACKED_V2"]
    s1 = per_arm_mean["ARM_STAGE1_ONLY"]
    s2 = per_arm_mean["ARM_STAGE2_ONLY"]
    s3v1 = per_arm_mean["ARM_STAGE3_V1_QUERY_ONLY_RESCORE"]
    s3v2 = per_arm_mean["ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY"]
    random_ctrl = per_arm_mean["ARM_RANDOM_CANDIDATES_CONTROL"]

    # Precedents from Exp 3B on-disk
    ORACLE_PRECEDENT = 0.8533
    EXP3_BASELINE_PRECEDENT = 0.4133
    STAGE3_V1_PRECEDENT = 0.0133

    oracle_drift = abs(oracle - ORACLE_PRECEDENT)
    exp3_base_drift = abs(exp3_base - EXP3_BASELINE_PRECEDENT)
    s3v1_drift = abs(s3v1 - STAGE3_V1_PRECEDENT)

    hp_full_target = 0.90 * oracle
    hp_interface_floor = EXP3_BASELINE_PRECEDENT   # 0.4133
    hf_main_floor = EXP3_BASELINE_PRECEDENT        # main below Exp3 baseline is HF-eligible
    hf_s3v2_floor = 0.20

    # Cardinality
    expected_units = 8 * len(active)
    actual_units = sum(len(s["per_arm"]) for s in active)
    cardinality_ok = actual_units == expected_units
    arms_differ_ok = all(len(s["arms_differ_violations"]) == 0 for s in active)

    summary = ("ORACLE=%.3f (drift=%.3f) EXP3_BASE=%.3f (drift=%.3f) "
                "S3V1=%.3f (drift=%.3f vs %.3f) MAIN_V2=%.3f "
                "S1=%.3f S2=%.3f S3V2=%.3f RANDOM=%.3f | "
                "hp_full=%.3f hp_interface=%.3f hf_main_floor=%.3f hf_s3v2_floor=%.3f | "
                "cardinality_ok=%s arms_differ_ok=%s") % (
        oracle, oracle_drift, exp3_base, exp3_base_drift,
        s3v1, s3v1_drift, STAGE3_V1_PRECEDENT,
        main_v2, s1, s2, s3v2, random_ctrl,
        hp_full_target, hp_interface_floor, hf_main_floor, hf_s3v2_floor,
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
                "Composition primitive appears to have changed. Do NOT trust MAIN_V2 "
                "interpretation. %s" % (
                    oracle, oracle_drift, ORACLE_PRECEDENT, summary), per_arm_mean)

    soft_flags = []
    if exp3_base_drift >= 0.10:
        soft_flags.append("FLAG_BASELINE_DRIFT: EXP3_BASELINE=%.3f (precedent=%.3f drift=%.3f)" % (
            exp3_base, EXP3_BASELINE_PRECEDENT, exp3_base_drift))
    if s3v1_drift >= 0.10:
        soft_flags.append("FLAG_V1_HF_DRIFT: STAGE3_V1=%.3f (precedent=%.3f drift=%.3f); "
                          "Fix#28 confidence-check reproduction imperfect" % (
                              s3v1, STAGE3_V1_PRECEDENT, s3v1_drift))
    soft_note = (" | " + "; ".join(soft_flags)) if soft_flags else ""

    # HP_FULL_CLOSURE gate
    if main_v2 >= hp_full_target:
        return ("HARD_PASS",
                "HARD_PASS_FULL_CLOSURE_LAYER075_V2: MAIN_V2=%.3f >= 0.90 * ORACLE=%.3f "
                "(hp_full_target=%.3f). Retrieval-architecture arc CLOSES: "
                "Layer 0.5 KG-walk + Layer 0.75 v2 iterative-query-augmentation + Layer 1 "
                "FHRR composition pipeline validated within hub-concept-bridge scope. "
                "Iterative query-augmentation via bridge-entity discovery SOLVED the "
                "abstraction-lossy failure Skunkworks diagnosed. "
                "Next: 170K-atom Director-KB scale re-test. %s%s" % (
                    main_v2, oracle, hp_full_target, summary, soft_note),
                per_arm_mean)

    # HP_INTERFACE_POSITIVE gate
    if main_v2 >= hp_interface_floor and s3v2 > hp_interface_floor:
        return ("HARD_PASS",
                "HARD_PASS_INTERFACE_POSITIVE_LAYER075_V2: MAIN_V2=%.3f >= Exp3_baseline=%.3f "
                "AND STAGE3_V2_ONLY=%.3f > Exp3_baseline. Iterative query-augmentation "
                "is at least NON-DESTRUCTIVE at the interface (v1 was strictly destructive: "
                "STAGE3_V1=%.3f << baseline). v2 primitive validated as non-destructive; "
                "deeper improvement toward full closure deferred to Layer 0.75 v3 or scale "
                "escalation. Route to Director for arc-continuation decision. %s%s" % (
                    main_v2, hp_interface_floor, s3v2, s3v1, summary, soft_note),
                per_arm_mean)

    # HARD_FAIL: MAIN_V2 below baseline AND STAGE3_V2_ONLY below floor
    if main_v2 < hf_main_floor and s3v2 < hf_s3v2_floor:
        return ("HARD_FAIL",
                "HARD_FAIL_LAYER075_V2_DEAD: MAIN_V2=%.3f < Exp3_baseline=%.3f "
                "AND STAGE3_V2_ONLY=%.3f < %.2f floor. Iterative query-augmentation is "
                "architecturally dead too -- no lift at either the interface OR in isolation. "
                "Bridge-entity discovery from candidate pool cannot recover multi-hop chain "
                "signal at this regime. ESCALATE to path (a) BridgeRAG tripartite s(q,b,c). "
                "%s%s" % (main_v2, hf_main_floor, s3v2, hf_s3v2_floor, summary, soft_note),
                per_arm_mean)

    # MIDDLE_BAND: partial signal
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_LAYER075_V2_PARTIAL: MAIN_V2=%.3f in [%.3f, %.3f) OR "
            "STAGE3_V2_ONLY=%.3f mixed. v2 primitive shows partial signal but does not "
            "clear either HP gate cleanly. Router: Director for regime assessment; potential "
            "hyperparameter tuning (B_BRIDGES, W_QUERY_ANCHOR/W_AUG) OR escalate to "
            "path (a). %s%s" % (
                main_v2, hf_main_floor, hp_full_target, s3v2, summary, soft_note),
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

    # 5. Composition primitive
    if len(corpus["queries"]) >= 1:
        p = arm_oracle(corpus["queries"][0], corpus)
        assert p in ENTITIES, "oracle arm returned invalid: %r" % p

    # 6. Entity KG + PPR
    A, neigh, degrees = build_entity_kg(corpus["facts"], len(ENTITIES))
    seed_v = seed_vec_from_indices([0], len(ENTITIES))
    ppr = ppr_iterate_sparse(A, seed_v, 0.15, 5)
    assert abs(ppr.sum() - 1.0) < 0.01, "PPR mass leaked: %.4f" % ppr.sum()

    # 7. Stage 1
    passage_counts = compute_passage_counts(corpus["facts"], len(ENTITIES))
    seed_ents = {0, 1, 5, 10}
    s1_vec = stage1_reweight_seed(seed_ents, passage_counts, len(ENTITIES))
    assert abs(s1_vec.sum() - 1.0) < 1e-6, "Stage1 seed vec not normalized"

    # 8. Stage 2
    A_damp = stage2_hub_dampen_adjacency(A, degrees, HUB_DEG_THRESH, 0.30)
    hub_indices_local = np.where(degrees > HUB_DEG_THRESH)[0]
    if len(hub_indices_local) > 0:
        A_dense = A.toarray()
        A_damp_dense = A_damp.toarray()
        for j in hub_indices_local:
            orig_sum = A_dense[:, j].sum()
            damp_sum = A_damp_dense[:, j].sum()
            if orig_sum > 0:
                ratio = damp_sum / orig_sum
                assert abs(ratio - 0.30) < 1e-6, (
                    "Stage2 hub col %d scale ratio=%.4f expected 0.30" % (j, ratio))

    # 9. Stage 3 v1 (MMR reproduction) -- same as Exp 3B
    d = 32
    fake_emb = np.random.default_rng(0).standard_normal((100, d)).astype(np.float32)
    fake_emb = fake_emb / (np.linalg.norm(fake_emb, axis=1, keepdims=True) + 1e-8)
    q_e = fake_emb[3]
    candidates = [3, 17, 42, 55, 68, 71, 82, 90, 95, 99]
    selected = stage3_v1_rescore_mmr(candidates, q_e, fake_emb, k_final=5,
                                       mmr_lambda=0.4)
    assert len(selected) == 5, "v1 MMR selected %d != 5" % len(selected)
    assert selected[0] == 3, "v1 MMR first pick should be identical fact 3, got %d" % selected[0]

    # 10. Stage 3 v2: bridge extraction correctness
    # Construct mini-facts pool where entity 5 co-occurs in facts 0, 1, 2 (bridge!)
    # and entity 10 co-occurs in facts 3, 4 (weaker bridge)
    mini_facts = [
        (ENTITIES[0], "mayor",  ENTITIES[5],  "The mayor of Alton is Fjord."),
        (ENTITIES[1], "river",  ENTITIES[5],  "The river of Bexley is Fjord."),
        (ENTITIES[5], "capital", ENTITIES[6], "The capital of Fjord is Gulch."),
        (ENTITIES[7], "founder", ENTITIES[10], "The founder of Hara is Kelm."),
        (ENTITIES[8], "neighbor", ENTITIES[10], "The neighbor of Iona is Kelm."),
        (ENTITIES[15], "mayor", ENTITIES[16], "The mayor of Pome is Quill."),
    ]
    candidate_indices_mini = list(range(6))
    query_text_mini = "What is the capital of the mayor of Alton?"
    bridges = extract_bridge_candidates(candidate_indices_mini, mini_facts,
                                          query_text_mini, b_bridges=5,
                                          min_cooccur=2)
    # Fjord (index 5) appears in facts 0,1,2 (3 distinct) -> bridge
    # Kelm (index 10) appears in facts 3,4 (2 distinct) -> bridge
    # Alton (index 0) appears only in fact 0 (1 distinct) -> NOT bridge
    # Also Alton (0) IS in the query text; would be filtered anyway
    assert 5 in bridges, "Stage3-v2: Fjord (bridge) not extracted: %r" % bridges
    assert 10 in bridges, "Stage3-v2: Kelm (bridge) not extracted: %r" % bridges
    assert 0 not in bridges, "Stage3-v2: Alton (in query text) not filtered: %r" % bridges
    # Ranking: Fjord should rank first (higher pool freq)
    assert bridges[0] == 5, "Stage3-v2: pool-freq ordering wrong: %r" % bridges

    # 11. Stage 3 v2: min_cooccur = 3 filters Kelm (only 2 co-occur)
    bridges_strict = extract_bridge_candidates(candidate_indices_mini, mini_facts,
                                                 query_text_mini, b_bridges=5,
                                                 min_cooccur=3)
    assert 5 in bridges_strict and 10 not in bridges_strict, (
        "Stage3-v2: min_cooccur=3 didn't filter Kelm: %r" % bridges_strict)

    # 12. Stage 3 v2: full flow with mock BGE encoder returns K_FINAL candidates
    def mock_encode(texts):
        # Simple deterministic mock: hash text -> normalized random vector
        arr = np.zeros((len(texts), d), dtype=np.float32)
        for i, t in enumerate(texts):
            h = hashlib.sha256(t.encode("utf-8")).digest()
            seed_ = int.from_bytes(h[:4], "little")
            v = np.random.default_rng(seed_).standard_normal(d).astype(np.float32)
            arr[i] = v / (np.linalg.norm(v) + 1e-8)
        return arr

    # Use fact_emb from step 9 (fake_emb) as fact_bge in this micro-test
    p1_pool = list(range(30))
    query_bge = fake_emb[0]
    selected_v2, bridges_v2 = stage3_v2_iterative_query_augmentation(
        p1_pool, "What is the mayor of Alton?", query_bge, fake_emb, mini_facts * 5,
        k_final=5, b_bridges=5, w_query=1.0, w_aug=1.0, bridge_min_cooccur=2,
        bge_encode_fn=mock_encode)
    assert len(selected_v2) == 5, "Stage3-v2 didn't return K_FINAL=5: got %d" % len(selected_v2)

    # 13. Stage 3 v2 fallback: empty bridge -> query-only top-K
    # Construct a pool where nothing co-occurs >= min
    facts_no_bridge = [
        (ENTITIES[0], "mayor", ENTITIES[1], "t0"),
        (ENTITIES[2], "river", ENTITIES[3], "t1"),
        (ENTITIES[4], "capital", ENTITIES[5], "t2"),
    ]
    selected_fb, bridges_fb = stage3_v2_iterative_query_augmentation(
        [0, 1, 2], "trivial", query_bge, fake_emb, facts_no_bridge,
        k_final=2, b_bridges=5, w_query=1.0, w_aug=1.0, bridge_min_cooccur=2,
        bge_encode_fn=mock_encode)
    assert bridges_fb == [], "Stage3-v2 fallback: expected empty bridges, got %r" % bridges_fb
    assert len(selected_fb) == 2, "Stage3-v2 fallback: expected 2, got %d" % len(selected_fb)

    # 14. Verdict formulas: HARD_PASS_FULL_CLOSURE
    def _mk_arm(o, e3b, mv2, ss1, ss2, sv1, sv2, rnd):
        return {
            "vacuous": False,
            "per_arm": {
                "ARM_ORACLE_COMPOSITION_SANITY": {"accuracy": o, "n_correct": 0, "n": 50},
                "ARM_EXP3_BASELINE_REPRODUCTION": {"accuracy": e3b, "n_correct": 0, "n": 50},
                "ARM_MAIN_LAYER075_STACKED_V2": {"accuracy": mv2, "n_correct": 0, "n": 50},
                "ARM_STAGE1_ONLY": {"accuracy": ss1, "n_correct": 0, "n": 50},
                "ARM_STAGE2_ONLY": {"accuracy": ss2, "n_correct": 0, "n": 50},
                "ARM_STAGE3_V1_QUERY_ONLY_RESCORE": {"accuracy": sv1, "n_correct": 0, "n": 50},
                "ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY": {"accuracy": sv2, "n_correct": 0, "n": 50},
                "ARM_RANDOM_CANDIDATES_CONTROL": {"accuracy": rnd, "n_correct": 0, "n": 50},
            },
            "arms_differ_violations": [],
        }
    fake_full = [_mk_arm(0.85, 0.41, 0.78, 0.39, 0.41, 0.01, 0.72, 0.05)]
    v, msg, _ = compute_verdict(fake_full)
    assert v == "HARD_PASS" and "FULL_CLOSURE" in msg, "HP_FULL formula: %s | %s" % (v, msg)

    # 15. HARD_PASS_INTERFACE_POSITIVE
    fake_iface = [_mk_arm(0.85, 0.41, 0.55, 0.39, 0.41, 0.01, 0.50, 0.05)]
    v, msg, _ = compute_verdict(fake_iface)
    assert v == "HARD_PASS" and "INTERFACE_POSITIVE" in msg, "HP_IFACE formula: %s | %s" % (v, msg)

    # 16. HARD_FAIL: both dead
    fake_dead = [_mk_arm(0.85, 0.41, 0.02, 0.39, 0.41, 0.01, 0.05, 0.05)]
    v, msg, _ = compute_verdict(fake_dead)
    assert v == "HARD_FAIL" and "DEAD" in msg, "HF formula: %s | %s" % (v, msg)

    # 17. MIDDLE_BAND: main clears baseline but s3v2_only below baseline
    # (so INTERFACE_POSITIVE second-clause fails), and main below FULL_CLOSURE target.
    fake_mid = [_mk_arm(0.85, 0.41, 0.50, 0.39, 0.41, 0.01, 0.30, 0.05)]
    v, msg, _ = compute_verdict(fake_mid)
    assert v == "MIDDLE_BAND" and "PARTIAL" in msg, "MB formula: %s | %s" % (v, msg)

    # 17b. MIDDLE_BAND: both below baselines but s3v2 clears HF floor (not-DEAD)
    fake_mid2 = [_mk_arm(0.85, 0.41, 0.30, 0.39, 0.41, 0.01, 0.25, 0.05)]
    v, msg, _ = compute_verdict(fake_mid2)
    assert v == "MIDDLE_BAND" and "PARTIAL" in msg, "MB formula 2: %s | %s" % (v, msg)

    # 18. HALT_ORACLE_DRIFT
    fake_drift = [_mk_arm(0.40, 0.41, 0.78, 0.39, 0.41, 0.01, 0.72, 0.05)]
    v, msg, _ = compute_verdict(fake_drift)
    assert v == "HARD_FAIL" and "ORACLE_DRIFT" in msg, "ORACLE_DRIFT: %s" % v

    print("[selftest] PASS: exp3c Layer 0.75 v2 iterative-query-augmentation primitive OK",
          flush=True)


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
    _write_start_marker(out_dir, expected_n_units=8 * len(SEEDS))

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
        "expected_n_units": 8 * len([s for s in per_seed if not s.get("vacuous", False)]),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed
                              if not s.get("vacuous", False)),
        "cardinality_ok": (sum(len(s.get("per_arm", {})) for s in per_seed
                               if not s.get("vacuous", False))
                           == 8 * len([s for s in per_seed if not s.get("vacuous", False)])),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.035,
        "crlb_formula_reference": "sqrt(K_final/N_dim) = sqrt(5/4096) per Plate 1995",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "scope": "hub_concept_bridge_only",
        "oracle_precedent": 0.8533,
        "exp3_baseline_precedent": 0.4133,
        "stage3_v1_precedent": 0.0133,
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
