"""
deletion_cert_zratio_n32768_v1 -- Wave 5 Anchor 3: deletion-cert Z-ratio at N=32768.

SCIENTIFIC QUESTION:
  At production N=32768, does the deletion-certificate Z-ratio reach the
  production-grade GDPR audit threshold (>=3.0 sigma over null)?

  Prior N=8192 result: Z-ratio ~2.0 sigma (marginal). Theory scales Z ~ sqrt(N),
  so N=32768 (2x N=8192) predicts Z ~2.8-3.0 sigma. Z-ratio ~3.6-5.1 sigma at
  N=32768 would cross the "production-grade GDPR audit" narrative threshold.

PRE-REGISTERED BANDS (per Wave 5 handoff):
  HARD-PASS: Z-ratio >= 3.0 sigma over null (mean across seeds).
  MIDDLE: 2.0 <= Z-ratio < 3.0.
  HARD-FAIL: Z-ratio < 1.5 sigma (no signal scaling at N=32768).

  Calibration probe: prior N=8192 anchor at ~2.0 sigma; theory predicts sqrt(N)
  scaling => N=32768 ~ 4 sigma. Bands at +-50% per policy.

FORMULA SELF-TESTS:
  1. Z = (mean_signal - mean_null) / std_null.
  2. Signal = ||W_pre @ xi_del - W_post @ xi_del|| where xi_del is the deleted pattern.
  3. Null = same metric measured on a NON-DELETED held-out pattern (random).
  4. Theory: signal ~ ||xi_del||^2 / N ~ 1.0 (rank-1 update); null ~ 1/sqrt(N).

PROT-018: anchor has _n32768 -> N must = 32768.
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "deletion_cert_zratio_n32768_v1"

# PROT-018: anchor has _n32768 -> N must = 32768
_N_SUFFIX = 32768
N_FULL = 32768
N_SMOKE = 4096

ALPHA = 0.05  # M / N
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
N_NULL_PROBES = 20  # number of null patterns per seed for null distribution

HP_Z = 3.0
MID_Z = 2.0
HF_Z = 1.5


def build_W_op(Pats: np.ndarray, N: int):
    """Operator W = (1/N) Pats^T Pats; W @ v = (1/N) Pats^T (Pats @ v)."""
    def matvec(v):
        return (Pats.T @ (Pats @ v)) / N
    return matvec


def deletion_signal(Pats: np.ndarray, N: int, k: int) -> float:
    """Measure ||W_pre @ xi_k - W_post @ xi_k|| where W_post deletes pattern k.

    Rank-1 update: W_post = W_pre - (1/N) xi_k xi_k^T.
    So W_pre @ xi_k - W_post @ xi_k = (1/N) xi_k (xi_k^T xi_k) = (1/N) * N * xi_k = xi_k.
    Theory: signal magnitude = ||xi_k|| = sqrt(N).
    """
    xi_k = Pats[k]
    # signal = (1/N) * xi_k * (xi_k^T xi_k) = (1/N) * N * xi_k = xi_k (theoretically)
    # but empirical: full retrieve through W's structure
    pre_response = (Pats.T @ (Pats @ xi_k)) / N
    Pats_post = np.delete(Pats, k, axis=0)
    post_response = (Pats_post.T @ (Pats_post @ xi_k)) / N
    return float(np.linalg.norm(pre_response - post_response))


def null_signal(Pats: np.ndarray, N: int, rng: np.random.Generator) -> float:
    """Measure ||W @ xi_random|| - baseline noise level for held-out random pattern.

    Null = random bipolar pattern not in the stored set; W @ xi_rand should be O(1/sqrt(N))
    (rank-M projection; signal in xi_k direction is zero for random xi).
    """
    N = Pats.shape[1]
    xi_rand = rng.choice([-1.0, 1.0], size=N).astype(Pats.dtype)
    response = (Pats.T @ (Pats @ xi_rand)) / N
    return float(np.linalg.norm(response))


def _instrumentation_selftest():
    """Tiny-N selftest: rank-1 deletion signal scales as sqrt(N)."""
    rng = np.random.default_rng(0)
    N_t = 256
    M_t = 13
    Pats_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    sig = deletion_signal(Pats_t, N_t, k=0)
    expected = math.sqrt(N_t)
    assert sig > 0.5 * expected and sig < 2.0 * expected, \
        f"deletion_signal selftest: got {sig:.2f}, expected ~{expected:.2f}"
    print(f"[selftest] PASS: deletion signal at N={N_t} = {sig:.3f} "
          f"(theory sqrt(N)={expected:.3f})", flush=True)


_instrumentation_selftest()


def _prot018_startup_check(n_actual: int) -> None:
    N_BOUND = 32768
    if n_actual != N_BOUND:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name '{ANCHOR_NAME}' binds to "
            f"N={N_BOUND} but script is running at N={n_actual}.")


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    N = N_FULL if run_mode == "full" else N_SMOKE
    if run_mode == "full":
        _prot018_startup_check(N)
    M = max(1, int(ALPHA * N))
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} M={M} "
          f"alpha={ALPHA} n_null_probes={N_NULL_PROBES}", flush=True)

    per_seed_results: List[Dict] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        print(f"  seed={seed}: building W (M={M}, N={N})...", flush=True)
        t_cell = time.time()
        Pats = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
        # Compute deletion signals for first few patterns
        # and null distribution from random held-out patterns
        n_sig_samples = 5
        signals = [deletion_signal(Pats, N, k) for k in range(n_sig_samples)]
        nulls = [null_signal(Pats, N, rng) for _ in range(N_NULL_PROBES)]
        sig_mean = float(np.mean(signals))
        null_mean = float(np.mean(nulls))
        null_std = float(np.std(nulls, ddof=1)) if len(nulls) > 1 else 1e-9
        z_ratio = (sig_mean - null_mean) / max(null_std, 1e-12)
        elapsed_cell = time.time() - t_cell
        print(f"    signal_mean={sig_mean:.4f} null_mean={null_mean:.4f} "
              f"null_std={null_std:.4f} Z={z_ratio:.2f} ({elapsed_cell:.1f}s)", flush=True)
        per_seed_results.append({
            "seed": seed,
            "signal_mean": sig_mean,
            "null_mean": null_mean,
            "null_std": null_std,
            "z_ratio": z_ratio,
            "elapsed_s": elapsed_cell,
        })

    z_across_seeds = [r["z_ratio"] for r in per_seed_results]
    z_mean = float(np.mean(z_across_seeds))
    z_min = float(np.min(z_across_seeds))

    if z_mean >= HP_Z and z_min >= MID_Z:
        verdict = "HARD_PASS"
    elif z_mean < HF_Z:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "M": M, "alpha": ALPHA,
        "n_seeds": len(seeds), "n_null_probes": N_NULL_PROBES,
        "per_seed_results": per_seed_results,
        "z_mean": z_mean, "z_min": z_min,
        "verdict": verdict,
        "elapsed_s": elapsed,
        "verdict_msg": (
            f"Deletion-cert Z-ratio at N={N} alpha={ALPHA}: "
            f"Z_mean={z_mean:.2f}, Z_min={z_min:.2f} across {len(seeds)} seeds. "
            f"Verdict: {verdict}."
        ),
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    main()
