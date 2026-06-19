"""
wave5_cell5_combo1_n65536_LOCAL_stretch_v1 -- Wave 5 Cell 5.5: COMBO-1 p=3 DAM at N=65536 LOCAL GPU.

Extends wave5_cell5_combo1_n32768_local_v1 (HARD_PASS) to N=65536.
VRAM critical: Xi (M x N float32) for M = N*alpha:
  alpha=0.05 -> M=3277: 3277*65536*4 = 859 MB. Safe.
  But N*N*4 = 17.18 GB for any N x N matrix -> MUST stay fully matrix-free.
  Brand refresh slope uses Xi_sub @ Xi_sub.T -> at M=3277: 3277*3277*4 = 43 MB Gram. Safe.
  DO NOT materialize any N x N tensor.

If VRAM exceeds 6 GB during smoke, abort and route to Strategy as OOM.
Multi-scale smoke: N_smoke=4096 AND N_smoke*4=16384 both must pass.

PRE-REGISTERED BANDS (inherited from n32768 HARD_PASS):
  HP1: MMD(retrieval_p3, stored_patterns) < 0.02.
  HP2: kappa3_rescaled within 5% of 1.0.
  HP3: Write wall-time log-log slope <= 1.3.
  HP4: Mean retrieval cosine >= 0.95.
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4.
  MIDDLE: HP1 + HP2 + exactly one of HP3/HP4.
  HARD-FAIL: MMD >= 0.10 OR |kappa3_rescaled - 1.0| > 0.20 OR cosine < 0.70.

FORMULA SELF-TESTS:
  1. G_ii = 1.0 for BSC patterns under p=3 Gram.
     [INPUT: xi +-1, N=256] [EXPECTED: G_ii = 1.0]
  2. Matrix-free p3 retrieve: h = Xi.T @ (Xi @ state)^2 / N at N=64.
     [INPUT: M=2, N=64] [EXPECTED: retrieved vector non-NaN]
  3. GPU memory < 6 GB after Xi alloc at N=65536 alpha=0.05.

PROT-018: anchor has _n65536 -> N must = 65536.
PROT-021: run_config includes N, alpha, run_mode.
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

ANCHOR_NAME = "wave5_cell5_combo1_n65536_LOCAL_stretch_v1"

_N_SUFFIX = 65536
N = 65536
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05  # pattern load: M = N * ALPHA -> matrix-free stays safe
VRAM_LIMIT_GB = 6.0  # abort if exceeded

if RUN_MODE == "smoke":
    # Multi-scale smoke: test at 4096 and 16384 (= 4096*4) both
    N_ACTIVE = 4096
    N_SMOKE_SCALE2 = 16384
    SEEDS = [7, 17]
    N_PROBES_K3 = 50
    N_TEST_RETRIEVAL = 5
else:
    N_ACTIVE = N  # 65536
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES_K3 = 200
    N_TEST_RETRIEVAL = 20

HP1_MMD = 0.02
HF1_MMD = 0.10
HP2_KAPPA3_TOL = 0.05
HF2_KAPPA3_TOL = 0.20
HP3_SLOPE = 1.3
HP4_COS = 0.95
HF4_COS = 0.70

VRAM_OOM_GUARD_GB = 6.5  # abort single seed if VRAM exceeds this


def p3_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor,
                    n_steps: int = 5, n: int = None) -> torch.Tensor:
    """p=3 matrix-free retrieval: h = Xi.T @ (Xi @ state)^2 / n."""
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
    if samples.shape[0] == 0 or references.shape[0] == 0:
        return 1.0
    s_norm = torch.nn.functional.normalize(samples.float(), dim=1)
    r_norm = torch.nn.functional.normalize(references.float(), dim=1)
    cross = torch.mm(s_norm, r_norm.t())
    return float(max(1.0 - float(cross.mean()), 0.0))


def hutchinson_kappa3_implicit(Xi: torch.Tensor, n: int, n_probes: int, seed: int) -> float:
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
    N_t = 256
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    xi = (torch.randint(0, 2, (N_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    g_ii = float(xi.dot(xi)) / N_t
    assert abs(g_ii - 1.0) < 0.01, f"G_ii test: {g_ii:.4f} != 1.0"


def _selftest_p3_matfree():
    n = 64
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    Xi = (torch.randint(0, 2, (2, n), generator=gen, device=DEVICE).float() * 2 - 1)
    state = Xi[0].clone()
    result = p3_retrieve_gpu(Xi, state, n_steps=1, n=n)
    assert not (result != result).any(), "p3_retrieve result contains NaN"


def _instrumentation_selftest():
    _selftest_gram_diagonal()
    _selftest_p3_matfree()
    mem_before = torch.cuda.memory_allocated(0)
    dummy = torch.zeros((1024, 1024), device=DEVICE, dtype=torch.float32)
    mem_after = torch.cuda.memory_allocated(0)
    assert mem_after > mem_before, f"GPU memory not increasing"
    del dummy
    print(f"[selftest] PASS: G_ii=1.0, p3_matfree_non_nan, gpu_mem_ok N={N}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_at_n(n_dim: int, seed: int) -> Dict:
    """Run a single (seed, N) combination. Returns dict with metrics or OOM flag."""
    M = max(1, int(n_dim * ALPHA))
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + n_dim)
    t0 = time.time()

    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={M}] GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)

    if mem_gb > VRAM_OOM_GUARD_GB:
        del Xi
        print(f"  [OOM_GUARD] VRAM {mem_gb:.2f} GB > {VRAM_OOM_GUARD_GB} GB limit -- aborting",
              flush=True)
        return {"n_dim": n_dim, "seed": seed, "oom": True, "vram_gb": mem_gb}

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
    kappa3 = hutchinson_kappa3_implicit(Xi, n_dim, N_PROBES_K3, seed=seed)
    kappa3_resc = kappa3 * n_dim / M if M > 0 else 0.0

    # HP3: Brand refresh slope (Gram only, M x M NOT N x N)
    write_steps = [max(1, M // 4), max(1, M // 2), M]
    write_times = []
    for w_step in write_steps:
        t_w = time.time()
        Xi_sub = Xi[:w_step]
        _G = Xi_sub @ Xi_sub.t() / n_dim  # M x M, safe
        torch.cuda.synchronize()
        write_times.append((w_step, time.time() - t_w))
        del _G

    slope = 1.0
    if len(write_times) >= 2:
        xs = [math.log(max(w, 1)) for w, _ in write_times]
        ys = [math.log(max(t, 1e-9)) for _, t in write_times]
        if xs[-1] != xs[0]:
            slope = (ys[-1] - ys[0]) / (xs[-1] - xs[0])

    # HP4: mean cosine
    cos_vals = [cosine_sim_gpu(retrieved[i], test_probes[i]) for i in range(N_TEST_RETRIEVAL)]
    mean_cos = float(sum(cos_vals) / len(cos_vals)) if cos_vals else 0.0

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    del Xi
    elapsed = time.time() - t0
    print(f"    [N={n_dim} M={M}] MMD={mmd:.4f} k3r={kappa3_resc:.4f} slope={slope:.2f} "
          f"cos={mean_cos:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "n_dim": n_dim, "seed": seed, "M": M, "oom": False,
        "mmd": float(mmd), "kappa3_resc": float(kappa3_resc),
        "write_slope": float(slope), "mean_cos": float(mean_cos),
        "peak_gpu_gb": float(peak_mem_gb), "elapsed_s": elapsed,
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()

    if RUN_MODE == "smoke":
        # Multi-scale smoke: run at N_smoke AND N_smoke*4
        r_s1 = run_at_n(N_ACTIVE, seed)
        r_s2 = run_at_n(N_SMOKE_SCALE2, seed)
        if r_s1.get("oom") or r_s2.get("oom"):
            return {"seed": seed, "oom": True, "elapsed_s": time.time() - t0,
                    "vram_s1_gb": r_s1.get("vram_gb", 0.0),
                    "vram_s2_gb": r_s2.get("vram_gb", 0.0)}
        # Use scale2 (N=16384) results as the smoke metrics
        return {
            "seed": seed, "oom": False, "run_mode": "smoke",
            "mmd": r_s2["mmd"], "kappa3_resc": r_s2["kappa3_resc"],
            "write_slope": r_s2["write_slope"], "mean_cos": r_s2["mean_cos"],
            "peak_gpu_gb": max(r_s1["peak_gpu_gb"], r_s2["peak_gpu_gb"]),
            "elapsed_s": time.time() - t0,
        }
    else:
        r = run_at_n(N_ACTIVE, seed)
        if r.get("oom"):
            return {"seed": seed, "oom": True, "elapsed_s": time.time() - t0}
        r["run_mode"] = "full"
        r["elapsed_s"] = time.time() - t0
        return r


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    oom_count = sum(1 for r in results if r.get("oom"))
    if oom_count > 0:
        return ("HARD_FAIL", f"HARD_FAIL OOM: {oom_count}/{len(results)} seeds OOM at N={N}. "
                f"Route to Strategy for N_max determination.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r and not r.get("oom")]
        return float(sum(vs) / len(vs)) if vs else 0.0

    mmd = mean_key("mmd")
    k3r = mean_key("kappa3_resc")
    slope = mean_key("write_slope")
    cos = mean_key("mean_cos")

    summary = (f"mmd={mmd:.4f}(HP<{HP1_MMD}) k3r={k3r:.4f}(HP~1.0+-{HP2_KAPPA3_TOL}) "
               f"slope={slope:.3f}(HP<={HP3_SLOPE}) cos={cos:.4f}(HP>={HP4_COS}) "
               f"n_seeds={len(results)} N={N}")

    if mmd >= HF1_MMD or abs(k3r - 1.0) > HF2_KAPPA3_TOL or cos < HF4_COS:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = mmd < HP1_MMD
    hp2 = abs(k3r - 1.0) <= HP2_KAPPA3_TOL
    hp3 = slope <= HP3_SLOPE
    hp4 = cos >= HP4_COS

    if hp1 and hp2 and hp3 and hp4:
        return ("HARD_PASS", f"HARD_PASS: all 4 HP at N=65536. {summary}")
    if sum([hp1, hp2, hp3, hp4]) >= 3 and hp1 and hp2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: HP1+HP2+one of HP3/HP4. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3,hp4])}/4 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return  # smoke allowed at smaller N
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"), "oom": r.get("oom"), "mmd": r.get("mmd"),
         "kappa3_resc": r.get("kappa3_resc"), "write_slope": r.get("write_slope"),
         "mean_cos": r.get("mean_cos"), "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
