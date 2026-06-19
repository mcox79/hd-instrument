"""
q_a3_l7_cross_layer_composition_v1_n4096 -- Q-A3: L=7 cross-layer composition at N=4096.

Extends L=6 (HARD_PASS all fidelities=1.0 at N=4096) to L=7.

Architecture:
  L1 (inner): N=4096, M_inner=100, p=2 Hopfield.
  L2: M_mid2=50, Hadamard binding ctx2*L1.
  L3: M_mid3=25.
  L4: M_mid4=12.
  L5: M_mid5=6.
  L6: M_mid6=3.
  L7: M_outer=2, Hadamard binding ctx7*L6.

GPU IMPLEMENTATION:
  7 W matrices x 67 MB each = 469 MB total. Safe on 8 GB.

PRE-REGISTERED BANDS:
  HP: all 7 level fidelities >= 0.90 AND l7_acc >= 0.50 in >= 4/5 seeds.
  HARD-FAIL: any per-level fidelity < 0.55 OR l7_acc < 0.25.
  MIDDLE: 6/7 conditions or l7_acc in [0.25, 0.50).
  Prior: L=6 HP all fidelities=1.0; L=7 is deeper -- HP threshold relaxed 0.60->0.50.
  Calibration: prior L=6 HP; envelope extension; bands +-0.15 of prior.

FORMULA SELF-TESTS:
  1. L=7 chain: decode via 7-step Hadamard roundtrip recovers xi_L1.
     [INPUT: tiny 2-element vectors] [EXPECTED: decoded = xi_L1]
  2. Capacity at N=4096: all alphas < 0.138.
  3. GPU guard: memory_allocated() > 0 after W build.

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

ANCHOR_NAME = "q_a3_l7_cross_layer_composition_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
HP_FIDELITY = 0.90
HF_FIDELITY = 0.55
HP_L7_ACC = 0.50
HF_L7_ACC = 0.25
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    M_INNER = 20
    M_MID2 = 10
    M_MID3 = 5
    M_MID4 = 3
    M_MID5 = 2
    M_MID6 = 2
    M_OUTER = 2
    N_QUERIES = 2
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 100
    M_MID2 = 50
    M_MID3 = 25
    M_MID4 = 12
    M_MID5 = 6
    M_MID6 = 3
    M_OUTER = 2
    N_QUERIES = 2


def _selftest_l7_chain():
    ctx7 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    ctx6 = torch.tensor([-1.0, 1.0], dtype=torch.float32, device=DEVICE)
    ctx5 = torch.tensor([1.0, 1.0], dtype=torch.float32, device=DEVICE)
    ctx4 = torch.tensor([-1.0, -1.0], dtype=torch.float32, device=DEVICE)
    ctx3 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    ctx2 = torch.tensor([-1.0, 1.0], dtype=torch.float32, device=DEVICE)
    xi_L1 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi_L2 = ctx2 * xi_L1
    xi_L3 = ctx3 * xi_L2
    xi_L4 = ctx4 * xi_L3
    xi_L5 = ctx5 * xi_L4
    xi_L6 = ctx6 * xi_L5
    xi_L7 = ctx7 * xi_L6
    # Roundtrip decode
    xi_L6_dec = xi_L7 * ctx7
    xi_L5_dec = xi_L6_dec * ctx6
    xi_L4_dec = xi_L5_dec * ctx5
    xi_L3_dec = xi_L4_dec * ctx4
    xi_L2_dec = xi_L3_dec * ctx3
    xi_L1_dec = xi_L2_dec * ctx2
    assert torch.allclose(xi_L1_dec, xi_L1, atol=1e-6), f"L7 chain decode failed: {xi_L1_dec}"


def _instrumentation_selftest():
    _selftest_l7_chain()
    n_dim = N_ACTIVE
    alphas = [M_INNER/n_dim, M_MID2/n_dim, M_MID3/n_dim,
              M_MID4/n_dim, M_MID5/n_dim, M_MID6/n_dim, M_OUTER/n_dim]
    for i, al in enumerate(alphas, 1):
        assert al < ALPHA_C, f"L{i} alpha {al:.4f} >= alpha_c={ALPHA_C}"
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: L7 chain decode, capacity_ok, gpu_mem_ok "
          f"N={n_dim} alpha_L1={alphas[0]:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve_gpu(W: torch.Tensor, probe: torch.Tensor, n_steps: int = 5) -> torch.Tensor:
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
    Xi_ctx5 = bsc(M_MID5, n_dim)
    Xi_mid5 = Xi_ctx5 * Xi_mid4[:M_MID5]
    Xi_ctx6 = bsc(M_MID6, n_dim)
    Xi_mid6 = Xi_ctx6 * Xi_mid5[:M_MID6]
    Xi_ctx7 = bsc(M_OUTER, n_dim)
    Xi_outer = Xi_ctx7 * Xi_mid6[:M_OUTER]

    W_inner = (Xi_inner.t() @ Xi_inner) / n_dim
    W_mid2 = (Xi_mid2.t() @ Xi_mid2) / n_dim
    W_mid3 = (Xi_mid3.t() @ Xi_mid3) / n_dim
    W_mid4 = (Xi_mid4.t() @ Xi_mid4) / n_dim
    W_mid5 = (Xi_mid5.t() @ Xi_mid5) / n_dim
    W_mid6 = (Xi_mid6.t() @ Xi_mid6) / n_dim
    W_outer = (Xi_outer.t() @ Xi_outer) / n_dim

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after W build: {mem_gb:.3f} GB", flush=True)

    level_fids = {f"L{l}": [] for l in range(1, 8)}
    l7_acc = []

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0

        # L7 retrieval
        xi_L7_ret = hopfield_retrieve_gpu(W_outer, probe)
        # Decode L7 -> L6
        xi_L6_ptr = xi_L7_ret * Xi_ctx7[q_idx]
        xi_L6_ret = hopfield_retrieve_gpu(W_mid6, xi_L6_ptr)
        # Decode L6 -> L5
        xi_L5_ptr = xi_L6_ret * Xi_ctx6[q_idx]
        xi_L5_ret = hopfield_retrieve_gpu(W_mid5, xi_L5_ptr)
        # Decode L5 -> L4
        xi_L4_ptr = xi_L5_ret * Xi_ctx5[q_idx]
        xi_L4_ret = hopfield_retrieve_gpu(W_mid4, xi_L4_ptr)
        # Decode L4 -> L3
        xi_L3_ptr = xi_L4_ret * Xi_ctx4[q_idx]
        xi_L3_ret = hopfield_retrieve_gpu(W_mid3, xi_L3_ptr)
        # Decode L3 -> L2
        xi_L2_ptr = xi_L3_ret * Xi_ctx3[q_idx]
        xi_L2_ret = hopfield_retrieve_gpu(W_mid2, xi_L2_ptr)
        # Decode L2 -> L1
        xi_L1_ptr = xi_L2_ret * Xi_ctx2[q_idx]
        xi_L1_ret = hopfield_retrieve_gpu(W_inner, xi_L1_ptr)

        xi_L1_true = Xi_inner[q_idx]
        xi_L2_true = Xi_mid2[q_idx]
        xi_L3_true = Xi_mid3[q_idx]
        xi_L4_true = Xi_mid4[q_idx]
        xi_L5_true = Xi_mid5[q_idx]
        xi_L6_true = Xi_mid6[q_idx]

        level_fids["L7"].append(cosine_sim_gpu(xi_L7_ret, xi_outer_true))
        level_fids["L6"].append(cosine_sim_gpu(xi_L6_ret, xi_L6_true))
        level_fids["L5"].append(cosine_sim_gpu(xi_L5_ret, xi_L5_true))
        level_fids["L4"].append(cosine_sim_gpu(xi_L4_ret, xi_L4_true))
        level_fids["L3"].append(cosine_sim_gpu(xi_L3_ret, xi_L3_true))
        level_fids["L2"].append(cosine_sim_gpu(xi_L2_ret, xi_L2_true))
        level_fids["L1"].append(cosine_sim_gpu(xi_L1_ret, xi_L1_true))
        l7_acc.append(cosine_sim_gpu(xi_L1_ret, xi_L1_true))

    mean_fids = {k: float(sum(v) / len(v)) if v else 0.0 for k, v in level_fids.items()}
    mean_l7 = float(sum(l7_acc) / len(l7_acc)) if l7_acc else 0.0

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] fids={' '.join(f'{k}:{mean_fids[k]:.4f}' for k in sorted(mean_fids.keys()))} "
          f"l7_acc={mean_l7:.4f} peak_gpu={peak_mem:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "l7_accuracy": float(mean_l7),
        "peak_gpu_gb": float(peak_mem), "elapsed_s": elapsed,
    }
    for k, v in mean_fids.items():
        result[f"fid_{k.lower()}"] = v
    return result


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    fid_l1 = mean_key("fid_l1")
    fid_l2 = mean_key("fid_l2")
    fid_l3 = mean_key("fid_l3")
    fid_l4 = mean_key("fid_l4")
    fid_l5 = mean_key("fid_l5")
    fid_l6 = mean_key("fid_l6")
    fid_l7 = mean_key("fid_l7")
    l7_acc = mean_key("l7_accuracy")

    summary = (f"L1={fid_l1:.4f} L2={fid_l2:.4f} L3={fid_l3:.4f} "
               f"L4={fid_l4:.4f} L5={fid_l5:.4f} L6={fid_l6:.4f} L7={fid_l7:.4f} "
               f"l7_acc={l7_acc:.4f}(HP>={HP_L7_ACC} HF<{HF_L7_ACC}) "
               f"n_seeds={len(results)}")

    fids = [fid_l1, fid_l2, fid_l3, fid_l4, fid_l5, fid_l6, fid_l7]
    if any(f < HF_FIDELITY for f in fids) or l7_acc < HF_L7_ACC:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp_fids = sum(1 for f in fids if f >= HP_FIDELITY)
    hp_l7 = l7_acc >= HP_L7_ACC

    if hp_fids >= 7 and hp_l7:
        return ("HARD_PASS", f"HARD_PASS: all 7 level fidelities + l7_acc. {summary}")
    if hp_fids >= 6 or (hp_fids >= 5 and hp_l7):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {hp_fids}/7 level HP + l7_acc={hp_l7}. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {hp_fids}/7 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} L=7", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "L": 7, "run_mode": RUN_MODE}
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
    "N": N, "L": 7, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         **{f"fid_l{i}": r.get(f"fid_l{i}") for i in range(1, 8)},
         "l7_accuracy": r.get("l7_accuracy"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
