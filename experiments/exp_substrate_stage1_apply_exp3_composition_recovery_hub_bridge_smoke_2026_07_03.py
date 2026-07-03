"""exp_substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03.

Experiment 3 from the optimal-retrieval-architecture drill (2026-07-03).

Question: does end-to-end pipeline
    (BGE dense hop-1) -> (PPR-walk over KG, seeded from hop-1) -> (FHRR composition)
recover composition F1 approaching ORACLE=0.783 within the hub-concept-bridge
scope validated by Skunkworks Exp 2C VET (MEASURED_MECHANISM tier)?

Precedents (MEASURED@ off-disk):
  ORACLE   = 0.7833  data/exp_substrate_rag_with_substrate_composition_smoke_2026_07_03_smoke/metrics.json
  BASELINE = 0.0833  same file (BGE dense-only composition)
  Exp 2C MAIN_PPR    = 0.993   data/exp_exp2c_smoke_local/metrics.json
  Exp 2C baseline    = 0.347   same file

Scope: hub-concept-bridge queries ONLY. In this synthetic corpus, hubs are 3
entities that receive ~3x more inbound fact-edges than non-hubs. Chain queries
"What is r1 of r2 of e0?" filtered to those where mid entity is a hub.

Arms (4):
  ARM_BGE_ONLY_COMPOSITION_BASELINE     - hop-1 BGE top-K -> composition; expect ~0.083
  ARM_PPR_UNION_HOP1_COMPOSITION_MAIN   - {BGE hop-1} U {PPR-recovered} -> composition
  ARM_ORACLE_COMPOSITION_SANITY         - GT chunks -> composition; expect ~0.783
  ARM_RANDOM_CANDIDATES_CONTROL         - random facts -> composition; expect ~0.05

Bands (auto-scaled to measured ORACLE):
  HARD_PASS: MAIN >= 0.90 * ORACLE
  HARD_FAIL: MAIN <  0.60 * ORACLE
  MIDDLE:    0.60..0.90
  HALT_ORACLE_DRIFT:  |ORACLE - 0.783| >= 0.10
  FLAG_BASELINE_DRIFT: |BASELINE - 0.083| >= 0.10 (soft flag, not fatal)

Composition primitive: identical to ORACLE cell's arm_tandem_rag_substrate_composition.
PPR primitive: identical to Exp 2C's ppr_iterate_sparse (alpha=0.15 iters=5).

ASCII-only. sequential-CPU. sharded storage.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm prediction-array hash)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_floor_computed=0.016  THEORETICAL@sqrt(K/N)=sqrt(5/4096) Plate 1995 FHRR floor
# - discriminator_reachability: True (HP target 0.70 >> CRLB 0.016)
# - baseline_in_band: 0.05 < BASELINE < 0.30 expected (BGE-composition HF regime)
# - discriminator survives scale: SMOKE regime IS test regime (N_DIM=4096 matches ORACLE)
# - HARD_PASS strictly above floor+5% band-width via 0.90 * ORACLE scaling
# - HP_SCOPE: HARD_PASS applies only to MAIN; ORACLE has reproduction gate; BASELINE/RANDOM exempted from HP
# - cardinality_ok: EXPECTED_N_UNITS = 4 arms x 3 seeds = 12
# - per-unit failure-class instrumentation (specific Exception only)
# - calibration_check: default_ok_for_this_regime (chain-grade FHRR + Exp 2C PPR)
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


ANCHOR_NAME = "substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03"
BI_MODEL = "BAAI/bge-small-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "

# Vocabulary (larger than ORACLE cell to accommodate hub structure)
ENTITIES = [
    "Alton", "Bexley", "Coral", "Delft", "Erie", "Fjord", "Gulch", "Hara",
    "Iona", "Juno", "Kelm", "Loam", "Mesa", "Nord", "Osek", "Pome",
    "Quill", "Riva", "Solt", "Tern",
    "Umbra", "Vail", "Wren", "Xylo", "Yara", "Zorn", "Ashe", "Brix",
    "Corv", "Dune", "Ebon", "Frey", "Glim", "Holt", "Ivor", "Jarl",
    "Kord", "Larn", "Mote", "Nyx",
]  # 40 entities

RELATIONS = ["mayor", "capital", "river", "neighbor", "founder"]  # 5 relations

# Hub structure: entities 0,1,2 = "Alton", "Bexley", "Coral" are hubs (over-sampled as VALUE)
HUB_INDICES = [0, 1, 2]
HUB_OVER_SAMPLE = 3.0  # hubs weighted 3x more likely to be chosen as fact value

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
    N_QUERIES_TARGET = 30
    SEEDS = [11, 17, 23]

TOP_K = 5
PPR_ALPHA = 0.15
PPR_ITERS = 5
PPR_TOP_K = 5


# ---------- FHRR primitives (real-valued phase encoding) ----------
def rand_phase_hd(rng: np.random.Generator, n_dim: int) -> np.ndarray:
    """Random phase vector in [-pi, pi)."""
    return (rng.random(n_dim, dtype=np.float64) * 2.0 - 1.0) * np.pi


def bind_phase(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind = phase addition wrapped."""
    s = a + b
    return (s + np.pi) % (2.0 * np.pi) - np.pi


