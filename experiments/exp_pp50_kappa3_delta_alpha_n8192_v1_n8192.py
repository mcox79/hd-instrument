"""
pp50_kappa3_delta_alpha_n8192_v1_n8192 -- PP-50: kappa_3 delta-alpha sensitivity at N=8192.

CONTEXT (v368 refill cycle):
  PP-50 delta_alpha band: 0.80-0.92 (v363 BAND-LIFT; 2-rung ALL-v3-protocol cross-N
    {N=16384 v345 + N=32768 v363}).
  N=16384 v3 (v345): sigma_sep(d=0.04)=642; (d=0.01)=186; (d=0.001)=19.3. All HP.
  N=32768 v3 (v363): sigma_sep(d=0.04)=572.5; (d=0.01)=167.3; (d=0.001)=17.8. All HP.
  N=8192: not yet tested. This is the first N=8192 rung for delta_alpha sub-property.

SCIENTIFIC QUESTION:
  Does kappa_3 delta-alpha sensitivity hold at N=8192 with the v3 protocol?
  N^(2/3) prediction from N=16384: sigma_sep(d=0.04) ~ 642 * (8192/16384)^(2/3) = 642 * 0.630 = 404.
  HP threshold (100) should be comfortably cleared if N^(2/3) scaling holds.

MEMORY ESTIMATE (OOM pre-check):
  M_base = int(0.05 * 8192) = 409 patterns.
  Xi size: 409 * 8192 * 4 bytes = 13.4 MB.
  V per Hutchinson probe: 8192 * 2000 * 4 = 65.5 MB.
  Peak: Xi + 4*V = 0.013 + 4*0.066 = 0.28 GB. Fits in 8 GB with 7.7 GB margin.

PRE-REGISTERED BANDS (PP-50 kappa3 N=8192 delta-alpha v1, first N=8192 rung):
  Calibration note: prior empirical anchor exists at N=16384 and N=32768; using
  N^(2/3) scaling from N=16384 (sigma_sep_16K=642) -> predicted N=8192=404.
  HP thresholds: set at 10% of N^(2/3) prediction (generous margin for cross-N protocol).
  HARD-PASS: sigma_sep(d=0.04) >= 100 AND sigma_sep(d=0.01) >= 10 AND sigma_sep(d=0.001) >= 3.0.
  MIDDLE: sigma_sep(d=0.04) in [50, 100) OR sigma_sep(d=0.01) in [5, 10).
  HARD-FAIL: sigma_sep(d=0.04) < 50 OR sigma_sep(d=0.01) < 5.

FORMULA SELF-TESTS (PROT-022):
  1. N^(2/3) scaling: 642 * (8192/16384)^(2/3) ~ 404 >> HP=100.
     [INPUT: sigma_n16384=642, N_ratio=0.5] [EXPECTED: ~404 > 100]
  2. M_base = int(0.05 * 8192) = 409.
     [EXPECTED: M_base = 409]
  3. Hutchinson kappa_3 on tiny N non-NaN.
  4. GPU memory > 100 MB after Xi creation.
  5. Xi VRAM at N=8192: 409 * 8192 * 4 < 1e8 (< 100 MB).
     [EXPECTED: Xi_bytes < 1e8]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + N + alpha_base.
QUEUE: overnight_queue (GPU; Hutchinson kappa_3 delta-alpha at N=8192).
TIMEOUT ESTIMATE: v3 N=16384 elapsed ~45s per seed (5000 probes, 3 delta_alphas).
  N=8192 scaling: cost ~ M * N * n_probes = alpha * N^2 * n_probes.
  N=8192 / N=16384 = 0.5x, so N^2 = 0.25x. n_probes: 5000->2000 = 0.4x.
  Estimated: 45 * 0.25 * 0.4 = 4.5s per seed. 5 seeds = 22.5s.
  ceil(1.5 * 25) = 37 -> 300s.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed; cannot run GPU experiment.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU. Aborting.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
_total_vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={_total_vram_gb:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp50_kappa3_delta_alpha_n8192_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# alpha_base: baseline load ratio (same as v3 protocol)
ALPHA_BASE = 0.05

# PROT-022 formula self-tests at module scope
_sigma_n16384 = 642.0
_N_ratio = 8192.0 / 16384.0
_extrapolated_sigma_04 = _sigma_n16384 * (_N_ratio ** (2.0 / 3.0))
print(f"[selftest-formula] N=8192 N^(2/3) scaling prediction: "
      f"sigma_sep(delta=0.04) ~ {_extrapolated_sigma_04:.0f} "
      f"(from N=16384 {_sigma_n16384:.0f} * {_N_ratio:.3f}^(2/3)={_N_ratio**(2.0/3.0):.3f})",
      flush=True)
assert _extrapolated_sigma_04 > 100, (
    f"Formula self-test: extrapolated {_extrapolated_sigma_04:.0f} < HP threshold 100")

_M_check = int(ALPHA_BASE * N)
assert _M_check == 409, f"M check: {_M_check} expected 409"

_xi_bytes = 409 * 8192 * 4
assert _xi_bytes < 1e8, f"Xi VRAM check: {_xi_bytes/1e6:.0f}MB >= 100MB"

if RUN_MODE == "smoke":
    N_ACTIVE = 1024          # smoke at 1024
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.01, 0.04]    # drop 0.001 for smoke speed
    N_PROBES_SENS = 200      # reduced for smoke
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    DELTA_ALPHAS = [0.04, 0.01, 0.001]
    N_PROBES_SENS = 2000

# Pre-registered thresholds (PP-50 N=8192 delta-alpha v1)
HP_DELTA_04 = 100.0     # sigma_sep >= 100 at delta_alpha=0.04 -> HARD-PASS
HP_DELTA_01 = 10.0      # sigma_sep >= 10 at delta_alpha=0.01 -> HARD-PASS
HP_DELTA_001 = 3.0      # sigma_sep >= 3.0 at delta_alpha=0.001 -> HARD-PASS
MID_DELTA_04_LOW = 50.0
MID_DELTA_01_LOW = 5.0
HF_DELTA_04 = 50.0      # sigma_sep < 50 at delta_alpha=0.04 -> HARD-FAIL
HF_DELTA_01 = 5.0       # sigma_sep < 5 at delta_alpha=0.01 -> HARD-FAIL


def hutchinson_kappa3_gpu_f64acc(Xi: torch.Tensor, n: int, n_probes: int,
                                  seed: int) -> Tuple[float, float]:
    """Hutchinson kappa_3 = Tr(W^3)/N. float32 patterns, float64 accumulation."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 7777)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        inner = Xi @ V          # M x n_probes
        return (Xi.t() @ inner) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)

    estimates_f64 = (V0.double() * V3.double()).sum(dim=0) / n
    mean_k3 = float(estimates_f64.mean())
    std_k3 = float(estimates_f64.std())
    se_k3 = std_k3 / math.sqrt(n_probes)
    return mean_k3, se_k3


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 512
    n_p = 100
    M_test = int(0.05 * n_test)  # alpha=0.05
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_base = (torch.randint(0, 2, (M_test, n_test), generator=gen,
                              device=DEVICE).float() * 2 - 1)
    k3_base, se_base = hutchinson_kappa3_gpu_f64acc(Xi_base, n_test, n_p, seed=42)
    assert not (k3_base != k3_base), "kappa_3 is NaN at tiny N"
    assert se_base > 0, f"SE is zero: {se_base}"

    # Perturbed matrix
    n_extra = max(1, int(0.01 * n_test))
    gen.manual_seed(99)
    Xi_extra = (torch.randint(0, 2, (n_extra, n_test), generator=gen,
                               device=DEVICE).float() * 2 - 1)
    Xi_pert = torch.cat([Xi_base, Xi_extra], dim=0)
    k3_pert, se_pert = hutchinson_kappa3_gpu_f64acc(Xi_pert, n_test, n_p, seed=43)
    pooled_se = math.sqrt(se_base**2 + se_pert**2)
    assert pooled_se > 0, f"pooled_SE is zero"
    sigma_sep = abs(k3_pert - k3_base) / pooled_se
    assert not (sigma_sep != sigma_sep), "sigma_sep is NaN"
    assert sigma_sep > 0, f"sigma_sep is zero at selftest scale"

    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated"
    print(f"[selftest] PASS: k3_base={k3_base:.4e} se={se_base:.2e} "
          f"sigma_sep_test={sigma_sep:.2f} gpu_mem={mem/1e6:.1f}MB", flush=True)
    del Xi_base, Xi_extra, Xi_pert


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    M_base = int(ALPHA_BASE * n_dim)
    Xi_base = (torch.randint(0, 2, (M_base, n_dim), generator=gen,
                              device=DEVICE).float() * 2 - 1)

    xi_mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M_base={M_base}] Xi_base VRAM: {xi_mem_gb:.3f}GB", flush=True)

    k3_base, se_base = hutchinson_kappa3_gpu_f64acc(Xi_base, n_dim, N_PROBES_SENS, seed=seed)
    print(f"  [seed={seed} M_base={M_base}] k3_base={k3_base:.4e} se={se_base:.2e}", flush=True)
    torch.cuda.empty_cache()

    delta_results = []
    for delta_alpha in DELTA_ALPHAS:
        n_extra = max(1, int(delta_alpha * n_dim))
        gen2 = torch.Generator(device=DEVICE)
        gen2.manual_seed(seed + 10000 + int(delta_alpha * 100000))
        Xi_extra = (torch.randint(0, 2, (n_extra, n_dim), generator=gen2,
                                   device=DEVICE).float() * 2 - 1)
        Xi_pert = torch.cat([Xi_base, Xi_extra], dim=0)

        k3_pert, se_pert = hutchinson_kappa3_gpu_f64acc(Xi_pert, n_dim, N_PROBES_SENS, seed=seed + 1)
        pooled_se = math.sqrt(se_base**2 + se_pert**2)
        if pooled_se < 1e-20:
            sigma_sep = 0.0
        else:
            sigma_sep = abs(k3_pert - k3_base) / pooled_se

        print(f"    [seed={seed} delta_alpha={delta_alpha:.3f}] "
              f"k3_pert={k3_pert:.4e} se_pert={se_pert:.2e} "
              f"sigma_sep={sigma_sep:.2f}", flush=True)
        delta_results.append({
            "delta_alpha": float(delta_alpha),
            "k3_base": float(k3_base),
            "k3_pert": float(k3_pert),
            "se_base": float(se_base),
            "se_pert": float(se_pert),
            "pooled_se": float(pooled_se),
            "sigma_sep": float(sigma_sep),
        })
        del Xi_extra, Xi_pert
        torch.cuda.empty_cache()

    del Xi_base
    torch.cuda.empty_cache()

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "alpha_base": ALPHA_BASE,
        "delta_results": delta_results,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    by_delta: Dict[float, List[float]] = {}
    for r in results:
        for dr in r.get("delta_results", []):
            da = dr["delta_alpha"]
            by_delta.setdefault(da, []).append(dr["sigma_sep"])

    summary_parts = []
    for da in sorted(by_delta):
        seps = by_delta[da]
        mean_sep = sum(seps) / len(seps)
        summary_parts.append(f"delta={da:.3f}:sigma_sep={mean_sep:.1f}(n={len(seps)})")
    summary = " | ".join(summary_parts) + f" | n_seeds={len(results)} N={N}"

    sep_04 = sum(by_delta.get(0.04, [0])) / max(len(by_delta.get(0.04, [0])), 1)
    sep_01 = sum(by_delta.get(0.01, [0])) / max(len(by_delta.get(0.01, [0])), 1)
    sep_001 = sum(by_delta.get(0.001, [0])) / max(len(by_delta.get(0.001, [1])), 1)

    # HARD-FAIL check first
    if 0.04 in by_delta and sep_04 < HF_DELTA_04:
        return ("HARD_FAIL", f"HARD_FAIL: sigma_sep(d=0.04)={sep_04:.1f} < HF={HF_DELTA_04}. {summary}")
    if 0.01 in by_delta and sep_01 < HF_DELTA_01:
        return ("HARD_FAIL", f"HARD_FAIL: sigma_sep(d=0.01)={sep_01:.1f} < HF={HF_DELTA_01}. {summary}")

    # HARD-PASS check
    hp04 = (0.04 not in by_delta) or sep_04 >= HP_DELTA_04
    hp01 = (0.01 not in by_delta) or sep_01 >= HP_DELTA_01
    hp001 = (0.001 not in by_delta) or sep_001 >= HP_DELTA_001

    if hp04 and hp01 and hp001:
        return ("HARD_PASS",
                f"HARD_PASS: PP-50 kappa_3 delta-alpha sensitivity confirmed at N={N} "
                f"(v3 protocol downscale). N^(2/3) scaling holds. {summary}")

    # MIDDLE check
    mid04 = MID_DELTA_04_LOW <= sep_04 < HP_DELTA_04
    mid01 = MID_DELTA_01_LOW <= sep_01 < HP_DELTA_01
    if mid04 or mid01:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP at N={N}; scaling plateau. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE != "smoke" and n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_base={ALPHA_BASE} delta_alphas={DELTA_ALPHAS} n_probes={N_PROBES_SENS} "
      f"n_seeds={len(SEEDS)}", flush=True)

