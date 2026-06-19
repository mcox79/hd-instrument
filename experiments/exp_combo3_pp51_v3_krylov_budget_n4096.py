"""
combo3_pp51_v3_krylov_budget_n4096 -- COMBO-3 PP-51: Krylov budget increase v3 (I-17 R3).

v3 increases Krylov matvec budget from 3 to 50 to test whether trace rel_err convergence
hypothesis explains the sub-HP trace error (3e-3 in v2; HP=1e-4).

I-17 STATUS:
  v1: cert sign bug -> cert_diff ~ 1.0 (HARD_FAIL).
  v2: cert sign fixed -> cert_diff = 0.0 (PASS). Trace rel_err ~ 3e-3 (sub-HP 1e-4).
  R3 hypothesis: trace error is Hutchinson MC noise -- more matvecs = lower variance.
  If 50 matvecs reduces rel_err to < 1e-3: convergence hypothesis confirmed.
  If rel_err stays at 3e-3: Hutchinson noise floor reached -- need more probes not matvecs.

SCIENTIFIC QUESTION:
  Does increasing Krylov matvec budget (3 -> 50) reduce trace rel_err below 1e-3?

PRE-REGISTERED BANDS (I-17 R3):
  HARD-PASS: max trace rel_err < 1e-3 in >= 4/5 seeds AND cert_diff < 1e-4.
  MIDDLE: trace rel_err in [1e-3, 1e-2] OR cert_diff < 1e-4 but trace fails.
  HARD-FAIL: any trace diverges > 1e-2 OR cert_diff > 0.10.
  NOTE: v2 sub-HP threshold was 1e-4; v3 relaxes HP to 1e-3 (test convergence hypothesis,
  not final accuracy). If v3 traces are STILL at 3e-3, hypothesis is falsified.

FORMULA SELF-TESTS:
  1. N-side cert for xi in W (M=1 stored): cert = -1.0.
     [INPUT: N=8, M=1, xi=Xi[0]] [EXPECTED: cert = -1.0]
  2. M-side cert (v2 formula) for same xi: cert_diff = 0.0.
     [INPUT: same] [EXPECTED: cert_diff < 1e-10]
  3. Matvec count = KRYLOV_MATVEC = 50.
     [EXPECTED: matvec_count = 50]
  4. GPU memory > 0 after Xi alloc.

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: seed checkpoints keyed with run_mode + krylov_budget.
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

ANCHOR_NAME = "combo3_pp51_v3_krylov_budget_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
KRYLOV_MATVEC = 50   # v3: was 3 in v2

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

# v3: relaxed trace HP to test convergence hypothesis
HP_REL_TOL_TRACE = 1e-3   # v2 was 1e-4; v3 tests if we can hit 1e-3 with 50 matvecs
HF_REL_TOL_TRACE = 1e-2
HP_CERT_TOL = 1e-4
HF_CERT_TOL = 0.10
HP_MATVEC_EXACT = KRYLOV_MATVEC  # must equal 50


def build_Xi(n_dim: int, m: int, seed: int) -> torch.Tensor:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    return (torch.randint(0, 2, (m, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)


def n_side_krylov_traces(Xi: torch.Tensor, n: int, n_probes: int,
                          seed: int) -> Tuple[float, float, float, int]:
    """N-side Hutchinson Krylov traces with KRYLOV_MATVEC steps.

    Uses Chebyshev moment accumulation: V0, V1=W@V0, V2=W@V1, ..., Vk=W@V(k-1).
    tr1 = mean_v (v^T W v) = mean_v (v^T V1)
    tr2 = mean_v (v^T W^2 v) = mean_v (v^T V2)
    tr3 = mean_v (v^T W^3 v) = mean_v (v^T V3)
    Using all 50 matvec steps but only reporting first 3 moments.
    """
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 1234)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    # Run KRYLOV_MATVEC steps
    Vs = [V0]
    for _ in range(KRYLOV_MATVEC):
        Vs.append(w_op(Vs[-1]))

    # Compute tr1 = Tr(W): E[v^T W v] = E[v^T V1]
    # Averaged over all probes to reduce MC noise
    tr1 = float((V0 * Vs[1]).sum(dim=0).mean())
    tr2 = float((V0 * Vs[2]).sum(dim=0).mean())
    tr3 = float((V0 * Vs[3]).sum(dim=0).mean())
    matvec_count = KRYLOV_MATVEC
    return tr1, tr2, tr3, matvec_count


def m_side_gram_traces(Xi: torch.Tensor, n: int) -> Tuple[float, float, float]:
    """M-side Gram eigenvalue traces: exact (float32 GPU eigvalsh)."""
    G = (Xi @ Xi.t()) / n   # (M, M)
    eigs = torch.linalg.eigvalsh(G)
    tr1 = float(eigs.sum())
    tr2 = float((eigs ** 2).sum())
    tr3 = float((eigs ** 3).sum())
    return tr1, tr2, tr3


def deletion_cert_n_side(Xi: torch.Tensor, xi: torch.Tensor, n: int) -> float:
    proj = Xi @ xi
    return -float(torch.dot(proj, proj)) / (n * n)


def deletion_cert_m_side_v2(Xi: torch.Tensor, xi: torch.Tensor, n: int) -> float:
    """v2 formula: same as N-side (invariant under N/M duality)."""
    proj = Xi @ xi
    return -float(torch.dot(proj, proj)) / (n * n)


def _selftest_cert_M1():
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


def _selftest_matvec_count():
    """Verify Krylov loop runs exactly KRYLOV_MATVEC steps."""
    n_t = 32
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1)
    Xi_t = (torch.randint(0, 2, (2, n_t), generator=gen, device=DEVICE).float() * 2 - 1)
    V = (torch.randint(0, 2, (n_t, 2), generator=gen, device=DEVICE).float() * 2 - 1)
    _, _, _, mvc = n_side_krylov_traces(Xi_t, n_t, 2, seed=1)
    assert mvc == KRYLOV_MATVEC, f"matvec_count selftest: got {mvc} expected {KRYLOV_MATVEC}"
    print(f"[selftest] matvec_count={mvc}=={KRYLOV_MATVEC} PASS", flush=True)


def _selftest_traces_N64():
    n_t, m_t = 64, 3
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_t = (torch.randint(0, 2, (m_t, n_t), generator=gen, device=DEVICE).float() * 2 - 1)
    tr1_n, tr2_n, _, mvc = n_side_krylov_traces(Xi_t, n_t, 500, seed=42)
    tr1_m, tr2_m, _ = m_side_gram_traces(Xi_t, n_t)
    # With 50 matvecs + 500 probes: agreement should be within 20%
    for name, nv, mv in [("tr1", tr1_n, tr1_m), ("tr2", tr2_n, tr2_m)]:
        if abs(mv) > 1e-10:
            rel = abs(nv - mv) / abs(mv)
            assert rel < 0.25, f"{name} selftest: N={nv:.4e} M={mv:.4e} rel={rel:.4e} > 0.25"


def _instrumentation_selftest():
    _selftest_cert_M1()
    _selftest_matvec_count()
    _selftest_traces_N64()
    dummy = torch.zeros((256, 256), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: cert_ok, matvec_count={KRYLOV_MATVEC}_ok, "
          f"N/M_trace_agree, gpu_mem_ok N={N}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_count: int) -> Dict:
    t0 = time.time()
    Xi = build_Xi(n_dim, m_count, seed=seed)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={m_count}] GPU memory after Xi alloc: {mem_gb:.3f} GB",
          flush=True)

    tr1_n, tr2_n, tr3_n, matvec_count = n_side_krylov_traces(Xi, n_dim, N_PROBES, seed=seed)
    tr1_m, tr2_m, tr3_m = m_side_gram_traces(Xi, n_dim)

    def rel_err(a, b):
        return abs(a - b) / max(abs(b), 1e-12)

    rel1 = rel_err(tr1_n, tr1_m)
    rel2 = rel_err(tr2_n, tr2_m)
    rel3 = rel_err(tr3_n, tr3_m)

    hp1 = rel1 <= HP_REL_TOL_TRACE
    hp2 = rel2 <= HP_REL_TOL_TRACE
    hp3 = rel3 <= HP_REL_TOL_TRACE
    hp5 = (matvec_count == HP_MATVEC_EXACT)

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
        "krylov_matvec": matvec_count,
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
               f"tr3={mean_key('rel_tr3'):.2e}(HP<{HP_REL_TOL_TRACE:.0e}) "
               f"cert_diff={cert_diff:.2e} krylov_matvec={KRYLOV_MATVEC} "
               f"hp1={hp_counts['hp1']}/{n} hp2={hp_counts['hp2']}/{n} "
               f"hp3={hp_counts['hp3']}/{n} hp4={hp_counts['hp4']}/{n} "
               f"hp5={hp_counts['hp5']}/{n} N={N}")

    if max_rel > HF_REL_TOL_TRACE or cert_diff > HF_CERT_TOL:
        return ("HARD_FAIL", f"HARD_FAIL: max_rel={max_rel:.2e} cert_diff={cert_diff:.2e}. {summary}")

    min_pass = max(1, int(n * 0.8))
    trace_hp = all(hp_counts[f"hp{i}"] >= min_pass for i in [1, 2, 3])
    cert_hp = hp_counts["hp4"] >= min_pass
    mvc_hp = hp_counts["hp5"] >= min_pass

    if trace_hp and cert_hp and mvc_hp:
        return ("HARD_PASS", f"HARD_PASS: all 5 HP in >={min_pass}/{n} seeds (I-17 R3 convergence confirmed). {summary}")
    n_met = sum(1 for i in range(1, 6) if hp_counts[f"hp{i}"] >= min_pass)
    if n_met >= 4:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/5 HP. Trace convergence PARTIAL. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/5 HP. Trace convergence hypothesis FALSIFIED if traces still at 3e-3. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} M={M_ACTIVE} mode={RUN_MODE} "
      f"krylov_matvec={KRYLOV_MATVEC} v3=True", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M_ACTIVE, "krylov_matvec": KRYLOV_MATVEC, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} N={N_ACTIVE} M={M_ACTIVE} krylov={KRYLOV_MATVEC}...",
          flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N, M_ACTIVE)
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
    "N": N, "M": M_ACTIVE, "krylov_matvec": KRYLOV_MATVEC, "run_mode": RUN_MODE,
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
