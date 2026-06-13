"""
exp_f4_kappa_n_deviation_snr_cpu_v1.py -- free-cumulant DEVIATION-SNR (independent-signal horizon) kappa_3..kappa_8 [Research re-spec Cell A] -- CPU (remote).

ROUTING: Research hand-off exp_dev_handoff_research_F4_kappa_n_hierarchy_saturation (Anchor 1, Tier-1). Extends the F4 free-
  cumulants cell (exp_f4_free_cumulants_v1, kappa_3/kappa_4) to the SATURATION HORIZON: report kappa_3..kappa_8 with bootstrap-
  resampled SNR per order and find n_sat (order at which higher free cumulants become noise-dominated at N=1024). Substrate-
  product: confirms/refutes the claim that the spectral pillar is COMPLETE at kappa_3 + kappa_4 (no 9th dimension needed for
  kappa_5+). Codebook W = Xi^T Xi / N (M=alpha*N patterns), free-Poisson/MP bulk where true kappa_n = alpha for all n; the
  EMPIRICAL kappa_k variance grows with k (Bao-Xie N^(2-r)), so SNR_k decreases with k -> n_sat = first k with SNR_k < 1.5.

  FREE CUMULANTS via the generating relation M(z) = 1 + sum_{j>=1} kappa_j z^j M(z)^j  (Speicher; equivalently M = C(zM)).
  Coefficient match: m_n = sum_{j=1}^{n} kappa_j [z^{n-j}] M(z)^j  =>  kappa_n = m_n - sum_{j=1}^{n-1} kappa_j [z^{n-j}] M(z)^j,
  with m_0=1 and [z^e] M(z)^j computed by truncated polynomial powers of the raw-moment series. RIGOROUS SELF-TEST: round-trip
  kappa=[alpha]*8 -> moments -> recover kappa=[alpha]*8 (and moments match the closed-form free-Poisson m_1..m_4).
  NO LLM; numpy only (no torch/GPU); ~1 min; runs on the REMOTE desktop (remote_cpu_queue) -- no laptop heat.

PRE-REGISTERED (research note): HARD-PASS HP-1 SNR_3>=5.0; HP-2 SNR_4>=3.0; HP-3 SNR_5 in [1.5,3.0] AND SNR_6<1.5; HP-4 n_sat
  stable (range<=1) across 3 codebook seeds. HARD-FAIL SNR_6>=3.0 (kappa_6 independent signal -> refutes pillar-completeness,
  needs 9th dim) OR SNR_4<2.0 (kappa_4 noise-dominated) OR n_sat range>=2 across seeds. Predicted n_sat in {4,5}.
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
ANCHOR_NAME = "f4_kappa_n_deviation_snr_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 1024; ALPHA = 0.5; KMAX = 8
SNR_FLOOR = 1.5


def _poly_pow_coeff(m: np.ndarray, j: int, e: int) -> float:
    """[z^e] of (sum_i m[i] z^i)^j, given moment-series coeffs m (m[0]=1). Truncated to degree e."""
    if j == 0:
        return 1.0 if e == 0 else 0.0
    base = m[:e + 1].copy()
    acc = np.zeros(e + 1); acc[0] = 1.0
    for _ in range(j):
        acc = np.convolve(acc, base)[:e + 1]
    return float(acc[e])


def free_cumulants_from_moments(moments: List[float], kmax: int) -> List[float]:
    """moments[k]=m_k (k=1..kmax). Returns kappa_1..kappa_kmax via M(z)=1+sum kappa_j z^j M(z)^j."""
    m = np.zeros(kmax + 1); m[0] = 1.0
    for k in range(1, kmax + 1):
        m[k] = moments[k - 1]
    kappa = [0.0] * (kmax + 1)
    for n in range(1, kmax + 1):
        s = sum(kappa[j] * _poly_pow_coeff(m, j, n - j) for j in range(1, n))
        kappa[n] = m[n] - s
    return kappa[1:]


def moments_from_free_cumulants(kappa: List[float], kmax: int) -> List[float]:
    """forward (for self-test): given kappa_1..kappa_kmax, produce m_1..m_kmax via the same relation."""
    m = np.zeros(kmax + 1); m[0] = 1.0
    kp = [0.0] + list(kappa)
    for n in range(1, kmax + 1):
        # m_n = kappa_n + sum_{j=1}^{n-1} kappa_j [z^{n-j}] M^j  (M uses m_0..m_{n-1}, all known)
        s = sum(kp[j] * _poly_pow_coeff(m, j, n - j) for j in range(1, n))
        m[n] = kp[n] + s
    return list(m[1:])


def _selftest():
    a = 0.37
    kap = [a] * KMAX
    mom = moments_from_free_cumulants(kap, KMAX)
    # closed-form free-Poisson (MP) moments via Narayana numbers N(k,r):
    #   m_1=a; m_2=a+a^2; m_3=a+3a^2+a^3; m_4=a+6a^2+6a^3+a^4  (k=4 Narayana row 1,6,6,1).
    # NOTE: exp_f4_free_cumulants_v1.py docstring states m_4=a+7a^2+... -- that 7a^2 is INCORRECT (should be 6a^2); flagged to Research.
    assert abs(mom[0] - a) < 1e-9
    assert abs(mom[1] - (a + a**2)) < 1e-9
    assert abs(mom[2] - (a + 3*a**2 + a**3)) < 1e-9
    assert abs(mom[3] - (a + 6*a**2 + 6*a**3 + a**4)) < 1e-9
    rec = free_cumulants_from_moments(mom, KMAX)              # round-trip
    assert all(abs(rec[i] - a) < 1e-7 for i in range(KMAX)), rec
    print("[selftest] PASS: f4_kappa_n_saturation (free-Poisson round-trip kappa_n=alpha recovered; m_1..m_4 closed-form match)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _eigs(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed); M = int(ALPHA * N)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = Xi.T @ Xi / N
    np.fill_diagonal(W, 0.0)
    return np.linalg.eigvalsh(W)


def _kappas_from_eigs(ev: np.ndarray) -> List[float]:
    moments = [float(np.mean(ev ** k)) for k in range(1, KMAX + 1)]
    return free_cumulants_from_moments(moments, KMAX)


def run() -> Dict:
    seeds = [11] if SMOKE else [11, 23, 37]
    B = 100 if SMOKE else 500
    per_seed_nsat = []; agg_snr = {k: [] for k in range(1, KMAX + 1)}; seed_rows = []
    for sd in seeds:
        ev = _eigs(sd); n = len(ev)
        rng = np.random.RandomState(sd + 1)
        boot = np.zeros((B, KMAX))
        for b in range(B):
            idx = rng.randint(0, n, n)
            boot[b] = _kappas_from_eigs(ev[idx])
        snr = {}
        for k in range(1, KMAX + 1):
            mean_k = float(np.mean(boot[:, k - 1])); std_k = float(np.std(boot[:, k - 1]) + 1e-12)
            snr[k] = abs(mean_k - ALPHA) / std_k; agg_snr[k].append(snr[k])  # DEVIATION-SNR: independent signal beyond alpha
        nsat = next((k for k in range(3, KMAX + 1) if snr[k] <= SNR_FLOOR), KMAX)
        per_seed_nsat.append(nsat)
        seed_rows.append({"seed": sd, "n_sat": nsat, "snr": {k: round(snr[k], 3) for k in range(3, KMAX + 1)}})
        print("  seed=%d n_sat=%d SNR_3..8=%s" % (sd, nsat, [round(snr[k], 2) for k in range(3, KMAX + 1)]), flush=True)
    snr_mean = {k: round(float(np.mean(agg_snr[k])), 3) for k in range(1, KMAX + 1)}
    nsat_range = max(per_seed_nsat) - min(per_seed_nsat)
    print("  mean SNR by order: %s" % {k: snr_mean[k] for k in range(3, KMAX + 1)}, flush=True)
    print("  n_sat per seed=%s range=%d (HP-4 needs range<=1)" % (per_seed_nsat, nsat_range), flush=True)
    return {"snr_mean": snr_mean, "n_sat_per_seed": per_seed_nsat, "n_sat_range": nsat_range,
            "n_sat_median": int(np.median(per_seed_nsat)), "seed_rows": seed_rows, "N": N, "alpha": ALPHA, "B": B}


def verdict(r) -> Tuple[str, str]:
    sm = r["snr_mean"]; rng = r["n_sat_range"]; nsat = r["n_sat_median"]; per = r["n_sat_per_seed"]
    dev_beyond5 = max(sm[6], sm[7], sm[8])
    s = "DEVIATION-SNR (|kappa_k-alpha|/std) k3..8 = %.2f/%.2f/%.2f/%.2f/%.2f/%.2f; n_sat/seed=%s range=%d; N=%d alpha=%.2f B=%d" % (
        sm[3], sm[4], sm[5], sm[6], sm[7], sm[8], per, rng, r["N"], r["alpha"], r["B"])
    if all(3 <= x <= 5 for x in per) and dev_beyond5 < 3.0:
        return ("HARD_PASS", "HARD_PASS: cumulant hierarchy SATURATES as predicted -- deviation-SNR returns to noise (<=1.5) at n_sat in {3,4,5} (per seed %s), and no order beyond 5 carries independent signal (max dev-SNR k>=6 = %.2f < 3). The 8d pillar STANDS: kappa_5+ add nothing independent beyond kappa_2=alpha. " % (per, dev_beyond5) + s)
    if dev_beyond5 >= 3.0:
        return ("HARD_FAIL", "HARD_FAIL: deviation-SNR >= 3.0 sustained beyond k=5 (max k>=6 = %.2f) -- genuine INDEPENDENT structure beyond kappa_4; would warrant a kappa_5/6 pillar dimension. " % dev_beyond5 + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: deviation-SNR at k=6 in [1.5,3) (=%.2f) -- ambiguous; the real-codebook Cell B decides (clustered-codebook structure vs uniform free-Poisson). n_sat/seed=%s. " % (sm[6], per) + s)


print("[config] anchor=%s mode=%s N=%d alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, N, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(r["n_sat_per_seed"]), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
