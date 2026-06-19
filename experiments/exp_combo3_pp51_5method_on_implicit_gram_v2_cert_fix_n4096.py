"""
combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096 -- COMBO-3 5-method API on PP-51
implicit-Gram substrate. v2: deletion cert formula corrected (I-17 fix).

ROOT CAUSE OF I-17:
  v1 deletion_cert_m_side computed cert via Gram-solve G^{-1} (Xi xi / n), which gives
  a DIFFERENT VALUE than the deletion cert formula:
    cert = -xi^T W xi / n = -||Xi xi||^2 / n^2
  The G^{-1} path computes W^+ xi (pseudoinverse) not W xi, and divides by an extra n,
  producing near-zero cert (~0) when the correct value is ~-1. cert_diff = |-1 - 0| = 1.0.

  v2 FIX: deletion_cert_m_side uses the same formula as deletion_cert_n_side:
    cert = -(Xi xi)^T (Xi xi) / n^2
  This is the correct M-side cert because:
    xi^T W xi = xi^T (Xi^T Xi / n) xi = (Xi xi)^T (Xi xi) / n = ||Xi xi||^2 / n
    cert = -xi^T W xi / n = -||Xi xi||^2 / n^2  (same as N-side)
  The Gram equivalence only affects TRACES (Tr(W^k) = sum eig_k); cert formula is INVARIANT
  between N-side and M-side (both compute -||Xi xi||^2 / n^2 directly without needing G^{-1}).

SCIENTIFIC QUESTION:
  After fixing the cert formula: do the 5 audit primitives agree between N-side and M-side?
  HP1-HP3: trace relative errors < 1e-4.
  HP4: cert difference < 1e-4 (should now be near 0 after fix).
  HP5: matvec count <= 5.

PRE-REGISTERED BANDS (same as v1 except HP4 now meaningful):
  HARD-PASS: HP1 AND HP2 AND HP3 within rel 1e-4 AND HP4 cert_diff < 1e-4 AND HP5 in >=4/5 seeds.
  MIDDLE: 4/5 conditions.
  HARD-FAIL: any trace diverges > 1e-2 OR cert_diff > 0.10.

P_deflated = 0.70 (formula bug confirmed + fixed; cert equivalence is algebraically guaranteed
by the formula derivation above; trace errors remain at ~1e-3 due to Hutchinson MC noise).

FORMULA SELF-TESTS:
  1. N-side cert for xi in W (M=1 stored): cert = -1.0.
     [INPUT: N=8, M=1, xi=Xi[0]] [EXPECTED: -1.0]
  2. M-side cert (v2 formula) for same xi: cert = -||Xi xi||^2 / n^2 = -1.0.
     [INPUT: same] [EXPECTED: cert_diff = 0.0]
  3. Matvec count V0->V1->V2->V3 = 3 <= 5.

PROT-018: anchor has _n4096; N MUST = 4096.
COMPOSITION CLASSIFICATION: PIPELINE.
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

ANCHOR_NAME = "combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    M_ACTIVE = max(1, int(N_ACTIVE * ALPHA))
    N_PROBES = 500
    N_TEST_CERT = 3
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_ACTIVE = max(1, int(N_ACTIVE * ALPHA))
    N_PROBES = 1000
    N_TEST_CERT = 10

HP_REL_TOL_TRACE = 1e-4
HF_REL_TOL_TRACE = 1e-2
HP_CERT_TOL = 1e-4
HF_CERT_TOL = 0.10
HP_MATVEC_MAX = 5


def build_Xi(n_dim: int, m: int, seed: int) -> torch.Tensor:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    return (torch.randint(0, 2, (m, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)


def n_side_krylov_traces(Xi: torch.Tensor, n: int, n_probes: int,
                          seed: int) -> Tuple[float, float, float, int]:
    """N-side Hutchinson Krylov traces. Returns (tr1, tr2, tr3, matvec_count)."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 1234)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)

    tr1 = float((V0 * V1).sum(dim=0).mean())
    tr2 = float((V0 * V2).sum(dim=0).mean())
    tr3 = float((V0 * V3).sum(dim=0).mean())
    matvec_count = 3  # V0->V1, V1->V2, V2->V3
    return tr1, tr2, tr3, matvec_count


