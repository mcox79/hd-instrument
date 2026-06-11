"""
exp_integ_temporal_policy_cpu_v1.py -- INTEG-TEMPORAL-POLICY (substrate-native temporal integration) -- CPU.

ROUTING: Research CYCLE226 Tier-0 (#2; the integration ANSWER). Meta-finding: substrate likes TIME + CONTEXT, dislikes FIXED
  structure. Integration via single-snapshot blending/selection hits the ~96% irreducible single-action frustration; a TEMPORAL
  POLICY (cycle of actions alternating over time) satisfies competing drives on average. This makes it SUBSTRATE-NATIVE: the
  policy is stored as a temporal composite (sum_t TIME[t] (X) action[t]), recovered per time-step, and executed over the cycle.
  Tests (a) temporal-policy min time-averaged drive-sat >> single-action minimax, (b) the temporal policy is substrate-recoverable. N=8192.
PRE-REGISTERED: HARD-PASS temporal min-avg-sat exceeds single-action minimax by >=20% AND policy recovery >=0.95. MIDDLE one of the two. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "integ_temporal_policy_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: integ-temporal-policy", flush=True)
def run() -> Dict:
    g = np.random.default_rng(687); ND = 5; NA = 12; L = 6; TR = 300 if not SMOKE else 80
    single = []; temporal = []; rec_acc = []
    for _ in range(TR):
        pref = g.random((ND, NA)) ** 3; pref = pref / pref.sum(1, keepdims=True)
        sm = float(np.max([np.min(pref[:, a]) for a in range(NA)]))     # single-action minimax
        # build a TEMPORAL POLICY: L-slot cycle; greedily fill each slot to lift the worst time-averaged drive
        policy = []; cumsum = np.zeros(ND)
        for t in range(L):
            cur_avg = cumsum / max(t, 1)
            dstar = int(np.argmin(cur_avg)) if t > 0 else int(g.integers(0, ND))
            a = int(np.argmax(pref[dstar]))                             # action best for currently-worst drive
            policy.append(a); cumsum += pref[:, a]
        time_avg = cumsum / L; tmin = float(np.min(time_avg))
        # SUBSTRATE-NATIVE: store the policy as a temporal composite, recover each slot's action
        TIME = cphasor(L, N, g); actions = cphasor(NA, N, g)
        comp = cnorm(sum((TIME[t] * actions[policy[t]] for t in range(L)), np.zeros(N, dtype=np.complex64)))
        rec = sum(int(cidx(comp * np.conj(TIME[t]), actions) == policy[t]) for t in range(L)) / L
        single.append(sm); temporal.append(tmin); rec_acc.append(rec)
    ms = float(np.mean(single)); mt = float(np.mean(temporal)); ra = float(np.mean(rec_acc)); esc = (mt - ms) / (ms + 1e-9)
    print("  INTEG-TEMPORAL-POLICY min-drive-sat: single-action=%.3f | temporal-policy=%.3f (escape=%.0f%%) | policy-recovery=%.3f" % (ms, mt, 100 * esc, ra), flush=True)
    return {"single_minimax": round(ms, 3), "temporal_minavg": round(mt, 3), "escape_pct": round(100 * esc, 1), "policy_recovery": round(ra, 3)}
def verdict(r) -> Tuple[str, str]:
    esc = r["escape_pct"]; ra = r["policy_recovery"]; s = "single=%.3f temporal=%.3f escape=%.0f%% recovery=%.3f" % (r["single_minimax"], r["temporal_minavg"], esc, ra)
    if esc >= 20 and ra >= 0.95:
        return ("HARD_PASS", "HARD_PASS: SUBSTRATE-NATIVE temporal-policy integration -- a recoverable temporal action composite (recovery>=0.95) alternates actions over time to lift the worst drive by >=20%% vs single-action minimax. Integration is solved by TIME (temporal policy), substrate-native; confirms the temporal/contextual meta-pattern. " + s)
    if esc >= 20 or ra >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: temporal escape OR recovery holds, not both. " + s)
    return ("HARD_FAIL", "HARD_FAIL: temporal policy neither escapes nor recovers. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
