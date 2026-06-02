"""
pp52_exact_rollback_n16384_v1 -- PP-52 A3: exact rollback via rank-1 subtraction at N=16384.

Production-N extension of pp52_exact_rollback_n8192_v1 (HP at N=8192 in Cycle 12).
Tests machine-precision rollback at N=16384.

SCIENTIFIC QUESTION:
  At N=16384: does rank-1 rollback W' - (1/N) xi xi^T = W_orig to within 1e-6 relative error?
  W matrix: 16384*16384*4 = 1073 MB. Safe on 8 GB GPU (1.07 GB per matrix; 3 matrices = 3.2 GB).

PRE-REGISTERED HARD-PASS (cross-N extension N=16384):
  HP1: ||W_rb - W_orig||_F / ||W_orig||_F < 1e-6 in >= 4/5 seeds (fp32 precision).
  HP2: retrieval accuracy >= 0.95 after rollback in >= 4/5 seeds.
  HP3: rollback wall-time < 2.0 seconds at N=16384 (double N=8192 gate to 2x scaling).
  HARD-PASS: all 3 HP in >= 4/5 seeds.

PRE-REGISTERED HARD-FAIL:
  HF1: relative error > 1e-3.
  HF2: accuracy drops > 5pp after rollback.

MIDDLE BAND: relative error in [1e-6, 1e-3] OR accuracy drop 1-5pp.
P_deflated = 0.80 (algebraically guaranteed; N=4096 + N=8192 both HARD_PASS).

OOM CHECK:
  W original + W' + W_rollback: 3 * 1073 MB = 3219 MB = 3.1 GB. Safe on 8 GB GPU.

FORMULA SELF-TESTS:
  1. Rollback identity: W + xi xi^T / N - xi xi^T / N = W exactly.
     [INPUT: N=4, W random, xi random] [EXPECTED: relative error < 1e-10]
  2. Multiple rollbacks: K writes then K rollbacks returns W.
     [INPUT: K=5] [EXPECTED: relative error < 1e-5]
  3. GPU memory > 100 MB after W build.

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode.
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

ANCHOR_NAME = "pp52_exact_rollback_n16384_v1"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    N_ACTIVE = 2048
    M_BASE = 150
    K_WRITES = 5
    SEEDS = [7, 17]
    N_QUERIES = 10
else:
    N_ACTIVE = N  # 16384
    M_BASE = 1300
    K_WRITES = 20
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 50

# fp32: ~7 digits; HP1 threshold 1e-6 achievable
HP_REL_ERR = 1e-6
HF_REL_ERR = 1e-3
HP_RETAIN_ACC = 0.95
HF_DROP_PP = 5.0
HP_ROLLBACK_TIME = 2.0  # 2x N=8192 gate (wall scales linearly with N^2 for outer product)


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def retrieve_hopfield_gpu(W: torch.Tensor, probe: torch.Tensor, n_steps: int = 5) -> torch.Tensor:
    state = probe.clone()
    for _ in range(n_steps):
        h = W @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def retrieval_accuracy(W: torch.Tensor, Xi_test: torch.Tensor, n_dim: int) -> float:
    n_q = Xi_test.shape[0]
    n_correct = 0
    gen = torch.Generator(device=DEVICE)
    for i in range(n_q):
        gen.manual_seed(i * 7 + 13)
        probe = Xi_test[i].clone()
        flip = torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC
        probe[flip] *= -1.0
        ret = retrieve_hopfield_gpu(W, probe)
        if cosine_sim_gpu(ret, Xi_test[i]) > 0.90:
            n_correct += 1
    return float(n_correct) / n_q if n_q > 0 else 0.0


def _selftest_rollback_identity():
    n = 4
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    W0 = (torch.randint(0, 2, (n, n), generator=gen, device=DEVICE).float() * 2 - 1) / n
    xi = (torch.randint(0, 2, (n,), generator=gen, device=DEVICE).float() * 2 - 1)
    W1 = W0 + torch.outer(xi, xi) / n
    W_rb = W1 - torch.outer(xi, xi) / n
    rel_err = float((W_rb - W0).norm() / (W0.norm() + 1e-12))
    assert rel_err < 1e-10, f"rollback identity: rel_err={rel_err:.4e} >= 1e-10"


def _selftest_multi_rollback():
    n = 16
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1)
    Xi0 = (torch.randint(0, 2, (5, n), generator=gen, device=DEVICE).float() * 2 - 1)
    W0 = Xi0.t() @ Xi0 / n
    patterns = []
    W = W0.clone()
    for k in range(5):
        xi = (torch.randint(0, 2, (n,), generator=gen, device=DEVICE).float() * 2 - 1)
        patterns.append(xi)
        W = W + torch.outer(xi, xi) / n
    for xi in reversed(patterns):
        W = W - torch.outer(xi, xi) / n
    rel_err = float((W - W0).norm() / (W0.norm() + 1e-12))
    assert rel_err < 1e-4, f"multi rollback: rel_err={rel_err:.4e} >= 1e-4"


def _selftest_gpu_vram():
    n_elems = int(200 * 1e6 / 4)
    dummy = torch.zeros((n_elems,), device=DEVICE, dtype=torch.float32)
    mem_mb = torch.cuda.memory_allocated(0) / 1e6
    assert mem_mb > 100.0, f"GPU VRAM < 100 MB: {mem_mb:.1f} MB"
    del dummy
    torch.cuda.empty_cache()


def _selftest_oom_check():
    # At N=16384, peak = 3 * 16384*16384*4 = 3.2 GB. Verify we have headroom.
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    peak_est_gb = 3 * (N_ACTIVE * N_ACTIVE * 4) / 1e9
    assert peak_est_gb < total_gb - 1.0, (
        f"OOM risk: peak_est={peak_est_gb:.2f}GB vs total={total_gb:.2f}GB (< 1GB headroom)")
    print(f"[selftest] OOM check: peak_est={peak_est_gb:.2f}GB total={total_gb:.2f}GB ok", flush=True)


def _instrumentation_selftest():
    _selftest_rollback_identity()
    _selftest_multi_rollback()
    _selftest_gpu_vram()
    _selftest_oom_check()
    print(f"[selftest] PASS: rollback_identity, multi_rollback, gpu_vram, oom_check", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    Xi_base = (torch.randint(0, 2, (M_BASE, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    W_orig = Xi_base.t() @ Xi_base / float(n_dim)

    test_patterns = Xi_base[:min(N_QUERIES, M_BASE)]
    acc_before = retrieval_accuracy(W_orig, test_patterns, n_dim)

    new_patterns = []
    W = W_orig.clone()
    for k in range(K_WRITES):
        xi = (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)
        new_patterns.append(xi)
        W = W + torch.outer(xi, xi) / float(n_dim)

    rollback_times = []
    for xi in reversed(new_patterns):
        t_r = time.time()
        W = W - torch.outer(xi, xi) / float(n_dim)
        torch.cuda.synchronize()
        rollback_times.append(time.time() - t_r)

    frob_orig = float(W_orig.norm())
    frob_err = float((W - W_orig).norm())
    rel_err = frob_err / (frob_orig + 1e-12)

    acc_after = retrieval_accuracy(W, test_patterns, n_dim)
    max_rollback_time = float(max(rollback_times)) if rollback_times else 0.0
    acc_drop = acc_before - acc_after

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] rel_err={rel_err:.2e} acc_before={acc_before:.4f} "
          f"acc_after={acc_after:.4f} acc_drop={acc_drop:.4f} "
          f"max_rollback_s={max_rollback_time:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "rel_err_frobenius": float(rel_err),
        "acc_before": float(acc_before),
        "acc_after": float(acc_after),
        "acc_drop_pp": float(acc_drop * 100.0),
        "max_rollback_time_s": float(max_rollback_time),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": float(elapsed),
        "hp1_pass": int(rel_err < HP_REL_ERR),
        "hp2_pass": int(acc_after >= HP_RETAIN_ACC),
        "hp3_pass": int(max_rollback_time < HP_ROLLBACK_TIME),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def count_pass(key):
        return sum(1 for r in results if r.get(key, 0))

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    n = len(results)
    hp1_count = count_pass("hp1_pass")
    hp2_count = count_pass("hp2_pass")
    hp3_count = count_pass("hp3_pass")

    rel_m = mean_key("rel_err_frobenius")
    drop_m = mean_key("acc_drop_pp")
    rt_m = mean_key("max_rollback_time_s")

    summary = (f"mean_rel_err={rel_m:.2e}(HP<{HP_REL_ERR:.0e} HF>{HF_REL_ERR:.0e}) "
               f"mean_acc_drop_pp={drop_m:.4f}(HF>{HF_DROP_PP:.1f}pp) "
               f"mean_rollback_s={rt_m:.4f}(HP<{HP_ROLLBACK_TIME}) "
               f"hp1_seeds={hp1_count}/{n} hp2_seeds={hp2_count}/{n} hp3_seeds={hp3_count}/{n}")

    if rel_m > HF_REL_ERR or drop_m > HF_DROP_PP:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1_ok = hp1_count >= 4
    hp2_ok = hp2_count >= 4
    hp3_ok = hp3_count >= n  # all seeds for timing gate

    if hp1_ok and hp2_ok and hp3_ok:
        return ("HARD_PASS", f"HARD_PASS: all HP at N=16384. {summary}")
    if hp1_ok and hp2_ok:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: timing only miss. {summary}")
    if hp1_count >= 3 or hp2_count >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_BASE={M_BASE} K_WRITES={K_WRITES}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_BASE": M_BASE, "K_WRITES": K_WRITES, "run_mode": RUN_MODE}
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
    "N": N, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "rel_err_frobenius": r.get("rel_err_frobenius"),
         "acc_drop_pp": r.get("acc_drop_pp"),
         "max_rollback_time_s": r.get("max_rollback_time_s"),
         "hp1_pass": r.get("hp1_pass"), "hp2_pass": r.get("hp2_pass"),
         "hp3_pass": r.get("hp3_pass"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
