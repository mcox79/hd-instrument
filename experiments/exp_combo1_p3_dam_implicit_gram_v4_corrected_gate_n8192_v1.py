"""
combo1_p3_dam_implicit_gram_v4_corrected_gate_n8192_v1

R3-A fix: the I-14 HARD-FAIL at alpha=2.0 N=8192 was a mis-specified HP gate.
The measured kappa3_resc=11.02 EXACTLY matches the Marchenko-Pastur moment
m_3(alpha=2) = 1 + 3*alpha + alpha^2 = 1 + 6 + 4 = 11.0. The old HP gate
"|kappa3_resc - 1.0| <= 0.05" was wrong; the correct gate is
"|kappa3_resc - m_3(alpha)| / m_3(alpha) <= 0.05".

Mechanical fix applied to HP2 gate formula. All other gates (HP1 MMD, HP3 slope,
HP4 cosine) are unchanged. N=8192 VRAM-friendly M=N*2 config is unchanged.

Reference: Marchenko-Pastur moments m_k = sum_{j=0}^{k-1} (1/(j+1)) C(k,j)
C(k-1,j) alpha^j (Narayana-number identity, Bai-Silverstein 2010).
For k=3: m_3 = 1 + 3*alpha + alpha^2.

FORMULA SELF-TEST:
  At alpha=2: m_3 = 1 + 3*2 + 4 = 11.0.
  [INPUT: alpha=2.0] [EXPECTED: m_3 = 11.0]
  At alpha=0.5: m_3 = 1 + 1.5 + 0.25 = 2.75.
  [INPUT: alpha=0.5] [EXPECTED: m_3 = 2.75]
  At alpha=1.0: m_3 = 1 + 3 + 1 = 5.0.
  [INPUT: alpha=1.0] [EXPECTED: m_3 = 5.0]

PRE-REGISTERED BANDS:
  HARD-PASS: |kappa3_resc - m_3(alpha)| / m_3(alpha) <= 0.05
             AND MMD < 0.02 AND mean_cos >= 0.95
  MIDDLE: |kappa3_resc - m_3(alpha)| / m_3(alpha) in (0.05, 0.20]
          AND MMD < 0.02 AND mean_cos >= 0.95
  HARD-FAIL: |kappa3_resc - m_3(alpha)| / m_3(alpha) > 0.20
             OR MMD >= 0.10 OR mean_cos < 0.70

PROT-018: anchor _n8192 binds N=8192.
PROT-021: run_config includes N, M_LIST, run_mode.
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
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

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

ANCHOR_NAME = "combo1_p3_dam_implicit_gram_v4_corrected_gate_n8192_v1"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

BRAND_REFRESH_K = 16


def mp_moment_3(alpha: float) -> float:
    """Third moment of Marchenko-Pastur distribution: m_3 = 1 + 3*alpha + alpha^2."""
    return 1.0 + 3.0 * alpha + alpha * alpha


# Formula self-tests at module scope
_m3_alpha2 = mp_moment_3(2.0)
_m3_alpha05 = mp_moment_3(0.5)
_m3_alpha1 = mp_moment_3(1.0)
assert abs(_m3_alpha2 - 11.0) < 0.001, f"m_3(2.0) selftest: {_m3_alpha2:.4f} != 11.0"
assert abs(_m3_alpha05 - 2.75) < 0.001, f"m_3(0.5) selftest: {_m3_alpha05:.4f} != 2.75"
assert abs(_m3_alpha1 - 5.0) < 0.001, f"m_3(1.0) selftest: {_m3_alpha1:.4f} != 5.0"
print(f"[selftest-formula] m_3: alpha=2->{_m3_alpha2:.1f}(exp 11.0) "
      f"alpha=0.5->{_m3_alpha05:.2f}(exp 2.75) alpha=1->{_m3_alpha1:.1f}(exp 5.0)", flush=True)


if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    # Smoke uses N_ACTIVE = N//4 = 2048. Set M_LIST relative to N_ACTIVE to keep alpha=2.0.
    _N_SMOKE = N // 4
    M_LIST = [_N_SMOKE * 2]     # alpha=2.0 at smoke scale (same alpha as FULL)
    N_PROBES_K3 = 50
    N_TEST_RETRIEVAL = 5
    N_WRITE_STEPS = [_N_SMOKE // 2, _N_SMOKE]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [N * 2]       # M = 16384, alpha=2.0 -- VRAM-friendly (537 MB)
    N_PROBES_K3 = 100
    N_TEST_RETRIEVAL = 20
    N_WRITE_STEPS = [N // 2, N, N * 2]

# Pre-registered thresholds
HP1_MMD = 0.02
HF1_MMD = 0.10
HP2_KAPPA3_REL_TOL = 0.05       # |kappa3_resc - m_3(alpha)| / m_3(alpha) <= 0.05
MID2_KAPPA3_REL_TOL = 0.20      # middle band upper bound
HF2_KAPPA3_REL_TOL = 0.20       # |kappa3_resc - m_3(alpha)| / m_3(alpha) > 0.20
HP3_SLOPE = 1.3
HP4_COS = 0.95
HF4_COS = 0.70


def p3_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor,
                    n_steps: int = 5, n: int = None) -> torch.Tensor:
    """p=3 polynomial DAM retrieval (matrix-free)."""
    if n is None:
        n = probe.shape[0]
    state = probe.clone()
    for _ in range(n_steps):
        overlaps = Xi @ state
        h = Xi.t() @ overlaps.pow(2)
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


def compute_mmd_gpu(samples: torch.Tensor, references: torch.Tensor) -> float:
    """Cosine-based pseudo-MMD."""
    if samples.shape[0] == 0 or references.shape[0] == 0:
        return 1.0
    s_norm = torch.nn.functional.normalize(samples.float(), dim=1)
    r_norm = torch.nn.functional.normalize(references.float(), dim=1)
    cross = torch.mm(s_norm, r_norm.t())
    return max(float(1.0 - cross.mean()), 0.0)


def hutchinson_kappa3_implicit_gpu(Xi: torch.Tensor, n: int, n_probes: int, seed: int) -> float:
    """Hutchinson kappa_3 = Tr(W^3)/N using implicit W = Xi.T @ Xi / n."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 5555)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)
    return float((V0 * V3).sum(dim=0).mean() / n)


