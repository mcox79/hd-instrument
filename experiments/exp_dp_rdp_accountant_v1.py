"""
exp_dp_rdp_accountant_v1 -- Renyi-DP accountant for federated aggregation (tighter than naive composition) -- CPU.

ROUTING: field_DP_5x (privacy accountant). The substrate's federated DP histograms (eps=1.0, MAE~0.6pct, cycle 170/171 HP)
  compose over T aggregation rounds; without a tight accountant the privacy budget is overstated. Validates a Renyi-DP (RDP)
  accountant: Gaussian-mechanism RDP eps(alpha)=T*alpha/(2 sigma^2) composed over T rounds, converted to (eps,delta), vs the
  naive (basic) composition eps_naive = T * eps_single. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS RDP-composed eps < 0.5 * naive eps at T=100 (>=2x tighter accountant) AND RDP eps is a valid upper
  bound (>= the single-round eps). MIDDLE 0.5-0.8x. HARD-FAIL not tighter than naive.
FORMULA SELF-TESTS (PROT-022): 1. rdp positive. 2. eps decreases with sigma. 3. convert monotone in delta.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "dp_rdp_accountant_v1"; SIGMA = 1.0; DELTA = 1e-5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
ALPHAS = np.concatenate([np.arange(2, 64), np.array([128, 256])]).astype(np.float64)


def rdp_gaussian(sigma, T, alphas):
    # RDP of T compositions of the Gaussian mechanism (sensitivity 1): eps_rdp(alpha) = T * alpha / (2 sigma^2)
    return T * alphas / (2.0 * sigma * sigma)


def rdp_to_dp(rdp, alphas, delta):
    # convert RDP curve to (eps, delta): eps = min_alpha [ rdp(alpha) + log(1/delta)/(alpha-1) ]
    return float(np.min(rdp + np.log(1.0 / delta) / (alphas - 1.0)))


def single_round_eps(sigma, delta):
    rdp1 = rdp_gaussian(sigma, 1, ALPHAS); return rdp_to_dp(rdp1, ALPHAS, delta)


def _selftest():
    r = rdp_gaussian(1.0, 10, ALPHAS); assert (r > 0).all(), "rdp positive"
    e_lo = rdp_to_dp(rdp_gaussian(0.5, 10, ALPHAS), ALPHAS, 1e-5); e_hi = rdp_to_dp(rdp_gaussian(2.0, 10, ALPHAS), ALPHAS, 1e-5)
    assert e_lo > e_hi, "eps decreases with sigma"
    e_d1 = rdp_to_dp(rdp_gaussian(1.0, 10, ALPHAS), ALPHAS, 1e-3); e_d2 = rdp_to_dp(rdp_gaussian(1.0, 10, ALPHAS), ALPHAS, 1e-6)
    assert e_d2 > e_d1, "convert monotone in delta"
    print("[selftest] PASS: dp-rdp-accountant", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    eps1 = single_round_eps(SIGMA, DELTA); rows = {}
    for T in ([10, 100] if RUN_MODE == "smoke" else [10, 50, 100]):
        rdp_eps = rdp_to_dp(rdp_gaussian(SIGMA, T, ALPHAS), ALPHAS, DELTA)
        naive_eps = T * eps1                                  # basic composition: linear in T
        rows["T%d" % T] = {"rdp": rdp_eps, "naive": naive_eps, "ratio": rdp_eps / naive_eps}
        print("  T=%d  RDP-eps=%.3f  naive-eps=%.3f  ratio=%.3f (sigma=%.1f, delta=%.0e)" % (T, rdp_eps, naive_eps, rdp_eps / naive_eps, SIGMA, DELTA), flush=True)
    return {"rows": rows, "eps_single": eps1, "sigma": SIGMA}


def verdict(r) -> Tuple[str, str]:
    rows = r["rows"]; t100 = rows.get("T100", rows[max(rows)])
    ratio = t100["ratio"]; summary = "at T=100 RDP-eps=%.2f naive-eps=%.2f ratio=%.3f (single-round eps=%.3f, sigma=%.1f)" % (t100["rdp"], t100["naive"], ratio, r["eps_single"], r["sigma"])
    valid = t100["rdp"] >= r["eps_single"] - 1e-6
    if ratio < 0.5 and valid:
        return ("HARD_PASS", "HARD_PASS: RDP accountant gives >=2x tighter privacy budget than naive composition at T=100 (valid upper bound) -- the federated consortium can run more aggregation rounds at the same eps. " + summary)
    if ratio < 0.8 and valid:
        return ("MIDDLE_BAND", "MIDDLE_BAND: RDP 0.5-0.8x of naive. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: RDP not >=2x tighter than naive (or invalid bound). " + summary)


print("[config] anchor=%s mode=%s sigma=%.1f delta=%.0e" % (ANCHOR_NAME, RUN_MODE, SIGMA, DELTA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
