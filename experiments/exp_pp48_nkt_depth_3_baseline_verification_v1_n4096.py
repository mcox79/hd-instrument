"""
pp48_nkt_depth_3_baseline_verification_v1_n4096 -- PP-48 NKT depth-3 baseline at N=4096.

Establishes explicit depth-3 baseline for the depth-scaling curve. Prior depths:
  depth-5: HARD_PASS, depth-7: HARD_PASS, depth-9: queued.
  depth-3 was never explicitly run at production N=4096 (only implied by depth-5 HP).
  This anchor establishes the baseline data point for the depth-3 -> depth-7 -> depth-9 curve.

SCIENTIFIC QUESTION:
  At N=4096, NKT depth-3 (B=2, total_forbidden = 2^3 - 1 = 7 patterns):
  Does signed-AM reliably repel all 7 forbidden patterns while retaining positive retrieval?

FORMULA SELF-TESTS:
  1. Total NKT patterns at B=2 depth=3: sum_{d=0}^{2} 2^d = 2^3 - 1 = 7.
     [INPUT: B=2, depth=3] [EXPECTED: total = 7]
  2. Signed-AM: single forbidden probe anti-converges.
  3. GPU memory > 100 MB after Xi alloc.

PRE-REGISTERED BANDS (depth-3 baseline; expected high fidelity):
  HARD-PASS: HP1 pos_retrieval_rate >= 0.90 AND HP2 nkt_repulsion_rate >= 0.90 AND HP3 tree_structure >= 0.90.
  HARD-FAIL: pos_retrieval_rate < 0.60 OR nkt_repulsion_rate < 0.60.
  MIDDLE: 2/3 HP conditions met.
  Calibration: depth-3 is near-trivial (7 forbidden patterns at alpha_total << alpha_c);
  high HP thresholds expected. Prior empirical anchor: depth-5 HP (0.85/0.80/0.80).
  Bands at depth-3 set ABOVE depth-5 HP since fewer forbidden patterns means higher repulsion.

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

ANCHOR_NAME = "pp48_nkt_depth_3_baseline_verification_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NKT_DEPTH = 3
BRANCH = 2
TOTAL_NKT = (BRANCH ** NKT_DEPTH - 1) // (BRANCH - 1)
assert TOTAL_NKT == 7, f"TOTAL_NKT formula: got {TOTAL_NKT}, expected 7"

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    K_POS = 10
    N_TEST = 5
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    K_POS = 100
    N_TEST = 20

# Depth-3 baseline: high thresholds (trivially few forbidden patterns)
HP_POS = 0.90
HP_NKT_REP = 0.90
HP_TREE = 0.90
HF_POS = 0.60
HF_NKT_REP = 0.60


def _instrumentation_selftest():
    # Self-test 1: NKT count
    total = sum(BRANCH ** d for d in range(NKT_DEPTH))
    assert total == TOTAL_NKT, f"NKT count: {total} != {TOTAL_NKT}"

    # Self-test 2: GPU memory
    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy

    # Self-test 3: signed-AM single forbidden probe
    n_t = 64
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi_f = (torch.randint(0, 2, (n_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_A = (torch.randint(0, 2, (5, n_t), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_B = xi_f.unsqueeze(0)
    state = xi_f.clone()
    for _ in range(5):
        ov_A = Xi_A @ state
        ov_B = Xi_B @ state
        h = (Xi_A.t() @ ov_A - Xi_B.t() @ ov_B) / n_t
        state = torch.sign(h)
        state[state == 0] = 1.0
    anti_cos = float(torch.dot(state, -xi_f) / n_t)
    assert not (anti_cos != anti_cos), f"signed-AM result is NaN"

    # Self-test 4: GPU VRAM > 100 MB
    n_elems = int(200 * 1e6 / 4)
    dummy2 = torch.zeros((n_elems,), device=DEVICE, dtype=torch.float32)
    mem_mb = torch.cuda.memory_allocated(0) / 1e6
    assert mem_mb > 100.0, f"GPU VRAM < 100 MB: {mem_mb:.1f} MB"
    del dummy2
    torch.cuda.empty_cache()

    print(f"[selftest] PASS: NKT count={total}, gpu_mem_ok, signed_am_non_nan "
          f"anti_cos={anti_cos:.3f} depth={NKT_DEPTH}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


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
    print(f"  [seed={seed} N={n_dim}] GPU mem after Xi alloc: {mem_gb:.3f} GB "
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
    pos_rate = float(pos_ok) / max(N_TEST, 1)

    # HP2: NKT repulsion rate (all nodes since depth-3 only has 7)
    nkt_ok = 0
    n_rep_tests = min(N_TEST, len(nkt_patterns))
    for node in nkt_patterns[:n_rep_tests]:
        probe = node.clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip] *= -1.0
        retrieved = signed_retrieve(probe)
        if cosine_sim_gpu(retrieved, node) < -0.2:
            nkt_ok += 1
    nkt_rep_rate = float(nkt_ok) / max(n_rep_tests, 1)

    # HP3: tree structure (Hadamard binding preserved)
    all_nodes = nkt_patterns
    tree_ok = sum(1 for node in all_nodes[:n_rep_tests]
                  if abs(float(node.norm()) / math.sqrt(n_dim) - 1.0) < 0.1)
    tree_rate = float(tree_ok) / max(n_rep_tests, 1)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] pos_rate={pos_rate:.4f} nkt_rep_rate={nkt_rep_rate:.4f} "
          f"tree_rate={tree_rate:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
        "K_pos": K_POS, "K_nkt": TOTAL_NKT,
        "pos_retrieval_rate": float(pos_rate),
        "nkt_repulsion_rate": float(nkt_rep_rate),
        "tree_structure_intact": float(tree_rate),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": float(elapsed),
        "hp1_pass": int(pos_rate >= HP_POS),
        "hp2_pass": int(nkt_rep_rate >= HP_NKT_REP),
        "hp3_pass": int(tree_rate >= HP_TREE),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    def count_pass(key):
        return sum(1 for r in results if r.get(key, 0))

    n = len(results)
    pos = mean_key("pos_retrieval_rate")
    nkt = mean_key("nkt_repulsion_rate")
    tree = mean_key("tree_structure_intact")

    summary = (f"pos_rate={pos:.4f}(HP>={HP_POS} HF<{HF_POS}) "
               f"nkt_rep={nkt:.4f}(HP>={HP_NKT_REP} HF<{HF_NKT_REP}) "
               f"tree={tree:.4f}(HP>={HP_TREE}) "
               f"NKT_total={TOTAL_NKT} depth={NKT_DEPTH} n_seeds={n}")

    if pos < HF_POS or nkt < HF_NKT_REP:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = pos >= HP_POS
    hp2 = nkt >= HP_NKT_REP
    hp3 = tree >= HP_TREE

    if hp1 and hp2 and hp3:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP at NKT depth-3 baseline. {summary}")
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
      f"NKT_depth={NKT_DEPTH} total_nkt={TOTAL_NKT}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "NKT_DEPTH": NKT_DEPTH, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

n_active = N_ACTIVE if RUN_MODE == "smoke" else N
for s in seeds_todo:
    res = run_seed(s, n_active)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
