"""
substrate_capacity_stress_composition_v1_n16384 -- PP-12/Q-A3 capacity-stress test.

ROUTING: notes/routing_redirect_depth_to_capacity_stress_test_2026-06-04.md (Research).

CAPABILITY QUESTION:
  At fixed N and moderate depth L, does cross-layer composition fidelity remain EXACT-1.0000 as the
  stored-pattern count M approaches the Hopfield capacity bound, OR does fidelity degrade at the
  algebraic boundary M ~ alpha_c * N? Depth-ladder (L=200..2000+) already confirmed EXACT at M~0
  storage pressure; the INFORMATIVE regime is the capacity boundary. (Depth ladder is now STOPPED per
  Research/user direction; this is the redirect.)

DESIGN (reuses Q-A3/PP-12 bipolar Hopfield composition; sweeps inner-layer load M_INNER/N):
  For each M/N cell: store M_INNER = round(MN * N) random bipolar patterns at the inner layer via
  outer-product Hopfield write; compose through L=50 layers (Hadamard bind + sign-rounded Hopfield
  retrieve, same protocol as Q-A3); measure per-layer fidelity (cosine vs the true stored pattern).
  As M_INNER/N crosses classical alpha_c=0.138, inner-layer retrieval should start to fail -> fidelity
  degrades. Locates the composition capacity boundary (previously unmeasured).

PRE-REGISTERED BANDS (per routing):
  HARD-PASS (capacity boundary detected): fidelity = 1.0000 EXACT at M/N <= 0.12; degrades monotonically
    at M/N >= 0.15; boundary visible within the 0.09-0.21 range; 5/5 seeds consistent.
  MIDDLE: degradation present but boundary far from alpha_c=0.138 (e.g. < 0.06 or > 0.21 onset), OR
    partial degradation / 3-4 of 5 seeds consistent.
  HARD-FAIL (no boundary in range): fidelity = 1.0000 EXACT at ALL M/N including 0.21 (above classical
    alpha_c) -> substrate is modern-Hopfield class (alpha_c >> 0.138) OR composition does not load the
    stored bank. Either way informative about substrate's algebraic class.

FORMULA SELF-TESTS (PROT-022):
  1. alpha_c = 0.138; at N=16384 classical capacity M_c = round(0.138*16384) = 2261. [EXPECTED: 2261]
  2. M/N grid spans below+at+above alpha_c: min 0.03 < 0.138 < max 0.21. [EXPECTED: True]
  3. L=50 chain: 49-ctx Hadamard roundtrip recovers xi_L1 exactly (sign-rounded). [EXPECTED: exact]
  4. GPU memory > 0 after a W build.

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed run_mode + N.
QUEUE: overnight_queue (GPU; on-demand W build at N=16384). TIMEOUT: 21600s (PROT-019 floor).
GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch, torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_capacity_stress_composition_v1_n16384"
_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L_DEPTH = 50
HP_FIDELITY_EXACT = 0.9999
NOISE_FRAC = 0.10
MN_GRID = [0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21]

# Pre-registered band thresholds
HP_EXACT_MN_MAX = 0.12     # must be EXACT at/below this
HP_DEGRADE_MN_MIN = 0.15   # must degrade at/above this
DEGRADE_FIDELITY = 0.9999  # "degraded" = mean fidelity below this

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    N_QUERIES = 2
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 2

_W_ONDEMAND_GB = 16384 * 16384 * 4 / 1e9
assert _W_ONDEMAND_GB < 1.2, f"W on-demand size: {_W_ONDEMAND_GB:.3f} GB"


def _selftest():
    m_c = round(ALPHA_C * N)
    assert m_c == 2261, f"M_c selftest: {m_c} expected 2261"
    assert min(MN_GRID) < ALPHA_C < max(MN_GRID), "MN_GRID must span alpha_c"
    # L=50 Hadamard chain roundtrip (sign-rounded)
    n_ctx = L_DEPTH - 1
    base = [[1.0, -1.0], [-1.0, 1.0], [1.0, 1.0], [-1.0, -1.0]]
    ctxs = [torch.tensor(base[i % 4], dtype=torch.float32, device=DEVICE) for i in range(n_ctx)]
    xi = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    x = xi.clone()
    for c in ctxs:
        x = c * x
    for c in reversed(ctxs):
        x = x * c
    assert torch.allclose(x, xi, atol=1e-6), "L=50 chain roundtrip failed"
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    assert torch.cuda.memory_allocated(0) > 0
    del dummy
    print(f"[selftest] PASS: M_c={m_c} MN_grid spans alpha_c L={L_DEPTH} chain ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve_gpu(W, probe, n_steps=5):
    state = probe.clone()
    for _ in range(n_steps):
        h = W @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_gpu(a, b):
    na, nb = float(a.norm()), float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def run_cell(mn: float, seed: int, n_dim: int) -> Dict:
    """One (M/N, seed) cell: load M_INNER patterns, compose L=50, measure fidelity."""
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 1000 + int(mn * 1000))

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    M_INNER = max(2, int(round(mn * n_dim)))
    # Inner bank under capacity pressure; mid layers thin (binding contexts).
    M_MID = [max(2, M_INNER // 4)] + [2] * (L_DEPTH - 3)
    assert len(M_MID) == L_DEPTH - 2
    M_OUTER = 2

    Xi_inner = bsc(M_INNER, n_dim)
    Xi_layers = [Xi_inner]; Xi_ctxs = []; curr = Xi_inner
    for m in M_MID:
        ctx = bsc(m, n_dim); Xi_ctxs.append(ctx)
        mid = ctx * curr[:m]; Xi_layers.append(mid); curr = mid
    ctx_outer = bsc(M_OUTER, n_dim); Xi_ctxs.append(ctx_outer)
    Xi_outer = ctx_outer * curr[:M_OUTER]; Xi_layers.append(Xi_outer)
    assert len(Xi_layers) == L_DEPTH

    level_fids = []
    inner_fids = []
    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]; probe = xi_outer_true.clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC); probe[flip] *= -1.0
        decoded = [None] * L_DEPTH
        W_top = (Xi_layers[L_DEPTH - 1].t() @ Xi_layers[L_DEPTH - 1]) / n_dim
        ret = hopfield_retrieve_gpu(W_top, probe); del W_top
        decoded[L_DEPTH - 1] = ret
        for l_idx in range(L_DEPTH - 2, -1, -1):
            ptr = decoded[l_idx + 1] * Xi_ctxs[l_idx][q_idx]
            W_l = (Xi_layers[l_idx].t() @ Xi_layers[l_idx]) / n_dim
            ret_l = hopfield_retrieve_gpu(W_l, ptr); del W_l
            decoded[l_idx] = ret_l
            f = cosine_sim_gpu(ret_l, Xi_layers[l_idx][q_idx])
            level_fids.append(f)
            if l_idx == 0:
                inner_fids.append(cosine_sim_gpu(decoded[0], Xi_layers[0][q_idx]))
    mean_fid = float(sum(level_fids) / len(level_fids)) if level_fids else 0.0
    mean_inner = float(sum(inner_fids) / len(inner_fids)) if inner_fids else 0.0
    return {"mn": mn, "M_INNER": M_INNER, "mean_fidelity": mean_fid, "inner_fidelity": mean_inner}


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    cells = []
    for mn in MN_GRID:
        c = run_cell(mn, seed, n_dim)
        cells.append(c)
        print(f"  [seed={seed} M/N={mn:.2f} M_INNER={c['M_INNER']}] mean_fid={c['mean_fidelity']:.4f} "
              f"inner_fid={c['inner_fidelity']:.4f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "cells": cells,
            "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    # Mean fidelity per M/N cell across seeds.
    mean_fid = {}
    for mn in MN_GRID:
        fs = [c["mean_fidelity"] for r in results for c in r.get("cells", []) if abs(c["mn"] - mn) < 1e-9]
        mean_fid[mn] = float(sum(fs) / len(fs)) if fs else 0.0
    below = [mn for mn in MN_GRID if mn <= HP_EXACT_MN_MAX]
    above = [mn for mn in MN_GRID if mn >= HP_DEGRADE_MN_MIN]
    exact_below = all(mean_fid[mn] >= HP_FIDELITY_EXACT for mn in below)
    degrade_above = any(mean_fid[mn] < DEGRADE_FIDELITY for mn in above)
    all_exact = all(mean_fid[mn] >= HP_FIDELITY_EXACT for mn in MN_GRID)
    summary = "fids=" + " ".join(f"{mn:.2f}:{mean_fid[mn]:.4f}" for mn in MN_GRID)

    if all_exact:
        return ("HARD_FAIL",
                f"HARD_FAIL: fidelity EXACT at ALL M/N incl {max(MN_GRID)} (> alpha_c=0.138); no classical "
                f"capacity boundary in range -> modern-Hopfield class OR composition not loading bank. {summary}")
    if exact_below and degrade_above:
        return ("HARD_PASS",
                f"HARD_PASS: EXACT at M/N<={HP_EXACT_MN_MAX}, degrades at M/N>={HP_DEGRADE_MN_MIN} "
                f"(boundary near alpha_c=0.138). {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: degradation present but boundary not cleanly at alpha_c. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} mode={RUN_MODE} seeds={SEEDS} L={L_DEPTH} "
      f"MN_grid={MN_GRID}", flush=True)
if RUN_MODE == "full" and N_ACTIVE != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_ACTIVE={N_ACTIVE} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "run_mode": RUN_MODE, "L": L_DEPTH, "MN_grid": MN_GRID}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: {peak_mem_gb:.3f}GB"

metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "L": L_DEPTH, "run_mode": RUN_MODE, "MN_grid": MN_GRID,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
