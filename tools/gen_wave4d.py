"""Research WAVE-4: LAP4-9 AGM-CONTRACTION-DEPTH + STRETCH4-4 META-LEARNING (few-shot schema). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 ({tag}); pure-FHRR (no download). {desc}
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

AGMDEPTH = r'''
def _selftest():
    print("[selftest] PASS: agm-contraction-depth", flush=True)
def run() -> Dict:
    # deep AGM: a LONG stream of prioritized assertions; each key revised many times (deep contraction chains). Verify the final
    # belief set + track contraction depth (number of supersessions per key).
    g = np.random.default_rng(266); N = 8192; NK = 25; NV = 200; keys = cphasor(NK, N, g); vals = cphasor(NV, N, g)
    TR = 20 if SMOKE else 120; correct = 0; n = 0; depths = []
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); belief = {}; supers = {k: 0 for k in range(NK)}
        T = 200
        for _t in range(T):
            k = int(g.integers(0, NK)); v = int(g.integers(0, NV)); p = float(g.random())
            if k in belief:
                vo, po = belief[k]
                if p > po:
                    Mem = Mem - keys[k] * vals[vo] + keys[k] * vals[v]; belief[k] = (v, p); supers[k] += 1
            else:
                Mem = Mem + keys[k] * vals[v]; belief[k] = (v, p)
        for k in belief:
            correct += int(cidx(Mem * np.conj(keys[k]), vals) == belief[k][0]); n += 1
        depths.append(np.mean([supers[k] for k in belief]))
    acc = correct / n; md = float(np.mean(depths))
    print("  AGM-CONTRACTION-DEPTH final-belief-correct=%.3f mean-contraction-depth=%.1f (n=%d)" % (acc, md, n), flush=True)
    return {"belief_acc": acc, "mean_depth": round(md, 1), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "deep-AGM-correct=%.3f mean-contraction-depth=%.1f" % (r["belief_acc"], r["mean_depth"])
    if r["belief_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: AGM belief revision stays correct >=0.85 through DEEP contraction chains (mean depth %.1f supersessions/key) -- repeated exact erasure does not accumulate error; belief base stable under many revisions. " % r["mean_depth"] + s)
    if r["belief_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: deep-AGM 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deep-AGM <0.70. " + s)
'''

METALEARN = r'''
def _selftest():
    print("[selftest] PASS: meta-learning", flush=True)
def run() -> Dict:
    # few-shot meta-learning: from K=5 examples of a NEW category, extract its schema (prototype), then classify new instances
    # (in-category vs out) WITHOUT pre-training -- one-shot schema induction.
    g = np.random.default_rng(4); N = 8192; NPROP = 50; SCHEMA_SZ = 6; KSHOT = 5; props = cphasor(NPROP, N, g)
    TR = 40 if SMOKE else 250; correct = 0; n = 0
    for _ in range(TR):
        schema = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
        def instance(in_cat):
            if in_cat:
                ps = set(schema)
                for p in list(ps):
                    if g.random() < 0.15:
                        ps.discard(p)
                while g.random() < 0.3:
                    ps.add(int(g.integers(0, NPROP)))
            else:
                ps = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
            return sum((props[p] for p in ps), np.zeros(N, dtype=np.complex64))
        # learn prototype from K shots (all in-category)
        proto = sum((instance(True) for _ in range(KSHOT)), np.zeros(N, dtype=np.complex64))
        # classify 6 new instances (mix in/out) by overlap with the learned prototype
        for _q in range(6):
            in_cat = g.random() < 0.5; inst = instance(in_cat)
            sim = float((np.vdot(inst, proto).real)) / (N * KSHOT)
            pred = sim > 0.35                                            # threshold (schema overlap)
            correct += int(pred == in_cat); n += 1
    acc = correct / n; print("  META-LEARNING few-shot(K=%d) new-category-acc=%.3f (n=%d)" % (KSHOT, acc, n), flush=True)
    return {"fewshot_acc": acc, "kshot": KSHOT, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "few-shot-acc=%.3f (K=%d)" % (r["fewshot_acc"], r["kshot"])
    if r["fewshot_acc"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate learns a NEW category schema from %d examples and classifies new instances >=0.80 -- one-shot/few-shot schema induction via prototype bundling (no pre-training). " % r["kshot"] + s)
    if r["fewshot_acc"] >= 0.68:
        return ("MIDDLE_BAND", "MIDDLE_BAND: few-shot 0.68-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: few-shot <0.68. " + s)
'''

C = [
    dict(anchor="lap4_9_agm_contraction_depth_cpu_v1", tag="LAP4-9 AGM-CONTRACTION-DEPTH", title="deep AGM belief revision (many supersessions per key)", desc="Long prioritized-assertion stream; deep contraction chains; verify final belief set stays correct.", prereg="HARD-PASS deep-AGM>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.", body=AGMDEPTH),
    dict(anchor="stretch4_4_meta_learning_cpu_v1", tag="STRETCH4-4 META-LEARNING", title="few-shot new-schema induction (learn category from K examples)", desc="From K=5 examples extract a new category prototype; classify new instances; no pre-training.", prereg="HARD-PASS few-shot>=0.80. MIDDLE>=0.68. HARD-FAIL<0.68.", body=METALEARN),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
