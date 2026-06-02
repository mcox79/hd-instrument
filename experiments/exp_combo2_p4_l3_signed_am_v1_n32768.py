"""
combo2_p4_l3_signed_am_v1_n32768 -- COMBO-2: p=4 DAM + L3 + signed-AM at N=32768.

Extends n16384 (HARD_PASS) to N=32768, the maximum local-GPU push.

VRAM STRATEGY (load-bearing -- W NxN float32 at N=32768 would be 4.29 GB):
  Do NOT materialize full W matrix. Use matrix-free operations on Xi (M x N) only.
  p=4 retrieve: h = Xi.T @ (Xi @ state)^3 / N  -- two batched matmuls, no W.
  Peak VRAM = Xi_inner (float32) + Xi_outer layers + temp buffers:
    Xi_inner (M_INNER=64 x N=32768) = 64*32768*4 = 8.4 MB
    Xi_outer layers: similar scale. Total < 200 MB. Safe on 8 GB GPU.

PRE-REGISTERED BANDS (inherited from n16384 HARD_PASS):
  HARD-PASS: HP1 AND HP2 AND HP3 (all 3).
    HP1: l3_fidelity_A >= 0.85
    HP2: b_repulsion_rate >= 0.95
    HP3: parity_contamination <= 0.05
  HARD-FAIL: l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50.
  MIDDLE: 2/3 conditions met.
  Calibration: prior anchor n16384 (HARD_PASS); bands inherited.

FORMULA SELF-TESTS:
  1. p=4 matfree: h = Xi.T @ (Xi @ xi)^3 / n; for M=1 Xi=[xi], h = xi * n^2.
     [INPUT: xi=[1,1,-1,1], n=4, M=1] [EXPECTED: h = xi * 16.0]
  2. Hadamard binding: xi_b = xi_a * xi_ctx; decode = xi_b * xi_ctx = xi_a.
     [INPUT: xi_a=[1,-1,1,-1], xi_ctx=[1,1,-1,-1]] [EXPECTED: decode = xi_a]
  3. signed-AM repulsion: h = -Xi_B.T @ (Xi_B @ eta) / N; retrieves ~-eta.
     [INPUT: N=64, single eta] [EXPECTED: retrieved anti-cosine ~ 1.0]
  4. GPU guard: cuda.memory_allocated() > 0 after tensor creation on device.

PROT-018: anchor has _n32768; N MUST = 32768.
PROT-021: run_config includes N, M_inner, run_mode.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

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

ANCHOR_NAME = "combo2_p4_l3_signed_am_v1_n32768"

# PROT-018: anchor has _n32768 -> N must = 32768
_N_SUFFIX = 32768
N = 32768
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_ACTIVE = 1024
    SEEDS = [7, 17]
    M_INNER = 4
    M_MID = 2
    M_OUTER = 2
    M_B = 2
    N_QUERIES = 2
    NOISE_FRAC = 0.10
else:
    N_ACTIVE = N   # 32768
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 64
    M_MID = 32
    M_OUTER = 16
    M_B = 16
    N_QUERIES = 30
    NOISE_FRAC = 0.10

HP_L3_FIDELITY = 0.85
HP_B_REPULSION = 0.95
HP_PARITY_CONTAMINATION = 0.05
HF_L3_FIDELITY = 0.50
HF_B_REPULSION = 0.50
ALPHA_C = 0.138


def _selftest_p4_matfree():
    """p=4 matrix-free: h = Xi.T @ (Xi @ xi)^3 / n."""
    n = 4
    xi = torch.tensor([1.0, 1.0, -1.0, 1.0], dtype=torch.float32, device=DEVICE)
    Xi = xi.unsqueeze(0)   # (1, n)
    overlaps = Xi @ xi     # (1,)
    h = (Xi.t() @ overlaps.unsqueeze(0).pow(3)) / n  # (n, 1) -> (n,)
    h = h.squeeze(1)
    expected = xi * (n ** 2)
    assert torch.allclose(h, expected, atol=1e-4), f"p4 matfree: got {h}, expected {expected}"


def _selftest_hadamard():
    xi_a = torch.tensor([1.0, -1.0, 1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi_b = torch.tensor([1.0, 1.0, -1.0, -1.0], dtype=torch.float32, device=DEVICE)
    bound = xi_a * xi_b
    decoded = bound * xi_a
    assert torch.allclose(decoded, xi_b, atol=1e-6), f"Hadamard: {decoded} != {xi_b}"


def _selftest_signed_am():
    n = 64
    rng = torch.Generator(device=DEVICE)
    rng.manual_seed(0)
    eta_b = torch.randint(0, 2, (n,), generator=rng, device=DEVICE).float() * 2 - 1
    # Repulsion: h_B = -Xi_B.T @ (Xi_B @ eta) / N; anti-converges
    Xi_B = eta_b.unsqueeze(0)  # (1, n)
    h = -(Xi_B.t() @ (Xi_B @ eta_b).unsqueeze(0)) / n  # (n,)
    h = h.squeeze(1)
    retrieved = torch.sign(h)
    retrieved[retrieved == 0] = 1.0
    anti_cos = float(torch.dot(retrieved, -eta_b) / n)
    assert anti_cos >= 0.5, f"signed_AM repulsion anti_cos={anti_cos:.4f} < 0.5"


def _instrumentation_selftest():
    _selftest_p4_matfree()
    _selftest_hadamard()
    _selftest_signed_am()
    # GPU memory check
    mem_before = torch.cuda.memory_allocated(0)
    dummy = torch.zeros((1024, 1024), device=DEVICE, dtype=torch.float32)
    mem_after = torch.cuda.memory_allocated(0)
    assert mem_after > mem_before, f"GPU memory not increasing: before={mem_before} after={mem_after}"
    del dummy
    # Capacity check at active N
    n_dim = N_ACTIVE
    alpha_inner = M_INNER / n_dim
    alpha_b = M_B / n_dim
    assert alpha_inner + alpha_b < ALPHA_C, f"alpha {alpha_inner+alpha_b:.4f} >= alpha_c={ALPHA_C}"
    print(f"[selftest] PASS: p4_matfree, hadamard, signed_am, gpu_mem_ok, capacity_ok "
          f"N={n_dim} alpha_inner={alpha_inner:.4f} alpha_b={alpha_b:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p4_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor,
                    n_steps: int = 5, n: int = None) -> torch.Tensor:
    """Matrix-free p=4 retrieval: h = Xi.T @ (Xi @ state)^3 / n."""
    if n is None:
        n = probe.shape[0]
    state = probe.clone()
    for _ in range(n_steps):
        overlaps = Xi @ state          # (M,)
        h = Xi.t() @ overlaps.pow(3)  # (N,)
        h = h / n
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
    rng = torch.Generator(device=DEVICE)
    rng.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=rng, device=DEVICE).float() * 2 - 1)

    Xi_inner = bsc(M_INNER, n_dim)    # (M_INNER, n_dim)
    Xi_ctx2 = bsc(M_MID, n_dim)
    Xi_mid = Xi_ctx2 * Xi_inner[:M_MID]    # Hadamard binding
    Xi_ctx3 = bsc(M_OUTER, n_dim)
    Xi_outer = Xi_ctx3 * Xi_mid[:M_OUTER]

    Xi_A_sub = bsc(M_B, n_dim)
    Xi_B = bsc(M_B, n_dim)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)

    # L3 end-to-end fidelity
    l3_fidelities = []
    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=rng, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0

        xi_outer_ret = p4_retrieve_gpu(Xi_outer, probe, n=n_dim)
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx]
        xi_mid_ret = p4_retrieve_gpu(Xi_mid, xi_mid_ptr, n=n_dim)
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx]
        xi_inner_ret = p4_retrieve_gpu(Xi_inner, xi_inner_ptr, n=n_dim)
        xi_inner_true = Xi_inner[q_idx]
        fid = cosine_sim_gpu(xi_inner_ret, xi_inner_true)
        l3_fidelities.append(fid)

    l3_fid_mean = float(sum(l3_fidelities) / len(l3_fidelities)) if l3_fidelities else 0.0

    # B-repulsion (signed-AM: h = Xi_A.T(Xi_A@s)^3 - Xi_B.T(Xi_B@s)^3) / n
    repulsion_count = 0
    n_b_queries = min(N_QUERIES, M_B)
    for b_idx in range(n_b_queries):
        eta_b = Xi_B[b_idx]
        state = eta_b.clone()
        flip_mask = (torch.rand(n_dim, generator=rng, device=DEVICE) < NOISE_FRAC)
        state[flip_mask] *= -1.0
        for _ in range(5):
            ov_A = Xi_A_sub @ state
            ov_B = Xi_B @ state
            h = (Xi_A_sub.t() @ ov_A.pow(3) - Xi_B.t() @ ov_B.pow(3)) / n_dim
            state = torch.sign(h)
            state[state == 0] = 1.0
        cos_to_b = cosine_sim_gpu(state, eta_b)
        if cos_to_b < -0.3:
            repulsion_count += 1

    b_repulsion_rate = repulsion_count / n_b_queries if n_b_queries > 0 else 0.0

    # Parity contamination
    contamination_flags = 0
    n_contam = min(N_QUERIES, M_OUTER, M_B)
    for q_idx in range(n_contam):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=rng, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0
        xi_outer_ret = p4_retrieve_gpu(Xi_outer, probe, n=n_dim)
        xi_mid_ptr = xi_outer_ret * Xi_ctx3[q_idx]
        xi_mid_ret = p4_retrieve_gpu(Xi_mid, xi_mid_ptr, n=n_dim)
        xi_inner_ptr = xi_mid_ret * Xi_ctx2[q_idx]
        xi_inner_ret = p4_retrieve_gpu(Xi_inner, xi_inner_ptr, n=n_dim)
        max_b_cos = max(
            abs(cosine_sim_gpu(xi_inner_ret, Xi_B[b])) for b in range(M_B)
        )
        if max_b_cos > 0.5:
            contamination_flags += 1

    parity_contamination = contamination_flags / n_contam if n_contam > 0 else 0.0

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] l3_fid={l3_fid_mean:.4f} b_repulsion={b_repulsion_rate:.4f} "
          f"parity_contam={parity_contamination:.4f} peak_gpu={peak_mem_gb:.3f}GB "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "M_inner": M_INNER, "M_mid": M_MID, "M_outer": M_OUTER, "M_B": M_B,
        "l3_fidelity_A": float(l3_fid_mean),
        "b_repulsion_rate": float(b_repulsion_rate),
        "parity_contamination": float(parity_contamination),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    l3_fids = [r["l3_fidelity_A"] for r in results if "l3_fidelity_A" in r]
    b_reps = [r["b_repulsion_rate"] for r in results if "b_repulsion_rate" in r]
    p_conts = [r["parity_contamination"] for r in results if "parity_contamination" in r]

    if not l3_fids:
        return ("HARD_FAIL", "No valid results.")

    mean_l3 = float(sum(l3_fids) / len(l3_fids))
    mean_brep = float(sum(b_reps) / len(b_reps))
    mean_pcont = float(sum(p_conts) / len(p_conts))

    summary = (f"l3_fidelity_A={mean_l3:.4f} (HP>={HP_L3_FIDELITY} HF<{HF_L3_FIDELITY}) "
               f"b_repulsion={mean_brep:.4f} (HP>={HP_B_REPULSION} HF<{HF_B_REPULSION}) "
               f"parity_contamination={mean_pcont:.4f} (HP<={HP_PARITY_CONTAMINATION}) "
               f"n_seeds={len(l3_fids)}")

    if mean_l3 < HF_L3_FIDELITY or mean_brep < HF_B_REPULSION:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = mean_l3 >= HP_L3_FIDELITY
    hp2 = mean_brep >= HP_B_REPULSION
    hp3 = mean_pcont <= HP_PARITY_CONTAMINATION

    if hp1 and hp2 and hp3:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met at N=32768. {summary}")
    if sum([hp1, hp2, hp3]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3])}/3 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {sum([hp1,hp2,hp3])}/3 HP conditions. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name '{ANCHOR_NAME}' binds to "
            f"N={_N_SUFFIX} but script running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"matrix_free=True VRAM_peak_est_MB={M_INNER*N_ACTIVE*4/1e6:.1f}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_inner": M_INNER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} M_inner={M_INNER} M_outer={M_OUTER} M_B={M_B}...",
          flush=True)
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
    "mean_l3_fidelity_A": float(sum(r["l3_fidelity_A"] for r in all_results) / len(all_results)) if all_results else None,
    "mean_b_repulsion_rate": float(sum(r["b_repulsion_rate"] for r in all_results) / len(all_results)) if all_results else None,
    "mean_parity_contamination": float(sum(r["parity_contamination"] for r in all_results) / len(all_results)) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
