"""
pp48_nkt_depth_13_v1_n4096 -- PP-48 NKT negative-knowledge tree at depth-13 at N=4096.

Extends depth-11 (in queue) to depth-13. Tests NKT depth ceiling.
  Total binary tree at depth-13: 2^13 - 1 = 8191 nodes (too large for sub-capacity).
  Same sampled-leaf design as depth-11: BRANCH=2, sample K_FORBIDDEN=100 leaves.
  alpha_total = (10 pos + 100 forbidden) / 4096 = 0.027. Well sub-capacity.

  Tree construction at depth-13: branching from root to leaves requires 13 recursion levels.
  Each leaf at depth-13 = product of 13 context Hadamard bindings from root.
  Test: does substrate still repel depth-13 leaves with the same anti-Hebbian inhibition?

PRE-REGISTERED BANDS:
  HP: pos_retrieval_rate >= 0.75 AND nkt_repulsion_rate >= 0.65.
  HARD-FAIL: pos_retrieval_rate < 0.40 OR nkt_repulsion_rate < 0.30.
  MIDDLE: 1/2 conditions.
  Calibration: depth-11 used same design; bands unchanged from depth-11.

FORMULA SELF-TESTS:
  1. BRANCH=2, depth=13 total tree: 2^13 - 1 = 8191.
     [INPUT: B=2, D=13] [EXPECTED: total = 8191]
  2. alpha_total check: (K_POS + K_FORBIDDEN) / N < 0.138.
     [INPUT: K_POS=10, K_FORBIDDEN=100, N=4096] [EXPECTED: 110/4096=0.027 < 0.138]
  3. GPU memory > 0 after Xi alloc.

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: seed checkpoints keyed with run_mode + NKT_DEPTH.
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

ANCHOR_NAME = "pp48_nkt_depth_13_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NKT_DEPTH = 13
BRANCH = 2
TOTAL_NKT_FULL = (BRANCH ** NKT_DEPTH - 1) // (BRANCH - 1)  # 2^13 - 1 = 8191
assert TOTAL_NKT_FULL == 8191, f"TOTAL_NKT formula: got {TOTAL_NKT_FULL}, expected 8191"

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5
ALPHA_C = 0.138

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    K_POS = 5
    K_FORBIDDEN = 20
    N_TEST = 3
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    K_POS = 10
    K_FORBIDDEN = 100
    N_TEST = 10

_alpha_total = (K_POS + K_FORBIDDEN) / N
assert _alpha_total < ALPHA_C, (
    f"alpha_total={_alpha_total:.4f} >= alpha_c={ALPHA_C}: "
    f"K_POS={K_POS} + K_FORBIDDEN={K_FORBIDDEN} = {K_POS+K_FORBIDDEN} patterns at N={N}")

HP_POS = 0.75
HP_NKT_REP = 0.65
HF_POS = 0.40
HF_NKT_REP = 0.30


def build_nkt_tree_sample(n_dim: int, gen: torch.Generator, k_sample: int) -> List[torch.Tensor]:
    """Build NKT tree to depth NKT_DEPTH and return K_SAMPLE leaves."""
    patterns = []
    root = (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)
    patterns.append(root)
    prev_level = [root]
    for lvl in range(1, NKT_DEPTH):
        curr_level = []
        for parent in prev_level:
            for child_idx in range(BRANCH):
                ctx = (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)
                child = parent * ctx
                curr_level.append(child)
        patterns.extend(curr_level)
        prev_level = curr_level
    # Return sampled leaves from the deepest level only
    leaves = prev_level  # 2^(NKT_DEPTH-1) leaves at depth 13
    return leaves[:k_sample]


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def _instrumentation_selftest():
    total = sum(BRANCH ** d for d in range(NKT_DEPTH))
    assert total == TOTAL_NKT_FULL, f"NKT count: {total} != {TOTAL_NKT_FULL}"

    alpha_t = (K_POS + K_FORBIDDEN) / N
    assert alpha_t < ALPHA_C, f"alpha_total={alpha_t:.4f} >= alpha_c={ALPHA_C}"

    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy

    print(f"[selftest] PASS: total_tree={TOTAL_NKT_FULL}, capacity_ok alpha={alpha_t:.4f}, "
          f"gpu_mem_ok depth={NKT_DEPTH} K_POS={K_POS} K_FORBIDDEN={K_FORBIDDEN}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    Xi_A = bsc(K_POS, n_dim)
    sampled_leaves = build_nkt_tree_sample(n_dim, gen, K_FORBIDDEN)
    Xi_B = torch.stack(sampled_leaves)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi alloc: {mem_gb:.3f} GB "
          f"K_pos={K_POS} K_forbidden={K_FORBIDDEN}", flush=True)

    def signed_retrieve(state, n_steps=N_RETRIEVE_STEPS):
        for _ in range(n_steps):
            ov_A = Xi_A @ state
            ov_B = Xi_B @ state
            h = (Xi_A.t() @ ov_A - Xi_B.t() @ ov_B) / n_dim
            state = torch.sign(h)
            state[state == 0] = 1.0
        return state

    pos_ok = 0
    for q in range(min(N_TEST, K_POS)):
        xi_true = Xi_A[q]
        probe = xi_true.clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip] *= -1.0
        retrieved = signed_retrieve(probe)
        if cosine_sim_gpu(retrieved, xi_true) >= 0.5:
            pos_ok += 1
    pos_rate = pos_ok / max(N_TEST, 1)

    nkt_ok = 0
    n_rep_tests = min(N_TEST, K_FORBIDDEN)
    for i in range(n_rep_tests):
        leaf = Xi_B[i]
        probe = leaf.clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip] *= -1.0
        retrieved = signed_retrieve(probe)
        if cosine_sim_gpu(retrieved, leaf) < -0.2:
            nkt_ok += 1
    nkt_rep_rate = nkt_ok / max(n_rep_tests, 1)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] pos_rate={pos_rate:.4f}(HP>={HP_POS}) "
          f"nkt_rep_rate={nkt_rep_rate:.4f}(HP>={HP_NKT_REP}) "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "K_pos": K_POS, "K_forbidden": K_FORBIDDEN,
        "pos_retrieval_rate": float(pos_rate),
        "nkt_repulsion_rate": float(nkt_rep_rate),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    pos = mean_key("pos_retrieval_rate")
    nkt = mean_key("nkt_repulsion_rate")

    summary = (f"pos_rate={pos:.4f}(HP>={HP_POS} HF<{HF_POS}) "
               f"nkt_rep={nkt:.4f}(HP>={HP_NKT_REP} HF<{HF_NKT_REP}) "
               f"NKT_total_tree={TOTAL_NKT_FULL} K_FORBIDDEN_sample={K_FORBIDDEN} "
               f"depth={NKT_DEPTH} K_POS={K_POS} n_seeds={len(results)}")

    if pos < HF_POS or nkt < HF_NKT_REP:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = pos >= HP_POS
    hp2 = nkt >= HP_NKT_REP

    if hp1 and hp2:
        return ("HARD_PASS", f"HARD_PASS: both HP at NKT depth-13 sampled-leaves. {summary}")
    if hp1 or hp2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 1/2 HP. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: 0/2 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"NKT_depth={NKT_DEPTH} K_FORBIDDEN={K_FORBIDDEN} K_POS={K_POS} "
      f"total_tree={TOTAL_NKT_FULL}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "NKT_DEPTH": NKT_DEPTH, "K_FORBIDDEN": K_FORBIDDEN, "run_mode": RUN_MODE}
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
    "N": N, "NKT_DEPTH": NKT_DEPTH, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "pos_retrieval_rate": r.get("pos_retrieval_rate"),
         "nkt_repulsion_rate": r.get("nkt_repulsion_rate"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
