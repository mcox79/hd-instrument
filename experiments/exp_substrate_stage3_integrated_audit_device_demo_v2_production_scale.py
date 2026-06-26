"""substrate_stage3_integrated_audit_device_demo_v2_production_scale -- EXT-1.

EXTENSION TARGET (per Research drill 2026-06-25 EXT-1): the v1 cell chain-
graded at V_C_IN=600 / V_REL=8 / M_KV=10k. Production audit-device needs
V_C_IN >= 2000 + V_REL >= 50. This cell answers "is the substrate-product
shippable at production V."

Sweeps 4 production-scale (V_C_IN, V_REL) operating points within a single
seed. Each point reuses the v1 pipeline structure (intent -> audit -> graph-
health -> KG retrieve -> templated response -> CSP confidence).

OPERATING POINTS (4):
  (V_C_IN=1000, V_REL=20)
  (V_C_IN=1000, V_REL=50)
  (V_C_IN=2000, V_REL=20)
  (V_C_IN=2000, V_REL=50)

CONFIG (cross-point fixed):
  N=8192, M_KV=10000, seeds=[11, 13, 19]
  4 categories x 1000 queries per category at each operating point
  Substrate-only; ASCII; per-arm/per-category metrics

ARMS (4; same as v1):
  ARM_INDIVIDUAL_PRIMITIVES_PARALLEL
  ARM_PIPELINE_COMPOSED                 (the product audit-device)
  ARM_AUDIT_ONLY_RAIL
  ARM_NO_REFUSE_RAIL

PRE-REG BANDS (LOCKED at module init):

  HARD_PASS_PRODUCTION_SCALE:
    at (V_C_IN=2000, V_REL=50):
      ARM_PIPELINE_COMPOSED:
        PURE_IN_DOMAIN answer_rate >= 0.85
        PURE_OUT_OF_DOMAIN refuse_rate >= 0.85
        NEAR_DOMAIN_MIXED refuse_rate >= 0.85
        IN_DOMAIN_UNCERTAIN correct_rate >= 0.70
      AND PIPELINE p95 latency <= 10 ms
      AND cv <= 0.07 across seeds

  CHAIN_GRADE_AT_LOWER_X:
    passes at one of (1000,20), (1000,50), (2000,20) but not (2000,50)

  HARD_FAIL_REFUSE_GATE_CLIFF:
    refuse-gate (NEAR_DOMAIN_MIXED refuse_rate) < 0.50 at any V_REL >= 20

  HARD_FAIL_LATENCY_BLOWN:
    pipeline p95 > 50 ms at any operating point

GPU routing: overnight_queue. V_C_IN=2000 x V_REL=50 x N=8192 + per-query
matmul is GPU-bound at full scale per Fix #24.

Author: exp_dev 2026-06-25 (EXT-1 production-scale).
ASCII-only; per-seed checkpoint; substrate-only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_stage3_integrated_audit_device_demo_v2_production_scale"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ============================================================================
# PROSPECTIVE BANDS (LOCKED)
# ============================================================================
HP_PURE_IN_ANSWER_MIN = 0.85
HP_PURE_OUT_REFUSE_MIN = 0.85
HP_NEAR_REFUSE_MIN = 0.85
HP_UNCERTAIN_CORR_MIN = 0.70
HP_LATENCY_P95_MS = 10.0
HP_CV_MAX = 0.07
HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20 = 0.50
HF_LATENCY_BLOWN_MS = 50.0

# Production-scale "target" operating point: (V_C_IN=2000, V_REL=50)
TARGET_POINT = (2000, 50)

assert 0 < HP_PURE_IN_ANSWER_MIN <= 1.0
assert HP_LATENCY_P95_MS < HF_LATENCY_BLOWN_MS

# ============================================================================
# CONFIG (per operating point)
# ============================================================================
N_DIM = 2048 if RUN_MODE == "smoke" else 8192

if RUN_MODE == "smoke":
    OPERATING_POINTS = [(200, 8), (400, 16)]  # micro
    SEEDS = [11]
    M_KV = 2000
    N_QUERIES_PURE_IN = 25
    N_QUERIES_PURE_OUT = 25
    N_QUERIES_NEAR = 25
    N_QUERIES_UNCERTAIN = 25
else:
    OPERATING_POINTS = [(1000, 20), (1000, 50), (2000, 20), (2000, 50)]
    SEEDS = [11, 13, 19]
    M_KV = 10000
    N_QUERIES_PURE_IN = 1000
    N_QUERIES_PURE_OUT = 1000
    N_QUERIES_NEAR = 500
    N_QUERIES_UNCERTAIN = 500

D_KV = 768
C_KV = 256
SIGMA_KV = 0.1
N_TEMPLATES = 20

SUBJECT_AUDIT_THR = 0.40
RELATION_AUDIT_THR = 0.40
INTENT_CONF_THR = 0.03
GRAPH_HEALTH_THR = 0.30
CSP_LOWCONF_THR = 5
CSP_MAX_ITERS = 10 if RUN_MODE == "smoke" else 20

# OOD subject/relation library sized to be larger than in-domain for clean OOD queries
V_C_OUT_FACTOR = 1.0  # OOD has same size as in-domain per category
V_REL_OUT_FACTOR = 1.0

FLIP_FRAC_NORMAL = 0.10
FLIP_FRAC_UNCERTAIN = 0.45

CATEGORY_LABELS = (
    "PURE_IN_DOMAIN", "PURE_OUT_OF_DOMAIN",
    "NEAR_DOMAIN_MIXED", "IN_DOMAIN_UNCERTAIN",
)
CATEGORY_EXPECT_ANSWER = {
    "PURE_IN_DOMAIN": True,
    "PURE_OUT_OF_DOMAIN": False,
    "NEAR_DOMAIN_MIXED": False,
    "IN_DOMAIN_UNCERTAIN": None,
}
N_QUERIES_PER_CAT = {
    "PURE_IN_DOMAIN": N_QUERIES_PURE_IN,
    "PURE_OUT_OF_DOMAIN": N_QUERIES_PURE_OUT,
    "NEAR_DOMAIN_MIXED": N_QUERIES_NEAR,
    "IN_DOMAIN_UNCERTAIN": N_QUERIES_UNCERTAIN,
}

CONFIG_VERSION = (
    "substrateStage3IntegratedDemoV2ProductionScale: N=%d operating_points=%s "
    "M_KV=%d d_kv=%d C_kv=%d sigma_kv=%.2f "
    "n_q_in=%d n_q_out=%d n_q_near=%d n_q_uncertain=%d seeds=%s mode=%s "
    "target=%s; bands HP_in_ans>=%.2f HP_out_ref>=%.2f HP_near_ref>=%.2f "
    "HP_uncert_corr>=%.2f HP_p95<=%.1fms HP_cv<=%.2f "
    "HF_near_ref_min_at_V_REL_ge_20<%.2f HF_lat>%.1fms"
) % (
    N_DIM, OPERATING_POINTS, M_KV, D_KV, C_KV, SIGMA_KV,
    N_QUERIES_PURE_IN, N_QUERIES_PURE_OUT, N_QUERIES_NEAR, N_QUERIES_UNCERTAIN,
    SEEDS, RUN_MODE, TARGET_POINT,
    HP_PURE_IN_ANSWER_MIN, HP_PURE_OUT_REFUSE_MIN, HP_NEAR_REFUSE_MIN,
    HP_UNCERTAIN_CORR_MIN, HP_LATENCY_P95_MS, HP_CV_MAX,
    HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20, HF_LATENCY_BLOWN_MS,
)


# ============================================================================
# Substrate primitives (mirrors stage3 v1)
# ============================================================================

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gaussian_keys(M: int, d: int, g: np.random.Generator) -> np.ndarray:
    return g.standard_normal((M, d)).astype(np.float32)


def _norm(X: np.ndarray) -> np.ndarray:
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def add_noise(vec: np.ndarray, flip_frac: float, fg: np.random.Generator,
               n_dim: int) -> np.ndarray:
    n_flip = int(n_dim * flip_frac)
    flip_idxs = fg.choice(n_dim, size=n_flip, replace=False)
    v = vec.copy()
    v[flip_idxs] *= -1.0
    v = v / (np.linalg.norm(v) + 1e-8)
    return v.astype(np.float32)


def build_substrate(g: np.random.Generator, V_C_IN: int, V_REL: int) -> Dict[str, Any]:
    V_C_OUT = int(V_C_IN * V_C_OUT_FACTOR)
    V_REL_OUT = int(V_REL * V_REL_OUT_FACTOR)

    W_subjects = bipolar(V_C_IN, N_DIM, g)
    W_relations_in = bipolar(V_REL, N_DIM, g)
    out_subject_atoms = bipolar(V_C_OUT, N_DIM, g)
    out_relation_atoms = bipolar(V_REL_OUT, N_DIM, g)
    relation_in_prototypes = W_relations_in.copy()

    K_kv = gaussian_keys(M_KV, D_KV, g)
    y_kv = g.integers(0, C_KV, M_KV).astype(np.int64)
    codebook_kv = _norm(g.standard_normal((C_KV, D_KV)).astype(np.float32))
    W_kv = codebook_kv[y_kv].T @ K_kv

    subject_to_kv_idx = g.integers(0, M_KV, V_C_IN).astype(np.int64)
    subject_to_template = g.integers(0, N_TEMPLATES, V_C_IN).astype(np.int64)
    templates = [
        "%s relates to %s via %s" % (s, "PLACEHOLDER", "RELATION")
        for s in ["item", "concept", "entity", "object", "node",
                  "atom", "instance", "subject", "term", "datum",
                  "datum2", "item2", "concept2", "entity2", "atom2",
                  "instance2", "subject2", "term2", "node2", "object2"]
    ]

    n_kg_nodes = min(128, V_C_IN)
    n_kg_edges = max(2, int(0.15 * n_kg_nodes))
    kg_node_idxs = g.choice(V_C_IN, n_kg_nodes, replace=False).astype(np.int64)
    edges_set = set()
    kg_edges: List[Tuple[int, int]] = []
    while len(kg_edges) < n_kg_edges:
        u = int(g.integers(0, n_kg_nodes))
        w = int(g.integers(0, n_kg_nodes))
        if u != w:
            k = (min(u, w), max(u, w))
            if k not in edges_set:
                edges_set.add(k)
                kg_edges.append(k)
    kg_node_vecs = W_subjects[kg_node_idxs]
    G = np.zeros(N_DIM, dtype=np.float32)
    for (u, w) in kg_edges:
        G += kg_node_vecs[u] * kg_node_vecs[w]

    return {
        "W_subjects": W_subjects,
        "W_relations_in": W_relations_in,
        "out_subject_atoms": out_subject_atoms,
        "out_relation_atoms": out_relation_atoms,
        "relation_in_prototypes": relation_in_prototypes,
        "K_kv": K_kv, "y_kv": y_kv, "codebook_kv": codebook_kv, "W_kv": W_kv,
        "subject_to_kv_idx": subject_to_kv_idx,
        "subject_to_template": subject_to_template,
        "templates": templates,
        "kg_node_idxs": kg_node_idxs, "kg_edges": kg_edges,
        "kg_node_vecs": kg_node_vecs, "G_kg": G,
        "V_C_IN": V_C_IN, "V_REL": V_REL,
        "V_C_OUT": V_C_OUT, "V_REL_OUT": V_REL_OUT,
    }


def build_query_corpus(g: np.random.Generator,
                       substrate: Dict[str, Any]) -> List[Dict[str, Any]]:
    W_subjects = substrate["W_subjects"]
    W_relations_in = substrate["W_relations_in"]
    out_subject_atoms = substrate["out_subject_atoms"]
    out_relation_atoms = substrate["out_relation_atoms"]
    V_C_IN_local = substrate["V_C_IN"]
    V_REL_local = substrate["V_REL"]
    V_C_OUT_local = substrate["V_C_OUT"]
    V_REL_OUT_local = substrate["V_REL_OUT"]

    queries: List[Dict[str, Any]] = []

    for _ in range(N_QUERIES_PURE_IN):
        s_i = int(g.integers(0, V_C_IN_local))
        r_i = int(g.integers(0, V_REL_local))
        queries.append({
            "category": "PURE_IN_DOMAIN",
            "subject_vec": add_noise(W_subjects[s_i], FLIP_FRAC_NORMAL, g, N_DIM),
            "relation_vec": add_noise(W_relations_in[r_i], FLIP_FRAC_NORMAL, g, N_DIM),
            "true_subject": s_i, "true_relation": r_i,
            "subject_in_substrate": True, "relation_in_substrate": True,
        })

    for _ in range(N_QUERIES_PURE_OUT):
        s_i = int(g.integers(0, V_C_OUT_local))
        r_i = int(g.integers(0, V_REL_OUT_local))
        queries.append({
            "category": "PURE_OUT_OF_DOMAIN",
            "subject_vec": add_noise(out_subject_atoms[s_i], FLIP_FRAC_NORMAL, g, N_DIM),
            "relation_vec": add_noise(out_relation_atoms[r_i], FLIP_FRAC_NORMAL, g, N_DIM),
            "true_subject": -1, "true_relation": -1,
            "subject_in_substrate": False, "relation_in_substrate": False,
        })

    for _ in range(N_QUERIES_NEAR):
        s_i = int(g.integers(0, V_C_IN_local))
        r_i = int(g.integers(0, V_REL_OUT_local))
        queries.append({
            "category": "NEAR_DOMAIN_MIXED",
            "subject_vec": add_noise(W_subjects[s_i], FLIP_FRAC_NORMAL, g, N_DIM),
            "relation_vec": add_noise(out_relation_atoms[r_i], FLIP_FRAC_NORMAL, g, N_DIM),
            "true_subject": s_i, "true_relation": -1,
            "subject_in_substrate": True, "relation_in_substrate": False,
        })

    for _ in range(N_QUERIES_UNCERTAIN):
        s_i = int(g.integers(0, V_C_IN_local))
        r_i = int(g.integers(0, V_REL_local))
        queries.append({
            "category": "IN_DOMAIN_UNCERTAIN",
            "subject_vec": add_noise(W_subjects[s_i], FLIP_FRAC_UNCERTAIN, g, N_DIM),
            "relation_vec": add_noise(W_relations_in[r_i], FLIP_FRAC_UNCERTAIN, g, N_DIM),
            "true_subject": s_i, "true_relation": r_i,
            "subject_in_substrate": True, "relation_in_substrate": True,
        })

    return queries


# ============================================================================
# Pipeline primitives + ARMs (compact; mirrors stage3 v1)
# ============================================================================

def prim_audit(vec: np.ndarray, W: np.ndarray) -> Tuple[int, float]:
    sims = W @ vec
    best_idx = int(np.argmax(sims))
    return best_idx, float(sims[best_idx])


def prim_intent_classify(rel_vec: np.ndarray, prototypes: np.ndarray) -> Tuple[int, float]:
    sims = prototypes @ rel_vec
    pred = int(np.argmax(sims))
    return pred, float(sims[pred])


def prim_graph_health(substrate: Dict[str, Any]) -> Tuple[float, bool]:
    G = substrate["G_kg"]
    nodes = substrate["kg_node_vecs"]
    edges = substrate["kg_edges"]
    n_kg_nodes = nodes.shape[0]
    eset = set(edges)
    ne_scores: List[float] = []
    need = min(64, len(edges) * 4)
    tries = 0
    while len(ne_scores) < need and tries < need * 10:
        u = tries % n_kg_nodes
        w = (tries * 7 + 13) % n_kg_nodes
        tries += 1
        if u != w and (min(u, w), max(u, w)) not in eset:
            sc = float((G * (nodes[u] * nodes[w])).sum() / N_DIM)
            ne_scores.append(sc)
    if not ne_scores:
        return 0.0, False
    health = float(np.var(ne_scores))
    refuse = health > GRAPH_HEALTH_THR
    return health, bool(refuse)


def prim_kv_retrieve(subj_idx: int, substrate: Dict[str, Any],
                     g: np.random.Generator) -> Tuple[int, float]:
    K_kv = substrate["K_kv"]
    W_kv = substrate["W_kv"]
    codebook_kv = substrate["codebook_kv"]
    kv_idx = int(substrate["subject_to_kv_idx"][subj_idx])
    cue = K_kv[kv_idx] + SIGMA_KV * g.standard_normal(D_KV).astype(np.float32)
    readout = cue @ W_kv.T
    readout_n = readout / (np.linalg.norm(readout) + 1e-8)
    decode_sims = codebook_kv @ readout_n
    pred = int(np.argmax(decode_sims))
    top2 = np.partition(decode_sims, -2)[-2:]
    cleanup_sigma = float(abs(top2[1] - top2[0]))
    return pred, cleanup_sigma


def prim_templated_response(subj_idx: int, rel_idx: int, label: int,
                            substrate: Dict[str, Any]) -> str:
    t_i = int(substrate["subject_to_template"][subj_idx]) if subj_idx >= 0 else 0
    template = substrate["templates"][t_i]
    return "%s [label=%d rel=%d]" % (template, label, rel_idx)


def prim_csp_confidence(retrieval_sigma: float, audit_sim: float,
                        intent_conf: float) -> Tuple[float, int]:
    signal = float(retrieval_sigma + audit_sim + intent_conf)
    iters = int(round(CSP_MAX_ITERS / (1.0 + 4.0 * max(signal, 0.001))))
    iters = min(max(iters, 0), CSP_MAX_ITERS)
    confidence = 1.0 - (iters / max(CSP_MAX_ITERS, 1))
    return float(confidence), iters


def arm_pipeline_composed(q: Dict[str, Any], substrate: Dict[str, Any],
                          g: np.random.Generator,
                          graph_health: Tuple[float, bool]) -> Dict[str, Any]:
    t = time.perf_counter()
    intent_pred, intent_conf = prim_intent_classify(
        q["relation_vec"], substrate["relation_in_prototypes"])
    if intent_conf < INTENT_CONF_THR:
        elapsed_ms = (time.perf_counter() - t) * 1000.0
        return {"refused": True, "refuse_reason": "intent_uncertain",
                "confidence": 0.0, "answer": None, "elapsed_ms": elapsed_ms}
    _, s_sim = prim_audit(q["subject_vec"], substrate["W_subjects"])
    _, r_sim = prim_audit(q["relation_vec"], substrate["W_relations_in"])
    if s_sim < SUBJECT_AUDIT_THR or r_sim < RELATION_AUDIT_THR:
        elapsed_ms = (time.perf_counter() - t) * 1000.0
        reason = "audit_subject" if s_sim < SUBJECT_AUDIT_THR else "audit_relation"
        return {"refused": True, "refuse_reason": reason,
                "confidence": 0.0, "answer": None, "elapsed_ms": elapsed_ms}
    health_val, health_refuse = graph_health
    if health_refuse:
        elapsed_ms = (time.perf_counter() - t) * 1000.0
        return {"refused": True, "refuse_reason": "graph_health",
                "confidence": 0.0, "answer": None, "elapsed_ms": elapsed_ms}
    audit_subj_idx, _ = prim_audit(q["subject_vec"], substrate["W_subjects"])
    kv_pred, kv_sigma = prim_kv_retrieve(audit_subj_idx, substrate, g)
    response = prim_templated_response(audit_subj_idx, intent_pred, kv_pred, substrate)
    confidence, iters = prim_csp_confidence(kv_sigma, s_sim, intent_conf)
    if confidence < (1.0 - CSP_LOWCONF_THR / max(CSP_MAX_ITERS, 1)):
        elapsed_ms = (time.perf_counter() - t) * 1000.0
        return {"refused": True, "refuse_reason": "csp_uncertain",
                "confidence": confidence, "answer": response, "elapsed_ms": elapsed_ms}
    elapsed_ms = (time.perf_counter() - t) * 1000.0
    return {"refused": False, "refuse_reason": None,
            "confidence": confidence, "answer": response, "elapsed_ms": elapsed_ms}


def arm_audit_only_rail(q: Dict[str, Any], substrate: Dict[str, Any],
                        g: np.random.Generator,
                        graph_health: Tuple[float, bool]) -> Dict[str, Any]:
    t = time.perf_counter()
    _, s_sim = prim_audit(q["subject_vec"], substrate["W_subjects"])
    _, r_sim = prim_audit(q["relation_vec"], substrate["W_relations_in"])
    refused = not (s_sim >= SUBJECT_AUDIT_THR and r_sim >= RELATION_AUDIT_THR)
    if refused:
        elapsed_ms = (time.perf_counter() - t) * 1000.0
        return {"refused": True, "refuse_reason": "audit",
                "confidence": 0.0, "answer": None, "elapsed_ms": elapsed_ms}
    audit_subj_idx, _ = prim_audit(q["subject_vec"], substrate["W_subjects"])
    kv_pred, kv_sigma = prim_kv_retrieve(audit_subj_idx, substrate, g)
    response = prim_templated_response(audit_subj_idx, 0, kv_pred, substrate)
    confidence = float(min(1.0, kv_sigma * 4.0))
    elapsed_ms = (time.perf_counter() - t) * 1000.0
    return {"refused": False, "refuse_reason": None,
            "confidence": confidence, "answer": response, "elapsed_ms": elapsed_ms}


def arm_no_refuse_rail(q: Dict[str, Any], substrate: Dict[str, Any],
                       g: np.random.Generator,
                       graph_health: Tuple[float, bool]) -> Dict[str, Any]:
    t = time.perf_counter()
    audit_subj_idx, _ = prim_audit(q["subject_vec"], substrate["W_subjects"])
    kv_pred, kv_sigma = prim_kv_retrieve(audit_subj_idx, substrate, g)
    response = prim_templated_response(audit_subj_idx, 0, kv_pred, substrate)
    confidence = float(min(1.0, kv_sigma * 4.0))
    elapsed_ms = (time.perf_counter() - t) * 1000.0
    return {"refused": False, "refuse_reason": None,
            "confidence": confidence, "answer": response, "elapsed_ms": elapsed_ms}


ARMS = {
    "ARM_PIPELINE_COMPOSED": arm_pipeline_composed,
    "ARM_AUDIT_ONLY_RAIL": arm_audit_only_rail,
    "ARM_NO_REFUSE_RAIL": arm_no_refuse_rail,
}


def is_answer_correct(q: Dict[str, Any], result: Dict[str, Any]) -> bool:
    cat = q["category"]
    expect_answer = CATEGORY_EXPECT_ANSWER[cat]
    if expect_answer is None:
        if result.get("refused"):
            return True
        return result.get("confidence", 1.0) < 0.7
    if expect_answer:
        return not result.get("refused", False)
    return bool(result.get("refused", False))


def evaluate_pipeline_arm(arm_label: str, queries: List[Dict[str, Any]],
                          substrate: Dict[str, Any],
                          g: np.random.Generator) -> Dict[str, Dict[str, Any]]:
    fn = ARMS[arm_label]
    graph_health = prim_graph_health(substrate)
    out: Dict[str, Dict[str, Any]] = {}
    for cat in CATEGORY_LABELS:
        cat_q = [q for q in queries if q["category"] == cat]
        n = len(cat_q)
        n_refused = 0
        n_answered = 0
        n_correct = 0
        confs: List[float] = []
        latencies: List[float] = []
        for q in cat_q:
            r = fn(q, substrate, g, graph_health)
            latencies.append(float(r.get("elapsed_ms", 0.0)))
            confs.append(float(r.get("confidence", 0.0)))
            if r.get("refused"):
                n_refused += 1
            else:
                n_answered += 1
            if is_answer_correct(q, r):
                n_correct += 1
        refuse_rate = n_refused / max(n, 1)
        answer_rate = n_answered / max(n, 1)
        correct_rate = n_correct / max(n, 1)
        avg_conf = float(np.mean(confs)) if confs else 0.0
        out[cat] = {
            "refuse_rate": round(refuse_rate, 4),
            "answer_rate": round(answer_rate, 4),
            "correct_rate": round(correct_rate, 4),
            "avg_confidence": round(avg_conf, 4),
            "latency_p50_ms": round(float(np.median(latencies)) if latencies else 0.0, 3),
            "latency_p95_ms": round(float(np.percentile(latencies, 95)) if latencies else 0.0, 3),
            "n_total": n,
        }
    return out


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    g = np.random.default_rng(0)
    # T1: bipolar unit-norm
    x = bipolar(5, 64, g)
    norms = np.linalg.norm(x, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-3)
    print("[selftest] T1 PASS: bipolar unit-norm")

    # T2: build substrate at tiny scale (V_C_IN=20, V_REL=4)
    global N_DIM
    orig_N = N_DIM
    N_DIM = 512
    try:
        s = build_substrate(np.random.default_rng(1), V_C_IN=20, V_REL=4)
        assert s["W_subjects"].shape == (20, N_DIM)
        assert s["W_relations_in"].shape == (4, N_DIM)
        assert s["W_kv"].shape == (D_KV, D_KV)
        print("[selftest] T2 PASS: substrate shapes correct at V_C_IN=20 V_REL=4")

        # T3: queries at tiny scale
        # Patch query counts at module-scope for selftest only
        global N_QUERIES_PURE_IN, N_QUERIES_PURE_OUT, N_QUERIES_NEAR, N_QUERIES_UNCERTAIN
        orig_qs = (N_QUERIES_PURE_IN, N_QUERIES_PURE_OUT, N_QUERIES_NEAR, N_QUERIES_UNCERTAIN)
        N_QUERIES_PURE_IN = 5
        N_QUERIES_PURE_OUT = 5
        N_QUERIES_NEAR = 5
        N_QUERIES_UNCERTAIN = 5
        try:
            qs = build_query_corpus(np.random.default_rng(2), s)
            assert len(qs) == 20
            for cat in CATEGORY_LABELS:
                assert sum(1 for q in qs if q["category"] == cat) == 5
            print("[selftest] T3 PASS: 4 categories x 5 queries each")

            # T4: pipeline runs end-to-end on each query
            gh = prim_graph_health(s)
            g_arm = np.random.default_rng(11)
            for q in qs[:5]:
                r = arm_pipeline_composed(q, s, g_arm, gh)
                assert "refused" in r and "elapsed_ms" in r
            print("[selftest] T4 PASS: pipeline runs on 5 test queries")

            # T5: PURE_OUT_OF_DOMAIN should refuse most queries at tiny scale
            per_arm = evaluate_pipeline_arm("ARM_PIPELINE_COMPOSED", qs, s, g_arm)
            pure_out = per_arm["PURE_OUT_OF_DOMAIN"]
            assert pure_out["refuse_rate"] >= 0.40, \
                "T5 OOD refuse=%.3f too low" % pure_out["refuse_rate"]
            print("[selftest] T5 PASS: OOD refuse_rate=%.3f at tiny scale"
                  % pure_out["refuse_rate"])
        finally:
            (N_QUERIES_PURE_IN, N_QUERIES_PURE_OUT, N_QUERIES_NEAR,
             N_QUERIES_UNCERTAIN) = orig_qs
    finally:
        N_DIM = orig_N

    # T6: LLM counter
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T6 PASS: LLM counter = 0")
    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ============================================================================
# Per-seed run
# ============================================================================

def run_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "M_KV": M_KV,
        "operating_points": OPERATING_POINTS,
        "n_queries_per_cat": dict(N_QUERIES_PER_CAT),
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "per_operating_point": {},
    }

    for (V_C_IN, V_REL) in OPERATING_POINTS:
        pt_key = "V_C_IN_%d_V_REL_%d" % (V_C_IN, V_REL)
        t_pt = time.time()
        g = np.random.default_rng(seed * 1009 + V_C_IN * 7 + V_REL * 11)
        substrate = build_substrate(g, V_C_IN=V_C_IN, V_REL=V_REL)
        queries = build_query_corpus(g, substrate)
        print("  [seed=%d %s] substrate built; n_queries=%d (V_C_OUT=%d V_REL_OUT=%d)"
              % (seed, pt_key, len(queries), substrate["V_C_OUT"],
                 substrate["V_REL_OUT"]), flush=True)

        pt_out: Dict[str, Any] = {"V_C_IN": V_C_IN, "V_REL": V_REL}
        for arm_label in ARMS.keys():
            t_arm = time.time()
            g_arm = np.random.default_rng(seed * 1009 + V_C_IN + V_REL + hash(arm_label) % 100003)
            per_cat = evaluate_pipeline_arm(arm_label, queries, substrate, g_arm)
            pt_out[arm_label.lower()] = {
                "per_category": per_cat,
                "elapsed_s_arm": round(time.time() - t_arm, 2),
            }
            line = " | ".join("%s[ref=%.3f ans=%.3f corr=%.3f p95=%.2fms]" %
                              (cat, per_cat[cat]["refuse_rate"], per_cat[cat]["answer_rate"],
                               per_cat[cat]["correct_rate"],
                               per_cat[cat]["latency_p95_ms"])
                              for cat in CATEGORY_LABELS)
            print("    [arm=%s] %s t=%.1fs" % (arm_label, line, time.time() - t_arm),
                  flush=True)

        pt_out["elapsed_s_point"] = round(time.time() - t_pt, 1)
        out["per_operating_point"][pt_key] = pt_out
        print("  [seed=%d %s] DONE t=%.1fs" % (seed, pt_key, pt_out["elapsed_s_point"]),
              flush=True)

    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


# ============================================================================
# Verdict
# ============================================================================

def _point_arm_cat(per_seed: List[Dict[str, Any]], pt_key: str,
                    arm_key: str, cat: str, metric: str) -> float:
    vals = []
    for p in per_seed:
        try:
            v = p["per_operating_point"][pt_key][arm_key]["per_category"][cat][metric]
            if isinstance(v, (int, float)) and not math.isnan(v):
                vals.append(float(v))
        except (KeyError, TypeError):
            continue
    return float(np.mean(vals)) if vals else float("nan")


def _point_arm_cat_cv(per_seed: List[Dict[str, Any]], pt_key: str,
                       arm_key: str, cat: str, metric: str) -> float:
    vals = []
    for p in per_seed:
        try:
            v = p["per_operating_point"][pt_key][arm_key]["per_category"][cat][metric]
            if isinstance(v, (int, float)) and not math.isnan(v):
                vals.append(float(v))
        except (KeyError, TypeError):
            continue
    if len(vals) < 2:
        return 0.0
    m = float(np.mean(vals))
    return float(np.std(vals) / max(abs(m), 1e-9))


def compute_verdict(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    pk = "arm_pipeline_composed"
    # Summarize each operating point
    summaries = {}
    for (V_C_IN, V_REL) in OPERATING_POINTS:
        pt_key = "V_C_IN_%d_V_REL_%d" % (V_C_IN, V_REL)
        in_ans = _point_arm_cat(per_seed, pt_key, pk, "PURE_IN_DOMAIN", "answer_rate")
        out_ref = _point_arm_cat(per_seed, pt_key, pk, "PURE_OUT_OF_DOMAIN", "refuse_rate")
        near_ref = _point_arm_cat(per_seed, pt_key, pk, "NEAR_DOMAIN_MIXED", "refuse_rate")
        uncert_corr = _point_arm_cat(per_seed, pt_key, pk, "IN_DOMAIN_UNCERTAIN", "correct_rate")
        p95 = _point_arm_cat(per_seed, pt_key, pk, "PURE_IN_DOMAIN", "latency_p95_ms")
        cv = _point_arm_cat_cv(per_seed, pt_key, pk, "PURE_IN_DOMAIN", "answer_rate")
        summaries[pt_key] = {
            "in_ans": in_ans, "out_ref": out_ref, "near_ref": near_ref,
            "uncert_corr": uncert_corr, "p95_ms": p95, "cv": cv,
        }

    summ = " | ".join("%s: in_ans=%.3f out_ref=%.3f near_ref=%.3f uncert_corr=%.3f p95=%.2fms cv=%.3f" % (
        pt, s["in_ans"], s["out_ref"], s["near_ref"], s["uncert_corr"], s["p95_ms"], s["cv"]
    ) for pt, s in summaries.items())

    # HARD_FAIL_LATENCY_BLOWN
    for pt_key, s in summaries.items():
        if s["p95_ms"] > HF_LATENCY_BLOWN_MS:
            return ("HARD_FAIL_LATENCY_BLOWN",
                    "HARD_FAIL_LATENCY_BLOWN at %s: p95=%.2fms > %.1fms | %s" % (
                        pt_key, s["p95_ms"], HF_LATENCY_BLOWN_MS, summ))

    # HARD_FAIL_REFUSE_GATE_CLIFF: any point at V_REL >= 20 with near_ref < 0.50
    for (V_C_IN, V_REL) in OPERATING_POINTS:
        if V_REL >= 20:
            pt_key = "V_C_IN_%d_V_REL_%d" % (V_C_IN, V_REL)
            near_ref = summaries[pt_key]["near_ref"]
            if not math.isnan(near_ref) and near_ref < HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20:
                return ("HARD_FAIL_REFUSE_GATE_CLIFF",
                        "HARD_FAIL_REFUSE_GATE_CLIFF at %s: near_ref=%.3f < %.2f | %s" % (
                            pt_key, near_ref, HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20, summ))

    # HARD_PASS_PRODUCTION_SCALE at TARGET_POINT
    target_key = "V_C_IN_%d_V_REL_%d" % TARGET_POINT
    if target_key in summaries:
        t = summaries[target_key]
        if (t["in_ans"] >= HP_PURE_IN_ANSWER_MIN
                and t["out_ref"] >= HP_PURE_OUT_REFUSE_MIN
                and t["near_ref"] >= HP_NEAR_REFUSE_MIN
                and t["uncert_corr"] >= HP_UNCERTAIN_CORR_MIN
                and t["p95_ms"] <= HP_LATENCY_P95_MS
                and t["cv"] <= HP_CV_MAX):
            return ("HARD_PASS_PRODUCTION_SCALE",
                    "HARD_PASS_PRODUCTION_SCALE at %s | %s" % (target_key, summ))

    # CHAIN_GRADE_AT_LOWER_X: passes at one of the 3 sub-production points
    sub_points = [pt for pt in OPERATING_POINTS if pt != TARGET_POINT]
    passing_sub = []
    for (V_C_IN, V_REL) in sub_points:
        pt_key = "V_C_IN_%d_V_REL_%d" % (V_C_IN, V_REL)
        if pt_key not in summaries:
            continue
        t = summaries[pt_key]
        if (t["in_ans"] >= HP_PURE_IN_ANSWER_MIN
                and t["out_ref"] >= HP_PURE_OUT_REFUSE_MIN
                and t["near_ref"] >= HP_NEAR_REFUSE_MIN
                and t["uncert_corr"] >= HP_UNCERTAIN_CORR_MIN
                and t["p95_ms"] <= HP_LATENCY_P95_MS
                and t["cv"] <= HP_CV_MAX):
            passing_sub.append(pt_key)
    if passing_sub:
        return ("CHAIN_GRADE_AT_LOWER_X",
                "CHAIN_GRADE_AT_LOWER_X passes at %s but not (V_C_IN=%d V_REL=%d) | %s" % (
                    ",".join(passing_sub), TARGET_POINT[0], TARGET_POINT[1], summ))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND production-scale audit-device partial: no point hit HP bar | %s" % summ)


# ============================================================================
# atexit
# ============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        v, vmsg = compute_verdict(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d operating_points=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, OPERATING_POINTS, CONFIG_VERSION),
          flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = compute_verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "EXT-1 Stage 3 integrated audit-device at production V. Extends v1 "
            "(chain-grade at V_C_IN=600 V_REL=8 M_KV=10k) to 4 production-scale "
            "operating points (V_C_IN x V_REL in {1000,2000} x {20,50}) at N=8192 "
            "M_KV=10k. Target = (2000, 50); CHAIN_GRADE_AT_LOWER_X if any of the "
            "3 sub-production points passes. Per-arm per-category per-point "
            "metrics reported. Substrate-only; zero LLM forward calls."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
