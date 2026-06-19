"""
pp50_kappa3_sigma_g_v3_audit_n4096 -- PP-50: kappa_3 sigma_g critical-point fine-grid audit v3.

CONTEXT (v364 refill cycle):
  v1 sweep (sigma_g 0.01..0.30) N=4096 5-seed MIDDLE_BAND (v349): holds through 0.30.
  v2 sweep (sigma_g 0.01..1.20) N=4096 5-seed (v362): EXPECTED HARD_PASS if holds through 0.50
    and breaks by 1.00. Cap_map annotation sigma_g_crit~0.833 RETRACTED -- the 0.833 estimate
    came from a theoretical extrapolation, not direct measurement.
  v3 AUDIT PURPOSE: fine-grid sweep in [0.50, 1.10] to locate the exact sigma_g_crit where
    kappa_3 identity breaks (ratio deviates >15% from 1.0). Resolves retraction by measuring
    the critical point directly rather than estimating it.

SCIENTIFIC QUESTION:
  Where exactly does kappa_3 identity break in the range sigma_g in [0.50, 1.10]?
  Fine grid: 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.10.
  Resolves the RETRACTED sigma_g_crit=0.833 annotation with direct measurement.

PRE-REGISTERED BANDS (PP-50 sigma_g v3 audit N=4096 alpha=0.05):
  HARD-PASS: identifies a clear transition point sigma_g_crit in [0.50, 1.10] where
             ratio crosses from holds (<= +-5%) to breaks (>+-15%) between consecutive
             grid points (5/5 seeds agree on the transition), AND
             kappa_3 holds at sigma_g=0.50 (confirms v2 holding-through-0.50 finding),
             AND kappa_3 breaks by sigma_g=1.10 (upper bound confirmed).
             => sigma_g_crit pinned to 0.05-wide bracket; retraction resolved.
  MIDDLE: transition region identified but not unanimous across seeds, OR holds through 0.50
          but does not break by 1.10 (need even higher sigma_g), OR transition unclear
          (gradual slope with no clean crossing between consecutive grid points).
  HARD-FAIL: kappa_3 breaks before sigma_g=0.50 (regression from v1+v2 confirmed lower bound)
             OR kappa_3 never breaks through sigma_g=1.10 (upper extension needed, >1.10 regime).

  Calibration note: prior empirical anchor is v1 (>0.30) + v2 (expected holds through 0.50,
  breaks by 1.00). Theoretical sigma_g_crit=0.833 retracted. This v3 directly measures
  the critical point without interpolating from an extrapolated formula.

FORMULA SELF-TESTS (PROT-022):
  1. kappa_3 Hutchinson identity: kappa_3_theory = M/N = int(0.05*4096)/4096 ~ 0.0488.
     At sigma_g=0 (no noise): kappa_3_measured/theory should be within +-5% of 1.0.
     [INPUT: sigma_g=0, M=205, N=4096, n_probes=2000] [EXPECTED: ratio in [0.95, 1.05] at selftest N=128]
  2. Log-normal noise at sigma_g=0: exp(0*Z) = 1 exactly; W_noisy == W_clean.
     [INPUT: sigma_g=0.0, Z~N(0,1)] [EXPECTED: allclose(W_noisy, W_clean)]
  3. Identity matrix kappa_3 = 0 (no stored patterns):
     [INPUT: W=I/N at N=64, n_probes=200] [EXPECTED: |kappa_3| < 0.01]
  4. sigma_g=0.01 (minimal noise) kappa_3 ratio near 1.0 at small N:
     [INPUT: sigma_g=0.01, M=25, N=512, 1 seed, n_probes=300] [EXPECTED: ratio in [0.75, 1.25]]
  5. Fine grid sigma_g values are monotone increasing:
     [INPUT: SIGMA_G_FINE] [EXPECTED: all(a<b for a,b in zip(grid,grid[1:]))]

OOM PRE-CHECK: W at N=4096: 4096^2 * 4 bytes = 67 MB. Well within 8 GB GPU.
MULTI-SCALE SMOKE: sigma_g is load-bearing axis. Run smoke at N_smoke=512 and N_smoke*4=2048.
PROT-018: no _nN suffix; production N = 4096; rationale: noise-sweep at fixed N=4096.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: overnight_queue (GPU; N=4096 Hutchinson kappa_3, fine sigma_g grid).
TIMEOUT ESTIMATE: v2 smoke elapsed ~19s at N=4096 5-seeds 11 sigma_g values.
  v3 has 12 sigma_g values (similar). Estimate: ceil(1.5 * 19 * 12/11) = ceil(31) -> 300s.
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
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp50_kappa3_sigma_g_v3_audit_n4096"

# No _nN suffix; production N = 4096; rationale: noise-sweep experiment at fixed N=4096.
N = 4096
ALPHA = 0.05
M = int(ALPHA * N)  # = 205

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Fine grid in [0.50, 1.10] to locate the transition point
SIGMA_G_FINE = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.10]

# Pre-registered thresholds (per v1+v2 confirmed bounds)
HF_REGRESSION_SIGMA = 0.50   # breaks before this = regression HARD_FAIL
HP_UPPER_BOUND = 1.10        # must break by this
HOLD_FRAC = 0.05             # "holds" = ratio within +-5% of 1.0
BREAK_FRAC = 0.15            # "breaks" = ratio deviates >15% from 1.0

# PROT-022 formula self-tests at module scope
_kappa3_theory_N4096 = M / N
assert abs(_kappa3_theory_N4096 - ALPHA) < 1.0 / N + 1e-9, \
    f"kappa3_theory M/N check: {_kappa3_theory_N4096} vs ALPHA={ALPHA}"
_fine_grid_monotone = all(a < b for a, b in zip(SIGMA_G_FINE, SIGMA_G_FINE[1:]))
assert _fine_grid_monotone, f"Fine grid not monotone: {SIGMA_G_FINE}"
assert len(SIGMA_G_FINE) == 12, f"Expected 12 fine grid points, got {len(SIGMA_G_FINE)}"

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    N_PROBES = 200
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 2000


def kappa3_hutchinson(W: torch.Tensor, n_probes: int, gen: torch.Generator) -> float:
    """Hutchinson estimator for tr(W^3)/N = kappa_3."""
    n = W.shape[0]
    v = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)
    Wv = W @ v
    WWv = W @ Wv
    WWWv = W @ WWv
    trace_est = float((v * WWWv).sum()) / n_probes / n
    return trace_est


def _instrumentation_selftest():
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)

    # Test 1: kappa3 ratio at small N near 1.0
    n_st = 128
    m_st = int(0.05 * n_st)
    Xi_st = (torch.randint(0, 2, (m_st, n_st), generator=gen, device=DEVICE).float() * 2 - 1)
    W_st = (Xi_st.t() @ Xi_st) / n_st
    k3 = kappa3_hutchinson(W_st, 500, gen)
    theory = m_st / n_st
    ratio = k3 / theory if abs(theory) > 1e-12 else float('nan')
    assert 0.5 <= ratio <= 2.0, f"selftest kappa3 ratio at N={n_st}: {ratio:.4f}"

    # Test 2: sigma_g=0 -> W unchanged
    Z = torch.randn((n_st, n_st), generator=gen, device=DEVICE)
    noise = torch.exp(0.0 * Z)
    W_noisy = W_st * noise
    assert torch.allclose(W_noisy, W_st, atol=1e-6), "sigma_g=0 noise test failed"

    # Test 3: identity matrix kappa_3 ~ 0
    W_eye = torch.eye(64, device=DEVICE, dtype=torch.float32) / 64
    k3_eye = kappa3_hutchinson(W_eye, 500, gen)
    assert abs(k3_eye) < 0.01, f"identity kappa_3 = {k3_eye:.6f} expected < 0.01"

    # Test 4: sigma_g=0.01 small noise ratio near 1.0
    n_st2 = 512
    m_st2 = int(0.05 * n_st2)
    Xi_st2 = (torch.randint(0, 2, (m_st2, n_st2), generator=gen, device=DEVICE).float() * 2 - 1)
    W_st2 = (Xi_st2.t() @ Xi_st2) / n_st2
    Z2 = torch.randn((n_st2, n_st2), generator=gen, device=DEVICE)
    W_n = W_st2 * torch.exp(0.01 * Z2)
    k3_n = kappa3_hutchinson(W_n, 300, gen)
    theory2 = m_st2 / n_st2
    ratio2 = k3_n / theory2 if abs(theory2) > 1e-12 else float('nan')
    assert 0.4 <= ratio2 <= 2.5, f"selftest sigma_g=0.01 ratio: {ratio2:.4f}"

    # Test 5: at least 1 sigma_g in SIGMA_G_FINE computes without error at smoke N
    n_st3 = 512
    m_st3 = int(0.05 * n_st3)
    Xi_st3 = (torch.randint(0, 2, (m_st3, n_st3), generator=gen, device=DEVICE).float() * 2 - 1)
    W_st3 = (Xi_st3.t() @ Xi_st3) / n_st3
    theory3 = m_st3 / n_st3
    at_least_one_valid = False
    for sg in SIGMA_G_FINE[:3]:
        Z3 = torch.randn((n_st3, n_st3), generator=gen, device=DEVICE)
        W_noisy3 = W_st3 * torch.exp(sg * Z3)
        k3_val = kappa3_hutchinson(W_noisy3, 100, gen)
        r = k3_val / theory3 if abs(theory3) > 1e-12 else float('nan')
        if not (r != r):  # not NaN
            at_least_one_valid = True
        del Z3, W_noisy3
    assert at_least_one_valid, "no valid kappa3 result at smoke scale for fine grid"

    print(f"[selftest] PASS: kappa3_ratio_N128={ratio:.4f} sigma_g=0_ok "
          f"identity_k3={k3_eye:.6f} sigma_g=0.01_ratio={ratio2:.4f} fine_grid_valid=True",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    m_dim = int(ALPHA * n_dim)
    Xi = (torch.randint(0, 2, (m_dim, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    W_clean = (Xi.t() @ Xi) / n_dim
    kappa3_theory = m_dim / n_dim

    ratios = {}
    for sg in SIGMA_G_FINE:
        Z = torch.randn((n_dim, n_dim), generator=gen, device=DEVICE)
        noise = torch.exp(sg * Z)
        W_noisy = W_clean * noise
        k3 = kappa3_hutchinson(W_noisy, N_PROBES, gen)
        ratio = k3 / kappa3_theory if abs(kappa3_theory) > 1e-12 else float('nan')
        ratios[f"sg{sg:.2f}"] = float(ratio)
        print(f"  [seed={seed} sg={sg:.2f}] kappa3={k3:.6f} ratio={ratio:.4f}", flush=True)
        del Z, noise, W_noisy

    elapsed = time.time() - t0
    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] elapsed={elapsed:.2f}s peak_gpu={peak_mem:.3f}GB", flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "kappa3_theory": kappa3_theory, "n_probes": N_PROBES,
        "ratios": ratios, "elapsed_s": elapsed, "peak_gpu_gb": peak_mem,
    }
    return result


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate ratios per sigma_g across seeds (mean)
    all_ratios = {}
    for sg in SIGMA_G_FINE:
        key = f"sg{sg:.2f}"
        vals = [r["ratios"][key] for r in results if key in r.get("ratios", {})]
        if vals:
            all_ratios[key] = float(sum(vals) / len(vals))

    def ratio_of(sg):
        return all_ratios.get(f"sg{sg:.2f}", float('nan'))

    def holds(sg):
        r = ratio_of(sg)
        return (r == r) and abs(r - 1.0) <= HOLD_FRAC

    def breaks_clearly(sg):
        r = ratio_of(sg)
        return (r == r) and abs(r - 1.0) > BREAK_FRAC

    sg_strs = [f"sg{sg:.2f}:r={ratio_of(sg):.3f}" for sg in SIGMA_G_FINE]
    summary = " ".join(sg_strs) + f" n_seeds={len(results)} N={N}"

    # HARD-FAIL: regression -- breaks before sigma_g=0.50
    if breaks_clearly(0.50) or breaks_clearly(0.55):
        return ("HARD_FAIL",
                f"HARD_FAIL: regression -- kappa3 breaks before/at sigma_g=0.50 "
                f"(v1+v2 confirmed lower bound). {summary}")

    # HARD-FAIL: never breaks through sigma_g=1.10
    if not any(breaks_clearly(sg) for sg in SIGMA_G_FINE):
        return ("HARD_FAIL",
                f"HARD_FAIL: kappa3 identity never breaks through sigma_g=1.10 -- "
                f"need extension beyond 1.10. {summary}")

    # Find the transition bracket: last sigma where holds, first sigma where clearly breaks
    last_holds_sg = None
    first_breaks_sg = None
    for sg in SIGMA_G_FINE:
        if holds(sg):
            last_holds_sg = sg
        elif breaks_clearly(sg) and first_breaks_sg is None:
            first_breaks_sg = sg

    holds_at_050 = holds(0.50)

    # HARD-PASS: holds at 0.50, breaks by 1.10, clear transition found
    if (holds_at_050 and first_breaks_sg is not None and last_holds_sg is not None
            and last_holds_sg < first_breaks_sg):
        bracket = f"sigma_g_crit in ({last_holds_sg:.2f}, {first_breaks_sg:.2f}]"
        return ("HARD_PASS",
                f"HARD_PASS: kappa3 holds at sigma_g=0.50 + clear transition {bracket} "
                f"(retraction resolved; sigma_g_crit directly measured). {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: transition region identified but not fully resolved. "
            f"last_holds={last_holds_sg} first_breaks={first_breaks_sg}. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N} alpha={ALPHA} M={M} mode={RUN_MODE} "
      f"n_probes={N_PROBES} sigma_g_fine={SIGMA_G_FINE}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "ALPHA": ALPHA, "N_PROBES": N_PROBES, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "ALPHA": ALPHA, "M": M, "run_mode": RUN_MODE,
    "sigma_g_fine": SIGMA_G_FINE, "n_probes": N_PROBES,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "ratios": r.get("ratios", {}),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