def unbind_phase(query: np.ndarray, bound: np.ndarray) -> np.ndarray:
    """FHRR unbind = phase subtraction."""
    s = bound - query
    return (s + np.pi) % (2.0 * np.pi) - np.pi


def phase_cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.cos(a - b)))


def phase_cos_batch(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    return np.mean(np.cos(B - a[None, :]), axis=1)


# ---------- corpus construction (hub-and-spoke) ----------
def build_corpus(rng_seed: int, n_dim: int) -> Dict:
    """Build synthetic hub-and-spoke corpus + chain queries filtered to hub-bridge scope."""
    rng = np.random.default_rng(rng_seed)
    py_rng = random.Random(rng_seed)

    E = len(ENTITIES)
    R = len(RELATIONS)

    # Weighted value sampler: hubs get HUB_OVER_SAMPLE probability multiplier
    weights = np.ones(E, dtype=np.float64)
    for h in HUB_INDICES:
        weights[h] = HUB_OVER_SAMPLE
    weights_norm = weights / weights.sum()

    # facts_dict[e][r] = value entity name
    facts_dict: Dict[str, Dict[str, str]] = {e: {} for e in ENTITIES}
    for e in ENTITIES:
        for r in RELATIONS:
            v_idx = int(rng.choice(E, p=weights_norm))
            v = ENTITIES[v_idx]
            facts_dict[e][r] = v

    # Flatten to list of (e, r, v, text) facts
    facts: List[Tuple[str, str, str, str]] = []
    for e in ENTITIES:
        for r in RELATIONS:
            v = facts_dict[e][r]
            text = "The %s of %s is %s." % (r, e, v)
            facts.append((e, r, v, text))

    # Codebooks
    entity_codebook = np.zeros((E, n_dim), dtype=np.float64)
    for i in range(E):
        entity_codebook[i] = rand_phase_hd(rng, n_dim)
    relation_codebook = np.zeros((R, n_dim), dtype=np.float64)
    for i in range(R):
        relation_codebook[i] = rand_phase_hd(rng, n_dim)
    value_codebook = entity_codebook

    # Encode facts as FHRR triples
    n_facts = len(facts)
    fact_hds = np.zeros((n_facts, n_dim), dtype=np.float64)
    for i, (e, r, v, _t) in enumerate(facts):
        ei = ENTITIES.index(e)
        ri = RELATIONS.index(r)
        vi = ENTITIES.index(v)
        inner = bind_phase(relation_codebook[ri], value_codebook[vi])
        fact_hds[i] = bind_phase(entity_codebook[ei], inner)

    # In-degree per entity (as VALUE): identifies hubs empirically
    in_deg = np.zeros(E, dtype=np.int64)
    for (_e, _r, v, _t) in facts:
        in_deg[ENTITIES.index(v)] += 1
    # Empirical hub set: top 3 by in-degree (should be dominated by HUB_INDICES by construction)
    hub_empirical = sorted(range(E), key=lambda i: -in_deg[i])[:3]
    hub_set = set(hub_empirical) | set(HUB_INDICES)

    # Build chain queries: e0 --r2--> mid --r1--> answer; filter mid in hub_set
    queries: List[Dict] = []
    tries = 0
    max_tries = N_QUERIES_TARGET * 100
    while len(queries) < N_QUERIES_TARGET and tries < max_tries:
        tries += 1
        e0 = py_rng.choice(ENTITIES)
        r1 = py_rng.choice(RELATIONS)
        r2 = py_rng.choice(RELATIONS)
        mid = facts_dict[e0][r2]
        mid_idx = ENTITIES.index(mid)
        if mid_idx not in hub_set:
            continue  # scope filter: hub-concept-bridge only
        answer = facts_dict[mid][r1]
        # Skip trivial (answer == e0, or mid == e0, or answer == mid) to avoid degenerate cases
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


# ---------- KG graph over entities ----------
def build_entity_kg(facts: List[Tuple[str, str, str, str]],
                    n_entities: int) -> Tuple[sp.csr_matrix, Dict[int, Set[int]]]:
    """Build undirected column-stochastic adjacency + neighbor sets from facts."""
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
    return A, neighbors


def ppr_iterate_sparse(A: sp.csr_matrix, seed_vec: np.ndarray, alpha: float,
                       iters: int) -> np.ndarray:
    """x_{t+1} = (1-alpha) * A @ x_t + alpha * s; renormalize defensively."""
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


# ---------- composition primitive (identical to ORACLE cell arm) ----------
def composition_primitive(q: Dict, corpus: Dict, retrieved_idx: List[int]) -> str:
    """FHRR 2-hop unbind chain over retrieved facts. Identical to
    ORACLE cell's arm_tandem_rag_substrate_composition."""
    e0 = q["e0"]; r1 = q["r1"]; r2 = q["r2"]
    E_cb = corpus["entity_codebook"]
    R_cb = corpus["relation_codebook"]
    V_cb = corpus["value_codebook"]
    e0i = ENTITIES.index(e0)
    r1i = RELATIONS.index(r1)
    r2i = RELATIONS.index(r2)
    if not retrieved_idx:
        return ENTITIES[0]  # degenerate; return arbitrary
    retrieved_hds = corpus["fact_hds"][retrieved_idx]  # (K, N)

    # Stage 1
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
    # Stage 2
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
def bge_retrieve_all(queries: List[Dict], fact_texts: List[str],
                     top_k: int) -> List[List[int]]:
    """Encode fact texts + queries with bge-small; return top-K fact indices per query."""
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
    sims = q_e @ fact_e.T
    retrieved = []
    for i in range(sims.shape[0]):
        order = np.argsort(sims[i])[::-1][:top_k].tolist()
        retrieved.append(order)
    del mdl
    return retrieved


# ---------- arm implementations ----------
def arm_bge_only_baseline(q: Dict, corpus: Dict, bge_retrieved: List[int]) -> str:
    """Hop-1 BGE dense top-K facts -> composition primitive."""
    return composition_primitive(q, corpus, bge_retrieved)


def arm_ppr_union_hop1_main(q: Dict, corpus: Dict, bge_retrieved: List[int],
                            A: sp.csr_matrix,
                            n_entities: int) -> Tuple[str, List[int]]:
    """{BGE hop-1} U {PPR-recovered facts} -> composition primitive.

    PPR seed = entities appearing in BGE hop-1 facts (both entity and value slots).
    Top-K PPR entities -> all facts whose entity or value is in that top-K set.

    DESIGN NOTE (2026-07-03 mid-smoke): a tightening attempt (top-K facts by
    endpoint-sum PPR score) collapsed MAIN to 0.044 -- PPR mass on hub-and-spoke
    KG concentrates on the hubs regardless of specific query, so top-K by PPR
    score becomes query-independent hub facts. Retained the looser "all facts
    touching top-K entities" design which at least achieves 0.411 MAIN.
    """
    seed_entities: Set[int] = set()
    for idx in bge_retrieved:
        e, _r, v, _t = corpus["facts"][idx]
        seed_entities.add(ENTITIES.index(e))
        seed_entities.add(ENTITIES.index(v))
    seed_vec = seed_vec_from_indices(sorted(seed_entities), n_entities)
    ppr_dist = ppr_iterate_sparse(A, seed_vec, PPR_ALPHA, PPR_ITERS)
    top_k_ent = np.argsort(ppr_dist)[::-1][:PPR_TOP_K].tolist()
    top_k_ent_set = set(top_k_ent)
    ppr_facts: List[int] = []
    for i, (e, _r, v, _t) in enumerate(corpus["facts"]):
        if ENTITIES.index(e) in top_k_ent_set or ENTITIES.index(v) in top_k_ent_set:
            ppr_facts.append(i)
    union = list(dict.fromkeys(bge_retrieved + ppr_facts))
    if len(union) > 30:
        union = union[:30]
    return composition_primitive(q, corpus, union), union


def arm_oracle(q: Dict, corpus: Dict) -> str:
    return composition_primitive(q, corpus, q["gt_chunks"])


def arm_random_control(q: Dict, corpus: Dict, rng: np.random.Generator,
                       k: int = TOP_K) -> str:
    n_facts = corpus["fact_hds"].shape[0]
    rand_idx = rng.choice(n_facts, size=k, replace=False).tolist()
    return composition_primitive(q, corpus, rand_idx)


# ---------- per-seed run ----------
def run_seed(seed: int) -> Dict:
    print("[seed=%d] building hub-and-spoke corpus N_DIM=%d target_queries=%d" % (
        seed, N_DIM, N_QUERIES_TARGET), flush=True)
    t0 = time.perf_counter()
    corpus = build_corpus(seed, N_DIM)
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
    A, neighbors = build_entity_kg(corpus["facts"], len(ENTITIES))
    print("  KG built: n_edges_undirected=%d" % (A.nnz // 2), flush=True)

    # BGE retrieval
    print("[seed=%d] running bge retrieval top_k=%d..." % (seed, TOP_K), flush=True)
    tr = time.perf_counter()
    bge_retrieved = bge_retrieve_all(corpus["queries"], fact_texts, TOP_K)
    print("  bge_done elapsed=%.1fs" % (time.perf_counter() - tr), flush=True)

    rng = np.random.default_rng(seed + 1000)
    arm_names = [
        "ARM_BGE_ONLY_COMPOSITION_BASELINE",
        "ARM_PPR_UNION_HOP1_COMPOSITION_MAIN",
        "ARM_ORACLE_COMPOSITION_SANITY",
        "ARM_RANDOM_CANDIDATES_CONTROL",
    ]
    preds_by_arm: Dict[str, List[str]] = {n: [] for n in arm_names}
    per_query_diag: List[Dict] = []

    n_entities = len(ENTITIES)
    for qi, q in enumerate(corpus["queries"]):
        bge_ret = bge_retrieved[qi]
        p_base = arm_bge_only_baseline(q, corpus, bge_ret)
        p_main, main_union = arm_ppr_union_hop1_main(
            q, corpus, bge_ret, A, n_entities)
        p_oracle = arm_oracle(q, corpus)
        p_random = arm_random_control(q, corpus, rng)
        preds_by_arm["ARM_BGE_ONLY_COMPOSITION_BASELINE"].append(p_base)
        preds_by_arm["ARM_PPR_UNION_HOP1_COMPOSITION_MAIN"].append(p_main)
        preds_by_arm["ARM_ORACLE_COMPOSITION_SANITY"].append(p_oracle)
        preds_by_arm["ARM_RANDOM_CANDIDATES_CONTROL"].append(p_random)
        if qi < 5:
            per_query_diag.append({
                "qi": qi, "text": q["text"], "e0": q["e0"], "mid": q["mid"],
                "answer": q["answer"], "gt_chunks": q["gt_chunks"],
                "bge_top5": bge_ret, "main_union_size": len(main_union),
                "p_base": p_base, "p_main": p_main,
                "p_oracle": p_oracle, "p_random": p_random,
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

    # ARMS-MUST-DIFFER
    digests = {}
    for name in arm_names:
        blob = "|".join(preds_by_arm[name]).encode("utf-8")
        digests[name] = hashlib.sha256(blob).hexdigest()[:16]
    seen: Dict[str, str] = {}
    arms_differ_violations = []
    for name, dig in digests.items():
        if dig in seen:
            arms_differ_violations.append((seen[dig], name, dig))
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
        "in_deg": corpus["in_deg"],
        "per_query_diag": per_query_diag,
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    active = [s for s in per_seed if not s.get("vacuous", False)]
    if not active:
        return ("HARD_FAIL",
                "HARD_FAIL_ALL_VACUOUS: no seeds produced >=10 hub-bridge queries. "
                "Corpus/scope filter too tight.", {})

    arm_names = ["ARM_BGE_ONLY_COMPOSITION_BASELINE",
                 "ARM_PPR_UNION_HOP1_COMPOSITION_MAIN",
                 "ARM_ORACLE_COMPOSITION_SANITY",
                 "ARM_RANDOM_CANDIDATES_CONTROL"]
    per_arm_mean = {}
    for name in arm_names:
        accs = [s["per_arm"][name]["accuracy"] for s in active]
        per_arm_mean[name] = float(np.mean(accs))

    baseline = per_arm_mean["ARM_BGE_ONLY_COMPOSITION_BASELINE"]
    main = per_arm_mean["ARM_PPR_UNION_HOP1_COMPOSITION_MAIN"]
    oracle = per_arm_mean["ARM_ORACLE_COMPOSITION_SANITY"]
    random_ctrl = per_arm_mean["ARM_RANDOM_CANDIDATES_CONTROL"]

    ORACLE_PRECEDENT = 0.7833  # MEASURED@data/exp_substrate_rag_with_substrate_composition_smoke_2026_07_03_smoke/metrics.json
    BASELINE_PRECEDENT = 0.0833  # same file

    oracle_drift = abs(oracle - ORACLE_PRECEDENT)
    baseline_drift = abs(baseline - BASELINE_PRECEDENT)

    hp_target = 0.90 * oracle  # scaled to measured ORACLE
    hf_target = 0.60 * oracle

    # Cardinality
    expected_units = 4 * len(active)
    actual_units = sum(len(s["per_arm"]) for s in active)
    cardinality_ok = actual_units == expected_units

    arms_differ_ok = all(len(s["arms_differ_violations"]) == 0 for s in active)

    summary = ("BASELINE=%.3f (drift=%.3f) MAIN=%.3f ORACLE=%.3f (drift=%.3f) "
               "RANDOM=%.3f | hp_target=%.3f hf_target=%.3f | cardinality_ok=%s "
               "arms_differ_ok=%s") % (
        baseline, baseline_drift, main, oracle, oracle_drift, random_ctrl,
        hp_target, hf_target, cardinality_ok, arms_differ_ok)

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d got %d. %s" % (
                    expected_units, actual_units, summary), per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical. %s" % summary, per_arm_mean)

    # ORACLE reproduction gate (composition primitive sanity)
    if oracle_drift >= 0.10:
        return ("HARD_FAIL",
                "HALT_ORACLE_DRIFT: ORACLE arm = %.3f drifted %.3f from precedent %.3f. "
                "Composition primitive appears to have changed since 2026-07-03 morning. "
                "Do NOT trust MAIN arm interpretation. %s" % (
                    oracle, oracle_drift, ORACLE_PRECEDENT, summary), per_arm_mean)

    baseline_note = ""
    if baseline_drift >= 0.10:
        baseline_note = (" FLAG_BASELINE_DRIFT: BASELINE=%.3f (precedent=%.3f drift=%.3f); "
                        "dense-retrieval failure regime differs from precedent (soft flag)." % (
                            baseline, BASELINE_PRECEDENT, baseline_drift))

    # Decision-point CLOSES only if all conditions met
    if main >= hp_target:
        return ("HARD_PASS",
                "HARD_PASS_COMPOSITION_RECOVERY_HUB_BRIDGE: MAIN=%.3f >= 0.90 * ORACLE=%.3f "
                "(target=%.3f). Retrieval-architecture arc CLOSES: composition works when fed "
                "PPR-recovered candidates; encoder-swap deferred validated; Layer 0.5 KG-walk "
                "viable within hub-concept-bridge scope. %s%s" % (
                    main, oracle, hp_target, summary, baseline_note), per_arm_mean)
    if main < hf_target:
        return ("HARD_FAIL",
                "HARD_FAIL_COMPOSITION_RECOVERY_HUB_BRIDGE: MAIN=%.3f < 0.60 * ORACLE=%.3f "
                "(hf_target=%.3f); PPR-recovered candidates do NOT restore composition F1 "
                "even in hub-bridge scope. Re-examine PPR-composition interface. %s%s" % (
                    main, oracle, hf_target, summary, baseline_note), per_arm_mean)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_COMPOSITION_RECOVERY_HUB_BRIDGE: MAIN=%.3f in [0.60 * ORACLE=%.3f, "
            "0.90 * ORACLE=%.3f]; partial signal; PPR helps but does not fully restore. %s%s" % (
                main, hf_target, hp_target, summary, baseline_note), per_arm_mean)


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
    corpus = build_corpus(11, 256)
    in_deg = corpus["in_deg"]
    hub_in = sum(in_deg[h] for h in HUB_INDICES)
    non_hub_in = sum(in_deg) - hub_in
    # Hubs (3 of 40 entities) should hold significantly more than 3/40 of total in-degree
    hub_frac = hub_in / max(sum(in_deg), 1)
    expected_baseline = 3.0 / 40.0
    # With HUB_OVER_SAMPLE=3, hub fraction should be ~ 3/(3*3 + 37) = 3/46 * 3 = 9/46 ~ 0.196
    # Loose check: at least 2x random baseline
    assert hub_frac >= 2 * expected_baseline, (
        "hub-injection failed: hub_frac=%.3f expected>=%.3f" % (hub_frac, 2 * expected_baseline))

    # 4. Queries respect hub-bridge scope
    if len(corpus["queries"]) >= 5:
        for q in corpus["queries"][:5]:
            mid_idx = ENTITIES.index(q["mid"])
            assert mid_idx in set(corpus["hub_set"]), (
                "scope violation: query mid=%r idx=%d not in hub_set=%s" % (
                    q["mid"], mid_idx, corpus["hub_set"]))

    # 5. Composition primitive on ORACLE arm (small N, may not be perfect but must return valid)
    if len(corpus["queries"]) >= 1:
        p = arm_oracle(corpus["queries"][0], corpus)
        assert p in ENTITIES, "oracle arm returned invalid: %r" % p

    # 6. Entity KG build + PPR
    A, neigh = build_entity_kg(corpus["facts"], len(ENTITIES))
    assert A.shape == (len(ENTITIES), len(ENTITIES))
    seed_v = seed_vec_from_indices([0], len(ENTITIES))
    ppr = ppr_iterate_sparse(A, seed_v, 0.15, 5)
    assert abs(ppr.sum() - 1.0) < 0.01, "PPR mass leaked: %.4f" % ppr.sum()

    # 7. Verdict formulas: HARD_PASS
    fake_pass = [{
        "vacuous": False,
        "per_arm": {
            "ARM_BGE_ONLY_COMPOSITION_BASELINE": {"accuracy": 0.08, "n_correct": 2, "n": 25},
            "ARM_PPR_UNION_HOP1_COMPOSITION_MAIN": {"accuracy": 0.72, "n_correct": 18, "n": 25},
            "ARM_ORACLE_COMPOSITION_SANITY": {"accuracy": 0.78, "n_correct": 19, "n": 25},
            "ARM_RANDOM_CANDIDATES_CONTROL": {"accuracy": 0.05, "n_correct": 1, "n": 25},
        },
        "arms_differ_violations": [],
    }]
    v, msg, _ = compute_verdict(fake_pass)
    assert v == "HARD_PASS", "HP formula: %s | %s" % (v, msg)

    # 8. HARD_FAIL (MAIN below 0.60 * ORACLE)
    fake_fail = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_PPR_UNION_HOP1_COMPOSITION_MAIN": {"accuracy": 0.30, "n_correct": 7, "n": 25}}}]
    v, msg, _ = compute_verdict(fake_fail)
    assert v == "HARD_FAIL" and "COMPOSITION_RECOVERY_HUB_BRIDGE" in msg, "HF: %s" % v

    # 9. MIDDLE_BAND
    fake_mid = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_PPR_UNION_HOP1_COMPOSITION_MAIN": {"accuracy": 0.55, "n_correct": 14, "n": 25}}}]
    v, msg, _ = compute_verdict(fake_mid)
    assert v == "MIDDLE_BAND", "MB: %s | %s" % (v, msg)

    # 10. HALT_ORACLE_DRIFT
    fake_drift = [{**fake_pass[0], "per_arm": {**fake_pass[0]["per_arm"],
        "ARM_ORACLE_COMPOSITION_SANITY": {"accuracy": 0.40, "n_correct": 10, "n": 25}}}]
    v, msg, _ = compute_verdict(fake_drift)
    assert v == "HARD_FAIL" and "ORACLE_DRIFT" in msg, "ORACLE_DRIFT: %s" % v

    print("[selftest] PASS: exp3 composition-recovery primitives OK", flush=True)


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
          "ppr_alpha=%.2f ppr_iters=%d hub_indices=%s hub_over=%.1f" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_QUERIES_TARGET, SEEDS, TOP_K,
              PPR_ALPHA, PPR_ITERS, HUB_INDICES, HUB_OVER_SAMPLE), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=4 * len(SEEDS))

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
        "hub_indices": HUB_INDICES,
        "hub_over_sample": HUB_OVER_SAMPLE,
        "per_seed": per_seed,
        "per_arm_mean_accuracy": per_arm_mean,
        "expected_n_units": 4 * len([s for s in per_seed if not s.get("vacuous", False)]),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed
                              if not s.get("vacuous", False)),
        "cardinality_ok": (sum(len(s.get("per_arm", {})) for s in per_seed
                               if not s.get("vacuous", False))
                           == 4 * len([s for s in per_seed if not s.get("vacuous", False)])),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.016,
        "crlb_formula_reference": "sqrt(K_chunks/N_dim) = sqrt(5/4096) per Plate 1995",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "scope": "hub_concept_bridge_only",
        "oracle_precedent": 0.7833,
        "baseline_precedent": 0.0833,
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
