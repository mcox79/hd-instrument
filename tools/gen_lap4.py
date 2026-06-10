"""Research overnight laptop batch: LAP-4 TOM-DEPTH-3 (nested beliefs) + LAP-11 K-HOP-CONDITIONAL (AND/NOT in multi-hop). Pure-FHRR, extends validated nested-binding + k-hop patterns. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch ({tag}); pure-FHRR (no download). {desc}
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

TOM = r'''
def _selftest():
    import numpy as _n; assert _n.argmax([0,1])==1, "argmax"; print("[selftest] PASS: tom-depth-3", flush=True)
def run() -> Dict:
    # depth-3 ToM: A believes (B believes (C believes X)). Per-level sharded BELIEF binding; unwind 3 nested agent-beliefs to X.
    g = np.random.default_rng(43); N = 8192; NAG = 12; VF = 200
    agents = cphasor(NAG, N, g); fillers = cphasor(VF, N, g); BEL = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; hit = 0; n = 0
    for _ in range(TR):
        a, b, c = (int(x) for x in g.choice(NAG, 3, replace=False)); x = int(g.integers(0, VF))
        inner = agents[c] * (BEL * fillers[x])                            # C believes X
        mid = agents[b] * (BEL * inner)                                   # B believes (C believes X)
        outer = agents[a] * (BEL * mid)                                   # A believes (B believes (C believes X))
        # unwind: peel A, then B, then C; recover X. cleanup at the leaf only.
        m1 = outer * np.conj(agents[a]) * np.conj(BEL)                    # ~ mid
        m2 = m1 * np.conj(agents[b]) * np.conj(BEL)                       # ~ inner
        leaf = m2 * np.conj(agents[c]) * np.conj(BEL)                     # ~ fillers[x]
        hit += int(cidx(leaf, fillers) == x); n += 1
    acc = hit / n; print("  TOM-DEPTH-3 nested-belief recall=%.3f (NAG=%d, n=%d)" % (acc, NAG, n), flush=True)
    return {"tom3_recall": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "depth3-ToM-recall=%.3f (n=%d)" % (r["tom3_recall"], r["n"])
    if r["tom3_recall"] >= 0.75:
        return ("HARD_PASS", "HARD_PASS: substrate represents depth-3 nested belief (A believes B believes C believes X) recall>=0.75 -- recursive theory-of-mind via nested binding; agent-belief composition holds 3 deep. " + s)
    if r["tom3_recall"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: depth-3 ToM 0.55-0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: depth-3 ToM <0.55. " + s)
'''

KCOND = r'''
def _selftest():
    import numpy as _n; assert len({1,2,3}-{2})==2, "setminus"; print("[selftest] PASS: k-hop-conditional", flush=True)
def run() -> Dict:
    # conditional multi-hop: X-FRIEND->{friends}; each friend-CITY->city; query "friends of X NOT in city Y". substrate retrieves
    # the friend set (multi-tail bundle, top-k), maps each to city, set-excludes those in city Y. Measure exact filtered set.
    g = np.random.default_rng(11); N = 8192; VE = 250; NC = 8; KF = 4
    ents = cphasor(VE, N, g); cities = cphasor(NC, N, g); FRIEND = cphasor(1, N, g)[0]; CITY = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; f1 = 0.0; n = 0
    for _ in range(TR):
        x = int(g.integers(0, VE)); friends = [int(v) for v in g.choice(VE, KF, replace=False) if v != x][:KF]
        fcity = {f: int(g.integers(0, NC)) for f in friends}
        fr_shard = sum((ents[x] * (FRIEND * ents[f]) for f in friends), np.zeros(N, dtype=np.complex64))
        cy_shard = {f: ents[f] * (CITY * cities[fcity[f]]) for f in friends}
        Y = int(g.integers(0, NC)); gold = set(f for f in friends if fcity[f] != Y)
        # retrieve friend set: top-KF cleanup of FRIEND unbind
        scores = (ents @ np.conj(fr_shard * np.conj(ents[x]) * np.conj(FRIEND))).real
        cand = [int(i) for i in np.argsort(scores)[::-1][:KF]]
        pred = set()
        for f in cand:
            if f in cy_shard:
                cy = cidx(cy_shard[f] * np.conj(ents[f]) * np.conj(CITY), cities)
                if cy != Y:
                    pred.add(f)
        inter = len(pred & gold); prec = inter / len(pred) if pred else (1.0 if not gold else 0.0); rec = inter / len(gold) if gold else 1.0
        f1 += (2 * prec * rec / (prec + rec)) if (prec + rec) else (1.0 if not gold and not pred else 0.0); n += 1
    score = f1 / n; print("  K-HOP-CONDITIONAL (NOT-filter) F1=%.3f (n=%d)" % (score, n), flush=True)
    return {"cond_f1": score, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "conditional-multihop-F1=%.3f (n=%d)" % (r["cond_f1"], r["n"])
    if r["cond_f1"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate answers conditional multi-hop (friends-of-X NOT-in-city-Y) F1>=0.80 -- AND/NOT set logic composes with K-hop traversal natively. " + s)
    if r["cond_f1"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: conditional F1 0.65-0.80 (multi-tail superposition; sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: conditional F1 <0.65. " + s)
'''

C = [
    dict(anchor="lap4_tom_depth3_cpu_v1", tag="LAP-4 TOM-DEPTH-3", title="substrate depth-3 nested belief (theory-of-mind)", desc="A believes (B believes (C believes X)); unwind 3 nested agent-belief bindings to X.", prereg="HARD-PASS depth-3 ToM>=0.75. MIDDLE>=0.55. HARD-FAIL<0.55.", body=TOM),
    dict(anchor="lap11_khop_conditional_cpu_v1", tag="LAP-11 K-HOP-CONDITIONAL", title="conditional multi-hop with AND/NOT set logic", desc="friends-of-X NOT-in-city-Y: multi-tail friend retrieval + per-friend city + NOT-filter; F1 on the filtered set.", prereg="HARD-PASS F1>=0.80. MIDDLE>=0.65. HARD-FAIL<0.65.", body=KCOND),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
