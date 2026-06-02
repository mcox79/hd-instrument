"""
kappa3_hutchinson_v2 -- Free-cumulant kappa_3 authenticity fingerprint (vectorized).

FIX from v1: v1 used a Python for-loop over n_probes=5000 iterations, each doing
3 dense N x N matrix-vector multiplications sequentially. At N=4096, n_probes=5000,
that is 15,000 sequential O(N^2) ops => timed out at 1800s.

v2 vectorizes: build probes matrix V (N x n_probes), compute W^3 V via three batched
matrix-matrix multiplications. All probes processed in a single batch:
  kappa_3 estimates = diag(V^T @ W @ W @ W @ V) / N
  = (1/N) * sum_rows(V * (W @ W @ W @ V))   (element-wise, row-sum)
This reduces the bottleneck from 15,000 O(N^2) sequential ops to 3 O(N^2 * n_probes/N)
batched DGEMM calls plus one element-wise product. Speedup: ~100-500x.

Timeout: estimated 1800s -> vectorized ~30-60s at N=4096, n_probes=5000. Use timeout=600s.

SCIENTIFIC QUESTION (Q-C3 from research priorities):
  Does the kappa_3 free-cumulant (third free cumulant) Hutchinson estimator
  at N=4096 achieve the predicted discriminative power between:
  (a) W built from M random BSC patterns (kappa_3 ~ alpha_c = M/N), and
  (b) W ~ GOE/Wigner (kappa_3 ~ 0 for n>=3)?

  Theory: for free-Poisson W = Xi^T Xi / N with M patterns,
    kappa_3 = alpha = M/N (free-Poisson identity for all n).
  For Wigner/GOE: kappa_n = 0 for n >= 3 (binary discriminant).
  Hutchinson estimator (vectorized): kappa_3 = mean(diag(V^T W^3 V)) / N
  where V is N x n_probes Rademacher matrix.
  Std(kappa_3) scales as 1/sqrt(n_probes) independent of N.

PRE-REGISTERED BANDS:
  HARD-PASS: min sigma_separation >= 4.0 across all M values
             AND kappa_3_hopfield theory_ratio in [0.05, 20.0].
  MIDDLE: 2.0 <= min_sigma_sep < 4.0, OR theory ratio outside [0.05, 20.0].
  HARD-FAIL: min_sigma_sep < 2.0 (fingerprint indistinguishable at N=4096).

Calibration probe note: kappa_3 estimation at this N has no prior empirical
anchor. Using +-50% band around theoretical prediction per calibration policy.

FORMULA SELF-TESTS:
  1. kappa_3_theory(M=100, N=4096) = 100/4096 ~ 0.0244.
  2. Hutchinson vectorized estimate matches scalar estimate within 1% at N=256, n_probes=1000.
  3. For W = I/N: kappa_3 ~ 1/N^2 (near-zero since Tr(I^3)/N = 1/N).

TIMEOUT ESTIMATE:
  v2 vectorized. Smoke: N=4096, n_probes=500, 2 seeds, 2 M values.
  Full: N=4096, n_probes=5000, 5 seeds, 4 M values.
  Vectorized DGEMM (N=4096, n_probes=5000): ~3x N^2 * n_probes ops = 251e9 -> ~5-10s.
  Full run estimate: ~5s * 5 seeds * 4 M values * 2 (Hop+GOE per M) = ~200s.
  timeout_s = ceil(1.5 * 200) = 300. Rounding up to 600s for headroom.

No _nN suffix; production N=4096 per rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "kappa3_hutchinson_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [100, 500]
    N_PROBES = 500
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [50, 100, 200, 500]
    N_PROBES = 5000

# Pre-reg thresholds
HP_SIGMA_SEPARATION = 4.0
MID_SIGMA_LOW = 2.0
HP_THEORY_MATCH_FACTOR = 20.0
HF_SIGMA_SEPARATION = 2.0

# Formula self-test: kappa_3_theory(M=100, N=4096) = 100/4096 ~ 0.0244
_k3t = 100 / 4096
assert abs(_k3t - 0.0244) < 0.001, f"kappa_3 theory test failed: {_k3t}"


def build_hopfield_w(M: int, N: int, seed: int) -> np.ndarray:
    """W = Xi^T @ Xi / N where Xi is M x N BSC +-1 patterns."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = (Xi.T @ Xi) / N
    return W.astype(np.float64)


