"""
exp_f4_substrate_codebook_kappa_n_deviation_snr_cpu_v1.py -- F4 Cell B: free-cumulant deviation-SNR on the REAL substrate codebook -- CPU/remote.

ROUTING: Research re-spec (research_to_exp_dev_F4_RE_SPEC...) Cell B -- the LOAD-BEARING test. Per Exp-Dev Correction 3: test the
  SUBSTRATE's real spectral bulk, not synthetic Xi. Build Gram G = A^T A / N where A = substrate atom-vector codebook
  (composite_hrr, the production identity vectors). Compute eigenvalues -> spectral moments m_1..m_8 -> free cumulants kappa_n via
  the (validated) free moment-cumulant recursion -> DEVIATION-SNR_k = |kappa_k - alpha_est| / bootstrap_std, alpha_est = m_1 = M/N.
  Decides whether the substrate spectrum is free-Poisson-like (pillar complete at kappa_2+; kappa_5+ add nothing independent) OR
  has CLUSTERED-CODEBOOK structure (independent signal at k=6-8; cf memory substrate_composition_decomposition...clustered_codebook).
  NO LLM; numpy only (AlgebraIndex is numpy; no torch/GPU); runs on remote desktop CPU runner (no laptop heat).

PRE-REGISTERED (Research Cell B): HARD-PASS deviation-SNR_k drops to noise (<=1.5) at k in {3,4,5} AND max dev-SNR k>=6 < 1.5
  (substrate bulk well-modeled by free-Poisson; 8d pillar complete). MIDDLE dev-SNR k in [1.5,3] at k=6-8 (clustered-codebook
  structure beyond uniform free-Poisson -- honest, aligns with clustered-codebook memory). HARD-FAIL dev-SNR >= 3 sustained beyond
  k=5 (genuine independent structure -> would add pillar dimensions). UNKNOWN if codebook unavailable / too few vectors.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "f4_substrate_codebook_kappa_n_deviation_snr_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
KMAX = 8; SNR_FLOOR = 1.5; VECTOR_FIELD = "composite_hrr"


def _poly_pow_coeff(m: np.ndarray, j: int, e: int) -> float:
    if j == 0:
        return 1.0 if e == 0 else 0.0
    base = m[:e + 1].copy(); acc = np.zeros(e + 1); acc[0] = 1.0
    for _ in range(j):
        acc = np.convolve(acc, base)[:e + 1]
    return float(acc[e])


def free_cumulants_from_moments(moments: List[float], kmax: int) -> List[float]:
    m = np.zeros(kmax + 1); m[0] = 1.0
    for k in range(1, kmax + 1):
        m[k] = moments[k - 1]
    kappa = [0.0] * (kmax + 1)
    for n in range(1, kmax + 1):
        s = sum(kappa[j] * _poly_pow_coeff(m, j, n - j) for j in range(1, n))
        kappa[n] = m[n] - s
    return kappa[1:]


def _selftest():
    # validated recursion: free-Poisson kappa_n=alpha -> m_4 = a+6a^2+6a^3+a^4 (Narayana 1,6,6,1) and round-trips.
    a = 0.236
    # forward via same relation
    m = np.zeros(KMAX + 1); m[0] = 1.0; kp = [0.0] + [a] * KMAX
    for n in range(1, KMAX + 1):
        m[n] = kp[n] + sum(kp[j] * _poly_pow_coeff(m, j, n - j) for j in range(1, n))
    assert abs(m[4] - (a + 6*a**2 + 6*a**3 + a**4)) < 1e-9
    rec = free_cumulants_from_moments(list(m[1:]), KMAX)
    assert all(abs(rec[i] - a) < 1e-7 for i in range(KMAX))
    print("[selftest] PASS: f4_substrate_codebook_kappa_n_deviation_snr (recursion validated on free-Poisson alpha=0.236)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _load_codebook() -> np.ndarray:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    idx = AlgebraIndex()
    vecs = []
    for a in PartitionedStore(REPO / "data" / "substrate_index").all_atoms():
        av = idx.encode_atom(a)
        v = getattr(av, VECTOR_FIELD, None)
        if v is not None:
            vecs.append(np.asarray(v, dtype=np.float64))
    return np.stack(vecs) if vecs else np.zeros((0, 1024))


def _kappas_from_eigs(ev: np.ndarray) -> List[float]:
    moments = [float(np.mean(ev ** k)) for k in range(1, KMAX + 1)]
    return free_cumulants_from_moments(moments, KMAX)


def run() -> Dict:
    if not (REPO / "data" / "substrate_index").exists():
        return {"error": "no_substrate_index"}
    A = _load_codebook()
    M, Ndim = A.shape
    if M < 30:
        return {"error": "too_few_codebook_vectors", "M": M}
    if SMOKE: A = A[:max(30, M // 2)]
    M = A.shape[0]
    # SCALE rows to norm^2 = Ndim so the Gram matches the free-Poisson/Wishart model (entry variance ~1, like +/-1 Xi).
    # composite_hrr are unit-norm by design -> without this, eigenvalues are ~1/N and m_1 != alpha (degenerate). NO diagonal-zeroing.
    row_norm = np.linalg.norm(A, axis=1, keepdims=True) + 1e-12
    A = (A / row_norm) * np.sqrt(Ndim)
    W = (A.T @ A) / Ndim                        # N x N Wishart; sum(eig)=M, mean(eig)=M/N=alpha
    ev = np.linalg.eigvalsh(W)
    alpha_est = float(np.mean(ev))              # empirical m_1 (= M/N for unit-var rows); the free-Poisson alpha
    kap = _kappas_from_eigs(ev)
    # bootstrap over eigenvalues for deviation-SNR
    B = 100 if SMOKE else 500
    rng = np.random.RandomState(1028); n = len(ev)
    boot = np.zeros((B, KMAX))
    for b in range(B):
        boot[b] = _kappas_from_eigs(ev[rng.randint(0, n, n)])
    dev_snr = {}
    for k in range(1, KMAX + 1):
        mean_k = float(np.mean(boot[:, k - 1])); std_k = float(np.std(boot[:, k - 1]) + 1e-12)
        dev_snr[k] = abs(mean_k - alpha_est) / std_k
    nsat = next((k for k in range(3, KMAX + 1) if dev_snr[k] <= SNR_FLOOR), KMAX)
    dev_beyond5 = max(dev_snr[6], dev_snr[7], dev_snr[8])
    print("  codebook: %s vectors=%d dim=%d alpha_est=M/N=%.4f kappa_2(emp)=%.4f" % (VECTOR_FIELD, M, Ndim, alpha_est, kap[1]), flush=True)
    print("  kappa_1..8 (empirical): %s" % [round(x, 4) for x in kap], flush=True)
    print("  DEVIATION-SNR |kappa_k - alpha|/std, k=3..8: %s" % [round(dev_snr[k], 3) for k in range(3, KMAX + 1)], flush=True)
    print("  n_sat=%d (first k with dev-SNR<=1.5); max dev-SNR k>=6 = %.3f" % (nsat, dev_beyond5), flush=True)
    return {"M": M, "Ndim": Ndim, "alpha_est": round(alpha_est, 4), "kappa": [round(x, 5) for x in kap],
            "dev_snr": {k: round(dev_snr[k], 4) for k in range(1, KMAX + 1)}, "n_sat": nsat,
            "dev_beyond5": round(dev_beyond5, 4), "vector_field": VECTOR_FIELD, "B": B}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("M", "")))
    ds = r["dev_snr"]; nsat = r["n_sat"]; d5 = r["dev_beyond5"]
    s = "real %s codebook M=%d N=%d alpha_est=%.4f; dev-SNR k3..8 = %s; n_sat=%d max-dev k>=6 = %.3f; kappa=%s" % (
        r["vector_field"], r["M"], r["Ndim"], r["alpha_est"], [ds[k] for k in range(3, 9)], nsat, d5, r["kappa"])
    if nsat <= 5 and d5 < 1.5:
        return ("HARD_PASS", "HARD_PASS: the SUBSTRATE's real spectral bulk is free-Poisson-like -- deviation-SNR saturates (<=1.5) at n_sat=%d in {3,4,5} and no order beyond 5 carries independent signal (max %.2f < 1.5). The 8d spectral pillar is COMPLETE on the real codebook; kappa_5+ add nothing independent. " % (nsat, d5) + s)
    if d5 < 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: the substrate codebook shows MILD independent structure beyond kappa_4 (max dev-SNR k>=6 = %.2f in [1.5,3)) -- consistent with CLUSTERED-codebook structure (not uniform free-Poisson); the 8d pillar captures the bulk but the clustered geometry adds weak higher-order signal. Honest substrate-product nuance, not a refutation. " % d5 + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate codebook has SUSTAINED independent structure beyond k=5 (max dev-SNR k>=6 = %.2f >= 3) -- the real spectral bulk is NOT free-Poisson; a kappa_5/6 pillar dimension would be warranted. " % d5 + s)


print("[config] anchor=%s mode=%s field=%s" % (ANCHOR_NAME, RUN_MODE, VECTOR_FIELD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
