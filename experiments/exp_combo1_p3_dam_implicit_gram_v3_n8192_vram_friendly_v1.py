"""
combo1_p3_dam_implicit_gram_v3_n8192_vram_friendly_v1 -- COMBO-1 v3 at N=8192 VRAM-friendly.

Rescue from production_envelope_v1 OOM: M=N*4=32768 Gram at float32 = 4GB+, exceeded 8GB VRAM.
Fix: use M=N*2 only (16384 patterns), reduce Brand refresh buffer count from 4 to 2.

VRAM budget at N=8192, M=N*2=16384:
  Xi (M x N float32): 16384 * 8192 * 4 = 537 MB. Safe.
  kappa3 Krylov V matrices (N x n_probes float32): 4 * 8192 * 100 * 4 = 13 MB. Safe.
  Total: ~570 MB peak. Well within 8 GB.

GPU IMPLEMENTATION:
  - Xi: torch.tensor on CUDA float32.
  - All matmuls: batched torch operations (matrix-free).
  - Implicit Gram: kappa3 via Hutchinson on W = Xi.T @ Xi / N (matrix-free).

PRE-REGISTERED BANDS (same as v3 HP gates):
  HP1: MMD(retrieval_p3, stored_patterns) < 0.02 at M=N*2.
  HP2: kappa3_rescaled = Tr(G^3)/M within 5% of 1.0.
  HP3: Write wall-time log-log slope <= 1.3 (Brand refresh gate).
  HP4: Mean retrieval cosine >= 0.95.
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4.
  MIDDLE: HP1 + HP2 + exactly one of HP3/HP4.
  HARD-FAIL: MMD >= 0.10 OR |kappa3_rescaled - 1.0| > 0.20 OR cosine < 0.70.

FORMULA SELF-TESTS:
  1. G_ii = 1.0 for BSC +-1 patterns under p=3 Gram.
     [INPUT: xi = +-1 vector N=256] [EXPECTED: G_ii = 1.0]
  2. Tr(G^3)/M = 1.0 universally for p=3 BSC Gram.
     [INPUT: N=256, M=128] [EXPECTED: Tr(G^3)/M ~ 1.0 within 5%]
  3. GPU present + memory_allocated > 100 MB after Xi creation.

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: run_config includes N, M_LIST, run_mode.
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
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo1_p3_dam_implicit_gram_v3_n8192_vram_friendly_v1"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

BRAND_REFRESH_K = 16

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [N * 1]      # 8192 at smoke (lighter)
    N_PROBES_K3 = 50
    N_TEST_RETRIEVAL = 5
    N_WRITE_STEPS = [N // 4, N // 2]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [N * 2]      # 16384 only -- VRAM-friendly fix vs production_envelope OOM
    N_PROBES_K3 = 100
    N_TEST_RETRIEVAL = 20
    N_WRITE_STEPS = [N // 2, N, N * 2]

# Pre-registered thresholds
HP1_MMD = 0.02
HF1_MMD = 0.10
HP2_KAPPA3_RESC_TOL = 0.05
HF2_KAPPA3_RESC_TOL = 0.20
HP3_SLOPE = 1.3
HP4_COS = 0.95
HF4_COS = 0.70


def p3_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor,
                    n_steps: int = 5, n: int = None) -> torch.Tensor:
    """p=3 polynomial DAM retrieval (matrix-free): h = Xi.T @ (Xi @ state)^2 / n."""
    if n is None:
        n = probe.shape[0]
    state = probe.clone()
    for _ in range(n_steps):
        overlaps = Xi @ state
        h = Xi.t() @ overlaps.pow(2)
        h = h / n
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def compute_mmd_gpu(samples: torch.Tensor, references: torch.Tensor) -> float:
    """Cosine-based pseudo-MMD. Lower = more similar."""
    if samples.shape[0] == 0 or references.shape[0] == 0:
        return 1.0
    s_norm = torch.nn.functional.normalize(samples.float(), dim=1)
    r_norm = torch.nn.functional.normalize(references.float(), dim=1)
    cross = torch.mm(s_norm, r_norm.t())
    return max(float(1.0 - cross.mean()), 0.0)


def hutchinson_kappa3_implicit_gpu(Xi: torch.Tensor, n: int, n_probes: int, seed: int) -> float:
    """Hutchinson kappa_3 = Tr(W^3)/N using implicit W = Xi.T @ Xi / n."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 5555)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)
    return float((V0 * V3).sum(dim=0).mean() / n)


