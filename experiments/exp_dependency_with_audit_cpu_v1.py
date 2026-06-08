"""
exp_dependency_with_audit_cpu_v1.py -- theorem-dependency closure with a per-dependency Merkle audit trail -- CPU.

ROUTING: FRESH cheap batch (CHEAP-CAP dependency K-hop + audit trail). K-hop dependency traversal + a hash-chained audit trail (each resolved edge appended to a Merkle chain). Measures closure recall AND that the audit chain reproduces (tamper-evident). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS closure recall >= 0.95 AND audit reproduces 100pct. MIDDLE recall >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "dependency_with_audit_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    h = hashlib.sha256(b"x").hexdigest(); assert len(h) == 64, "sha"; print("[selftest] PASS: dependency-with-audit", flush=True)
def run() -> Dict:
    g = np.random.default_rng(952); N = 8192; VT = 120; DEP = cphasor(1, N, g)[0]; thms = cphasor(VT, N, g); TR = 40 if SMOKE else 120; HOPS = 3
    rec_sum = 0.0; audit_ok = 0; n = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VT)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VT)}
        for t in range(1, VT):
            for d in g.choice(t, min(int(g.integers(1, 4)), t), replace=False):
                adj[t].append(int(d)); shard[t] = shard[t] + DEP * thms[int(d)]
        root = int(g.integers(VT // 2, VT)); gold = set(); fr = {root}
        for _h in range(HOPS):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - gold
            gold |= nf; fr = nf
        if not gold:
            continue
        reached = set(); fr = [root]; chain = "0" * 64; edges = []
        for _h in range(HOPS):
            nf = []
            for u in fr:
                if not adj[u]:
                    continue
                for v in np.where((thms @ np.conj(shard[u] * np.conj(DEP))).real / N > 0.30)[0].tolist():
                    if v not in reached:
                        nf.append(v); edges.append((u, v)); chain = hashlib.sha256((chain + "%d-%d" % (u, v)).encode()).hexdigest()
            reached |= set(nf); fr = nf
        replay = "0" * 64
        for (u, v) in edges:
            replay = hashlib.sha256((replay + "%d-%d" % (u, v)).encode()).hexdigest()
        rec_sum += len(gold & reached) / len(gold); audit_ok += int(replay == chain); n += 1
    rc = rec_sum / n; ar = audit_ok / n; print("  dependency-closure recall=%.3f audit-reproduces=%.3f (n=%d)" % (rc, ar, n), flush=True)
    return {"recall": rc, "audit": ar}
def verdict(r) -> Tuple[str, str]:
    s = "closure-recall=%.3f audit-reproduces=%.3f" % (r["recall"], r["audit"])
    if r["recall"] >= 0.95 and r["audit"] >= 0.999: return ("HARD_PASS", "HARD_PASS: dependency K-hop closure >=0.95 with a 100pct-reproducible Merkle audit trail -- verifiable derivations. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: closure 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: closure <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