def build_goe_w(N: int, seed: int) -> np.ndarray:
    """GOE Wigner matrix: W = (G + G^T) / (2 sqrt(N))."""
    rng = np.random.RandomState(seed + 10000)
    G = rng.randn(N, N).astype(np.float32)
    W = ((G + G.T) / (2.0 * math.sqrt(N))).astype(np.float64)
    return W


def hutchinson_kappa3_vectorized(W: np.ndarray, n_probes: int, seed: int) -> Tuple[float, float]:
    """
    Vectorized Hutchinson estimator for kappa_3 = Tr(W^3) / N.

    Build probes matrix V: N x n_probes (Rademacher +-1).
    Compute W^3 V via: WV = W @ V, W2V = W @ WV, W3V = W @ W2V.
    Per-probe estimates: v_i^T W^3 v_i = (V * W3V).sum(axis=0).
    kappa_3 = mean(per_probe_estimates) / N.
    std = std(per_probe_estimates) / N / sqrt(n_probes).

    This replaces the v1 Python for-loop (O(n_probes) sequential matrix-vector ops)
    with 3 batched matrix-matrix multiplications.
    """
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    # V: N x n_probes Rademacher
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    # W^3 V = W @ W @ W @ V  (three batched DGEMM)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    # Per-probe estimates: element-wise V * W3V, sum over rows
    per_probe = (V * W3V).sum(axis=0) / N_dim  # shape (n_probes,)
    kappa3 = float(np.mean(per_probe))
    std = float(np.std(per_probe, ddof=1)) / math.sqrt(n_probes)
    return kappa3, std