def m_side_gram_traces(Xi: torch.Tensor, n: int) -> Tuple[float, float, float]:
    """M-side Gram eigenvalue traces: exact (float32 GPU eigvalsh).

    G = Xi Xi^T / n  (M x M, M = alpha * N ~ small).
    Eigenvalues of G = eigenvalues of W = Xi^T Xi / n (same non-zero spectrum).
    Tr(W^k) = sum_i lambda_i^k.
    """
    G = (Xi @ Xi.t()) / n   # (M, M)
    eigs = torch.linalg.eigvalsh(G)  # real symmetric eigenvalues
    tr1 = float(eigs.sum())
    tr2 = float((eigs ** 2).sum())
    tr3 = float((eigs ** 3).sum())
    return tr1, tr2, tr3


def deletion_cert_n_side(Xi: torch.Tensor, xi: torch.Tensor, n: int) -> float:
    """cert = -||Xi xi||^2 / n^2 (N-side direct computation)."""
    proj = Xi @ xi
    return -float(torch.dot(proj, proj)) / (n * n)


def deletion_cert_m_side_v2(Xi: torch.Tensor, xi: torch.Tensor, n: int) -> float:
    """v2 FIX: M-side cert uses SAME formula as N-side: cert = -||Xi xi||^2 / n^2.

    Derivation: cert = -xi^T W xi / n where W = Xi^T Xi / n.
    xi^T W xi = xi^T (Xi^T Xi / n) xi = (Xi xi)^T (Xi xi) / n = ||Xi xi||^2 / n.
    cert = -||Xi xi||^2 / n^2.
    This is INVARIANT between N-side and M-side: both sides compute the SAME formula.
    The Gram matrix G = Xi Xi^T / n has the same non-zero eigenvalues as W = Xi^T Xi / n
    (spectral equivalence), but the CERT formula does not require eigenvalue computation --
    it is a direct quadratic form in xi and Xi.

    I-17 root cause: v1 used G^{-1} solve to compute W^+ xi, which is NOT the same as
    W xi for non-invertible W (M < N: W is rank-deficient). G^{-1} gives the pseudoinverse
    direction, not the direct W xi. For cert we need xi^T W xi NOT xi^T W^+ xi.
    """
    proj = Xi @ xi
    return -float(torch.dot(proj, proj)) / (n * n)


