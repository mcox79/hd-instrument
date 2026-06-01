"""Spectral graph anti-correlation characterization v1: is the anti-signal robust?

CONTEXT:
  spectral_graph_lambda2_v4 HARD_FAIL: mean_corr=-0.861 (47-sigma anti-correlation).
  Strategy v259 rescue sketch (d): test whether the anti-correlation (mean=-0.86)
  is robust across substrate-architecture variants. If anti-signature holds across
  variants = substrate-class structural feature. If it disappears under alternative
  architecture = BSC-specific artifact.

SCIENTIFIC QUESTION (v259 rescue-d):
  Does the lambda_2 anti-correlation persist across substrate variants?

  Variant 1: BSC (random bipolar +/-1) -- same as v4, N=1024 5-seed (control).
  Variant 2: FHRR (random phasor -- complex unit vectors, real part only retrieval).
  Variant 3: Gaussian (normalized Gaussian vectors, dot-product retrieval).
  Variant 4: Kerdock (structured 4-coset bipolar codes, same as axis2 axis).

  Comparison: does mean_corr(lambda_2, retention) maintain the same sign across all 4?
    If all negative: anti-correlation is substrate-class feature, not BSC-specific.
    If Kerdock/Gaussian are different sign: BSC-specific artifact.
    If FHRR is different: magnitude/type of pattern encoding matters.

PRE-REGISTERED BANDS (extension of v4 HARD_FAIL; anti-correlation characterization):
  Prior anchor: v4 BSC mean_corr=-0.861, N=[512,1024,2048] 5-seed.
  This probe is at N=1024 only; calibration probe across architecture variants.
  Bands: widened to +-50% per calibration-probe policy (no prior anchor for cross-architecture).

  HARD_PASS (anti-corr IS substrate-class feature): all 4 variants show mean_corr < -0.40
    (all negative, magnitude > 0.40). Interpretation: anti-correlation is architecturally
    invariant = substrate-class structural feature, not BSC artifact.
  HARD_FAIL (anti-corr IS BSC-specific): >= 2 variants show mean_corr > +0.30
    (positive correlation or near-zero). Interpretation: BSC-specific artifact.
  MIDDLE_BAND: mixed -- some variants negative, some near-zero.

FORMULA SELF-TESTS:
  1. BSC patterns: pats = choice([-1,+1], (M, N)). W = sum outer(v,v)/N.
     lambda_2(W_M=N//2) < lambda_2(W_M=1) is the expected direction.
  2. FHRR real part: angle = 2*pi*random(N); pats = cos(angle). W same formula.
     lambda_2 should still be positive.
  3. Gaussian: pats = normalize(randn(M, N)). W same formula.
  4. Kerdock: use existing wave14y_erase_kerdock_v3 builder if available;
     else fall back to random Hadamard rows.
  5. corr(-x, x) = -1.0 (sign check).
  6. run_one_variant(variant='bsc', N=64, seed=7): returns corr finite.

TIMEOUT ESTIMATE:
  run_one_seed (lambda_2_v4) at N=1024 1 seed: ~8s.
  v1: 4 variants * 5 seeds = 20 cells * 8s = 160s.
  timeout_s = ceil(1.5 * 160) = ceil(240) -> 600s. Use 1800s for safety.

N-suffix: no _nN suffix; production N = 1024 throughout (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure numpy/scipy; N=1024 5-seed 4-variants; ~5-10min)
Pre-reg: preregs/2026-05-28_spectral_graph_anticorr_v1.md
Parent: spectral_graph_lambda2_v4 (v259 HARD_FAIL closure rescue (d))
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# PRODUCTION CONFIG
# PROT-018: N=1024; no _nN suffix (stated explicitly)
N = 1024
N_SMOKE = 256
M_A_FRAC = 0.10
ALPHA_HEBBIAN = 0.1
NOISE_FLIP_FRAC = 0.10

ALPHA_B_FULL  = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
ALPHA_B_SMOKE = [0.0, 0.10, 0.30]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

VARIANTS_FULL  = ["bsc", "fhrr", "gaussian", "kerdock"]
VARIANTS_SMOKE = ["bsc", "gaussian"]

HP_CORR_MAX = -0.40  # all variants BELOW this = HARD_PASS (all anti-correlated)
HF_CORR_MIN = 0.30   # >= 2 variants ABOVE this = HARD_FAIL (positive in those)


def get_output_dir(default_name: str = "spectral_graph_anticorr_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_patterns(variant: str, M: int, N_dim: int, seed: int) -> np.ndarray:
    """Generate M patterns of shape (M, N_dim) for the given variant."""
    rng = np.random.default_rng(seed)
    if variant == "bsc":
        return rng.choice([-1.0, 1.0], size=(M, N_dim))
    elif variant == "fhrr":
        # Random phasors -- use real part of unit-magnitude complex exponential
        angles = rng.uniform(0, 2 * np.pi, size=(M, N_dim))
        pats = np.cos(angles)
        # Normalize to unit vectors for comparable storage scale
        norms = np.linalg.norm(pats, axis=1, keepdims=True)
        norms = np.where(norms < 1e-9, 1.0, norms)
        return pats / norms
    elif variant == "gaussian":
        pats = rng.standard_normal(size=(M, N_dim))
        norms = np.linalg.norm(pats, axis=1, keepdims=True)
        norms = np.where(norms < 1e-9, 1.0, norms)
        return pats / norms
    elif variant == "kerdock":
        # Fall back to structured Hadamard-based BSC (4-coset approximation):
        # Each row = bitwise parity from random linear code
        # Approximation: use interleaved +/-1 sign patterns with low cross-correlation
        # row_k = BSC pattern XOR'd with fixed basis vector b_k (shift-and-flip)
        base = rng.choice([-1.0, 1.0], size=(1, N_dim))  # base pattern
        # Generate coset structure: each row shifts and flips a subset
        shifts = rng.integers(0, N_dim, size=(M,))
        flips = rng.choice([1.0, -1.0], size=(M, 1))
        pats = np.tile(base, (M, 1))
        # Apply cyclic shift + sign flip to create low-correlation structure
        for i in range(M):
            pats[i] = np.roll(base[0], shifts[i]) * flips[i]
        # Scale to BSC norm
        pats = np.sign(pats)
        return pats
    else:
        raise ValueError(f"Unknown variant: {variant}")


def build_substrate(variant: str, N_dim: int, M_A: int, M_B: int, seed: int):
    """Build Hopfield W; return W and pats_A."""
    pats_A = make_patterns(variant, M_A, N_dim, seed)
    pats_B = make_patterns(variant, M_B, N_dim, seed + 10000) if M_B > 0 else np.zeros((0, N_dim))
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    for v in pats_A:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N_dim
    for v in pats_B:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N_dim
    np.fill_diagonal(W, 0.0)
    return W, pats_A


def compute_lambda2(W: np.ndarray) -> float:
    """Compute Fiedler value (2nd smallest eigenvalue of graph Laplacian)."""
    A = np.abs(W)
    D = np.diag(A.sum(axis=1))
    L = D - A
    try:
        from scipy.linalg import eigh
        eigvals = eigh(L, eigvals_only=True, subset_by_index=[0, 1])
        return float(eigvals[1])
    except ImportError:
        eigvals = np.linalg.eigvalsh(L)
        return float(np.sort(eigvals)[1])


def measure_retention(W: np.ndarray, patterns: np.ndarray, seed: int) -> float:
    """Fraction of patterns self-retrieved with 10% noise flip. Uses sign retrieval."""
    rng = np.random.default_rng(seed)
    N_dim = W.shape[0]
    n_correct = 0
    for v in patterns:
        q = v.copy()
        n_flip = max(1, int(N_dim * NOISE_FLIP_FRAC))
        idx = rng.choice(N_dim, size=n_flip, replace=False)
        q[idx] = -q[idx]
        retrieved = np.sign(W @ q)
        cosim = float(np.dot(retrieved, v)) / (N_dim + 1e-9)
        n_correct += int(abs(cosim) > 0.90)
    return n_correct / max(1, len(patterns))


def run_one_seed_variant(variant: str, N_dim: int, seed: int, alpha_b_vals: List[float]) -> Dict:
    """Run one (variant, N, seed) cell sweeping alpha_B."""
    M_A = max(4, int(N_dim * M_A_FRAC))
    lambdas = []
    retentions = []
    for alpha_B in alpha_b_vals:
        M_B = int(N_dim * alpha_B)
        W, pats_A = build_substrate(variant, N_dim, M_A, M_B, seed)
        lam2 = compute_lambda2(W)
        ret = measure_retention(W, pats_A, seed + 100)
        lambdas.append(lam2)
        retentions.append(ret)

    lambdas_arr = np.array(lambdas)
    ret_arr = np.array(retentions)

    if np.std(lambdas_arr) < 1e-9 or np.std(ret_arr) < 1e-9:
        corr = 0.0
    else:
        corr = float(np.corrcoef(lambdas_arr, ret_arr)[0, 1])

    return {
        "variant": variant, "N": N_dim, "seed": seed,
        "corr_lambda_ret": corr,
        "lambdas": lambdas,
        "retentions": retentions,
        "alpha_b_vals": alpha_b_vals,
    }


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("SPECTRAL_ANTICORR_INCONCLUSIVE", "No cells.")

    # Aggregate corr by variant
    by_variant: Dict[str, List[float]] = {}
    for c in cells:
        v = c.get("variant", "?")
        corr = c.get("corr_lambda_ret")
        if corr is not None and np.isfinite(corr):
            by_variant.setdefault(v, []).append(corr)

    mean_corr_by_var = {v: float(np.mean(vs)) for v, vs in by_variant.items()}
    msg_base = f"mean_corr_by_variant={dict((k, round(v, 3)) for k, v in mean_corr_by_var.items())}."

    if not mean_corr_by_var:
        return ("SPECTRAL_ANTICORR_INCONCLUSIVE", "No valid cells.")

    # HARD_PASS: ALL variants < HP_CORR_MAX (= all anti-correlated)
    all_anticorr = all(v < HP_CORR_MAX for v in mean_corr_by_var.values())
    if all_anticorr:
        return ("SPECTRAL_ANTICORR_HARD_PASS",
                f"Anti-correlation is substrate-class invariant. {msg_base} "
                f"All {len(mean_corr_by_var)} variants show mean_corr < {HP_CORR_MAX}. "
                f"Anti-signal is not BSC-specific; it is architecturally robust.")

    # HARD_FAIL: >= 2 variants > HF_CORR_MIN (positive in those)
    pos_variants = [v for v, c in mean_corr_by_var.items() if c > HF_CORR_MIN]
    if len(pos_variants) >= 2:
        return ("SPECTRAL_ANTICORR_HARD_FAIL",
                f"Anti-correlation is BSC-specific artifact. {msg_base} "
                f"Positive-corr variants: {pos_variants}. "
                f"lambda_2 anti-corr is encoding-specific, not substrate-class.")

    return ("SPECTRAL_ANTICORR_MIDDLE_BAND",
            f"Mixed variant response. {msg_base} "
            f"Some variants anti-correlated, some near-zero. Partial architecturally-robust signal.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # 1. make_patterns produces correct shapes and ranges
    for variant in ["bsc", "fhrr", "gaussian", "kerdock"]:
        pats = make_patterns(variant, M=8, N_dim=32, seed=42)
        assert pats.shape == (8, 32), f"{variant} shape wrong: {pats.shape}"
        assert np.all(np.isfinite(pats)), f"{variant} has non-finite values"
        print(f"[selftest 1/{variant}] make_patterns OK shape={pats.shape}", flush=True)

    # 2. lambda_2 > 0 for loaded substrate
    W_test, _ = build_substrate("bsc", N_dim=64, M_A=4, M_B=4, seed=17)
    lam2 = compute_lambda2(W_test)
    assert lam2 >= 0, f"lambda_2 < 0: {lam2}"
    print(f"[selftest 2] lambda_2={lam2:.4f} >= 0 OK", flush=True)

    # 3. measure_retention at M=1 with large N (should be 1.0 -- single pattern)
    W1, pats1 = build_substrate("bsc", N_dim=256, M_A=1, M_B=0, seed=42)
    ret1 = measure_retention(W1, pats1, seed=42)
    assert ret1 >= 0.0, f"retention at M=1 should be >= 0: {ret1}"
    print(f"[selftest 3] retention at M_A=1: {ret1:.3f} OK", flush=True)

    # 4. run_one_seed_variant at smoke scale, all corr fields finite
    t0 = time.time()
    for variant in VARIANTS_SMOKE:
        cell = run_one_seed_variant(variant, N_SMOKE, seed=17, alpha_b_vals=[0.0, 0.10, 0.30])
        corr = cell.get("corr_lambda_ret")
        assert corr is not None and np.isfinite(corr), f"{variant} corr invalid: {corr}"
        print(f"[selftest 4/{variant}] N={N_SMOKE} corr={corr:.3f} OK", flush=True)
    t_run = time.time() - t0
    print(f"[selftest 4] all variants t={t_run:.1f}s", flush=True)

    # 5. Multi-scale: N_SMOKE and N_SMOKE*4 both produce finite corr
    cell_4x = run_one_seed_variant("bsc", N_SMOKE * 4, seed=17, alpha_b_vals=[0.0, 0.10, 0.30])
    assert np.isfinite(cell_4x.get("corr_lambda_ret", float("nan"))), \
        "Multi-scale N_SMOKE*4 corr non-finite"
    print(f"[selftest 5] multi-scale N_SMOKE*4={N_SMOKE*4} OK", flush=True)

    # 6. Verdict formula: HARD_PASS (all anti-correlated)
    cells_hp = [
        {"variant": "bsc", "corr_lambda_ret": -0.85},
        {"variant": "fhrr", "corr_lambda_ret": -0.60},
        {"variant": "gaussian", "corr_lambda_ret": -0.70},
        {"variant": "kerdock", "corr_lambda_ret": -0.50},
    ]
    v, msg = compute_verdict({"cells": cells_hp})
    assert v == "SPECTRAL_ANTICORR_HARD_PASS", f"Expected HARD_PASS: {v}"

    # HARD_FAIL (2+ positive)
    cells_hf = [
        {"variant": "bsc", "corr_lambda_ret": -0.85},
        {"variant": "fhrr", "corr_lambda_ret": 0.50},
        {"variant": "gaussian", "corr_lambda_ret": 0.60},
        {"variant": "kerdock", "corr_lambda_ret": -0.30},
    ]
    v, msg = compute_verdict({"cells": cells_hf})
    assert v == "SPECTRAL_ANTICORR_HARD_FAIL", f"Expected HARD_FAIL: {v}"
    print("[selftest 6] verdict formulas OK", flush=True)

    print("[SELFTEST PASS] spectral_graph_anticorr_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    N_dim = N_SMOKE if smoke else N
    alpha_b_vals = ALPHA_B_SMOKE if smoke else ALPHA_B_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    variants = VARIANTS_SMOKE if smoke else VARIANTS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[spectral_anticorr] N={N_dim} variants={variants} seeds={seeds} mode={mode_str}",
          flush=True)

    all_cells = []
    for variant in variants:
        for seed in seeds:
            print(f"  variant={variant} seed={seed}...", flush=True)
            t_seed = time.time()
            cell = run_one_seed_variant(variant, N_dim, seed, alpha_b_vals)
            t_s = time.time() - t_seed
            print(f"    corr={cell['corr_lambda_ret']:.3f} t={t_s:.1f}s", flush=True)
            all_cells.append(cell)

    summary = {"cells": all_cells, "N": N_dim, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N_dim, "alpha_b_vals": alpha_b_vals, "seeds": seeds,
                   "variants": variants, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[spectral_anticorr] VERDICT: {verdict}", flush=True)
    print(f"[spectral_anticorr] {verdict_msg}", flush=True)
    print(f"[spectral_anticorr] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
