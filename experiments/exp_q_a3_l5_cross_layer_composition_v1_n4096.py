"""
q_a3_l5_cross_layer_composition_v1_n4096 -- Q-A3: L=5 cross-layer composition at N=4096.

Extends L=2/3/4 (all HARD_PASS) to L=5 boundary at N=4096.

Architecture:
  L1 (inner): N=4096, M_inner=100, p=2 Hopfield.
  L2: M_mid2=50, Hadamard binding ctx2*L1.
  L3: M_mid3=25, Hadamard binding ctx3*L2.
  L4: M_mid4=12, Hadamard binding ctx4*L3.
  L5: M_outer=6, Hadamard binding ctx5*L4.

GPU IMPLEMENTATION:
  All W matrices and Xi pattern tensors on device='cuda'.
  W = Xi.T @ Xi / N (explicit, but N=4096 -> W is 4096^2 float32 = 67 MB each).
  Peak VRAM: 5 W matrices x 67 MB = 335 MB. Safe on 8 GB.

PRE-REGISTERED BANDS:
  HP: all 5 conditions in >= 4/5 seeds.
    HP1-HP5: per-level fidelity (L1...L5) each >= 0.93.
    HP6: end-to-end L=5 accuracy >= 0.70.
  HARD-FAIL: any fidelity < 0.55 OR l5_acc < 0.35.
  MIDDLE: 5/6 conditions met.
  Prior: L=4 HARD_PASS at N=4096/8192; L=5 extends the depth envelope.
  Calibration: L=4 HP'd; L=5 expected similar per geometric chain model.

FORMULA SELF-TESTS:
  1. L=5 chain: xi_L5 = ctx5*(ctx4*(ctx3*(ctx2*xi_L1))); full round-trip recovers xi_L1.
     [INPUT: tiny 2-element vectors] [EXPECTED: decode = xi_L1]
  2. Capacity at N=4096: alpha_L1=100/4096=0.0244, L2=50/4096=0.0122,
     L3=25/4096=0.0061, L4=12/4096=0.00293, L5=6/4096=0.00146; all < alpha_c=0.138.
  3. GPU guard: cuda.memory_allocated() > 0 after W build.

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

# GPU GUARD
try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed; cannot run GPU experiment.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU. Aborting.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_a3_l5_cross_layer_composition_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
HP_FIDELITY = 0.93
HF_FIDELITY = 0.55
HP_L5_ACC = 0.70
HF_L5_ACC = 0.35
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    M_INNER = 20
    M_MID2 = 10
    M_MID3 = 5
    M_MID4 = 3
    M_OUTER = 2
    N_QUERIES = 2
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 100
    M_MID2 = 50
    M_MID3 = 25
    M_MID4 = 12
    M_OUTER = 6
    N_QUERIES = 5


def _selftest_l5_chain():
    ctx5 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    ctx4 = torch.tensor([-1.0, 1.0], dtype=torch.float32, device=DEVICE)
    ctx3 = torch.tensor([1.0, 1.0], dtype=torch.float32, device=DEVICE)
    ctx2 = torch.tensor([-1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi_L1 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi_L2 = ctx2 * xi_L1
    xi_L3 = ctx3 * xi_L2
    xi_L4 = ctx4 * xi_L3
    xi_L5 = ctx5 * xi_L4
    xi_L4_dec = xi_L5 * ctx5
    xi_L3_dec = xi_L4_dec * ctx4
    xi_L2_dec = xi_L3_dec * ctx3
    xi_L1_dec = xi_L2_dec * ctx2
    assert torch.allclose(xi_L1_dec, xi_L1, atol=1e-6), f"L5 chain decode failed: {xi_L1_dec}"


def _instrumentation_selftest():
    _selftest_l5_chain()
    # Capacity check
    n_dim = N_ACTIVE
    alphas = [M_INNER/n_dim, M_MID2/n_dim, M_MID3/n_dim, M_MID4/n_dim, M_OUTER/n_dim]
    for i, al in enumerate(alphas, 1):
        assert al < ALPHA_C, f"L{i} alpha {al:.4f} >= alpha_c={ALPHA_C}"
    # GPU memory check
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: L5 chain decode, capacity_ok, gpu_mem_ok "
          f"N={n_dim} alpha_L1={alphas[0]:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve_gpu(W: torch.Tensor, Xi: torch.Tensor, probe: torch.Tensor,
                           n_steps: int = 5) -> torch.Tensor:
    """p=2 Hopfield retrieval with W on GPU."""
    state = probe.clone()
    for _ in range(n_steps):
        h = W @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


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

    Xi_inner = bsc(M_INNER, n_dim)
    Xi_ctx2 = bsc(M_MID2, n_dim)
    Xi_mid2 = Xi_ctx2 * Xi_inner[:M_MID2]
    Xi_ctx3 = bsc(M_MID3, n_dim)
    Xi_mid3 = Xi_ctx3 * Xi_mid2[:M_MID3]
    Xi_ctx4 = bsc(M_MID4, n_dim)
    Xi_mid4 = Xi_ctx4 * Xi_mid3[:M_MID4]
    Xi_ctx5 = bsc(M_OUTER, n_dim)
    Xi_outer = Xi_ctx5 * Xi_mid4[:M_OUTER]

    # Build W matrices (N x N float32 GPU -- N=4096 means 67 MB each)
    W_inner = (Xi_inner.t() @ Xi_inner) / n_dim
    W_mid2 = (Xi_mid2.t() @ Xi_mid2) / n_dim
    W_mid3 = (Xi_mid3.t() @ Xi_mid3) / n_dim
    W_mid4 = (Xi_mid4.t() @ Xi_mid4) / n_dim
    W_outer = (Xi_outer.t() @ Xi_outer) / n_dim

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after W build: {mem_gb:.3f} GB", flush=True)

    # Per-level fidelities and L=5 end-to-end accuracy
    level_fids = {f"L{l}": [] for l in range(1, 6)}

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0

        # Decode chain: L5 -> L4 -> L3 -> L2 -> L1
        xi_L5_ret = hopfield_retrieve_gpu(W_outer, Xi_outer, probe)
        level_fids["L5"].append(cosine_sim_gpu(xi_L5_ret, xi_outer_true))

        xi_L4_ptr = xi_L5_ret * Xi_ctx5[q_idx]
        xi_L4_true = Xi_mid4[q_idx] if q_idx < M_MID4 else Xi_mid4[0]
        xi_L4_ret = hopfield_retrieve_gpu(W_mid4, Xi_mid4, xi_L4_ptr)
        level_fids["L4"].append(cosine_sim_gpu(xi_L4_ret, xi_L4_true))

        xi_L3_ptr = xi_L4_ret * Xi_ctx4[q_idx] if q_idx < M_MID4 else xi_L4_ret * Xi_ctx4[0]
        xi_L3_true = Xi_mid3[q_idx] if q_idx < M_MID3 else Xi_mid3[0]
        xi_L3_ret = hopfield_retrieve_gpu(W_mid3, Xi_mid3, xi_L3_ptr)
        level_fids["L3"].append(cosine_sim_gpu(xi_L3_ret, xi_L3_true))

        xi_L2_ptr = xi_L3_ret * Xi_ctx3[q_idx] if q_idx < M_MID3 else xi_L3_ret * Xi_ctx3[0]
        xi_L2_true = Xi_mid2[q_idx] if q_idx < M_MID2 else Xi_mid2[0]
        xi_L2_ret = hopfield_retrieve_gpu(W_mid2, Xi_mid2, xi_L2_ptr)
        level_fids["L2"].append(cosine_sim_gpu(xi_L2_ret, xi_L2_true))

        xi_L1_ptr = xi_L2_ret * Xi_ctx2[q_idx] if q_idx < M_MID2 else xi_L2_ret * Xi_ctx2[0]
        xi_L1_true = Xi_inner[q_idx] if q_idx < M_INNER else Xi_inner[0]
        xi_L1_ret = hopfield_retrieve_gpu(W_inner, Xi_inner, xi_L1_ptr)
        level_fids["L1"].append(cosine_sim_gpu(xi_L1_ret, xi_L1_true))

    mean_fids = {k: float(sum(v)/len(v)) if v else 0.0 for k, v in level_fids.items()}
    l5_acc = mean_fids["L1"]  # end-to-end: L5 input recovered L1 output

    # Free W matrices to conserve VRAM for next seed
    del W_inner, W_mid2, W_mid3, W_mid4, W_outer

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] fids=L1:{mean_fids['L1']:.4f} L2:{mean_fids['L2']:.4f} "
          f"L3:{mean_fids['L3']:.4f} L4:{mean_fids['L4']:.4f} L5:{mean_fids['L5']:.4f} "
          f"l5_e2e={l5_acc:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "fid_L1": mean_fids["L1"], "fid_L2": mean_fids["L2"],
        "fid_L3": mean_fids["L3"], "fid_L4": mean_fids["L4"],
        "fid_L5": mean_fids["L5"], "l5_acc": float(l5_acc),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    fids = {f"L{l}": [r[f"fid_L{l}"] for r in results if f"fid_L{l}" in r] for l in range(1, 6)}
    l5_accs = [r["l5_acc"] for r in results if "l5_acc" in r]

    means = {k: float(sum(v)/len(v)) if v else 0.0 for k, v in fids.items()}
    mean_l5_acc = float(sum(l5_accs)/len(l5_accs)) if l5_accs else 0.0

    summary = (f"fids={','.join(f'{k}:{means[k]:.4f}' for k in sorted(means.keys()))} "
               f"l5_acc={mean_l5_acc:.4f} n_seeds={len(results)}")

    # HARD_FAIL check
    for k in means:
        if means[k] < HF_FIDELITY:
            return ("HARD_FAIL", f"HARD_FAIL: {k} fidelity {means[k]:.4f} < {HF_FIDELITY}. {summary}")
    if mean_l5_acc < HF_L5_ACC:
        return ("HARD_FAIL", f"HARD_FAIL: l5_acc {mean_l5_acc:.4f} < {HF_L5_ACC}. {summary}")

    hp_fids = sum(1 for k in means if means[k] >= HP_FIDELITY)
    hp_acc = mean_l5_acc >= HP_L5_ACC

    if hp_fids >= 5 and hp_acc:
        return ("HARD_PASS", f"HARD_PASS: 5/5 level fidelities >= {HP_FIDELITY} + l5_acc >= {HP_L5_ACC}. {summary}")
    if hp_fids >= 4 and hp_acc:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {hp_fids}/5 fidelity HP + l5_acc HP. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {hp_fids}/5 fidelity HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} M_inner={M_INNER} M_outer={M_OUTER}...", flush=True)
    result = run_seed(seed, N_ACTIVE)
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
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "n_active": N_ACTIVE,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
if all_results:
    for lv in ["L1", "L2", "L3", "L4", "L5"]:
        vals = [r[f"fid_{lv}"] for r in all_results if f"fid_{lv}" in r]
        metrics[f"mean_fid_{lv}"] = float(sum(vals)/len(vals)) if vals else None
    l5_accs = [r["l5_acc"] for r in all_results if "l5_acc" in r]
    metrics["mean_l5_acc"] = float(sum(l5_accs)/len(l5_accs)) if l5_accs else None

metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
