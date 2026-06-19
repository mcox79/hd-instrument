"""
activation_barrier_r3b_n8192_v3_n8192 -- PP-33 R3b: activation barrier N-scale at N=8192.

R3a (v2_n4096 extended grid) MIDDLE_BAND: nf_crit boundary persists at grid_max=0.90;
ratio=None (nf_crit for alpha=0.10 never drops below 0.50 in 0.00..0.90 grid at N=4096).
n_valid_nf=25 (nf_crit measured but all at grid boundary).

R3b = N-scale: test whether substrate's retrieval boundary moves to resolvable range at N=8192.
Key question: at N=8192, does recall drop below 0.50 at alpha=0.10 before noise_frac=0.90?
If yes: nf_crit is now resolvable -> ratio(0.05/0.10) can be computed -> HP/MID/HF verdict.
If no: MIDDLE_BAND; R3c (lower alpha values {0.01,0.02,0.03}) is next.

SCIENTIFIC QUESTION: Is the nf_crit boundary an N=4096 finite-N artifact?
At larger N, Hopfield networks are less robust to noise (more patterns compete) so recall
should drop at lower noise_frac. If the transition shifts to nf < 0.90, ratio is resolvable.

FORMULA SELF-TESTS (PROT-022):
  1. Arrhenius ratio formula: (alpha_c - 0.05) / (alpha_c - 0.10) = 2.3157 +- 0.001
     [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10] [EXPECTED: 2.3157 within 0.001]
  2. b=0.3 ratio prediction: 2.3157^0.3 in [1.25, 1.40]
     [INPUT: b=0.3] [EXPECTED: ratio_b03 approx 1.287]
  3. Extended grid: max step = 0.01 (FULL). Range 0.00..0.90 => 91 points.
     [EXPECTED: len(NOISE_FRACS) = 91]
  4. M at alpha=0.10 N=8192: int(0.10 * 8192) = 819 >= 1.
     [EXPECTED: M_alpha10_N8192 = 819]

PRE-REGISTERED BANDS (same as R3a; N-scale does not change hypothesis):
  HARD-PASS: power-law exponent b < 0.7 AND ratio(0.05/0.10) > 1.30 AND n_monotone >= 4/5
  MIDDLE: b in [0.7, 1.1] OR ratio in [1.10, 1.30] OR ratio=None (boundary persists at N=8192)
  HARD-FAIL: b > 1.2 (super-linear) OR ratio <= 1.02 (flat)

NOTE: if ratio=None even at N=8192 with extended grid, MIDDLE_BAND.
  R3c (lower alpha values) is next rescue.

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-022: formula self-tests above.
QUEUE: remote_cpu_queue (pure CPU; 5 alpha x 91 noise steps x 5 seeds at N=8192).
TIMEOUT ESTIMATE: R3a (N=4096 extended grid) elapsed ~134s FULL 5-seed. N-scale: N=8192 is
  2x larger; O(N^2) W matrix and per-step ops dominate.
  ceil(1.5 * 134 * (8192/4096)^2 * (5/5)) = ceil(1.5 * 134 * 4) = ceil(804) = 900s.
  With 2x margin for extended high-noise region: 1800s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "activation_barrier_r3b_n8192_v3_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_VALUES = [0.02, 0.05, 0.08, 0.10, 0.12]
CRIT_RECALL = 0.5
N_RETRIEVAL_STEPS = 8

# PROT-022 formula self-tests (at module scope)
_PREDICTED_BARRIER_RATIO = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)  # 2.3158
assert abs(_PREDICTED_BARRIER_RATIO - 2.3157) < 0.001, f"barrier ratio: {_PREDICTED_BARRIER_RATIO:.4f}"
_B03_RATIO = _PREDICTED_BARRIER_RATIO ** 0.3
assert 1.25 < _B03_RATIO < 1.40, f"b=0.3 ratio: {_B03_RATIO:.4f}"

# PROT-022 test 4: M at alpha=0.10 N=8192
_M_ALPHA10_N8192 = int(0.10 * N)  # 819
assert _M_ALPHA10_N8192 == 819, f"M_alpha10_N8192={_M_ALPHA10_N8192} expected 819"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024
    N_QUERIES = 5
    # Smoke grid 0..0.90 step 0.05 (same as R3a smoke)
    NOISE_FRACS = [round(i * 0.05, 3) for i in range(19)]  # 0..0.90 step 0.05 = 19 pts
    ALPHA_VALUES_ACTIVE = [0.05, 0.10]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 8
    # EXTENDED GRID: 0.00..0.90 step 0.01 => 91 points (same as R3a full)
    NOISE_FRACS = [round(i * 0.01, 3) for i in range(91)]  # 0.00..0.90 step 0.01
    ALPHA_VALUES_ACTIVE = ALPHA_VALUES

assert len(NOISE_FRACS) == (19 if RUN_MODE == "smoke" else 91), \
    f"grid size check: {len(NOISE_FRACS)} expected {19 if RUN_MODE=='smoke' else 91}"

# Pre-registered thresholds (same as R3a)
HP_B_MAX = 0.7
HP_RATIO_MIN = 1.30
HF_B_MAX = 1.2
HF_RATIO_MIN = 1.02
MIDDLE_RATIO_LOW = 1.10


def _instrumentation_selftest() -> None:
    r = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)
    assert abs(r - 2.3157) < 0.002, f"barrier ratio formula: {r:.4f}"

    b03 = r ** 0.3
    assert 1.25 < b03 < 1.40, f"b=0.3 ratio out of range: {b03:.4f}"

    step_max = max(abs(NOISE_FRACS[i+1] - NOISE_FRACS[i]) for i in range(len(NOISE_FRACS)-1))
    expected_step = 0.05 if RUN_MODE == "smoke" else 0.01
    assert abs(step_max - expected_step) < 1e-9, f"grid step: {step_max:.4f} expected {expected_step}"

    expected_len = 19 if RUN_MODE == "smoke" else 91
    assert len(NOISE_FRACS) == expected_len, f"grid length: {len(NOISE_FRACS)} expected {expected_len}"

    assert _M_ALPHA10_N8192 == 819, f"M_alpha10_N8192={_M_ALPHA10_N8192} expected 819"

    # Small-scale recall sweep to verify filter passes >= 1 item
    N_t = 64
    M_t = max(1, int(0.05 * N_t))
    rng = np.random.RandomState(0)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N_t)
    fracs = [0.0, 0.20, 0.40, 0.60, 0.80]
    recalls = []
    for nf in fracs:
        acc = 0.0
        for k in range(M_t):
            probe = Xi[k].copy()
            if nf > 0:
                flip = rng.random(N_t) < nf
                probe[flip] *= -1.0
            state = probe
            for _ in range(N_RETRIEVAL_STEPS):
                h = W @ state
                state = np.sign(h).astype(np.float32)
                state[state == 0] = 1.0
            acc += float(np.mean(state == Xi[k]))
        recalls.append(acc / M_t)
    assert all(not np.isnan(v) for v in recalls), f"selftest recalls contain NaN: {recalls}"
    assert len(recalls) >= 1, "no valid recall measurements"
    print(f"[selftest] PASS: barrier_ratio={r:.4f}, b03={b03:.4f}, "
          f"grid_step={step_max:.4f}, grid_len={len(NOISE_FRACS)}, "
          f"M_alpha10={_M_ALPHA10_N8192}, recall_scan ok N_active={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def measure_recall_curve(alpha: float, n_dim: int, seed: int) -> Optional[float]:
    """Measure nf_crit for given alpha at n_dim.
    Returns the noise fraction where recall drops below CRIT_RECALL=0.5, or boundary value.
    """
    M = max(1, int(alpha * n_dim))
    rng = np.random.RandomState(seed + int(alpha * 1000))
    Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
    W = (Xi.T @ Xi) / float(n_dim)

    last_nf_above = None
    first_nf_below = None

    for nf in NOISE_FRACS:
        total_acc = 0.0
        n_q = min(N_QUERIES, M)
        for k in range(n_q):
            probe = Xi[k].copy()
            if nf > 0:
                flip_mask = rng.random(n_dim) < nf
                probe[flip_mask] *= -1.0
            state = probe
            for _ in range(N_RETRIEVAL_STEPS):
                h = W @ state
                state = np.sign(h).astype(np.float32)
                state[state == 0] = 1.0
            acc = float(np.mean(state == Xi[k]))
            total_acc += acc
        mean_acc = total_acc / n_q

        if mean_acc >= CRIT_RECALL:
            last_nf_above = nf
        else:
            if first_nf_below is None:
                first_nf_below = nf
                break

    if last_nf_above is not None and first_nf_below is not None:
        return (last_nf_above + first_nf_below) / 2.0
    elif last_nf_above is not None:
        return last_nf_above  # never dropped below crit in this grid
    return None


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    nf_crit_by_alpha = {}

    for alpha in ALPHA_VALUES_ACTIVE:
        nf_c = measure_recall_curve(alpha, n_dim, seed)
        nf_crit_by_alpha[str(alpha)] = float(nf_c) if nf_c is not None else None
        nf_str = f"{nf_c:.4f}" if nf_c is not None else "None"
        print(f"  [seed={seed} alpha={alpha}] nf_crit={nf_str}", flush=True)

    nf_05 = nf_crit_by_alpha.get("0.05")
    nf_10 = nf_crit_by_alpha.get("0.1")
    if nf_10 is None:
        nf_10 = nf_crit_by_alpha.get("0.10")
    ratio_05_10 = float(nf_05 / nf_10) if (nf_05 and nf_10 and nf_10 > 1e-9) else None

    valid_pts = [(alpha, nf_crit_by_alpha[str(alpha)])
                 for alpha in ALPHA_VALUES_ACTIVE
                 if nf_crit_by_alpha.get(str(alpha)) is not None]

    b_fit = None
    if len(valid_pts) >= 2:
        x_vals = np.array([np.log(ALPHA_C - a) for a, _ in valid_pts])
        y_vals = np.array([np.log(nf + 1e-12) for _, nf in valid_pts])
        if len(x_vals) >= 2:
            try:
                coeffs = np.polyfit(x_vals, y_vals, 1)
                b_fit = float(coeffs[0])
            except Exception:
                b_fit = None

    elapsed = time.time() - t0
    nf_05_str = f"{nf_05:.4f}" if nf_05 else "None"
    nf_10_str = f"{nf_10:.4f}" if nf_10 else "None"
    ratio_str = f"{ratio_05_10:.4f}" if ratio_05_10 else "None"
    b_str = f"{b_fit:.3f}" if b_fit is not None else "None"
    print(f"  [seed={seed} N={n_dim}] nf05={nf_05_str} nf10={nf_10_str} "
          f"ratio={ratio_str} b_fit={b_str} grid_len={len(NOISE_FRACS)} elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "nf_crit_by_alpha": nf_crit_by_alpha,
        "ratio_05_10": ratio_05_10,
        "b_fit": b_fit,
        "elapsed_s": elapsed,
        "grid_max": max(NOISE_FRACS),
        "grid_len": len(NOISE_FRACS),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    ratios = [r["ratio_05_10"] for r in results if r.get("ratio_05_10") is not None]
    b_fits = [r["b_fit"] for r in results if r.get("b_fit") is not None]

    mean_ratio = float(np.mean(ratios)) if ratios else None
    mean_b = float(np.mean(b_fits)) if b_fits else None
    n_monotone = sum(1 for r in results
                     if r.get("b_fit") is not None and r["b_fit"] > 0)

    n_valid_nf = sum(1 for r in results
                     for alpha in ALPHA_VALUES_ACTIVE
                     if r.get("nf_crit_by_alpha", {}).get(str(alpha)) is not None)

    ratio_str = f"{mean_ratio:.4f}" if mean_ratio is not None else "None"
    b_str = f"{mean_b:.3f}" if mean_b is not None else "None"
    summary = (
        f"ratio={ratio_str}(HP>{HP_RATIO_MIN} HF<={HF_RATIO_MIN}) "
        f"b={b_str}(HP<{HP_B_MAX} HF>{HF_B_MAX}) "
        f"n_monotone={n_monotone}/{len(results)} n_valid_nf={n_valid_nf} "
        f"grid_max={max(NOISE_FRACS):.2f} N={N} n_seeds={len(results)}"
    )

    if n_valid_nf == 0:
        return ("HARD_FAIL", f"HARD_FAIL: no nf_crit measurements at all. {summary}")

    if mean_ratio is None:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: ratio unavailable (nf_crit boundary persists at grid_max={max(NOISE_FRACS):.2f}); "
                f"n_valid_nf={n_valid_nf}. R3c (lower alpha) needed. {summary}")

    if mean_ratio <= HF_RATIO_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL: ratio={mean_ratio:.4f}<={HF_RATIO_MIN} (flat). {summary}")
    if mean_b is not None and mean_b > HF_B_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL: b={mean_b:.3f}>{HF_B_MAX} (super-linear). {summary}")

    if (mean_ratio > HP_RATIO_MIN and mean_b is not None and mean_b < HP_B_MAX
            and n_monotone >= int(0.8 * len(results))):
        return ("HARD_PASS",
                f"HARD_PASS: sublinear compression b={mean_b:.3f}<{HP_B_MAX}; "
                f"ratio={mean_ratio:.4f}>{HP_RATIO_MIN}. PP-33 R3 viable at N=8192. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial signal at N=8192. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_values={ALPHA_VALUES_ACTIVE} n_noise_fracs={len(NOISE_FRACS)} "
      f"grid_max={max(NOISE_FRACS):.2f}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha_values": ALPHA_VALUES_ACTIVE, "run_mode": RUN_MODE,
              "grid_max": max(NOISE_FRACS)}

done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
elapsed_total = time.time() - t_sweep

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE,
    "n_seeds": len(all_results), "elapsed_s": elapsed_total,
    "alpha_values": ALPHA_VALUES_ACTIVE,
    "grid_max": max(NOISE_FRACS),
    "grid_len": len(NOISE_FRACS),
    "predicted_barrier_ratio_b1": float(_PREDICTED_BARRIER_RATIO),
    "predicted_ratio_b03": float(_B03_RATIO),
    "per_seed": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
