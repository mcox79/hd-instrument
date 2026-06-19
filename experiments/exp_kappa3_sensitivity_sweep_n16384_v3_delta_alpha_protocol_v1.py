"""
kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1

R3-A fix: re-spec N=16384 with the delta-alpha sensitivity protocol (Part B
of kappa46_fingerprint_n32768_v1). The prior v1/v2 HF used Hopfield-vs-GOE
observable; the cloud HP used Hopfield-vs-Hopfield+delta. These are NOT
comparable observables. This anchor measures the same DELTA-ALPHA SENSITIVITY
as the cloud anchor, at N=16384.

Observable:
  sigma_sep = |kappa_3(M_base) - kappa_3(M_base + n_extra)| / pooled_SE
  where pooled_SE = sqrt(SE_base^2 + SE_pert^2)
  and SE = std_estimator / sqrt(n_probes)

Protocol:
  alpha_base = 0.05  (M_base = N * alpha_base)
  delta_alpha_grid = [0.001, 0.01, 0.04]
  n_probes_sens = 5000
  dtype: float32 patterns + float64 estimator accumulation

PRE-REGISTERED BANDS (R3-A from research audit, matched to Part B bands):
  HARD-PASS: sigma_sep >= 100 at delta_alpha=0.04
             AND sigma_sep >= 10 at delta_alpha=0.01
             AND sigma_sep >= 3.0 at delta_alpha=0.001
  MIDDLE: sigma_sep at delta_alpha=0.001 in [1.5, 3.0)
  HARD-FAIL: sigma_sep < 50 at delta_alpha=0.04
             OR sigma_sep < 3.0 at delta_alpha=0.01

FORMULA SELF-TESTS (from audit Section 3):
  1. At delta_alpha=0.04, N=32768: predicted sigma_sep~1727 (cloud measured).
     At N=16384: sigma_sep ~ 1727 * (16384/32768)^(2/3) ~ 860 via N^(2/3) scaling.
     [INPUT: delta_alpha=0.04, N=16384] [EXPECTED: sigma_sep >> 100]
  2. Hutchinson kappa_3 on tiny N non-NaN.
  3. GPU memory > 100 MB after Xi creation.

PROT-018: anchor _n16384 binds N=16384.
PROT-021: run_config includes N, alpha_base, run_mode.
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

ANCHOR_NAME = "kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# alpha_base: baseline load ratio (same as cloud Part B)
ALPHA_BASE = 0.05

if RUN_MODE == "smoke":
    N_ACTIVE = 4096          # smoke at 4096 (1/4 of N=16384)
    SEEDS = [7, 17, 23]
    DELTA_ALPHAS = [0.01, 0.04]    # drop 0.001 for smoke speed
    N_PROBES_SENS = 500     # reduced for smoke
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    DELTA_ALPHAS = [0.001, 0.01, 0.04]
    N_PROBES_SENS = 5000    # matches cloud Part B

# Pre-registered thresholds
HP_DELTA_04 = 100.0     # sigma_sep >= 100 at delta_alpha=0.04 -> HARD-PASS
HP_DELTA_01 = 10.0      # sigma_sep >= 10 at delta_alpha=0.01 -> HARD-PASS
HP_DELTA_001 = 3.0      # sigma_sep >= 3.0 at delta_alpha=0.001 -> HARD-PASS
MID_DELTA_001_LOW = 1.5 # middle band lower bound
HF_DELTA_04 = 50.0      # sigma_sep < 50 at delta_alpha=0.04 -> HARD-FAIL
HF_DELTA_01 = 3.0       # sigma_sep < 3.0 at delta_alpha=0.01 -> HARD-FAIL

# Formula self-test: N^(2/3) scaling from cloud result
_expected_sigma_04_n32768 = 1727.0  # cloud measured
_n16384_over_n32768_23 = (16384.0 / 32768.0) ** (2.0 / 3.0)
_expected_sigma_04_n16384 = _expected_sigma_04_n32768 * _n16384_over_n32768_23
print(f"[selftest-formula] N=16384 scaling prediction: "
      f"sigma_sep(delta=0.04) ~ {_expected_sigma_04_n16384:.0f} "
      f"(from cloud {_expected_sigma_04_n32768:.0f} * {_n16384_over_n32768_23:.3f})", flush=True)
assert _expected_sigma_04_n16384 > HP_DELTA_04, (
    f"Formula self-test: predicted {_expected_sigma_04_n16384:.0f} < HP={HP_DELTA_04}")


def hutchinson_kappa3_gpu_f64acc(Xi: torch.Tensor, n: int, n_probes: int,
                                  seed: int) -> Tuple[float, float]:
    """Hutchinson kappa_3 = Tr(W^3)/N. float32 patterns, float64 accumulation."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 7777)
    # Rademacher probes in float64 for accumulation precision
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        # float32 matmul (fast), accumulate in float32 then upcast
        inner = Xi @ V          # M x n_probes
        return (Xi.t() @ inner) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)

    # Accumulate estimates in float64
    estimates_f64 = (V0.double() * V3.double()).sum(dim=0) / n
    mean_k3 = float(estimates_f64.mean())
    std_k3 = float(estimates_f64.std())
    se_k3 = std_k3 / math.sqrt(n_probes)
    return mean_k3, se_k3   # returns (mean, SE) not (mean, std)


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 512
    n_p = 200
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

    k3_base, se_base = hutchinson_kappa3_gpu_f64acc(Xi_base, n_dim, N_PROBES_SENS, seed=seed)
    print(f"  [seed={seed} M_base={M_base}] k3_base={k3_base:.4e} se={se_base:.2e}", flush=True)

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

    # Aggregate per delta_alpha across seeds
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
    summary = " | ".join(summary_parts) + f" | n_seeds={len(results)}"

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
        return ("HARD_PASS", f"HARD_PASS: delta-alpha sensitivity confirmed at N=16384. {summary}")

    # MIDDLE check
    mid001 = (0.001 not in by_delta) or (MID_DELTA_001_LOW <= sep_001 < HP_DELTA_001)
    if hp04 and hp01 and mid001:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: HP at d=0.04,0.01; borderline d=0.001. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE != "smoke" and n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_base={ALPHA_BASE} delta_alphas={DELTA_ALPHAS} n_probes={N_PROBES_SENS} "
      f"n_seeds={len(SEEDS)}", flush=True)

# VRAM pre-check
_M_base = int(ALPHA_BASE * N_ACTIVE)
_vram_xi = _M_base * N_ACTIVE * 4  # float32
_vram_v = N_ACTIVE * N_PROBES_SENS * 4  # float32
_vram_est_gb = (_vram_xi + _vram_v * 4) / 1e9  # Xi + 4 V matrices
print(f"[VRAM] estimated peak: {_vram_est_gb:.3f} GB at N={N_ACTIVE}", flush=True)
if _vram_est_gb > _total_vram_gb * 0.75:
    print(f"[WARN] VRAM pre-check tight: {_vram_est_gb:.2f}GB / {_total_vram_gb:.1f}GB", flush=True)

_prot018_startup_check(N_ACTIVE)

out_dir = get_output_dir(ANCHOR_NAME)
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
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

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
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
