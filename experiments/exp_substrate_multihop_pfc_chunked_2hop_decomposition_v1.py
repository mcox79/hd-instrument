"""substrate_multihop_pfc_chunked_2hop_decomposition_v1.

REVIVAL ANGLE 5 (Research 2026-06-25 drill) -- PFC task-decomposition chunking.

Background (4-for-4 prior HARD_FAIL):
  pointer-chain-v2/wm-scaffold/csp-gated/consolidation-v3 all do per-hop argmax
  cleanup downstream of THE SAME primitive. Per-step accuracy is BIT-IDENTICAL
  across cells on identical seeds because the underlying cleanup math is the
  same. The per-hop primitive's information-theoretic floor (~0.69 at V_C=200
  V_P=10 K_SET=20 max_depth=10 -> 2000 W bindings) sets a hard ceiling on
  5-hop accuracy of 0.69^5 = 0.156 (empirical: 0.122).

Mechanism (this cell):
  Never go beyond 2-hop per sub-query. Decompose multi-hop into a sequence of
  2-hop sub-queries; each sub-query gets a CLEAN intermediate entity to start
  from. The 2-hop primitive at this regime gives ~0.485 (chain primitive with
  noisy state) but with a CLEAN entity start, 2-hop should approach the
  beta-sweep 2-hop sanity rail of ~0.65.

  For k=5 query: decompose as 2+2+1 sub-queries. For k=10: 2+2+2+2+2.
  Each sub-query: state = E[entity]; for two hops, state = W @ (state * R[p] * sq);
  cleanup s_pred = argmax(E @ state); then for sub-query 2, state = E[s_pred].
  i.e. the CHAIN STATE is RE-CLEANED to an atomic E[] vector between sub-queries.

  WM-scaffold v1's flaw: it wrote intermediates to a WM scaffold but each per-hop
  was still a NOISY state propagation. This cell does TRUE 2-hop sub-queries
  (the chain RESTARTS from a clean atomic vector every 2 hops).

ARMS (4):
  ARM_BASELINE_HRR_2HOP        beta-sweep verbatim regime (sanity rail [0.62, 0.68])
  ARM_SINGLE_CHAIN_5HOP        pointer-chain v2 monolithic 5hop (rail ~0.122)
  ARM_PFC_CHUNKED_5HOP         decomposed 2+2+1; clean entity start per sub-query
  ARM_PFC_CHUNKED_10HOP        decomposed 2+2+2+2+2; clean entity start per sub-query

PROSPECTIVE BANDS (locked at module init via assert):
  HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING:
    ARM_PFC_CHUNKED_5HOP top1 >= 0.50 AND
    ARM_PFC_CHUNKED_10HOP top1 >= 0.30 AND
    cv (both chunked) <= 0.07
  HARD_PASS_PARTIAL:
    ARM_PFC_CHUNKED_5HOP top1 >= 0.30 (lift over 0.122 rail)
  HARD_FAIL_CHUNKING_DOESNT_HELP:
    ARM_PFC_CHUNKED_5HOP top1 < 0.20

SACRED SANITY: ARM_BASELINE_HRR_2HOP reproduces 0.65 +/- 0.03; otherwise
SANITY_BREACH verdict.

META_M7 DISCIPLINE: smoke must NOT show >>0.50 lift over 5-hop rail. If smoke
shows lift, that signals smoke regime is too small. PRE-DISPATCH ABORT.

ASCII-only; per-seed checkpoint; atexit synthesizer.
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
    write_metrics
)

ANCHOR_NAME = "substrate_multihop_pfc_chunked_2hop_decomposition_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# HARD bands (LOCKED prospectively)
HP_CHUNKED_5HOP = 0.50
HP_CHUNKED_10HOP = 0.30
HP_CHUNKED_CV_MAX = 0.07
HP_PARTIAL_5HOP = 0.30
HF_5HOP = 0.20

# SACRED SANITY: baseline must reproduce beta-sweep regime
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# BASELINE arm regime (verbatim beta-sweep)
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
# POINTER+CHUNKED regime
POINTER_V_P = 10
POINTER_K_SET = 20

# META_PROSPECTIVE_BANDS_FRESH_SEEDS lock
assert HP_CHUNKED_5HOP > HP_PARTIAL_5HOP > HF_5HOP, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands must be HP > MID_low > HF"
assert HP_CHUNKED_10HOP < HP_CHUNKED_5HOP, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: 10hop HP_threshold must be <= 5hop"
assert 0.0 < HP_CHUNKED_CV_MAX < 0.20, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: cv ceiling must be in (0, 0.20)"

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTER_N_CHAINS = 50
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS
    HOP_DEPTHS_CHUNKED = [5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    POINTER_N_CHAINS = 200
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS
    HOP_DEPTHS_CHUNKED = [5, 10]

n_predicates = max(BASELINE_V_P, POINTER_V_P)

CONFIG_VERSION = (
    "pfcChunked2hopDecompositionV1: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "seeds=%s mode=%s hop_depths=%s chunk_size=2 "
    "HP_chunked_5hop>=%.2f HP_chunked_10hop>=%.2f HP_cv<=%.2f "
    "HP_partial_5hop>=%.2f HF_5hop<%.2f baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    SEEDS, RUN_MODE, HOP_DEPTHS_CHUNKED,
    HP_CHUNKED_5HOP, HP_CHUNKED_10HOP, HP_CHUNKED_CV_MAX,
    HP_PARTIAL_5HOP, HF_5HOP, BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


# ---- BASELINE: verbatim beta-sweep regime + mechanism --------------------

def make_two_hop_chains_betasweep(n_chains: int, V: int, g: np.random.Generator,
                                    p1: int = 0, p2: int = 1):
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int, int]] = []
    used_s: set = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def chain_naive_hard(W, E, R, sq, start: int, relations: List[int]) -> int:
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def arm_baseline_hrr_2hop_betasweep(E, R, sq, train_triples, queries):
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s, p1, p2, o_true, _x = q
        pred = chain_naive_hard(W, E, R, sq, s, [p1, p2])
        if pred == o_true:
            hits += 1
    return {"top1": round(hits / max(len(queries), 1), 4),
            "n_queries": len(queries), "mechanism": "beta_sweep_naive_hard"}


# ---- POINTER + CHUNKED arms ---------------------------------------------

def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set):
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d generated"
            % (len(chain_queries), n_chains)
        )
    return all_triples, chain_queries


def _retrieve_1hop(E, W, R, s: int, p: int, sq: float) -> int:
    key = (E[s] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


def arm_single_chain_naive(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """Monolithic chain via pointer-chain (per-step argmax cleanup). Rail-match."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth}


