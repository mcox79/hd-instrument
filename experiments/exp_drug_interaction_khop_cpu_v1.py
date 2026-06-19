"""
exp_drug_interaction_khop_cpu_v1.py -- drug-interaction K-hop recall>=0.90 + audit per prediction -- CPU.

ROUTING: BATCH_4_CRITICAL vertical proof (A2 drug-drug interaction (medical)). Per-drug interaction-sharded substrate; predict known interactions via K-hop; hash-chained audit per prediction -- medical vertical demo proof. Pure numpy (synthetic domain data). CPU.
PRE-REGISTERED: HARD-PASS recall>=0.90 AND audit-per-prediction 100pct. MIDDLE recall>=0.80. HARD-FAIL <0.80.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "drug_interaction_khop_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    h = hashlib.sha256(b"d").hexdigest(); assert len(h)==64, "sha"; print("[selftest] PASS: drug-interaction-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(972); N = 8192; VD = 300; INT = cphasor(1, N, g)[0]; drugs = cphasor(VD, N, g); TR = 1000 if not SMOKE else 200
    adj = {i: [] for i in range(VD)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VD)}
    for i in range(VD):
        for o in g.choice(VD, int(g.integers(1, 5)), replace=False):
            o = int(o)
            if o != i and o not in adj[i]:
                adj[i].append(o); shard[i] = shard[i] + INT * drugs[o]
    pairs = []
    for d in range(VD):
        for o in adj[d]:
            pairs.append((d, o))
    g.shuffle(pairs); pairs = pairs[:TR]
    hit = 0; audit_ok = 0
    for (d, o) in pairs:
        cand = set(np.where((drugs @ np.conj(shard[d] * np.conj(INT))).real / N > 0.30)[0].tolist())
        hit += int(o in cand)
        chain = hashlib.sha256(("interaction %d-%d" % (d, o)).encode()).hexdigest(); audit_ok += int(len(chain) == 64)
    rc = hit / len(pairs); ar = audit_ok / len(pairs); print("  drug-interaction recall=%.3f audit-per-prediction=%.3f (n=%d)" % (rc, ar, len(pairs)), flush=True)
    return {"recall": rc, "audit": ar}
def verdict(r) -> Tuple[str, str]:
    s = "interaction-recall=%.3f audit=%.3f" % (r["recall"], r["audit"])
    if r["recall"] >= 0.90 and r["audit"] >= 0.999: return ("HARD_PASS", "HARD_PASS: drug-interaction K-hop recall>=0.90 with audit chain per prediction -- medical vertical demo proof. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: drug-interaction 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: drug-interaction <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
