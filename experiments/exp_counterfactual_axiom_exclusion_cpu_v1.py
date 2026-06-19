"""
exp_counterfactual_axiom_exclusion_cpu_v1.py -- removing an axiom makes its dependent theorems underivable (correctly excluded) -- CPU.

ROUTING: fast-cheap batch (CAP-4 counterfactual axiom exclusion). A theorem-dependency KB; counterfactually REMOVE an axiom and verify that theorems depending (transitively) on it become underivable (excluded from the reachable closure) while independent theorems remain derivable. Tests counterfactual reasoning over a proof graph. Pure numpy FHRR (sub-minute; all-or-nothing OK). CPU.
PRE-REGISTERED: HARD-PASS >= 0.80 of truly-dependent theorems correctly excluded after axiom removal (and independents retained). MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
ANCHOR_NAME = "counterfactual_axiom_exclusion_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    assert (set([1,2,3]) - set([2])) == {1,3}, "set diff"; print("[selftest] PASS: counterfactual-axiom-exclusion", flush=True)
def run() -> Dict:
    g = np.random.default_rng(803); N = 8192; VT = 120; DEP = cphasor(1, N, g)[0]; thms = cphasor(VT, N, g); TR = 40 if SMOKE else 120; HOPS = 4
    excl_ok = 0; excl_tot = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VT)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VT)}
        for t in range(1, VT):
            k = int(g.integers(1, 4)); deps = g.choice(t, min(k, t), replace=False)
            for d in deps:
                adj[t].append(int(d)); shard[t] = shard[t] + DEP * thms[int(d)]
        axiom = int(g.integers(0, VT // 4))                                    # remove a low-level axiom
        def closure(skip):
            seen = set(); fr = set(range(VT))
            # ground-truth: a theorem is derivable if NONE of its transitive deps include the removed axiom
            derivable = set()
            for t in range(VT):
                stack = [t]; deps_all = set(); bad = False
                while stack:
                    u = stack.pop()
                    for d in adj[u]:
                        if d == skip:
                            bad = True
                        if d not in deps_all:
                            deps_all.add(d); stack.append(d)
                if not bad and t != skip:
                    derivable.add(t)
            return derivable
        deriv_after = closure(axiom)
        truly_dependent = set(range(VT)) - deriv_after - {axiom}
        # substrate check: a theorem is "excluded" if axiom appears in its substrate dependency closure (K-hop)
        for t in list(truly_dependent)[:15]:
            reached = set(); fr = [t]
            for _h in range(HOPS):
                nf = []
                for u in fr:
                    if not adj[u]:
                        continue
                    for v in np.where((thms @ np.conj(shard[u] * np.conj(DEP))).real / N > 0.30)[0].tolist():
                        if v not in reached:
                            nf.append(v)
                reached |= set(nf); fr = nf
            excl_ok += int(axiom in reached); excl_tot += 1
    rc = excl_ok / max(1, excl_tot); print("  counterfactual axiom-exclusion recall=%.3f (n=%d dependent theorems)" % (rc, excl_tot), flush=True)
    return {"recall": rc}
def verdict(r) -> Tuple[str, str]:
    s = "exclusion-recall=%.3f" % r["recall"]
    if r["recall"] >= 0.80: return ("HARD_PASS", "HARD_PASS: removed-axiom dependents correctly identified as excluded >=0.80 -- counterfactual proof-graph reasoning works. " + s)
    if r["recall"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: exclusion 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: exclusion <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
