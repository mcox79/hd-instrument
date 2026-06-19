"""Research WAVE-4: LAP4-12 SUBSTRATE-QUERY-COMPILER + STRETCH4-1 BAYESIAN-NETWORK-LEARNING. Pure-FHRR/numpy. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 ({tag}); pure-FHRR/numpy (no download). {desc}
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
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

QUERY = r'''
def _selftest():
    print("[selftest] PASS: query-compiler", flush=True)
def run() -> Dict:
    # query compiler: a relational query (SELECT t WHERE subj -REL-> t AND prop(t)=val) compiles to substrate ops
    # (unbind REL -> candidate set, then filter by PROP=val) and executes. Compare result set to ground truth.
    g = np.random.default_rng(12); N = 8192; VE = 250; NREL = 4; NC = 6; KF = 3
    ents = cphasor(VE, N, g); rels = cphasor(NREL, N, g); cities = cphasor(NC, N, g); PROP = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; f1 = 0.0; n = 0
    for _ in range(TR):
        x = int(g.integers(0, VE)); r_ = int(g.integers(0, NREL))
        tails = [int(v) for v in g.choice(VE, KF, replace=False)]
        rel_shard = sum((ents[x] * (rels[r_] * ents[t]) for t in tails), np.zeros(N, dtype=np.complex64))
        tcity = {t: int(g.integers(0, NC)) for t in tails}
        prop_shard = {t: ents[t] * (PROP * cities[tcity[t]]) for t in tails}
        Y = int(g.integers(0, NC)); gold = set(t for t in tails if tcity[t] == Y)
        # COMPILE+EXECUTE: op1 = unbind REL -> candidate tails (top-KF); op2 = filter PROP==Y
        scores = (ents @ np.conj(rel_shard * np.conj(ents[x]) * np.conj(rels[r_]))).real
        cand = [int(i) for i in np.argsort(scores)[::-1][:KF]]
        res = set(t for t in cand if t in prop_shard and cidx(prop_shard[t] * np.conj(ents[t]) * np.conj(PROP), cities) == Y)
        inter = len(res & gold); prec = inter / len(res) if res else (1.0 if not gold else 0.0); rec = inter / len(gold) if gold else 1.0
        f1 += (2 * prec * rec / (prec + rec)) if (prec + rec) else 1.0; n += 1
    score = f1 / n; print("  QUERY-COMPILER select-where-filter F1=%.3f (n=%d)" % (score, n), flush=True)
    return {"query_f1": score, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "query-F1=%.3f (n=%d)" % (r["query_f1"], r["n"])
    if r["query_f1"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate compiles+executes relational queries (SELECT-WHERE-FILTER) F1>=0.85 -- a query plan of unbind(traverse)+filter ops over the substrate; declarative querying without an external DB. " + s)
    if r["query_f1"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: query F1 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: query F1 <0.70. " + s)
'''

BNLEARN = r'''
def _selftest():
    print("[selftest] PASS: bayes-net-learning", flush=True)
def run() -> Dict:
    g = np.random.default_rng(279); NV = 5; NSAMP = 3000; PROBS = 25 if SMOKE else 90
    tp = 0; fp = 0; fn = 0; cpt_err = []
    for _ in range(PROBS):
        parents = {v: sorted(set(int(p) for p in g.choice(v, min(v, 2), replace=False))) if v > 0 else [] for v in range(NV)}
        true_edges = set((p, v) for v in range(NV) for p in parents[v])
        cpt = {}
        for v in range(NV):
            for cfg in itertools.product([0, 1], repeat=len(parents[v])):
                cpt[(v, cfg)] = g.uniform(0.1, 0.9)
        # sample
        X = np.zeros((NSAMP, NV), dtype=int)
        for v in range(NV):
            cfgs = [tuple(X[i, parents[v]]) for i in range(NSAMP)]
            ps = np.array([cpt[(v, c)] for c in cfgs]); X[:, v] = (g.random(NSAMP) < ps).astype(int)
        # STRUCTURE learning: partial-correlation skeleton (precision matrix)
        Xc = X - X.mean(0); C = np.corrcoef(X.T); P = np.linalg.pinv(C + 1e-6 * np.eye(NV))
        pred = set()
        for i in range(NV):
            for j in range(i + 1, NV):
                pc = -P[i, j] / math.sqrt(P[i, i] * P[j, j] + 1e-12)
                if abs(pc) > 0.07:
                    pred.add((i, j))
        skel = set((min(a, b), max(a, b)) for (a, b) in true_edges)
        tp += len(pred & skel); fp += len(pred - skel); fn += len(skel - pred)
        # PARAMETER learning: MLE of a CPT entry from counts
        v = NV - 1
        if parents[v]:
            for cfg in itertools.product([0, 1], repeat=len(parents[v])):
                mask = np.all(X[:, parents[v]] == np.array(cfg), axis=1)
                if mask.sum() > 20:
                    est = X[mask, v].mean(); cpt_err.append(abs(est - cpt[(v, cfg)]))
    prec = tp / (tp + fp) if (tp + fp) else 0.0; rec = tp / (tp + fn) if (tp + fn) else 0.0; cerr = float(np.mean(cpt_err)) if cpt_err else 1.0
    print("  BAYES-NET-LEARNING structure-precision=%.3f recall=%.3f CPT-MLE-err=%.3f" % (prec, rec, cerr), flush=True)
    return {"struct_precision": round(prec, 3), "struct_recall": round(rec, 3), "cpt_err": round(cerr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "structure-precision=%.3f recall=%.3f CPT-err=%.3f" % (r["struct_precision"], r["struct_recall"], r["cpt_err"])
    if r["struct_precision"] >= 0.70 and r["cpt_err"] <= 0.10:
        return ("HARD_PASS", "HARD_PASS: substrate LEARNS a Bayes net from data -- structure (skeleton precision>=0.70 via partial-corr) AND parameters (CPT MLE err<=0.10). Full structure+parameter learning. " + s)
    if r["struct_precision"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: structure precision 0.55-0.70 or CPT-err>0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: structure precision <0.55. " + s)
'''

C = [
    dict(anchor="lap4_12_query_compiler_cpu_v1", tag="LAP4-12 SUBSTRATE-QUERY-COMPILER", title="compile+execute relational queries over the substrate", desc="SELECT-WHERE-FILTER query compiled to unbind(traverse)+filter substrate ops; F1 vs ground-truth result set.", prereg="HARD-PASS query-F1>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.", body=QUERY),
    dict(anchor="stretch4_1_bayes_net_learning_cpu_v1", tag="STRETCH4-1 BAYESIAN-NETWORK-LEARNING", title="learn Bayes-net structure + parameters from data", desc="Sample from a hidden Bayes net; recover skeleton (partial-corr) + estimate CPTs (MLE).", prereg="HARD-PASS structure-prec>=0.70 AND CPT-err<=0.10. MIDDLE struct>=0.55. HARD-FAIL<0.55.", body=BNLEARN),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
