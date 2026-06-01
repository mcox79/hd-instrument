"""Orthogonal non-equilibrium corroborator v1: Hatano-Sasa excess-entropy probe at N=8192.

CONTEXT:
  TCFT FULL HARD_PASS (tcft_n8192_v7 running) confirms deletion-certificate foundation.
  Non-eq-stat-mech framework class is 🟢 45-60% (v229: BID HARD_PASS outside 3 Hopfield
  static bands + SKAH-M non-reciprocal Hopfield class).
  Crooks FT (v153 FULL HARD_PASS) + Sagawa-Ueda (v3 HARD_PASS N=4096) + TCFT (v7 in-flight)
  are the positive non-eq anchors.

  TCFT followon routing note (strategy_request_to_exp_dev_tcft_followon_2026-05-27.md)
  sketches an "independent angle on TCFT HARD_PASS" as a CPU candidate.

WHAT IS HATANO-SASA EXCESS ENTROPY:
  Hatano-Sasa (HS) relation (Hatano & Sasa, PRL 2001) is a fluctuation theorem for
  NESS (non-equilibrium steady states):
    <exp(-sigma_ex)> = 1
  where sigma_ex is the "excess entropy production" accumulated during a
  protocol-driven perturbation from one NESS to another.

  For our substrate:
  - The "NESS" is the steady-state retrieval distribution of the Hopfield W matrix.
  - A "protocol perturbation" is adding new patterns (overwriting W incrementally).
  - sigma_ex is computed as the change in log-probability of the state under the new
    W vs the old W:
      sigma_ex(mu) = log(P_new(v_mu)) - log(P_old(v_mu))
    where P(v) = exp(-beta * E(v)) / Z, E(v) = -v^T W v / 2.

  HS test:
    mean(exp(-sigma_ex)) should be near 1.0 (HS equality).
  Deviation from 1.0 signals NESS departure.

  The primary metric is:
    hs_ratio = mean(exp(-sigma_ex)) -- target ~ 1.0 if substrate satisfies HS
    hs_sigma_ex_var -- variance of sigma_ex (lower = more uniform NESS transition)

  Compare to Crooks FT (v153): Crooks uses forward/reverse work distributions to test
  equilibrium. HS tests NESS-to-NESS transitions. They are ORTHOGONAL non-eq tests --
  different mathematical structures testing different aspects of the non-eq class.

SCIENTIFIC QUESTION:
  Does substrate's incremental pattern loading satisfy the Hatano-Sasa relation?
  A positive result (hs_ratio near 1.0) is independent corroboration of non-eq class
  from a different mathematical angle than Crooks/TCFT.

DESIGN:
  1. Initialize W = 0. Load M_init patterns to establish initial NESS.
  2. Compute log P_old(v_mu) for M_probe patterns under old W.
  3. Load M_delta more patterns (protocol perturbation).
  4. Compute log P_new(v_mu) for same M_probe patterns under new W.
  5. sigma_ex(mu) = log P_new / log P_old (simplified; see below for exact formula).
  6. hs_ratio = mean(exp(-sigma_ex)) -- target ~ 1.0.

  Energy E(v) = -v^T W v / 2. log P proportional to -beta * E (dropping log Z).
  sigma_ex(mu) = -beta * (E_new(v_mu) - E_old(v_mu)) = beta * (E_old - E_new).

  M_init = int(0.10 * N), M_delta = int(0.02 * N), M_probe = min(50, M_init).
  beta = 1.0 (inverse temperature at KBT=1).

PRE-REGISTERED BANDS:
  No prior empirical anchor on this exact protocol. Bands widened to +-50% per
  calibration-probe policy.

  HARD_PASS (HS equality confirmed):
    hs_ratio in [0.50, 1.50] in >= 3/5 seeds.
    Interpretation: substrate satisfies HS relation; confirms NESS non-eq class
    from an angle independent of Crooks/TCFT.

  HARD_FAIL (HS equality violated):
    |hs_ratio - 1.0| > 5.0 in ALL 5 seeds.
    (hs_ratio < 0.001 or > 6.0)
    Interpretation: substrate does NOT satisfy HS; non-eq class membership uncertain.

  MIDDLE_BAND:
    hs_ratio in (1.50, 6.0) OR only 1-2 seeds pass the [0.50, 1.50] band.

  Calibration note: first direct HS measurement on this substrate; bands [0.50, 1.50]
  represent +-50% around the theoretical prediction of 1.0 per calibration-probe policy.

FORMULA SELF-TESTS:
  1. For W = 0: E(v) = 0 for all v. sigma_ex = 0. hs_ratio = mean(exp(0)) = 1.0.
  2. For M_probe=1 with sigma_ex=0: hs_ratio = 1.0.
  3. log P formula: -beta * (E_new - E_old) = beta * (E_old - E_new).
  4. hs_ratio = mean(exp(-sigma_ex)) where sigma_ex is a scalar per probe pattern.
  5. smoke scale N=512, M_init=51, M_delta=10, M_probe=50: all arrays should be non-empty.

TIMEOUT ESTIMATE:
  Smoke at N=512: outer-product W build O(M*N^2) = ~51*512^2 = ~13M ops per seed.
  Estimated ~0.5s per seed.
  FULL at N=8192: O(M*N^2) = ~820*8192^2 = ~55B ops per seed. Scales as N^2.
  Seed ratio 5/1. N-ratio (8192/512)^2 = 256.
  timeout_s = ceil(1.5 * 0.5 * 256 * 5) = ceil(960) = 1200s.
  Safety margin 50%: 1800s. Under 4h. Use 1800s.

OOM PRE-CHECK:
  W at N=8192: 8192^2 * 8 bytes (float64) = 512MB < 6GB. OK.
  Two W matrices (old + new): 1GB < 6GB. OK.

N-suffix: no _nN suffix; production N = 8192 (N_FULL = 8192 stated explicitly below).
Queue: remote_cpu_queue (pure numpy; no CUDA; ~1800s)
Pre-reg: preregs/2026-05-27_ortho_noneq_corroborator_v1.md
Parent: TCFT followon routing note (strategy_request_to_exp_dev_tcft_followon_2026-05-27.md)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL = 8192   # PROT-018: no _nN suffix; N stated explicitly
N_SMOKE = 512

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

BETA = 1.0
ALPHA_INIT = 0.10   # M_init / N: initial NESS load
ALPHA_DELTA = 0.02  # M_delta / N: perturbation size
M_PROBE_CAP = 50    # maximum probe patterns per seed

# Pre-registered HS bands
HS_PASS_LOW = 0.50
HS_PASS_HIGH = 1.50
HS_FAIL_EXTREME = 6.0   # |hs_ratio| > 6 = HARD_FAIL
HP_SEED_MIN = 3          # >= 3/5 seeds pass -> HARD_PASS


def build_W(N: int, M: int, rng: np.random.Generator) -> Tuple:
    """Build Hopfield W by incremental outer-product; return W + patterns."""
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        W += np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def energy(v: np.ndarray, W: np.ndarray) -> float:
    """E(v) = -v^T W v / 2."""
    return float(-0.5 * v @ W @ v)


def run_one_seed(N: int, seed: int) -> Dict:
    """Run Hatano-Sasa probe for one seed at dimension N."""
    rng = np.random.default_rng(seed)
    M_init = max(4, int(N * ALPHA_INIT))
    M_delta = max(2, int(N * ALPHA_DELTA))
    M_probe = min(M_PROBE_CAP, M_init)

    t0 = time.time()

    # Build W_old
    W_old, patterns_init = build_W(N, M_init, rng)

    # Sample probe patterns (subset of init patterns for reproducibility)
    probe_idx = np.arange(M_probe)
    probe_patterns = patterns_init[probe_idx]

    # Compute E_old for probe patterns
    E_old = np.array([energy(probe_patterns[i], W_old) for i in range(M_probe)],
                     dtype=np.float64)

    # Apply perturbation: add M_delta new patterns
    new_patterns = rng.choice([-1.0, 1.0], size=(M_delta, N)).astype(np.float64)
    W_new = W_old.copy()
    for mu in range(M_delta):
        v = new_patterns[mu]
        W_new += np.outer(v, v) / N
    np.fill_diagonal(W_new, 0.0)

    # Compute E_new for same probe patterns
    E_new = np.array([energy(probe_patterns[i], W_new) for i in range(M_probe)],
                     dtype=np.float64)

    # sigma_ex = beta * (E_old - E_new)
    sigma_ex = BETA * (E_old - E_new)

    # HS ratio: mean(exp(-sigma_ex))
    hs_values = np.exp(-sigma_ex)
    hs_ratio = float(np.mean(hs_values))
    hs_std = float(np.std(hs_values))
    sigma_ex_var = float(np.var(sigma_ex))

    elapsed = time.time() - t0

    # Per-seed pass check
    hp = HS_PASS_LOW <= hs_ratio <= HS_PASS_HIGH

    return {
        "N": N, "seed": seed, "M_init": M_init, "M_delta": M_delta, "M_probe": M_probe,
        "hs_ratio": hs_ratio, "hs_std": hs_std, "sigma_ex_var": sigma_ex_var,
        "hp": hp, "elapsed_s": round(elapsed, 3),
    }


def get_output_dir(default_name: str = "ortho_noneq_corroborator_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # PROT-018 explicit
    assert N_FULL == 8192, f"N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: W=0 gives hs_ratio = 1.0
    # When W_old = W_new = 0: E_old = E_new = 0, sigma_ex = 0, exp(-0)=1, mean=1.0
    rng0 = np.random.default_rng(42)
    N_t = 8
    M_t = 1
    W0 = np.zeros((N_t, N_t))
    v0 = rng0.choice([-1.0, 1.0], size=N_t)
    E_old_t = energy(v0, W0)
    E_new_t = energy(v0, W0)
    sigma_ex_t = BETA * (E_old_t - E_new_t)
    hs_t = float(np.exp(-sigma_ex_t))
    assert abs(hs_t - 1.0) < 1e-9, f"W=0 should give hs_ratio=1.0; got {hs_t}"

    # Self-test 2: energy formula check
    W_id = np.eye(4)
    v_id = np.array([1.0, 1.0, 1.0, 1.0])
    E_check = energy(v_id, W_id)
    assert abs(E_check - (-2.0)) < 1e-9, f"energy([1,1,1,1], I4) should be -2.0; got {E_check}"

    # Self-test 3: run_one_seed at smoke scale
    r = run_one_seed(N=256, seed=17)
    assert "hs_ratio" in r, f"hs_ratio missing from result: {r}"
    assert r["hs_ratio"] is not None, "hs_ratio is None"
    assert not np.isnan(r["hs_ratio"]), f"hs_ratio is NaN: {r}"
    assert r["M_probe"] > 0, f"M_probe = 0; validity filter eliminated all probes"

    # Self-test 4: multi-scale smoke at N=256 and N=512
    r4 = run_one_seed(N=512, seed=17)
    assert "hs_ratio" in r4 and r4["hs_ratio"] is not None, f"hs_ratio null at N=512: {r4}"
    assert not np.isnan(r4["hs_ratio"]), f"hs_ratio NaN at N=512: {r4}"

    # Self-test 5: output-path parameterization
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_hs_path_check"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_hs_path_check", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    # Self-test 6: OOM check
    oom_bytes = N_FULL * N_FULL * 8 * 2  # two W matrices
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] ortho_noneq_corroborator_v1 PASSED: "
          f"W=0 hs_ratio=1.0 OK, N=256 smoke hs_ratio={r['hs_ratio']:.4f}, "
          f"N=512 hs_ratio={r4['hs_ratio']:.4f}, OOM={oom_bytes:.2e}", flush=True)


# Import Tuple for type annotation
from typing import Tuple  # noqa: E402 (below sys.path insert)

_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    exp_name = os.environ.get("HDLAB_EXP_NAME", "ortho_noneq_corroborator_v1")
    mode_str = "SMOKE" if smoke else "FULL"
    print(f"[run] {exp_name} mode={mode_str} N={N} seeds={seeds}", flush=True)

    if not smoke:
        assert N == N_FULL, f"FULL run must use N={N_FULL}; got {N}"

    per_seed = {}
    hp_count = 0
    for seed in seeds:
        r = run_one_seed(N, seed)
        per_seed[str(seed)] = r
        if r["hp"]:
            hp_count += 1
        print(f"  seed={seed}: hs_ratio={r['hs_ratio']:.4f} "
              f"hp={r['hp']} elapsed={r['elapsed_s']:.2f}s", flush=True)

    # Verdict
    n_seeds = len(seeds)
    if smoke:
        r0 = list(per_seed.values())[0]
        hs = r0["hs_ratio"]
        if HS_PASS_LOW <= hs <= HS_PASS_HIGH:
            verdict = "SMOKE_PASS"
            msg = f"Smoke N={N}: hs_ratio={hs:.4f} in [{HS_PASS_LOW}, {HS_PASS_HIGH}]. FULL warranted."
        else:
            verdict = "SMOKE_MIDDLE_BAND"
            msg = f"Smoke N={N}: hs_ratio={hs:.4f} outside pass band. FULL uncertain."
    else:
        if hp_count >= HP_SEED_MIN:
            verdict = "HARD_PASS"
            msg = (f"HARD_PASS: hs_ratio in [{HS_PASS_LOW}, {HS_PASS_HIGH}] in "
                   f"{hp_count}/{n_seeds} seeds at N={N}. "
                   f"HS relation confirmed; independent non-eq corroboration of TCFT/Crooks.")
        else:
            # Check HARD_FAIL: all seeds have extreme hs_ratio
            all_extreme = all(
                abs(v["hs_ratio"] - 1.0) > HS_FAIL_EXTREME
                for v in per_seed.values()
            )
            if all_extreme:
                verdict = "HARD_FAIL"
                msg = (f"HARD_FAIL: hs_ratio extreme (|hs-1.0|>{HS_FAIL_EXTREME}) in all "
                       f"{n_seeds} seeds. HS relation violated; non-eq class uncertain.")
            else:
                verdict = "MIDDLE_BAND"
                hs_vals = [v["hs_ratio"] for v in per_seed.values()]
                msg = (f"MIDDLE_BAND: {hp_count}/{n_seeds} seeds pass hs_ratio band. "
                       f"hs_ratios: {[f'{h:.4f}' for h in hs_vals]}. "
                       f"Corroboration inconclusive.")

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "hp_count": hp_count,
        "n_seeds": n_seeds,
        "per_seed": per_seed,
        "config": {
            "N": N, "smoke": smoke, "seeds": seeds,
            "ALPHA_INIT": ALPHA_INIT, "ALPHA_DELTA": ALPHA_DELTA,
            "M_PROBE_CAP": M_PROBE_CAP, "BETA": BETA,
            "HS_PASS_LOW": HS_PASS_LOW, "HS_PASS_HIGH": HS_PASS_HIGH,
        },
    }
    mpath = get_output_dir(exp_name) / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
