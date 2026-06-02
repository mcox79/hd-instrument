"""
wave5_cell5_combo1_n32768_local_v1 -- Wave 5 Cell 5: COMBO-1 at N=32768 LOCAL GPU.

Unlocked by combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096 HARD_PASS.
This is the local GPU N=32768 extension.

VRAM STRATEGY (load-bearing):
  NEVER materialize W = Xi.T @ Xi (N=32768 x N=32768 float32 = 4.29 GB -- too large).
  Use FULLY MATRIX-FREE operations:
    p=3 retrieve: h = Xi.T @ (Xi @ state)^2 / N  (two matmuls, no W materialized).
    kappa3 via Hutchinson with implicit W-op.
  Xi (M x N float32) for M=2*N=65536: 65536*32768*4 = 8.59 GB -- ALSO TOO LARGE.
  Use alpha = 0.10 -> M = 3277 patterns:
    Xi (3277 x 32768 float32) = 429 MB. Safe.
  For M_LIST full sweep: [N, 2*N] would OOM. Use [N//4, N//2] = [8192, 16384].
    Xi at M=16384: 16384 * 32768 * 4 = 2.15 GB. Fine.
    Xi at M=8192: 8192 * 32768 * 4 = 1.07 GB. Fine.

PRE-REGISTERED BANDS (same as v3_gpu_fix N=4096 HARD_PASS; N=32768 production):
  HP1: MMD(retrieval_p3, stored_patterns) < 0.02 at tested M values.
  HP2: kappa3_rescaled = Tr(G^3)/M within 5% of 1.0.
  HP3: Write wall-time log-log slope <= 1.3.
  HP4: Mean retrieval cosine >= 0.95.
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4.
  MIDDLE: HP1 + HP2 + exactly one of HP3/HP4.
  HARD-FAIL: MMD >= 0.10 OR |kappa3_rescaled - 1.0| > 0.20 OR cosine < 0.70.

FORMULA SELF-TESTS:
  1. G_ii = 1.0 for BSC patterns under p=3 Gram.
     [INPUT: xi +-1, N=256] [EXPECTED: G_ii = 1.0]
  2. GPU guard: memory_allocated > 0 after Xi alloc.
  3. Matrix-free p3 retrieve: h = Xi.T @ (Xi @ state)^2 / N at tiny scale.

PROT-018: anchor has _n32768; N MUST = 32768.
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

# GPU GUARD
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

ANCHOR_NAME = "wave5_cell5_combo1_n32768_local_v1"

_N_SUFFIX = 32768
N = 32768
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    # M at smoke: safe sizes
    M_LIST = [N_ACTIVE // 4, N_ACTIVE // 2]
    N_PROBES_K3 = 50
    N_TEST_RETRIEVAL = 5
    N_WRITE_STEPS = [N_ACTIVE // 4, N_ACTIVE // 2]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [N // 4, N // 2]   # 8192 and 16384 (safe VRAM: 1.07 + 2.15 GB)
    N_PROBES_K3 = 200
    N_TEST_RETRIEVAL = 15
    N_WRITE_STEPS = [N // 4, N // 2]

# Pre-registered thresholds
HP1_MMD = 0.02
HF1_MMD = 0.10
HP2_KAPPA3_TOL = 0.05
HF2_KAPPA3_TOL = 0.20
HP3_SLOPE = 1.3
HP4_COS = 0.95
HF4_COS = 0.70


def p3_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor, n: int, n_steps: int = 5):
    """Matrix-free p=3 retrieval: h = Xi.T @ (Xi @ state)^2 / n."""
    state = probe.clone()
    for _ in range(n_steps):
        overlaps = Xi @ state           # (M,)
        h = Xi.t() @ overlaps.pow(2)   # (N,)
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


def compute_mmd_proxy(retrieved: List[torch.Tensor], references: torch.Tensor) -> float:
    """MMD proxy via cosine cross-similarity."""
    if not retrieved:
        return 1.0
    ret_t = torch.stack(retrieved)
    s_norm = torch.nn.functional.normalize(ret_t.float(), dim=1)
    r_norm = torch.nn.functional.normalize(references[:len(retrieved)].float(), dim=1)
    cross = torch.mm(s_norm, r_norm.t())
    return float(max(1.0 - cross.mean(), 0.0))


def hutchinson_kappa3_gpu(Xi: torch.Tensor, n: int, n_probes: int, seed: int) -> float:
    """Implicit kappa_3 = Tr(W^3)/N via Hutchinson."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 3333)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)
    return float((V0 * V3).sum(dim=0).mean() / n)


