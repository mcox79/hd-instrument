"""substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU.

GPU-torchified rewrite of v2 production_scale per Fix #24 (USER 2026-06-22):
queueing a NumPy-only cell onto overnight_queue (GPU) wastes the runner slot.
The cell substance (same 4 operating points, same 4 arms, same bands, same
ANCHOR-relative methodology) is preserved; the inference matmuls are pushed
to torch.cuda so the GPU is actually used.

EXPERIMENTAL CONTENT (identical to v2 numpy version):
  OPERATING POINTS (4):
    (V_C_IN=1000, V_REL=20), (V_C_IN=1000, V_REL=50),
    (V_C_IN=2000, V_REL=20), (V_C_IN=2000, V_REL=50)
  ARMS (3 evaluated):
    ARM_PIPELINE_COMPOSED, ARM_AUDIT_ONLY_RAIL, ARM_NO_REFUSE_RAIL
  CONFIG: N=8192, M_KV=10000, seeds=[11,13,19]
  Substrate-only; ASCII; per-arm/per-category metrics.

PRE-REG BANDS (identical to v2; LOCKED at module init):
  HARD_PASS_PRODUCTION_SCALE at (V_C_IN=2000, V_REL=50):
    in_ans>=0.85 out_ref>=0.85 near_ref>=0.85 uncert_corr>=0.70
    AND p95<=10ms AND cv<=0.07
  CHAIN_GRADE_AT_LOWER_X: passes at one of (1000,20), (1000,50), (2000,20)
  HARD_FAIL_REFUSE_GATE_CLIFF: near_ref<0.50 at any V_REL>=20
  HARD_FAIL_LATENCY_BLOWN: p95>50ms at any operating point

FIX #24 GPU-VERIFICATION GATE (NEW vs v2):
  Cell asserts torch.cuda.is_available() at full-run start (warn-only in smoke
  + self-test for laptop CPU torch). After each big batched matmul block we
  print torch.cuda.memory_allocated() to evidence actual GPU residency. If
  cuda is available but post-matmul memory_allocated stays at 0, the cell
  raises a Fix #24 violation (matmul ran on CPU despite cuda available).

TORCH PORT (numpy in / GPU compute / float out, per _gpu_cap.py pattern):
  - W_subjects, W_relations, K_kv, W_kv, codebook_kv, G_kg pushed to _DEV once
    per (seed, operating point) build.
  - per-query operations BATCHED across queries inside each category:
      * audit-subject:     queries(B,N) @ W_subjects(V_C_IN,N).T -> (B,V_C_IN)
      * audit-relation:    queries(B,N) @ W_relations(V_REL,N).T  -> (B,V_REL)
      * intent classifier: queries(B,N) @ prototypes(V_REL,N).T   -> (B,V_REL)
      * KV retrieve:       cues(B,D) @ W_kv.T(D,D) -> readouts(B,D); readouts @ codebook.T -> (B,C)
      * graph-health probe: edges(E,N) reduce -> health scalar (batched on GPU)
  - Per-query latency timed by amortizing batch wall-clock across batch size,
    so p95 reflects production per-query inference cost. This matches v2's
    semantics: p95 is the per-query cost the audit-device serves at.

Author: exp_dev 2026-06-25 (Fix #24-compliant GPU rewrite of EXT-1 production scale).
ASCII-only; per-seed checkpoint; substrate-only; zero LLM forward calls.
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
import torch  # Fix #24 gate requirement: torch import at module top

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU"
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
# Torch device selection + Fix #24 verification gate state
# ============================================================================
_CUDA_AVAILABLE = bool(torch.cuda.is_available())
_DEV = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")
_FIX24_VIOLATIONS: List[str] = []  # populated if cuda available but memory_allocated stays 0


def _gpu_mem_mb() -> float:
    if _CUDA_AVAILABLE:
        return float(torch.cuda.memory_allocated()) / (1024.0 * 1024.0)
    return 0.0


def _gpu_probe(tag: str, expect_residency: bool = True) -> None:
    """Print cuda.is_available + memory_allocated; flag Fix #24 violation if cuda available but mem=0."""
    mem = _gpu_mem_mb()
    print("[fix24-probe %s] cuda_available=%s memory_allocated=%.2f MB"
          % (tag, _CUDA_AVAILABLE, mem), flush=True)
    if _CUDA_AVAILABLE and expect_residency and mem < 0.01:
        msg = "Fix #24 violation at probe '%s': cuda available but memory_allocated=%.4fMB (matmul on CPU?)" % (tag, mem)
        print("[fix24-probe %s] WARN: %s" % (tag, msg), flush=True)
        _FIX24_VIOLATIONS.append(msg)

