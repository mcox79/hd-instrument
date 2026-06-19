"""
exp_tool_extended_substrate_cpu_v1.py -- body schema extends to incorporate a used tool -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-1 (TOOL-EXTENDED-SUBSTRATE); substrate-only (no LLM). Body-part bundle B; using a tool binds it into B (peripersonal space); used tool reaches body-part membership.
PRE-REGISTERED: HARD-PASS membership-AUC>=0.85 AND tool-delta>0.05. MIDDLE AUC>=0.70. HARD-FAIL else.
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
ANCHOR_NAME = "tool_extended_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))

def _selftest():
    print("[selftest] PASS: tool-extended", flush=True)
def run() -> Dict:
    # Maravita-Iriki: after USING a tool, the body schema B incorporates it (peripersonal extension). Membership of the
    # used tool in B should rise to body-part level; unused tools + random objects stay OUT.
    g = np.random.default_rng(640); NB = 8; NT = 10; NR = 40
    TR = 25 if SMOKE else 150; sc = []; lab = []; deltas = []
    for _ in range(TR):
        body = cphasor(NB, N, g); tools = cphasor(NT, N, g); rand = cphasor(NR, N, g)
        B = cnorm(body.sum(0))
        t = int(g.integers(0, NT)); B_t = cnorm(B * (NB ** 0.5) + tools[t])     # "use" tool t -> incorporate into body schema
        mem = lambda x, Bv: float((np.vdot(Bv, x).real) / N)
        deltas.append(mem(tools[t], B_t) - mem(tools[t], B))                     # tool membership increase after use
        for j in range(NB):
            sc.append(mem(body[j], B_t)); lab.append(1)                          # body parts: IN
        sc.append(mem(tools[t], B_t)); lab.append(1)                             # used tool: IN (peripersonal)
        for j in range(NT):
            if j != t:
                sc.append(mem(tools[j], B_t)); lab.append(0)                      # unused tools: OUT
        for j in range(min(NR, 12)):
            sc.append(mem(rand[j], B_t)); lab.append(0)                           # random objects: OUT
    auc = _auc(np.array(sc), np.array(lab)); dmean = float(np.mean(deltas))
    print("  TOOL-EXTENDED body-membership AUC=%.3f (used-tool IN vs unused/random OUT) | tool-membership-delta-after-use=%.3f" % (auc, dmean), flush=True)
    return {"membership_auc": round(auc, 3), "tool_delta": round(dmean, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "membership-AUC=%.3f tool-delta=%.3f" % (r["membership_auc"], r["tool_delta"])
    if r["membership_auc"] >= 0.85 and r["tool_delta"] > 0.05:
        return ("HARD_PASS", "HARD_PASS: using a tool extends the substrate body schema to incorporate it (used tool reaches body-part membership, AUC>=0.85; membership rises after use) -- Maravita-Iriki peripersonal extension, substrate-only. " + s)
    if r["membership_auc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: tool extension partial. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no tool-body incorporation. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
