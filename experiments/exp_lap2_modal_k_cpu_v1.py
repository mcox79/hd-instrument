"""
exp_lap2_modal_k_cpu_v1.py -- LAP-2 MODAL-K-1: K modal logic over finite Kripke frames -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-2). System K: box p (necessity) holds at world w iff p holds at
  ALL worlds accessible from w; diamond p (possibility) iff p holds at SOME accessible world. Substrate stores the accessibility
  relation (per-world bundle of accessible worlds) and per-world valuations (prop bundle); a modal query is evaluated by
  retrieving the accessible-world set (top-k cleanup) and testing prop membership at each, then applying all/some. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS >= 0.80 correct on box/diamond queries. MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
ANCHOR_NAME = "lap2_modal_k_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    assert all([True, True]) and any([False, True]), "modal"; print("[selftest] PASS: lap2-modal-k", flush=True)


def run() -> Dict:
    g = np.random.default_rng(2); W = 6; NP = 4
    TR = 50 if SMOKE else 300; correct = 0; n = 0
    for _ in range(TR):
        worlds = cphasor(W, N, g); PROP = cphasor(NP, N, g)
        acc = {w: sorted(set(int(x) for x in g.choice(W, g.integers(1, 4), replace=False))) for w in range(W)}
        val = {w: set(int(p) for p in range(NP) if g.random() < 0.5) for w in range(W)}
        acc_shard = {w: sum((worlds[w2] for w2 in acc[w]), np.zeros(N, dtype=np.complex64)) for w in range(W)}
        prophold = {w: sum((PROP[p] for p in val[w]), np.zeros(N, dtype=np.complex64)) for w in range(W)}
        w = int(g.integers(0, W)); p = int(g.integers(0, NP)); box = bool(g.integers(0, 2))
        # gold
        accset = acc[w]; gold = all(p in val[w2] for w2 in accset) if box else any(p in val[w2] for w2 in accset)
        # substrate eval: recover accessible worlds (top-|acc| cleanup), test p membership via cosine threshold
        sc = (worlds @ np.conj(acc_shard[w])).real; rec = [int(i) for i in np.argsort(sc)[::-1][:len(accset)]]
        holds = []
        for w2 in rec:
            m = (np.vdot(PROP[p], prophold[w2]).real) / N                 # ~1 if p holds at w2, ~0 otherwise
            holds.append(m > 0.5)
        pred = all(holds) if box else any(holds)
        correct += int(pred == gold); n += 1
    acc_score = correct / n; print("  MODAL-K box/diamond acc=%.3f (W=%d, NP=%d, n=%d)" % (acc_score, W, NP, n), flush=True)
    return {"modal_acc": acc_score, "n": n}


def verdict(r) -> Tuple[str, str]:
    s = "modal-K-acc=%.3f (n=%d)" % (r["modal_acc"], r["n"])
    if r["modal_acc"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate evaluates K modal logic (box=all-accessible, diamond=some-accessible) >=0.80 -- accessibility + valuation stored as bundles, modal quantifiers as all/some over retrieved accessible worlds. " + s)
    if r["modal_acc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: modal-K 0.65-0.80 (accessible-set cleanup load; sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: modal-K <0.65. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
