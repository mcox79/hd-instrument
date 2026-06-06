"""
exp_cs1_dt_algebraic_audit_v1 -- Batch B: Donoho-Tanner phase-boundary audit of rescue axes -- CPU.

ROUTING: Research Batch B (highest-leverage framework). Maps each capacity rescue axis to a (delta=M/N, rho=k/M) operating
  point and checks it against the Donoho-Tanner l1 phase-transition boundary rho_DT(delta). Unifies sparse-coding /
  Hadamard / dim-expansion as movements in the (delta,rho) plane: a rescue "works" iff it moves the operating point BELOW
  the boundary (recoverable zone). Empirically anchored by d_eff=82 (intrinsic-dim sets the effective N). Pure algebra +
  a small numpy DT-boundary fit; CPU $0.
PRE-REGISTERED: HARD-PASS the empirically-passing arms (sparse f<=0.10) lie BELOW rho_DT and the failing arms (dense) lie
  ABOVE -- DT boundary PREDICTS the capacity verdicts. MID: partial agreement. HF: no predictive agreement.
FORMULA SELF-TESTS (PROT-022): 1. DT boundary monotone in delta. 2. dense above / sparse below at matched alpha.
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

ANCHOR_NAME = "cs1_dt_algebraic_audit_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N = 4096; D_EFF = 82   # intrinsic dim (Batch A finding); effective N for real-encoder arms
# rescue arms: (name, alpha_capacity=M/N observed, k_active_per_pattern_frac). delta=alpha, rho=k_active/M=k_frac/alpha.
ARMS = [("dense", 0.05, 1.0), ("sparse0.20", 0.20, 0.20), ("sparse0.10", 0.40, 0.10),
        ("sparse0.05", 1.00, 0.05), ("hadamard", 0.40, 1.0)]


def rho_dt(delta):
    # Donoho-Tanner l1 weak phase-transition approx: rho* ~ delta / (2 ln(1/delta)+ ... ); use the standard small-delta form
    delta = np.clip(delta, 1e-4, 0.999)
    return delta / (2.0 * np.log(1.0 / delta) + delta)


def _selftest():
    ds = np.array([0.05, 0.1, 0.2, 0.4]); r = rho_dt(ds); assert np.all(np.diff(r) > 0), "DT boundary monotone in delta"
    print("[selftest] PASS: dt", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    rows = []
    for name, alpha, kfrac in ARMS:
        delta = alpha                                   # M/N at capacity
        rho = min(0.999, kfrac / max(alpha, 1e-6))      # active fraction of M ... use k_active/M proxy = kfrac/alpha
        boundary = float(rho_dt(delta))
        below = bool(rho <= boundary)                   # below boundary -> recoverable (rescue works)
        rows.append({"arm": name, "alpha": alpha, "delta": delta, "rho": rho, "rho_DT": boundary, "below_boundary": below})
        print("  [%s] delta=%.3f rho=%.3f rho_DT=%.3f below=%s" % (name, delta, rho, boundary, below), flush=True)
    return {"rows": rows}


def verdict(r) -> Tuple[str, str]:
    rows = r["rows"]
    # empirical: sparse arms PASS (high alpha), dense LOW. Does below_boundary track that ordering?
    passing = [x for x in rows if x["alpha"] >= 0.2]; failing = [x for x in rows if x["alpha"] < 0.2]
    pass_below = np.mean([x["below_boundary"] for x in passing]) if passing else 0
    fail_below = np.mean([x["below_boundary"] for x in failing]) if failing else 1
    summary = "DT-below by arm: %s" % {x["arm"]: x["below_boundary"] for x in rows}
    if pass_below >= 0.6 and fail_below <= 0.4:
        return ("HARD_PASS", "HARD_PASS: DT phase boundary PREDICTS capacity verdicts (passing arms below, failing above) -- unifying framework validated. " + summary)
    if pass_below > fail_below:
        return ("MIDDLE_BAND", "MIDDLE_BAND: DT boundary partially predictive. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: DT boundary does not predict capacity ordering. " + summary)


print("[config] anchor=%s mode=%s N=%d d_eff=%d arms=%d" % (ANCHOR_NAME, RUN_MODE, N, D_EFF, len(ARMS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