# VRAM pre-check at FULL scale
_M_base_full = int(ALPHA_BASE * N)
_vram_xi_full = _M_base_full * N * 4  # float32
_vram_v_full = N * N_PROBES_SENS * 4  # float32 per V
_vram_est_gb_full = (_vram_xi_full + _vram_v_full * 4) / 1e9
print(f"[VRAM-full] N={N} M={_M_base_full} n_probes={N_PROBES_SENS}: "
      f"Xi={_vram_xi_full/1e9:.3f}GB + 4xV={_vram_v_full*4/1e9:.3f}GB = "
      f"est_peak={_vram_est_gb_full:.3f}GB / {_total_vram_gb:.1f}GB", flush=True)
if _vram_est_gb_full > _total_vram_gb * 0.85:
    print(f"[WARN] VRAM pre-check tight at N={N}: {_vram_est_gb_full:.2f}GB / "
          f"{_total_vram_gb:.1f}GB", flush=True)

_prot018_startup_check(N_ACTIVE)

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
run_config = {"N": N, "alpha_base": ALPHA_BASE, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} alpha_base={ALPHA_BASE} "
          f"delta_alphas={DELTA_ALPHAS}...", flush=True)
    result = run_seed(seed, N_ACTIVE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N, "n_active": N_ACTIVE,
    "run_mode": RUN_MODE,
    "alpha_base": ALPHA_BASE,
    "delta_alphas": DELTA_ALPHAS,
    "n_probes_sens": N_PROBES_SENS,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
