"""substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED.

V1 BUG DISCOVERED (Director triage 2026-06-26):
  BASELINE_HRR_2HOP top1 = 0.395 (mean across 3 seeds) but the sanity rail
  expected 0.65 +/- 0.03 (beta-sweep regime). Root cause: v1's `make_chains`
  uses RANDOM predicates per triple (V_P=10 freely sampled) and constructs
  10-hop chains (max_depth=10) yielding 3000 (s,p,o) bindings in W (300 per
  chain x 300 chains shared across 10 predicates). Beta-sweep's regime:
  V_P=2 fixed-pair (p1=0, p2=1) + 2-hop chains -> 400 (s,p,o) bindings in W
  (200 chains x 2 hops). Pointer-chain v1's W ingested ~7.5x more triples
  spread across the same per-predicate key space -> drastically more
  per-(s,p) crosstalk -> lower 1-hop accuracy -> chain compounds.

V1 also used `_retrieve_1hop` which does `argmax(E @ W @ E[s] * R[p] * sq)`
i.e. cleanup AFTER each hop. Beta-sweep's `chain_naive_hard` propagates the
NOISY state without per-hop cleanup. Both are valid mechanisms but only the
beta-sweep regime + mechanism pair reproduces 0.65.

V2 FIX: BASELINE arm uses beta-sweep's EXACT regime + EXACT mechanism
(verbatim `chain_naive_hard` + `make_two_hop_chains` with fixed-pair
p1=0/p2=1). Its W is built from a SEPARATE 2-hop-only chain set (V_P=2,
N_CHAINS=200) -> 400 bindings, matching beta-sweep exactly.

POINTER_CHAIN arms use their OWN deep-chain set (V_P=10, multi-hop) with
their OWN W. They share E and R primitives with the baseline arm but operate
on a different graph. The COMPARISON IS NOT APPLES-TO-APPLES W; that's the
honest scope flag. What's apples-to-apples is encoder + atoms + bind/unbind
primitives. The pointer-chain claim is that the MECHANISM (per-step
cleanup + pointer routing) lifts retrieval; the baseline = beta-sweep regime
floor that the mechanism MUST beat to be useful.

SACRED SANITY GATE: baseline arm must reproduce 0.65 +/- 0.03. If not, the
cell ABORTS via sys.exit(1) BEFORE running pointer-chain arms.

ARMS (5):
  ARM_BASELINE_HRR_2HOP        beta-sweep regime; verbatim mechanism (~0.65 sanity rail)
  ARM_POINTER_CHAIN_2HOP       pointer index + per-step argmax cleanup
  ARM_POINTER_CHAIN_5HOP       5-hop depth retention
  ARM_POINTER_CHAIN_10HOP      10-hop depth retention
  ARM_POINTER_HRR_HYBRID       pointer routing + HRR content cleanup (2-hop)

HARD bands (LOCKED prospectively, unchanged from v1):
  HARD_PASS_BREAK_CEILING:
    ARM_POINTER_CHAIN_2HOP top1 >= 0.95 AND
    ARM_POINTER_HRR_HYBRID top1 >= 0.85 AND CV <= 0.05
  HARD_PASS_DEPTH_RETENTION:
    ARM_POINTER_CHAIN_10HOP top1 >= 0.80
  MIDDLE_BAND: 0.75 < PRIMARY <= 0.95
  HARD_FAIL: PRIMARY <= 0.75

SACRED SANITY: ARM_BASELINE_HRR_2HOP reproduces 0.65 +/- 0.03; otherwise
cell ABORTS (does not write metrics; does not run other arms).

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

ANCHOR_NAME = "substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed"
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
HP_BREAK_POINTER_2HOP_TOP1 = 0.95
HP_BREAK_HYBRID_TOP1 = 0.85
HP_BREAK_CV_MAX = 0.05
HP_DEPTH_RETENTION_TOP1 = 0.80
HF_TOP1 = 0.75
MB_TOP1 = 0.75

# SACRED SANITY: baseline must reproduce beta-sweep regime
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# BASELINE arm regime (verbatim beta-sweep)
BASELINE_V_P = 2  # p1=0, p2=1 used; defines R width >= 2
BASELINE_N_CHAINS = 200  # matches beta-sweep
# POINTER arms regime (Director Barrier-1 spec)
POINTER_V_P = 10
POINTER_K_SET = 20

if RUN_MODE == "smoke":
    N_DIM = 2048   # smoke uses smaller N (still big enough for sanity check)
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTER_N_CHAINS = 50
    HOP_DEPTHS = [2, 5]
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS  # 200 (full beta-sweep regime)
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    POINTER_N_CHAINS = 200      # apples-to-apples with beta-sweep n_chains
    HOP_DEPTHS = [2, 5, 10]
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS

n_predicates = max(BASELINE_V_P, POINTER_V_P)

CONFIG_VERSION = (
    "pointerChainHybrid-v2-baselineRailFixed: N=%d V_C=%d "
    "BASELINE_V_P=%d (fixed p1=0/p2=1; verbatim beta-sweep regime) "
    "BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "seeds=%s mode=%s hop_depths=%s "
    "HP_pointer_2hop_top1>=%.2f HP_hybrid_top1>=%.2f HP_cv<=%.2f "
    "HP_depth_retention_top1>=%.2f HF_top1<=%.2f baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    SEEDS, RUN_MODE, HOP_DEPTHS,
    HP_BREAK_POINTER_2HOP_TOP1, HP_BREAK_HYBRID_TOP1, HP_BREAK_CV_MAX,
    HP_DEPTH_RETENTION_TOP1, HF_TOP1, BASELINE_SANITY_LO, BASELINE_SANITY_HI,
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
    """VERBATIM port of beta-sweep's make_two_hop_chains. Fixed-pair (p1, p2).

    Source: experiments/exp_substrate_resonator_softchain_beta_sweep_v1.py L171-192
    """
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
    """VERBATIM port of beta-sweep's chain_naive_hard (L136-142).

    State propagates noisy through hops; final argmax cleanup only.
    """
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def arm_baseline_hrr_2hop_betasweep(E, R, sq, train_triples, queries):
    """Baseline arm verbatim from beta-sweep. queries=[(s, p1, p2, o, x), ...].

    W is built from train_triples (the SAME 2-hop chains constructed via
    make_two_hop_chains_betasweep). Expected: ~0.65 at N=8192/V_C=200.
    """
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


# ---- POINTER arms: per-step cleanup mechanism ----------------------------

def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set
                      ) -> Tuple[List[Tuple[int, int, int]],
                                  List[List[Tuple[int, int, int]]]]:
    """Build n_chains random chains of `max_depth` hops with random predicates.

    Returns (all_triples, chains). chains[i] = list of (s, p, o) for chain i.
    BLOCKING: raises if cannot produce n_chains in V * 100 tries.
    """
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
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d disallow|=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, len(disallow_s), max_depth)
        )
    return all_triples, chain_queries


def _retrieve_1hop(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                    s: int, p: int, sq: float) -> int:
    key = (E[s] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


def arm_pointer_chain(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """Pointer-chain: per-step argmax cleanup. NB: with cleanup-between-hops,
    this is exactly _retrieve_1hop chained depth times.
    """
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
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
    }


def arm_pointer_hrr_hybrid(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """Pointer-chain for KEY routing + HRR cleanup at retrieval node.
    Per step: pointer step (W @ key) then nearest-atom argmax over E.
    """
    n = len(chains_test)
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            key = (E[s] * R[p] * sq).astype(np.float32)
            o_scores = W @ key
            cleanup_scores = E @ o_scores
            s_pred = int(cleanup_scores.argmax())
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4), "n_queries": n, "depth": depth}


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    P = 2  # for baseline subset
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(max(P, 2), n, g)
    # Baseline regime selftest: beta-sweep at small scale should give clearly-
    # above-chance top1 (chance=1/V); we don't require 0.65 at smoke selftest
    # scale, just sanity-of-mechanism.
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, R, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0
    assert r_base["top1"] > 5.0 / V, \
        "baseline_top1=%.3f must beat 5/V=%.3f at selftest scale" % (r_base["top1"], 5.0 / V)

    # Pointer arms selftest
    R2 = bipolar(4, n, g)
    triples_d, chains_d = make_deep_chains(8, V, 4, max_depth=2, g=g, disallow_s=set())
    W2 = ingest_hebbian(triples_d, E, R2, sq, n)
    r_ptr = arm_pointer_chain(E, R2, sq, W2, chains_d, depth=2)
    r_hyb = arm_pointer_hrr_hybrid(E, R2, sq, W2, chains_d, depth=2)
    assert 0.0 <= r_ptr["top1"] <= 1.0
    assert 0.0 <= r_hyb["top1"] <= 1.0
    assert len(r_ptr["per_step_acc"]) == 2

    print("[selftest] PASS baseline_top1=%.3f (n=%d V=%d) pointer_top1=%.3f hybrid_top1=%.3f per_step=%s"
          % (r_base["top1"], len(queries), V, r_ptr["top1"], r_hyb["top1"],
             r_ptr["per_step_acc"]), flush=True)


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
    max_depth = max(HOP_DEPTHS)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates, "K_SET": POINTER_K_SET,
        "baseline_n_chains": BASELINE_N_CHAINS_LOCAL,
        "pointer_n_chains": POINTER_N_CHAINS,
        "max_depth": max_depth,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE (SACRED sanity rail; reproduces beta-sweep) =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS_LOCAL, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples,
                                                   base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f (n=%d, beta-sweep regime) t=%.1fs"
          % (seed, r_baseline["top1"], r_baseline["n_queries"],
             r_baseline["elapsed_s_arm"]), flush=True)

    # SACRED SANITY: if baseline out-of-band, ABORT this seed (cell-wide abort
    # comes at the end after we've run all seeds; per-seed flag the breach).
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    if not baseline_ok:
        # Run the pointer arms anyway so we can diagnose; but flag the breach
        # both per-seed and (later) in verdict.
        print("  [seed=%d] SANITY BREACH: baseline=%.4f not in [%.2f, %.2f]; "
              "pointer arms will run but verdict will MARK SANITY_BREACH."
              % (seed, r_baseline["top1"], BASELINE_SANITY_LO,
                 BASELINE_SANITY_HI), flush=True)

    # ===== POINTER arms: separate chain set, separate W =====
    # Pointer chains can reuse s-values from baseline arm because the two
    # arms use SEPARATE W matrices; same E atom indices are fine.
    t_arm = time.time()
    pointer_triples, pointer_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=max_depth,
        g=g, disallow_s=set())
    W_pointer = ingest_hebbian(pointer_triples, E, R, sq, N_DIM)
    pointer_W_build_s = round(time.time() - t_arm, 2)
    print("  [seed=%d] pointer W built (%d triples, %d chains, max_depth=%d) t=%.1fs"
          % (seed, len(pointer_triples), len(pointer_chains), max_depth,
             pointer_W_build_s), flush=True)

    for d in HOP_DEPTHS:
        t_arm = time.time()
        chains_d = [c[:d] for c in pointer_chains]
        r = arm_pointer_chain(E, R, sq, W_pointer, chains_d, depth=d)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out["arm_pointer_chain_%dhop" % d] = r
        print("  [seed=%d] ARM_POINTER_CHAIN_%dHOP top1=%.4f per_step=%s t=%.1fs"
              % (seed, d, r["top1"], r["per_step_acc"], r["elapsed_s_arm"]),
              flush=True)

    # POINTER_HRR_HYBRID at 2-hop
    t_arm = time.time()
    chains_2 = [c[:2] for c in pointer_chains]
    r_hyb = arm_pointer_hrr_hybrid(E, R, sq, W_pointer, chains_2, depth=2)
    r_hyb["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_pointer_hrr_hybrid"] = r_hyb
    print("  [seed=%d] ARM_POINTER_HRR_HYBRID top1=%.4f t=%.1fs"
          % (seed, r_hyb["top1"], r_hyb["elapsed_s_arm"]), flush=True)

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
    pointer_2hop = mean_top1("arm_pointer_chain_2hop")
    pointer_2hop_cv = cv_top1("arm_pointer_chain_2hop")
    hybrid = mean_top1("arm_pointer_hrr_hybrid")
    hybrid_cv = cv_top1("arm_pointer_hrr_hybrid")

    deep_results: List[Tuple[int, float]] = []
    for d in HOP_DEPTHS:
        key = "arm_pointer_chain_%dhop" % d
        v = mean_top1(key)
        if not math.isnan(v):
            deep_results.append((d, v))
    pointer_10hop = next((v for d, v in deep_results if d == 10), float("nan"))

    # SACRED SANITY RAIL
    rails: List[str] = []
    sanity_breached_seeds = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    if sanity_breached_seeds > 0:
        rails.append("SANITY_BREACH(%d/%d seeds baseline out of [%.2f, %.2f]; baseline_mean=%.4f)"
                      % (sanity_breached_seeds, len(per_seed),
                         BASELINE_SANITY_LO, BASELINE_SANITY_HI, baseline))

    primary_ok = (not math.isnan(pointer_2hop) and pointer_2hop >= HP_BREAK_POINTER_2HOP_TOP1
                   and not math.isnan(hybrid) and hybrid >= HP_BREAK_HYBRID_TOP1)
    cv_ok = ((math.isnan(pointer_2hop_cv) or pointer_2hop_cv <= HP_BREAK_CV_MAX)
              and (math.isnan(hybrid_cv) or hybrid_cv <= HP_BREAK_CV_MAX))
    depth_retention_ok = (not math.isnan(pointer_10hop) and pointer_10hop >= HP_DEPTH_RETENTION_TOP1)

    summ = ("BASELINE=%.4f (sanity_breach_seeds=%d/%d) "
            "POINTER_2HOP=%.4f (cv=%.3f) HYBRID=%.4f (cv=%.3f) "
            "%s | rails=%s | bands: HP_break=%s cv_ok=%s depth_ret=%s "
            "(deep_results=%s)") % (
        baseline, sanity_breached_seeds, len(per_seed),
        pointer_2hop, pointer_2hop_cv, hybrid, hybrid_cv,
        " ".join("POINTER_%dHOP=%.4f" % (d, v) for d, v in deep_results),
        rails, primary_ok, cv_ok, depth_retention_ok, deep_results,
    )

    # If SACRED SANITY breached on a majority of seeds, mark SANITY_BREACH
    # as the verdict (cell is not interpretable).
    if sanity_breached_seeds >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    if primary_ok and cv_ok and depth_retention_ok:
        return "HARD_PASS_BREAK_CEILING_WITH_DEPTH", \
               "HARD_PASS_BREAK_CEILING_WITH_DEPTH_RETENTION: " + summ
    if primary_ok and cv_ok:
        return "HARD_PASS_BREAK_CEILING", "HARD_PASS_BREAK_CEILING: " + summ
    best_primary = max(pointer_2hop if not math.isnan(pointer_2hop) else -1,
                        hybrid if not math.isnan(hybrid) else -1)
    if best_primary > MB_TOP1:
        return "MIDDLE_BAND", "MIDDLE_BAND_POINTER_PARTIAL: " + summ
    return "HARD_FAIL", "HARD_FAIL_POINTER_NO_LIFT: " + summ


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
            "V2 BASELINE_RAIL_FIXED: v1's baseline reached only 0.395 because "
            "(a) it used make_chains with V_P=10 random predicates + max_depth=10 "
            "(3000 W bindings; high crosstalk); (b) it used cleanup-between-hops "
            "_retrieve_1hop mechanism. Beta-sweep's regime: V_P=2 fixed-pair + "
            "2-hop chains (400 W bindings) + noisy-state chain_naive_hard "
            "mechanism. V2 baseline arm uses beta-sweep's EXACT regime + EXACT "
            "mechanism (verbatim from L171-192 + L136-142). Pointer arms use "
            "their own deep-chain set + W; the apples-to-apples is "
            "encoder/atoms/primitives, not W. SACRED SANITY RAIL: cell verdict = "
            "SANITY_BREACH if baseline out of [0.62, 0.68] on majority of seeds."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
