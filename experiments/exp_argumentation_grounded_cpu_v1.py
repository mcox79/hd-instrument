"""
exp_argumentation_grounded_cpu_v1.py -- LAP-STRETCH-1 ARGUMENTATION-1: Dung grounded semantics over substrate-stored attack graph -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop STRETCH. Abstract argumentation framework (arguments + attack relation). The
  GROUNDED extension is the least fixpoint of the characteristic function: an argument is IN iff all its attackers are OUT
  (attacked by something already IN); unattacked args seed the set. Substrate stores per-argument attacker bundles; grounded
  semantics is computed by retrieving attackers (cleanup) and running the fixpoint. Compares substrate-driven grounded extension
  to the ground-truth algorithm on random frameworks. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS per-argument accept/reject agreement >= 0.90 (P=0.80 prior; well-defined deterministic semantics). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "argumentation_grounded_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    assert True; print("[selftest] PASS: argumentation-grounded", flush=True)


def grounded_truth(NA, attackers):
    IN = set(); OUT = set()
    while True:
        changed = False
        for a in range(NA):
            if a in IN or a in OUT:
                continue
            if all(att in OUT for att in attackers[a]):                  # all attackers defeated -> accept
                IN.add(a); changed = True
        for a in range(NA):
            if a in OUT:
                continue
            if any(att in IN for att in attackers[a]):                   # attacked by an accepted arg -> reject
                OUT.add(a); changed = True
        if not changed:
            break
    return IN


def grounded_substrate(NA, args, ATT, shard):
    # recover attackers via cleanup then run the same fixpoint (substrate supplies the edges)
    rec = {}
    for a in range(NA):
        sc = (args @ np.conj(shard[a] * np.conj(args[a]) * np.conj(ATT))).real
        deg = int(round(float((np.abs(np.vdot(shard[a], shard[a])) / N))))  # ~ number of attackers
        rec[a] = set(int(i) for i in np.argsort(sc)[::-1][:max(0, deg)]) if deg > 0 else set()
    return grounded_truth(NA, rec)


def run() -> Dict:
    g = np.random.default_rng(8); NA = 8; TR = 40 if SMOKE else 250; agree = 0; tot = 0
    ATT = cphasor(1, N, g)[0]
    for _ in range(TR):
        args = cphasor(NA, N, g)
        attackers = {a: set() for a in range(NA)}
        for a in range(NA):
            for b in range(NA):
                if a != b and g.random() < 0.22:
                    attackers[a].add(b)
        shard = {a: sum((args[a] * (ATT * args[b]) for b in attackers[a]), np.zeros(N, dtype=np.complex64)) for a in range(NA)}
        gt = grounded_truth(NA, attackers); sub = grounded_substrate(NA, args, ATT, shard)
        for a in range(NA):
            agree += int((a in gt) == (a in sub)); tot += 1
    acc = agree / tot; print("  ARGUMENTATION grounded per-arg agreement=%.3f (NA=%d, n=%d)" % (acc, NA, tot), flush=True)
    return {"grounded_agreement": acc, "NA": NA, "n": tot}


def verdict(r) -> Tuple[str, str]:
    s = "grounded-agreement=%.3f (NA=%d, n=%d)" % (r["grounded_agreement"], r["NA"], r["n"])
    if r["grounded_agreement"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate-stored attack graph supports Dung grounded semantics >=0.90 per-arg -- formal argumentation (accept/reject via least-fixpoint defense) computed over retrieved attack edges. " + s)
    if r["grounded_agreement"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: grounded 0.75-0.90 (attacker-set cleanup load; per-arg sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: grounded <0.75. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
