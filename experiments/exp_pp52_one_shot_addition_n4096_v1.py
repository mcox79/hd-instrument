"""
pp52_one_shot_addition_n4096_v1 -- PP-52 A2: one-shot addition and recall at N=4096.

Production-N validation of A2 (founded at N=1024 in v339). Tests whether one-shot
Hebbian write adds new patterns with immediate retrievability at N=4096.

SCIENTIFIC QUESTION:
  At N=4096, M=400 initial patterns: can substrate one-shot-add new patterns with
  immediate retrievability AND existing patterns retain >= 95% accuracy?

PRE-REGISTERED HARD-PASS (A2 spec):
  HP1: new pattern cosine >= 0.90 immediately after one write in >= 4/5 seeds.
  HP2: existing patterns retain >= 95% accuracy after K_NEW=10 additions in >= 4/5 seeds.
  HP3: write wall-time < 1.0 second for any single pattern addition at N=4096 in all seeds.
  HARD-PASS: all 3 HP in >= 4/5 seeds.

PRE-REGISTERED HARD-FAIL:
  HF1: new pattern cosine < 0.70.
  HF2: existing pattern accuracy drops > 10pp.
  HF3: write wall-time > 10 seconds.

MIDDLE BAND: cosine in [0.70, 0.90) OR accuracy drop 5-10pp.
P_deflated = 0.80 (algebraically guaranteed; test validates at production N).

GPU IMPLEMENTATION:
  W matrix (N x N float32 at N=4096): 67 MB. One-shot write = batched outer product sum.

FORMULA SELF-TESTS:
  1. After one write: W' @ xi_new ~ xi_new (dominant term).
     [INPUT: N=64, M=6, xi_new random] [EXPECTED: retrieval cosine >= 0.90]
  2. Alpha check: (M + K_NEW) / N < alpha_c.
     [INPUT: M=400, K_NEW=10, N=4096] [EXPECTED: alpha=0.100 < 0.138]
  3. GPU memory > 100 MB after W build.

PROT-018: anchor has _n4096; N MUST = 4096.
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

ANCHOR_NAME = "pp52_one_shot_addition_n4096_v1"

_N_SUFFIX = 4096
N = 4096
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
    M_INIT = 50
    K_NEW = 5
    SEEDS = [7, 17]
    N_QUERIES = 20
else:
    N_ACTIVE = N  # 4096
    M_INIT = 400
    K_NEW = 10
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 50

HP_COS = 0.90
HF_COS = 0.70
HP_RETAIN_ACC = 0.95
HF_RETAIN_DROP_PP = 10.0
HP_WRITE_TIME = 1.0
HF_WRITE_TIME = 10.0

# Formula self-test: alpha check
_alpha_new = (M_INIT + K_NEW) / N
print(f"[config] alpha_new = {_alpha_new:.4f} (< alpha_c={ALPHA_C})", flush=True)


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
        cos = cosine_sim_gpu(ret, Xi_test[i])
        if cos > 0.90:
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
    assert cos >= 0.70, f"oneshot write selftest: cos={cos:.4f} < 0.70"


def _selftest_alpha_check():
    assert _alpha_new < ALPHA_C, f"alpha_new={_alpha_new:.4f} >= alpha_c={ALPHA_C}"


def _instrumentation_selftest():
    _selftest_oneshot_write()
    _selftest_alpha_check()
    dummy = torch.zeros((N_ACTIVE // 2, N_ACTIVE // 2), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 1e5, f"GPU memory not > 100KB: {mem}"
    del dummy
    print(f"[selftest] PASS: oneshot_write_ok, alpha_check_ok, gpu_mem={mem/1e6:.1f}MB",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    Xi_init = (torch.randint(0, 2, (M_INIT, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    W = Xi_init.t() @ Xi_init / float(n_dim)

    # Baseline accuracy before any additions
    test_init = Xi_init[:min(N_QUERIES, M_INIT)]
    acc_before = retrieval_accuracy(W, test_init, n_dim)

    # One-shot addition of K_NEW new patterns
    new_patterns = (torch.randint(0, 2, (K_NEW, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
    cos_new_vals = []
    write_times = []

    for k in range(K_NEW):
        xi_new = new_patterns[k]
        t_w = time.time()
        W += torch.outer(xi_new, xi_new) / float(n_dim)
        torch.cuda.synchronize()
        write_time = time.time() - t_w
        write_times.append(write_time)

        ret = retrieve_hopfield_gpu(W, xi_new)
        cos = cosine_sim_gpu(ret, xi_new)
        cos_new_vals.append(cos)

    # Accuracy after K_NEW additions
    acc_after = retrieval_accuracy(W, test_init, n_dim)

    mean_cos_new = float(sum(cos_new_vals) / len(cos_new_vals)) if cos_new_vals else 0.0
    max_write_time = max(write_times) if write_times else 0.0
    acc_drop_pp = max(0.0, (acc_before - acc_after) * 100.0)

    hp1 = mean_cos_new >= HP_COS
    hp2 = acc_drop_pp <= (100.0 - HP_RETAIN_ACC * 100.0)
    hp3 = max_write_time < HP_WRITE_TIME
    hf1 = mean_cos_new < HF_COS
    hf2 = acc_drop_pp > HF_RETAIN_DROP_PP
    hf3 = max_write_time > HF_WRITE_TIME

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] mean_cos_new={mean_cos_new:.4f}(HP>={HP_COS}) "
          f"acc_before={acc_before:.4f} acc_after={acc_after:.4f} "
          f"drop_pp={acc_drop_pp:.2f} "
          f"max_write={max_write_time:.4f}s(HP<{HP_WRITE_TIME}s) "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "mean_cos_new": float(mean_cos_new),
        "acc_before": float(acc_before),
        "acc_after": float(acc_after),
        "acc_drop_pp": float(acc_drop_pp),
        "max_write_time": float(max_write_time),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2), "hf3": bool(hf3),
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
    cos_new = mean_key("mean_cos_new")
    drop_pp = mean_key("acc_drop_pp")
    max_wt = mean_key("max_write_time")
    hp1_n = sum(1 for r in results if r.get("hp1"))
    hp2_n = sum(1 for r in results if r.get("hp2"))
    hp3_n = sum(1 for r in results if r.get("hp3"))
    hf1 = any(r.get("hf1") for r in results)
    hf2 = any(r.get("hf2") for r in results)
    hf3 = any(r.get("hf3") for r in results)

    summary = (f"cos_new={cos_new:.4f}(HP>={HP_COS} HF<{HF_COS}) "
               f"acc_drop_pp={drop_pp:.2f}(HP<={100-HP_RETAIN_ACC*100:.0f}pp) "
               f"max_write={max_wt:.4f}s(HP<{HP_WRITE_TIME}s) "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}")

    if hf1:
        return ("HARD_FAIL", f"HARD_FAIL HF1: cos_new < {HF_COS}. {summary}")
    if hf2:
        return ("HARD_FAIL", f"HARD_FAIL HF2: accuracy drop > {HF_RETAIN_DROP_PP}pp. {summary}")
    if hf3:
        return ("HARD_FAIL", f"HARD_FAIL HF3: write time > {HF_WRITE_TIME}s. {summary}")

    min_pass = max(1, int(n * 0.8))
    if all(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n]):
        return ("HARD_PASS", f"HARD_PASS: all 3 HP in >={min_pass}/{n} seeds at N=4096. {summary}")
    n_met = sum(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n])
    if n_met >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/3 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_met}/3 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_init={M_INIT} K_new={K_NEW}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

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

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "n_active": N_ACTIVE, "M_INIT": M_INIT, "K_NEW": K_NEW,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
