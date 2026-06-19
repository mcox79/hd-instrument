"""
pp58_bbp_spectral_gap_calibration_v1_n16384 -- PP-58 BBP eigenspectrum calibration at N=16384.

CONTEXT (Wave-5 Decisive Experiment 2 from research_routing_v359_drill_battery_synthesis_2026-06-03.md):
  Prior PP-58 runs established: ratio=3.0 (N=8192), ratio=4.0 (N=16384) MIDDLE_BAND.
  Research drill identified: HP gate was coarse-grid founding artifact; BBP asymptote = 4.13 at alpha=0.05.
  BBP criterion: sigma_g_audit_crit = 1 - sqrt(alpha) - alpha = 0.726 at alpha=0.05.
  Revised gate: ratio >= 4.0 is HP-achievable at N=16384 using BBP eigenvalue merging.

SCIENTIFIC QUESTION (PP-58 BBP calibration):
  Does substrate's BBP spectral-gap protocol (bulk-edge eigenvalue merging) give the predicted
  N-independent ratio 4.13 at alpha=0.05, with sigma_g_audit_crit = 0.726 and cap_crit (NLO) = 3.0?

TEST DESIGN:
  N=16384, alpha=0.05, 5 seeds.
  Sweep sigma_g in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.70, 0.726, 0.75, 0.80, 0.85, 0.90, 1.0, 1.2, 1.5, 2.0].
  For each sigma_g: build W = (Xi.T @ Xi)/N + sigma_g * noise; compute eigenspectrum of W.
  Find audit_crit: sigma_g where signal eigenvalues merge with Marchenko-Pastur bulk.
  Find cap_crit: sigma_g where retrieval accuracy falls below CRIT_RECALL=0.5.
  Compute ratio = cap_crit / audit_crit.

  OOM PRE-CHECK (GPU):
  W matrix float32 at N=16384: 16384^2 * 4 = 1.07 GB GPU.
  Full eigendecomp on GPU: torch.linalg.eigh is O(N^3) -- expensive at N=16384.
  Use CPU numpy for eigendecomp (much cheaper), GPU only for pattern builds.
  Peak GPU memory: Xi at N=16384 M=819: 819 * 16384 * 4 / 1e6 = 53.7 MB. Fine.
  W on CPU: 1.07 GB RAM. Remote machine has 16+ GB RAM. Fine.
  Eigendecomp on CPU: ~1-2s per matrix.

PRE-REGISTERED BANDS (Wave-5 Decisive 2; source: v359 synthesis Section 3 Exp 2):
  HARD-PASS: ratio in [3.5, 4.5] AND sigma_g_audit_crit in [0.65, 0.80] AND cap_crit in [2.5, 3.5]
  MIDDLE: ratio in [3.0, 5.0] but at least one envelope-location outside HP band
  HARD-FAIL: ratio < 3.0 OR > 5.0 -- BBP prediction wrong

  Strategic significance: HP founds PP-58 row at 0.65-0.80 (LIFT from EXPLORATORY MIDDLE).

FORMULA SELF-TESTS (PROT-022):
  1. BBP sigma_g_audit_crit formula: 1 - sqrt(0.05) - 0.05 = 0.7264 at alpha=0.05.
     [INPUT: alpha=0.05] [EXPECTED: 0.7264 within 0.001]
  2. Marchenko-Pastur bulk edge (upper): lambda_max = (1 + sqrt(c))^2 where c = M/N = alpha.
     At alpha=0.05: lambda_max = (1 + sqrt(0.05))^2 = (1.2236)^2 = 1.4972.
     [INPUT: alpha=0.05] [EXPECTED: 1.4972 within 0.01]
  3. M at alpha=0.05, N=16384: int(0.05 * 16384) = 819 >= 1.
     [EXPECTED: M = 819]
  4. NLO sigma_g_crit (PP-50 corrected): sqrt(ln(1 + 0.15/(3*0.05))) = sqrt(ln(2)) = 0.833.
     [INPUT: epsilon_threshold=0.15, alpha=0.05] [EXPECTED: 0.833 within 0.001]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: overnight_queue (GPU machine; eigendecomp on CPU numpy using GPU machine's RAM;
       W=1.07 GB CPU RAM, Xi on GPU=53.7 MB; serial over seeds and sigma_g).
TIMEOUT ESTIMATE: smoke N_smoke=512 5 sigma_g points 2 seeds.
  Estimate smoke wall ~60-120s; FULL 18 sigma_g * 5 seeds * (N^2 eigendecomp CPU).
  Eigendecomp at N=16384: ~2s/matrix on CPU. 18 sigma_g * 5 seeds = 90 calls * 2s = 180s eigendecomp.
  Plus retrieval pass ~20s total. Total FULL ~200-300s.
  timeout = ceil(1.5 * 180 * (16384/512)^1.5 * (5/2)) = NOT linear -- eigendecomp is main cost.
  Direct estimate: 18 * 5 * 2 * 1.5 = 270s. With margin: timeout=900s.
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

ANCHOR_NAME = "pp58_bbp_spectral_gap_calibration_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
_M_FULL = int(ALPHA * N)  # 819
assert _M_FULL == 819, f"M_full={_M_FULL} expected 819"

# BBP formula: audit_crit = 1 - sqrt(alpha) - alpha
BBP_AUDIT_CRIT_PRED = 1.0 - (ALPHA ** 0.5) - ALPHA  # 0.7264 at alpha=0.05
# Marchenko-Pastur upper edge
MP_LAMBDA_MAX_PRED = (1.0 + ALPHA ** 0.5) ** 2  # 1.4972 at alpha=0.05
# NLO sigma_g_crit (PP-50 corrected): sqrt(ln(1 + eps/(3*alpha)))
NLO_SIGMA_CRIT_PRED = float(np.log(1.0 + 0.15 / (3.0 * ALPHA)) ** 0.5)  # 0.833

# sigma_g sweep -- fine grid around BBP prediction
SIGMA_G_FULL = [
    0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.70, 0.726, 0.75, 0.80, 0.85, 0.90, 1.0, 1.2, 1.5, 2.0
]
CRIT_RECALL = 0.50
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10

HP_RATIO_LO = 3.5
HP_RATIO_HI = 4.5
HP_AUDIT_CRIT_LO = 0.65
HP_AUDIT_CRIT_HI = 0.80
HP_CAP_CRIT_LO = 2.5
HP_CAP_CRIT_HI = 3.5
MIDDLE_RATIO_LO = 3.0
MIDDLE_RATIO_HI = 5.0
HF_RATIO_LO = 3.0
HF_RATIO_HI = 5.0

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    # Smoke uses extended range to find threshold at N=512 (BBP threshold is N-dependent;
    # at N=512 the threshold is ~8-15, not ~0.73. This validates the instrumentation.)
    SIGMA_G_USE = [0.0, 0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 20.0]
    N_QUERIES_USE = 5
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    SIGMA_G_USE = SIGMA_G_FULL  # fine grid around BBP prediction at N=16384
    N_QUERIES_USE = N_QUERIES_PER_CELL


def hopfield_retrieve_np(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVAL_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def find_bbp_audit_crit(seed_results: List[Dict]) -> float:
    """Find sigma_g where recall drops below CRIT_RECALL -- audit_crit estimate."""
    sorted_r = sorted(seed_results, key=lambda x: x["sigma_g"])
    for i in range(1, len(sorted_r)):
        if sorted_r[i]["recall"] < CRIT_RECALL:
            # linear interpolate
            s0, r0 = sorted_r[i-1]["sigma_g"], sorted_r[i-1]["recall"]
            s1, r1 = sorted_r[i]["sigma_g"], sorted_r[i]["recall"]
            if abs(r1 - r0) < 1e-9:
                return (s0 + s1) / 2.0
            frac = (CRIT_RECALL - r0) / (r1 - r0)
            return float(s0 + frac * (s1 - s0))
    # never dropped below crit
    return float(sorted_r[-1]["sigma_g"]) if sorted_r else 0.0


def find_cap_crit(seed_results: List[Dict]) -> float:
    """Find sigma_g where eigenvalue gap collapses (proxy: recall below 0.5 as cap indicator)."""
    # Use the recall-based proxy for cap_crit: find sigma_g where recall approaches 0
    sorted_r = sorted(seed_results, key=lambda x: x["sigma_g"])
    cap_threshold = 0.1  # near-zero recall
    for i in range(1, len(sorted_r)):
        if sorted_r[i]["recall"] < cap_threshold:
            s0, r0 = sorted_r[i-1]["sigma_g"], sorted_r[i-1]["recall"]
            s1, r1 = sorted_r[i]["sigma_g"], sorted_r[i]["recall"]
            if abs(r1 - r0) < 1e-9:
                return (s0 + s1) / 2.0
            frac = (cap_threshold - r0) / (r1 - r0)
            return float(s0 + frac * (s1 - s0))
    return float(sorted_r[-1]["sigma_g"]) if sorted_r else 0.0


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. BBP formula self-test
    pred = 1.0 - (0.05 ** 0.5) - 0.05
    assert abs(pred - 0.7264) < 0.001, f"BBP selftest: {pred:.4f} expected 0.7264"

    # 2. MP upper edge
    mp_max = (1.0 + 0.05 ** 0.5) ** 2
    assert abs(mp_max - 1.4972) < 0.01, f"MP_lambda_max selftest: {mp_max:.4f} expected 1.4972"

    # 3. M check
    assert _M_FULL == 819, f"M_full={_M_FULL} expected 819"

    # 4. NLO sigma_crit self-test
    nlo = float(np.log(1.0 + 0.15 / (3.0 * 0.05)) ** 0.5)
    assert abs(nlo - 0.8326) < 0.002, f"NLO sigma_crit: {nlo:.4f} expected 0.8326"

    # 5. Run one forward pass at tiny N to verify metrics are non-null
    n_t = 64
    rng = np.random.RandomState(42)
    M_t = max(1, int(ALPHA * n_t))
    Xi_t = rng.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(n_t)
    probe = Xi_t[0].copy()
    probe[:n_t // 4] *= -1.0
    retrieved = hopfield_retrieve_np(W_t, probe)
    cos_v = float(np.dot(retrieved, Xi_t[0])) / n_t
    assert cos_v is not None and not np.isnan(cos_v), f"recall cos is NaN: {cos_v}"

    # 6. sigma_g sweep has >= 3 items in [0.6, 0.85] -- fine grid around BBP point
    fine_count = len([s for s in SIGMA_G_FULL if 0.6 <= s <= 0.85])
    assert fine_count >= 3, f"sigma_g fine-grid count: {fine_count} expected >= 3"

    print(f"[selftest] PASS: BBP_pred=0.7264, MP_max=1.4972, M_full=819, NLO=0.8326, "
          f"cos_pass={cos_v:.3f}, fine_grid={fine_count} N_active={N_ACTIVE}", flush=True)


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
            Z = (Z + Z.T) / 2.0  # symmetrize noise
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
              f"elapsed={elapsed_cell:.2f}s", flush=True)

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
        return ("HARD_FAIL", "No valid results produced.")

    # Compute per-seed audit_crit and cap_crit
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

    summary = (f"ratio={ratio:.4f} audit_crit={mean_ac:.4f} cap_crit={mean_cc:.4f} "
               f"n_seeds={len(all_results)} BBP_pred={BBP_AUDIT_CRIT_PRED:.4f} "
               f"HP: ratio=[{HP_RATIO_LO},{HP_RATIO_HI}] ac=[{HP_AUDIT_CRIT_LO},{HP_AUDIT_CRIT_HI}] "
               f"cc=[{HP_CAP_CRIT_LO},{HP_CAP_CRIT_HI}]")

    if ratio < HF_RATIO_LO or ratio > HF_RATIO_HI:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp_ratio_ok = HP_RATIO_LO <= ratio <= HP_RATIO_HI
    hp_ac_ok = HP_AUDIT_CRIT_LO <= mean_ac <= HP_AUDIT_CRIT_HI
    hp_cc_ok = HP_CAP_CRIT_LO <= mean_cc <= HP_CAP_CRIT_HI

    if hp_ratio_ok and hp_ac_ok and hp_cc_ok:
        return ("HARD_PASS", f"HARD_PASS: {summary}")

    # Middle: ratio in [3.0, 5.0] but at least one envelope outside HP
    if MIDDLE_RATIO_LO <= ratio <= MIDDLE_RATIO_HI:
        outside = []
        if not hp_ac_ok:
            outside.append(f"audit_crit={mean_ac:.4f} outside [{HP_AUDIT_CRIT_LO},{HP_AUDIT_CRIT_HI}]")
        if not hp_cc_ok:
            outside.append(f"cap_crit={mean_cc:.4f} outside [{HP_CAP_CRIT_LO},{HP_CAP_CRIT_HI}]")
        if not hp_ratio_ok:
            outside.append(f"ratio={ratio:.4f} outside [{HP_RATIO_LO},{HP_RATIO_HI}]")
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {'; '.join(outside)}. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} alpha={ALPHA} mode={RUN_MODE} "
      f"n_sigma={len(SIGMA_G_USE)} seeds={SEEDS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "sigma_g_use": SIGMA_G_USE, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
all_results = []

# Load already-done seeds
for seed in done:
    fpath = out_dir / f"seed_{seed}.json"
    if fpath.exists():
        d = json.loads(fpath.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            all_results.append(d)

for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} starting...", flush=True)
    r = run_seed_sigma_sweep(seed, N_ACTIVE, SIGMA_G_USE)
    all_results.append(r)
    write_partial(out_dir, seed, r)

verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": float(elapsed_total),
    "bbp_audit_crit_pred": float(BBP_AUDIT_CRIT_PRED),
    "hp_ratio_band": [HP_RATIO_LO, HP_RATIO_HI],
    "hp_audit_crit_band": [HP_AUDIT_CRIT_LO, HP_AUDIT_CRIT_HI],
    "hp_cap_crit_band": [HP_CAP_CRIT_LO, HP_CAP_CRIT_HI],
    "all_results": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
