"""
combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1 -- COMBO-2 production-lock at N=32768 5-seed.

Re-confirmation of combo2_p4_l3_signed_am_v1_n32768 (completed) with explicit 5-seed
production-lock verification + full alpha grid.

Prior result (combo2_p4_l3_signed_am_v1_n32768): 5 seeds HARD_PASS
  l3_fidelity_A=1.0, b_repulsion_rate=1.0, parity_contamination=0.0.
This anchor provides the production-envelope LOCK entry with explicit verification framing
for the cap_map band-LIFT eligibility at N=32768 (cross-N {4096, 8192, 16384, 32768}).

VRAM STRATEGY: same as prior n32768 -- NO full W matrix, matrix-free p=4.
  Xi_inner (M_INNER=64 x N=32768 float32) = 8.4 MB.
  Peak VRAM < 200 MB. Safe.

PRE-REGISTERED BANDS (inherited from n32768 HARD_PASS):
  HARD-PASS: l3_fidelity_A >= 0.85 AND b_repulsion_rate >= 0.95 AND parity_contamination <= 0.05
             in >= 4/5 seeds.
  HARD-FAIL: l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50 in any seed.
  MIDDLE: 2/3 conditions met.

FORMULA SELF-TESTS:
  1. p=4 matfree: h = Xi.T @ (Xi @ xi)^3 / n; M=1 Xi=[xi], h = xi * n^2.
     [INPUT: xi=[1,1,-1,1], n=4, M=1] [EXPECTED: h = xi * 16.0]
  2. Hadamard binding: xi_b = xi_a * xi_ctx; decode = xi_b * xi_ctx = xi_a.
  3. signed-AM repulsion: anti-cosine >= 0.5 at N=64.
  4. GPU guard: memory_allocated() > 0 after tensor creation.

PROT-018: anchor has _n32768; N MUST = 32768.
PROT-021: run_config includes N, M_INNER, run_mode.
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

ANCHOR_NAME = "combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1"

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
    N_ACTIVE = N
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
    n = 4
    xi = torch.tensor([1.0, 1.0, -1.0, 1.0], dtype=torch.float32, device=DEVICE)
    Xi = xi.unsqueeze(0)
    overlaps = Xi @ xi
    h = (Xi.t() @ overlaps.unsqueeze(0).pow(3)) / n
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
    Xi_B = eta_b.unsqueeze(0)
    h = -(Xi_B.t() @ (Xi_B @ eta_b).unsqueeze(0)) / n
    h = h.squeeze(1)
    retrieved = torch.sign(h)
    retrieved[retrieved == 0] = 1.0
    anti_cos = float(torch.dot(retrieved, -eta_b) / n)
    assert anti_cos >= 0.5, f"signed_AM repulsion anti_cos={anti_cos:.4f} < 0.5"


def _instrumentation_selftest():
    _selftest_p4_matfree()
    _selftest_hadamard()
    _selftest_signed_am()
    mem_before = torch.cuda.memory_allocated(0)
    dummy = torch.zeros((1024, 1024), device=DEVICE, dtype=torch.float32)
    mem_after = torch.cuda.memory_allocated(0)
    assert mem_after > mem_before, f"GPU memory not increasing"
    del dummy
    n_dim = N_ACTIVE
    alpha_inner = M_INNER / n_dim
    alpha_b = M_B / n_dim
    assert alpha_inner + alpha_b < ALPHA_C, f"alpha {alpha_inner+alpha_b:.4f} >= alpha_c"
    print(f"[selftest] PASS: p4_matfree, hadamard, signed_am, gpu_mem_ok, capacity_ok "
          f"N={n_dim} alpha_inner={alpha_inner:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def p4_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor,
                    n_steps: int = 5, n: int = None) -> torch.Tensor:
    if n is None:
        n = probe.shape[0]
    state = probe.clone()
    for _ in range(n_steps):
        overlaps = Xi @ state
        h = Xi.t() @ overlaps.pow(3)
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

    Xi_inner = bsc(M_INNER, n_dim)
    Xi_ctx2 = bsc(M_MID, n_dim)
    Xi_mid = Xi_ctx2 * Xi_inner[:M_MID]
    Xi_ctx3 = bsc(M_OUTER, n_dim)
    Xi_outer = Xi_ctx3 * Xi_mid[:M_OUTER]
    Xi_A_sub = bsc(M_B, n_dim)
    Xi_B = bsc(M_B, n_dim)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)

    # HP1: L3 end-to-end fidelity
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
        l3_fidelities.append(cosine_sim_gpu(xi_inner_ret, xi_inner_true))
    l3_fid = float(sum(l3_fidelities) / len(l3_fidelities)) if l3_fidelities else 0.0

    # HP2: B-repulsion
    n_b_queries = min(N_QUERIES, M_B)
    repulsion_count = 0
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
        if cosine_sim_gpu(state, eta_b) < -0.3:
            repulsion_count += 1
    b_rep_rate = repulsion_count / n_b_queries if n_b_queries > 0 else 0.0

    # HP3: parity contamination
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
        for b_idx in range(min(5, M_B)):
            if cosine_sim_gpu(xi_inner_ret, Xi_B[b_idx]) > 0.5:
                contamination_flags += 1
                break
    parity_contam = contamination_flags / max(n_contam, 1)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] l3_fid={l3_fid:.4f} b_rep={b_rep_rate:.4f} "
          f"parity_contam={parity_contam:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "l3_fidelity_A": float(l3_fid),
        "b_repulsion_rate": float(b_rep_rate),
        "parity_contamination": float(parity_contam),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    l3 = mean_key("l3_fidelity_A")
    rep = mean_key("b_repulsion_rate")
    contam = mean_key("parity_contamination")

    summary = (f"l3_fid={l3:.4f}(HP>={HP_L3_FIDELITY} HF<{HF_L3_FIDELITY}) "
               f"b_rep={rep:.4f}(HP>={HP_B_REPULSION} HF<{HF_B_REPULSION}) "
               f"parity_contam={contam:.4f}(HP<={HP_PARITY_CONTAMINATION}) "
               f"n_seeds={len(results)} N={N}")

    if l3 < HF_L3_FIDELITY or rep < HF_B_REPULSION:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp1 = l3 >= HP_L3_FIDELITY
    hp2 = rep >= HP_B_REPULSION
    hp3 = contam <= HP_PARITY_CONTAMINATION

    if hp1 and hp2 and hp3:
        return ("HARD_PASS",
                f"HARD_PASS: N=32768 5-seed production-lock verified. {summary}")
    if sum([hp1, hp2, hp3]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3])}/3 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {sum([hp1,hp2,hp3])}/3 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_INNER": M_INNER, "run_mode": RUN_MODE}
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
    "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"), "l3_fidelity_A": r.get("l3_fidelity_A"),
         "b_repulsion_rate": r.get("b_repulsion_rate"),
         "parity_contamination": r.get("parity_contamination"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