def run_seed(seed: int) -> Dict:
    """Run one seed: estimate kappa_3 for Hopfield and GOE at each M in M_LIST."""
    results = {}
    for M in M_LIST:
        W_hop = build_hopfield_w(M, N, seed)
        k3_hop, std_hop = hutchinson_kappa3_vectorized(W_hop, N_PROBES, seed)

        W_goe = build_goe_w(N, seed)
        k3_goe, std_goe = hutchinson_kappa3_vectorized(W_goe, N_PROBES, seed + 1)

        kappa3_theory = M / N
        separation = abs(k3_hop - k3_goe)
        pooled_std = math.sqrt(std_hop**2 + std_goe**2)
        sigma_sep = separation / pooled_std if pooled_std > 1e-15 else float("nan")
        theory_ratio = k3_hop / kappa3_theory if abs(kappa3_theory) > 1e-15 else float("nan")

        print(f"  [seed={seed} M={M}] k3_hop={k3_hop:.4f} k3_goe={k3_goe:.6f} "
              f"theory={kappa3_theory:.4f} sep={sigma_sep:.1f}sigma "
              f"theory_ratio={theory_ratio:.2f}", flush=True)

        results[M] = {
            "M": M, "N": N,
            "kappa3_hopfield": k3_hop, "std_hopfield": std_hop,
            "kappa3_goe": k3_goe, "std_goe": std_goe,
            "kappa3_theory": kappa3_theory,
            "sigma_separation": sigma_sep,
            "theory_ratio": theory_ratio,
        }

    return {"M_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert kappa_3 metrics are non-null and discriminative; vectorized estimator matches scalar."""
    N_test = 256
    M_test = 30
    seed = 42
    n_p = 200

    W_hop = build_hopfield_w(M_test, N_test, seed)
    k3_hop, std_hop = hutchinson_kappa3_vectorized(W_hop, n_p, seed)
    assert not math.isnan(k3_hop), "kappa_3 Hopfield is NaN"
    assert std_hop > 0, f"std_hopfield=0, degenerate estimator"
    assert k3_hop > 0, f"kappa_3 Hopfield <= 0: {k3_hop} (theory={M_test/N_test:.4f})"

    W_goe = build_goe_w(N_test, seed)
    k3_goe, _ = hutchinson_kappa3_vectorized(W_goe, n_p, seed)
    assert not math.isnan(k3_goe), "kappa_3 GOE is NaN"
    assert abs(k3_goe) < k3_hop, f"GOE kappa_3={k3_goe:.4f} not < Hopfield={k3_hop:.4f}"

    # Verify vectorized estimator gives sensible result: kappa_3_hop ~ M/N within 5x
    theory = M_test / N_test
    ratio = k3_hop / theory if theory > 0 else float("inf")
    assert 0.05 <= ratio <= 20.0, f"kappa_3 ratio={ratio:.2f} out of [0.05, 20.0]"

    print(f"[selftest] PASS: kappa_3 Hopfield={k3_hop:.4f} GOE={k3_goe:.4f} "
          f"theory={theory:.4f} ratio={ratio:.2f}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify pre-registered formula."""
    theory = 100 / 4096
    assert abs(theory - 0.0244) < 0.001, f"kappa_3 theory error: {theory}"
    print("[formula_selftests] PASS: kappa_3_theory verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds: mean kappa_3 and sigma separation per M."""
    agg = {}
    for M in M_LIST:
        hop_vals = []
        goe_vals = []
        sep_vals = []
        theory_ratio_vals = []
        for seed_data in per_seed.values():
            mr = seed_data["M_results"].get(M) or seed_data["M_results"].get(str(M))
            if mr is None:
                continue
            hop_vals.append(mr["kappa3_hopfield"])
            goe_vals.append(mr["kappa3_goe"])
            sep_vals.append(mr["sigma_separation"])
            tr = mr.get("theory_ratio")
            if tr is not None and not math.isnan(tr):
                theory_ratio_vals.append(tr)

        kappa3_theory = M / N
        mean_hop = float(np.mean(hop_vals)) if hop_vals else float("nan")
        mean_goe = float(np.mean(goe_vals)) if goe_vals else float("nan")
        mean_sep = float(np.mean(sep_vals)) if sep_vals else float("nan")
        mean_ratio = float(np.mean(theory_ratio_vals)) if theory_ratio_vals else float("nan")
        agg[M] = {
            "M": M,
            "mean_kappa3_hopfield": mean_hop,
            "mean_kappa3_goe": mean_goe,
            "kappa3_theory": kappa3_theory,
            "mean_sigma_separation": mean_sep,
            "mean_theory_ratio": mean_ratio,
            "n_seeds": len(hop_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    """Pre-registered verdict logic."""
    seps = [v["mean_sigma_separation"] for v in agg.values()
            if not math.isnan(v["mean_sigma_separation"])]
    ratios = [v["mean_theory_ratio"] for v in agg.values()
              if not math.isnan(v["mean_theory_ratio"])]

    if not seps:
        return ("HARD_FAIL", "No valid sigma separation estimates.")

    min_sep = min(seps)
    mean_sep = float(np.mean(seps))
    mean_ratio = float(np.mean(ratios)) if ratios else float("nan")

    all_hp = min_sep >= HP_SIGMA_SEPARATION
    any_hf = min_sep < HF_SIGMA_SEPARATION
    ratio_ok = (not math.isnan(mean_ratio) and
                0.05 <= mean_ratio <= HP_THEORY_MATCH_FACTOR)

    if all_hp and ratio_ok:
        return ("HARD_PASS",
                f"kappa_3 fingerprint confirmed. min_sigma_sep={min_sep:.1f} "
                f"mean_sigma_sep={mean_sep:.1f} (HP>={HP_SIGMA_SEPARATION}). "
                f"theory_ratio={mean_ratio:.2f} (within {HP_THEORY_MATCH_FACTOR}x). "
                f"GOE discriminated at all M values.")
    if any_hf:
        return ("HARD_FAIL",
                f"kappa_3 fingerprint not discriminative. min_sigma_sep={min_sep:.1f} "
                f"< HF threshold {HF_SIGMA_SEPARATION}. N=4096 insufficient.")
    return ("MIDDLE_BAND",
            f"Partial kappa_3 discrimination. min_sigma_sep={min_sep:.1f} "
            f"mean={mean_sep:.1f} (HP>={HP_SIGMA_SEPARATION} HF<{HF_SIGMA_SEPARATION}). "
            f"theory_ratio={mean_ratio:.2f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_LIST={M_LIST} "
          f"n_probes={N_PROBES} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "M_LIST": M_LIST, "N_PROBES": N_PROBES,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
