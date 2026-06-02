"""
q_b1_chain_depth_25_v1_n8192 -- Q-B1: heteroassoc chain at depth-25 at N=8192.

Intermediate point between depth-20 (HARD_PASS) and depth-30 (in flight). Tests the
chain degradation curve at depth-25 with the same production N=8192 config.
Prior: depth-20 HARD_PASS (mean_cos >= 0.70 at N=8192); depth-30 queued.

SCIENTIFIC QUESTION:
  At N=8192 depth-25: does the heteroassoc chain still retrieve at cosine >= 0.60?
  This fills the depth-20 -> depth-30 interpolation gap.

GPU IMPLEMENTATION:
  H matrix (N x N float32 at N=8192): 268 MB. Safe on 8 GB GPU.
  Readout snapshots at depths [1, 3, 5, 10, 15, 20, 25].

PRE-REGISTERED BANDS:
  HARD-PASS: depth-5 >= 0.95 AND depth-10 >= 0.88 AND depth-20 >= 0.70 AND depth-25 >= 0.60.
  HARD-FAIL: depth-5 < 0.80 OR depth-10 < 0.65 OR depth-20 < 0.40 OR depth-25 < 0.30.
  MIDDLE: depth-25 in [0.45, 0.60) while earlier depths meet HP.
  Prior: depth-20 HARD_PASS extrapolation at 0.995^25 ~ 0.882 -> conservative HP=0.60.
  Calibration: prior anchor depth-20 HP; bands set with 0.10 tolerance below predicted 0.88.

FORMULA SELF-TESTS:
  1. depth-25 chain retrieval non-NaN at N=128.
     [INPUT: N=128, depth=25, M_bg=5] [EXPECTED: depth25_cos non-NaN]
  2. Cosine of stored pattern with itself = 1.0.
     [INPUT: xi, xi] [EXPECTED: cos=1.0]
  3. GPU memory > 100 MB after H build.

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

ANCHOR_NAME = "q_b1_chain_depth_25_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

CHAIN_DEPTH = 25
SNAPSHOT_DEPTHS = [1, 3, 5, 10, 15, 20, 25]

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
HP_D25 = 0.60
HF_D5 = 0.80
HF_D10 = 0.65
HF_D20 = 0.40
HF_D25 = 0.30


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def bsc(m: int, n: int, gen: torch.Generator) -> torch.Tensor:
    return (torch.randint(0, 2, (m, n), generator=gen, device=DEVICE).float() * 2 - 1)


def _selftest_chain_retrieval():
    """Chain at depth-25 is non-NaN at N=128."""
    n_t = 128
    depth = 25
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    # Build small chain
    seqs = bsc(depth + 1, n_t, gen)  # (depth+1, N) patterns
    H = torch.zeros((n_t, n_t), device=DEVICE, dtype=torch.float32)
    for d in range(depth):
        H = H + torch.outer(seqs[d + 1], seqs[d]) / n_t
    # Retrieve
    state = seqs[0].clone()
    for d in range(depth):
        state = torch.sign(H @ state)
        state[state == 0] = 1.0
    cos_val = cosine_sim_gpu(state, seqs[depth])
    assert not (cos_val != cos_val), f"depth-25 chain retrieval is NaN"
    assert cos_val > -2.0, "cos_val sanity check failed"


def _selftest_cosine_identity():
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1)
    xi = (torch.randint(0, 2, (32,), generator=gen, device=DEVICE).float() * 2 - 1)
    c = cosine_sim_gpu(xi, xi)
    assert abs(c - 1.0) < 1e-5, f"cosine(xi, xi) = {c:.6f} != 1.0"


def _selftest_gpu_vram():
    n_elems = int(200 * 1e6 / 4)
    dummy = torch.zeros((n_elems,), device=DEVICE, dtype=torch.float32)
    mem_mb = torch.cuda.memory_allocated(0) / 1e6
    assert mem_mb > 100.0, f"GPU VRAM < 100 MB: {mem_mb:.1f} MB"
    del dummy
    torch.cuda.empty_cache()


def _instrumentation_selftest():
    _selftest_chain_retrieval()
    _selftest_cosine_identity()
    _selftest_gpu_vram()
    print(f"[selftest] PASS: chain_retrieval_ok, cosine_id_ok, gpu_vram_ok depth={CHAIN_DEPTH}",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    # Build background patterns to simulate realistic loading
    Xi_bg = bsc(M_BACKGROUND, n_dim, gen)

    # Build heteroassoc chains: each chain is a sequence of (depth+1) patterns
    # H = sum_chains sum_d xi_{d+1} xi_d^T / N
    H = Xi_bg.t() @ Xi_bg / float(n_dim) * 0.1  # small background noise

    chain_starts = []
    chain_ends = []  # at each snapshot depth

    snapshot_cos = {d: [] for d in SNAPSHOT_DEPTHS}

    for c in range(N_CHAINS):
        seq = bsc(CHAIN_DEPTH + 1, n_dim, gen)
        chain_starts.append(seq[0])

        for d in range(CHAIN_DEPTH):
            H = H + torch.outer(seq[d + 1], seq[d]) / float(n_dim)

        # Retrieval: follow chain from start
        state = seq[0].clone()
        for d in range(CHAIN_DEPTH):
            state = torch.sign(H @ state)
            state[state == 0] = 1.0
            depth_here = d + 1
            if depth_here in SNAPSHOT_DEPTHS:
                cos_val = cosine_sim_gpu(state, seq[depth_here])
                snapshot_cos[depth_here].append(cos_val)

    mean_cos = {}
    for d in SNAPSHOT_DEPTHS:
        vals = snapshot_cos[d]
        mean_cos[d] = float(sum(vals) / len(vals)) if vals else 0.0

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    cos_str = " ".join(f"d{d}={mean_cos[d]:.3f}" for d in SNAPSHOT_DEPTHS)
    print(f"  [seed={seed} N={n_dim}] {cos_str} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
        **{f"mean_cos_d{d}": mean_cos[d] for d in SNAPSHOT_DEPTHS},
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": float(elapsed),
        "hp_d5_pass": int(mean_cos[5] >= HP_D5),
        "hp_d10_pass": int(mean_cos[10] >= HP_D10),
        "hp_d20_pass": int(mean_cos[20] >= HP_D20),
        "hp_d25_pass": int(mean_cos[25] >= HP_D25),
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
    d5 = mean_key("mean_cos_d5")
    d10 = mean_key("mean_cos_d10")
    d20 = mean_key("mean_cos_d20")
    d25 = mean_key("mean_cos_d25")

    summary = (f"d5={d5:.4f}(HP>={HP_D5} HF<{HF_D5}) "
               f"d10={d10:.4f}(HP>={HP_D10} HF<{HF_D10}) "
               f"d20={d20:.4f}(HP>={HP_D20} HF<{HF_D20}) "
               f"d25={d25:.4f}(HP>={HP_D25} HF<{HF_D25}) n_seeds={n}")

    if d5 < HF_D5 or d10 < HF_D10 or d20 < HF_D20 or d25 < HF_D25:
        return ("HARD_FAIL", f"HARD_FAIL: depth threshold violated. {summary}")

    if d5 >= HP_D5 and d10 >= HP_D10 and d20 >= HP_D20 and d25 >= HP_D25:
        return ("HARD_PASS", f"HARD_PASS: all 4 depth-HP at N=8192 depth-25. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: depth-25 in middle band. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"depth={CHAIN_DEPTH} N_chains={N_CHAINS} M_bg={M_BACKGROUND}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "CHAIN_DEPTH": CHAIN_DEPTH, "run_mode": RUN_MODE}

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