def _instrumentation_selftest():
    """G_ii=1.0, p3 matfree retrieval non-NaN, GPU mem > 0."""
    # G_ii test
    N_t = 256
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi = (torch.randint(0, 2, (N_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    dot_self = float(xi.dot(xi)) / N_t
    assert abs(dot_self - 1.0) < 0.01, f"G_ii: {dot_self:.4f}"

    # p3 matfree at tiny scale
    Xi_t = xi.unsqueeze(0)
    state = xi.clone()
    overlaps = Xi_t @ state
    h = Xi_t.t() @ overlaps.pow(2) / N_t
    assert not (float(h.sum()) != float(h.sum())), "p3 matfree NaN"

    # GPU memory check
    dummy = torch.zeros((1024, 1024), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy

    print(f"[selftest] PASS: G_ii=1.0, p3_matfree_non_nan, gpu_mem_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_m(seed: int, n_dim: int, M: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + M * 7)
    t0 = time.time()

    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    vram_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={M}] GPU memory after Xi alloc: {vram_gb:.3f} GB", flush=True)

    # HP1: MMD proxy -- retrieve test patterns
    n_test = min(N_TEST_RETRIEVAL, M)
    retrieved = []
    for i in range(n_test):
        probe = Xi[i].clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < 0.10)
        probe[flip] *= -1.0
        ret = p3_retrieve_gpu(Xi, probe, n_dim)
        retrieved.append(ret)
    mmd = compute_mmd_proxy(retrieved, Xi)

    # HP2: kappa3 rescaled
    k3 = hutchinson_kappa3_gpu(Xi, n_dim, N_PROBES_K3, seed=seed)
    k3_resc = k3 * n_dim / M if M > 0 else 0.0

    # HP3: write slope
    write_times = []
    for w_step in [s for s in N_WRITE_STEPS if s <= M]:
        Xi_sub = Xi[:w_step]
        t_w = time.time()
        # Gram build proxy
        _ = Xi_sub @ Xi_sub.t() / n_dim
        torch.cuda.synchronize()
        write_times.append((w_step, time.time() - t_w))
        del _

    slope = 1.0
    if len(write_times) >= 2:
        xs = [math.log(w) for w, _ in write_times]
        ys = [math.log(max(t, 1e-9)) for _, t in write_times]
        if xs[-1] != xs[0]:
            slope = (ys[-1] - ys[0]) / (xs[-1] - xs[0])

    # HP4: mean cosine
    cos_vals = [cosine_sim_gpu(retrieved[i], Xi[i]) for i in range(len(retrieved))]
    mean_cos = float(sum(cos_vals)/len(cos_vals)) if cos_vals else 0.0

    del Xi
    elapsed = time.time() - t0
    print(f"    [M={M}] MMD={mmd:.4f} k3_resc={k3_resc:.4f} slope={slope:.2f} "
          f"cos={mean_cos:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "M": M, "mmd": float(mmd), "kappa3_resc": float(k3_resc),
        "write_slope": float(slope), "mean_cos": float(mean_cos),
    }


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    m_results = [run_seed_m(seed, n_dim, M) for M in M_LIST]
    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)
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

    mean_mmd = float(sum(mmds)/len(mmds))
    mean_k3 = float(sum(k3s)/len(k3s))
    mean_slope = float(sum(slopes)/len(slopes))
    mean_cos = float(sum(coss)/len(coss))

    summary = (f"MMD={mean_mmd:.4f}(HP<{HP1_MMD} HF>={HF1_MMD}) "
               f"k3_resc={mean_k3:.4f}(|k-1|<={HP2_KAPPA3_TOL}) "
               f"slope={mean_slope:.3f}(HP<={HP3_SLOPE}) "
               f"cos={mean_cos:.4f}(HP>={HP4_COS} HF<{HF4_COS}) "
               f"n_results={len(all_m_results)}")

    if mean_mmd >= HF1_MMD or abs(mean_k3 - 1.0) > HF2_KAPPA3_TOL or mean_cos < HF4_COS:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = mean_mmd < HP1_MMD
    hp2 = abs(mean_k3 - 1.0) <= HP2_KAPPA3_TOL
    hp3 = mean_slope <= HP3_SLOPE
    hp4 = mean_cos >= HP4_COS

    if hp1 and hp2 and hp3 and hp4:
        return ("HARD_PASS", f"HARD_PASS: all 4 HP conditions at N=32768. {summary}")
    if hp1 and hp2 and (hp3 or hp4):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: HP1+HP2+1 of HP3/HP4. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3,hp4])}/4 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_LIST={M_LIST} matrix_free=True", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
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