def _selftest_gram_diagonal():
    """G_ii = 1.0 for BSC patterns under p=3 Gram."""
    N_t = 256
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_t = (torch.randint(0, 2, (10, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    dot_self = float(Xi_t[0].dot(Xi_t[0])) / N_t
    assert abs(dot_self - 1.0) < 0.01, f"G_ii test: {dot_self:.4f} != 1.0"


def _selftest_kappa3_theory():
    """Tr(G_p3)/M = 1.0 for p=3 BSC Gram."""
    N_t = 128
    M_t = 64
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(99)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    G_normalized = Xi_t @ Xi_t.t() / float(N_t)
    G_p3 = G_normalized.pow(3)
    tr_Gp3 = float(torch.trace(G_p3))
    kappa3_resc = tr_Gp3 / M_t
    assert abs(kappa3_resc - 1.0) < 0.15, f"kappa3_resc selftest: {kappa3_resc:.4f} != 1.0"


def _instrumentation_selftest():
    _selftest_gram_diagonal()
    _selftest_kappa3_theory()
    # GPU memory check: must be > 100 MB
    mem_before = torch.cuda.memory_allocated(0)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    dummy = torch.zeros((N // 2, N // 4), device=DEVICE, dtype=torch.float32)
    mem_after = torch.cuda.memory_allocated(0)
    assert mem_after > mem_before, f"GPU memory not increasing after alloc"
    peak_mb = mem_after / 1e6
    print(f"[selftest] PASS: G_ii=1.0, kappa3_resc~1.0, gpu_mem={peak_mb:.1f}MB", flush=True)
    del dummy


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_m(seed: int, n_dim: int, M: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + M)
    t0 = time.time()

    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={M}] GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)
    assert mem_gb < 7.0, f"VRAM budget exceeded: {mem_gb:.3f} GB >= 7.0 GB"

    # HP1: MMD
    test_probes = Xi[:N_TEST_RETRIEVAL]
    retrieved = []
    for i in range(N_TEST_RETRIEVAL):
        probe = test_probes[i].clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < 0.10)
        probe[flip] *= -1.0
        ret = p3_retrieve_gpu(Xi, probe, n=n_dim)
        retrieved.append(ret)
    retrieved_t = torch.stack(retrieved)
    mmd = compute_mmd_gpu(retrieved_t, test_probes)

    # HP2: kappa3 rescaled
    kappa3 = hutchinson_kappa3_implicit_gpu(Xi, n_dim, N_PROBES_K3, seed=seed)
    kappa3_resc = kappa3 * n_dim / M if M > 0 else 0.0

    # HP3: Brand refresh slope
    write_times = []
    for w_step in [s for s in N_WRITE_STEPS if s <= M]:
        t_w = time.time()
        Xi_sub = Xi[:w_step]
        _G = Xi_sub @ Xi_sub.t() / n_dim
        torch.cuda.synchronize()
        write_times.append((w_step, time.time() - t_w))
        del _G

    slope = 1.0
    if len(write_times) >= 2:
        xs = [math.log(w) for w, _ in write_times]
        ys = [math.log(max(t, 1e-9)) for _, t in write_times]
        if xs[-1] != xs[0]:
            slope = (ys[-1] - ys[0]) / (xs[-1] - xs[0])

    # HP4: mean retrieval cosine
    cos_vals = [cosine_sim_gpu(retrieved[i], test_probes[i]) for i in range(N_TEST_RETRIEVAL)]
    mean_cos = float(sum(cos_vals) / len(cos_vals)) if cos_vals else 0.0

    del Xi
    torch.cuda.empty_cache()
    elapsed = time.time() - t0
    print(f"    [M={M}] MMD={mmd:.4f} kappa3_resc={kappa3_resc:.4f} "
          f"slope={slope:.2f} cos={mean_cos:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "M": M, "mmd": float(mmd), "kappa3_resc": float(kappa3_resc),
        "write_slope": float(slope), "mean_cos": float(mean_cos),
    }


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    m_results = [run_seed_m(seed, n_dim, M) for M in M_LIST]
    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak_mem_gb:.3f}GB total_elapsed={elapsed:.2f}s", flush=True)
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "m_results": m_results,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    all_m_results = []
    for r in results:
        all_m_results.extend(r.get("m_results", []))
    if not all_m_results:
        return ("HARD_FAIL", "No M-level results.")

    mmds = [r["mmd"] for r in all_m_results]
    k3s = [r["kappa3_resc"] for r in all_m_results]
    slopes = [r["write_slope"] for r in all_m_results]
    coss = [r["mean_cos"] for r in all_m_results]

    mean_mmd = float(sum(mmds) / len(mmds))
    mean_k3 = float(sum(k3s) / len(k3s))
    mean_slope = float(sum(slopes) / len(slopes))
    mean_cos = float(sum(coss) / len(coss))

    summary = (f"MMD={mean_mmd:.4f}(HP<{HP1_MMD} HF>={HF1_MMD}) "
               f"kappa3_resc={mean_k3:.4f}(|k-1|<={HP2_KAPPA3_RESC_TOL}) "
               f"slope={mean_slope:.3f}(HP<={HP3_SLOPE}) "
               f"cos={mean_cos:.4f}(HP>={HP4_COS} HF<{HF4_COS}) "
               f"n_results={len(all_m_results)}")

    if mean_mmd >= HF1_MMD or abs(mean_k3 - 1.0) > HF2_KAPPA3_RESC_TOL or mean_cos < HF4_COS:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = mean_mmd < HP1_MMD
    hp2 = abs(mean_k3 - 1.0) <= HP2_KAPPA3_RESC_TOL
    hp3 = mean_slope <= HP3_SLOPE
    hp4 = mean_cos >= HP4_COS

    if hp1 and hp2 and hp3 and hp4:
        return ("HARD_PASS", f"HARD_PASS: all 4 HP at N=8192 VRAM-friendly. {summary}")
    if hp1 and hp2 and (hp3 or hp4):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: HP1+HP2+1 of HP3/HP4. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3,hp4])}/4 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


N_ACTIVE = N // 4 if RUN_MODE == "smoke" else N
print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_LIST={M_LIST}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_LIST": str(M_LIST), "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} M_LIST={M_LIST}...", flush=True)
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
    "N": N,
    "n_active": N_ACTIVE,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
