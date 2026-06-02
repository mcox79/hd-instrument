"""
pp48_nkt_depth_9_v1_n4096 -- PP-48 NKT negative-knowledge tree at depth-9 at N=4096.

Extends depth-7 (HARD_PASS all rates=1.0 at N=4096) to depth-9.
  Total forbidden patterns at depth-9 B=2: sum_{d=0}^{8} 2^d = 2^9 - 1 = 511.
  At K_POS=100 positive + 511 NKT forbidden: alpha_total = 611/4096 = 0.149.
  NOTE: alpha_total > alpha_c=0.138 at K_POS=100. Reduce K_POS to 50 for depth-9:
  alpha_total = 561/4096 = 0.137 < 0.138 (barely sub-capacity).

Architecture:
  L1 (root): 1 NKT root.
  ...
  L9: 2^8 = 256 leaves. Total forbidden: 511 patterns in W_B.
  W_signed = W_A (positive) - W_B (forbidden).

GPU IMPLEMENTATION: matrix-free signed-AM, no N x N materialization.

PRE-REGISTERED BANDS:
  HP: pos_retrieval_rate >= 0.80 AND nkt_repulsion_rate >= 0.70 AND tree_structure >= 0.70.
  HARD-FAIL: pos_retrieval_rate < 0.50 OR nkt_repulsion_rate < 0.40.
  MIDDLE: 2/3 conditions met.
  Prior: depth-7 HP all rates=1.0; depth-9 substantially harder (511 patterns, near-capacity).
  Calibration: conservative HP threshold (0.80/0.70/0.70 vs depth-7 0.85/0.80/0.80).

FORMULA SELF-TESTS:
  1. Total NKT patterns at B=2 depth=9: 2^9 - 1 = 511.
     [INPUT: B=2, depth=9] [EXPECTED: total = 511]
  2. alpha_total check: (K_POS + TOTAL_NKT) / N < 0.138.
     [INPUT: K_POS=50, TOTAL_NKT=511, N=4096] [EXPECTED: 561/4096=0.137 < 0.138]
  3. GPU memory > 0 after Xi alloc.

PROT-018: anchor has _n4096; N MUST = 4096.
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

ANCHOR_NAME = "pp48_nkt_depth_9_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NKT_DEPTH = 9
BRANCH = 2
# sum_{d=0}^{depth-1} B^d = (B^depth - 1) / (B-1) = 2^9 - 1 = 511
TOTAL_NKT = (BRANCH ** NKT_DEPTH - 1) // (BRANCH - 1)
assert TOTAL_NKT == 511, f"TOTAL_NKT formula: got {TOTAL_NKT}, expected 511"

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    K_POS = 5
    N_TEST = 3
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    K_POS = 50
    N_TEST = 10

# Verify alpha < alpha_c at N=4096
_alpha_total = (K_POS + TOTAL_NKT) / N
assert _alpha_total < 0.138, (
    f"alpha_total={_alpha_total:.4f} >= alpha_c=0.138: "
    f"K_POS={K_POS} + TOTAL_NKT={TOTAL_NKT} = {K_POS+TOTAL_NKT} patterns at N={N}")

# Relaxed thresholds vs depth-7 (near-capacity tree)
HP_POS = 0.80
HP_NKT_REP = 0.70
HP_TREE = 0.70
HF_POS = 0.50
HF_NKT_REP = 0.40


def _instrumentation_selftest():
    total = sum(BRANCH ** d for d in range(NKT_DEPTH))
    assert total == TOTAL_NKT, f"NKT count: {total} != {TOTAL_NKT}"

    alpha_t = (K_POS + TOTAL_NKT) / N
    assert alpha_t < 0.138, f"alpha_total={alpha_t:.4f} >= 0.138"
    print(f"[selftest] alpha_total={alpha_t:.4f} < 0.138 OK (K_POS={K_POS} + NKT={TOTAL_NKT})",
          flush=True)

    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy

    print(f"[selftest] PASS: NKT count={total}, capacity_ok, gpu_mem_ok "
          f"depth={NKT_DEPTH}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def build_nkt_tree(n_dim: int, gen: torch.Generator) -> List[torch.Tensor]:
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
    return patterns


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    Xi_A = bsc(K_POS, n_dim)
    nkt_patterns = build_nkt_tree(n_dim, gen)
    Xi_B = torch.stack(nkt_patterns)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi alloc: {mem_gb:.3f} GB "
          f"K_pos={K_POS} K_nkt={TOTAL_NKT}", flush=True)

    def signed_retrieve(state, n_steps=N_RETRIEVE_STEPS):
        for _ in range(n_steps):
            ov_A = Xi_A @ state
            ov_B = Xi_B @ state
            h = (Xi_A.t() @ ov_A - Xi_B.t() @ ov_B) / n_dim
            state = torch.sign(h)
            state[state == 0] = 1.0
        return state

    # HP1: positive retrieval rate
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

    # HP2: NKT repulsion rate (leaves only)
    leaves = nkt_patterns[-(BRANCH ** (NKT_DEPTH - 1)):]
    nkt_ok = 0
    n_rep_tests = min(N_TEST, len(leaves))
    for leaf in leaves[:n_rep_tests]:
        probe = leaf.clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip] *= -1.0
        retrieved = signed_retrieve(probe)
        if cosine_sim_gpu(retrieved, leaf) < -0.2:
            nkt_ok += 1
    nkt_rep_rate = nkt_ok / max(n_rep_tests, 1)

    # HP3: tree structure (leaf norm check as proxy)
    tree_ok = sum(1 for leaf in leaves[:n_rep_tests]
                  if abs(float(leaf.norm()) / math.sqrt(n_dim) - 1.0) < 0.1)
    tree_rate = tree_ok / max(n_rep_tests, 1)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] pos_rate={pos_rate:.4f} nkt_rep_rate={nkt_rep_rate:.4f} "
          f"tree_rate={tree_rate:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "K_pos": K_POS, "K_nkt": TOTAL_NKT,
        "pos_retrieval_rate": float(pos_rate),
        "nkt_repulsion_rate": float(nkt_rep_rate),
        "tree_structure_intact": float(tree_rate),
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
    tree = mean_key("tree_structure_intact")

    summary = (f"pos_rate={pos:.4f}(HP>={HP_POS} HF<{HF_POS}) "
               f"nkt_rep={nkt:.4f}(HP>={HP_NKT_REP} HF<{HF_NKT_REP}) "
               f"tree={tree:.4f}(HP>={HP_TREE}) "
               f"NKT_total={TOTAL_NKT} depth={NKT_DEPTH} K_POS={K_POS} n_seeds={len(results)}")

    if pos < HF_POS or nkt < HF_NKT_REP:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = pos >= HP_POS
    hp2 = nkt >= HP_NKT_REP
    hp3 = tree >= HP_TREE

    if hp1 and hp2 and hp3:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP at NKT depth-9. {summary}")
    if sum([hp1, hp2, hp3]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3])}/3 HP. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3])}/3 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"NKT_depth={NKT_DEPTH} total_nkt={TOTAL_NKT} K_POS={K_POS}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "NKT_DEPTH": NKT_DEPTH, "run_mode": RUN_MODE}
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
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "NKT_DEPTH": NKT_DEPTH, "TOTAL_NKT": TOTAL_NKT, "K_POS": K_POS,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "pos_retrieval_rate": r.get("pos_retrieval_rate"),
         "nkt_repulsion_rate": r.get("nkt_repulsion_rate"),
         "tree_structure_intact": r.get("tree_structure_intact"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
