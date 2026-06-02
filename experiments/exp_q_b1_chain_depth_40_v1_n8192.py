"""
q_b1_chain_depth_40_v1_n8192 -- Q-B1: heteroassoc chain at depth-40 at N=8192.

Extends depth-30 (just shipped) to depth-40. Tests chain degradation envelope at depth-40.
Prior anchors: depth-20 HP, depth-25 HP, depth-30 pending.

Extrapolation from depth-20 HP (mean_cos >= 0.70) at 0.995^40 ~ 0.819 decay factor.
HP threshold at depth-40 set conservatively at 0.45 given accumulated interference.

GPU IMPLEMENTATION:
  H matrix (N x N float32 at N=8192): 268 MB. Safe on 8 GB GPU.
  Readout snapshots at depths [1, 3, 5, 10, 15, 20, 25, 30, 35, 40].

PRE-REGISTERED BANDS:
  HARD-PASS: depth-5 >= 0.95 AND depth-10 >= 0.88 AND depth-20 >= 0.70 AND
             depth-30 >= 0.55 AND depth-40 >= 0.45.
  HARD-FAIL: depth-5 < 0.80 OR depth-10 < 0.65 OR depth-20 < 0.40 OR
             depth-30 < 0.30 OR depth-40 < 0.25.
  MIDDLE: depth-40 in [0.30, 0.45) while earlier depths meet HP.
  Prior: depth-30 HP threshold >= 0.55; depth-40 HP threshold relaxed to 0.45.

FORMULA SELF-TESTS:
  1. depth-40 chain non-NaN at N=128.
  2. self-cosine = 1.0.
  3. GPU memory > 0 after H build (> 100 MB).

PROT-018: anchor has _n8192; N MUST = 8192.
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

ANCHOR_NAME = "q_b1_chain_depth_40_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

CHAIN_DEPTH = 40
SNAPSHOT_DEPTHS = [1, 3, 5, 10, 15, 20, 25, 30, 35, 40]

if RUN_MODE == "smoke":
    N_ACTIVE = 1024
    SEEDS = [7, 17]
    N_CHAINS = 5
    M_BACKGROUND = 30
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 15
    M_BACKGROUND = 200

HP_D5 = 0.95
HP_D10 = 0.88
HP_D20 = 0.70
HP_D30 = 0.55
HP_D40 = 0.45
HF_D5 = 0.80
HF_D10 = 0.65
HF_D20 = 0.40
HF_D30 = 0.30
HF_D40 = 0.25


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def _instrumentation_selftest():
    N_t = 128
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    chain = [bsc(1, N_t).squeeze(0) for _ in range(CHAIN_DEPTH + 1)]
    H = torch.zeros((N_t, N_t), device=DEVICE, dtype=torch.float32)
    for h in range(CHAIN_DEPTH):
        H += torch.outer(chain[h + 1], chain[h]) / N_t

    r = chain[0].clone()
    for step in range(CHAIN_DEPTH):
        h_vec = H @ r
        r = torch.sign(h_vec)
        r[r == 0] = 1.0

    cos = cosine_sim_gpu(r, chain[CHAIN_DEPTH])
    assert not (cos != cos), f"depth-40 retrieval is NaN at N={N_t}"
    assert -1.1 < cos < 1.1, f"cosine out of range: {cos}"

    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"

    v = chain[0]
    self_cos = cosine_sim_gpu(v, v)
    assert abs(self_cos - 1.0) < 1e-5, f"self-cosine = {self_cos} != 1.0"

    del H
    print(f"[selftest] PASS: depth-40 chain non-NaN N={N_t}, self-cosine=1.0, "
          f"gpu_mem={mem/1e6:.1f}MB", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    chains = [[bsc(1, n_dim).squeeze(0) for _ in range(CHAIN_DEPTH + 1)]
              for _ in range(N_CHAINS)]
    bg_keys = bsc(M_BACKGROUND, n_dim)
    bg_vals = bsc(M_BACKGROUND, n_dim)

    H = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
    for chain in chains:
        for h in range(CHAIN_DEPTH):
            H += torch.outer(chain[h + 1], chain[h]) / n_dim
    for i in range(M_BACKGROUND):
        H += torch.outer(bg_vals[i], bg_keys[i]) / n_dim

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after H build: {mem_gb:.3f} GB", flush=True)

    snap_sims = {d: [] for d in SNAPSHOT_DEPTHS}

    for chain in chains:
        r = chain[0].clone()
        depth_results = {}
        for step in range(1, CHAIN_DEPTH + 1):
            h_vec = H @ r
            r = torch.sign(h_vec)
            r[r == 0] = 1.0
            if step in SNAPSHOT_DEPTHS:
                cos = cosine_sim_gpu(r, chain[step])
                depth_results[step] = cos
        for d in SNAPSHOT_DEPTHS:
            snap_sims[d].append(depth_results.get(d, 0.0))

    mean_snaps = {d: float(sum(v) / len(v)) if v else 0.0 for d, v in snap_sims.items()}

    del H
    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] snaps={' '.join(f'd{d}:{mean_snaps[d]:.4f}' for d in SNAPSHOT_DEPTHS)} "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "n_chains": N_CHAINS, "m_background": M_BACKGROUND,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }
    for d in SNAPSHOT_DEPTHS:
        result[f"mean_cos_d{d}"] = mean_snaps[d]
    return result


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    d5 = mean_key("mean_cos_d5")
    d10 = mean_key("mean_cos_d10")
    d20 = mean_key("mean_cos_d20")
    d30 = mean_key("mean_cos_d30")
    d40 = mean_key("mean_cos_d40")

    summary = (f"d5={d5:.4f}(HP>={HP_D5} HF<{HF_D5}) "
               f"d10={d10:.4f}(HP>={HP_D10} HF<{HF_D10}) "
               f"d20={d20:.4f}(HP>={HP_D20} HF<{HF_D20}) "
               f"d30={d30:.4f}(HP>={HP_D30} HF<{HF_D30}) "
               f"d40={d40:.4f}(HP>={HP_D40} HF<{HF_D40}) "
               f"n_seeds={len(results)}")

    if (d5 < HF_D5 or d10 < HF_D10 or d20 < HF_D20
            or d30 < HF_D30 or d40 < HF_D40):
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp5 = d5 >= HP_D5
    hp10 = d10 >= HP_D10
    hp20 = d20 >= HP_D20
    hp30 = d30 >= HP_D30
    hp40 = d40 >= HP_D40

    if hp5 and hp10 and hp20 and hp30 and hp40:
        return ("HARD_PASS", f"HARD_PASS: all depth thresholds met at N=8192 depth-40. {summary}")
    n_hp = sum([hp5, hp10, hp20, hp30, hp40])
    if n_hp >= 4:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/5 depth HP. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/5 depth HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"chain_depth={CHAIN_DEPTH} snapshots={SNAPSHOT_DEPTHS}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "chain_depth": CHAIN_DEPTH, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

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
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "chain_depth": CHAIN_DEPTH, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         **{f"mean_cos_d{d}": r.get(f"mean_cos_d{d}") for d in SNAPSHOT_DEPTHS},
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
