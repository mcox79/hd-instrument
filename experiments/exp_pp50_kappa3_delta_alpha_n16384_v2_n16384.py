"""
pp50_kappa3_delta_alpha_n16384_v2_n16384 -- PP-50: kappa_3 delta-alpha sensitivity at N=16384 (v2).

CONTEXT (v370 refill cycle):
  v1 FAILED: exit_code=3221226505 (Windows CUDA access violation, 0xC0000005).
  Root cause: stochastic CUDA driver crash during first GPU tensor allocation in _instrumentation_selftest().
  Pattern: same crash seen in 5+ other experiments (wave14yt, pp49_hrc_depth_10, q_a3_l28, etc.).
  Fix (v2): torch.cuda.empty_cache() + torch.cuda.synchronize() before first GPU alloc in selftest.
  Logic: identical to v1. Only selftest init ordering changed.
  PP-50 delta_alpha band: 0.83-0.94 (v370 BAND-LIFT).
  Cross-N: N=16384 v3 (v345): sigma_sep(d=0.04)=642; (d=0.01)=186; (d=0.001)=19.3. All HP.
  Cross-N: N=32768 v3 (v363): sigma_sep(d=0.04)=572.5; (d=0.01)=167.3; (d=0.001)=17.8. All HP.
  Cross-N: N=8192 v1 (v368): sigma_sep(d=0.04)~290 HP.

SCIENTIFIC QUESTION:
  Does kappa_3 delta-alpha sensitivity at N=16384 reproduce the v345 results (sigma_sep(d=0.04)=642)
  under the current v1 delta-alpha protocol? Cross-N validation of the upgraded sigma_g envelope.

MEMORY ESTIMATE (OOM pre-check):
  M_base = int(0.05 * 16384) = 819 patterns.
  Xi size: 819 * 16384 * 4 bytes = 53.7 MB. Fine.
  V per Hutchinson probe: 16384 * 2000 * 4 = 131 MB.
  Peak: Xi + 4*V = 0.054 + 4*0.131 = 0.578 GB. Fits in 8.6 GB with 8.0 GB margin.

PRE-REGISTERED BANDS (PP-50 kappa3 N=16384 delta-alpha v2, cross-N gap closure):
  Prior empirical anchor: N=16384 v3 (v345) sigma_sep(d=0.04)=642.
  HARD-PASS: sigma_sep(d=0.04) >= 300 AND sigma_sep(d=0.01) >= 80 AND sigma_sep(d=0.001) >= 8.0.
  MIDDLE: sigma_sep(d=0.04) in [150, 300) OR sigma_sep(d=0.01) in [40, 80).
  HARD-FAIL: sigma_sep(d=0.04) < 150 OR sigma_sep(d=0.01) < 40.

FORMULA SELF-TESTS (PROT-022):
  1. NLO sigma_g_crit: sqrt(ln(1 + 0.15/(3*0.05))) = sqrt(ln(2)) = 0.833.
     [INPUT: epsilon=0.15, alpha=0.05] [EXPECTED: 0.833 within 0.001]
  2. N^(2/3) scaling from N=8192 to N=16384: ratio = (16384/8192)^(2/3) = 1.587.
     [EXPECTED: 1.587 within 0.01]
  3. M_base = int(0.05 * 16384) = 819. [EXPECTED: 819]
  4. Hutchinson kappa_3 on tiny N non-NaN.
  5. GPU memory > 100 MB after Xi creation.
  6. Xi VRAM at N=16384: 819 * 16384 * 4 < 2e8 (< 200 MB). [EXPECTED: True]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + N + alpha_base.
QUEUE: overnight_queue (GPU; Hutchinson kappa_3 delta-alpha at N=16384).
TIMEOUT ESTIMATE: v1 N=8192 ~22.5s (5 seeds). N=16384 scaling: N^2 ~ 4x.
  Estimated wall: 22.5 * 4 = 90s. ceil(1.5 * 90) = 135s -> 300s floor.
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

ANCHOR_NAME = "pp50_kappa3_delta_alpha_n16384_v2_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_BASE = 0.05

# PROT-022 formula self-tests at module scope (arithmetic only, no GPU)
import math as _math
_sigma_g_crit_nlo = _math.sqrt(_math.log(1.0 + 0.15 / (3.0 * ALPHA_BASE)))
print(f"[selftest-formula] NLO sigma_g_crit = sqrt(ln(2)) = {_sigma_g_crit_nlo:.4f} "
      f"(expected 0.833)", flush=True)
assert abs(_sigma_g_crit_nlo - 0.8326) < 0.001, (
    f"NLO sigma_g_crit selftest: got {_sigma_g_crit_nlo:.4f} expected 0.833")

_n_scale_ratio = (16384.0 / 8192.0) ** (2.0 / 3.0)
print(f"[selftest-formula] N^(2/3) scale ratio 16384/8192: {_n_scale_ratio:.4f} "
      f"(expected ~1.587)", flush=True)
assert abs(_n_scale_ratio - 1.587) < 0.01, (
    f"N^(2/3) ratio selftest: got {_n_scale_ratio:.4f} expected 1.587")

_M_check = int(ALPHA_BASE * N)
assert _M_check == 819, f"M check: {_M_check} expected 819"

_xi_bytes = 819 * 16384 * 4
assert _xi_bytes < 2e8, f"Xi VRAM check: {_xi_bytes/1e6:.0f}MB >= 200MB"

if RUN_MODE == "smoke":
    N_ACTIVE = 1024
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.01, 0.04]
    N_PROBES_SENS = 200
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    DELTA_ALPHAS = [0.04, 0.01, 0.001]
    N_PROBES_SENS = 2000

# Pre-registered thresholds (PP-50 N=16384 delta-alpha v2)
HP_DELTA_04 = 300.0
HP_DELTA_01 = 80.0
HP_DELTA_001 = 8.0
MID_DELTA_04_LOW = 150.0
MID_DELTA_01_LOW = 40.0
HF_DELTA_04 = 150.0
HF_DELTA_01 = 40.0


def hutchinson_kappa3_gpu_f64acc(Xi: torch.Tensor, n: int, n_probes: int,
                                  seed: int) -> Tuple[float, float]:
    """Hutchinson kappa_3 = Tr(W^3)/N. float32 patterns, float64 accumulation."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 7777)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        inner = Xi @ V
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
    """Assert all claimed metrics are non-null/non-sentinel at small scale.
    v2 fix: empty_cache + synchronize before first GPU alloc to avoid Windows CUDA
    access violation (exit_code 3221226505 / 0xC0000005) seen in v1.
    """
    # v2: settle CUDA context before first allocation
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    n_test = 512
    n_p = 100
    M_test = int(0.05 * n_test)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_base = (torch.randint(0, 2, (M_test, n_test), generator=gen,
                              device=DEVICE).float() * 2 - 1)
    k3_base, se_base = hutchinson_kappa3_gpu_f64acc(Xi_base, n_test, n_p, seed=42)
    assert not (k3_base != k3_base), "kappa_3 is NaN at tiny N"
    assert se_base > 0, f"SE is zero: {se_base}"

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
    torch.cuda.empty_cache()


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

    if 0.04 in by_delta and sep_04 < HF_DELTA_04:
        return ("HARD_FAIL", f"HARD_FAIL: sigma_sep(d=0.04)={sep_04:.1f} < HF={HF_DELTA_04}. {summary}")
    if 0.01 in by_delta and sep_01 < HF_DELTA_01:
        return ("HARD_FAIL", f"HARD_FAIL: sigma_sep(d=0.01)={sep_01:.1f} < HF={HF_DELTA_01}. {summary}")

    hp04 = (0.04 not in by_delta) or sep_04 >= HP_DELTA_04
    hp01 = (0.01 not in by_delta) or sep_01 >= HP_DELTA_01
    hp001 = (0.001 not in by_delta) or sep_001 >= HP_DELTA_001

    if hp04 and hp01 and hp001:
        return ("HARD_PASS",
                f"HARD_PASS: PP-50 kappa_3 delta-alpha sensitivity at N={N}. "
                f"NLO sigma_g_crit=0.833 envelope confirmed. {summary}")

    mid04 = MID_DELTA_04_LOW <= sep_04 < HP_DELTA_04
    mid01 = MID_DELTA_01_LOW <= sep_01 < HP_DELTA_01
    if mid04 or mid01:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP at N={N}. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE != "smoke" and n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_base={ALPHA_BASE} delta_alphas={DELTA_ALPHAS} n_probes={N_PROBES_SENS} "
      f"n_seeds={len(SEEDS)}", flush=True)

_M_base_full = int(ALPHA_BASE * N)
_vram_xi_full = _M_base_full * N * 4
_vram_v_full = N * N_PROBES_SENS * 4
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
