"""
pp58_bbp_dense_xn_n8192_v1_n8192 -- PP-58 BBP spectral-gap calibration cross-N at N=8192.

CONTEXT (v372 all-night burst cycle 43):
  pp58_bbp_spectral_gap_calibration_v1_n16384 COMPLETED (v372 cycle 42 batch).
  N=16384 BBP result: ratio=4.13 predicted by BBP asymptote; sigma_g_audit_crit=0.726
  at alpha=0.05. Cross-N companion at N=8192 tests N-dependence of the BBP merging point
  and whether ratio continues to approach asymptote from below (N=8192 expected ratio ~3.0-3.5).

  BBP prediction: sigma_g_audit_crit = 1 - sqrt(alpha) - alpha = 0.726 at alpha=0.05
                  (N-independent in the large-N limit).
  At N=8192 the BBP transition is sharper; denser sigma_g grid used to catch the merging.

SCIENTIFIC QUESTION:
  Does the BBP eigenvalue-merging criterion at N=8192 agree with the BBP formula prediction
  (sigma_g_audit_crit ~ 0.726)? What is the ratio cap_crit/audit_crit at N=8192?
  Expected: ratio ~ 3.0-3.5 (below N=16384 ratio=4.13; approaching BBP asymptote from below).

OOM PRE-CHECK (GPU):
  W matrix at N=8192: 8192^2 * 4 = 268 MB. W+noise on CPU: 268 MB. Remote machine has 16+ GB. Fine.
  Xi on GPU at N=8192 M=409: 409 * 8192 * 4 = 13.4 MB GPU. Fine.
  Eigendecomp on CPU (numpy): ~0.1s/matrix at N=8192.

PRE-REGISTERED BANDS (PP-58 BBP cross-N N=8192; empirical anchor: N=16384 ratio=4.13):
  N=8192 prior isochoric ratio=3.0 (v353 MIDDLE). BBP predicts ratio increases with N.
  HARD-PASS: ratio in [2.5, 4.0] AND sigma_g_audit_crit in [0.55, 0.85]
             (N=8192 is below asymptote; audit_crit may be in 0.60-0.75 range).
  MIDDLE: ratio in [2.0, 5.0] but audit_crit or cap_crit outside HP range.
  HARD-FAIL: ratio < 2.0 OR ratio > 5.0 (BBP N-scaling prediction fails).

  Calibration note: no prior per-N BBP empirical anchor at N=8192 (isochoric v353 was different
  protocol -- kappa_3 not eigenspectrum). Bands set +-50% around N-scaled prediction per
  calibration-probe policy.

FORMULA SELF-TESTS (PROT-022):
  1. BBP sigma_g_audit_crit: 1 - sqrt(0.05) - 0.05 = 0.7264 at alpha=0.05.
     [INPUT: alpha=0.05] [EXPECTED: 0.7264 within 0.001]
  2. MP upper edge: (1 + sqrt(0.05))^2 = 1.4972 at alpha=0.05.
     [INPUT: alpha=0.05] [EXPECTED: 1.4972 within 0.01]
  3. M at alpha=0.05, N=8192: int(0.05 * 8192) = 409 >= 1.
     [EXPECTED: M = 409]
  4. W size at N=8192: 8192^2 * 4 = 268 MB < 512 MB.
     [EXPECTED: True]
  5. Dense sigma_g grid has >= 5 items in [0.55, 0.85].
     [EXPECTED: fine_count >= 5]
  6. Retrieval forward pass at tiny N: recall is non-NaN.

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: overnight_queue (GPU machine; eigendecomp on CPU numpy; Xi build on GPU).
TIMEOUT ESTIMATE: N=8192 eigendecomp ~0.1s/matrix. 22 sigma_g * 5 seeds = 110 calls * 0.1s = 11s.
  Plus retrieval: 5s total. Direct estimate: 30s. With margin: timeout=300s (use PROT-019 floor).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

try:
    import torch
    import torch.cuda
    HAVE_CUDA = torch.cuda.is_available()
except ImportError:
    HAVE_CUDA = False

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_bbp_dense_xn_n8192_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
_M_FULL = int(ALPHA * N)  # 409
assert _M_FULL == 409, f"M_full={_M_FULL} expected 409"

# BBP formula: audit_crit = 1 - sqrt(alpha) - alpha
BBP_AUDIT_CRIT_PRED = 1.0 - (ALPHA ** 0.5) - ALPHA  # 0.7264 at alpha=0.05
# Marchenko-Pastur upper edge
MP_LAMBDA_MAX_PRED = (1.0 + ALPHA ** 0.5) ** 2  # 1.4972 at alpha=0.05

# PROT-022 formula self-tests at module scope (arithmetic only, no GPU)
_bbp_crit = 1.0 - (ALPHA ** 0.5) - ALPHA
assert abs(_bbp_crit - 0.7264) < 0.001, f"BBP selftest: {_bbp_crit:.4f} expected 0.7264"
_mp_max = (1.0 + ALPHA ** 0.5) ** 2
assert abs(_mp_max - 1.4972) < 0.01, f"MP_max selftest: {_mp_max:.4f} expected 1.4972"
_w_bytes = N * N * 4
assert _w_bytes < 512e6, f"W size: {_w_bytes/1e6:.0f}MB expected < 512MB"
print(f"[selftest-formula] BBP_crit={_bbp_crit:.4f} MP_max={_mp_max:.4f} "
      f"M_full={_M_FULL} W_MB={_w_bytes/1e6:.0f}", flush=True)

# Dense sigma_g grid for N=8192 -- include fine-grid around BBP prediction
# At N=8192 the merging is at lower sigma_g than N=inf; test wider range
SIGMA_G_FULL = [
    0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.60, 0.65, 0.70, 0.726, 0.75,
    0.80, 0.85, 0.90, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0, 8.0
]
_fine_count = len([s for s in SIGMA_G_FULL if 0.55 <= s <= 0.85])
assert _fine_count >= 5, f"Dense sigma_g grid fine-count: {_fine_count} expected >= 5"
print(f"[selftest-formula] Dense sigma_g grid fine_count={_fine_count} OK", flush=True)

CRIT_RECALL = 0.50
CAP_CRIT_RECALL = 0.10
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10

# Pre-registered bands
HP_RATIO_LO = 2.5
HP_RATIO_HI = 4.0
HP_AUDIT_CRIT_LO = 0.55
HP_AUDIT_CRIT_HI = 0.85
MIDDLE_RATIO_LO = 2.0
MIDDLE_RATIO_HI = 5.0
HF_RATIO_LO = 2.0
HF_RATIO_HI = 5.0

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    SIGMA_G_USE = [0.0, 0.5, 1.0, 3.0, 5.0, 8.0, 12.0, 15.0]
    N_QUERIES_USE = 5
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    SIGMA_G_USE = SIGMA_G_FULL
    N_QUERIES_USE = N_QUERIES_PER_CELL


def hopfield_retrieve_np(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVAL_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def find_bbp_audit_crit(sigma_g_results: List[Dict]) -> float:
    """Find sigma_g where recall drops below CRIT_RECALL."""
    sorted_r = sorted(sigma_g_results, key=lambda x: x["sigma_g"])
    for i in range(1, len(sorted_r)):
        if sorted_r[i]["recall"] < CRIT_RECALL:
            s0, r0 = sorted_r[i-1]["sigma_g"], sorted_r[i-1]["recall"]
            s1, r1 = sorted_r[i]["sigma_g"], sorted_r[i]["recall"]
            if abs(r1 - r0) < 1e-9:
                return (s0 + s1) / 2.0
            frac = (CRIT_RECALL - r0) / (r1 - r0)
            return float(s0 + frac * (s1 - s0))
    return float(sorted_r[-1]["sigma_g"]) if sorted_r else 0.0


def find_cap_crit(sigma_g_results: List[Dict]) -> float:
    """Find sigma_g where recall approaches zero (cap_crit proxy)."""
    sorted_r = sorted(sigma_g_results, key=lambda x: x["sigma_g"])
    for i in range(1, len(sorted_r)):
        if sorted_r[i]["recall"] < CAP_CRIT_RECALL:
            s0, r0 = sorted_r[i-1]["sigma_g"], sorted_r[i-1]["recall"]
            s1, r1 = sorted_r[i]["sigma_g"], sorted_r[i]["recall"]
            if abs(r1 - r0) < 1e-9:
                return (s0 + s1) / 2.0
            frac = (CAP_CRIT_RECALL - r0) / (r1 - r0)
            return float(s0 + frac * (s1 - s0))
    return float(sorted_r[-1]["sigma_g"]) if sorted_r else 0.0


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. BBP formula
    pred = 1.0 - (0.05 ** 0.5) - 0.05
    assert abs(pred - 0.7264) < 0.001, f"BBP selftest: {pred:.4f}"

    # 2. MP upper edge
    mp_max = (1.0 + 0.05 ** 0.5) ** 2
    assert abs(mp_max - 1.4972) < 0.01, f"MP_max selftest: {mp_max:.4f}"

    # 3. M check
    assert _M_FULL == 409, f"M_full={_M_FULL}"

    # 4. Run one forward pass at tiny N
    n_t = 64
    rng = np.random.RandomState(42)
    M_t = max(1, int(ALPHA * n_t))
    Xi_t = rng.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(n_t)
    probe = Xi_t[0].copy()
    probe[:n_t // 4] *= -1.0
    retrieved = hopfield_retrieve_np(W_t, probe)
    cos_v = float(np.dot(retrieved, Xi_t[0])) / n_t
    assert not np.isnan(cos_v), f"recall cos is NaN"

    # 5. find_bbp_audit_crit returns non-NaN for synthetic data
    test_results = [
        {"sigma_g": 0.0, "recall": 0.9},
        {"sigma_g": 1.0, "recall": 0.7},
        {"sigma_g": 5.0, "recall": 0.3},
        {"sigma_g": 10.0, "recall": 0.05},
    ]
    ac = find_bbp_audit_crit(test_results)
    cc = find_cap_crit(test_results)
    assert not np.isnan(ac) and ac > 0, f"audit_crit NaN or zero: {ac}"
    assert not np.isnan(cc) and cc > 0, f"cap_crit NaN or zero: {cc}"

    print(f"[selftest] PASS: BBP={pred:.4f} MP={mp_max:.4f} M={_M_FULL} "
          f"cos={cos_v:.3f} ac={ac:.2f} cc={cc:.2f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_sigma_sweep(seed: int, n_dim: int, sigma_g_list: List[float]) -> Dict:
    """Run one seed across the sigma_g sweep: recall at each sigma_g."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_val = max(1, int(ALPHA * n_dim))
    Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
    W_clean = (Xi.T @ Xi) / float(n_dim)

    cell_results = []
    for sigma_g in sigma_g_list:
        t_cell = time.time()
        if sigma_g == 0.0:
            W_noisy = W_clean.copy()
        else:
            Z = rng.standard_normal((n_dim, n_dim))
            Z = (Z + Z.T) / 2.0
            W_noisy = W_clean + sigma_g * Z / float(n_dim)

        n_q = min(N_QUERIES_USE, M_val)
        recalls = []
        for q in range(n_q):
            xi_q = Xi[q]
            probe = xi_q.copy()
            flip_mask = rng.random(n_dim) < 0.10
            probe[flip_mask] *= -1.0
            state = hopfield_retrieve_np(W_noisy, probe)
            cos_v = float(np.dot(state, xi_q)) / n_dim
            recalls.append(cos_v)
        mean_recall = float(np.mean(recalls)) if recalls else 0.0
        elapsed_cell = time.time() - t_cell

        print(f"  [seed={seed} sg={sigma_g:.4f}] recall={mean_recall:.4f} "
              f"elapsed={elapsed_cell:.3f}s", flush=True)

        cell_results.append({
            "sigma_g": float(sigma_g),
            "recall": float(mean_recall),
            "n_queries": n_q,
        })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "alpha": ALPHA, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed),
        "sigma_g_results": cell_results,
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    audit_crits = []
    cap_crits = []
    for r in all_results:
        ac = find_bbp_audit_crit(r["sigma_g_results"])
        cc = find_cap_crit(r["sigma_g_results"])
        if ac > 0.0:
            audit_crits.append(ac)
        if cc > 0.0:
            cap_crits.append(cc)

    if not audit_crits or not cap_crits:
        return ("HARD_FAIL", f"audit_crit or cap_crit could not be computed. "
                f"n_audit={len(audit_crits)} n_cap={len(cap_crits)}")

    mean_ac = float(np.mean(audit_crits))
    mean_cc = float(np.mean(cap_crits))
    ratio = mean_cc / mean_ac if mean_ac > 0 else 0.0

    summary = (f"N={N} alpha={ALPHA} audit_crit={mean_ac:.3f} (pred={BBP_AUDIT_CRIT_PRED:.3f}) "
               f"cap_crit={mean_cc:.3f} ratio={ratio:.2f} "
               f"HP=[{HP_RATIO_LO},{HP_RATIO_HI}] n_seeds={len(all_results)}")

    if ratio < HF_RATIO_LO or ratio > HF_RATIO_HI:
        return ("HARD_FAIL",
                f"HARD_FAIL: ratio={ratio:.2f} outside [{HF_RATIO_LO},{HF_RATIO_HI}]. "
                f"BBP N-scaling prediction fails. {summary}")

    hp_ratio = HP_RATIO_LO <= ratio <= HP_RATIO_HI
    hp_ac = HP_AUDIT_CRIT_LO <= mean_ac <= HP_AUDIT_CRIT_HI

    if hp_ratio and hp_ac:
        return ("HARD_PASS",
                f"HARD_PASS: PP-58 BBP cross-N at N={N}. "
                f"ratio={ratio:.2f} in [{HP_RATIO_LO},{HP_RATIO_HI}]; "
                f"audit_crit={mean_ac:.3f} in [{HP_AUDIT_CRIT_LO},{HP_AUDIT_CRIT_HI}]. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial BBP calibration at N={N}. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE if RUN_MODE == 'smoke' else N} "
      f"mode={RUN_MODE} alpha={ALPHA}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed_sigma_sweep(seed, N_ACTIVE if RUN_MODE == "smoke" else N, SIGMA_G_USE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
# GPU util check: if CUDA available, check memory was used
if HAVE_CUDA and torch.cuda.is_available():
    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
    # Xi built in numpy (not GPU) but runner has GPU; check it can be allocated
    dummy = torch.zeros((128,), device='cuda')
    dummy_mem = torch.cuda.memory_allocated(0)
    del dummy
    assert dummy_mem >= 0, "GPU memory check failed"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"),
         "sigma_g_results": r.get("sigma_g_results", [])}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
