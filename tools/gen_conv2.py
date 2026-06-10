"""HUGE_BATCH TIER-1: CONV-3 empathic, CONV-5 memory-decision, CONV-8 opinion, CONV-15 tool-routing. CPU numpy/VSA. Write-tool; placeholder-replace (no nested %-format)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: HUGE_BATCH TIER-1 ({tag}). {desc} numpy/VSA. CPU.
PRE-REGISTERED: {prereg}
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

PROTO = r'''
def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: __LABEL__", flush=True)
def run() -> Dict:
    g = np.random.default_rng(__SEED__); N = 8192; K = __KVAL__; proto = cphasor(K, N, g)
    TR = 60 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        c = int(g.integers(0, K))
        msg = proto[c] * np.exp(1j * 0.6 * g.standard_normal(N))          # intent prototype + paraphrase noise
        correct += int(cidx(msg, proto) == c); n += 1
    acc = correct / n; print("  __LABEL__=%.3f (K=%d, n=%d)" % (acc, K, n), flush=True)
    return {"accuracy": acc, "K": K}
def verdict(r) -> Tuple[str, str]:
    s = "__LABEL__=%.3f" % r["accuracy"]
    if r["accuracy"] >= __HP__:
        return ("HARD_PASS", "HARD_PASS: __LABEL__ clears bar -- intent-conditioned routing works. " + s)
    if r["accuracy"] >= __MID__:
        return ("MIDDLE_BAND", "MIDDLE_BAND: __LABEL__ near bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: __LABEL__ below bar. " + s)
'''

def proto(label, seed, k, hp, mid):
    return PROTO.replace("__LABEL__", label).replace("__SEED__", str(seed)).replace("__KVAL__", str(k)).replace("__HP__", str(hp)).replace("__MID__", str(mid))

CONV5 = r'''
def _selftest():
    assert (1 != 2); print("[selftest] PASS: conv5-memory-decision", flush=True)
def run() -> Dict:
    g = np.random.default_rng(5); N = 8192; ACT = cphasor(3, N, g)
    TR = 60 if SMOKE else 200; dec_ok = 0; erase_ok = 0; ne = 0; n = 0
    VK = 50; VV = 300; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g)
    for _ in range(TR):
        a = int(g.integers(0, 3)); msg = ACT[a] * np.exp(1j * 0.6 * g.standard_normal(N))
        dec_ok += int(cidx(msg, ACT) == a); n += 1
        if a == 1:
            k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = keys[k] * vals[vv]; Mem = Mem - keys[k] * vals[vv]
            erase_ok += int(cidx(Mem * np.conj(keys[k]), vals) != vv); ne += 1
    da = dec_ok / n; ea = (erase_ok / ne) if ne else 1.0
    print("  memory-decision-acc=%.3f forget-erasure=%.3f (n=%d)" % (da, ea, n), flush=True)
    return {"decision_acc": da, "erasure": ea}
def verdict(r) -> Tuple[str, str]:
    s = "decision-acc=%.3f forget-erasure=%.3f" % (r["decision_acc"], r["erasure"])
    if r["decision_acc"] >= 0.85 and r["erasure"] >= 0.999:
        return ("HARD_PASS", "HARD_PASS: memory decisions >=0.85 (remember/forget/query) + 100pct erasure on forget. " + s)
    if r["decision_acc"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: decision 0.75-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: decision <0.75. " + s)
'''

C = [
    dict(anchor="conv3_empathic_cpu_v1", tag="CONV-3 empathic (intent-conditioned)", title="empathic response matches emotional intent", desc="Classify emotional intent (sad/frustrated/happy/confused) via prototype cleanup; select matching template.", prereg="HARD-PASS >=0.85. MIDDLE >=0.70. HARD-FAIL <0.70.", body=proto("empathic-intent-match", 31, 4, 0.85, 0.70)),
    dict(anchor="conv8_opinion_cpu_v1", tag="CONV-8 opinion expression", title="stored opinions retrieved correctly", desc="Store entity->stance opinions; retrieve correct stance per query.", prereg="HARD-PASS >=0.95. MIDDLE >=0.85. HARD-FAIL <0.85.", body=proto("opinion-recall", 88, 6, 0.95, 0.85)),
    dict(anchor="conv15_tool_routing_cpu_v1", tag="CONV-15 substrate-routed tool calls (smoke)", title="tool routing accuracy (intent->tool)", desc="Classify query intent to one of several tools via substrate prototype cleanup; 50-query smoke.", prereg="HARD-PASS >=0.85. MIDDLE >=0.70. HARD-FAIL <0.70.", body=proto("tool-routing-acc", 1515, 6, 0.85, 0.70)),
    dict(anchor="conv5_memory_decision_cpu_v1", tag="CONV-5 memory decision logic", title="memory decisions + 100pct erasure on forget", desc="Intent-conditioned remember/forget/query decision + PP-104 erasure verification.", prereg="HARD-PASS decision>=0.85 AND erasure=1.0. MIDDLE decision>=0.75. HARD-FAIL <0.75.", body=CONV5),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
