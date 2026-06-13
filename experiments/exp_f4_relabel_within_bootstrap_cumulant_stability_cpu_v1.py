"""
exp_f4_relabel_within_bootstrap_cumulant_stability_cpu_v1.py -- F4-RELABEL-WITHIN: are the 9d pillar's higher free cumulants (kappa_3, kappa_4) STABLE / structure-driven, not outlier/label artifacts? -- CPU/local (no heat).

ROUTING: Research handoff exp_dev_handoff_research_F4_relabeled_codebook_audit_robust (Anchor 1) -- a robustness audit of the 9d spectral
  pillar (Cell C). Codebook-dependent (atom vectors via AlgebraIndex), NOT relation-dependent -> runnable during the relations re-ingest.

  HONEST DESIGN NOTE (verify-before-assert): the handoff's literal "within-cluster RELABELING" of atom LABELS is ANALYTICALLY TRIVIAL --
  free cumulants depend only on the eigenvalue spectrum (Voiculescu), which is permutation-invariant, so pure label-permutation gives SE=0
  by mathematics, not measurement. The INFORMATIVE robustness test is BOOTSTRAP-COMPOSITION stability: resample the codebook atoms (with
  replacement) and ask whether kappa_3/kappa_4 stay stable or are driven by a few outlier atoms. Stable (low SE/|kappa|) => the 9d pillar's
  higher-cumulant dimensions read the codebook's STRUCTURE (broad spectral shape), not a handful of atoms -> audit-robust. NO LLM; numpy; no heat.

PRE-REGISTERED (Research suggested bands): HARD-PASS SE(kappa_3)/|kappa_3| <= 0.05 AND SE(kappa_4)/|kappa_4| <= 0.05 (cumulants stable
  under codebook resampling -> structure-driven, audit-robust). HARD-FAIL SE/|kappa| > 0.20 on either (cumulants are outlier-driven, not
  robust). MIDDLE_BAND in between. UNKNOWN if codebook unavailable / M<30. ASCII-only. --self-test + --smoke + metrics.json.
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
ANCHOR_NAME = "f4_relabel_within_bootstrap_cumulant_stability_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
KMAX = 4; N_BOOT = 100; VECTOR_FIELD = "composite_hrr"; SEED = 1028


def _poly_pow_coeff(m: np.ndarray, j: int, e: int) -> float:
    if j == 0:
        return 1.0 if e == 0 else 0.0
    acc = np.zeros(e + 1); acc[0] = 1.0; base = m[:e + 1]
    for _ in range(j):
        acc = np.convolve(acc, base)[:e + 1]
    return float(acc[e])


def free_cumulants(moments: List[float], kmax: int) -> List[float]:
    m = np.zeros(kmax + 1); m[0] = 1.0
    for k in range(1, kmax + 1): m[k] = moments[k - 1]
    kappa = [0.0] * (kmax + 1)
    for n in range(1, kmax + 1):
        kappa[n] = m[n] - sum(kappa[j] * _poly_pow_coeff(m, j, n - j) for j in range(1, n))
    return kappa[1:]


def kappas_of(A: np.ndarray, kmax: int) -> List[float]:
    Ndim = A.shape[1]
    rn = np.linalg.norm(A, axis=1, keepdims=True) + 1e-12
    A = (A / rn) * np.sqrt(Ndim)                         # Cell B/C row-scaling
    ev = np.linalg.eigvalsh((A.T @ A) / Ndim)
    moments = [float(np.mean(ev ** k)) for k in range(1, kmax + 1)]
    return free_cumulants(moments, kmax)


def _selftest():
    a = 0.236
    m = np.zeros(KMAX + 1); m[0] = 1.0; kp = [0.0] + [a] * KMAX
    for n in range(1, KMAX + 1):
        m[n] = kp[n] + sum(kp[j] * _poly_pow_coeff(m, j, n - j) for j in range(1, n))
    rec = free_cumulants(list(m[1:]), KMAX)
    assert all(abs(rec[i] - a) < 1e-7 for i in range(KMAX)), rec       # free-Poisson round-trip
    rng = np.random.RandomState(0); X = rng.standard_normal((40, 64))
    k = kappas_of(X, KMAX); assert len(k) == KMAX and np.isfinite(k).all()
    print("[selftest] PASS: f4_relabel_within_bootstrap_cumulant_stability (recursion + kappas_of)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _load_codebook() -> np.ndarray:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    idx = AlgebraIndex(); vecs = []
    for a in PartitionedStore(REPO / "data" / "substrate_index").all_atoms():
        v = getattr(idx.encode_atom(a), VECTOR_FIELD, None)
        if v is not None: vecs.append(np.asarray(v, dtype=np.float64))
    return np.stack(vecs) if vecs else np.zeros((0, 1024))


def run() -> Dict:
    if not (REPO / "data" / "substrate_index").exists():
        return {"error": "no_substrate_index"}
    # race-tolerant codebook load (atoms may be mid-write during ingest)
    A = None
    for _ in range(5):
        try:
            A = _load_codebook()
            if A.shape[0] >= 30: break
        except Exception:
            A = None; time.sleep(8)
    if A is None or A.shape[0] < 30:
        return {"error": "codebook_unavailable_or_race", "M": 0 if A is None else int(A.shape[0])}
    M, Ndim = A.shape
    base = kappas_of(A, KMAX)
    rng = np.random.RandomState(SEED); nb = N_BOOT if RUN_MODE != "smoke" else 20
    boot = np.zeros((nb, KMAX))
    for b in range(nb):
        idx = rng.randint(0, M, M)                        # bootstrap-resample atoms (composition perturbation)
        boot[b] = kappas_of(A[idx], KMAX)
    se = boot.std(axis=0); mean = boot.mean(axis=0)
    cov = {k + 1: round(float(se[k] / (abs(mean[k]) + 1e-12)), 4) for k in range(KMAX)}
    print("  codebook %s: M=%d Ndim=%d | baseline kappa_1..4=%s" % (VECTOR_FIELD, M, Ndim, [round(x, 4) for x in base]), flush=True)
    print("  bootstrap (N=%d) kappa SE: %s" % (nb, [round(float(se[k]), 4) for k in range(KMAX)]), flush=True)
    print("  SE/|kappa| (coeff of variation) k=1..4: %s | k3=%.4f k4=%.4f (HARD-PASS<=0.05)" % (cov, cov[3], cov[4]), flush=True)
    return {"M": M, "Ndim": Ndim, "baseline_kappa": [round(x, 5) for x in base], "cov": cov,
            "cov_k3": cov[3], "cov_k4": cov[4], "n_boot": nb}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("M", "")))
    c3 = r["cov_k3"]; c4 = r["cov_k4"]
    s = ("M=%d codebook; baseline kappa=%s; bootstrap SE/|kappa| k3=%.4f k4=%.4f (k1..4=%s). Pure within-cluster LABEL permutation is "
         "analytically SE=0 (Voiculescu: cumulants depend on the spectrum, not labels); this measures BOOTSTRAP-COMPOSITION stability instead.") % (
        r["M"], r["baseline_kappa"], c3, c4, r["cov"])
    if c3 <= 0.05 and c4 <= 0.05:
        return ("HARD_PASS", "HARD_PASS: kappa_3 + kappa_4 are STABLE under codebook resampling (SE/|kappa| %.4f, %.4f <= 0.05) -- the 9d pillar's higher-cumulant dimensions are STRUCTURE-driven (broad spectral shape), not outlier/atom-label artifacts. Audit-robust; contrasts with INV-1 (load-bearing axis was label-DEPENDENT). " % (c3, c4) + s)
    if c3 > 0.20 or c4 > 0.20:
        return ("HARD_FAIL", "HARD_FAIL: kappa_3 or kappa_4 SE/|kappa| > 0.20 (%.4f, %.4f) -- higher cumulants are OUTLIER-driven, not robust; the 9d pillar's higher dimensions need an honest robustness footnote. " % (c3, c4) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: kappa stability in (0.05,0.20] (%.4f, %.4f) -- moderately robust; higher cumulants partly composition-sensitive. " % (c3, c4) + s)


print("[config] anchor=%s mode=%s field=%s n_boot=%d" % (ANCHOR_NAME, RUN_MODE, VECTOR_FIELD, N_BOOT), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
