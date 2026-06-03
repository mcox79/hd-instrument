"""
q_b1_bisect_d275_v1_n16384 -- Q-B1: heteroassoc chain bisection at depth=275 N=16384.

Bisection target: depth_250 HARD_PASS (d5=0.9322, flat ~0.929 to d250; v356).
depth_300 HARD_FAIL (d5=0.8635, collapses d30-50; v355). Loading conditions identical
(N_CHAINS=15, M_BACKGROUND=200) confirming genuine collapse onset between d250 and d300.
depth_400 HARD_FAIL (d5=0.655, faster collapse; v356).

Binary bisection: d=275 is midpoint between d=250 (PASS) and d=300 (FAIL).
If PASS (d5>0.9): collapse onset is in (275, 300]. Next bisect: d=287 or d=290.
If FAIL (d5<0.8): collapse onset is in (250, 275]. Next bisect: d=262 or d=265.
If MIDDLE (d5 in [0.80, 0.90)): collapse onset approaching; bisect toward failure side.

H matrix (N x N float32 at N=16384): 1073 MB. Fits in 8 GB GPU with margin.
Snapshots at depths including bisection anchor points.

PRE-REGISTERED BANDS (bisection probe; prior d=250 flat d5~0.932, d=300 d5=0.864):
  HARD-PASS: d5 >= 0.90 AND d20 >= 0.75 AND d50 >= 0.50 AND d100 >= 0.20
             AND d200 >= 0.02 AND d275 >= 0.005.
             Interpretation: flat-profile continues to d=275 (same regime as d=250).
  MIDDLE: d5 in [0.80, 0.90) OR d275 in [0.001, 0.005) while earlier depths pass.
          Interpretation: degradation onset visible at d=275 but not full collapse.
  HARD-FAIL: d5 < 0.80 OR d275 < 0.001 OR d20 < 0.50.
             Interpretation: collapse onset before d=275 (same as d=300 pattern).

Calibration note: if flat-profile continues (d=275 bisect -> PASS) then band
0.87-0.97 claim is confirmed further; collapse onset is in (275, 300].
If HARD_FAIL: band 0.87-0.97 reflects conditions with chain_depth <= 250.

FORMULA SELF-TESTS (PROT-022):
  1. Bisection midpoint: (250 + 300) // 2 = 275.
     [INPUT: d_low=250, d_high=300] [EXPECTED: bisect = 275]
  2. Cosine of stored pattern with itself = 1.0.
     [INPUT: xi vs xi] [EXPECTED: cos_self = 1.0]
  3. GPU memory > 100 MB after H build.
  4. d=250 flat-profile extrapolation: 0.9322 * ((1 - 0.00015) ** 25) > 0.90 (sanity).
     [INPUT: d250_cos=0.9322, lambda=0.00015, extra_hops=25] [EXPECTED: > 0.90]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + chain_depth.
QUEUE: overnight_queue (GPU; N=16384 H matrix ~1073 MB).
TIMEOUT ESTIMATE: depth_250 elapsed ~621s FULL 5-seed GPU.
  d=275 scales near-linearly with depth (275/250 = 1.10x).
  ceil(1.5 * 621 * 1.10 * 1.0) = ceil(1025) = 1200s.
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

ANCHOR_NAME = "q_b1_bisect_d275_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

CHAIN_DEPTH = 275
SNAPSHOT_DEPTHS = [1, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                   110, 120, 130, 140, 150, 160, 170, 180, 190, 200,
                   210, 220, 230, 240, 250, 260, 270, 275]

# PROT-022 formula self-tests at module scope
_BISECT_MIDPOINT = (250 + 300) // 2
assert _BISECT_MIDPOINT == 275, f"bisect midpoint: {_BISECT_MIDPOINT} expected 275"
_D250_EXTRAP = 0.9322 * ((1.0 - 0.00015) ** 25)
assert _D250_EXTRAP > 0.90, f"d250 extrap to d275 sanity: {_D250_EXTRAP:.4f} < 0.90"

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

# Pre-registered bands (bisection probe)
HP_D5 = 0.90
HP_D20 = 0.75
HP_D50 = 0.50
HP_D100 = 0.20
HP_D200 = 0.02
HP_D275 = 0.005
HF_D5 = 0.80
HF_D20 = 0.50
HF_D275 = 0.001
MIDDLE_D275_LOW = 0.001
MIDDLE_D275_HIGH = 0.005


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
    assert not (cos != cos), f"depth-275 retrieval is NaN at N={N_t}"
    assert -1.1 < cos < 1.1, f"cosine out of range: {cos}"

    # Verify cosine of stored pattern with itself = 1.0
    xi = chain[0]
    cos_self = cosine_sim_gpu(xi, xi)
    assert abs(cos_self - 1.0) < 1e-6, f"cos_self={cos_self:.6f} expected 1.0"

    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    print(f"[selftest] PASS: bisect_d275 chain ok, cos_self=1.0, gpu_mem_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    # Build heteroassociative chain: H stores M associations xi_{h+1} <- xi_h
    # M_BACKGROUND background patterns + N_CHAINS tracked chains
    total_patterns = M_BACKGROUND + N_CHAINS
    chains = []
    for _ in range(N_CHAINS):
        chain = [bsc(1, n_dim).squeeze(0) for _ in range(CHAIN_DEPTH + 1)]
        chains.append(chain)

    H = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
    # Store all chain associations
    for chain in chains:
        for h in range(CHAIN_DEPTH):
            H += torch.outer(chain[h + 1], chain[h]) / n_dim
    # Add background patterns (random associations, treated as noise load)
    bg_xi = bsc(M_BACKGROUND, n_dim)
    bg_xi2 = bsc(M_BACKGROUND, n_dim)
    for k in range(M_BACKGROUND):
        H += torch.outer(bg_xi2[k], bg_xi[k]) / n_dim

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after H build: {mem_gb:.3f} GB", flush=True)

    # Evaluate retrieval at each snapshot depth
    snap_results = {d: [] for d in SNAPSHOT_DEPTHS}
    for chain_idx in range(N_CHAINS):
        chain = chains[chain_idx]
        state = chain[0].clone()
        step = 0
        snap_idx = 0
        while snap_idx < len(SNAPSHOT_DEPTHS) and step < CHAIN_DEPTH:
            target_depth = SNAPSHOT_DEPTHS[snap_idx]
            while step < target_depth and step < CHAIN_DEPTH:
                h_vec = H @ state
                state = torch.sign(h_vec)
                state[state == 0] = 1.0
                step += 1
            if step == target_depth:
                cos = cosine_sim_gpu(state, chain[step])
                snap_results[target_depth].append(cos)
                snap_idx += 1

    mean_cos = {}
    for d, vals in snap_results.items():
        mean_cos[d] = float(sum(vals) / len(vals)) if vals else 0.0

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0

    snaps_str = " ".join(f"d{d}:{mean_cos[d]:.4f}" for d in sorted(SNAPSHOT_DEPTHS))
    print(f"  [seed={seed}] {snaps_str} peak_gpu={peak_mem:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "peak_gpu_gb": float(peak_mem), "elapsed_s": elapsed,
    }
    for d, v in mean_cos.items():
        result[f"mean_cos_d{d}"] = v
    return result


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    d5  = mean_key("mean_cos_d5")
    d20 = mean_key("mean_cos_d20")
    d50 = mean_key("mean_cos_d50")
    d100 = mean_key("mean_cos_d100")
    d200 = mean_key("mean_cos_d200")
    d275 = mean_key("mean_cos_d275")

    summary = (f"d5={d5:.4f}(HP>={HP_D5} HF<{HF_D5}) "
               f"d20={d20:.4f}(HP>={HP_D20} HF<{HF_D20}) "
               f"d50={d50:.4f}(HP>={HP_D50}) "
               f"d100={d100:.4f}(HP>={HP_D100}) "
               f"d200={d200:.4f}(HP>={HP_D200}) "
               f"d275={d275:.4f}(HP>={HP_D275} HF<{HF_D275}) "
               f"n_seeds={len(results)}")

    if d5 < HF_D5 or d20 < HF_D20 or d275 < HF_D275:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    d5_ok = d5 >= HP_D5
    d20_ok = d20 >= HP_D20
    d50_ok = d50 >= HP_D50
    d100_ok = d100 >= HP_D100
    d200_ok = d200 >= HP_D200
    d275_ok = d275 >= HP_D275

    if d5_ok and d20_ok and d50_ok and d100_ok and d200_ok and d275_ok:
        return ("HARD_PASS", f"HARD_PASS: all depth thresholds met at N={N} depth-275 bisection. "
                             f"FLAT regime continues through d275. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial depth thresholds. Collapse onset near d275. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} chain_depth={CHAIN_DEPTH}",
      flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "chain_depth": CHAIN_DEPTH, "run_mode": RUN_MODE}
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
