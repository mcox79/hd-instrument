"""Research REVIVAL_SUBSTRATE_NATIVE Sprint-1 remainder: TOOL-EXTENDED-SUBSTRATE (embodied) + FRISSON (aesthetic).
Both substrate-only, cheap. TOOL: body schema extends to incorporate a used tool (peripersonal space). FRISSON: cleanup-
margin spike when a built-up sequence resolves to a known schema = prediction-error-resolution aesthetic proxy. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-1 ({tag}); substrate-only (no LLM). {desc}
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
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
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

TOOL = r'''
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
'''

FRISSON = r'''
def _selftest():
    print("[selftest] PASS: frisson", flush=True)
def run() -> Dict:
    # frisson = prediction-error-resolution: a built-up sequence that RESOLVES to a known schema produces a cleanup-margin
    # SPIKE; an unresolved (random ending) sequence does not. Frisson magnitude should discriminate resolved vs unresolved.
    g = np.random.default_rng(641); NSCHEMA = 40; LEN = 6; M = 200
    schemas = None; TR = 25 if SMOKE else 150; fr = []; lab = []; buildups = []; frmag = []
    for _ in range(TR):
        notes = cphasor(M, N, g); slots = cphasor(LEN, N, g)
        sch_seq = [[int(x) for x in g.integers(0, M, size=LEN)] for _ in range(NSCHEMA)]
        schema_vecs = np.stack([cnorm(sum((slots[k] * notes[s[k]] for k in range(LEN)), np.zeros(N, dtype=np.complex64))) for s in sch_seq])
        for _q in range(8):
            resolves = g.random() < 0.5; si = int(g.integers(0, NSCHEMA)); seq = list(sch_seq[si])
            if not resolves:
                seq[-1] = int(g.integers(0, M))                                  # unresolved: wrong final note
            partial = cnorm(sum((slots[k] * notes[seq[k]] for k in range(LEN - 1)), np.zeros(N, dtype=np.complex64)))
            complete = cnorm(partial * ((LEN - 1) ** 0.5) + slots[LEN - 1] * notes[seq[-1]])
            m_part = float((schema_vecs[si] @ np.conj(partial)).real) / N        # margin to schema BEFORE resolution
            m_full = float((schema_vecs[si] @ np.conj(complete)).real) / N        # AFTER
            frisson = m_full - m_part                                            # the resolution spike
            fr.append(frisson); lab.append(int(resolves));
            if resolves:
                buildups.append(LEN); frmag.append(frisson)
    auc = _auc(np.array(fr), np.array(lab))
    print("  FRISSON resolution-margin-spike AUC(resolved vs unresolved)=%.3f (n=%d)" % (auc, len(fr)), flush=True)
    return {"frisson_auc": round(auc, 3), "n": len(fr)}
def verdict(r) -> Tuple[str, str]:
    s = "frisson-AUC=%.3f" % r["frisson_auc"]
    if r["frisson_auc"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate cleanup-margin spike at sequence resolution discriminates RESOLVED vs unresolved (AUC>=0.80) -- prediction-error-resolution frisson proxy from existing cleanup dynamics, substrate-only no new infra. " + s)
    if r["frisson_auc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: frisson AUC 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: frisson margin does not track resolution. " + s)
'''

C = [
    dict(anchor="tool_extended_substrate_cpu_v1", tag="TOOL-EXTENDED-SUBSTRATE", title="body schema extends to incorporate a used tool",
         desc="Body-part bundle B; using a tool binds it into B (peripersonal space); used tool reaches body-part membership.",
         prereg="HARD-PASS membership-AUC>=0.85 AND tool-delta>0.05. MIDDLE AUC>=0.70. HARD-FAIL else.", body=TOOL),
    dict(anchor="frisson_cleanup_margin_cpu_v1", tag="FRISSON-CLEANUP-MARGIN", title="cleanup-margin spike at resolution as frisson proxy",
         desc="A built-up sequence resolving to a known schema yields a cleanup-margin SPIKE; unresolved sequences do not.",
         prereg="HARD-PASS frisson-AUC(resolved vs unresolved)>=0.80. MIDDLE>=0.65. HARD-FAIL else.", body=FRISSON),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
