"""KF-4 DRIFT DETECTION v2: N=4096 5-seed FULL (defense-in-depth extension).

PARENT: exp_kf4_drift_detect_v1.py -- v1 used 3 seeds [7,17,23].
  v1 result: MIDDLE_BAND (r_drift tracked at 3-seed, r_bnv=0.994; spectral weak).
  v2 extends to 5-seed [7,17,23,31,41] to lock in r_bnv=0.994 as reproducible
  before Cat-B drift-detection killer feature commit.

SCIENTIFIC QUESTION (Killer Feature 4):
  5/5 seeds: r_drift >= 0.9 AND r_bnv >= 0.9 across sequential edit sequence.
  Defense-in-depth: r_bnv=0.994 at 3-seed merits 5-seed confirmation.

PRE-REGISTERED BANDS (v2 tightened per routing-note spec):
  HARD_PASS: 5/5 seeds r_drift >= 0.9 AND 5/5 seeds r_bnv >= 0.9.
    Interpretation: BNV is a reliable early-warning signal across all seeds.
  HARD_FAIL: >= 2 seeds r_drift < 0.5.
    Drift is not consistently accumulating -- not a product-grade signal.
  MIDDLE_BAND: r_drift >= 0.9 in >= 3/5 seeds but r_bnv weaker OR < 5/5 seeds.

FORMULA SELF-TESTS (inherited from v1):
  1. pearson_r([0..9], [0..9]) = 1.0.
  2. drift_amplitude = ||W_t - W_0||_F / ||W_0||_F. After 0 edits = 0.
  3. After n_edits edits: drift_final > 0.
  4. HARD_PASS fires: 5/5 r_drift>=0.9 AND r_bnv>=0.9.
  5. HARD_FAIL fires: 2+ seeds r_drift < 0.5.

TIMEOUT ESTIMATE:
  smoke_wall_s (v1 CPU, 1 seed): 0.1s.
  Full v2: N=4096, 5 seeds (was 3), 50 edits.
  Scale vs v1 3-seed: (5/3) factor; same N.
  v1 prereg estimate: 900s for 3 seeds. v2: 900 * (5/3) = 1500s.
  With +50% buffer: 2250s -> round to 2400s. Under 2h.
  timeout_s = 2400.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly; N_FULL=4096).
Queue: overnight_queue (GPU; Kerdock N=4096, 5-seed drift sequence)
Pre-reg: preregs/2026-05-27_kf4_drift_detect_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load v1 base (provides all core functions)
_v1_path = REPO / "experiments" / "exp_kf4_drift_detect_v1.py"
_v1_spec = importlib.util.spec_from_file_location("kf4v1", _v1_path)
kf4v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(kf4v1)

# PRODUCTION CONFIG v2 -- PROT-018: no _nN suffix; N_FULL=4096 stated explicitly
N_FULL = 4096
N_SMOKE = 1024
M_FRAC = 1.0
N_EDITS_FULL = 50
N_EDITS_SMOKE = 25
MEASURE_EVERY = 5
N_PROBE = 200
N_PROBE_SMOKE = 50
# v2: 5 seeds for defense-in-depth
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# v2 tightened thresholds
PASS_DRIFT_R = 0.90
PASS_BNV_R = 0.90       # v2: explicit BNV pass threshold
FAIL_DRIFT_R = 0.50
FAIL_SEEDS_COUNT = 2    # >= 2 seeds below FAIL_DRIFT_R = HARD_FAIL


def get_output_dir(default_name: str = "kf4_drift_detect_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict_v2(summary: dict) -> tuple[str, str]:
    """v2 verdict: tightened 5-seed HP gate + explicit BNV >= 0.9 requirement."""
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("KF4_INCONCLUSIVE", "No per-seed data.")

    r_drifts = [sd["r_drift"] for sd in per_seed.values() if sd.get("n_steps", 0) > 0]
    r_bnvs = [sd["r_bnv"] for sd in per_seed.values()]
    r_spectrals = [sd["r_spectral"] for sd in per_seed.values()]
    drift_finals = [sd["drift_final"] for sd in per_seed.values()]

    if not r_drifts:
        return ("KF4_INCONCLUSIVE", "No drift data.")

    n_seeds = len(r_drifts)
    seeds_drift_pass = sum(1 for r in r_drifts if r >= PASS_DRIFT_R)
    seeds_bnv_pass = sum(1 for r in r_bnvs if r >= PASS_BNV_R)
    seeds_fail = sum(1 for r in r_drifts if r < FAIL_DRIFT_R)
    mean_drift_r = sum(r_drifts) / n_seeds
    mean_bnv_r = sum(r_bnvs) / n_seeds if r_bnvs else 0.0
    mean_spectral_r = sum(r_spectrals) / n_seeds if r_spectrals else 0.0
    mean_drift_final = sum(drift_finals) / n_seeds if drift_finals else 0.0

    # HARD_FAIL: >= 2 seeds drift doesn't accumulate
    if seeds_fail >= FAIL_SEEDS_COUNT:
        return ("KF4_HARD_FAIL",
                f"Drift NOT reproducible: {seeds_fail}/{n_seeds} seeds r_drift < {FAIL_DRIFT_R}. "
                f"r_drift={[round(r, 3) for r in r_drifts]}. "
                f"Drift signal is not a reliable Cat-B product feature.")

    # HARD_PASS v2: 5/5 r_drift >= 0.9 AND 5/5 r_bnv >= 0.9
    if seeds_drift_pass == n_seeds and seeds_bnv_pass == n_seeds:
        return ("KF4_HARD_PASS",
                f"DRIFT DETECTION 5-SEED CONFIRMED. "
                f"{seeds_drift_pass}/{n_seeds} seeds r_drift >= {PASS_DRIFT_R}. "
                f"{seeds_bnv_pass}/{n_seeds} seeds r_bnv >= {PASS_BNV_R}. "
                f"mean_r_drift={mean_drift_r:.3f}. "
                f"mean_r_bnv={mean_bnv_r:.3f}. "
                f"mean_r_spectral={mean_spectral_r:.3f}. "
                f"mean_drift_final={mean_drift_final:.4f}. "
                f"Cat-B drift-detection killer feature: BNV is reliable early-warning signal.")

    return ("KF4_MIDDLE_BAND",
            f"Drift mostly detectable. "
            f"r_drift_pass={seeds_drift_pass}/{n_seeds} seeds. "
            f"r_bnv_pass={seeds_bnv_pass}/{n_seeds} seeds. "
            f"mean_r_drift={mean_drift_r:.3f}. mean_r_bnv={mean_bnv_r:.3f}. "
            f"mean_drift_final={mean_drift_final:.4f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(SEEDS_FULL) == 5, f"v2 requires 5 seeds; got {SEEDS_FULL}"

    # Import-chain: v1 functions accessible
    assert hasattr(kf4v1, "run_one_seed"), "v1 run_one_seed missing"
    assert hasattr(kf4v1, "pearson_r"), "v1 pearson_r missing"

    # Self-test 1: verdict v2 HARD_PASS
    def mk_sd(r_d, r_s, r_b):
        return {"r_drift": r_d, "r_spectral": r_s, "r_bnv": r_b,
                "r_retention": -0.5, "drift_final": 0.05, "retention_final": 0.99,
                "n_steps": 10, "drift_series": [0.01*i for i in range(1, 11)],
                "bnv_series": [], "spectral_series": [], "retention_series": []}

    v, msg = compute_verdict_v2({"per_seed": {
        str(s): dict(seed=s, N=4096, M=4096, **mk_sd(0.95, 0.60, 0.95))
        for s in [7, 17, 23, 31, 41]
    }})
    assert v == "KF4_HARD_PASS", f"Expected KF4_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: 2+ seeds fail drift
    v, msg = compute_verdict_v2({"per_seed": {
        "7": dict(seed=7, N=4096, M=4096, **mk_sd(0.30, 0.10, 0.05)),
        "17": dict(seed=17, N=4096, M=4096, **mk_sd(0.25, 0.10, 0.05)),
        "23": dict(seed=23, N=4096, M=4096, **mk_sd(0.95, 0.60, 0.95)),
    }})
    assert v == "KF4_HARD_FAIL", f"Expected KF4_HARD_FAIL, got {v}: {msg}"

    # Smoke forward pass via v1 run_one_seed
    device = torch.device("cpu")
    config_smoke = {"smoke": True, "N": 1024, "n_edits": 10, "n_probe": 30}
    result = kf4v1.run_one_seed(17, config_smoke, device)
    assert "r_drift" in result and "r_bnv" in result, "missing r_drift or r_bnv"
    assert result["drift_final"] > 0.0, (
        f"SUSPICIOUS: drift_final=0 after 10 edits: {result['drift_final']}"
    )

    print("[SELFTEST PASS] kf4_drift_detect_v2 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE
    config = {"smoke": smoke, "N": N, "n_edits": n_edits, "n_probe": n_probe}

    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[kf4v2] N={N} seeds={seeds} n_edits={n_edits} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = kf4v1.run_one_seed(seed, config, device)
        te = time.time() - ts
        print(f"  seed {seed} done in {te:.1f}s r_drift={result['r_drift']:.3f} "
              f"r_bnv={result['r_bnv']:.3f} drift_final={result['drift_final']:.4f}", flush=True)
        per_seed[str(seed)] = result
        # Per-seed checkpoint
        checkpoint_path = out_dir / "metrics_checkpoint.json"
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"per_seed": per_seed, "N_full": N_FULL}, f, indent=2)

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_v2(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[kf4v2] VERDICT: {verdict}", flush=True)
    print(f"[kf4v2] {verdict_msg}", flush=True)
    print(f"[kf4v2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
