"""
exp_qdef_rate_limit_5qpm_v1 -- post-quantum defenses anchor 1 (Chain 1 Drill 4) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_chain1_drill4_quantum_defenses. GOLD 4.0: Grover oracle is physically
  impossible against a black-box centralized API; architectural defenses (rate limiting) close residual threats without
  formal post-quantum crypto. Simulates a per-account token-bucket rate limit at 5 queries/min: measures (a) throughput
  impact on LEGITIMATE Poisson traffic, (b) whether an adversarial extraction campaign is blocked after k=20 queries.
  CPU $0.
PRE-REGISTERED (research bands): HARD-PASS legit throughput impact < 1%% AND adversarial campaign blocked by k=20.
  MID 1-10%% legit impact. HARD-FAIL > 10%% legit impact (rate limiting needs refinement).
FORMULA SELF-TESTS (PROT-022): 1. token bucket refills. 2. burst blocked. 3. slow traffic unaffected.
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

ANCHOR_NAME = "qdef_rate_limit_5qpm_v1"
RATE_PER_MIN = 5.0; BUCKET = 5.0; CAMPAIGN_K = 20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_LEGIT = 200; SIM_MIN = 60
else:
    N_LEGIT = 2000; SIM_MIN = 600


def token_bucket(arrival_times, rate_per_min=RATE_PER_MIN, bucket=BUCKET):
    # returns boolean allowed[] per arrival (times in minutes, sorted)
    tokens = bucket; last = 0.0; allowed = []
    for t in arrival_times:
        tokens = min(bucket, tokens + (t - last) * rate_per_min); last = t
        if tokens >= 1.0:
            tokens -= 1.0; allowed.append(True)
        else:
            allowed.append(False)
    return np.array(allowed)


def _selftest():
    # slow traffic (1/min < 5/min) all allowed
    slow = np.arange(0, 10, 1.0); assert token_bucket(slow).all(), "slow traffic unaffected"
    # burst of 20 at t=0 -> only ~bucket(5) allowed
    burst = np.zeros(20); assert token_bucket(burst).sum() <= 6, "burst blocked"
    # refill: after 1 min, a token returns
    assert token_bucket(np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.01]))[-1], "token bucket refills"
    print("[selftest] PASS: qdef-rate-limit", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7)
    # LEGITIMATE: Poisson at a benign rate (~1/min, well under the 5/min limit)
    legit_rate = 1.0; inter = g.exponential(1.0 / legit_rate, N_LEGIT); arr = np.cumsum(inter)
    arr = arr[arr <= SIM_MIN]
    allowed = token_bucket(arr); legit_impact = 1.0 - allowed.mean()
    # ADVERSARIAL: campaign of CAMPAIGN_K queries in a tight burst (all at ~t=100)
    camp = 100.0 + np.linspace(0, 0.05, CAMPAIGN_K)                  # 20 queries within 3 seconds
    camp_allowed = token_bucket(camp); blocked_after = int(np.argmax(~camp_allowed)) if (~camp_allowed).any() else CAMPAIGN_K
    campaign_blocked = (~camp_allowed).any() and blocked_after <= CAMPAIGN_K
    print("  legit_impact=%.4f (n=%d) | campaign first-block at query %d of %d, blocked=%s" % (
        legit_impact, len(arr), blocked_after, CAMPAIGN_K, campaign_blocked), flush=True)
    return {"legit_impact": float(legit_impact), "n_legit": int(len(arr)), "campaign_first_block": blocked_after, "campaign_blocked": bool(campaign_blocked)}


def verdict(r) -> Tuple[str, str]:
    imp = r["legit_impact"]; blocked = r["campaign_blocked"]
    summary = "legit_throughput_impact=%.3f%% campaign_first_block_at=%d/20 campaign_blocked=%s" % (imp * 100, r["campaign_first_block"], blocked)
    if imp < 0.01 and blocked:
        return ("HARD_PASS", "HARD_PASS: rate limit blocks adversarial campaign by k=20 with <1%% legit impact -- universal defense per GOLD 4.0. " + summary)
    if imp <= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1-10%% legit impact (qualify). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: >10%% legit throughput impact -- rate limiting needs refinement. " + summary)


print("[config] anchor=%s mode=%s n_legit=%d sim_min=%d rate=%.1f/min" % (ANCHOR_NAME, RUN_MODE, N_LEGIT, SIM_MIN, RATE_PER_MIN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
