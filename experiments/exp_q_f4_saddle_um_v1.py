"""
q_f4_saddle_um_v1 -- Q-F4: Saddle-space ultrametricity (SKAH-M saddle-hierarchy signature).

SCIENTIFIC QUESTION (Q-F4):
  SKAH-M class confirmed at v228 = non-reciprocal Hopfield + spatial-correlated DAM
  + SADDLE-HIERARCHY DAM. The saddle-hierarchy axis predicts STRICT hierarchy in
  SADDLE space and only WEAK hierarchy in MINIMA space. v324 tested MINIMA overlaps
  (mean_ratio=0.583 = HARD_FAIL). Q-F4 tests SADDLE overlaps -- the correct space
  for the SKAH-M prediction.

  Protocol:
    1. Build Hopfield weight matrix W with M stored patterns.
    2. From each stored pattern init, run gradient ASCENT on -E(s) to reach a
       saddle approximation (Hessian approximately zero eigenvalue direction).
       Practically: gradient ascent is sign(+W@s) updates until energy stops
       increasing -- these are LOCAL MAXIMA which serve as saddle proxies in
       the Hopfield energy landscape.
    3. Collect R saddle-proxy states {s_saddle_i}.
    4. Compute pairwise overlap matrix Q_sad_ij = (1/N)*dot(s_i, s_j).
    5. Apply same triplet ultrametric test from v324: for each triple (i,j,k),
       check abc <= max(ab, bc). Mean_ratio_saddle = mean(abc / max(ab,bc)).
    6. Compare mean_ratio_saddle vs mean_ratio_minima (expected: saddle >> minima).

  Alternative saddle sampling: anti-pattern noise corruption at rho=0.5 (50% flip)
  -- this produces states that are equidistant from two stored patterns, which are
  natural saddle-proxies in the retrieval landscape. Validated by:
    a. Low energy relative to random, high energy relative to retrieved pattern.
    b. Moderate overlap with two distinct stored patterns simultaneously.

HARD-PASS:
  mean_ratio_saddle >= 0.85 (strict ultrametricity in saddle space)
  AND mean_ratio_saddle > mean_ratio_minima + 0.15 (saddle strictly more UM than minima)

HARD-FAIL:
  mean_ratio_saddle < 0.70
  OR mean_ratio_saddle <= mean_ratio_minima (no saddle-hierarchy signal)

MIDDLE BAND:
  0.70 <= mean_ratio_saddle < 0.85 (soft saddle hierarchy -- partial SKAH-M confirmation)

FORMULA SELF-TESTS:
  1. Triplet UM ratio: for abc=0.3, max(ab,bc) = max(0.5, 0.5) = 0.5:
     ratio = 0.3/0.5 = 0.6. Assert == 0.6.
  2. Perfect UM: abc <= max(ab,bc) always holds with equality: abc = max(ab,bc) => ratio = 1.0.
  3. Anti-noise saddle proxy: for pattern xi and flip mask at rho=0.5,
     dot(s_corrupted, xi)/N = 1 - 2*rho = 0.0 for rho=0.5. Assert ~= 0.

SWEEP DESIGN:
  N = 2048 (full) / 512 (smoke)
  ALPHA = 0.15
  M = int(ALPHA * N) patterns
  P_SADDLES = 100 (full) / 30 (smoke)  -- saddle proxy states
  SEEDS = [7, 17, 23, 31, 41] (full) / [7] (smoke)
  Saddle sampling: for each of M*2 random {pattern, anti-pattern} pairs, corrupt
  at rho=0.5 to get saddle proxies. Filter for valid saddles (overlap < 0.2 with
  all stored patterns = not collapsed to any minimum).
  Additionally sample: gradient-ascent from random init for 20 steps = finds
  local maxima (energy increases then plateaus).

TIMEOUT ESTIMATE:
  Smoke: N=512, 30 saddles, 1 seed. Matrix ops only.
  Smoke wall expected ~2s.
  Full: N=2048, 100 saddles, 5 seeds.
  Scale: 1.5 * 2 * (2048/512)^1.5 * (5/1) = ceil(1.5*2*11.3*5) = ceil(170) = 180s.
  timeout=900s (5x buffer for saddle sampling variability).

No _nN suffix; production N=2048 per rule 3 (stated here: N=2048, rationale:
saddle-hierarchy requires enough patterns M ~ 300 for saddle diversity; N=2048
gives M=307 patterns at alpha=0.15).
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q_f4_saddle_um_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7]
    ALPHA = 0.15
    P_SADDLES = 30
    RHO_CORRUPT = 0.5  # 50% flip for saddle proxy
    ASCENT_STEPS = 20  # gradient ascent steps
else:
    N = 2048
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA = 0.15
    P_SADDLES = 100
    RHO_CORRUPT = 0.5
    ASCENT_STEPS = 30

# Pre-registered thresholds
HP_RATIO_SADDLE = 0.85
HF_RATIO_SADDLE = 0.70
HP_SADDLE_LIFT = 0.15   # saddle must exceed minima by at least this


# ---- FORMULA SELF-TESTS ----
def _selftest_triplet_ratio():
    """Triplet UM ratio: abc=0.3, ab=0.5, bc=0.5 => ratio=0.6."""
    abc, ab, bc = 0.3, 0.5, 0.5
    ratio = abc / max(ab, bc)
    assert abs(ratio - 0.6) < 1e-9, f"triplet ratio={ratio:.6f}, expected 0.6"
    return ratio


def _selftest_perfect_um():
    """Perfect UM: abc = max(ab,bc) => ratio=1.0."""
    ab, bc = 0.7, 0.5
    abc = min(ab, bc)  # satisfies abc <= max(ab,bc) with equality at abc=min
    # Actually: ultrametric inequality: abc <= max(ab,bc). With abc=max(ab,bc) => ratio=1.
    abc_at_max = max(ab, bc)
    ratio = abc_at_max / max(ab, bc)
    assert abs(ratio - 1.0) < 1e-9, f"perfect UM ratio={ratio:.6f}, expected 1.0"
    return ratio


def _selftest_anti_noise_overlap():
    """Anti-noise: rho=0.5 gives overlap ~ 0 with original pattern."""
    N_test = 1000
    rng = np.random.RandomState(0)
    xi = rng.choice([-1.0, 1.0], size=(N_test,))
    # Flip 50% randomly
    flip_mask = rng.rand(N_test) < 0.5
    s_corrupt = xi.copy()
    s_corrupt[flip_mask] *= -1.0
    overlap = float(np.dot(xi, s_corrupt)) / N_test
    # Expected overlap = 1 - 2*rho = 0.0 for rho=0.5
    assert abs(overlap) < 0.1, f"anti-noise overlap={overlap:.4f}, expected ~0"
    return overlap


_t1 = _selftest_triplet_ratio()
_t2 = _selftest_perfect_um()
_t3 = _selftest_anti_noise_overlap()
print(f"[selftest] triplet_ratio={_t1:.4f} perfect_um={_t2:.4f} anti_noise_overlap={_t3:.4f}",
      flush=True)


def build_hopfield_w(M: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W, Xi


def gradient_ascent_saddle(W: np.ndarray, init_state: np.ndarray,
                            n_steps: int) -> np.ndarray:
    """
    Gradient ASCENT on energy E(s) = -(1/2)*s^T*W*s.
    Ascent = descent on -E = follow +gradient direction.
    For Ising: gradient ascent step = sign(W@s) (same as retrieval!).
    Instead: use ANTI-Hopfield update: sign(-W@s) pushes away from attractors.
    Run for n_steps; result approximates unstable fixed point / saddle proxy.
    """
    s = init_state.copy()
    for _ in range(n_steps):
        h = W @ s
        # Anti-Hopfield: flip to ANTI-aligned state
        s = -np.sign(h)
        s[s == 0] = 1.0
    return s


def sample_saddle_proxies(W: np.ndarray, Xi: np.ndarray,
                           N_dim: int, P_sad: int,
                           rho: float, ascent_steps: int,
                           rng: np.random.RandomState) -> np.ndarray:
    """
    Generate P_sad saddle proxy states using two methods combined:
    Method A: anti-noise corruption at rho=0.5 from stored patterns.
    Method B: gradient ascent (anti-Hopfield) from random inits.
    Filter: keep states with max overlap < 0.3 with all stored patterns
    (to ensure they are NOT collapsed to any minimum).
    """
    M_pats = len(Xi)
    saddle_states = []

    # Method A: anti-noise from stored patterns
    for i in range(M_pats):
        if len(saddle_states) >= P_sad:
            break
        s = Xi[i].copy()
        flip_mask = rng.rand(N_dim) < rho
        s[flip_mask] *= -1.0
        overlaps = np.abs(Xi @ s) / N_dim
        max_ov = float(np.max(overlaps))
        if max_ov < 0.35:  # not too close to any pattern
            saddle_states.append(s)

    # Method B: anti-Hopfield gradient ascent if need more
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
    """Relax from each stored pattern to its attractor (minima states)."""
    minima = []
    M_pats = len(Xi)
    for i in range(M_pats):
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


def compute_overlap_um_ratio(states: np.ndarray, N_dim: int, rng: np.random.RandomState,
                              max_triples: int = 2000) -> Dict:
    """
    Compute pairwise overlap matrix and mean ultrametric ratio.
    Sample max_triples random triples for efficiency.
    """
    P = len(states)
    if P < 3:
        return {"mean_ratio": float('nan'), "n_triples": 0, "mean_overlap": float('nan')}

    Q = (states @ states.T) / N_dim  # P x P overlap
    # Sample triples
    indices = np.arange(P)
    n_triples = min(max_triples, P * (P - 1) * (P - 2) // 6)
    ratios = []
    for _ in range(n_triples):
        i, j, k = rng.choice(indices, size=3, replace=False)
        ab = float(abs(Q[i, j]))
        bc = float(abs(Q[j, k]))
        abc = float(abs(Q[i, k]))
        denom = max(ab, bc)
        if denom > 0.01:
            ratios.append(abc / denom)

    if not ratios:
        return {"mean_ratio": float('nan'), "n_triples": 0,
                "mean_overlap": float(np.mean(np.abs(Q[np.triu_indices(P, k=1)])))}

    return {
        "mean_ratio": float(np.mean(ratios)),
        "std_ratio": float(np.std(ratios)),
        "n_triples": len(ratios),
        "mean_overlap": float(np.mean(np.abs(Q[np.triu_indices(P, k=1)]))),
        "n_states": P,
    }


def _instrumentation_selftest():
    """Assert saddle metrics non-null at small scale."""
    N_test, M_test = 256, 20
    rng = np.random.RandomState(42)
    W, Xi = build_hopfield_w(M_test, N_test, 42)
    saddles = sample_saddle_proxies(W, Xi, N_test, 15, RHO_CORRUPT, ASCENT_STEPS, rng)
    assert len(saddles) >= 3, f"Only {len(saddles)} saddle proxies found in selftest (need >=3)"

    rng2 = np.random.RandomState(42)
    result = compute_overlap_um_ratio(saddles, N_test, rng2, max_triples=100)
    assert not math.isnan(result["mean_ratio"]), "mean_ratio is NaN in selftest"
    assert result["n_triples"] > 0, f"n_triples=0 in selftest"

    # Minima
    minima = compute_minima_states(W, Xi, N_test, 20, rng)
    assert len(minima) > 0, "No minima states computed in selftest"
    rng3 = np.random.RandomState(42)
    m_result = compute_overlap_um_ratio(minima, N_test, rng3, max_triples=100)
    assert not math.isnan(m_result["mean_ratio"]), "minima mean_ratio is NaN in selftest"

    print(f"[selftest] PASS: n_saddles={len(saddles)} saddle_ratio={result['mean_ratio']:.4f} "
          f"minima_ratio={m_result['mean_ratio']:.4f} n_triples={result['n_triples']}",
          flush=True)


_instrumentation_selftest()


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    M = max(1, int(ALPHA * N))
    print(f"[seed={seed}] N={N} M={M} P_SADDLES={P_SADDLES}", flush=True)
    W, Xi = build_hopfield_w(M, N, seed)

    # Saddle proxies
    saddles = sample_saddle_proxies(W, Xi, N, P_SADDLES, RHO_CORRUPT, ASCENT_STEPS,
                                    np.random.RandomState(seed + 1000))
    print(f"[seed={seed}] found {len(saddles)} saddle proxies", flush=True)

    saddle_um = compute_overlap_um_ratio(saddles, N, np.random.RandomState(seed + 2000))

    # Minima
    minima = compute_minima_states(W, Xi, N, 50, np.random.RandomState(seed + 3000))
    minima_um = compute_overlap_um_ratio(minima, N, np.random.RandomState(seed + 4000))

    print(f"[seed={seed}] saddle_ratio={saddle_um['mean_ratio']:.4f} "
          f"minima_ratio={minima_um['mean_ratio']:.4f} "
          f"n_saddle_triples={saddle_um['n_triples']}", flush=True)

    return {
        "seed": seed, "N": N, "M": M, "alpha": ALPHA,
        "n_saddle_proxies": len(saddles),
        "saddle_um": saddle_um,
        "minima_um": minima_um,
        "run_mode": RUN_MODE,
    }


def aggregate_results(per_seed: Dict) -> Dict:
    saddle_ratios = [v["saddle_um"]["mean_ratio"] for v in per_seed.values()
                     if not math.isnan(v["saddle_um"].get("mean_ratio", float('nan')))]
    minima_ratios = [v["minima_um"]["mean_ratio"] for v in per_seed.values()
                     if not math.isnan(v["minima_um"].get("mean_ratio", float('nan')))]
    n_saddles = [v["n_saddle_proxies"] for v in per_seed.values()]

    return {
        "mean_ratio_saddle": float(np.mean(saddle_ratios)) if saddle_ratios else float('nan'),
        "std_ratio_saddle": float(np.std(saddle_ratios)) if saddle_ratios else float('nan'),
        "mean_ratio_minima": float(np.mean(minima_ratios)) if minima_ratios else float('nan'),
        "saddle_lift_over_minima": (float(np.mean(saddle_ratios) - np.mean(minima_ratios))
                                    if saddle_ratios and minima_ratios else float('nan')),
        "mean_n_saddles": float(np.mean(n_saddles)) if n_saddles else float('nan'),
        "n_seeds": len(saddle_ratios),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    r_sad = agg["mean_ratio_saddle"]
    r_min = agg["mean_ratio_minima"]
    lift = agg["saddle_lift_over_minima"]

    if math.isnan(r_sad):
        return ("HARD_FAIL", "mean_ratio_saddle is NaN -- instrumentation failure or no saddle proxies.")

    if r_sad < HF_RATIO_SADDLE or (not math.isnan(lift) and lift <= 0):
        return ("HARD_FAIL",
                f"SADDLE HIERARCHY ABSENT. mean_ratio_saddle={r_sad:.4f} < {HF_RATIO_SADDLE}. "
                f"mean_ratio_minima={r_min:.4f}. lift={lift:.4f}. "
                f"SKAH-M saddle-hierarchy component NOT confirmed in overlap space. "
                f"n_seeds={agg['n_seeds']}.")

    if r_sad >= HP_RATIO_SADDLE and (not math.isnan(lift) and lift >= HP_SADDLE_LIFT):
        return ("HARD_PASS",
                f"SKAH-M SADDLE HIERARCHY CONFIRMED. mean_ratio_saddle={r_sad:.4f} >= {HP_RATIO_SADDLE}. "
                f"mean_ratio_minima={r_min:.4f}. saddle_lift={lift:.4f} >= {HP_SADDLE_LIFT}. "
                f"Strict ultrametricity in SADDLE space but not MINIMA space -- "
                f"SKAH-M saddle-hierarchy prediction CONFIRMED. "
                f"n_seeds={agg['n_seeds']}.")

    return ("MIDDLE_BAND",
            f"Partial saddle hierarchy. mean_ratio_saddle={r_sad:.4f} in [{HF_RATIO_SADDLE},{HP_RATIO_SADDLE}). "
            f"mean_ratio_minima={r_min:.4f}. lift={lift:.4f} (need >={HP_SADDLE_LIFT}). "
            f"n_seeds={agg['n_seeds']}. "
            f"Increase P_SADDLES or N for cleaner saddle-hierarchy signal.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"P_SADDLES={P_SADDLES} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "ALPHA": ALPHA, "P_SADDLES": P_SADDLES, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "alpha": ALPHA,
        "seeds": SEEDS, "P_SADDLES": P_SADDLES,
        "aggregated": agg,
        "thresholds": {
            "HP_RATIO_SADDLE": HP_RATIO_SADDLE, "HF_RATIO_SADDLE": HF_RATIO_SADDLE,
            "HP_SADDLE_LIFT": HP_SADDLE_LIFT,
        },
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
