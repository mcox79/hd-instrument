"""
q_f4_saddle_um_n_filter_v1 -- Q-F4 saddle UM with N raised and filter threshold fixed.

RESCUE from q_f4_saddle_um_v1 INSTRUMENTATION_SUSPECT (minima_ratio=1.0095 at N=512):
  Root cause: at N=512, noise floor ~ 1/sqrt(N) = 0.044, comparable to mean overlap
  ~0.064 for M=76 patterns. Filter denom > 0.01 passes noise-contaminated triples
  where abc > max(ab,bc) by noise -> ratio > 1.0. Meaningless computation.

FIXES (per upstream push note 2026-06-02):
  R1: Increase filter threshold: denom > 0.01 -> denom > 0.10.
      Focuses on triples with real overlap signal.
  R2: Switch to N=2048 (production N). Noise floor 1/sqrt(2048) = 0.022.
      Mean overlap ~0.064 is 3x above noise floor -> reliable ratio computation.
  Combined R1+R2: at N=2048 with denom > 0.10, triples passing filter should have
  real signal; minima_ratio should converge to < 1.0.

SCIENTIFIC QUESTION (Q-F4):
  SKAH-M class predicts strict hierarchy in SADDLE space but only weak hierarchy
  in MINIMA space. v324 tested MINIMA overlaps (HARD_FAIL). Q-F4 tests SADDLE
  overlaps -- the correct space for SKAH-M.

PRE-REGISTERED BANDS (from q_f4_saddle_um_v1 original pre-reg, now with N=2048):
  HARD-PASS: mean_ratio_saddle >= 0.85 AND saddle_lift > mean_ratio_minima + 0.15.
  MIDDLE: 0.70 <= mean_ratio_saddle < 0.85.
  HARD-FAIL: mean_ratio_saddle < 0.70 OR lift <= 0 (no saddle-hierarchy signal).

FORMULA SELF-TESTS:
  1. At N=2048: noise_floor = 1/sqrt(2048) = 0.022. Filter denom > 0.10 is 4.5x
     above noise floor -> reliable separation of signal from noise.
  2. Triplet ratio abc / max(ab, bc): for valid triples (denom > 0.10), ratio in [0,1].
     Assert all ratios in [0.0, 1.0+eps] after filter fix.
  3. Anti-noise saddle proxy: rho=0.5 flip gives overlap ~ 0 with original pattern.

PROT-018: no _nN suffix; production N=2048 per rule 3 (saddle-hierarchy requires
enough patterns M ~ 300 for saddle diversity; N=2048 gives M=307 at alpha=0.15).
PROT-021: run_config includes N, alpha, run_mode.
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

ANCHOR_NAME = "q_f4_saddle_um_n_filter_v1"

# PROT-018: no _nN suffix; production N=2048 per rule 3 (stated explicitly)
# N=2048 gives M=307 patterns at alpha=0.15; noise floor=0.022 << filter=0.10

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 2048       # SAME N for smoke and full -- small N was the problem
    SEEDS = [7]
    ALPHA = 0.15
    P_SADDLES = 30
    RHO_CORRUPT = 0.5
    ASCENT_STEPS = 20
    UM_FILTER_DENOM = 0.10  # FIXED: was 0.01, now 0.10 (4.5x above noise floor)
else:
    N = 2048       # PROT-018: production N=2048 matching anchor name semantics
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA = 0.15
    P_SADDLES = 100
    RHO_CORRUPT = 0.5
    ASCENT_STEPS = 30
    UM_FILTER_DENOM = 0.10  # FIXED: was 0.01, now 0.10

# Pre-registered thresholds (same as v1 original)
HP_RATIO_SADDLE = 0.85
HF_RATIO_SADDLE = 0.70
HP_SADDLE_LIFT = 0.15   # saddle must exceed minima ratio by >= 0.15


def _selftest_triplet_ratio():
    """Triplet UM ratio: abc=0.3, ab=0.5, bc=0.5 => ratio=0.6."""
    abc, ab, bc = 0.3, 0.5, 0.5
    ratio = abc / max(ab, bc)
    assert abs(ratio - 0.6) < 1e-9, f"triplet ratio={ratio:.6f}, expected 0.6"
    return ratio


def _selftest_filter_bound():
    """Filter denom > 0.10: assert ratio in [0,1] for valid triples."""
    # After filter: denom = max(ab,bc) > 0.10, abc <= (some bound)
    # For +-1 vectors, |overlap| = |dot(a,b)/N| <= 1. So abc/denom <= 1/0.10 = 10 potential.
    # But abc = |dot(s_i, s_k)/N|, also in [0,1], so abc/denom <= 1/0.10 = 10 max.
    # However if abc <= max(ab,bc) (ultrametric), ratio <= 1.
    # If NOT ultrametric (abc > max(ab,bc)), ratio > 1. This is what we're measuring.
    # Key assertion: filter reduces the frequency of ratio > 1.
    # Formula check: if abc=0.15, denom=0.11 -> ratio=0.15/0.11 ~ 1.36 (legal, non-UM).
    # Vs abc=0.08, denom=0.11 -> ratio=0.73 (UM-satisfying).
    # The distribution of ratios tells us about UM structure.
    abc_um, denom_um = 0.08, 0.11
    ratio_um = abc_um / denom_um
    assert ratio_um < 1.0, f"UM-satisfying ratio should be < 1.0: {ratio_um:.4f}"

    # Noise floor assertion: 1/sqrt(N) << UM_FILTER_DENOM
    noise_floor = 1.0 / math.sqrt(N)
    assert noise_floor < UM_FILTER_DENOM / 2.0, (
        f"Noise floor {noise_floor:.4f} >= filter/2 {UM_FILTER_DENOM/2:.4f}; "
        f"filter is not sufficiently above noise"
    )
    return noise_floor


def _selftest_anti_noise_overlap():
    """Anti-noise: rho=0.5 gives overlap ~ 0 with original pattern."""
    N_test = 1000
    rng = np.random.RandomState(0)
    xi = rng.choice([-1.0, 1.0], size=(N_test,))
    flip_mask = rng.rand(N_test) < 0.5
    s_corrupt = xi.copy()
    s_corrupt[flip_mask] *= -1.0
    overlap = float(np.dot(xi, s_corrupt)) / N_test
    assert abs(overlap) < 0.1, f"anti-noise overlap={overlap:.4f}, expected ~0"
    return overlap


_t1 = _selftest_triplet_ratio()
_t2 = _selftest_filter_bound()
_t3 = _selftest_anti_noise_overlap()
print(
    f"[selftest] triplet_ratio={_t1:.4f} noise_floor={_t2:.4f} "
    f"(filter={UM_FILTER_DENOM}) anti_noise_overlap={_t3:.4f}",
    flush=True
)


def build_hopfield_w(M: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W, Xi


def gradient_ascent_saddle(W: np.ndarray, init_state: np.ndarray,
                            n_steps: int) -> np.ndarray:
    """Anti-Hopfield ascent: sign(-W@s) for n_steps."""
    s = init_state.copy()
    for _ in range(n_steps):
        h = W @ s
        s = -np.sign(h)
        s[s == 0] = 1.0
    return s


def sample_saddle_proxies(W: np.ndarray, Xi: np.ndarray,
                           N_dim: int, P_sad: int, rho: float,
                           ascent_steps: int,
                           rng: np.random.RandomState) -> np.ndarray:
    """Generate P_sad saddle proxy states via anti-noise and gradient ascent."""
    M_pats = len(Xi)
    saddle_states = []

    # Method A: anti-noise corruption at rho from stored patterns
    for i in range(M_pats):
        if len(saddle_states) >= P_sad:
            break
        s = Xi[i].copy()
        flip_mask = rng.rand(N_dim) < rho
        s[flip_mask] *= -1.0
        overlaps = np.abs(Xi @ s) / N_dim
        max_ov = float(np.max(overlaps))
        if max_ov < 0.35:
            saddle_states.append(s)

    # Method B: anti-Hopfield gradient ascent
    attempts = 0
    while len(saddle_states) < P_sad and attempts < P_sad * 10:
        s_init = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
        s_asc = gradient_ascent_saddle(W, s_init, ascent_steps)
        overlaps = np.abs(Xi @ s_asc) / N_dim
        max_ov = float(np.max(overlaps))
        if max_ov < 0.35:
            saddle_states.append(s_asc)
        attempts += 1

    if len(saddle_states) < 3:
        return np.zeros((0, N_dim))
    return np.array(saddle_states[:P_sad])


def compute_minima_states(W: np.ndarray, Xi: np.ndarray,
                           N_dim: int, n_relax: int,
                           rng: np.random.RandomState) -> np.ndarray:
    """Relax from each stored pattern to attractor (minima)."""
    minima = []
    for i in range(len(Xi)):
        s = Xi[i].copy()
        for _ in range(n_relax):
            h = W @ s
            s_new = np.sign(h)
            s_new[s_new == 0] = 1.0
            if np.array_equal(s_new, s):
                break
            s = s_new
        minima.append(s)
    return np.array(minima)


def compute_overlap_um_ratio(states: np.ndarray, N_dim: int,
                              rng: np.random.RandomState,
                              max_triples: int = 2000,
                              filter_denom: float = 0.10) -> Dict:
    """
    Compute pairwise overlap matrix and mean ultrametric ratio.
    FIXED: filter_denom=0.10 (was 0.01 in v1) to exclude noise-contaminated triples.
    """
    P = len(states)
    if P < 3:
        return {"mean_ratio": float('nan'), "n_triples": 0,
                "mean_overlap": float('nan'), "n_valid_triples": 0,
                "filter_denom": filter_denom}

    Q = (states @ states.T) / N_dim
    indices = np.arange(P)
    n_triples = min(max_triples, P * (P - 1) * (P - 2) // 6)
    ratios = []
    n_filtered_out = 0

    for _ in range(n_triples):
        i, j, k = rng.choice(indices, size=3, replace=False)
        ab = float(abs(Q[i, j]))
        bc = float(abs(Q[j, k]))
        abc = float(abs(Q[i, k]))
        denom = max(ab, bc)
        if denom <= filter_denom:  # FIXED: was > 0.01, now > 0.10
            n_filtered_out += 1
            continue
        ratios.append(abc / denom)

    n_valid = len(ratios)
    if not ratios:
        return {"mean_ratio": float('nan'), "n_triples": 0,
                "n_valid_triples": 0, "n_filtered_out": n_filtered_out,
                "mean_overlap": float(np.mean(np.abs(Q[np.triu_indices(P, k=1)]))),
                "filter_denom": filter_denom}

    return {
        "mean_ratio": float(np.mean(ratios)),
        "std_ratio": float(np.std(ratios)),
        "n_triples": n_valid,
        "n_filtered_out": n_filtered_out,
        "mean_overlap": float(np.mean(np.abs(Q[np.triu_indices(P, k=1)]))),
        "n_states": P,
        "filter_denom": filter_denom,
        "max_ratio": float(np.max(ratios)),  # diagnostic: should be <= 1+eps for clean data
    }


def _instrumentation_selftest():
    """Assert fixed filter gives mean_ratio <= 1.0 and n_valid_triples > 0."""
    N_test = 2048
    M_test = max(1, int(ALPHA * N_test))  # = 307
    rng = np.random.RandomState(42)

    W, Xi = build_hopfield_w(M_test, N_test, 42)
    saddles = sample_saddle_proxies(
        W, Xi, N_test, 20, RHO_CORRUPT, ASCENT_STEPS, rng
    )
    assert len(saddles) >= 3, (
        f"Only {len(saddles)} saddle proxies at N={N_test}; need >= 3"
    )

    rng2 = np.random.RandomState(99)
    result = compute_overlap_um_ratio(
        saddles, N_test, rng2, max_triples=500, filter_denom=UM_FILTER_DENOM
    )

    # Key assertion: with fixed filter, max_ratio should be <= 1.0+eps
    if result["n_triples"] > 0:
        assert result["max_ratio"] <= 1.05, (
            f"max_ratio={result['max_ratio']:.4f} > 1.05 even with filter={UM_FILTER_DENOM}; "
            f"noise contamination still present -- increase filter further"
        )
        assert not math.isnan(result["mean_ratio"]), "mean_ratio NaN after filter fix"

    # Verify minima also work
    minima = compute_minima_states(W, Xi, N_test, 20, rng)
    rng3 = np.random.RandomState(77)
    m_result = compute_overlap_um_ratio(
        minima, N_test, rng3, max_triples=500, filter_denom=UM_FILTER_DENOM
    )
    if m_result["n_triples"] > 0:
        assert m_result["max_ratio"] <= 1.05, (
            f"minima max_ratio={m_result['max_ratio']:.4f} > 1.05 after filter fix"
        )

    print(
        f"[selftest] PASS: N={N_test} M={M_test} n_saddles={len(saddles)} "
        f"saddle_ratio={result.get('mean_ratio', float('nan')):.4f} "
        f"n_valid={result['n_triples']} n_filtered={result['n_filtered_out']} "
        f"max_ratio={result.get('max_ratio', float('nan')):.4f} "
        f"minima_ratio={m_result.get('mean_ratio', float('nan')):.4f}",
        flush=True
    )


_instrumentation_selftest()


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    M = max(1, int(ALPHA * N))
    print(f"[seed={seed}] N={N} M={M} P_SADDLES={P_SADDLES} filter_denom={UM_FILTER_DENOM}", flush=True)

    W, Xi = build_hopfield_w(M, N, seed)

    saddles = sample_saddle_proxies(
        W, Xi, N, P_SADDLES, RHO_CORRUPT, ASCENT_STEPS,
        np.random.RandomState(seed + 1000)
    )
    print(f"[seed={seed}] found {len(saddles)} saddle proxies", flush=True)

    saddle_um = compute_overlap_um_ratio(
        saddles, N, np.random.RandomState(seed + 2000),
        filter_denom=UM_FILTER_DENOM
    )

    minima = compute_minima_states(W, Xi, N, 50, np.random.RandomState(seed + 3000))
    minima_um = compute_overlap_um_ratio(
        minima, N, np.random.RandomState(seed + 4000),
        filter_denom=UM_FILTER_DENOM
    )

    saddle_ratio = saddle_um.get("mean_ratio", float("nan"))
    minima_ratio = minima_um.get("mean_ratio", float("nan"))
    print(
        f"[seed={seed}] saddle_ratio={saddle_ratio:.4f} "
        f"minima_ratio={minima_ratio:.4f} "
        f"saddle_n_valid={saddle_um.get('n_triples',0)} "
        f"saddle_max_ratio={saddle_um.get('max_ratio', float('nan')):.4f}",
        flush=True
    )

    return {
        "seed": seed, "N": N, "M": M, "alpha": ALPHA,
        "n_saddle_proxies": len(saddles),
        "saddle_um": saddle_um, "minima_um": minima_um,
        "run_mode": RUN_MODE,
    }


def aggregate_results(per_seed: Dict) -> Dict:
    saddle_ratios = [
        v["saddle_um"]["mean_ratio"]
        for v in per_seed.values()
        if not math.isnan(v["saddle_um"].get("mean_ratio", float('nan')))
        and v["saddle_um"].get("n_triples", 0) > 0
    ]
    minima_ratios = [
        v["minima_um"]["mean_ratio"]
        for v in per_seed.values()
        if not math.isnan(v["minima_um"].get("mean_ratio", float('nan')))
        and v["minima_um"].get("n_triples", 0) > 0
    ]

    mean_saddle = float(np.mean(saddle_ratios)) if saddle_ratios else float("nan")
    mean_minima = float(np.mean(minima_ratios)) if minima_ratios else float("nan")
    lift = mean_saddle - mean_minima if (
        not math.isnan(mean_saddle) and not math.isnan(mean_minima)
    ) else float("nan")

    return {
        "mean_ratio_saddle": mean_saddle,
        "std_ratio_saddle": float(np.std(saddle_ratios)) if saddle_ratios else float("nan"),
        "mean_ratio_minima": mean_minima,
        "saddle_lift_over_minima": lift,
        "n_seeds": len(saddle_ratios),
        "filter_denom": UM_FILTER_DENOM,
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    r_sad = agg["mean_ratio_saddle"]
    r_min = agg["mean_ratio_minima"]
    lift = agg["saddle_lift_over_minima"]
    filt = agg["filter_denom"]

    if math.isnan(r_sad) or agg["n_seeds"] == 0:
        return (
            "HARD_FAIL",
            f"mean_ratio_saddle NaN or no valid seeds (filter_denom={filt}). "
            f"Saddle proxies not found or all triples filtered."
        )

    if r_sad < HF_RATIO_SADDLE or (not math.isnan(lift) and lift <= 0):
        return (
            "HARD_FAIL",
            f"SADDLE HIERARCHY ABSENT. mean_ratio_saddle={r_sad:.4f}<{HF_RATIO_SADDLE}. "
            f"mean_ratio_minima={r_min:.4f}. lift={lift:.4f}<=0. "
            f"SKAH-M saddle-hierarchy component NOT confirmed. N={N} filter={filt}."
        )

    if r_sad >= HP_RATIO_SADDLE and not math.isnan(lift) and lift >= HP_SADDLE_LIFT:
        return (
            "HARD_PASS",
            f"SKAH-M SADDLE HIERARCHY CONFIRMED. mean_ratio_saddle={r_sad:.4f}>={HP_RATIO_SADDLE}. "
            f"mean_ratio_minima={r_min:.4f}. saddle_lift={lift:.4f}>={HP_SADDLE_LIFT}. "
            f"N={N} filter={filt}. n_seeds={agg['n_seeds']}. "
            f"Saddle-space strictly more ultrametric than minima-space -- SKAH-M confirmed."
        )

    return (
        "MIDDLE_BAND",
        f"Partial saddle hierarchy. saddle={r_sad:.4f} in [{HF_RATIO_SADDLE},{HP_RATIO_SADDLE}). "
        f"minima={r_min:.4f}. lift={lift:.4f}. N={N} filter={filt} n_seeds={agg['n_seeds']}."
    )


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(
        f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
        f"P_SADDLES={P_SADDLES} filter_denom={UM_FILTER_DENOM} seeds={SEEDS}",
        flush=True
    )

    # PROT-021: include N and alpha in run_config
    run_config = {"N": N, "alpha": ALPHA, "run_mode": RUN_MODE}
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
        "alpha": ALPHA, "P_SADDLES": P_SADDLES,
        "filter_denom": UM_FILTER_DENOM,
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