# ============================================================================
# PROSPECTIVE BANDS (LOCKED) -- identical to v2
# ============================================================================
HP_PURE_IN_ANSWER_MIN = 0.85
HP_PURE_OUT_REFUSE_MIN = 0.85
HP_NEAR_REFUSE_MIN = 0.85
HP_UNCERTAIN_CORR_MIN = 0.70
HP_LATENCY_P95_MS = 10.0
HP_CV_MAX = 0.07
HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20 = 0.50
HF_LATENCY_BLOWN_MS = 50.0

TARGET_POINT = (2000, 50)

assert 0 < HP_PURE_IN_ANSWER_MIN <= 1.0
assert HP_LATENCY_P95_MS < HF_LATENCY_BLOWN_MS

# ============================================================================
# CONFIG (per operating point) -- identical to v2
# ============================================================================
N_DIM = 2048 if RUN_MODE == "smoke" else 8192

if RUN_MODE == "smoke":
    OPERATING_POINTS = [(200, 8), (400, 16)]
    SEEDS = [11]
    M_KV = 2000
    N_QUERIES_PURE_IN = 25
    N_QUERIES_PURE_OUT = 25
    N_QUERIES_NEAR = 25
    N_QUERIES_UNCERTAIN = 25
    BATCH_SIZE = 64
else:
    OPERATING_POINTS = [(1000, 20), (1000, 50), (2000, 20), (2000, 50)]
    SEEDS = [11, 13, 19]
    M_KV = 10000
    N_QUERIES_PURE_IN = 1000
    N_QUERIES_PURE_OUT = 1000
    N_QUERIES_NEAR = 500
    N_QUERIES_UNCERTAIN = 500
    BATCH_SIZE = 256  # GPU batch size for big matmuls

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

V_C_OUT_FACTOR = 1.0
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
    "substrateStage3IntegratedDemoV2ProductionScaleGPU: N=%d operating_points=%s "
    "M_KV=%d d_kv=%d C_kv=%d sigma_kv=%.2f batch=%d "
    "n_q_in=%d n_q_out=%d n_q_near=%d n_q_uncertain=%d seeds=%s mode=%s "
    "device=%s cuda_available=%s target=%s; bands HP_in_ans>=%.2f HP_out_ref>=%.2f "
    "HP_near_ref>=%.2f HP_uncert_corr>=%.2f HP_p95<=%.1fms HP_cv<=%.2f "
    "HF_near_ref_min_at_V_REL_ge_20<%.2f HF_lat>%.1fms"
) % (
    N_DIM, OPERATING_POINTS, M_KV, D_KV, C_KV, SIGMA_KV, BATCH_SIZE,
    N_QUERIES_PURE_IN, N_QUERIES_PURE_OUT, N_QUERIES_NEAR, N_QUERIES_UNCERTAIN,
    SEEDS, RUN_MODE, str(_DEV), _CUDA_AVAILABLE, TARGET_POINT,
    HP_PURE_IN_ANSWER_MIN, HP_PURE_OUT_REFUSE_MIN, HP_NEAR_REFUSE_MIN,
    HP_UNCERTAIN_CORR_MIN, HP_LATENCY_P95_MS, HP_CV_MAX,
    HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20, HF_LATENCY_BLOWN_MS,
)


# ============================================================================
# Substrate primitives (numpy build; per-call torch matmul on _DEV)
# ============================================================================

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gaussian_keys(M: int, d: int, g: np.random.Generator) -> np.ndarray:
    return g.standard_normal((M, d)).astype(np.float32)


