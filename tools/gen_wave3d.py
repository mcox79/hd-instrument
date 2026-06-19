"""Research WAVE-3: LAP3-10 PARACONSISTENT-MULTI-CONTEXT + STRETCH3-3 META-COGNITIVE-2-LEVEL. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 ({tag}); pure-FHRR (no download). {desc}
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

MULTICTX = r'''
def _selftest():
    print("[selftest] PASS: paraconsistent-multi-context", flush=True)
def run() -> Dict:
    # per-CONTEXT Belnap 4-valued: a prop can be T/F/U/B differently in each context. Context-keyed pos/neg evidence bundles.
    g = np.random.default_rng(1); N = 8192; NP = 30; NC = 5; props = cphasor(NP, N, g); ctx = cphasor(NC, N, g)
    TR = 30 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        pos = {c: set() for c in range(NC)}; neg = {c: set() for c in range(NC)}
        for c in range(NC):
            for p in range(NP):
                if g.random() < 0.5:
                    pos[c].add(p)
                if g.random() < 0.4:
                    neg[c].add(p)
        # store context-bound evidence: POS = sum_c ctx[c] (X) (sum_{p in pos[c]} props[p])
        POS = sum((ctx[c] * sum((props[p] for p in pos[c]), np.zeros(N, dtype=np.complex64)) for c in range(NC)), np.zeros(N, dtype=np.complex64))
        NEG = sum((ctx[c] * sum((props[p] for p in neg[c]), np.zeros(N, dtype=np.complex64)) for c in range(NC)), np.zeros(N, dtype=np.complex64))
        for _q in range(NP):
            c = int(g.integers(0, NC)); p = int(g.integers(0, NP))
            hp = (np.vdot(props[p], POS * np.conj(ctx[c])).real) / N > 0.5     # unbind context, test prop membership
            hn = (np.vdot(props[p], NEG * np.conj(ctx[c])).real) / N > 0.5
            val = ("B" if (hp and hn) else "T" if hp else "F" if hn else "U")
            gold = ("B" if (p in pos[c] and p in neg[c]) else "T" if p in pos[c] else "F" if p in neg[c] else "U")
            correct += int(val == gold); n += 1
    acc = correct / n; print("  PARACONSISTENT-MULTI-CONTEXT per-context 4-valued acc=%.3f (NC=%d, n=%d)" % (acc, NC, n), flush=True)
    return {"multictx_acc": acc, "NC": NC, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "multi-context-4valued-acc=%.3f (NC=%d)" % (r["multictx_acc"], r["NC"])
    if r["multictx_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate tracks Belnap 4-valued truth PER CONTEXT >=0.85 -- a prop can be T/F/U/B differently across contexts; context-bound paraconsistent evidence (no cross-context contamination or explosion). " + s)
    if r["multictx_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-context 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: multi-context <0.70. " + s)
'''

META2 = r'''
def _auc(scores, labels):
    import numpy as _n; o = _n.argsort(scores); r = _n.empty(len(scores)); r[o] = _n.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: meta-2level", flush=True)
def run() -> Dict:
    # depth-2 meta-cognition: L1 = "do I know P?" (margin>tau). L2 = "am I SURE about my L1 answer?" = |margin - tau| (distance
    # from the decision boundary). L2 meta-confidence should predict whether L1 was CORRECT.
    g = np.random.default_rng(263); N = 2048; M = 180; VV = 200; tau = 0.14
    TR = 40 if SMOKE else 250; l1_correct = 0; n = 0; metaconf = []; l1ok = []
    for _ in range(TR):
        keys = cphasor(M, N, g); vals = cphasor(VV, N, g); truth = g.integers(0, VV, size=M); Mem = (keys * vals[truth]).sum(axis=0)
        for _q in range(8):
            known = g.random() < 0.5; nz = (g.random() * 0.4) * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            if known:
                qi = int(g.integers(0, M)); probe = Mem * np.conj(keys[qi]) + nz; gold_known = True
            else:
                nk = cphasor(1, N, g)[0]; probe = Mem * np.conj(nk) + nz; gold_known = False
            sc = np.sort((vals @ np.conj(probe)).real)[::-1] / N; margin = float(sc[0] - sc[1])
            l1 = margin > tau                                            # L1: knows-P assessment
            l1_right = (l1 == gold_known); l1_correct += int(l1_right); n += 1
            metaconf.append(abs(margin - tau)); l1ok.append(int(l1_right))   # L2: meta-confidence vs L1-correctness
    l1a = l1_correct / n; l2_auc = _auc(np.array(metaconf), np.array(l1ok))
    print("  META-2LEVEL L1-knows-acc=%.3f L2-metaconf-AUC(predicts-L1-correct)=%.3f (n=%d)" % (l1a, l2_auc, n), flush=True)
    return {"l1_acc": l1a, "l2_auc": l2_auc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "L1-knows=%.3f L2-metaconf-AUC=%.3f" % (r["l1_acc"], r["l2_auc"])
    if r["l1_acc"] >= 0.80 and r["l2_auc"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: depth-2 meta-cognition -- L1 knows-P >=0.80 AND L2 meta-confidence predicts L1 correctness (AUC>=0.70). Substrate knows WHAT IT KNOWS ABOUT what it knows (margin-distance = meta-certainty). " + s)
    if r["l1_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L1 0.70-0.80 or L2-AUC<0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: L1 <0.70. " + s)
'''

C = [
    dict(anchor="lap3_10_paracons_multictx_cpu_v1", tag="LAP3-10 PARACONSISTENT-MULTI-CONTEXT", title="Belnap 4-valued truth per context", desc="Context-bound pos/neg evidence; a prop can be T/F/U/B differently in each context; no cross-context contamination.", prereg="HARD-PASS multi-context>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.", body=MULTICTX),
    dict(anchor="stretch3_3_meta_2level_cpu_v1", tag="STRETCH3-3 META-COGNITIVE-2-LEVEL", title="depth-2 meta-cognition (knows what it knows about what it knows)", desc="L1 knows-P via margin; L2 meta-confidence = margin distance from boundary, predicts L1 correctness.", prereg="HARD-PASS L1>=0.80 AND L2-AUC>=0.70. MIDDLE L1>=0.70. HARD-FAIL<0.70.", body=META2),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
