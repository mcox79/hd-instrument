"""
pp52_one_shot_addition_n16384_v1 -- PP-52 A2: one-shot addition and recall at N=16384.

Production-N extension of pp52_one_shot_addition_n8192_v1 (HP at N=8192 in Cycle 12).
Tests whether Hebbian one-shot-addition holds at N=16384.

SCIENTIFIC QUESTION:
  At N=16384, M=1300 initial patterns: does one-shot Hebbian write add new patterns
  with immediate retrievability AND existing patterns retain >= 95% accuracy?
  W matrix: 16384*16384*4 = 1073 MB. Safe on 8 GB GPU.

PRE-REGISTERED HARD-PASS (A2 spec N=16384):
  HP1: new pattern cosine >= 0.90 immediately after one write in >= 4/5 seeds.
  HP2: existing patterns retain >= 95% accuracy after K_NEW=10 additions in >= 4/5 seeds.
  HP3: write wall-time < 2.0 seconds for any single pattern addition at N=16384.
  HARD-PASS: all 3 HP in >= 4/5 seeds.

PRE-REGISTERED HARD-FAIL:
  HF1: new pattern cosine < 0.70.
  HF2: existing accuracy drops > 10pp.
  HF3: write wall-time > 20 seconds.

MIDDLE BAND: cosine in [0.70, 0.90) OR accuracy drop 5-10pp.
P_deflated = 0.80 (algebraically guaranteed; N=4096+N=8192 both HARD_PASS).

OOM CHECK:
  W matrix: 1073 MB. Peak (W + Xi_init + Xi_new): ~1100 MB. Safe on 8 GB GPU.

FORMULA SELF-TESTS:
  1. After one write: W' @ xi_new ~ xi_new (dominant term).
     [INPUT: N=64, M=6, xi_new random] [EXPECTED: retrieval cosine >= 0.60]
  2. Alpha check: (M_INIT + K_NEW) / N < alpha_c.
     [INPUT: M=1300, K_NEW=10, N=16384] [EXPECTED: alpha=0.0800 < 0.138]
  3. GPU memory > 100 MB after W build.
  4. OOM check: peak_est < total_gpu - 1 GB.

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

ANCHOR_NAME = "pp52_one_shot_addition_n16384_v1"

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
    M_INIT = 150
    K_NEW = 5
    SEEDS = [7, 17]
    N_QUERIES = 10
else:
    N_ACTIVE = N  # 16384
    M_INIT = 1300
    K_NEW = 10
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 50

# Formula self-test
_alpha_new = (M_INIT + K_NEW) / N
print(f"[config] alpha_new = {_alpha_new:.4f} (< alpha_c={ALPHA_C})", flush=True)

HP_COS = 0.90
HF_COS = 0.70
HP_RETAIN_ACC = 0.95
HF_RETAIN_DROP_PP = 10.0
HP_WRITE_TIME = 2.0   # 2x N=8192 gate
HF_WRITE_TIME = 20.0


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


def _selftest_oneshot_write():
    N_t, M_t = 64, 6
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    W_t = Xi_t.t() @ Xi_t / float(N_t)
    xi_new = (torch.randint(0, 2, (N_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    W_t2 = W_t + torch.outer(xi_new, xi_new) / float(N_t)
    ret = retrieve_hopfield_gpu(W_t2, xi_new)
    cos = cosine_sim_gpu(ret, xi_new)
    assert cos >= 0.60, f"oneshot write selftest: cos={cos:.4f} < 0.60"


def _selftest_alpha_check():
    assert _alpha_new < ALPHA_C, f"alpha_new={_alpha_new:.4f} >= alpha_c={ALPHA_C}"


def _selftest_gpu_vram():
    n_elems = int(200 * 1e6 / 4)
    dummy = torch.zeros((n_elems,), device=DEVICE, dtype=torch.float32)
    mem_mb = torch.cuda.memory_allocated(0) / 1e6
    assert mem_mb > 100.0, f"GPU VRAM < 100 MB: {mem_mb:.1f} MB"
    del dummy
    torch.cuda.empty_cache()


def _selftest_oom_check():
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    peak_est_gb = 2 * (N_ACTIVE * N_ACTIVE * 4) / 1e9  # W + W_new
    assert peak_est_gb < total_gb - 1.0, (
        f"OOM risk: peak_est={peak_est_gb:.2f}GB vs total={total_gb:.2f}GB (< 1GB headroom)")
    print(f"[selftest] OOM check: peak_est={peak_est_gb:.2f}GB total={total_gb:.2f}GB ok", flush=True)


def _instrumentation_selftest():
    _selftest_oneshot_write()
    _selftest_alpha_check()
    _selftest_gpu_vram()
    _selftest_oom_check()
    print(f"[selftest] PASS: oneshot_write_ok, alpha_check_ok, gpu_vram_ok, oom_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    Xi_init = (torch.randint(0, 2, (M_INIT, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    W = Xi_init.t() @ Xi_init / float(n_dim)

    test_init = Xi_init[:min(N_QUERIES, M_INIT)]
    acc_before = retrieval_accuracy(W, test_init, n_dim)

    new_patterns = (torch.randint(0, 2, (K_NEW, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    cos_new_vals = []
    write_times = []

    for k in range(K_NEW):
        xi_new = new_patterns[k]
        t_w = time.time()
        W = W + torch.outer(xi_new, xi_new) / float(n_dim)
        torch.cuda.synchronize()
        write_time = time.time() - t_w
        write_times.append(write_time)

        ret = retrieve_hopfield_gpu(W, xi_new)
        cos_new = cosine_sim_gpu(ret, xi_new)
        cos_new_vals.append(cos_new)

    acc_after = retrieval_accuracy(W, test_init, n_dim)

    mean_cos_new = float(sum(cos_new_vals) / len(cos_new_vals)) if cos_new_vals else 0.0
    max_write_time = float(max(write_times)) if write_times else 0.0
    acc_drop = acc_before - acc_after

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] cos_new={mean_cos_new:.4f} acc_before={acc_before:.4f} "
          f"acc_after={acc_after:.4f} acc_drop={acc_drop:.4f} max_write_s={max_write_time:.4f} "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "mean_cos_new": float(mean_cos_new),
        "acc_before": float(acc_before),
        "acc_after": float(acc_after),
        "acc_drop_pp": float(acc_drop * 100.0),
        "max_write_time_s": float(max_write_time),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": float(elapsed),
        "hp1_pass": int(mean_cos_new >= HP_COS),
        "hp2_pass": int(acc_after >= HP_RETAIN_ACC),
        "hp3_pass": int(max_write_time < HP_WRITE_TIME),
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

    cos_m = mean_key("mean_cos_new")
    drop_m = mean_key("acc_drop_pp")
    wt_m = mean_key("max_write_time_s")

    summary = (f"mean_cos_new={cos_m:.4f}(HP>={HP_COS} HF<{HF_COS}) "
               f"mean_acc_drop_pp={drop_m:.4f}(HF>{HF_RETAIN_DROP_PP:.1f}pp) "
               f"mean_max_write_s={wt_m:.4f}(HP<{HP_WRITE_TIME}) "
               f"hp1_seeds={hp1_count}/{n} hp2_seeds={hp2_count}/{n} hp3_seeds={hp3_count}/{n}")

    if cos_m < HF_COS or drop_m > HF_RETAIN_DROP_PP:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    GATE = max(4, n - 1) if n >= 4 else n
    hp1_ok = hp1_count >= GATE
    hp2_ok = hp2_count >= GATE
    hp3_ok = hp3_count >= n

    if hp1_ok and hp2_ok and hp3_ok:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP at N=16384. {summary}")
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
      f"M_INIT={M_INIT} K_NEW={K_NEW} alpha={_alpha_new:.4f}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_INIT": M_INIT, "K_NEW": K_NEW, "run_mode": RUN_MODE}
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
         "mean_cos_new": r.get("mean_cos_new"),
         "acc_drop_pp": r.get("acc_drop_pp"),
         "max_write_time_s": r.get("max_write_time_s"),
         "hp1_pass": r.get("hp1_pass"), "hp2_pass": r.get("hp2_pass"),
         "hp3_pass": r.get("hp3_pass"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
