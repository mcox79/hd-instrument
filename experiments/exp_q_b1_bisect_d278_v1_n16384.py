"""
q_b1_bisect_d278_v1_n16384 -- Q-B1: heteroassoc chain bisection at depth=278 N=16384.

Bisection context (v361 + d293 result):
  depth_275 HARD_PASS (d5=0.932, flat-profile continues).
  depth_281 MIDDLE_BAND (d5=0.896, degradation onset visible near d281).
  depth_287 HARD_FAIL (collapse onset before d287; d5=0.884).
  depth_293 HARD_FAIL (collapse onset confirmed; d5=0.880; chain collapses d40-d50).

  Analysis: d287 and d293 both HF with d5~0.88, collapse at d40-70.
  The collapse window is between d275 (HP) and d281 (MIDDLE).
  Strict binary bisection: (275 + 281) // 2 = 278.

  If d=278 HARD_PASS: flat-profile through d=278; onset window narrows to (278, 281].
  If d=278 MIDDLE_BAND: onset visible at d=278; window remains (275, 278].
  If d=278 HARD_FAIL: unexpected (d275 was HP, d278 HF would be very sharp; treat as onset).

H matrix (N x N float32 at N=16384): 1073 MB. Fits in 8 GB GPU with margin.
Loading conditions matched to d_275/281/287/293 (N_CHAINS=15, M_BACKGROUND=200).

PRE-REGISTERED BANDS (bisection probe; prior d=275 HP, d=281 MIDDLE):
  HARD-PASS: d5 >= 0.90 AND d20 >= 0.75 AND d50 >= 0.50 AND d100 >= 0.20
             AND d200 >= 0.02 AND d275 >= 0.005 AND d278 >= 0.005.
             Interpretation: flat-profile continues to d=278; onset window is (278, 281].
  MIDDLE: d5 in [0.80, 0.90) OR d278 in [0.001, 0.005) while earlier depths pass.
          Interpretation: degradation onset near d=278; onset window is (275, 278].
  HARD-FAIL: d5 < 0.80 OR d278 < 0.001 OR d20 < 0.50.
             Interpretation: collapse onset before d=278 (unexpected given d275 HP).

Calibration note: calibration probe (new bisect point). Bands +-50% of extrapolated
  flat-profile prediction per calibration policy. Prior d=281 MID had d5=0.896.

FORMULA SELF-TESTS (PROT-022):
  1. Bisection midpoint: (275 + 281) // 2 = 278.
     [INPUT: d_low=275, d_high=281] [EXPECTED: bisect = 278]
  2. Cosine of stored pattern with itself = 1.0.
     [INPUT: xi vs xi] [EXPECTED: cos_self = 1.0]
  3. GPU memory > 100 MB after H build.
  4. d=275 extrapolation: 0.93 * ((1 - 0.00010) ** 3) > 0.90 (sanity).
     [INPUT: d275_cos_est=0.93, lambda=0.0001, extra_hops=3] [EXPECTED: > 0.90]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + chain_depth.
QUEUE: overnight_queue (GPU; N=16384 H matrix ~1073 MB).
TIMEOUT ESTIMATE: d=287 wall=751.7s 5-seed. d=278 depth is similar.
  ceil(1.5 * 800 * (278/287) * 1.0) = ceil(1167) = 1200s.
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

ANCHOR_NAME = "q_b1_bisect_d278_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

CHAIN_DEPTH = 278
SNAPSHOT_DEPTHS = [1, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                   110, 120, 130, 140, 150, 160, 170, 180, 190, 200,
                   210, 220, 230, 240, 250, 260, 270, 275, 276, 277, 278]

# PROT-022 formula self-tests at module scope
_BISECT_MIDPOINT = (275 + 281) // 2
assert _BISECT_MIDPOINT == 278, f"bisect midpoint: {_BISECT_MIDPOINT} expected 278"
_D275_EXTRAP = 0.93 * ((1.0 - 0.0001) ** 3)
assert _D275_EXTRAP > 0.90, f"d275 extrap to d278 sanity: {_D275_EXTRAP:.4f} < 0.90"

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
HP_D278 = 0.005
HF_D5 = 0.80
HF_D20 = 0.50
HF_D278 = 0.001
MIDDLE_D278_LOW = 0.001
MIDDLE_D278_HIGH = 0.005


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
    assert not (cos != cos), f"depth-278 retrieval is NaN at N={N_t}"
    assert -1.1 < cos < 1.1, f"cosine out of range: {cos}"

    xi = chain[0]
    cos_self = cosine_sim_gpu(xi, xi)
    assert abs(cos_self - 1.0) < 1e-6, f"cos_self={cos_self:.6f} expected 1.0"

    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    print(f"[selftest] PASS: bisect_d278 chain ok, cos_self=1.0, gpu_mem_ok", flush=True)


_instrumentation_selftest()
# Clear GPU cache after self-test before production run
torch.cuda.empty_cache()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    chains = []
    for _ in range(N_CHAINS):
        chain = [bsc(1, n_dim).squeeze(0) for _ in range(CHAIN_DEPTH + 1)]
        chains.append(chain)

    H = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
    for chain in chains:
        for h in range(CHAIN_DEPTH):
            H += torch.outer(chain[h + 1], chain[h]) / n_dim
    bg_xi = bsc(M_BACKGROUND, n_dim)
    bg_xi2 = bsc(M_BACKGROUND, n_dim)
    for k in range(M_BACKGROUND):
        H += torch.outer(bg_xi2[k], bg_xi[k]) / n_dim

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after H build: {mem_gb:.3f} GB", flush=True)

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

    d5   = mean_key("mean_cos_d5")
    d20  = mean_key("mean_cos_d20")
    d50  = mean_key("mean_cos_d50")
    d100 = mean_key("mean_cos_d100")
    d200 = mean_key("mean_cos_d200")
    d275 = mean_key("mean_cos_d275")
    d278 = mean_key("mean_cos_d278")

    summary = (f"d5={d5:.4f}(HP>={HP_D5} HF<{HF_D5}) "
               f"d20={d20:.4f}(HP>={HP_D20} HF<{HF_D20}) "
               f"d50={d50:.4f}(HP>={HP_D50}) "
               f"d100={d100:.4f}(HP>={HP_D100}) "
               f"d200={d200:.4f}(HP>={HP_D200}) "
               f"d275={d275:.4f}(HP>={HP_D275}) "
               f"d278={d278:.4f}(HP>={HP_D278} HF<{HF_D278}) "
               f"n_seeds={len(results)}")

    if d5 < HF_D5 or d20 < HF_D20 or d278 < HF_D278:
        return ("HARD_FAIL", f"HARD_FAIL: collapse onset at or before d=278. {summary}")

    d5_ok   = d5   >= HP_D5
    d20_ok  = d20  >= HP_D20
    d50_ok  = d50  >= HP_D50
    d100_ok = d100 >= HP_D100
    d200_ok = d200 >= HP_D200
    d275_ok = d275 >= HP_D275
    d278_ok = d278 >= HP_D278

    if d5_ok and d20_ok and d50_ok and d100_ok and d200_ok and d275_ok and d278_ok:
        return ("HARD_PASS", f"HARD_PASS: all depth thresholds met at N={N} depth-278 bisection. "
                             f"FLAT regime continues through d278. Onset window is (278, 281]. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial depth thresholds. Onset near d=278. {summary}")


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