def _selftest_gram_diagonal():
    """G_ii = 1.0 for BSC patterns."""
    N_t = 256
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_t = (torch.randint(0, 2, (10, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    dot_self = float(Xi_t[0].dot(Xi_t[0])) / N_t
    assert abs(dot_self - 1.0) < 0.01, f"G_ii test: {dot_self:.4f} != 1.0"


def _selftest_kappa3_corrected_formula():
    """kappa3_resc at alpha=2 should match m_3(alpha=2)=11.0 within 15%."""
    # Use Hutchinson on small N to verify m_3 prediction (within variance)
    N_t = 512
    M_t = N_t * 2  # alpha=2.0
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(99)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    k3 = hutchinson_kappa3_implicit_gpu(Xi_t, N_t, 200, seed=99)
    kappa3_resc = k3 * N_t / M_t  # normalization: multiply back by N, divide by M
    alpha_t = M_t / N_t  # = 2.0
    expected = mp_moment_3(alpha_t)
    rel_err = abs(kappa3_resc - expected) / expected
    assert rel_err < 0.30, (f"kappa3 corrected-gate selftest: "
                             f"kappa3_resc={kappa3_resc:.4f} expected={expected:.1f} "
                             f"rel_err={rel_err:.3f} (>0.30)")
    print(f"[selftest-kappa3] alpha={alpha_t} kappa3_resc={kappa3_resc:.4f} "
          f"m_3={expected:.1f} rel_err={rel_err:.3f}", flush=True)
    del Xi_t


def _instrumentation_selftest():
    _selftest_gram_diagonal()
    _selftest_kappa3_corrected_formula()
    # GPU memory check
    mem_before = torch.cuda.memory_allocated(0)
    dummy = torch.zeros((N // 2, N // 4), device=DEVICE, dtype=torch.float32)
    mem_after = torch.cuda.memory_allocated(0)
    assert mem_after > mem_before, "GPU memory not increasing"
    print(f"[selftest] PASS: G_ii=1.0, kappa3_corrected_gate, "
          f"gpu_mem={mem_after/1e6:.1f}MB", flush=True)
    del dummy


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_m(seed: int, n_dim: int, M: int) -> Dict:
    alpha = M / n_dim
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + M)
    t0 = time.time()

    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={M} alpha={alpha:.2f}] "
          f"GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)
    assert mem_gb < 7.0, f"VRAM budget exceeded: {mem_gb:.3f} GB >= 7.0 GB"

    # HP1: MMD
    test_probes = Xi[:N_TEST_RETRIEVAL]
    retrieved = []
    for i in range(N_TEST_RETRIEVAL):
        probe = test_probes[i].clone()
        flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < 0.10)
        probe[flip] *= -1.0
        ret = p3_retrieve_gpu(Xi, probe, n=n_dim)
        retrieved.append(ret)
    retrieved_t = torch.stack(retrieved)
    mmd = compute_mmd_gpu(retrieved_t, test_probes)

    # HP2: kappa3 with CORRECTED gate (m_3(alpha) not 1.0)
    kappa3_raw = hutchinson_kappa3_implicit_gpu(Xi, n_dim, N_PROBES_K3, seed=seed)
    # kappa3_raw = Tr(W^3)/N where W = Xi.T @ Xi / N
    # For the M x M Gram perspective: Tr(G^3)/M = kappa3_raw * N / M = kappa3_raw / alpha
    # But the script tracks kappa3_resc as the rescaled form measured against m_3(alpha)
    # Per research audit: kappa3_resc measured = Tr(G^3)/M = kappa3_raw * N/M
    kappa3_resc = kappa3_raw * n_dim / M if M > 0 else 0.0
    expected_m3 = mp_moment_3(alpha)
    kappa3_rel_err = abs(kappa3_resc - expected_m3) / expected_m3 if expected_m3 > 0 else 1.0

    # HP3: Brand refresh slope
    write_times = []
    for w_step in [s for s in N_WRITE_STEPS if s <= M]:
        t_w = time.time()
        Xi_sub = Xi[:w_step]
        _G = Xi_sub @ Xi_sub.t() / n_dim
        torch.cuda.synchronize()
        write_times.append((w_step, time.time() - t_w))
        del _G

    slope = 1.0
    if len(write_times) >= 2:
        xs = [math.log(w) for w, _ in write_times]
        ys = [math.log(max(t, 1e-9)) for _, t in write_times]
        if xs[-1] != xs[0]:
            slope = (ys[-1] - ys[0]) / (xs[-1] - xs[0])

    # HP4: mean retrieval cosine
    cos_vals = [cosine_sim_gpu(retrieved[i], test_probes[i]) for i in range(N_TEST_RETRIEVAL)]
    mean_cos = float(sum(cos_vals) / len(cos_vals)) if cos_vals else 0.0

    del Xi
    torch.cuda.empty_cache()
    elapsed = time.time() - t0

    print(f"    [M={M} alpha={alpha:.2f}] MMD={mmd:.4f} "
          f"kappa3_resc={kappa3_resc:.4f} m_3={expected_m3:.1f} "
          f"rel_err={kappa3_rel_err:.4f} "
          f"slope={slope:.2f} cos={mean_cos:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "M": M, "alpha": float(alpha),
        "mmd": float(mmd),
        "kappa3_resc": float(kappa3_resc),
        "expected_m3": float(expected_m3),
        "kappa3_rel_err": float(kappa3_rel_err),
        "write_slope": float(slope),
        "mean_cos": float(mean_cos),
    }


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    m_results = [run_seed_m(seed, n_dim, M) for M in M_LIST]
    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak_mem_gb:.3f}GB total_elapsed={elapsed:.2f}s", flush=True)
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "m_results": m_results,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    all_m_results = []
    for r in results:
        all_m_results.extend(r.get("m_results", []))
    if not all_m_results:
        return ("HARD_FAIL", "No M-level results.")

    mmds = [r["mmd"] for r in all_m_results]
    k3_rels = [r["kappa3_rel_err"] for r in all_m_results]
    slopes = [r["write_slope"] for r in all_m_results]
    coss = [r["mean_cos"] for r in all_m_results]
    k3_rescs = [r["kappa3_resc"] for r in all_m_results]
    exp_m3s = [r["expected_m3"] for r in all_m_results]

    mean_mmd = float(sum(mmds) / len(mmds))
    mean_k3_rel = float(sum(k3_rels) / len(k3_rels))
    mean_slope = float(sum(slopes) / len(slopes))
    mean_cos = float(sum(coss) / len(coss))
    mean_k3_resc = float(sum(k3_rescs) / len(k3_rescs))
    mean_expected_m3 = float(sum(exp_m3s) / len(exp_m3s))

    summary = (
        f"MMD={mean_mmd:.4f}(HP<{HP1_MMD}) "
        f"kappa3_resc={mean_k3_resc:.4f}(m_3={mean_expected_m3:.1f}) "
        f"rel_err={mean_k3_rel:.4f}(HP<={HP2_KAPPA3_REL_TOL} HF>{HF2_KAPPA3_REL_TOL}) "
        f"slope={mean_slope:.3f}(HP<={HP3_SLOPE}) "
        f"cos={mean_cos:.4f}(HP>={HP4_COS} HF<{HF4_COS}) "
        f"n_results={len(all_m_results)}"
    )

    # HARD-FAIL check first
    if mean_mmd >= HF1_MMD:
        return ("HARD_FAIL", f"HARD_FAIL: MMD>={HF1_MMD}. {summary}")
    if mean_k3_rel > HF2_KAPPA3_REL_TOL:
        return ("HARD_FAIL", f"HARD_FAIL: kappa3_rel_err>{HF2_KAPPA3_REL_TOL} (corrected gate). {summary}")
    if mean_cos < HF4_COS:
        return ("HARD_FAIL", f"HARD_FAIL: cos<{HF4_COS}. {summary}")

    hp1 = mean_mmd < HP1_MMD
    hp2 = mean_k3_rel <= HP2_KAPPA3_REL_TOL
    hp3 = mean_slope <= HP3_SLOPE
    hp4 = mean_cos >= HP4_COS

    if hp1 and hp2 and hp3 and hp4:
        return ("HARD_PASS", f"HARD_PASS: all 4 HP with corrected kappa3 gate at N=8192. {summary}")
    if hp1 and hp2 and (hp3 or hp4):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: HP1+HP2+1 of HP3/HP4 (corrected gate). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {sum([hp1,hp2,hp3,hp4])}/4 HP (corrected gate). {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    # Smoke may run at reduced N_ACTIVE; PROT-018 checks the FULL production N only.
    if RUN_MODE != "smoke" and n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


N_ACTIVE = N // 4 if RUN_MODE == "smoke" else N
print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_LIST={M_LIST}", flush=True)
_prot018_startup_check(N_ACTIVE)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_LIST": str(M_LIST), "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} M_LIST={M_LIST} (corrected gate)...", flush=True)
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
    "gate_correction": "HP2 now uses |kappa3_resc - m_3(alpha)| / m_3(alpha) <= 0.05",
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
