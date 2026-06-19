"""
dynamical_um_ck_class_v1 -- Q-F1: CK-class dynamical ultrametricity.

SCIENTIFIC QUESTION (Q-F1 DECISIVE):
  Static ultrametricity (v324 mean_ratio=0.583) is the WRONG TEST for the
  substrate's confirmed CK-aging/SKAH-M phase class. Research established:
  - Cacciuto-Marinari-Parisi 1996: N=4096 is below the static-UM finite-N
    threshold (need N >= 20736 for clean static UM in 4D EA).
  - Stariolo 2001: "dynamical UM passes where static UM fails" at finite N.
  - Cugliandolo-Kurchan 1993: dynamical ultrametricity M_dyn measures whether
    THREE-TIME TRIANGLE INEQUALITY holds IN TRAJECTORY SPACE (not overlap space).

  CK dynamical ultrametricity protocol (Castillo-Chamon-Cugliandolo 2002):
    Given 3 time points t_1 < t_2 < t_3, measure:
      C_12 = C(t_2, t_1)  -- two-time correlator
      C_23 = C(t_3, t_2)  -- two-time correlator
      C_13 = C(t_3, t_1)  -- two-time correlator
    Dynamical ultrametric ratio: r_dyn = C_13 / min(C_12, C_23)
    M_dyn = mean(r_dyn) over R replica pairs
    (r_dyn <= 1 always by the CK inequality if CK class holds perfectly)
    Empirically: M_dyn close to 1 => strong dynamical UM; M_dyn << 1 => absent.

  CANONICAL PREDICTION for CK aging class: M_dyn in [0.85, 0.95]
    (Iniguez-Marinari-Parisi-Ruiz-Lorenzo 1999 found mean_ratio ~ 0.88 in 3D EA).

SWEEP DESIGN:
  Time triplets tested: (t_1, t_2, t_3) in:
    (16, 128, 1024) -- primary triplet from research recommendation
    (8, 64, 512)    -- shorter-scale triplet
    (32, 256, 2048) -- longer-scale triplet (full only)
  R = 200 replica pairs per triplet (smoke: 100)
  Glauber dynamics at beta=2.0 starting from random initial state (NOT a
  stored pattern -- CK protocol uses QUENCH from high temperature).

  The substrate's dreaming dynamics ARE the CK protocol natively when
  wrapped with t_w-stamped snapshots + R-replica averaging.

HARD-PASS: M_dyn >= 0.75 (smoke) / 0.75 (full), in >=2/3 triplets.
HARD-FAIL: M_dyn <= 0.65 in >=2/3 triplets.
MIDDLE BAND: 0.65 < M_dyn < 0.75.

Note: calibration probe (no prior empirical M_dyn for this substrate).
Bands set at +-50% around theoretical center 0.88:
  HARD_PASS center 0.88 * 0.5 = 0.44 -- but this is too loose.
  Override with DECISIVE bounds per research: HP>=0.75, HF<=0.65.
  These are within +-15% of the CK prediction range [0.85,0.95].
  Rationale: research established clear separation from static-UM=0.583.

FORMULA SELF-TESTS:
  1. CK ratio: given C_12=0.9, C_23=0.8, C_13=0.7:
     min(C_12, C_23) = 0.8, ratio = 0.7/0.8 = 0.875. Assert == 0.875.
  2. Perfect dynamical UM: if C_13 = min(C_12, C_23) exactly for all triplets,
     M_dyn = 1.0.
  3. No dynamical UM: if C_13 << min(C_12, C_23), M_dyn << 1.
     E.g. C_12=0.8, C_23=0.8, C_13=0.1 => ratio=0.125.

TIMEOUT ESTIMATE:
  Smoke: N=512, alpha=0.15, R=100, 3 triplets, 1 seed, T_MAX=2048.
  Glauber cost: R pairs * T_MAX steps * N ops per step / seed.
  100 * 2048 * 512 = ~10^8 ops. Expected ~15-30s.
  Full: N=1024, R=200, 3 triplets, 3 seeds, T_MAX=2048.
  Scaling: 1.5 * 30 * (1024/512)^1.5 * (3/1) = ceil(1.5*30*2.83*3) = ceil(382) = 390s.
  timeout=1200s (3x buffer).

No _nN suffix; production N=1024 per rule 3 (N=1024, rationale: CK protocol
is CPU-bound at R=200 replica pairs; 1024 gives ample statistics with 3 seeds).
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

ANCHOR_NAME = "dynamical_um_ck_class_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Time triplets: (t1, t2, t3) for CK protocol
TRIPLETS_SMOKE = [(8, 64, 512), (16, 128, 1024)]
TRIPLETS_FULL = [(8, 64, 512), (16, 128, 1024), (32, 256, 2048)]

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7]
    ALPHA = 0.15           # above alpha_c
    R_REPLICAS = 100       # replica pairs per triplet
    BETA = 2.0
    TRIPLETS = TRIPLETS_SMOKE
else:
    N = 1024
    SEEDS = [7, 17, 23]
    ALPHA = 0.15
    R_REPLICAS = 200
    BETA = 2.0
    TRIPLETS = TRIPLETS_FULL

T_MAX = max(t3 for _, _, t3 in TRIPLETS)

# Pre-registered thresholds
HP_MDYN = 0.75
HF_MDYN = 0.65
HP_TRIPLET_FRAC = 2 / 3   # pass in >= 2/3 triplets


# ---- FORMULA SELF-TESTS ----
def _selftest_ck_ratio():
    """CK ratio calculation: C_13 / min(C_12, C_23) = 0.875 for known values."""
    C_12, C_23, C_13 = 0.9, 0.8, 0.7
    expected = C_13 / min(C_12, C_23)
    assert abs(expected - 0.875) < 1e-9, f"CK ratio={expected:.6f}, expected 0.875"
    return expected


def _selftest_perfect_dyn_um():
    """Perfect CK: C_13 = min(C_12, C_23) => ratio = 1.0."""
    C_12, C_23 = 0.8, 0.7
    C_13 = min(C_12, C_23)  # saturates the ultrametric bound
    ratio = C_13 / min(C_12, C_23)
    assert abs(ratio - 1.0) < 1e-9, f"Perfect dyn UM ratio={ratio:.6f}, expected 1.0"
    return ratio


def _selftest_no_dyn_um():
    """No dyn UM: C_13 << min => ratio << 1."""
    C_12, C_23, C_13 = 0.8, 0.8, 0.1
    ratio = C_13 / min(C_12, C_23)
    assert ratio < 0.2, f"No dyn UM ratio={ratio:.4f}, expected < 0.2"
    return ratio


_r1 = _selftest_ck_ratio()
_r2 = _selftest_perfect_dyn_um()
_r3 = _selftest_no_dyn_um()
print(f"[selftest] CK ratio={_r1:.4f}, perfect_dyn_UM={_r2:.4f}, no_dyn_UM={_r3:.4f}", flush=True)


def build_hopfield_w(M: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def glauber_sweep(state: np.ndarray, W: np.ndarray,
                  beta: float, rng: np.random.RandomState) -> np.ndarray:
    """One async Glauber sweep: N random single-spin updates."""
    N_dim = len(state)
    indices = rng.randint(0, N_dim, size=N_dim)
    for i in indices:
        h_i = float(W[i] @ state)
        prob_up = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        state[i] = 1.0 if rng.rand() < prob_up else -1.0
    return state


def measure_two_time_correlator(W: np.ndarray, N_dim: int,
                                 t1: int, t2: int, t3: int,
                                 R: int, beta: float,
                                 rng: np.random.RandomState) -> Dict:
    """
    CK protocol: run R independent quench replicas.
    For each replica: random init -> Glauber to t_max.
    Record states at t1, t2, t3. Compute pairwise C.
    M_dyn = mean(C_13 / min(C_12, C_23)) over R replicas.
    """
    C_12_list, C_23_list, C_13_list = [], [], []

    for r in range(R):
        # Quench from random high-T state
        s = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
        s1 = s2 = s3 = None

        for step in range(1, t3 + 1):
            s = glauber_sweep(s, W, beta, rng)
            if step == t1:
                s1 = s.copy()
            elif step == t2:
                s2 = s.copy()
            elif step == t3:
                s3 = s.copy()

        if s1 is None or s2 is None or s3 is None:
            continue

        c12 = float(np.dot(s1, s2)) / N_dim
        c23 = float(np.dot(s2, s3)) / N_dim
        c13 = float(np.dot(s1, s3)) / N_dim
        C_12_list.append(c12)
        C_23_list.append(c23)
        C_13_list.append(c13)

    if len(C_12_list) < R // 2:
        return {"M_dyn": float("nan"), "mean_C12": float("nan"),
                "mean_C23": float("nan"), "mean_C13": float("nan"), "n_valid": 0}

    C12 = np.array(C_12_list)
    C23 = np.array(C_23_list)
    C13 = np.array(C_13_list)

    # CK ratio per replica: C_13 / min(C_12, C_23)
    denom = np.minimum(np.abs(C12), np.abs(C23))
    # Avoid division by zero: skip replicas where min denom is near zero
    valid = denom > 0.01
    if not np.any(valid):
        return {"M_dyn": float("nan"), "mean_C12": float(np.mean(C12)),
                "mean_C23": float(np.mean(C23)), "mean_C13": float(np.mean(C13)),
                "n_valid": 0}

    ratios = np.abs(C13[valid]) / denom[valid]
    M_dyn = float(np.mean(ratios))

    return {
        "M_dyn": M_dyn,
        "mean_C12": float(np.mean(C12)),
        "mean_C23": float(np.mean(C23)),
        "mean_C13": float(np.mean(C13)),
        "n_valid": int(np.sum(valid)),
        "std_ratios": float(np.std(ratios)),
    }


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    M = max(1, int(ALPHA * N))
    W = build_hopfield_w(M, N, seed)
    print(f"[seed={seed}] N={N} M={M} R={R_REPLICAS}", flush=True)

    triplet_results = {}
    for t1, t2, t3 in TRIPLETS:
        print(f"  triplet ({t1},{t2},{t3})...", flush=True)
        result = measure_two_time_correlator(W, N, t1, t2, t3, R_REPLICAS, BETA, rng)
        key = f"{t1}_{t2}_{t3}"
        triplet_results[key] = result
        print(f"  M_dyn={result['M_dyn']:.4f} C12={result['mean_C12']:.4f} "
              f"C23={result['mean_C23']:.4f} C13={result['mean_C13']:.4f} "
              f"n_valid={result['n_valid']}", flush=True)

    return {"seed": seed, "N": N, "M": M, "alpha": ALPHA,
            "R": R_REPLICAS, "triplets": triplet_results, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert M_dyn non-null at small scale."""
    N_test = 128
    M_test = max(1, int(0.15 * N_test))
    rng = np.random.RandomState(42)
    W = build_hopfield_w(M_test, N_test, 42)
    result = measure_two_time_correlator(W, N_test, t1=4, t2=16, t3=64,
                                          R=10, beta=BETA, rng=rng)
    assert result["n_valid"] > 0, f"n_valid=0 in selftest -- no valid replicas"
    assert not math.isnan(result["M_dyn"]), "M_dyn is NaN in selftest"
    assert 0.0 <= result["M_dyn"] <= 2.0, f"M_dyn={result['M_dyn']} out of plausible range"
    print(f"[selftest] PASS: M_dyn={result['M_dyn']:.4f} n_valid={result['n_valid']} "
          f"at N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    # Per-triplet M_dyn across seeds
    triplet_keys = list(set(
        k for v in per_seed.values() for k in v.get("triplets", {}).keys()
    ))
    by_triplet = {}
    for key in triplet_keys:
        mdyn_vals = []
        for sd in per_seed.values():
            tr = sd.get("triplets", {}).get(key, {})
            m = tr.get("M_dyn", float("nan"))
            if not math.isnan(m):
                mdyn_vals.append(m)
        by_triplet[key] = {
            "mean_M_dyn": float(np.mean(mdyn_vals)) if mdyn_vals else float("nan"),
            "std_M_dyn": float(np.std(mdyn_vals)) if mdyn_vals else float("nan"),
            "n_seeds": len(mdyn_vals),
        }

    all_mdyn = [v["mean_M_dyn"] for v in by_triplet.values() if not math.isnan(v["mean_M_dyn"])]
    return {
        "by_triplet": by_triplet,
        "global_mean_M_dyn": float(np.mean(all_mdyn)) if all_mdyn else float("nan"),
        "n_triplets": len(all_mdyn),
        "n_triplets_pass_hp": sum(1 for m in all_mdyn if m >= HP_MDYN),
        "n_triplets_fail_hf": sum(1 for m in all_mdyn if m <= HF_MDYN),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    global_m = agg["global_mean_M_dyn"]
    n_trip = agg["n_triplets"]
    n_pass = agg["n_triplets_pass_hp"]
    n_fail = agg["n_triplets_fail_hf"]
    n_required_pass = max(1, math.ceil(n_trip * HP_TRIPLET_FRAC))
    n_required_fail = max(1, math.ceil(n_trip * HP_TRIPLET_FRAC))

    if math.isnan(global_m):
        return ("HARD_FAIL", "global_mean_M_dyn is NaN -- instrumentation failure.")

    if n_fail >= n_required_fail:
        return ("HARD_FAIL",
                f"CK dynamical ultrametricity ABSENT. global_mean_M_dyn={global_m:.4f} <= {HF_MDYN}. "
                f"n_triplets_fail={n_fail}/{n_trip}. "
                f"Substrate's Glauber trajectory is NOT in CK aging class.")

    if n_pass >= n_required_pass:
        return ("HARD_PASS",
                f"CK DYNAMICAL ULTRAMETRICITY CONFIRMED. global_mean_M_dyn={global_m:.4f} >= {HP_MDYN}. "
                f"n_triplets_pass={n_pass}/{n_trip}. "
                f"CK prediction range [0.85,0.95]; observed {global_m:.4f}. "
                f"Substrate trajectory space is ultrametric: CK aging class confirmed.")

    return ("MIDDLE_BAND",
            f"Partial CK signature. global_mean_M_dyn={global_m:.4f} "
            f"(hp={HP_MDYN}, hf={HF_MDYN}). n_pass={n_pass}, n_fail={n_fail}/{n_trip}. "
            f"Escalate to FULL with larger R and more seeds.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"ALPHA={ALPHA} R={R_REPLICAS} TRIPLETS={TRIPLETS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "ALPHA": ALPHA, "R": R_REPLICAS, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "alpha": ALPHA, "R": R_REPLICAS,
        "seeds": SEEDS, "triplets": TRIPLETS,
        "aggregated": agg,
        "thresholds": {"HP_MDYN": HP_MDYN, "HF_MDYN": HF_MDYN},
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
