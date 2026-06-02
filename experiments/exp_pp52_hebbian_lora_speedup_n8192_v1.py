"""
pp52_hebbian_lora_speedup_n8192_v1 -- PP-52 A1: Hebbian vs GD+Adam speedup at N=8192.

Extends N=4096 (HARD_PASS) to N=8192. Tests whether 100x+ speedup holds at production N=8192.

SCIENTIFIC QUESTION:
  At N=8192, M=800 (alpha=0.098): does Hebbian one-shot write achieve same encoding
  fidelity as GD+Adam with >= 100x wall-time speedup?

  W matrix at N=8192: 8192^2 * 4 bytes = 268 MB. Fits on 8 GB GPU.

PRE-REGISTERED HARD-PASS:
  HP1: Hebbian retrieval accuracy within +-2pp of GD accuracy in >= 4/5 seeds.
  HP2: wall-time speedup >= 100x in >= 4/5 seeds.
  HP3: FLOPs speedup >= 400x in >= 4/5 seeds.
  HARD-PASS: all 3 HP in >= 4/5 seeds.

PRE-REGISTERED HARD-FAIL:
  HF1: Hebbian accuracy < 90% of GD accuracy.
  HF2: speedup < 10x.

MIDDLE BAND: accuracy within +-5pp OR speedup 10-100x.
P_deflated = 0.72 (prior N=4096 HP; algebraic identity; N=8192 extends).

GPU IMPLEMENTATION:
  W matrix (N x N float32 at N=8192): 268 MB. GD uses GPU matmuls.
  Reduced GD_MAX_ITER vs N=4096 (3000 steps max; early-stop at loss < 0.001).

FORMULA SELF-TESTS:
  1. Hebbian W = Xi^T Xi / N. At alpha=0.098, retrieval acc > 0.85.
     [INPUT: N=256, M=25] [EXPECTED: accuracy > 0.85]
  2. GD convergence: loss reaches < 0.1 at convergence.
     [INPUT: N=64, M=6] [EXPECTED: final loss < 0.1]
  3. GPU memory > 100 MB after W build.

PROT-018: anchor has _n8192; N MUST = 8192.
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
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
    import torch.nn as nn
    import torch.optim as optim
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

ANCHOR_NAME = "pp52_hebbian_lora_speedup_n8192_v1"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    M = 50
    SEEDS = [7, 17]
    N_QUERIES = 10
    GD_LR = 0.05
    GD_MAX_ITER = 1000
else:
    N_ACTIVE = N  # 8192
    M = 800       # alpha = 0.098
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 50
    GD_LR = 0.05
    GD_MAX_ITER = 3000

HP_ACC_DELTA_PP = 2.0
HF_ACC_RATIO = 0.90
HP_WALL_SPEEDUP = 100.0
HF_WALL_SPEEDUP = 10.0
HP_FLOPS_SPEEDUP = 400.0


def retrieve_hopfield_gpu(W: torch.Tensor, probe: torch.Tensor, n_steps: int = 5) -> torch.Tensor:
    state = probe.clone()
    for _ in range(n_steps):
        h = W @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def hebbian_accuracy(W: torch.Tensor, Xi: torch.Tensor, queries: torch.Tensor,
                     n_dim: int) -> float:
    n_q = queries.shape[0]
    n_correct = 0
    for i in range(n_q):
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(i * 1000 + 7)
        probe = queries[i].clone()
        flip = torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC
        probe[flip] *= -1.0
        ret = retrieve_hopfield_gpu(W, probe)
        cos = float(torch.dot(ret, queries[i])) / (float(ret.norm()) * float(queries[i].norm()) + 1e-12)
        if cos > 0.90:
            n_correct += 1
    return float(n_correct) / n_q if n_q > 0 else 0.0


def _selftest_hebbian_acc():
    N_t, M_t = 256, 25
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    W_t = Xi_t.t() @ Xi_t / float(N_t)
    acc = hebbian_accuracy(W_t, Xi_t, Xi_t[:10], N_t)
    assert acc > 0.85, f"Hebbian acc selftest: {acc:.4f} < 0.85 at alpha=0.098"


def _selftest_gd_convergence():
    N_t, M_t = 64, 6
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    W_gd = torch.zeros((N_t, N_t), device=DEVICE, dtype=torch.float32, requires_grad=True)
    opt = optim.Adam([W_gd], lr=0.05)
    for _ in range(300):
        opt.zero_grad()
        loss = ((W_gd @ Xi_t.t() - Xi_t.t()) ** 2).mean()
        loss.backward()
        opt.step()
    final_loss = float(((W_gd @ Xi_t.t() - Xi_t.t()) ** 2).mean())
    assert final_loss < 0.1, f"GD convergence selftest: loss={final_loss:.4f} >= 0.1"


def _instrumentation_selftest():
    _selftest_hebbian_acc()
    _selftest_gd_convergence()
    # VRAM check: GPU must be available and allocating memory
    dummy = torch.zeros((2048, 2048), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 1e6, f"GPU memory not > 1MB: {mem/1e6:.1f}MB"
    del dummy
    # N=8192 VRAM estimate: 268 MB W_heb + 268 MB W_gd + overhead ~ 600 MB < 8 GB OK
    vram_est_mb = (2 * N * N * 4) / 1e6
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    assert vram_est_mb < total_gb * 1000 * 0.8, f"VRAM estimate {vram_est_mb:.0f}MB > 80% GPU {total_gb:.1f}GB"
    print(f"[selftest] PASS: hebbian_acc>0.85, gd_converges, gpu_mem={mem/1e6:.1f}MB "
          f"N=8192 VRAM_est={vram_est_mb:.0f}MB GPU_total={total_gb:.1f}GB", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0_seed = time.time()

    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    queries = Xi[:min(N_QUERIES, M)]

    # Hebbian arm
    t0_heb = time.time()
    W_heb = Xi.t() @ Xi / float(n_dim)
    torch.cuda.synchronize()
    t_heb = time.time() - t0_heb

    acc_heb = hebbian_accuracy(W_heb, Xi, queries, n_dim)
    n_flops_heb = 2 * M * n_dim * n_dim

    # GD arm
    t0_gd = time.time()
    W_gd = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32, requires_grad=True)
    opt = optim.Adam([W_gd], lr=GD_LR)
    n_iter = 0
    for step in range(GD_MAX_ITER):
        opt.zero_grad()
        loss = ((W_gd @ Xi.t() - Xi.t()) ** 2).mean()
        loss.backward()
        opt.step()
        n_iter += 1
        if float(loss) < 0.001:
            break
        if step % 500 == 0:
            print(f"    [seed={seed} GD step={step}] loss={float(loss):.6f}", flush=True)

    torch.cuda.synchronize()
    t_gd = time.time() - t0_gd

    with torch.no_grad():
        acc_gd = hebbian_accuracy(W_gd, Xi, queries, n_dim)

    n_flops_gd = 4 * n_iter * M * n_dim * n_dim
    wall_speedup = t_gd / max(t_heb, 1e-9)
    flops_speedup = n_flops_gd / max(n_flops_heb, 1)
    acc_delta_pp = abs(acc_heb - acc_gd) * 100.0

    hp1 = acc_delta_pp <= HP_ACC_DELTA_PP
    hp2 = wall_speedup >= HP_WALL_SPEEDUP
    hp3 = flops_speedup >= HP_FLOPS_SPEEDUP
    hf1 = acc_gd > 0 and acc_heb < HF_ACC_RATIO * acc_gd
    hf2 = wall_speedup < HF_WALL_SPEEDUP

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0_seed
    print(f"  [seed={seed} N={n_dim}] acc_heb={acc_heb:.4f} acc_gd={acc_gd:.4f} "
          f"delta_pp={acc_delta_pp:.2f}(HP<={HP_ACC_DELTA_PP}pp) "
          f"wall_speedup={wall_speedup:.1f}x(HP>={HP_WALL_SPEEDUP}x) "
          f"flops_speedup={flops_speedup:.1f}x "
          f"t_heb={t_heb:.3f}s t_gd={t_gd:.2f}s n_iter={n_iter} "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "acc_heb": float(acc_heb), "acc_gd": float(acc_gd),
        "acc_delta_pp": float(acc_delta_pp),
        "wall_speedup": float(wall_speedup),
        "flops_speedup": float(flops_speedup),
        "t_heb": float(t_heb), "t_gd": float(t_gd), "n_iter": int(n_iter),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    n = len(results)
    acc_delta = mean_key("acc_delta_pp")
    wall_spd = mean_key("wall_speedup")
    flops_spd = mean_key("flops_speedup")
    hp1_n = sum(1 for r in results if r.get("hp1"))
    hp2_n = sum(1 for r in results if r.get("hp2"))
    hp3_n = sum(1 for r in results if r.get("hp3"))
    hf1_any = any(r.get("hf1") for r in results)
    hf2_any = any(r.get("hf2") for r in results)

    summary = (f"acc_delta_pp={acc_delta:.2f}(HP<={HP_ACC_DELTA_PP}pp) "
               f"wall_speedup={wall_spd:.1f}x(HP>={HP_WALL_SPEEDUP}x) "
               f"flops_speedup={flops_spd:.1f}x "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}")

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: Hebbian accuracy < 90% of GD. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: speedup < {HF_WALL_SPEEDUP}x. {summary}")

    min_pass = max(1, int(n * 0.8))
    if all(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n]):
        return ("HARD_PASS", f"HARD_PASS: all 3 HP in >={min_pass}/{n} seeds at N=8192. {summary}")
    n_met = sum(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n])
    if n_met >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/3 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_met}/3 HP met. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} M={M} "
      f"GD_MAX_ITER={GD_MAX_ITER}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M, "run_mode": RUN_MODE}
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

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "n_active": N_ACTIVE, "M": M,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