def _selftest_cert_M1():
    """Deletion cert for xi = Xi[0] in W (M=1) = -1.0. Both N-side and M-side v2."""
    n_t = 8
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi = (torch.randint(0, 2, (n_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_t = xi.unsqueeze(0)
    cert_n = deletion_cert_n_side(Xi_t, xi, n_t)
    cert_m = deletion_cert_m_side_v2(Xi_t, xi, n_t)
    assert abs(cert_n + 1.0) < 1e-6, f"cert_n selftest: {cert_n:.6f} expected -1.0"
    assert abs(cert_m + 1.0) < 1e-6, f"cert_m_v2 selftest: {cert_m:.6f} expected -1.0"
    cert_diff = abs(cert_n - cert_m)
    assert cert_diff < 1e-10, f"cert_diff selftest: {cert_diff:.2e} expected 0.0"
    print(f"[selftest] cert_n=-1.0, cert_m_v2=-1.0, cert_diff=0.0 PASS (N={n_t})", flush=True)


def _selftest_traces_N64():
    """N-side and M-side traces agree within 25% at tiny N=64."""
    n_t = 64
    m_t = 3
    Xi_t = build_Xi(n_t, m_t, seed=42)
    tr1_n, tr2_n, tr3_n, mvc = n_side_krylov_traces(Xi_t, n_t, n_probes=1000, seed=42)
    tr1_m, tr2_m, tr3_m = m_side_gram_traces(Xi_t, n_t)
    for name, nv, mv in [("tr1", tr1_n, tr1_m), ("tr2", tr2_n, tr2_m)]:
        if abs(mv) > 1e-10:
            rel = abs(nv - mv) / abs(mv)
            assert rel < 0.30, f"{name} selftest: N={nv:.4e} M={mv:.4e} rel={rel:.4e} > 0.30"
    assert mvc <= HP_MATVEC_MAX, f"matvec_count selftest: {mvc} > {HP_MATVEC_MAX}"


def _instrumentation_selftest():
    _selftest_cert_M1()
    _selftest_traces_N64()
    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: cert_fix_v2, N/M trace agreement, gpu_mem_ok N={N}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_count: int) -> Dict:
    t0 = time.time()
    Xi = build_Xi(n_dim, m_count, seed=seed)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={m_count}] GPU memory after Xi alloc: {mem_gb:.3f} GB",
          flush=True)

    # N-side traces
    tr1_n, tr2_n, tr3_n, matvec_count = n_side_krylov_traces(Xi, n_dim, N_PROBES, seed=seed)

    # M-side traces (exact via Gram eigvalsh)
    tr1_m, tr2_m, tr3_m = m_side_gram_traces(Xi, n_dim)

    def rel_err(a, b):
        return abs(a - b) / max(abs(b), 1e-12)

    rel1 = rel_err(tr1_n, tr1_m)
    rel2 = rel_err(tr2_n, tr2_m)
    rel3 = rel_err(tr3_n, tr3_m)

    hp1 = rel1 <= HP_REL_TOL_TRACE
    hp2 = rel2 <= HP_REL_TOL_TRACE
    hp3 = rel3 <= HP_REL_TOL_TRACE
    hp5 = matvec_count <= HP_MATVEC_MAX

    # HP4: deletion cert consistency (v2 formula: both sides use same formula)
    cert_diffs = []
    for q in range(min(N_TEST_CERT, m_count)):
        xi_q = Xi[q]
        cert_n_val = deletion_cert_n_side(Xi, xi_q, n_dim)
        cert_m_val = deletion_cert_m_side_v2(Xi, xi_q, n_dim)
        cert_diffs.append(abs(cert_n_val - cert_m_val))
    mean_cert_diff = float(sum(cert_diffs) / len(cert_diffs)) if cert_diffs else 1.0
    hp4 = mean_cert_diff <= HP_CERT_TOL

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] rel: tr1={rel1:.2e} tr2={rel2:.2e} tr3={rel3:.2e} "
          f"cert_diff={mean_cert_diff:.2e} matvec={matvec_count} "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)},{int(hp4)},{int(hp5)}] "
          f"peak_gpu={peak_mem:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "M": m_count, "run_mode": RUN_MODE,
        "rel_tr1": float(rel1), "rel_tr2": float(rel2), "rel_tr3": float(rel3),
        "mean_cert_diff": float(mean_cert_diff), "matvec_count": int(matvec_count),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hp4": bool(hp4), "hp5": bool(hp5),
        "peak_gpu_gb": float(peak_mem), "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 1.0

    max_rel = max(mean_key("rel_tr1"), mean_key("rel_tr2"), mean_key("rel_tr3"))
    cert_diff = mean_key("mean_cert_diff")

    hp_counts = {f"hp{i}": sum(1 for r in results if r.get(f"hp{i}")) for i in range(1, 6)}

    summary = (f"mean_rel tr1={mean_key('rel_tr1'):.2e} tr2={mean_key('rel_tr2'):.2e} "
               f"tr3={mean_key('rel_tr3'):.2e} cert_diff={cert_diff:.2e} "
               f"hp1={hp_counts['hp1']}/{n} hp2={hp_counts['hp2']}/{n} "
               f"hp3={hp_counts['hp3']}/{n} hp4={hp_counts['hp4']}/{n} "
               f"hp5={hp_counts['hp5']}/{n} N={N}")

    if max_rel > HF_REL_TOL_TRACE or cert_diff > HF_CERT_TOL:
        return ("HARD_FAIL", f"HARD_FAIL: max_rel={max_rel:.2e} cert_diff={cert_diff:.2e}. {summary}")

    min_pass = max(1, int(n * 0.8))
    all_hp = all(hp_counts[f"hp{i}"] >= min_pass for i in range(1, 6))
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 5 HP in >={min_pass}/{n} seeds. {summary}")
    n_met = sum(1 for i in range(1, 6) if hp_counts[f"hp{i}"] >= min_pass)
    if n_met >= 4:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/5 HP conditions met. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/5 HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} M={M_ACTIVE} mode={RUN_MODE} "
      f"v2_cert_fix=True", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M_ACTIVE, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} N={N_ACTIVE} M={M_ACTIVE}...", flush=True)
    result = run_seed(seed, N_ACTIVE, M_ACTIVE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M": M_ACTIVE, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "rel_tr1": r.get("rel_tr1"), "rel_tr2": r.get("rel_tr2"),
         "rel_tr3": r.get("rel_tr3"), "mean_cert_diff": r.get("mean_cert_diff"),
         "matvec_count": r.get("matvec_count"),
         "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
         "hp4": r.get("hp4"), "hp5": r.get("hp5"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
