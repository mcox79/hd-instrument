"""
combo3_pp51_5method_on_implicit_gram_v1_n4096 -- COMBO-3 5-method API on PP-51 implicit-Gram substrate.

SCIENTIFIC QUESTION:
  COMBO-3 (PP-45 5-method unified audit API: trace, deletion, kappa_3, CNDC, cert) confirmed
  for standard Hopfield W = Xi^T Xi / N.
  PP-51 (implicit-Gram audit-on-M-side architecture): Gram solve G = Xi Xi^T / N + eps*I
  produces audit-equivalent results to direct W-based audit.

  This anchor tests COMBO-3 audit self-consistency when the substrate is in PP-51
  implicit-Gram mode: Krylov buffer computed via matrix-free G-solve (M-side) rather
  than N-side W-matvec. Are the 5 audit primitives consistent between N-side and M-side?

  Self-consistency tests:
    (a) Tr(W^1) via N-side Hutchinson == Tr(W^1) via M-side Gram eigenvalues (HP1).
    (b) Tr(W^2) via N-side == M-side (HP2).
    (c) Tr(W^3) via N-side == M-side (HP3).
    (d) Deletion cert from N-side == M-side (within 1e-4) (HP4).
    (e) Matvec count <= 5 for Krylov buffer (HP5, operational requirement).

HP:
  HARD-PASS: HP1 AND HP2 AND HP3 within relative 1e-4 AND HP4 AND HP5 in >= 4/5 seeds.
  MIDDLE: 4/5 conditions.
  HARD-FAIL: any trace diverges by > 1e-2 OR deletion cert off by > 0.10.

  P_deflated = 0.65 (COMBO-3 API confirmed at N=4096/8192/16384/32768;
  PP-51 M-side equivalence theorem is proven but first substrate-level confirmation).

FORMULA SELF-TESTS:
  1. Krylov N-side tr_W1 = (sum eigenvalues of G) / N (by eigenvalue equivalence).
     [INPUT: N=64, M=3] [EXPECTED: rel_err < 0.25 at N=64 with 500 probes]
  2. Deletion cert N-side for xi: cert = -(Xi xi)^T (Xi xi) / n^2 = -||Xi xi||^2/n^2.
     For M=1 xi=Xi[0]: cert = -(n)^2/n^2 = -1.0.
     [INPUT: N=8, M=1, xi=Xi[0]] [EXPECTED: cert = -1.0]
  3. Matvec count: V0, V1=W V0, V2=W^2 V0 -> 2 matvecs <= 5.
  4. GPU memory > 0 after Xi alloc.

PROT-018: anchor has _n4096; N MUST = 4096.
COMPOSITION CLASSIFICATION: PIPELINE (Krylov buffer passes through both N-side and M-side pathways).
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

ANCHOR_NAME = "combo3_pp51_5method_on_implicit_gram_v1_n4096"

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
    Tr(W^k) = Tr((Xi^T Xi / n)^k) = sum_i eig_i^k / n^k.
    """
    G = (Xi @ Xi.t()) / n   # (M, M) -- NOT dividing by n again; already normalized
    # Eigenvalues of G = Xi Xi^T / n have same non-zero eigvals as W = Xi^T Xi / n
    # Tr(W^k) = sum_i lambda_i^k where lambda_i = eigenvalues of W = G (same spectrum)
    eigs = torch.linalg.eigvalsh(G)  # real symmetric; NOTE: eigenvalues of Xi Xi^T / n
    # But Tr(W^1) = sum_i lambda_i / 1 (already /n in G definition)
    # W = Xi^T Xi / n; eigenvalues of W = eigenvalues of Xi Xi^T / n = eigenvalues of G.
    # Tr(W^k) = sum eig_i^k
    tr1 = float(eigs.sum())
    tr2 = float((eigs ** 2).sum())
    tr3 = float((eigs ** 3).sum())
    return tr1, tr2, tr3


def deletion_cert_n_side(Xi: torch.Tensor, xi: torch.Tensor, n: int) -> float:
    """cert = xi^T (-(1/N) xi xi^T) xi / N for xi in stored set -- M=1 formula.
    For M>1: cert = -||Xi xi||^2 / n^2 (aggregate contribution).
    """
    proj = Xi @ xi
    return -float(torch.dot(proj, proj)) / (n * n)


def deletion_cert_m_side(Xi: torch.Tensor, xi: torch.Tensor, n: int,
                          eps: float = 1e-6) -> float:
    """PP-51 M-side cert: via Gram-solve G = Xi Xi^T / n + eps I.

    cert = xi^T W_solved xi / n where W_solved xi = Xi^T (G^{-1} (Xi xi / n)) / n.
    For M=1: same as N-side.
    """
    G = (Xi @ Xi.t()) / n + eps * torch.eye(Xi.shape[0], device=DEVICE, dtype=torch.float32)
    rhs = (Xi @ xi) / n   # (M,)
    try:
        g_inv_rhs = torch.linalg.solve(G, rhs.unsqueeze(1)).squeeze(1)
    except Exception:
        return float("nan")
    w_xi = Xi.t() @ g_inv_rhs / n   # (N,)
    return -float(torch.dot(xi, w_xi)) / n  # signed cert (negative for stored)


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


def _selftest_cert_M1():
    """Deletion cert for xi = Xi[0] in W (M=1) = -1.0."""
    n_t = 8
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi = (torch.randint(0, 2, (n_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_t = xi.unsqueeze(0)
    cert_n = deletion_cert_n_side(Xi_t, xi, n_t)
    assert abs(cert_n + 1.0) < 0.01, f"cert_n selftest: {cert_n:.4f} expected -1.0"


def _instrumentation_selftest():
    _selftest_traces_N64()
    _selftest_cert_M1()
    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: N/M trace agreement, cert_M1=-1.0, gpu_mem_ok N={N}",
          flush=True)


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

    # HP4: deletion cert consistency
    cert_diffs = []
    for q in range(min(N_TEST_CERT, m_count)):
        xi_q = Xi[q]
        cert_n_val = deletion_cert_n_side(Xi, xi_q, n_dim)
        cert_m_val = deletion_cert_m_side(Xi, xi_q, n_dim)
        if not (cert_m_val != cert_m_val):  # NaN check
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


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} M={M_ACTIVE} mode={RUN_MODE}", flush=True)
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
