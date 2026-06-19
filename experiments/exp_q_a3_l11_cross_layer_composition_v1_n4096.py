"""
q_a3_l11_cross_layer_composition_v1_n4096 -- Q-A3: L=11 cross-layer composition at N=4096.

Extends L=10 to L=11. Tests substrate compositional ceiling at depth-11.
  L=10 was HARD_PASS with all 10 level fidelities = 1.0000 (N=4096 5-seed).

Architecture:
  L1 (inner): N=4096, M_inner=100, p=2 Hopfield.
  L2: M_mid2=50.  L3: M_mid3=25.  L4: M_mid4=12.  L5: M_mid5=6.
  L6: M_mid6=3.   L7: M_mid7=2.   L8: M_mid8=2.   L9: M_mid9=2.
  L10: M_mid10=2. L11: M_outer=2, Hadamard binding ctx11*L10.

  11 W matrices x ~67 MB each = ~737 MB total. Safe on 8 GB GPU.

PRE-REGISTERED BANDS (ceiling push from L=10 EXACT-1.0):
  HARD-PASS: all 11 level fidelities = 1.0000 unanimous (5/5 seeds).
  MIDDLE: any L_fid in [0.85, 1.0).
  HARD-FAIL: any L_fid < 0.85 OR l11_acc < 0.5.

FORMULA SELF-TESTS:
  1. L=11 chain: 11-step Hadamard roundtrip recovers xi_L1.
     [INPUT: 2-element +-1 vectors] [EXPECTED: decode = xi_L1]
  2. All alphas < alpha_c=0.138.
  3. GPU guard: memory > 0 after W build.

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: seed checkpoints keyed with run_mode + L.
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

ANCHOR_NAME = "q_a3_l11_cross_layer_composition_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L_DEPTH = 11
HP_FIDELITY_UNANI_THRESH = 0.9999
MIDDLE_FIDELITY = 0.85
HF_FIDELITY = 0.85
HP_LACC = 0.5
HF_LACC = 0.5
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
    M_MID7 = 2
    M_MID8 = 2
    M_MID9 = 2
    M_MID10 = 2
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
    M_MID7 = 2
    M_MID8 = 2
    M_MID9 = 2
    M_MID10 = 2
    M_OUTER = 2
    N_QUERIES = 2


def _selftest_l11_chain():
    """11-step Hadamard roundtrip recovers xi_L1."""
    ctxs = [torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([-1.0, 1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([1.0, 1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([-1.0, -1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([-1.0, 1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([1.0, 1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([-1.0, -1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE),
            torch.tensor([-1.0, 1.0], dtype=torch.float32, device=DEVICE)]  # ctx2..ctx11
    xi_L1 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi = xi_L1.clone()
    for c in ctxs:
        xi = c * xi
    xi_dec = xi.clone()
    for c in reversed(ctxs):
        xi_dec = xi_dec * c
    assert torch.allclose(xi_dec, xi_L1, atol=1e-6), f"L11 chain decode failed: {xi_dec}"


def _instrumentation_selftest():
    _selftest_l11_chain()
    n_dim = N_ACTIVE
    ms = [M_INNER, M_MID2, M_MID3, M_MID4, M_MID5, M_MID6, M_MID7, M_MID8, M_MID9, M_MID10, M_OUTER]
    for i, m in enumerate(ms, 1):
        al = m / n_dim
        assert al < ALPHA_C, f"L{i} alpha {al:.4f} >= alpha_c={ALPHA_C}"
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: L11 chain decode ok, capacity_ok, gpu_mem_ok N={n_dim}", flush=True)


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
    Xi_ctx7 = bsc(M_MID7, n_dim)
    Xi_mid7 = Xi_ctx7 * Xi_mid6[:M_MID7]
    Xi_ctx8 = bsc(M_MID8, n_dim)
    Xi_mid8 = Xi_ctx8 * Xi_mid7[:M_MID8]
    Xi_ctx9 = bsc(M_MID9, n_dim)
    Xi_mid9 = Xi_ctx9 * Xi_mid8[:M_MID9]
    Xi_ctx10 = bsc(M_MID10, n_dim)
    Xi_mid10 = Xi_ctx10 * Xi_mid9[:M_MID10]
    Xi_ctx11 = bsc(M_OUTER, n_dim)
    Xi_outer = Xi_ctx11 * Xi_mid10[:M_OUTER]

    W_inner = (Xi_inner.t() @ Xi_inner) / n_dim
    W_mid2 = (Xi_mid2.t() @ Xi_mid2) / n_dim
    W_mid3 = (Xi_mid3.t() @ Xi_mid3) / n_dim
    W_mid4 = (Xi_mid4.t() @ Xi_mid4) / n_dim
    W_mid5 = (Xi_mid5.t() @ Xi_mid5) / n_dim
    W_mid6 = (Xi_mid6.t() @ Xi_mid6) / n_dim
    W_mid7 = (Xi_mid7.t() @ Xi_mid7) / n_dim
    W_mid8 = (Xi_mid8.t() @ Xi_mid8) / n_dim
    W_mid9 = (Xi_mid9.t() @ Xi_mid9) / n_dim
    W_mid10 = (Xi_mid10.t() @ Xi_mid10) / n_dim
    W_outer = (Xi_outer.t() @ Xi_outer) / n_dim

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after W build: {mem_gb:.3f} GB", flush=True)

    level_fids = {f"L{l}": [] for l in range(1, L_DEPTH + 1)}
    l11_acc = []

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0

        xi_L11_ret = hopfield_retrieve_gpu(W_outer, probe)
        xi_L10_ptr = xi_L11_ret * Xi_ctx11[q_idx]
        xi_L10_ret = hopfield_retrieve_gpu(W_mid10, xi_L10_ptr)
        xi_L9_ptr = xi_L10_ret * Xi_ctx10[q_idx]
        xi_L9_ret = hopfield_retrieve_gpu(W_mid9, xi_L9_ptr)
        xi_L8_ptr = xi_L9_ret * Xi_ctx9[q_idx]
        xi_L8_ret = hopfield_retrieve_gpu(W_mid8, xi_L8_ptr)
        xi_L7_ptr = xi_L8_ret * Xi_ctx8[q_idx]
        xi_L7_ret = hopfield_retrieve_gpu(W_mid7, xi_L7_ptr)
        xi_L6_ptr = xi_L7_ret * Xi_ctx7[q_idx]
        xi_L6_ret = hopfield_retrieve_gpu(W_mid6, xi_L6_ptr)
        xi_L5_ptr = xi_L6_ret * Xi_ctx6[q_idx]
        xi_L5_ret = hopfield_retrieve_gpu(W_mid5, xi_L5_ptr)
        xi_L4_ptr = xi_L5_ret * Xi_ctx5[q_idx]
        xi_L4_ret = hopfield_retrieve_gpu(W_mid4, xi_L4_ptr)
        xi_L3_ptr = xi_L4_ret * Xi_ctx4[q_idx]
        xi_L3_ret = hopfield_retrieve_gpu(W_mid3, xi_L3_ptr)
        xi_L2_ptr = xi_L3_ret * Xi_ctx3[q_idx]
        xi_L2_ret = hopfield_retrieve_gpu(W_mid2, xi_L2_ptr)
        xi_L1_ptr = xi_L2_ret * Xi_ctx2[q_idx]
        xi_L1_ret = hopfield_retrieve_gpu(W_inner, xi_L1_ptr)

        xi_L1_true = Xi_inner[q_idx]
        xi_L2_true = Xi_mid2[q_idx]
        xi_L3_true = Xi_mid3[q_idx]
        xi_L4_true = Xi_mid4[q_idx]
        xi_L5_true = Xi_mid5[q_idx]
        xi_L6_true = Xi_mid6[q_idx]
        xi_L7_true = Xi_mid7[q_idx]
        xi_L8_true = Xi_mid8[q_idx]
        xi_L9_true = Xi_mid9[q_idx]
        xi_L10_true = Xi_mid10[q_idx]

        level_fids["L11"].append(cosine_sim_gpu(xi_L11_ret, xi_outer_true))
        level_fids["L10"].append(cosine_sim_gpu(xi_L10_ret, xi_L10_true))
        level_fids["L9"].append(cosine_sim_gpu(xi_L9_ret, xi_L9_true))
        level_fids["L8"].append(cosine_sim_gpu(xi_L8_ret, xi_L8_true))
        level_fids["L7"].append(cosine_sim_gpu(xi_L7_ret, xi_L7_true))
        level_fids["L6"].append(cosine_sim_gpu(xi_L6_ret, xi_L6_true))
        level_fids["L5"].append(cosine_sim_gpu(xi_L5_ret, xi_L5_true))
        level_fids["L4"].append(cosine_sim_gpu(xi_L4_ret, xi_L4_true))
        level_fids["L3"].append(cosine_sim_gpu(xi_L3_ret, xi_L3_true))
        level_fids["L2"].append(cosine_sim_gpu(xi_L2_ret, xi_L2_true))
        level_fids["L1"].append(cosine_sim_gpu(xi_L1_ret, xi_L1_true))
        l11_acc.append(cosine_sim_gpu(xi_L1_ret, xi_L1_true))

    mean_fids = {k: float(sum(v) / len(v)) if v else 0.0 for k, v in level_fids.items()}
    mean_l11 = float(sum(l11_acc) / len(l11_acc)) if l11_acc else 0.0

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] fids={' '.join(f'{k}:{mean_fids[k]:.4f}' for k in sorted(mean_fids.keys()))} "
          f"l11_acc={mean_l11:.4f} peak_gpu={peak_mem:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "l11_accuracy": float(mean_l11),
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

    fid_vals = {}
    for l in range(1, L_DEPTH + 1):
        fid_vals[f"L{l}"] = mean_key(f"fid_l{l}")
    l11_acc = mean_key("l11_accuracy")

    fid_list = [fid_vals[f"L{l}"] for l in range(1, L_DEPTH + 1)]
    summary = (" ".join(f"L{l}:{fid_vals[f'L{l}']:.4f}" for l in range(1, L_DEPTH + 1)) +
               f" l11_acc={l11_acc:.4f}(HP>={HP_LACC} HF<{HF_LACC}) n_seeds={len(results)}")

    if any(f < HF_FIDELITY for f in fid_list) or l11_acc < HF_LACC:
        return ("HARD_FAIL", f"HARD_FAIL: any fid<{HF_FIDELITY} or l11_acc<{HF_LACC}. {summary}")

    all_unanimous = all(f >= HP_FIDELITY_UNANI_THRESH for f in fid_list)
    if all_unanimous and l11_acc >= HP_LACC:
        return ("HARD_PASS", f"HARD_PASS: all {L_DEPTH} levels EXACT-1.0 unanimous + l11_acc HP. {summary}")

    any_below_middle = any(f < MIDDLE_FIDELITY for f in fid_list)
    if any_below_middle:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: graceful degradation (some fid<{MIDDLE_FIDELITY}). {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: some fids in [{MIDDLE_FIDELITY},1.0). {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} L={L_DEPTH}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "L": L_DEPTH, "run_mode": RUN_MODE}
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
    "N": N, "L": L_DEPTH, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         **{f"fid_l{l}": r.get(f"fid_l{l}") for l in range(1, L_DEPTH + 1)},
         "l11_accuracy": r.get("l11_accuracy"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
