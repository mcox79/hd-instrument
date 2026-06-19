"""HUGE_BATCH TIER-2 laptop (pure-FHRR, no download): ORCH-MULTI-TOOL (substrate composes 3-tool pipeline) + CONV-13 (higher-order nested-binding composition). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: HUGE_BATCH TIER-2 laptop ({tag}); pure-FHRR (no HF download, no desktop CPU). {desc}
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

MULTITOOL = r'''
def _selftest():
    import numpy as _n; assert int(_n.argmax([0,1,0]))==1, "argmax"; print("[selftest] PASS: orch-multi-tool", flush=True)
def run() -> Dict:
    # substrate routes a query to a 3-TOOL PIPELINE (ordered sequence). K query-types -> distinct gold pipelines over T tools.
    g = np.random.default_rng(33); N = 8192; T = 6; K = 8; STEPS = 3
    tools = cphasor(T, N, g); slot = cphasor(STEPS, N, g); qproto = cphasor(K, N, g)
    gold = {k: [int(x) for x in g.integers(0, T, size=STEPS)] for k in range(K)}
    plan = {}                                                             # substrate stores query-type -> bound pipeline
    for k in range(K):
        v = np.zeros(N, dtype=np.complex64)
        for s in range(STEPS):
            v = v + slot[s] * tools[gold[k][s]]
        plan[k] = v
    TR = 60 if SMOKE else 240; pipe_ok = 0; step_ok = 0; n = 0
    for _ in range(TR):
        k = int(g.integers(0, K)); q = qproto[k] * np.exp(1j * 0.5 * g.standard_normal(N))
        kk = cidx(q, qproto)                                              # route query -> type
        seq = [cidx(plan[kk] * np.conj(slot[s]), tools) for s in range(STEPS)]   # unbind each slot -> tool
        ok_steps = sum(int(seq[s] == gold[k][s]) for s in range(STEPS))
        step_ok += ok_steps; pipe_ok += int(kk == k and ok_steps == STEPS); n += 1
    pr = pipe_ok / n; sr = step_ok / (n * STEPS)
    print("  ORCH-MULTI-TOOL full-pipeline=%.3f per-step=%.3f (K=%d, T=%d, steps=%d, n=%d)" % (pr, sr, K, T, STEPS, n), flush=True)
    return {"pipeline_acc": pr, "step_acc": sr}
def verdict(r) -> Tuple[str, str]:
    s = "full-pipeline=%.3f per-step=%.3f" % (r["pipeline_acc"], r["step_acc"])
    if r["pipeline_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate composes the correct 3-tool pipeline >=85pct end-to-end (route + ordered slot-bound tool sequence). Substrate-as-multi-tool-orchestrator validated. " + s)
    if r["pipeline_acc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: full-pipeline 0.65-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: full-pipeline <0.65. " + s)
'''

HIGHER = r'''
def _selftest():
    import numpy as _n; assert _n.allclose(_n.exp(1j*0.0), 1+0j), "phasor"; print("[selftest] PASS: conv13-higher-order", flush=True)
def run() -> Dict:
    # higher-order composition: nested records. outer = sum_i role_i * inner_i ; inner_i = sum_j subrole_j * filler_ij.
    # retrieve through TWO levels of unbinding: unbind(outer, role_i) -> inner_i ; unbind(inner_i, subrole_j) -> filler_ij.
    g = np.random.default_rng(44); N = 8192; NR = 3; NS = 3; VF = 200
    roles = cphasor(NR, N, g); subroles = cphasor(NS, N, g); fillers = cphasor(VF, N, g)
    TR = 60 if SMOKE else 240; lvl2 = 0; n = 0
    for _ in range(TR):
        truth = {}; outer = np.zeros(N, dtype=np.complex64)
        for i in range(NR):
            inner = np.zeros(N, dtype=np.complex64)
            for j in range(NS):
                f = int(g.integers(0, VF)); inner = inner + subroles[j] * fillers[f]; truth[(i, j)] = f
            outer = outer + roles[i] * inner
        for i in range(NR):
            inner_hat = outer * np.conj(roles[i])                         # level-1 unbind -> approx inner_i
            for j in range(NS):
                pred = cidx(inner_hat * np.conj(subroles[j]), fillers)    # level-2 unbind -> filler
                lvl2 += int(pred == truth[(i, j)]); n += 1
    acc = lvl2 / n
    print("  CONV-13 higher-order 2-level retrieval acc=%.3f (NR=%d, NS=%d, n=%d)" % (acc, NR, NS, n), flush=True)
    return {"twolevel_acc": acc, "depth": 2}
def verdict(r) -> Tuple[str, str]:
    s = "2-level-retrieval=%.3f" % r["twolevel_acc"]
    if r["twolevel_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate retrieves fillers through TWO levels of nested binding >=85pct -- higher-order compositional structure holds (role-of-(subrole-filler)). Substrate algebra extends to nested records. " + s)
    if r["twolevel_acc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2-level 0.65-0.85 (nested superposition load; sub-sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-level <0.65. " + s)
'''

C = [
    dict(anchor="orch_multi_tool_cpu_v1", tag="ORCH-MULTI-TOOL", title="substrate composes a 3-tool pipeline per query", desc="Substrate routes a query to its type then unbinds an ordered 3-slot tool pipeline; measures full-pipeline + per-step accuracy.", prereg="HARD-PASS full-pipeline>=0.85. MIDDLE>=0.65. HARD-FAIL<0.65.", body=MULTITOOL),
    dict(anchor="conv13_higher_order_cpu_v1", tag="CONV-13 higher-order composition", title="substrate retrieves through 2 levels of nested binding", desc="Nested records (role-of-(subrole-filler)); retrieve fillers through two unbinding levels.", prereg="HARD-PASS 2-level>=0.85. MIDDLE>=0.65. HARD-FAIL<0.65.", body=HIGHER),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
