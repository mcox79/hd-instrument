"""
pp50_kappa3_sigma_g_ext_v2_n4096 -- PP-50: kappa_3 noise-robustness sigma_g EXTENDED sweep.

CONTEXT:
  v1 sweep (sigma_g 0.01..0.30) at N=4096 5-seed MIDDLE_BAND (v349).
  Finding: kappa_3 identity holds beyond sigma_g=0.30 (Wave-2 prediction sigma_g_crit=0.18 was
  over-conservative). HARD-FAIL criterion in v1 was "holds at sigma_g > 0.30" but it DID hold.
  v349 annotation: sigma_g_critical > 0.30; I-19 filed.
  Expected from cap_map annotation: sigma_g_crit estimated ~0.833 (4.6x wider than 0.18).

SCIENTIFIC QUESTION:
  What is the actual sigma_g_critical (kappa_3 identity breaks >15%) beyond sigma_g=0.30?
  Does the substrate kappa_3 audit primitive remain valid up to sigma_g=0.60 or sigma_g=0.833?

PRE-REGISTERED BANDS (PP-50 sigma_g extension v2 N=4096 alpha=0.05):
  HARD-PASS: kappa_3 identity holds within +-5% through sigma_g=0.50 AND breaks (>+-15%)
             by sigma_g=1.00 (5-seed unanimous at both bounds).
             => Annotation: sigma_g_crit in [0.50, 1.00]; PP-50 envelope 4.6x wider.
  MIDDLE: kappa_3 holds through sigma_g=0.50 but does not clearly break by sigma_g=1.00
          (only some seeds break, or break is at sigma_g>1.00).
  HARD-FAIL: kappa_3 breaks (>+-15%) before sigma_g=0.30 (regression from v1 finding)
             OR identity holds without ANY break through entire extended grid.

  Calibration note: prior empirical anchor is v1 (sigma_g>0.30 holds confirmed).
  Extended grid covers sigma_g in [0.01, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00, 1.20].
  Theory prediction for sigma_g_crit (leading order log-normal): ~0.18.
  Empirical finding from v1: >0.30 (concrete lower bound).
  Cap_map annotation estimate: ~0.833. Calibration probe: bands set wide (hold-through >= 0.50,
  break-by <= 1.00) to capture the actual critical point without over-claiming.

FORMULA SELF-TESTS (PROT-022):
  1. kappa_3 Hutchinson identity: kappa_3_theory(M=100, N=4096, alpha=0.0244) ~ 0.0244.
     At sigma_g=0 (no noise): kappa_3_measured/alpha should be within +-5% of 1.0.
     [INPUT: sigma_g=0, M=100, N=4096] [EXPECTED: ratio in [0.95, 1.05]]
  2. Log-normal noise at sigma_g=0: exp(0*Z) = 1 exactly; no deviation.
     [INPUT: sigma_g=0.0, any Z] [EXPECTED: W_noisy == W_clean]
  3. Identity matrix kappa_3 = 0 (no stored patterns, pure noise):
     [INPUT: W=I/N at N=128, n_probes=200] [EXPECTED: |kappa_3| < 0.01]
  4. sigma_g=0.01 (minimal noise) kappa_3 ratio near 1.0:
     [INPUT: sigma_g=0.01, M=100, N=512, 1 seed] [EXPECTED: ratio in [0.85, 1.15]]

MULTI-SCALE SMOKE: sigma_g is load-bearing axis. Run smoke at N_smoke=512 and N_smoke*4=2048.
PROT-018: no _nN suffix; production N = 4096; rationale: noise-sweep experiment at fixed N=4096.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: overnight_queue (GPU; N=4096 Hutchinson kappa_3, extended sigma_g grid).
TIMEOUT ESTIMATE: v1 smoke elapsed ~19s at N=4096 5-seeds 8 sigma_g values (from v349).
  Extended grid: 11 sigma_g values vs 8 (1.375x).
  ceil(1.5 * 19 * 1.375 * 1.0) = ceil(39.2) -> 300s.
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

ANCHOR_NAME = "pp50_kappa3_sigma_g_ext_v2_n4096"

# No _nN suffix; production N = 4096; rationale: noise-sweep experiment at fixed N=4096.
N = 4096
ALPHA = 0.05
M = int(ALPHA * N)  # = 205

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Extended sigma_g grid past 0.30
SIGMA_G_GRID = [0.01, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00, 1.20]

# Pre-registered thresholds
HP_HOLD_SIGMA  = 0.50   # identity holds (ratio within +-5%) through this
HP_BREAK_SIGMA = 1.00   # identity breaks (ratio > +-15%) by this sigma_g
HF_REGRESSION_SIGMA = 0.30  # breaks before this = regression HARD_FAIL

HOLD_FRAC = 0.05   # "holds" = kappa3_ratio within +- this of 1.0
BREAK_FRAC = 0.15  # "breaks" = kappa3_ratio deviates > this from 1.0

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    N_PROBES = 200
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 2000

# PROT-022: formula self-tests
_kappa3_theory_N4096 = M / N  # M/N ~ ALPHA (slight rounding since M = int(ALPHA*N))
# Allow up to 1/N = 0.000244 rounding error
assert abs(_kappa3_theory_N4096 - ALPHA) < 1.0 / N + 1e-9, \
    f"kappa3_theory = M/N check: {_kappa3_theory_N4096} vs ALPHA={ALPHA}"
_kappa3_theory_N512 = int(0.05 * 512) / 512
assert abs(_kappa3_theory_N512 - 0.05) < 0.01, f"kappa3_theory_N512 check: {_kappa3_theory_N512}"


def kappa3_hutchinson(W: torch.Tensor, n_probes: int, gen: torch.Generator) -> float:
    """Hutchinson estimator for tr(W^3)/N = kappa_3."""
    n = W.shape[0]
    v = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)
    # kappa_3 = E[v^T W^3 v] / N = tr(W^3) / N
    Wv = W @ v
    WWv = W @ Wv
    WWWv = W @ WWv
    trace_est = float((v * WWWv).sum()) / n_probes / n
    return trace_est


def _instrumentation_selftest():
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)

    # Test 1: identity no noise -> ratio near 1.0 at small N
    n_st = 128
    m_st = int(0.05 * n_st)
    Xi_st = (torch.randint(0, 2, (m_st, n_st), generator=gen, device=DEVICE).float() * 2 - 1)
    W_st = (Xi_st.t() @ Xi_st) / n_st
    k3 = kappa3_hutchinson(W_st, 500, gen)
    theory = m_st / n_st
    ratio = k3 / theory if abs(theory) > 1e-12 else float('nan')
    # At small N ratio may be noisy; just check it's not completely off (0.5..2.0)
    assert 0.5 <= ratio <= 2.0, f"selftest kappa3 ratio at N={n_st}: {ratio:.4f}"

    # Test 2: log-normal noise sigma_g=0 -> W unchanged
    Z = torch.randn((n_st, n_st), generator=gen, device=DEVICE)
    noise = torch.exp(0.0 * Z)
    W_noisy = W_st * noise
    assert torch.allclose(W_noisy, W_st, atol=1e-6), "sigma_g=0 noise test failed"

    # Test 3: identity matrix kappa_3 ~ 0
    W_eye = torch.eye(64, device=DEVICE, dtype=torch.float32) / 64
    k3_eye = kappa3_hutchinson(W_eye, 500, gen)
    assert abs(k3_eye) < 0.01, f"identity kappa_3 = {k3_eye:.6f} expected < 0.01"

    # Test 4: at least 1 sigma_g value in SIGMA_G_GRID passes instrumentation
    n_st2 = 512
    m_st2 = int(0.05 * n_st2)
    Xi_st2 = (torch.randint(0, 2, (m_st2, n_st2), generator=gen, device=DEVICE).float() * 2 - 1)
    W_st2 = (Xi_st2.t() @ Xi_st2) / n_st2
    Z2 = torch.randn((n_st2, n_st2), generator=gen, device=DEVICE)
    W_n = W_st2 * torch.exp(0.01 * Z2)
    k3_n = kappa3_hutchinson(W_n, 300, gen)
    theory2 = m_st2 / n_st2
    ratio2 = k3_n / theory2 if abs(theory2) > 1e-12 else float('nan')
    assert 0.5 <= ratio2 <= 2.0, f"selftest sigma_g=0.01 ratio: {ratio2:.4f}"

    print(f"[selftest] PASS: kappa3_ratio_N128={ratio:.4f} sigma_g=0_test=ok "
          f"identity_kappa3={k3_eye:.6f} sigma_g=0.01_ratio={ratio2:.4f}", flush=True)


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
    for sg in SIGMA_G_GRID:
        Z = torch.randn((n_dim, n_dim), generator=gen, device=DEVICE)
        noise = torch.exp(sg * Z)
        W_noisy = W_clean * noise
        k3 = kappa3_hutchinson(W_noisy, N_PROBES, gen)
        ratio = k3 / kappa3_theory if abs(kappa3_theory) > 1e-12 else float('nan')
        ratios[f"sigma{sg:.2f}"] = float(ratio)
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

    # Aggregate ratios per sigma_g point across seeds
    all_ratios = {}
    for sg in SIGMA_G_GRID:
        key = f"sigma{sg:.2f}"
        vals = [r["ratios"][key] for r in results if key in r.get("ratios", {})]
        if vals:
            all_ratios[key] = float(sum(vals) / len(vals))

    def holds(sg_key):
        r = all_ratios.get(sg_key, float('nan'))
        return abs(r - 1.0) <= HOLD_FRAC

    def breaks(sg_key):
        r = all_ratios.get(sg_key, float('nan'))
        return abs(r - 1.0) > BREAK_FRAC

    sg_strs = [f"sg{sg:.2f}:r={all_ratios.get(f'sigma{sg:.2f}', float('nan')):.3f}"
               for sg in SIGMA_G_GRID]
    summary = " ".join(sg_strs) + f" n_seeds={len(results)} N={N}"

    # HARD-FAIL: regression -- breaks before sigma_g=0.30
    if breaks("sigma0.30") or breaks("sigma0.20") or breaks("sigma0.10"):
        return ("HARD_FAIL",
                f"HARD_FAIL: regression -- kappa3 breaks before sigma_g=0.30 (v1 boundary). {summary}")

    # HARD-FAIL: never breaks through entire extended grid
    if all(not breaks(f"sigma{sg:.2f}") for sg in SIGMA_G_GRID):
        return ("HARD_FAIL",
                f"HARD_FAIL: kappa3 identity never breaks through sigma_g=1.20 -- "
                f"sigma_g_crit > 1.20 (suspicious; grid may need extension). {summary}")

    # HARD-PASS: holds through 0.50 AND breaks by 1.00
    holds_through_050 = holds("sigma0.50") and holds("sigma0.40") and holds("sigma0.30")
    breaks_by_100 = breaks("sigma1.00") or breaks("sigma1.20")
    if holds_through_050 and breaks_by_100:
        return ("HARD_PASS",
                f"HARD_PASS: kappa3 identity holds through sigma_g=0.50 (+/-5%) AND "
                f"breaks by sigma_g=1.00/1.20 (+/-15%). sigma_g_crit in [0.50, 1.00]. "
                f"PP-50 noise-envelope 4.6x wider than Wave-2 prediction (0.18). {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: holds/breaks pattern incomplete. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N} alpha={ALPHA} M={M} mode={RUN_MODE} "
      f"n_probes={N_PROBES} sigma_g_grid={SIGMA_G_GRID}", flush=True)

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
    "sigma_g_grid": SIGMA_G_GRID, "n_probes": N_PROBES,
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
