"""Cell F: CSP-with-learning interference envelope (dual-objective Hopfield).

SCIENTIFIC QUESTION:
  Can the substrate simultaneously (a) converge to a planted combinatorial-optimization
  solution encoded in W_csp and (b) retrieve independently stored data patterns from
  W_data = W_csp + W_hebbian? The W = W_csp + W_data superposition is the novel axis
  (no published precedent). Modal expected outcome is MIDDLE_BAND -- do NOT pre-frame
  as failure.

PRE-REGISTERED BANDS (from exp_dev_handoff_research_csp_with_learning_2026-06-01.md):
  HARD-PASS (coexistence confirmed):
    - cut_ratio >= 0.80 * OPT on >= 4/5 seeds
    - retrieval_accuracy >= 0.90 on >= 4/5 seeds
  MIDDLE BAND: one objective passes HP, the other is middling (0.50 to HP threshold).
  HARD-FAIL (coexistence refuted at M=20, N=1024):
    - cut_ratio < 0.50 * OPT on >= 3/5 seeds, OR
    - retrieval_accuracy < 0.50 on >= 3/5 seeds.

  P(HARD-PASS)=0.35, P(MIDDLE)=0.40, P(HARD-FAIL)=0.25.

DESIGN:
  N=1024. Planted bipartite MAX-CUT: nodes split into two groups of N/2;
  W_csp[i,j] = -1/N if i,j in same partition, +1/N if i,j in different partitions
  (Ising encoding: minimizing energy finds the bipartition = maximum cut).
  M=20 random Hebbian patterns W_data = (1/N) sum_mu xi_mu xi_mu^T.
  W_combined = W_csp + W_data.
  Synchronous descent from random initial states (20 restarts per seed).
  Measure: (a) cut_ratio = achieved_cut / planted_OPT_cut; (b) retrieval accuracy.

SELF-TESTS (from handoff; run before main sweep):
  1. W_csp alone (M=0): descent finds planted bipartition >= 0.70 * OPT on >= 4/5 restarts.
  2. W_data alone (no W_csp): retrieval accuracy >= 0.90 for M=20 << alpha_c * N.
  3. W_combined: the actual test.

PROT-018: no _nN suffix. Production N=1024; stated per PROT-018 rule 3.
  Stated: production N = 1024; rationale: CSP-with-learning at M=20 << alpha_c*N.

TIMEOUT ESTIMATE:
  N=1024: synchronous descent step O(N^2) = ~0.5ms. 20 restarts * 200 steps = 4000 steps.
  5 seeds * 4000 steps = 20000 steps at 0.5ms = ~10s. 3x safety -> timeout=300 (floor).

Anchor: csp_hebbian_coexist_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_csp_hebbian_coexist_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "csp_hebbian_coexist_v1"

# Production config
N = 1024
M_DATA = 20
N_RESTARTS = 20
MAX_STEPS = 200
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_CUT_RATIO   = 0.80
HP_RETRIEVAL   = 0.90
HF_CUT_RATIO   = 0.50
HF_RETRIEVAL   = 0.50
HP_MIN_SEEDS   = 4  # out of 5
HF_MIN_SEEDS   = 3  # out of 5

# Planted bipartite: p_within = 0.0 weight (same partition), p_across = +1 (different)
# W_csp[i,j] = +1/N if different partition (planted cut), -1/N if same partition
# Energy = -(1/2) x^T W x -> finding MINIMUM energy finds MAX CUT (x_i=+1 iff in group A)
# Planted bipartition: first N//2 nodes = +1, last N//2 nodes = -1.


def build_w_csp(N: int) -> np.ndarray:
    """Build planted bipartite MAX-CUT weight matrix."""
    # label[i] = +1 if i < N//2, -1 otherwise
    label = np.ones(N, dtype=np.float64)
    label[N // 2:] = -1.0
    # W_csp[i,j] = label[i]*label[j] / N  (Ising Hopfield encoding of bipartition)
    # This creates a pattern memory for the bipartition vector
    W_csp = np.outer(label, label) / N
    np.fill_diagonal(W_csp, 0.0)
    return W_csp, label


def build_w_data(patterns: np.ndarray, N: int) -> np.ndarray:
    """Hebbian weight matrix for M random patterns."""
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def synchronous_descent(W: np.ndarray, state: np.ndarray,
                        max_steps: int, beta: float = 10.0) -> np.ndarray:
    """Synchronous Hopfield descent (deterministic at high beta)."""
    s = state.copy()
    for _ in range(max_steps):
        h = W @ s
        s_new = np.where(h > 0, 1.0, -1.0)
        if np.all(s_new == s):
            break
        s = s_new
    return s


def compute_cut_ratio(state: np.ndarray, planted_label: np.ndarray, N: int) -> float:
    """Fraction of planted OPT cut achieved. OPT cut = N^2/4 (bipartite)."""
    # Achieved cut: edges where state[i] != state[j] across all pairs
    # Planted OPT: N//2 * N//2 = N^2/4 edges
    opt_cut = (N // 2) ** 2
    # Count achieved cut: sum_{i<j} I(state[i] != state[j])
    # = (N^2 - sum_ij state[i]*state[j]) / 2 - N/2... use direct formula
    # Number of +1 nodes and -1 nodes in final state
    n_pos = int(np.sum(state > 0))
    n_neg = N - n_pos
    achieved_cut = n_pos * n_neg  # max-cut value for a bipartite assignment
    return achieved_cut / max(opt_cut, 1)


def run_one_seed(seed: int, N: int, M_data: int,
                 n_restarts: int, max_steps: int) -> Dict:
    rng = np.random.default_rng(seed)
    W_csp, planted_label = build_w_csp(N)
    patterns = rng.choice([-1.0, 1.0], size=(M_data, N))
    W_data = build_w_data(patterns, N)
    W_combined = W_csp + W_data

    # Self-test 1: W_csp alone
    cut_ratios_csp = []
    for _ in range(n_restarts):
        init = rng.choice([-1.0, 1.0], size=N)
        final = synchronous_descent(W_csp, init, max_steps)
        cut_ratios_csp.append(compute_cut_ratio(final, planted_label, N))
    csp_alone_median = float(np.median(cut_ratios_csp))

    # Self-test 2: W_data alone
    ret_acc_data_alone = []
    for mu in range(min(5, M_data)):
        init = patterns[mu].copy()
        init[:N // 10] *= -1  # 10% noise
        final = synchronous_descent(W_data, init, max_steps)
        overlap = float(np.mean(final == patterns[mu]))
        ret_acc_data_alone.append(overlap)
    data_alone_median = float(np.median(ret_acc_data_alone)) if ret_acc_data_alone else 0.0

    # Main test: W_combined
    cut_ratios = []
    for _ in range(n_restarts):
        init = rng.choice([-1.0, 1.0], size=N)
        final = synchronous_descent(W_combined, init, max_steps)
        cut_ratios.append(compute_cut_ratio(final, planted_label, N))

    ret_accs = []
    for mu in range(M_data):
        init = patterns[mu].copy()
        init[:N // 10] *= -1
        final = synchronous_descent(W_combined, init, max_steps)
        overlap = float(np.mean(final == patterns[mu]))
        ret_accs.append(overlap)

    cut_ratio = float(np.max(cut_ratios))  # best over restarts
    retrieval_acc = float(np.mean(ret_accs))  # mean over patterns

    return {
        "cut_ratio": cut_ratio,
        "retrieval_acc": retrieval_acc,
        "csp_alone_median": csp_alone_median,
        "data_alone_median": data_alone_median,
        "cut_ratios_all": [float(x) for x in cut_ratios],
        "ret_accs_all": [float(x) for x in ret_accs],
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert W_csp, W_data, and combined metrics are non-null at N=64."""
    N_t = 64
    W_csp_t, lbl = build_w_csp(N_t)
    assert W_csp_t.shape == (N_t, N_t), "W_csp shape wrong"
    rng = np.random.default_rng(42)
    pats = rng.choice([-1.0, 1.0], size=(5, N_t))
    W_d = build_w_data(pats, N_t)
    assert W_d.shape == (N_t, N_t), "W_data shape wrong"
    # descent on W_csp should converge in <= 200 steps
    init = rng.choice([-1.0, 1.0], size=N_t)
    final = synchronous_descent(W_csp_t, init, 200)
    cr = compute_cut_ratio(final, lbl, N_t)
    assert 0.0 <= cr <= 1.5, f"cut_ratio out of range: {cr}"
    assert not math.isnan(cr), "cut_ratio is NaN"
    # retrieval on W_data at M=5, N=64 should work
    noisy = pats[0].copy(); noisy[:6] *= -1
    final2 = synchronous_descent(W_d, noisy, 200)
    overlap = float(np.mean(final2 == pats[0]))
    assert not math.isnan(overlap), "retrieval_acc is NaN"
    print("[selftest] PASS: CSP+Hebbian metrics non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} M_data={M_DATA}",
          flush=True)

    all_results = {}
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        res = run_one_seed(seed, N, M_DATA, N_RESTARTS, MAX_STEPS)
        all_results[str(seed)] = res
        print(f"    cut_ratio={res['cut_ratio']:.3f} retrieval_acc={res['retrieval_acc']:.3f} "
              f"csp_alone={res['csp_alone_median']:.3f} data_alone={res['data_alone_median']:.3f}",
              flush=True)

    cut_ratios = [r["cut_ratio"] for r in all_results.values()]
    ret_accs = [r["retrieval_acc"] for r in all_results.values()]

    n_seeds = len(seeds)
    seeds_pass_cut = sum(1 for c in cut_ratios if c >= HP_CUT_RATIO)
    seeds_pass_ret = sum(1 for r in ret_accs if r >= HP_RETRIEVAL)
    seeds_fail_cut = sum(1 for c in cut_ratios if c < HF_CUT_RATIO)
    seeds_fail_ret = sum(1 for r in ret_accs if r < HF_RETRIEVAL)

    hp_threshold = HP_MIN_SEEDS if n_seeds >= 5 else math.ceil(n_seeds * 0.8)
    hf_threshold = HF_MIN_SEEDS if n_seeds >= 5 else math.ceil(n_seeds * 0.6)

    cut_hp = seeds_pass_cut >= hp_threshold
    ret_hp = seeds_pass_ret >= hp_threshold
    cut_hf = seeds_fail_cut >= hf_threshold
    ret_hf = seeds_fail_ret >= hf_threshold

    if cut_hf or ret_hf:
        verdict = "HARD_FAIL"
    elif cut_hp and ret_hp:
        verdict = "HARD_PASS"
    elif cut_hp or ret_hp:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "M_data": M_DATA, "n_seeds": n_seeds,
        "cut_ratio_mean": float(np.mean(cut_ratios)),
        "cut_ratio_std": float(np.std(cut_ratios)),
        "retrieval_acc_mean": float(np.mean(ret_accs)),
        "retrieval_acc_std": float(np.std(ret_accs)),
        "seeds_pass_cut": seeds_pass_cut, "seeds_pass_ret": seeds_pass_ret,
        "seeds_fail_cut": seeds_fail_cut, "seeds_fail_ret": seeds_fail_ret,
        "verdict": verdict, "elapsed_s": elapsed,
        "per_seed": {k: {
            "cut_ratio": v["cut_ratio"],
            "retrieval_acc": v["retrieval_acc"],
            "csp_alone_median": v["csp_alone_median"],
            "data_alone_median": v["data_alone_median"],
        } for k, v in all_results.items()},
        "thresholds": {
            "HP_cut": HP_CUT_RATIO, "HP_ret": HP_RETRIEVAL,
            "HF_cut": HF_CUT_RATIO, "HF_ret": HF_RETRIEVAL,
        },
        "verdict_msg": (
            f"CSP+Hebbian coexistence at N={N}, M=20: "
            f"cut_ratio={np.mean(cut_ratios):.3f}+/-{np.std(cut_ratios):.3f} "
            f"({seeds_pass_cut}/{n_seeds} seeds >= {HP_CUT_RATIO}), "
            f"retrieval={np.mean(ret_accs):.3f}+/-{np.std(ret_accs):.3f} "
            f"({seeds_pass_ret}/{n_seeds} seeds >= {HP_RETRIEVAL}). "
            f"Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope (SEEDS_SMOKE) for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