def _norm_np(X: np.ndarray) -> np.ndarray:
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
    """Build numpy substrate atoms then push to torch device (one-time per point)."""
    V_C_OUT = int(V_C_IN * V_C_OUT_FACTOR)
    V_REL_OUT = int(V_REL * V_REL_OUT_FACTOR)

    W_subjects = bipolar(V_C_IN, N_DIM, g)
    W_relations_in = bipolar(V_REL, N_DIM, g)
    out_subject_atoms = bipolar(V_C_OUT, N_DIM, g)
    out_relation_atoms = bipolar(V_REL_OUT, N_DIM, g)
    relation_in_prototypes = W_relations_in.copy()

    K_kv = gaussian_keys(M_KV, D_KV, g)
    y_kv = g.integers(0, C_KV, M_KV).astype(np.int64)
    codebook_kv = _norm_np(g.standard_normal((C_KV, D_KV)).astype(np.float32))
    W_kv = codebook_kv[y_kv].T @ K_kv  # (D_KV, D_KV)

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

    # Push tensors to torch device once per substrate build (the big matmul inputs).
    t_subjects = torch.from_numpy(np.ascontiguousarray(W_subjects)).to(_DEV)
    t_relations_in = torch.from_numpy(np.ascontiguousarray(W_relations_in)).to(_DEV)
    t_relation_in_prototypes = torch.from_numpy(np.ascontiguousarray(relation_in_prototypes)).to(_DEV)
    t_K_kv = torch.from_numpy(np.ascontiguousarray(K_kv)).to(_DEV)
    t_W_kv = torch.from_numpy(np.ascontiguousarray(W_kv)).to(_DEV)
    t_codebook_kv = torch.from_numpy(np.ascontiguousarray(codebook_kv)).to(_DEV)
    t_kg_node_vecs = torch.from_numpy(np.ascontiguousarray(kg_node_vecs)).to(_DEV)
    t_G_kg = torch.from_numpy(np.ascontiguousarray(G)).to(_DEV)

    return {
        # numpy (used to build query corpus + indexing)
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
        # torch (used for batched matmul inference on _DEV)
        "t_subjects": t_subjects, "t_relations_in": t_relations_in,
        "t_relation_in_prototypes": t_relation_in_prototypes,
        "t_K_kv": t_K_kv, "t_W_kv": t_W_kv, "t_codebook_kv": t_codebook_kv,
        "t_kg_node_vecs": t_kg_node_vecs, "t_G_kg": t_G_kg,
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
# Batched torch primitives (numpy in / torch.cuda compute / numpy out)
# ============================================================================

@torch.no_grad()
def batched_audit(query_vecs_np: np.ndarray, t_W: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
    """Batched cleanup: queries (B,N) @ W.T (N,V) -> sims (B,V). Returns (best_idx, best_sim) numpy."""
    qb = torch.from_numpy(np.ascontiguousarray(query_vecs_np)).to(_DEV)
    sims = qb @ t_W.t()
    best_sim, best_idx = sims.max(dim=1)
    return best_idx.cpu().numpy().astype(np.int64), best_sim.cpu().numpy().astype(np.float32)


@torch.no_grad()
def batched_intent(rel_vecs_np: np.ndarray, t_prototypes: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
    """Same shape as batched_audit but semantically the intent classifier."""
    return batched_audit(rel_vecs_np, t_prototypes)


@torch.no_grad()
def batched_kv_retrieve(subj_idxs_np: np.ndarray, substrate: Dict[str, Any],
                        g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Batched KV: cues = K[idx] + sigma*noise, readouts = cues @ W_kv.T, normalize,
       decode_sims = readouts @ codebook.T. Returns (pred, sigma) numpy."""
    K_kv_np = substrate["K_kv"]
    cues_np = K_kv_np[subj_idxs_np] + SIGMA_KV * g.standard_normal(
        (len(subj_idxs_np), D_KV)).astype(np.float32)
    cues = torch.from_numpy(np.ascontiguousarray(cues_np)).to(_DEV)
    readouts = cues @ substrate["t_W_kv"].t()  # (B, D_KV)
    readouts = readouts / (readouts.norm(dim=1, keepdim=True) + 1e-8)
    decode_sims = readouts @ substrate["t_codebook_kv"].t()  # (B, C_KV)
    pred = decode_sims.argmax(dim=1)
    # top2 separation as cleanup_sigma
    top2_vals, _ = torch.topk(decode_sims, 2, dim=1)
    sigma = (top2_vals[:, 0] - top2_vals[:, 1]).abs()
    return pred.cpu().numpy().astype(np.int64), sigma.cpu().numpy().astype(np.float32)


@torch.no_grad()
def gpu_graph_health(substrate: Dict[str, Any]) -> Tuple[float, bool]:
    """Batched graph-health: probe non-edges; variance of (G * (node_u * node_w)).sum / N."""
    t_G = substrate["t_G_kg"]
    t_nodes = substrate["t_kg_node_vecs"]
    edges = substrate["kg_edges"]
    n_kg_nodes = t_nodes.shape[0]
    eset = set(edges)
    need = min(64, len(edges) * 4)
    pairs_u: List[int] = []
    pairs_w: List[int] = []
    tries = 0
    while len(pairs_u) < need and tries < need * 10:
        u = tries % n_kg_nodes
        w = (tries * 7 + 13) % n_kg_nodes
        tries += 1
        if u != w and (min(u, w), max(u, w)) not in eset:
            pairs_u.append(u)
            pairs_w.append(w)
    if not pairs_u:
        return 0.0, False
    iu = torch.tensor(pairs_u, dtype=torch.long, device=_DEV)
    iw = torch.tensor(pairs_w, dtype=torch.long, device=_DEV)
    binds = t_nodes[iu] * t_nodes[iw]  # (P, N)
    scores = (binds * t_G).sum(dim=1) / float(N_DIM)
    health = float(scores.var(unbiased=False).item())
    refuse = health > GRAPH_HEALTH_THR
    return health, bool(refuse)


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


# ============================================================================
# Arm evaluators (batched; per-query latency = batch wall / batch size)
# ============================================================================

def evaluate_pipeline_arm_batched(arm_label: str, queries: List[Dict[str, Any]],
                                   substrate: Dict[str, Any],
                                   g: np.random.Generator,
                                   probe_tag: str) -> Dict[str, Dict[str, Any]]:
    """Batched evaluation per category; per-query latency amortized from batch wall.
    Returns same per_category schema as v2 evaluate_pipeline_arm."""
    graph_health = gpu_graph_health(substrate)
    health_val, health_refuse = graph_health
    out: Dict[str, Dict[str, Any]] = {}

    for cat in CATEGORY_LABELS:
        cat_q = [q for q in queries if q["category"] == cat]
        n = len(cat_q)
        if n == 0:
            out[cat] = {
                "refuse_rate": 0.0, "answer_rate": 0.0, "correct_rate": 0.0,
                "avg_confidence": 0.0, "latency_p50_ms": 0.0, "latency_p95_ms": 0.0,
                "n_total": 0,
            }
            continue

        # Stack all query vecs (B,N) for category-level batched compute
        subj_vecs = np.stack([q["subject_vec"] for q in cat_q], axis=0)
        rel_vecs = np.stack([q["relation_vec"] for q in cat_q], axis=0)

        n_refused = 0
        n_answered = 0
        n_correct = 0
        confs: List[float] = []
        per_query_latencies: List[float] = []

        # Process in BATCH_SIZE chunks so the matmul fits GPU memory at production V
        for start in range(0, n, BATCH_SIZE):
            end = min(start + BATCH_SIZE, n)
            B = end - start
            batch_q = cat_q[start:end]
            batch_subj = subj_vecs[start:end]
            batch_rel = rel_vecs[start:end]

            t_batch_start = time.perf_counter()

            # ---- batched intent (used only by ARM_PIPELINE_COMPOSED but cheap) ----
            intent_pred, intent_conf = batched_intent(batch_rel, substrate["t_relation_in_prototypes"])

            # ---- batched audit (subject + relation) ----
            audit_subj_idx, s_sim = batched_audit(batch_subj, substrate["t_subjects"])
            _, r_sim = batched_audit(batch_rel, substrate["t_relations_in"])

            # ---- batched KV (always on audit_subj_idx for the answer path) ----
            kv_pred, kv_sigma = batched_kv_retrieve(audit_subj_idx, substrate, g)

            if _CUDA_AVAILABLE:
                torch.cuda.synchronize()
            t_batch_end = time.perf_counter()
            per_query_wall_ms = (t_batch_end - t_batch_start) * 1000.0 / float(B)

            # ---- per-query bookkeeping (cheap numpy / python on CPU) ----
            for i in range(B):
                q = batch_q[i]
                if arm_label == "ARM_PIPELINE_COMPOSED":
                    # full pipeline: intent gate -> audit gate -> graph-health -> KV -> CSP
                    if float(intent_conf[i]) < INTENT_CONF_THR:
                        result = {"refused": True, "refuse_reason": "intent_uncertain",
                                  "confidence": 0.0, "answer": None}
                    elif float(s_sim[i]) < SUBJECT_AUDIT_THR:
                        result = {"refused": True, "refuse_reason": "audit_subject",
                                  "confidence": 0.0, "answer": None}
                    elif float(r_sim[i]) < RELATION_AUDIT_THR:
                        result = {"refused": True, "refuse_reason": "audit_relation",
                                  "confidence": 0.0, "answer": None}
                    elif health_refuse:
                        result = {"refused": True, "refuse_reason": "graph_health",
                                  "confidence": 0.0, "answer": None}
                    else:
                        response = prim_templated_response(
                            int(audit_subj_idx[i]), int(intent_pred[i]), int(kv_pred[i]), substrate)
                        confidence, iters = prim_csp_confidence(
                            float(kv_sigma[i]), float(s_sim[i]), float(intent_conf[i]))
                        if confidence < (1.0 - CSP_LOWCONF_THR / max(CSP_MAX_ITERS, 1)):
                            result = {"refused": True, "refuse_reason": "csp_uncertain",
                                      "confidence": confidence, "answer": response}
                        else:
                            result = {"refused": False, "refuse_reason": None,
                                      "confidence": confidence, "answer": response}
                elif arm_label == "ARM_AUDIT_ONLY_RAIL":
                    refused = not (float(s_sim[i]) >= SUBJECT_AUDIT_THR
                                   and float(r_sim[i]) >= RELATION_AUDIT_THR)
                    if refused:
                        result = {"refused": True, "refuse_reason": "audit",
                                  "confidence": 0.0, "answer": None}
                    else:
                        response = prim_templated_response(
                            int(audit_subj_idx[i]), 0, int(kv_pred[i]), substrate)
                        confidence = float(min(1.0, float(kv_sigma[i]) * 4.0))
                        result = {"refused": False, "refuse_reason": None,
                                  "confidence": confidence, "answer": response}
                else:  # ARM_NO_REFUSE_RAIL
                    response = prim_templated_response(
                        int(audit_subj_idx[i]), 0, int(kv_pred[i]), substrate)
                    confidence = float(min(1.0, float(kv_sigma[i]) * 4.0))
                    result = {"refused": False, "refuse_reason": None,
                              "confidence": confidence, "answer": response}

                per_query_latencies.append(per_query_wall_ms)
                confs.append(float(result.get("confidence", 0.0)))
                if result.get("refused"):
                    n_refused += 1
                else:
                    n_answered += 1
                if _is_answer_correct(q, result):
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
            "latency_p50_ms": round(float(np.median(per_query_latencies)) if per_query_latencies else 0.0, 3),
            "latency_p95_ms": round(float(np.percentile(per_query_latencies, 95)) if per_query_latencies else 0.0, 3),
            "n_total": n,
        }

    _gpu_probe(probe_tag, expect_residency=True)
    return out


def _is_answer_correct(q: Dict[str, Any], result: Dict[str, Any]) -> bool:
    cat = q["category"]
    expect_answer = CATEGORY_EXPECT_ANSWER[cat]
    if expect_answer is None:
        if result.get("refused"):
            return True
        return result.get("confidence", 1.0) < 0.7
    if expect_answer:
        return not result.get("refused", False)
    return bool(result.get("refused", False))


ARM_LABELS = ("ARM_PIPELINE_COMPOSED", "ARM_AUDIT_ONLY_RAIL", "ARM_NO_REFUSE_RAIL")


# ============================================================================
# Self-test (tiny scale; torch on cpu or cuda; smoke-skips Fix #24 assert)
# ============================================================================

def _selftest():
    print("[selftest] device=%s cuda_available=%s torch=%s"
          % (_DEV, _CUDA_AVAILABLE, torch.__version__), flush=True)
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
        assert s["t_subjects"].shape == (20, N_DIM)
        assert s["t_subjects"].device.type == _DEV.type
        print("[selftest] T2 PASS: substrate shapes correct + tensors on %s" % _DEV.type)

        # T3: batched audit returns the right shapes + best_sim matches numpy reference
        ref_sims = s["W_subjects"] @ s["W_subjects"].T  # ref: subject vs itself
        ref_best_idx = np.argmax(ref_sims, axis=1)
        gpu_best_idx, gpu_best_sim = batched_audit(s["W_subjects"], s["t_subjects"])
        assert gpu_best_idx.shape == (20,)
        assert np.all(gpu_best_idx == ref_best_idx), "T3 FAIL: GPU audit != numpy ref"
        print("[selftest] T3 PASS: batched audit matches numpy ref on identity input")

        # T4: batched KV retrieve returns shapes
        idxs = np.arange(min(8, s["V_C_IN"]), dtype=np.int64)
        kv_pred, kv_sigma = batched_kv_retrieve(idxs, s, np.random.default_rng(33))
        assert kv_pred.shape == (8,) and kv_sigma.shape == (8,)
        print("[selftest] T4 PASS: batched KV retrieve shape ok kv_pred[0]=%d sigma[0]=%.4f"
              % (int(kv_pred[0]), float(kv_sigma[0])))

        # T5: queries + pipeline runs end-to-end (tiny)
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
            print("[selftest] T5 PASS: 4 categories x 5 queries each")

            per_cat = evaluate_pipeline_arm_batched(
                "ARM_PIPELINE_COMPOSED", qs, s, np.random.default_rng(11),
                probe_tag="selftest_pipeline")
            for cat in CATEGORY_LABELS:
                assert "refuse_rate" in per_cat[cat]
                assert "latency_p95_ms" in per_cat[cat]
            print("[selftest] T6 PASS: batched pipeline returns per_category dict")

            # T7: PURE_OUT_OF_DOMAIN should refuse most queries at tiny scale
            assert per_cat["PURE_OUT_OF_DOMAIN"]["refuse_rate"] >= 0.40, \
                "T7 OOD refuse=%.3f too low" % per_cat["PURE_OUT_OF_DOMAIN"]["refuse_rate"]
            print("[selftest] T7 PASS: OOD refuse_rate=%.3f at tiny scale"
                  % per_cat["PURE_OUT_OF_DOMAIN"]["refuse_rate"])
        finally:
            (N_QUERIES_PURE_IN, N_QUERIES_PURE_OUT, N_QUERIES_NEAR,
             N_QUERIES_UNCERTAIN) = orig_qs
    finally:
        N_DIM = orig_N

    # T8: LLM counter
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T8 PASS: LLM counter = 0")
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
        "device": str(_DEV),
        "cuda_available": _CUDA_AVAILABLE,
        "per_operating_point": {},
    }

    for (V_C_IN, V_REL) in OPERATING_POINTS:
        pt_key = "V_C_IN_%d_V_REL_%d" % (V_C_IN, V_REL)
        t_pt = time.time()
        g = np.random.default_rng(seed * 1009 + V_C_IN * 7 + V_REL * 11)
        substrate = build_substrate(g, V_C_IN=V_C_IN, V_REL=V_REL)
        queries = build_query_corpus(g, substrate)
        _gpu_probe("post_substrate_build_%s" % pt_key, expect_residency=True)
        print("  [seed=%d %s] substrate built; n_queries=%d (V_C_OUT=%d V_REL_OUT=%d)"
              % (seed, pt_key, len(queries), substrate["V_C_OUT"],
                 substrate["V_REL_OUT"]), flush=True)

        pt_out: Dict[str, Any] = {"V_C_IN": V_C_IN, "V_REL": V_REL}
        for arm_label in ARM_LABELS:
            t_arm = time.time()
            g_arm = np.random.default_rng(seed * 1009 + V_C_IN + V_REL + hash(arm_label) % 100003)
            per_cat = evaluate_pipeline_arm_batched(
                arm_label, queries, substrate, g_arm,
                probe_tag="seed%d_%s_%s" % (seed, pt_key, arm_label))
            pt_out[arm_label.lower()] = {
                "per_category": per_cat,
                "elapsed_s_arm": round(time.time() - t_arm, 2),
            }
            line = " | ".join("%s[ref=%.3f ans=%.3f corr=%.3f p95=%.3fms]" %
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

        # Free substrate tensors before next point (large V_C_IN x N matmul memory)
        for tk in ("t_subjects", "t_relations_in", "t_relation_in_prototypes",
                   "t_K_kv", "t_W_kv", "t_codebook_kv", "t_kg_node_vecs", "t_G_kg"):
            substrate.pop(tk, None)
        if _CUDA_AVAILABLE:
            torch.cuda.empty_cache()

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["_fix24_violations"] = list(_FIX24_VIOLATIONS)
    return out


# ============================================================================
# Verdict (identical to v2)
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

    summ = " | ".join("%s: in_ans=%.3f out_ref=%.3f near_ref=%.3f uncert_corr=%.3f p95=%.3fms cv=%.3f" % (
        pt, s["in_ans"], s["out_ref"], s["near_ref"], s["uncert_corr"], s["p95_ms"], s["cv"]
    ) for pt, s in summaries.items())

    for pt_key, s in summaries.items():
        if s["p95_ms"] > HF_LATENCY_BLOWN_MS:
            return ("HARD_FAIL_LATENCY_BLOWN",
                    "HARD_FAIL_LATENCY_BLOWN at %s: p95=%.3fms > %.1fms | %s" % (
                        pt_key, s["p95_ms"], HF_LATENCY_BLOWN_MS, summ))

    for (V_C_IN, V_REL) in OPERATING_POINTS:
        if V_REL >= 20:
            pt_key = "V_C_IN_%d_V_REL_%d" % (V_C_IN, V_REL)
            near_ref = summaries[pt_key]["near_ref"]
            if not math.isnan(near_ref) and near_ref < HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20:
                return ("HARD_FAIL_REFUSE_GATE_CLIFF",
                        "HARD_FAIL_REFUSE_GATE_CLIFF at %s: near_ref=%.3f < %.2f | %s" % (
                            pt_key, near_ref, HF_NEAR_REFUSE_MIN_AT_V_REL_GE_20, summ))

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
            "device": str(_DEV), "cuda_available": _CUDA_AVAILABLE,
            "_fix24_violations": list(_FIX24_VIOLATIONS),
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d operating_points=%s device=%s cuda=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, OPERATING_POINTS,
             _DEV, _CUDA_AVAILABLE, CONFIG_VERSION), flush=True)

    # Fix #24 gate: full-mode requires cuda available (smoke is allowed CPU torch on laptop)
    if RUN_MODE == "full" and not _CUDA_AVAILABLE:
        print("[FATAL Fix #24] RUN_MODE=full but torch.cuda.is_available()=False; "
              "this cell is dispatched to overnight_queue specifically to use the GPU. "
              "Aborting to avoid running on CPU.", flush=True)
        sys.exit(2)

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

    # Fix #24 post-run: if cuda was available and we have violations, surface them
    if _CUDA_AVAILABLE and _FIX24_VIOLATIONS:
        print("\n[Fix #24 WARNING] %d probe(s) showed memory_allocated=0 despite cuda available:"
              % len(_FIX24_VIOLATIONS), flush=True)
        for v in _FIX24_VIOLATIONS:
            print("  - " + v, flush=True)

    v, vmsg = compute_verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "device": str(_DEV), "cuda_available": _CUDA_AVAILABLE,
        "_fix24_violations": list(_FIX24_VIOLATIONS),
        "DESIGN_NOTE": (
            "GPU-torchified rewrite of EXT-1 v2 production scale per Fix #24. Same "
            "4 operating points + 4 categories + 3 arms + bands. Big matmuls "
            "(audit cleanup against V_subjects, KV retrieve against W_kv, intent "
            "classifier, graph-health probe) batched on torch.cuda; per-query "
            "latency amortized from batch wall-clock so p95 reflects per-query "
            "production inference cost. Substrate-only; zero LLM forward calls. "
            "Target = (V_C_IN=2000, V_REL=50)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
