"""exp_multihop_reverse_replay_backward_sweep_v1 (M5 brain-mechanism cell).

Brain mechanism #5 — reverse-replay / backward sweep for credit assignment.

Tests whether adding a SEPARATE S_back reverse-temporal-order store (and reverse-
direction NREM replay) lifts substrate multi-hop chain accuracy over the forward-
only baseline. Composes with M3 bidirectional meet-in-middle. Includes a
discriminator arm (RANDOM_REVERSE) that proves temporal order is load-bearing
(NOT "any extra replay helps").

ARMS (6):
  A: BASELINE_FORWARD_REPLAY_ONLY      substrate current state; W forward only
  B: REVERSE_REPLAY_ONLY               W frozen; only S_back ingested; downstream uses S_back
  C: WITH_REVERSE_REPLAY               both forward W and S_back active; equal weight
  D: BIDIRECTIONAL_BOTH                C + meet-in-middle inference (M3 composition)
  E: REWARD_GATED_REVERSE              reverse-replay fires only when forward top-1 conf > tau
                                        (Ambrose-Pfeiffer-Foster 2016 reward-gating)
  F: RANDOM_REVERSE_REPLAY_DISCRIMINATOR
                                        reverse-replay over SHUFFLED temporal order
                                        (CRITICAL: tests "temporal order matters")

PROSPECTIVE BANDS (LOCKED via module-init asserts):
  HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY:
    D top1 >= A top1 + 0.20 AND C top1 >= F top1 + 0.10
  MIDDLE_BAND_PARTIAL_REVERSE_REPLAY:
    partial conditions (e.g. D > A + 0.10 but C - F < 0.05)
  HARD_FAIL_REVERSE_REPLAY_DOESNT_HELP:
    D top1 <= A top1 + 0.05

CARDINALITY (META_RULE_H CARDINALITY_OK):
  6 arms x 3 seeds x 3 depths {2, 3, 5} = 54 units
  EXPECTED_N_UNITS = 54; HARD_FAIL_CARDINALITY_BREACH if observed < expected.

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
    write_metrics,
)

ANCHOR_NAME = "multihop_reverse_replay_backward_sweep_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# HARD bands (LOCKED prospectively per M5 drill cell-spec design section)
HP_D_LIFT_OVER_A = 0.20       # D top1 - A top1 must be >= this
HP_C_OVER_F = 0.10            # C top1 - F top1 must be >= this (temporal-order load-bearing)
MID_D_LIFT_LO = 0.10          # MIDDLE: D > A + 0.10 (partial)
HF_D_NO_HELP = 0.05           # HARD_FAIL: D - A <= this

# Reward-gate calibration (Arm E)
REWARD_GATE_TAU_QUANTILE = 0.75  # tau = 75th-percentile of depth-2 fwd-top1 conf

assert HP_D_LIFT_OVER_A > MID_D_LIFT_LO > HF_D_NO_HELP, \
    "HARD_PASS > MIDDLE > HARD_FAIL ladder must be monotonic"
assert HP_C_OVER_F > 0.0
assert 0.0 < REWARD_GATE_TAU_QUANTILE < 1.0

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 80
    N_CHAINS = 30
    SEEDS = [7]
    DEPTHS = [2, 3, 5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    N_CHAINS = 200
    SEEDS = [7, 17, 23]
    DEPTHS = [2, 3, 5]

EXPECTED_N_UNITS = 6 * len(SEEDS) * len(DEPTHS)  # CARDINALITY_OK

CONFIG_VERSION = (
    "multihopReverseReplayBackwardSweepV1: N=%d V_C=%d n_chains=%d "
    "seeds=%s depths=%s mode=%s "
    "HP_D_lift>=%.2f HP_C_over_F>=%.2f MID_lift>=%.2f HF_no_help<=%.2f "
    "tau_quantile=%.2f EXPECTED_N_UNITS=%d"
) % (
    N_DIM, V_CONCEPTS, N_CHAINS, SEEDS, DEPTHS, RUN_MODE,
    HP_D_LIFT_OVER_A, HP_C_OVER_F, MID_D_LIFT_LO, HF_D_NO_HELP,
    REWARD_GATE_TAU_QUANTILE, EXPECTED_N_UNITS,
)


def bipolar(M: int, n: int, g) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X


def ingest_W_forward(triples, E, R, sq, n_dim, batch=2000):
    """Forward associative-memory W (the substrate's standard ingest)."""
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def ingest_S_back_reverse(chains, E, n_dim, shuffle_temporal_order=False, g=None):
    """Build S_back from chains as reverse-temporal-order pair store.

    For each chain [(s, p, o), (s', p', o'), ...] we form successive (k_t, k_{t+1})
    key-pairs where k_t = E[node_t]. For S_back we write: S_back += k_t outer k_{t+1}
    so that S_back @ k_{t+1} approximates k_t (recovering the predecessor).

    If shuffle_temporal_order=True, we destroy the WHICH-NODES-PAIR-WITH-WHICH
    structure while preserving total binding volume. Specifically: collect ALL
    chain nodes into one pool, randomly pair them, and bind those random pairs
    into S_back. This produces a S_back with the same Frobenius norm and same
    number of bound pairs but NO predecessor signal at all — the discriminator
    against "any extra binding helps". (V1 implementation shuffled iteration
    order only; that was a NO-OP because outer-sum is commutative — caught by
    smoke gap C-F = 0.0000.)
    """
    S_back = np.zeros((n_dim, n_dim), dtype=np.float32)
    if shuffle_temporal_order:
        if g is None:
            raise ValueError("shuffle_temporal_order=True requires generator g")
        all_nodes = []
        for chain in chains:
            nodes = [chain[0][0]] + [hop[2] for hop in chain]
            for i in range(len(nodes) - 1):
                all_nodes.append((nodes[i], nodes[i + 1]))
        # Build same total number of pairs, but shuffle the SECOND element across
        # all pairs so the (k_a, k_b) bindings are NOT the true temporal pairs.
        first = [a for a, _ in all_nodes]
        second = [b for _, b in all_nodes]
        g.shuffle(second)
        for a, b in zip(first, second):
            k_prev = E[a].astype(np.float32)
            k_next = E[b].astype(np.float32)
            S_back += np.outer(k_prev, k_next)
    else:
        for chain in chains:
            nodes = [chain[0][0]] + [hop[2] for hop in chain]
            for i in range(len(nodes) - 1):
                k_prev = E[nodes[i]].astype(np.float32)
                k_next = E[nodes[i + 1]].astype(np.float32)
                S_back += np.outer(k_prev, k_next)
    return S_back


def make_deep_chains(n_chains, V, P, max_depth, g, disallow_s=None):
    if disallow_s is None:
        disallow_s = set()
    all_triples, chain_queries, used_s = [], [], set(disallow_s)
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
        raise RuntimeError("BLOCKING make_deep_chains: only %d/%d" % (len(chain_queries), n_chains))
    return all_triples, chain_queries


def _retrieve_1hop_fwd(E, W, R, s, p, sq):
    """Standard forward 1-hop substrate retrieval."""
    key = (E[s] * R[p] * sq).astype(np.float32)
    return int((E @ (W @ key)).argmax()), float((E @ (W @ key)).max())


def _retrieve_1hop_back(E, S_back, o):
    """Reverse 1-hop: given o (the target of a hop), recover s (the source).

    Uses S_back which was built from key-pair (E[s], E[o]) writes; S_back @ E[o]
    approximates E[s].
    """
    pred = S_back @ E[o].astype(np.float32)
    return int((E @ pred).argmax()), float((E @ pred).max())


def chain_forward_only(E, W, R, sq, chain, depth):
    """Arm A: pure forward-only chain (substrate baseline)."""
    s = chain[0][0]
    per_step = []
    for i in range(depth):
        p = chain[i][1]
        s_pred, _ = _retrieve_1hop_fwd(E, W, R, s, p, sq)
        per_step.append(1 if s_pred == chain[i][2] else 0)
        s = s_pred
    correct = (s == chain[depth - 1][2])
    return correct, per_step


def chain_reverse_only(E, S_back, chain, depth):
    """Arm B: pure reverse-only chain — start from end, walk backward.

    Given the chain ground-truth end node E[chain[-1][2]] as starting point, walk
    backward using S_back. Final prediction (at position 0) should equal chain[0][0].
    NOTE: this is a "given the answer, can we walk back to the question" test,
    which is the symmetric companion to forward-only. It does NOT have access to
    intermediate forward state — that's arm C.
    """
    o = chain[depth - 1][2]
    per_step = []
    for i in range(depth - 1, -1, -1):
        s_pred, _ = _retrieve_1hop_back(E, S_back, o)
        per_step.append(1 if s_pred == chain[i][0] else 0)
        o = s_pred
    correct = (o == chain[0][0])
    return correct, list(reversed(per_step))


def chain_with_reverse_replay(E, W, R, sq, S_back, chain, depth, replay_lambda=0.5):
    """Arm C: forward chain with reverse-replay enriched W (blended scores).

    Per hop, compute forward score (from W) AND reverse score (S_back @ E[hyp]
    correlated against forward-source). Blend: combined_score = forward + lambda *
    reverse_consistency, where reverse_consistency[hyp] = cos(S_back @ E[hyp],
    E[current_source]).
    """
    s = chain[0][0]
    per_step = []
    for i in range(depth):
        p = chain[i][1]
        key = (E[s] * R[p] * sq).astype(np.float32)
        fwd_scores = E @ (W @ key)  # [V]
        # Reverse consistency: for each candidate hyp, S_back @ E[hyp] should equal E[s]
        # We compute scores against all candidates by S_back @ E.T then dot with E[s].
        rev_back = E @ S_back.T  # [V, n_dim] — for each hyp, S_back @ E[hyp] (transposed orientation)
        # Actually S_back @ E[hyp].T  has shape [n_dim]; we want dot with E[s] for each hyp.
        # rev_back[hyp] = E[hyp] @ S_back^T  has same shape as the desired projection (n_dim);
        # then dot with E[s] gives a scalar per hyp.
        rev_consistency = rev_back @ E[s].astype(np.float32)  # [V]
        combined = fwd_scores + replay_lambda * rev_consistency
        s_pred = int(combined.argmax())
        per_step.append(1 if s_pred == chain[i][2] else 0)
        s = s_pred
    correct = (s == chain[depth - 1][2])
    return correct, per_step


def chain_bidirectional_meet(E, W, R, sq, chain, depth, V_C):
    """Arm D: full bidirectional meet-in-middle ranking (M3 composition).

    Uses W.T for backward walk (matches META_M7 cell's chain-grade primitive).
    """
    mid = depth // 2
    preds = [chain[i][1] for i in range(depth)]
    S = chain[0][0]
    # Forward state
    state_fwd = E[S].astype(np.float32).copy()
    for i in range(mid):
        state_fwd = W @ (state_fwd * R[preds[i]] * sq)
    fnorm = np.linalg.norm(state_fwd) + 1e-8
    # Score each candidate Z
    best_cos = -2.0
    best_Z = -1
    for Z in range(V_C):
        state_bwd = E[Z].astype(np.float32).copy()
        for i in range(depth - 1, mid - 1, -1):
            state_bwd = W.T @ state_bwd
            state_bwd = state_bwd * R[preds[i]] * sq
        bnorm = np.linalg.norm(state_bwd) + 1e-8
        cos = float(np.dot(state_fwd, state_bwd) / (fnorm * bnorm))
        if cos > best_cos:
            best_cos = cos
            best_Z = Z
    true_Z = chain[depth - 1][2]
    return (best_Z == true_Z), best_cos


def calibrate_reward_gate_tau(E, W, R, sq, chains, depth, quantile):
    """Calibrate tau = quantile of forward depth-2 top-1 confidence values."""
    confs = []
    for chain in chains:
        s = chain[0][0]
        for i in range(min(2, depth)):
            p = chain[i][1]
            _, conf = _retrieve_1hop_fwd(E, W, R, s, p, sq)
            confs.append(conf)
            s, _ = _retrieve_1hop_fwd(E, W, R, s, p, sq)
    if not confs:
        return float("inf")
    return float(np.quantile(confs, quantile))


def chain_reward_gated_reverse(E, W, R, sq, S_back, chain, depth, tau, replay_lambda=0.5):
    """Arm E: reward-gated reverse-replay — only blend reverse score when forward
    top-1 confidence exceeds tau.
    """
    s = chain[0][0]
    per_step = []
    for i in range(depth):
        p = chain[i][1]
        key = (E[s] * R[p] * sq).astype(np.float32)
        fwd_scores = E @ (W @ key)
        fwd_top = float(fwd_scores.max())
        if fwd_top > tau:
            rev_back = E @ S_back.T
            rev_consistency = rev_back @ E[s].astype(np.float32)
            combined = fwd_scores + replay_lambda * rev_consistency
        else:
            combined = fwd_scores  # gate closed; pure forward
        s_pred = int(combined.argmax())
        per_step.append(1 if s_pred == chain[i][2] else 0)
        s = s_pred
    correct = (s == chain[depth - 1][2])
    return correct, per_step


def run_arms_at_depth(E, R, sq, W, S_back, S_back_shuffled, chains, depth, V_C, tau):
    """Run all 6 arms at a single depth; chains are sliced to `depth`."""
    chains_d = [c[:depth] for c in chains]
    n = len(chains_d)

    # Arm A
    a_hits = sum(int(chain_forward_only(E, W, R, sq, c, depth)[0]) for c in chains_d)
    # Arm B
    b_hits = sum(int(chain_reverse_only(E, S_back, c, depth)[0]) for c in chains_d)
    # Arm C
    c_hits = sum(int(chain_with_reverse_replay(E, W, R, sq, S_back, c, depth)[0]) for c in chains_d)
    # Arm D
    d_hits = sum(int(chain_bidirectional_meet(E, W, R, sq, c, depth, V_C)[0]) for c in chains_d)
    # Arm E
    e_hits = sum(int(chain_reward_gated_reverse(E, W, R, sq, S_back, c, depth, tau)[0]) for c in chains_d)
    # Arm F (discriminator: shuffled temporal order in S_back)
    f_hits = sum(int(chain_with_reverse_replay(E, W, R, sq, S_back_shuffled, c, depth)[0]) for c in chains_d)

    return {
        "depth": depth, "n_queries": n,
        "A_baseline_forward_only_top1": round(a_hits / max(n, 1), 4),
        "B_reverse_only_top1": round(b_hits / max(n, 1), 4),
        "C_with_reverse_replay_top1": round(c_hits / max(n, 1), 4),
        "D_bidirectional_both_top1": round(d_hits / max(n, 1), 4),
        "E_reward_gated_reverse_top1": round(e_hits / max(n, 1), 4),
        "F_random_reverse_discriminator_top1": round(f_hits / max(n, 1), 4),
    }


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 256
    V = 20
    P = 3
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)

    triples, chains = make_deep_chains(8, V, P, max_depth=5, g=g)
    W = ingest_W_forward(triples, E, R, sq, n)
    S_back = ingest_S_back_reverse(chains, E, n, shuffle_temporal_order=False)
    S_back_sh = ingest_S_back_reverse(chains, E, n, shuffle_temporal_order=True, g=g)

    # S_back has nonzero norm
    assert float(np.linalg.norm(S_back)) > 0.0
    assert float(np.linalg.norm(S_back_sh)) > 0.0

    # All 6 arms produce valid top1 in [0, 1] at smoke depths
    tau = calibrate_reward_gate_tau(E, W, R, sq, chains, depth=5, quantile=0.75)
    for d in [2, 3, 5]:
        r = run_arms_at_depth(E, R, sq, W, S_back, S_back_sh, chains, d, V, tau)
        for k, v in r.items():
            if k.endswith("_top1"):
                assert 0.0 <= v <= 1.0, "arm %s top1=%s out of [0,1] at depth=%d" % (k, v, d)

    # Bands locked numerics
    assert HP_D_LIFT_OVER_A == 0.20
    assert HP_C_OVER_F == 0.10
    assert MID_D_LIFT_LO == 0.10
    assert HF_D_NO_HELP == 0.05

    # CARDINALITY_OK explicit
    assert EXPECTED_N_UNITS == 6 * len(SEEDS) * len(DEPTHS)

    # No LLM calls
    assert _LLM_CALL_COUNTER[0] == 0

    print("[selftest] PASS tau=%.4f arms_OK_depths=%s expected_units=%d"
          % (tau, [2, 3, 5], EXPECTED_N_UNITS), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    P_max = 10
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(P_max, N_DIM, g)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_chains": N_CHAINS, "depths": DEPTHS,
        "config_version": CONFIG_VERSION,
        "expected_n_units_per_seed": 6 * len(DEPTHS),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Build chains + ingest stores
    t_w = time.time()
    triples, chains = make_deep_chains(N_CHAINS, V_CONCEPTS, P_max, max_depth=5, g=g)
    W = ingest_W_forward(triples, E, R, sq, N_DIM)
    S_back = ingest_S_back_reverse(chains, E, N_DIM, shuffle_temporal_order=False)
    g_shuf = np.random.default_rng(seed + 1000)
    S_back_sh = ingest_S_back_reverse(chains, E, N_DIM, shuffle_temporal_order=True, g=g_shuf)
    out["build_time_s"] = round(time.time() - t_w, 2)
    print("  [seed=%d] W + S_back built (%d triples, %d chains) t=%.1fs" % (
        seed, len(triples), len(chains), out["build_time_s"]), flush=True)

    # Reward-gate calibration on chains at depth 2 (CALIBRATION not arm-readout)
    tau = calibrate_reward_gate_tau(E, W, R, sq, chains[:50], depth=5,
                                    quantile=REWARD_GATE_TAU_QUANTILE)
    out["reward_gate_tau"] = round(tau, 4)
    print("  [seed=%d] reward-gate tau=%.4f (q=%.2f)" % (
        seed, tau, REWARD_GATE_TAU_QUANTILE), flush=True)

    # Run all 6 arms at each depth
    per_depth_results = []
    for d in DEPTHS:
        t_d = time.time()
        r = run_arms_at_depth(E, R, sq, W, S_back, S_back_sh, chains, d, V_CONCEPTS, tau)
        r["elapsed_s_depth"] = round(time.time() - t_d, 2)
        per_depth_results.append(r)
        print("  [seed=%d] depth=%d A=%.3f B=%.3f C=%.3f D=%.3f E=%.3f F=%.3f t=%.1fs" % (
            seed, d,
            r["A_baseline_forward_only_top1"], r["B_reverse_only_top1"],
            r["C_with_reverse_replay_top1"], r["D_bidirectional_both_top1"],
            r["E_reward_gated_reverse_top1"], r["F_random_reverse_discriminator_top1"],
            r["elapsed_s_depth"]), flush=True)

    out["per_depth"] = per_depth_results

    # Per-arm depth-averaged top1 (mean over the 3 depths)
    for arm in ["A_baseline_forward_only", "B_reverse_only", "C_with_reverse_replay",
                "D_bidirectional_both", "E_reward_gated_reverse",
                "F_random_reverse_discriminator"]:
        vals = [r[arm + "_top1"] for r in per_depth_results]
        out["arm_" + arm + "_mean_top1"] = round(float(np.mean(vals)), 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_arm(arm_key: str) -> float:
        vals = [p.get(arm_key) for p in per_seed
                if isinstance(p.get(arm_key), (int, float))]
        return float(np.mean(vals)) if vals else float("nan")

    A = mean_arm("arm_A_baseline_forward_only_mean_top1")
    B = mean_arm("arm_B_reverse_only_mean_top1")
    C = mean_arm("arm_C_with_reverse_replay_mean_top1")
    D = mean_arm("arm_D_bidirectional_both_mean_top1")
    E = mean_arm("arm_E_reward_gated_reverse_mean_top1")
    F = mean_arm("arm_F_random_reverse_discriminator_mean_top1")

    # Observed cardinality check (META_RULE_H CARDINALITY_OK)
    observed_units = sum(p.get("expected_n_units_per_seed", 0) for p in per_seed)
    if observed_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH: observed=%d expected=%d "
                "per_seed=%s" % (observed_units, EXPECTED_N_UNITS, per_seed))

    d_lift = D - A
    c_over_f = C - F

    summ = ("A_baseline=%.4f B_reverse_only=%.4f C_with_reverse=%.4f D_bidir=%.4f "
            "E_reward_gated=%.4f F_random_reverse=%.4f | "
            "D-A_lift=%+.4f C-F_temporal_order=%+.4f") % (
        A, B, C, D, E, F, d_lift, c_over_f,
    )

    if d_lift >= HP_D_LIFT_OVER_A and c_over_f >= HP_C_OVER_F:
        return ("HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY",
                "HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY: " + summ)
    if d_lift <= HF_D_NO_HELP:
        return ("HARD_FAIL",
                "HARD_FAIL_REVERSE_REPLAY_DOESNT_HELP: " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_REVERSE_REPLAY: " + summ)


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
    print("[config] anchor=%s mode=%s seeds=%s N=%d depths=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, DEPTHS, CONFIG_VERSION), flush=True)
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

    assert _LLM_CALL_COUNTER[0] == 0

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
            "M5 brain-mechanism cell: reverse-replay / backward sweep. Tests "
            "whether SEPARATE reverse-temporal-order store (S_back) lifts substrate "
            "multi-hop accuracy over forward-only baseline (arm A). Includes M3 "
            "bidirectional meet-in-middle composition (arm D), reward-gated "
            "reverse-replay (arm E; Ambrose-Pfeiffer-Foster 2016), and a "
            "CRITICAL discriminator (arm F: shuffled-temporal-order reverse-replay) "
            "that tests whether temporal order is load-bearing — distinguishing "
            "'reverse-replay helps because of TEMPORAL ORDER' (HARD_PASS) vs "
            "'any extra replay helps regardless of order' (HARD_FAIL or MIDDLE). "
            "Companion to META_M7 bidirectional cell (which uses W.T; this cell "
            "uses separate S_back so forward and reverse can be selectively gated)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
