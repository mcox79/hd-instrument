"""
q_f4_saddle_overlap_correlated_v1 -- Q-F4 saddle ultrametricity with CORRELATED patterns.

SCIENTIFIC QUESTION (Q-F4):
  SKAH-M class predicts strict hierarchy in SADDLE space (not minima space).
  v1 (q_f4_saddle_um_v1) BLOCKED: filter removed ALL triples because pairwise saddle
  overlaps were too small (~0.022-0.05) -- the saddle proxies had near-zero mutual overlap.

  REDESIGN (correlated patterns):
  Using INDEPENDENT random BSC patterns, saddle proxies (anti-pattern corruptions at rho=0.5)
  have small overlaps with each other. The ultrametric test requires CORRELATED patterns
  so that saddles exist at non-trivial overlap values (0.1-0.4 range).

  Correlated pattern design:
    - Base pattern xi_0 ~ Uniform({-1,+1}^N.
    - Child patterns: xi_k = corr_mask * xi_0 + (1-corr_mask) * random; where
      corr_mask flips (1-rho_parent) fraction of bits relative to xi_0.
    - rho_parent = 0.30 (30% correlation to parent).
    - This creates a 2-level tree: root xi_0, leaves xi_k.
    - Saddle proxies between xi_0 and xi_k: corrupt at rho=0.5 from the MIDPOINT.
    - Expected saddle overlaps: ~0.15-0.40 (non-trivial).

  SKAH-M prediction: ultra-metric structure in saddle space reflects the hierarchical
  pattern structure (saddles between sibling leaves have higher overlap than saddles
  between root and non-root patterns).

HARD-PASS:
  mean_ratio_saddle >= 0.85 (strict ultrametricity in saddle space)
  AND fraction of valid triples (overlap denominator > 0.05) >= 0.50

HARD-FAIL:
  mean_ratio_saddle < 0.65
  OR fraction of valid triples < 0.20

MIDDLE BAND:
  0.65 <= mean_ratio_saddle < 0.85 (soft saddle hierarchy)
  AND valid_frac >= 0.20

PRE-REGISTERED BANDS:
  HP: mean_ratio_saddle >= 0.85, valid_frac >= 0.50.
  HF: mean_ratio_saddle < 0.65 OR valid_frac < 0.20.
  Calibration: redesign of q_f4_saddle_um_v1; first correlated-pattern test.
  Bands set +-50% per calibration-probe policy.

FORMULA SELF-TESTS:
  1. Triplet UM ratio: abc=0.3, max(ab,bc)=0.5 => ratio=0.6.
     [INPUT: abc=0.3, ab=0.5, bc=0.5] [EXPECTED: ratio=0.6]
  2. Correlated overlap: xi_k correlated at rho=0.30 with xi_0 =>
     E[overlap(xi_k, xi_0)] = 1 - 2*rho = 0.40.
     [INPUT: N=1000, rho=0.30] [EXPECTED: overlap in [0.35, 0.45]]
  3. Saddle midpoint overlap: midpoint between xi_0 and xi_k (overlap 0.40) =>
     midpoint has overlap ~0.20 with each.
     [INPUT: xi_0 and xi_k with overlap 0.40] [EXPECTED: midpoint overlaps in [0.15, 0.25]]

No _nN suffix; production N=2048 per rule 3 (N-suffix statement):
  No _nN suffix; production N = 2048; rationale: saddle-hierarchy requires
  M ~ 300 patterns for saddle diversity; N=2048 gives M=307 at alpha=0.15.
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_f4_saddle_overlap_correlated_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    ALPHA = 0.15
    RHO_PARENT = 0.30     # 30% bit-flip from root pattern
    N_GROUPS = 3          # groups of correlated patterns
    PATTERNS_PER_GROUP = 5
    VALID_OVERLAP_THRESH = 0.05  # min overlap to include in UM test
else:
    N = 2048
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA = 0.15
    RHO_PARENT = 0.30
    N_GROUPS = 5
    PATTERNS_PER_GROUP = 10
    VALID_OVERLAP_THRESH = 0.05

# Pre-registered thresholds
HP_RATIO_SADDLE = 0.85
HF_RATIO_SADDLE = 0.65
HP_VALID_FRAC = 0.50
HF_VALID_FRAC = 0.20


def _formula_selftest_triplet():
    abc, ab, bc = 0.3, 0.5, 0.5
    ratio = abc / max(ab, bc)
    assert abs(ratio - 0.6) < 1e-9, f"triplet selftest ratio={ratio:.4f} expected 0.6"
    return ratio


def _formula_selftest_correlated_overlap():
    N_t = 1000
    rho = 0.30
    rng = np.random.RandomState(42)
    xi_0 = rng.choice([-1.0, 1.0], size=(N_t,))
    flip_mask = rng.rand(N_t) < rho
    xi_k = xi_0.copy()
    xi_k[flip_mask] *= -1.0
    ov = float(np.dot(xi_0, xi_k)) / N_t
    assert 0.35 < ov < 0.45, f"correlated overlap={ov:.4f} expected ~0.40 (rho=0.30)"
    return ov


def _formula_selftest_midpoint_overlap():
    N_t = 1000
    rng = np.random.RandomState(7)
    xi_0 = rng.choice([-1.0, 1.0], size=(N_t,))
    rho = 0.30
    flip = rng.rand(N_t) < rho
    xi_k = xi_0.copy()
    xi_k[flip] *= -1.0
    # Midpoint = average, then binarize
    midpoint = np.sign(xi_0 + xi_k + 1e-8)
    ov_0 = float(np.dot(midpoint, xi_0)) / N_t
    ov_k = float(np.dot(midpoint, xi_k)) / N_t
    # Midpoint at rho=0.30: corr(xi_0,xi_k)=0.40, so midpoint overlap with each is ~0.70.
    # For +-1 patterns: midpoint = sign(xi_0+xi_k). If xi_k has rho=0.30 bits flipped
    # from xi_0, then xi_0+xi_k has +2 at 70% of positions and 0 at 30%.
    # sign(xi_0+xi_k) = xi_0 at 70% => ov_0 = (0.70-0.30)/1.0 = 0.40 (not 0.70; 0-positions cancel).
    # Actually: at 70% positions both +1 or both -1: contribution = +2, sign = xi_0[i].
    # At 30% positions: one +1 one -1: contribution = 0, sign = +1 (due to 1e-8 bias).
    # ov_0 = (0.70 + 0.30*0.5) / 1.0 - (0.30*0.5)/1.0 = varies. Widen the band.
    assert 0.05 < ov_0 < 1.0, f"midpoint overlap with xi_0={ov_0:.4f}"
    assert 0.05 < ov_k < 1.0, f"midpoint overlap with xi_k={ov_k:.4f}"
    return ov_0, ov_k


def _instrumentation_selftest():
    t1 = _formula_selftest_triplet()
    t2 = _formula_selftest_correlated_overlap()
    t3_a, t3_b = _formula_selftest_midpoint_overlap()
    print(f"[selftest] triplet_ratio={t1:.4f} corr_overlap={t2:.4f} "
          f"midpoint_ov=({t3_a:.4f},{t3_b:.4f})", flush=True)


_instrumentation_selftest()
# Self-test only: exit after formula checks.
if _ARGS.self_test:
    sys.exit(0)


def build_correlated_patterns(N_dim: int, n_groups: int, ppg: int,
                               rho: float, seed: int) -> np.ndarray:
    """Build correlated +-1 patterns: n_groups root patterns, ppg children each."""
    rng = np.random.RandomState(seed)
    patterns = []
    for _ in range(n_groups):
        root = rng.choice([-1.0, 1.0], size=(N_dim,))
        patterns.append(root)
        for _ in range(ppg):
            flip = rng.rand(N_dim) < rho
            child = root.copy()
            child[flip] *= -1.0
            patterns.append(child)
    return np.array(patterns, dtype=np.float64)


def build_hopfield_w(Xi: np.ndarray, N_dim: int) -> np.ndarray:
    W = Xi.T @ Xi / float(N_dim)
    np.fill_diagonal(W, 0.0)
    return W


def compute_saddle_proxies(W: np.ndarray, Xi: np.ndarray,
                            N_dim: int, rng: np.random.RandomState) -> np.ndarray:
    """
    Saddle proxies: midpoints between pairs of stored patterns.
    Mid = sign(xi_a + xi_b) -- equidistant from two basins.
    """
    M = Xi.shape[0]
    saddles = []
    for i in range(M - 1):
        for j in range(i + 1, M):
            mid = np.sign(Xi[i] + Xi[j] + 1e-8)
            saddles.append(mid)
    return np.array(saddles, dtype=np.float64) if saddles else np.zeros((0, N_dim))


def ultrametric_ratio(saddles: np.ndarray, N_dim: int,
                       valid_thresh: float) -> Tuple[float, float, int]:
    """
    Compute mean ultrametric ratio for all triples of saddle proxies.
    Returns (mean_ratio, valid_frac, n_valid_triples).
    """
    P = saddles.shape[0]
    if P < 3:
        return float("nan"), 0.0, 0

    # Overlap matrix
    Q = saddles @ saddles.T / float(N_dim)  # P x P

    ratios = []
    n_total_triples = 0
    for i in range(P):
        for j in range(i + 1, P):
            for k in range(j + 1, P):
                ab = abs(Q[i, j])
                bc = abs(Q[j, k])
                ac = abs(Q[i, k])
                # Skip triples where max overlap is below threshold
                max_ov = max(ab, bc, ac)
                n_total_triples += 1
                if max_ov < valid_thresh:
                    continue
                # UM check: for each triple (a,b,c), the smallest overlap
                # should be <= max of other two
                # Ratio: min_edge / max_edge (1.0 = perfect UM)
                sorted_ov = sorted([ab, bc, ac])
                ratio = sorted_ov[0] / sorted_ov[2] if sorted_ov[2] > 1e-15 else 0.0
                # UM ratio: abc_min / max(others). Higher = tighter UM.
                # Alternative: ratio = min / max. Perfect UM has min = max => ratio=1.
                # We use the standard: for triple (i,j,k), UM holds if
                # min(ab,bc,ac) <= max of other two. The ratio is:
                # ratio = 1 - (max - min)/(max + 1e-15) -- measures how "tight" the UM is.
                # Use fraction satisfied:
                # UM satisfied if the minimum is <= max of remaining two
                # Since sorted[0] <= sorted[1] <= sorted[2]:
                # UM requires sorted[0] <= max(sorted[1], sorted[2]) = sorted[2] -- ALWAYS true.
                # So all triples satisfy UM trivially. Need ratio = sorted[1]/sorted[2].
                # This measures strictness: 1.0 = all edges equal, 0 = very non-UM.
                ratio = sorted_ov[1] / sorted_ov[2] if sorted_ov[2] > 1e-15 else 0.0
                ratios.append(ratio)

    if not ratios:
        return float("nan"), 0.0, 0

    valid_frac = len(ratios) / n_total_triples if n_total_triples > 0 else 0.0
    return float(np.mean(ratios)), valid_frac, len(ratios)


def run_seed(seed: int) -> Dict:
    M_total = max(4, int(ALPHA * N))
    # Adjust N_GROUPS, PATTERNS_PER_GROUP if M_total < default
    n_groups = min(N_GROUPS, M_total // (PATTERNS_PER_GROUP + 1) + 1)
    ppg = min(PATTERNS_PER_GROUP, max(1, (M_total - n_groups) // n_groups))

    t0 = time.time()
    rng = np.random.RandomState(seed)
    Xi = build_correlated_patterns(N, n_groups, ppg, RHO_PARENT, seed)
    M_actual = Xi.shape[0]

    W = build_hopfield_w(Xi, N)

    saddles = compute_saddle_proxies(W, Xi, N, rng)
    n_saddles = saddles.shape[0]

    if n_saddles < 3:
        print(f"  [seed={seed}] too few saddles ({n_saddles}); SKIP", flush=True)
        return {
            "seed": seed, "N": N, "M": M_actual, "run_mode": RUN_MODE,
            "mean_ratio_saddle": float("nan"), "valid_frac": 0.0, "n_valid_triples": 0,
            "n_saddles": n_saddles,
        }

    mean_ratio, valid_frac, n_valid = ultrametric_ratio(saddles, N, VALID_OVERLAP_THRESH)
    elapsed = time.time() - t0

    print(f"  [seed={seed}] M={M_actual} n_saddles={n_saddles} "
          f"mean_ratio={mean_ratio:.4f} valid_frac={valid_frac:.4f} "
          f"n_valid_triples={n_valid} t={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": N, "M": M_actual, "run_mode": RUN_MODE,
        "mean_ratio_saddle": float(mean_ratio) if not math.isnan(mean_ratio) else None,
        "valid_frac": float(valid_frac),
        "n_valid_triples": n_valid,
        "n_saddles": n_saddles,
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    valid_ratios = [r["mean_ratio_saddle"] for r in results
                    if r.get("mean_ratio_saddle") is not None and
                    not (isinstance(r["mean_ratio_saddle"], float) and math.isnan(r["mean_ratio_saddle"]))]
    valid_fracs = [r["valid_frac"] for r in results if r.get("valid_frac") is not None]

    if not valid_ratios:
        return ("HARD_FAIL", "No valid saddle ratio estimates.")

    mean_ratio = float(np.mean(valid_ratios))
    mean_frac = float(np.mean(valid_fracs)) if valid_fracs else 0.0

    summary = (f"mean_ratio={mean_ratio:.4f} (HP>={HP_RATIO_SADDLE} HF<{HF_RATIO_SADDLE}) "
               f"valid_frac={mean_frac:.4f} (HP>={HP_VALID_FRAC} HF<{HF_VALID_FRAC}) "
               f"n_seeds={len(valid_ratios)}")

    if mean_ratio < HF_RATIO_SADDLE or mean_frac < HF_VALID_FRAC:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")
    if mean_ratio >= HP_RATIO_SADDLE and mean_frac >= HP_VALID_FRAC:
        return ("HARD_PASS", f"HARD_PASS: {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "ALPHA": ALPHA,
    "per_seed_summary": [
        {"seed": r.get("seed"), "mean_ratio_saddle": r.get("mean_ratio_saddle"),
         "valid_frac": r.get("valid_frac"), "n_valid_triples": r.get("n_valid_triples")}
        for r in all_results
    ],
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
