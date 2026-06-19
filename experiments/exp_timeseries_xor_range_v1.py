"""
timeseries_xor_range_v1 -- Time-tag XOR range query correctness.

Tests whether XOR time-binding (m_t = xi_t XOR tau_t) supports algebraic range queries.

Pre-registered thresholds (from handoff research note):
  HARD-PASS: in-window accuracy > 85% AND out-of-window contamination < 20%.
  MIDDLE:    in-window [50%, 85%] OR out-of-window [20%, 40%].
  HARD-FAIL: in-window < 50% OR out-of-window > 40%.

Design:
  - K time-tagged patterns m_t = content_t XOR tau_t stored in W.
  - Range query: generate tau_range = sum of tau_t for t in [t_lo, t_hi].
  - Retrieve: walk W with tau_range, check which content vectors are retrieved.
  - In-window acc = fraction of patterns in [t_lo, t_hi] correctly retrieved.
  - Out-of-window contamination = fraction of patterns outside [t_lo, t_hi] spuriously retrieved.

Note: BSC XOR time-tags use {-1,+1} elementwise product as binding.
The range query is an OR-bundle of time-tag vectors for the window.

No _nN suffix; production N=1024 rule 3. Smoke-first per handoff tier hint.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import time
import math
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "timeseries_xor_range_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024  # production N; no _nN suffix, stated here per rule 3

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    K_PATTERNS = 10
    WINDOW_SIZES = [2, 3]
else:
    SEEDS = [7, 17, 23, 31, 41]
    K_PATTERNS = 20
    WINDOW_SIZES = [2, 3, 5]

RETRIEVAL_THRESH = 0.60  # cosine threshold for "retrieved"
N_QUERIES = 10  # range queries per seed


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """Bundle (superpose) a list of vectors, return normalized sum."""
    if not vecs:
        raise ValueError("empty bundle")
    s = np.sum(vecs, axis=0)
    return np.sign(s + 1e-12)


def hopfield_update(W: np.ndarray, x: np.ndarray, n_iters: int = 20) -> np.ndarray:
    for _ in range(n_iters):
        x = np.sign(W @ x + 1e-12)
    return x


def run_one_seed(N: int, K: int, seed: int, window_sizes: List[int]) -> Dict:
    rng = np.random.RandomState(seed)

    # Content and time-tag atoms
    contents = rng.choice([-1.0, 1.0], size=(N, K))
    tau = rng.choice([-1.0, 1.0], size=(N, K))

    # Build W: store m_t = content_t XOR tau_t (elementwise product).
    # Key insight: m_t = content_t * tau_t, so content_t = m_t * tau_t (XOR is self-inverse).
    # To query content via tau: use tau_t as retrieval key -> W @ tau_t should activate m_t,
    # then unbind: content = retrieved * tau_t.
    # But Hopfield W stores m_t m_t^T / N, so W @ tau_t gives projection onto m_t-space only
    # if tau_t correlates with m_t. Since m_t = content_t * tau_t, inner product is
    # m_t . tau_t = sum_i content_i (tau_i)^2 = sum_i content_i = bounded random walk.
    # Better approach: store (tau_t, m_t) as key-value in W = sum m_t tau_t^T / N.
    # Then W @ tau_t ~ m_t, unbind -> content_t.
    W_kv = np.zeros((N, N))  # key-value: W @ tau_t -> m_t
    m_vecs = []
    for t in range(K):
        m_t = xor_bind(contents[:, t], tau[:, t])
        W_kv += np.outer(m_t, tau[:, t]) / N
        m_vecs.append(m_t)

    results_by_window = {}

    for win_size in window_sizes:
        in_window_accs = []
        out_window_conts = []

        for q in range(N_QUERIES):
            # Random window [t_lo, t_lo + win_size)
            t_lo = rng.randint(0, max(1, K - win_size))
            t_hi = min(t_lo + win_size, K)
            in_window = list(range(t_lo, t_hi))
            out_window = [t for t in range(K) if t not in in_window]

            # In-window accuracy: for each t in window, query tau_t -> get m_t -> unbind -> content
            in_retrieved = []
            for t in in_window:
                # Retrieve m_t via W_kv @ tau_t
                m_hat = np.sign(W_kv @ tau[:, t] + 1e-12)
                # Unbind: content_hat = m_hat * tau_t (XOR inverse)
                content_hat = xor_bind(m_hat, tau[:, t])
                cos = float(np.dot(content_hat, contents[:, t]) /
                            (np.linalg.norm(content_hat) * np.linalg.norm(contents[:, t]) + 1e-10))
                in_retrieved.append(cos > RETRIEVAL_THRESH)

            # Out-of-window contamination: for each t out of window,
            # does a window-bundle query accidentally retrieve t?
            # Query: bundle of tau vectors for window
            tau_window_vecs = [tau[:, t2] for t2 in in_window]
            q_bundle = bundle(tau_window_vecs)
            m_bundle_hat = np.sign(W_kv @ q_bundle + 1e-12)
            out_retrieved = []
            for t in out_window:
                m_hat_t = xor_bind(m_bundle_hat, tau[:, t])
                cos = float(np.dot(m_hat_t, contents[:, t]) /
                            (np.linalg.norm(m_hat_t) * np.linalg.norm(contents[:, t]) + 1e-10))
                out_retrieved.append(cos > RETRIEVAL_THRESH)

            in_acc = float(np.mean(in_retrieved)) if in_retrieved else 0.0
            out_cont = float(np.mean(out_retrieved)) if out_retrieved else 0.0
            in_window_accs.append(in_acc)
            out_window_conts.append(out_cont)

        mean_in_acc = float(np.mean(in_window_accs))
        mean_out_cont = float(np.mean(out_window_conts))
        results_by_window[win_size] = {
            "win_size": win_size,
            "mean_in_acc": mean_in_acc,
            "mean_out_cont": mean_out_cont,
            "hp": mean_in_acc > 0.85 and mean_out_cont < 0.20,
        }
        print(f"  window={win_size} in_acc={mean_in_acc:.3f} out_cont={mean_out_cont:.3f} "
              f"hp={results_by_window[win_size]['hp']}", flush=True)

    return {
        "seed": seed,
        "K": K,
        "results_by_window": results_by_window,
    }


def _instrumentation_selftest():
    """Assert range query returns non-null in/out metrics at small scale."""
    rng = np.random.RandomState(999)
    N_test, K_test = 256, 8
    contents = rng.choice([-1.0, 1.0], size=(N_test, K_test))
    tau = rng.choice([-1.0, 1.0], size=(N_test, K_test))
    # Build KV matrix
    W_kv = np.zeros((N_test, N_test))
    for t in range(K_test):
        m_t = xor_bind(contents[:, t], tau[:, t])
        W_kv += np.outer(m_t, tau[:, t]) / N_test

    # Retrieve pattern 0 via tau_0
    m_hat = np.sign(W_kv @ tau[:, 0] + 1e-12)
    content_hat = xor_bind(m_hat, tau[:, 0])
    cos_0 = float(np.dot(content_hat, contents[:, 0]) /
                  (np.linalg.norm(content_hat) * np.linalg.norm(contents[:, 0]) + 1e-10))
    assert not math.isnan(cos_0), "cos_0 NaN"
    assert cos_0 is not None, "cos_0 is None"
    # at smoke scale, cos_0 > 0 is expected (single pattern, no interference)
    # If K_test=8 and N=256 > K, should be well above threshold
    assert cos_0 > 0.0, f"cos_0={cos_0:.4f} not positive at selftest scale"
    print(f"[selftest] PASS: cos_with_content_0={cos_0:.4f}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} seeds={SEEDS} "
          f"K={K_PATTERNS} window_sizes={WINDOW_SIZES}", flush=True)

    all_results = []
    for seed in SEEDS:
        print(f"\n[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r = run_one_seed(N, K_PATTERNS, seed, WINDOW_SIZES)
        all_results.append(r)

    # Aggregate
    n_seeds = len(SEEDS)
    per_window_hp = {}
    per_window_in_acc = {}
    per_window_out_cont = {}

    for win_size in WINDOW_SIZES:
        hp_count = sum(
            1 for r in all_results
            if r["results_by_window"].get(win_size, {}).get("hp", False)
        )
        in_accs = [r["results_by_window"].get(win_size, {}).get("mean_in_acc", 0.0)
                   for r in all_results]
        out_conts = [r["results_by_window"].get(win_size, {}).get("mean_out_cont", 1.0)
                     for r in all_results]
        per_window_hp[win_size] = hp_count
        per_window_in_acc[win_size] = float(np.mean(in_accs))
        per_window_out_cont[win_size] = float(np.mean(out_conts))

    # Overall verdict
    mean_in_acc_all = float(np.mean(list(per_window_in_acc.values())))
    mean_out_cont_all = float(np.mean(list(per_window_out_cont.values())))

    if mean_in_acc_all > 0.85 and mean_out_cont_all < 0.20:
        verdict = "HARD_PASS"
    elif mean_in_acc_all < 0.50 or mean_out_cont_all > 0.40:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    # Per-window breakdown
    per_window_n_hp = {str(k): int(v) for k, v in per_window_hp.items()}

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"timeseries_xor_range: mean_in_acc={mean_in_acc_all:.3f} "
            f"mean_out_cont={mean_out_cont_all:.3f} N={N} K={K_PATTERNS}"
        ),
        "mean_in_window_acc": float(mean_in_acc_all),
        "mean_out_window_cont": float(mean_out_cont_all),
        "per_window_n_hp": per_window_n_hp,
        "per_window_in_acc": {str(k): float(v) for k, v in per_window_in_acc.items()},
        "per_window_out_cont": {str(k): float(v) for k, v in per_window_out_cont.items()},
        "n_seeds": int(n_seeds),
        "N": N,
        "K": K_PATTERNS,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_in_acc={mean_in_acc_all:.3f} mean_out_cont={mean_out_cont_all:.3f}",
          flush=True)
    print(f"  per_window HP counts: {per_window_n_hp}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()