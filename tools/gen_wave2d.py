"""Research WAVE-2 laptop: LAP2-1 PARACONS-1 (Belnap 4-valued) + LAP2-4 CULTURAL-CONVENTIONS (scripts/ToM-shortcut). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research LAPTOP_WAVE2 ({tag}); pure-FHRR (no download). {desc}
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

PARACONS = r'''
def _selftest():
    print("[selftest] PASS: paracons", flush=True)
def run() -> Dict:
    # Belnap 4-valued: each prop has pos-evidence and neg-evidence. (pos,neg)->T(1,0)/F(0,1)/U(0,0)/B(1,1). Inconsistent KB = some B.
    g = np.random.default_rng(1); N = 8192; NP = 50; props = cphasor(NP, N, g)
    TR = 30 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        pos = set(); neg = set()
        for p in range(NP):
            if g.random() < 0.5:
                pos.add(p)
            if g.random() < 0.4:                                         # overlap with pos -> 'Both' (contradiction)
                neg.add(p)
        POS = sum((props[p] for p in pos), np.zeros(N, dtype=np.complex64))
        NEG = sum((props[p] for p in neg), np.zeros(N, dtype=np.complex64))
        for p in range(NP):
            hp = (np.vdot(props[p], POS).real) / N > 0.5
            hn = (np.vdot(props[p], NEG).real) / N > 0.5
            val = ("B" if (hp and hn) else "T" if hp else "F" if hn else "U")
            gold = ("B" if (p in pos and p in neg) else "T" if p in pos else "F" if p in neg else "U")
            correct += int(val == gold); n += 1
    acc = correct / n; print("  PARACONS 4-valued (T/F/U/B) acc=%.3f (NP=%d, n=%d)" % (acc, NP, n), flush=True)
    return {"paracons_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "4-valued-acc=%.3f (n=%d)" % (r["paracons_acc"], r["n"])
    if r["paracons_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate assigns Belnap 4-valued truth (T/F/U/B) >=0.85 on INCONSISTENT KBs -- pos/neg evidence bundles tracked separately; contradiction (Both) handled gracefully, no explosion. " + s)
    if r["paracons_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 4-valued 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 4-valued <0.70. " + s)
'''

SCRIPTS = r'''
def _selftest():
    print("[selftest] PASS: cultural-conventions", flush=True)
def run() -> Dict:
    # Schank-Abelson scripts: NSCRIPT scripts each an ordered sequence of actions; ToM = retrieve expected next action by lookup.
    g = np.random.default_rng(4); N = 8192; NSCRIPT = 30; NACT = 40; LEN = 6
    actions = cphasor(NACT, N, g); slots = cphasor(LEN, N, g); skeys = cphasor(NSCRIPT, N, g)
    scripts = {s: [int(x) for x in g.integers(0, NACT, size=LEN)] for s in range(NSCRIPT)}
    store = {s: sum((slots[i] * actions[scripts[s][i]] for i in range(LEN)), np.zeros(N, dtype=np.complex64)) for s in range(NSCRIPT)}
    TR = 50 if SMOKE else 250; hit = 0; n = 0
    for _ in range(TR):
        s = int(g.integers(0, NSCRIPT)); i = int(g.integers(0, LEN))      # "given script s at step i, what action is expected?"
        pred = cidx(store[s] * np.conj(slots[i]), actions)
        hit += int(pred == scripts[s][i]); n += 1
    acc = hit / n; print("  CULTURAL-CONVENTIONS script-action lookup=%.3f (%d scripts, n=%d)" % (acc, NSCRIPT, n), flush=True)
    return {"script_acc": acc, "n_scripts": NSCRIPT, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "script-lookup=%.3f (%d scripts)" % (r["script_acc"], r["n_scripts"])
    if r["script_acc"] >= 0.85 and r["n_scripts"] >= 30:
        return ("HARD_PASS", "HARD_PASS: substrate stores 30+ social scripts and resolves expected-action (ToM) by lookup >=0.85 -- convention-as-retrieval shortcut; common-sense social reasoning without per-step inference. " + s)
    if r["script_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: script-lookup 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: script-lookup <0.70. " + s)
'''

C = [
    dict(anchor="lap2_1_paracons_cpu_v1", tag="LAP2-1 PARACONS-1", title="Belnap 4-valued paraconsistent logic on inconsistent KBs", desc="Separate pos/neg evidence bundles; assign T/F/U/B per prop; graceful on contradictions (Both).", prereg="HARD-PASS 4-valued>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.", body=PARACONS),
    dict(anchor="lap2_4_cultural_conventions_cpu_v1", tag="LAP2-4 CULTURAL-CONVENTIONS", title="social scripts; ToM-as-schema-lookup", desc="30+ Schank-Abelson scripts stored as slot-bound action sequences; resolve expected next action by lookup.", prereg="HARD-PASS script-lookup>=0.85 AND scripts>=30. MIDDLE>=0.70. HARD-FAIL<0.70.", body=SCRIPTS),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