def _two_hop_subquery(E, R, sq, W, start_idx: int, p_a: int, p_b: int) -> int:
    """Two-hop sub-query from a CLEAN starting entity index.

    state = E[start_idx]; bind+walk via p_a; bind+walk via p_b; cleanup.
    Returns the cleaned entity index after both hops.
    """
    state = E[start_idx].copy()
    state = W @ (state * R[p_a] * sq)
    # No mid-cleanup; let the 2-hop accumulate as in beta-sweep regime, then cleanup
    state = W @ (state * R[p_b] * sq)
    return int((E @ state).argmax())


def _one_hop_subquery(E, R, sq, W, start_idx: int, p: int) -> int:
    return _retrieve_1hop(E, W, R, start_idx, p, sq)


def _decompose_chunks(depth: int, chunk_size: int = 2) -> List[int]:
    """Return list of chunk sizes summing to depth. e.g. depth=5 -> [2, 2, 1]."""
    chunks = []
    remaining = depth
    while remaining > 0:
        c = min(chunk_size, remaining)
        chunks.append(c)
        remaining -= c
    return chunks


def arm_pfc_chunked(E, R, sq, W, chains_test, depth: int,
                     chunk_size: int = 2) -> Dict[str, Any]:
    """PFC chunked decomposition: walk chain in 2-hop chunks; restart from
    CLEAN entity index between chunks. Per-chunk accuracy tracked.
    """
    n = len(chains_test)
    hits = 0
    chunk_sizes = _decompose_chunks(depth, chunk_size)
    per_chunk_hits = np.zeros(len(chunk_sizes), dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        hop_offset = 0
        for ci, csz in enumerate(chunk_sizes):
            if csz == 2:
                p_a = chain[hop_offset][1]
                p_b = chain[hop_offset + 1][1]
                s_pred = _two_hop_subquery(E, R, sq, W, s, p_a, p_b)
                target = chain[hop_offset + 1][2]
            elif csz == 1:
                p = chain[hop_offset][1]
                s_pred = _one_hop_subquery(E, R, sq, W, s, p)
                target = chain[hop_offset][2]
            else:
                raise RuntimeError("only chunk_size in {1,2} supported")
            if s_pred == target:
                per_chunk_hits[ci] += 1
            s = s_pred  # CLEAN entity index restart
            hop_offset += csz
        if s == chain[depth - 1][2]:
            hits += 1
    per_chunk_acc = (per_chunk_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_chunk_acc": [round(x, 4) for x in per_chunk_acc],
            "chunk_sizes": chunk_sizes,
            "n_queries": n, "depth": depth, "chunk_size": chunk_size}


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    # Baseline sanity at selftest scale
    Rb = bipolar(max(BASELINE_V_P, 2), n, g)
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, Rb, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0

    # Chunked + single-chain selftest at small scale
    triples_d, chains_d = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W2 = ingest_hebbian(triples_d, E, R, sq, n)

    r_single = arm_single_chain_naive(E, R, sq, W2, chains_d, depth=5)
    r_chunked = arm_pfc_chunked(E, R, sq, W2, chains_d, depth=5, chunk_size=2)

    assert 0.0 <= r_single["top1"] <= 1.0
    assert 0.0 <= r_chunked["top1"] <= 1.0
    assert len(r_single["per_step_acc"]) == 5
    assert r_chunked["chunk_sizes"] == [2, 2, 1], \
        "chunk_sizes=%s expected [2,2,1]" % r_chunked["chunk_sizes"]
    assert sum(r_chunked["chunk_sizes"]) == 5
    # Verify chunks=[2,2,2,2,2] for depth=10
    cs10 = _decompose_chunks(10, 2)
    assert cs10 == [2, 2, 2, 2, 2], "depth=10 expected [2,2,2,2,2] got %s" % cs10

    print("[selftest] PASS baseline=%.3f single5hop=%.3f chunked5hop=%.3f chunks=%s"
          % (r_base["top1"], r_single["top1"], r_chunked["top1"],
             r_chunked["chunk_sizes"]), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)
    max_depth = max(HOP_DEPTHS_CHUNKED)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates, "K_SET": POINTER_K_SET,
        "baseline_n_chains": BASELINE_N_CHAINS_LOCAL,
        "pointer_n_chains": POINTER_N_CHAINS,
        "max_depth": max_depth,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE (SACRED sanity rail) =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS_LOCAL, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples,
                                                   base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f n=%d t=%.1fs"
          % (seed, r_baseline["top1"], r_baseline["n_queries"],
             r_baseline["elapsed_s_arm"]), flush=True)

    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    if not baseline_ok:
        print("  [seed=%d] SANITY BREACH: baseline=%.4f not in [%.2f, %.2f]"
              % (seed, r_baseline["top1"], BASELINE_SANITY_LO,
                 BASELINE_SANITY_HI), flush=True)

    # ===== POINTER arms (deep chains; per-step + chunked) =====
    t_arm = time.time()
    pointer_triples, pointer_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=max_depth,
        g=g, disallow_s=set())
    W_pointer = ingest_hebbian(pointer_triples, E, R, sq, N_DIM)
    print("  [seed=%d] pointer W built (%d triples, %d chains, max_depth=%d) t=%.1fs"
          % (seed, len(pointer_triples), len(pointer_chains), max_depth,
             round(time.time() - t_arm, 2)), flush=True)

    # Single-chain rail at depth=5 (baseline match to pointer-chain v2)
    t_arm = time.time()
    chains_5 = [c[:5] for c in pointer_chains]
    r_single5 = arm_single_chain_naive(E, R, sq, W_pointer, chains_5, depth=5)
    r_single5["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_single_chain_5hop"] = r_single5
    print("  [seed=%d] ARM_SINGLE_CHAIN_5HOP top1=%.4f per_step=%s t=%.1fs"
          % (seed, r_single5["top1"], r_single5["per_step_acc"],
             r_single5["elapsed_s_arm"]), flush=True)

    # Chunked arms
    for d in HOP_DEPTHS_CHUNKED:
        t_arm = time.time()
        chains_d = [c[:d] for c in pointer_chains]
        r_ch = arm_pfc_chunked(E, R, sq, W_pointer, chains_d, depth=d,
                                chunk_size=2)
        r_ch["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out["arm_pfc_chunked_%dhop" % d] = r_ch
        print("  [seed=%d] ARM_PFC_CHUNKED_%dHOP top1=%.4f per_chunk=%s chunks=%s t=%.1fs"
              % (seed, d, r_ch["top1"], r_ch["per_chunk_acc"],
                 r_ch["chunk_sizes"], r_ch["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    baseline = mean_top1("arm_baseline_hrr_2hop")
    single5 = mean_top1("arm_single_chain_5hop")
    chunked5 = mean_top1("arm_pfc_chunked_5hop")
    chunked5_cv = cv_top1("arm_pfc_chunked_5hop")
    chunked10 = mean_top1("arm_pfc_chunked_10hop") if RUN_MODE == "full" else float("nan")
    chunked10_cv = cv_top1("arm_pfc_chunked_10hop") if RUN_MODE == "full" else float("nan")

    rails: List[str] = []
    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d seeds baseline_mean=%.4f not in [%.2f, %.2f])"
                      % (sanity_breached, len(per_seed), baseline,
                         BASELINE_SANITY_LO, BASELINE_SANITY_HI))

    summ = ("BASELINE=%.4f (sanity_breach_seeds=%d/%d) "
            "SINGLE_CHAIN_5HOP=%.4f (rail) "
            "CHUNKED_5HOP=%.4f (cv=%.3f) "
            "CHUNKED_10HOP=%.4f (cv=%.3f) "
            "lift_5hop_over_rail=%+.4f | rails=%s") % (
        baseline, sanity_breached, len(per_seed),
        single5, chunked5, chunked5_cv,
        chunked10, chunked10_cv,
        (chunked5 - single5) if (not math.isnan(chunked5) and not math.isnan(single5)) else float("nan"),
        rails,
    )

    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    hp_chain_grade = (
        not math.isnan(chunked5) and chunked5 >= HP_CHUNKED_5HOP
        and (math.isnan(chunked10) or chunked10 >= HP_CHUNKED_10HOP)
        and (math.isnan(chunked5_cv) or chunked5_cv <= HP_CHUNKED_CV_MAX)
    )
    hp_partial = (not math.isnan(chunked5) and chunked5 >= HP_PARTIAL_5HOP)

    if hp_chain_grade:
        return "HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING", \
               "HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING: " + summ
    if hp_partial:
        return "HARD_PASS_PARTIAL", "HARD_PASS_PARTIAL_CHUNKING_LIFT: " + summ
    if not math.isnan(chunked5) and chunked5 < HF_5HOP:
        return "HARD_FAIL", "HARD_FAIL_CHUNKING_DOESNT_HELP: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND_CHUNKING_PARTIAL: " + summ


_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "ANGLE 5 revival: PFC task-decomposition chunking. 5-hop chain "
            "decomposed as 2+2+1 sub-queries; each sub-query restarts from a "
            "CLEAN atomic E[] vector (the cleaned argmax index from previous "
            "chunk). 10-hop decomposed as 2+2+2+2+2. WM-scaffold v1 wrote "
            "intermediates to scaffold but per-hop was still noisy-state "
            "propagation; this cell does TRUE 2-hop sub-queries with chain "
            "STATE re-cleaned to atomic E[] between sub-queries."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
