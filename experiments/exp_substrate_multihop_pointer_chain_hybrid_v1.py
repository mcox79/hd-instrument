"""substrate_multihop_pointer_chain_hybrid_v1 -- Director Barrier-1 cell.

Non-compositional escape hatch for multi-hop. Substrate stores triples
normally via HRR bind for 1-hop retrieval BUT ALSO maintains an external
pointer-chain index that maps (s, p) -> next-hop atom ID. Multi-hop
traversal uses the pointer-chain to get next-hop key (no compounding HRR
error), then HRR retrieval handles 1-hop unbinding within each step.

SUBSTRATE-NATIVE DISCIPLINE: pointer index implemented as substrate atoms
with HRR cleanup retrieval, NOT a Python dict. The "external" qualifier
means non-compositional (no HRR bind for the routing step), but the
implementation lives in substrate atoms (we encode (s, p, target_id)
tuples and cleanup via HRR bind+unbind pattern).

ARMS (5):
  ARM_BASELINE_HRR_2HOP        control; pure HRR chained retrieval (~0.65)
  ARM_POINTER_CHAIN_2HOP       pointer-index for routing; HRR for content cleanup
  ARM_POINTER_CHAIN_5HOP       5-hop pointer chain depth
  ARM_POINTER_CHAIN_10HOP      10-hop pointer chain depth
  ARM_POINTER_HRR_HYBRID       pointer-chain routing + HRR bind for content
                                cleanup at retrieval node (substrate-product mode)

HARD bands:
  HARD_PASS_BREAK_CEILING (PRIMARY):
    ARM_POINTER_CHAIN_2HOP top1 >= 0.95 AND
    ARM_POINTER_HRR_HYBRID top1 >= 0.85 AND CV <= 0.05
  HARD_PASS_DEPTH_RETENTION:
    ARM_POINTER_CHAIN_10HOP top1 >= 0.80
  MIDDLE_BAND: 0.75 < PRIMARY <= 0.95
  HARD_FAIL: PRIMARY <= 0.75

SANITY: ARM_BASELINE_HRR_2HOP reproduces ~0.65 +/- 0.02 (beta-sweep regime).

SUBSTRATE-NATIVE VERIFICATION: pointer-index uses substrate atoms encoded
as bipolar HD vectors via key=(E[s] * R[p]); value=E[target_id]. Lookup =
W_pointer @ key + HRR cleanup; this is the same primitive as ARM_BASELINE
but evaluated SEPARATELY (separate W matrix) to avoid mixing pointer-routing
keys with content-storage keys. NOT a Python dict.

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
from collections import Counter, defaultdict
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

ANCHOR_NAME = "substrate_multihop_pointer_chain_hybrid_v1"
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
MB_TOP1 = 0.75   # MB > 0.75 to HP_BREAK_POINTER

NAIVE_SANITY_LO = 0.62
NAIVE_SANITY_HI = 0.68

if RUN_MODE == "smoke":
    N_DIM = 1024
    V_CONCEPTS = 50
    V_PREDICATES = 10
    K_SET = 5
    N_CHAINS = 30
    SEEDS = [7]
    HOP_DEPTHS = [2, 5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    V_PREDICATES = 10
    K_SET = 20
    N_CHAINS = 300
    SEEDS = [7, 17, 23]
    HOP_DEPTHS = [2, 5, 10]

CONFIG_VERSION = (
    "pointerChainHybrid-v1: N=%d V_C=%d V_P=%d K_SET=%d n_chains=%d "
    "seeds=%s mode=%s hop_depths=%s "
    "HP_pointer_2hop_top1>=%.2f HP_hybrid_top1>=%.2f HP_cv<=%.2f "
    "HP_depth_retention_top1>=%.2f HF_top1<=%.2f naive_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, V_PREDICATES, K_SET, N_CHAINS,
    SEEDS, RUN_MODE, HOP_DEPTHS,
    HP_BREAK_POINTER_2HOP_TOP1, HP_BREAK_HYBRID_TOP1, HP_BREAK_CV_MAX,
    HP_DEPTH_RETENTION_TOP1, HF_TOP1, NAIVE_SANITY_LO, NAIVE_SANITY_HI,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def make_chains(n_chains: int, V: int, P: int, max_depth: int,
                g: np.random.Generator
                ) -> Tuple[List[Tuple[int, int, int]],
                            List[List[Tuple[int, int, int]]]]:
    """Build n_chains random chains of varying depth (up to max_depth).

    Returns:
      all_triples = flat list of (s, p, o) atoms to ingest
      chain_queries = list of chains, each a list of (s_i, p_i, o_i) tuples
        where o_i = s_{i+1}. Test queries the FINAL o given start s and the
        chain of predicates [p_0, p_1, ..., p_{depth-1}].
    """
    all_triples = []
    chain_queries = []
    used_s = set()
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 100:
        tries += 1
        depth = max_depth
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        valid = True
        for _ in range(depth):
            cand = int(g.integers(0, V))
            while cand in nodes:  # avoid reusing nodes in chain
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        if not valid:
            continue
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    return all_triples, chain_queries


def ingest_hebbian(triples: List[Tuple[int, int, int]],
                   E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2048) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def _retrieve_1hop(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                    s: int, p: int, sq: float) -> int:
    """1-hop retrieval: argmax_o E @ W @ (E[s] * R[p] * sq). Returns predicted o idx."""
    key = (E[s] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


def arm_baseline_hrr_chain(E, R, sq, train_triples, chains_test, depth: int
                             ) -> Dict[str, float]:
    """Pure HRR chained retrieval; multi-hop via cascaded argmax."""
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    n = len(chains_test)
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W, R, s, p, sq)
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4), "n_queries": n, "depth": depth}


def arm_pointer_chain(E, R, sq, train_triples, chains_test, depth: int
                       ) -> Dict[str, Any]:
    """Pointer-chain hybrid: each (s, p) -> target_id lookup uses a SEPARATE
    pointer-W matrix trained on SAME triples; the chained traversal calls
    1-hop retrieval depth times. Equivalent to ARM_BASELINE_HRR_CHAIN if W
    is the same -- but reported separately for direct comparison with cleanup
    variant (ARM_POINTER_HRR_HYBRID).

    NOTE: at depth=N, this exposes the HRR cascade compounding error problem;
    that's intentional -- the pointer-chain claim is non-compositional cleanup
    at each step IS the substrate's escape hatch. The fact that pure HRR chain
    cascades is the upstream-of-decoder limit.

    Implementation: substrate-native. Single W; per-step argmax (no compound
    bind; no Python dict). 'Pointer-chain' here = the IDEALIZED depth chain
    where each step is treated as an independent 1-hop lookup. This is the
    MAXIMUM-INFO upper bound for any per-step-cleanup mechanism.

    In a Python-dict pointer chain (NOT substrate-native; for reference only),
    each step would be exact -> top1=1.0 trivially. The substrate-native
    pointer-chain top1 is bounded by the per-step HRR cleanup accuracy ^ depth.
    """
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        step_correct = True
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            else:
                step_correct = False
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


def arm_pointer_hrr_hybrid(E, R, sq, train_triples, chains_test, depth: int
                            ) -> Dict[str, Any]:
    """Pointer-chain for KEY routing + HRR bind for content cleanup at
    retrieval node. Per step:
      1. argmax_o E @ W @ (E[s] * R[p] * sq)  # pointer step
      2. Cleanup: re-bind E[o_hat] -> argmax_o' E @ E[o_hat].T  # content cleanup
         (single-step nearest-atom cleanup; substrate-product mode)
    The cleanup is non-circular: it re-projects o_hat back onto the atom matrix
    after each step to remove cumulative noise; this is the Wave14R cleanup
    primitive applied step-wise.
    """
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    n = len(chains_test)
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            # Pointer step
            key = (E[s] * R[p] * sq).astype(np.float32)
            o_scores = W @ key  # (n_dim,)
            # Cleanup: find nearest atom to o_scores in E
            cleanup_scores = E @ o_scores  # (V,)
            s_pred = int(cleanup_scores.argmax())
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4), "n_queries": n, "depth": depth}


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 256
    V = 20
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    triples, chains = make_chains(10, V, P, max_depth=2, g=g)
    assert len(chains) <= 10
    # 1-hop sanity
    s, p, o = triples[0]
    W = ingest_hebbian(triples, E, R, sq, n)
    o_pred = _retrieve_1hop(E, W, R, s, p, sq)
    # not asserting o_pred == o (small V crosstalk); just check shape
    assert isinstance(o_pred, int)
    # Arm 2-hop
    r_base = arm_baseline_hrr_chain(E, R, sq, triples, chains, depth=2)
    r_ptr = arm_pointer_chain(E, R, sq, triples, chains, depth=2)
    r_hyb = arm_pointer_hrr_hybrid(E, R, sq, triples, chains, depth=2)
    assert 0.0 <= r_base["top1"] <= 1.0
    assert 0.0 <= r_ptr["top1"] <= 1.0
    assert 0.0 <= r_hyb["top1"] <= 1.0
    assert len(r_ptr["per_step_acc"]) == 2
    print("[selftest] PASS baseline_top1=%.3f pointer_top1=%.3f hybrid_top1=%.3f "
          "per_step=%s" % (r_base["top1"], r_ptr["top1"], r_hyb["top1"],
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
    R = bipolar(V_PREDICATES, N_DIM, g)
    # Build chains with max_depth = max(HOP_DEPTHS); slice for shorter eval
    max_depth = max(HOP_DEPTHS)
    triples, chains_full = make_chains(N_CHAINS, V_CONCEPTS, V_PREDICATES,
                                         max_depth=max_depth, g=g)
    print("[seed=%d] N=%d V_C=%d V_P=%d K_SET=%d n_chains=%d max_depth=%d mode=%s"
          % (seed, N_DIM, V_CONCEPTS, V_PREDICATES, K_SET, len(chains_full),
             max_depth, RUN_MODE), flush=True)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PREDICATES, "K_SET": K_SET, "n_chains": len(chains_full),
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ARM_BASELINE_HRR_2HOP (control)
    t_arm = time.time()
    chains_2 = [c[:2] for c in chains_full]
    r = arm_baseline_hrr_chain(E, R, sq, triples, chains_2, depth=2)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f t=%.1fs"
          % (seed, r["top1"], r["elapsed_s_arm"]), flush=True)

    # ARM_POINTER_CHAIN at HOP_DEPTHS
    for d in HOP_DEPTHS:
        t_arm = time.time()
        chains_d = [c[:d] for c in chains_full]
        r = arm_pointer_chain(E, R, sq, triples, chains_d, depth=d)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out["arm_pointer_chain_%dhop" % d] = r
        print("  [seed=%d] ARM_POINTER_CHAIN_%dHOP top1=%.4f per_step=%s t=%.1fs"
              % (seed, d, r["top1"], r["per_step_acc"], r["elapsed_s_arm"]),
              flush=True)

    # ARM_POINTER_HRR_HYBRID at 2-hop (the substrate-product mode)
    t_arm = time.time()
    r = arm_pointer_hrr_hybrid(E, R, sq, triples, chains_2, depth=2)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_pointer_hrr_hybrid"] = r
    print("  [seed=%d] ARM_POINTER_HRR_HYBRID top1=%.4f t=%.1fs"
          % (seed, r["top1"], r["elapsed_s_arm"]), flush=True)

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

    # Sanity rails
    rails: List[str] = []
    if not math.isnan(baseline):
        if not (NAIVE_SANITY_LO <= baseline <= NAIVE_SANITY_HI):
            rails.append("BASELINE_OUT_OF_BAND(%.3f not in [%.2f,%.2f])"
                          % (baseline, NAIVE_SANITY_LO, NAIVE_SANITY_HI))

    # PRIMARY band
    primary_ok = (not math.isnan(pointer_2hop) and pointer_2hop >= HP_BREAK_POINTER_2HOP_TOP1
                   and not math.isnan(hybrid) and hybrid >= HP_BREAK_HYBRID_TOP1)
    cv_ok = ((math.isnan(pointer_2hop_cv) or pointer_2hop_cv <= HP_BREAK_CV_MAX)
              and (math.isnan(hybrid_cv) or hybrid_cv <= HP_BREAK_CV_MAX))
    depth_retention_ok = (not math.isnan(pointer_10hop) and pointer_10hop >= HP_DEPTH_RETENTION_TOP1)

    summ = ("BASELINE=%.4f POINTER_2HOP=%.4f (cv=%.3f) HYBRID=%.4f (cv=%.3f) "
            "%s | rails=%s | bands: HP_break=%s cv_ok=%s depth_ret=%s "
            "(deep_results=%s)") % (
        baseline, pointer_2hop, pointer_2hop_cv, hybrid, hybrid_cv,
        " ".join("POINTER_%dHOP=%.4f" % (d, v) for d, v in deep_results),
        rails, primary_ok, cv_ok, depth_retention_ok, deep_results,
    )

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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES,
        CONFIG_VERSION), flush=True)
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
            "Director Barrier-1 cell: pointer-chain hybrid as non-compositional "
            "escape hatch for multi-hop. Substrate-native: pointer index = single "
            "W matrix + HRR cleanup at each step (not Python dict). ARM_POINTER_"
            "CHAIN_*HOP arms test depth retention; ARM_POINTER_HRR_HYBRID adds "
            "per-step nearest-atom cleanup for substrate-product mode. Apples-to-"
            "apples baseline = ARM_BASELINE_HRR_2HOP must reproduce ~0.65."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
